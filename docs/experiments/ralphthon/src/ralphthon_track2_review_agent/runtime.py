"""Bounded, restart-safe mock runtime for the Track 2 review contract."""

from __future__ import annotations

import json
import math
import re
import threading
import time
from collections import Counter, deque
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .calibration import (
    CalibrationGateSnapshot,
    CalibrationPolicy,
    CalibrationRequest,
    RiskSignals,
    VerifierDecisionError,
    VerifierFinding,
    VerifierPort,
    assess_risk,
    calibration_cap,
    parse_verifier_decision,
    select_for_calibration,
)
from .contract import SCHEMA_SHA256, validate_review
from .identity import PROMPT_SHA256
from .io_utils import atomic_write_bytes, atomic_write_json, canonical_json_bytes, sha256_bytes
from .ledger import AtomicLedger, audit_ledger
from .manifest import freeze_manifest


AGENT_VERSION = "ralphthon-track2-review-agent-v1"
SAFE_PAPER_ID = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
BLOCKING_IDENTITY_FIELDS = frozenset(
    {"paper_id", "lease_id", "input_hash", "evidence_hash", "prompt_hash", "agent_version"}
)


class Mode(str, Enum):
    BUILD = "BUILD"
    DRY_RUN = "DRY-RUN"
    LIVE = "LIVE"

    @classmethod
    def parse(cls, value: str | "Mode") -> "Mode":
        if isinstance(value, cls):
            return value
        normalized = value.strip().upper().replace("_", "-")
        return cls(normalized)


class LiveAdapterUnavailable(RuntimeError):
    """Raised when LIVE is requested before a verified platform adapter exists."""


class ControlledProcessInterruption(RuntimeError):
    """Signal a test-only DRY-RUN process boundary after durable completion."""

    exit_code = 75

    def __init__(self, posted_verified: int) -> None:
        self.posted_verified = posted_verified
        super().__init__(
            f"controlled DRY-RUN interruption after {posted_verified} posted_verified papers"
        )


@dataclass(frozen=True)
class RunSummary:
    mode: str
    assigned_count: int
    posted_verified: int
    schema_valid_count: int
    duplicate_post_attempts: int
    duplicate_idempotency_keys: int
    worker_timeout_recoveries: int
    malformed_json_repairs: int
    claim_timeout_reconciliations: int
    post_timeout_reconciliations: int
    restart_recoveries: int
    calibration_adapter: str
    verifier_cap: int
    risk_scored_count: int
    high_risk_count: int
    verifier_selected_count: int
    verifier_pass_count: int
    verifier_repair_count: int
    verifier_timeout_count: int
    verifier_failure_count: int
    verifier_malformed_count: int
    verifier_max_active: int
    schema_repair_count: int
    calibration_repair_count: int
    repair_budget_exhausted_count: int
    verifier_bypass_counts: dict[str, int]
    failed_ids: tuple[str, ...]
    elapsed_seconds: float
    latency_p50_seconds: float
    latency_p95_seconds: float
    success: bool

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["failed_ids"] = list(self.failed_ids)
        return result


def _failure_ids(plan: Mapping[str, Any], name: str) -> set[str]:
    raw = plan.get(name, ())
    if isinstance(raw, str):
        return {raw}
    if isinstance(raw, Iterable) and not isinstance(raw, (bytes, Mapping)):
        return {str(value) for value in raw}
    return set()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_paper_id(value: Any) -> str:
    if not isinstance(value, str) or not SAFE_PAPER_ID.fullmatch(value):
        raise ValueError(
            "paper_id must be a non-empty path-safe ASCII identifier "
            "containing only letters, digits, dot, underscore, or hyphen"
        )
    return value


def _blocking_identity_errors(errors: Sequence[str]) -> list[str]:
    return [error for error in errors if error.partition(":")[0] in BLOCKING_IDENTITY_FIELDS]


def _risk_signals_for(
    paper_id: str,
    signal_map: Mapping[str, RiskSignals | Mapping[str, Any]],
) -> RiskSignals:
    raw = signal_map.get(paper_id, RiskSignals())
    if isinstance(raw, RiskSignals):
        return raw
    if not isinstance(raw, Mapping):
        raise TypeError(f"risk signals for {paper_id} must be an object")
    allowed = set(RiskSignals.__dataclass_fields__)
    unknown = sorted(set(raw) - allowed, key=str)
    if unknown:
        raise ValueError(f"unknown risk signals for {paper_id}: {unknown}")
    return RiskSignals(**dict(raw))


def _pointer_tokens(pointer: str) -> tuple[str, ...]:
    if not pointer.startswith("/"):
        raise ValueError(f"invalid JSON Pointer {pointer!r}")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/"))


def _read_pointer(document: Any, pointer: str) -> Any:
    value = document
    for token in _pointer_tokens(pointer):
        if isinstance(value, list):
            value = value[int(token)]
        elif isinstance(value, Mapping):
            value = value[token]
        else:
            raise KeyError(pointer)
    return value


def _write_pointer(document: Any, pointer: str, replacement: Any) -> None:
    tokens = _pointer_tokens(pointer)
    if not tokens:
        raise ValueError("the ReviewDraft root is not repairable")
    parent = document
    for token in tokens[:-1]:
        if isinstance(parent, list):
            parent = parent[int(token)]
        elif isinstance(parent, Mapping):
            parent = parent[token]
        else:
            raise KeyError(pointer)
    final = tokens[-1]
    if isinstance(parent, list):
        parent[int(final)] = replacement
    elif isinstance(parent, dict):
        if final not in parent:
            raise KeyError(pointer)
        parent[final] = replacement
    else:
        raise KeyError(pointer)


def _changed_pointers(before: Any, after: Any, pointer: str = "") -> set[str]:
    if type(before) is not type(after):
        return {pointer or "/"}
    if isinstance(before, Mapping):
        if set(before) != set(after):
            return {pointer or "/"}
        changed: set[str] = set()
        for key in before:
            escaped = str(key).replace("~", "~0").replace("/", "~1")
            changed.update(_changed_pointers(before[key], after[key], f"{pointer}/{escaped}"))
        return changed
    if isinstance(before, list):
        if len(before) != len(after):
            return {pointer or "/"}
        changed = set()
        for index, (left, right) in enumerate(zip(before, after)):
            changed.update(_changed_pointers(left, right, f"{pointer}/{index}"))
        return changed
    return set() if before == after else {pointer or "/"}


def _changes_are_field_scoped(changed: set[str], requested: set[str]) -> bool:
    if not changed:
        return False
    return all(
        any(path == allowed or path.startswith(f"{allowed}/") for allowed in requested)
        for path in changed
    )


def _finding_payload(finding: VerifierFinding) -> dict[str, str]:
    return {
        "field_path": finding.field_path,
        "problem": finding.problem,
        "location": finding.location,
        "instruction": finding.instruction,
    }


def _calibration_adapter_name(verifier: VerifierPort | None) -> str:
    if verifier is None:
        return "none"
    value = getattr(verifier, "adapter_name", None)
    if isinstance(value, str) and value:
        return value
    if verifier.__class__.__name__ == "MockVerifier":
        return "mock"
    return "injected"


def _first_locator(text: str, fallback: str) -> str:
    match = re.search(r"\b(Table|Figure)\s+([A-Za-z0-9.-]+)", text, re.IGNORECASE)
    if match:
        return f"{match.group(1).title()} {match.group(2)} (page 3)"
    return fallback


def _section(text: str, name: str) -> str:
    match = re.search(
        rf"(?ims)^##\s+{re.escape(name)}\s*\([^\n]+\)\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def _review_evidence(paper_text: str) -> tuple[dict[str, str], dict[str, str]]:
    method = _section(paper_text, "Method")
    results = _section(paper_text, "Results")
    method_lower = method.lower()
    results_lower = results.lower()

    if all(token in method_lower for token in ("sensitivity", "epsilon", "neighbor")):
        strength = {
            "claim": "The method states the privacy mechanism parameters and neighboring relation.",
            "location": "Method (page 2)",
        }
    else:
        strength = {
            "claim": "The frozen mock paper reports an explicit comparison that can be audited.",
            "location": _first_locator(results, "Results (page 3)"),
        }

    if "same evaluation set" in method_lower:
        weakness = {
            "claim": "Selecting a threshold on the evaluation set risks an optimistic assessment.",
            "location": "Method (page 2)",
        }
    elif "no composition analysis" in results_lower:
        weakness = {
            "claim": "The result omits repeated-release composition, limiting the practical claim.",
            "location": _first_locator(results, "Results (page 3)"),
        }
    elif "test-family performance" in results_lower or "test-informed" in results_lower:
        weakness = {
            "claim": "Test-informed selection makes the reported comparison optimistic.",
            "location": "Results (page 3)",
        }
    elif "lowest-resource" in results_lower:
        weakness = {
            "claim": "The aggregate result hides a material degradation for the lowest-resource group.",
            "location": _first_locator(results, "Results (page 3)"),
        }
    else:
        weakness = {
            "claim": "The stated limitations restrict how broadly the reported comparison can be interpreted.",
            "location": "Limitations (page 4)",
        }
    return strength, weakness


def _mock_review(paper: Mapping[str, Any], manifest: Mapping[str, Any], worker_id: str) -> dict[str, Any]:
    started = _utc_now()
    paper_text = Path(str(paper["resolved_paper_path"])).read_text(encoding="utf-8")
    strength, weakness = _review_evidence(paper_text)
    rationales = {
        "soundness": weakness,
        "presentation": strength,
        "contribution": strength,
        "significance": weakness,
        "originality": strength,
        "overall_recommendation": weakness,
        "confidence": strength,
    }
    return {
        "review_draft_version": "1.0",
        "paper_id": manifest["paper_id"],
        "lease_id": paper["lease_id"],
        "summary": "The mock paper presents a bounded comparison with explicit existing evidence.",
        "strengths": [strength],
        "weaknesses": [weakness],
        "questions": ["Which additional frozen evaluation would most directly test the stated limitation?"],
        "soundness": 3,
        "presentation": 3,
        "contribution": 3,
        "significance": 2,
        "originality": 2,
        "overall_recommendation": 4,
        "confidence": 3,
        "comment": (
            "The comparison is clearly reported, but the paper should narrow its claim and add "
            "evidence that directly addresses the limitation identified above."
        ),
        "ethics_and_limitations": (
            "No additional ethics issue is established by this synthetic fixture; the evidence "
            "scope and external-validity limitation remain material."
        ),
        "evidence_trace": [strength, weakness],
        "score_rationales": rationales,
        "worker_id": worker_id,
        "agent_version": manifest["agent_version"],
        "prompt_hash": manifest["prompt_hash"],
        "input_hash": manifest["input_hash"],
        "evidence_hash": manifest["evidence_hash"],
        "started_at": started,
        "completed_at": _utc_now(),
    }


class MockReviewPlatform:
    """In-memory adapter with deterministic one-shot fault injection.

    The adapter models visible remote state so the coordinator can reconcile a
    timeout before deciding whether a retry is safe. It never reaches a network.
    """

    def __init__(self, failure_plan: Mapping[str, Any] | None = None) -> None:
        self.failure_plan = dict(failure_plan or {})
        self.claimed: set[str] = set()
        self.posted: dict[str, str] = {}
        self.attempts: Counter[tuple[str, str]] = Counter()
        self.status_checks: Counter[tuple[str, str]] = Counter()
        self._lock = threading.RLock()

    def _first_fault(self, kind: str, paper_id: str) -> bool:
        with self._lock:
            self.attempts[(kind, paper_id)] += 1
            return (
                paper_id in _failure_ids(self.failure_plan, kind)
                and self.attempts[(kind, paper_id)] == 1
            )

    def claim(self, paper_id: str) -> dict[str, str]:
        timed_out = self._first_fault("claim_timeout", paper_id)
        with self._lock:
            self.claimed.add(paper_id)
        if timed_out:
            raise TimeoutError(f"injected claim timeout for {paper_id}")
        return {"state": "claimed", "paper_id": paper_id}

    def status(self, paper_id: str, state: str) -> bool:
        with self._lock:
            self.status_checks[(state, paper_id)] += 1
            if state == "claimed":
                return paper_id in self.claimed
            if state == "posted":
                return paper_id in self.posted
        raise ValueError(f"unsupported mock status {state!r}")

    def draft(
        self,
        paper: Mapping[str, Any],
        manifest: Mapping[str, Any],
        worker_id: str,
    ) -> Mapping[str, Any] | str:
        paper_id = str(paper["paper_id"])
        if self._first_fault("worker_timeout", paper_id):
            raise TimeoutError(f"injected worker timeout for {paper_id}")
        review = _mock_review(paper, manifest, worker_id)
        if self._first_fault("malformed_json", paper_id):
            return "{malformed-json"
        return review

    def repair(
        self,
        paper: Mapping[str, Any],
        manifest: Mapping[str, Any],
        worker_id: str,
        errors: Sequence[str],
    ) -> Mapping[str, Any]:
        del errors
        return _mock_review(paper, manifest, worker_id)

    def repair_calibration(
        self,
        paper: Mapping[str, Any],
        manifest: Mapping[str, Any],
        review: Mapping[str, Any],
        findings: Sequence[VerifierFinding],
    ) -> Mapping[str, Any]:
        """Apply a deterministic field-scoped synthetic repair.

        This is a DRY-RUN Worker stand-in, not scientific review logic. Tests
        may supply exact values under ``calibration_repair_values``.
        """

        del manifest
        paper_id = str(paper["paper_id"])
        with self._lock:
            self.attempts[("calibration_repair", paper_id)] += 1
        repaired = deepcopy(dict(review))
        configured = self.failure_plan.get("calibration_repair_values", {})
        paper_values = configured.get(paper_id, {}) if isinstance(configured, Mapping) else {}
        if not isinstance(paper_values, Mapping):
            raise ValueError(f"calibration repair values for {paper_id} must be an object")
        for finding in findings:
            current = _read_pointer(repaired, finding.field_path)
            if finding.field_path in paper_values:
                replacement = deepcopy(paper_values[finding.field_path])
            elif isinstance(current, str):
                replacement = f"{current} Targeted calibration repair: {finding.instruction}"
            elif isinstance(current, int) and not isinstance(current, bool):
                upper = 6 if finding.field_path == "/overall_recommendation" else 5
                if finding.field_path not in {"/overall_recommendation", "/confidence"}:
                    upper = 4
                replacement = current - 1 if current > 1 else min(upper, current + 1)
            else:
                raise ValueError(
                    f"mock calibration repair needs an explicit value for {finding.field_path}"
                )
            _write_pointer(repaired, finding.field_path, replacement)
        if paper_id in _failure_ids(self.failure_plan, "calibration_repair_invalid"):
            repaired["comment"] = ""
        if paper_id in _failure_ids(self.failure_plan, "calibration_repair_identity"):
            repaired["paper_id"] = f"wrong-{paper_id}"
        if paper_id in _failure_ids(self.failure_plan, "calibration_repair_scope"):
            repaired["worker_id"] = "unauthorized-calibration-worker"
        return repaired

    def post(self, paper_id: str, review: Mapping[str, Any], idempotency_key: str) -> dict[str, str]:
        timed_out = self._first_fault("post_timeout", paper_id)
        review_hash = sha256_bytes(canonical_json_bytes(review))
        with self._lock:
            previous = self.posted.get(paper_id)
            if previous is not None and previous != review_hash:
                raise RuntimeError(f"mock platform rejects a second distinct post for {paper_id}")
            self.posted[paper_id] = review_hash
        if timed_out:
            raise TimeoutError(f"injected post timeout for {paper_id}")
        return {
            "state": "posted",
            "paper_id": paper_id,
            "review_hash": review_hash,
            "idempotency_key": idempotency_key,
        }


def _clipboard_text(review: Mapping[str, Any]) -> str:
    fields = (
        ("Paper ID", "paper_id"),
        ("Soundness", "soundness"),
        ("Presentation", "presentation"),
        ("Contribution", "contribution"),
        ("Significance", "significance"),
        ("Originality", "originality"),
        ("Overall Recommendation", "overall_recommendation"),
        ("Confidence", "confidence"),
        ("Comment", "comment"),
    )
    return "\n".join(f"{label}: {review[key]}" for label, key in fields) + "\n"


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1))
    return ordered[index]


def _resolve_paper(root: Path, paper: Mapping[str, Any], lease_id: str) -> dict[str, Any]:
    resolved = dict(paper)
    paper_path = Path(str(paper["paper_path"]))
    if not paper_path.is_absolute():
        paper_path = root / paper_path
    evidence_paths: list[str] = []
    for value in paper.get("evidence_paths", []):
        evidence_path = Path(str(value))
        if not evidence_path.is_absolute():
            evidence_path = root / evidence_path
        evidence_paths.append(str(evidence_path))
    resolved["resolved_paper_path"] = str(paper_path)
    resolved["resolved_evidence_paths"] = evidence_paths
    resolved["lease_id"] = lease_id
    return resolved


def run_batch(
    papers: Sequence[Mapping[str, Any]],
    output_dir: str | Path,
    *,
    mode: str | Mode = Mode.DRY_RUN,
    workers: int = 3,
    failure_plan: Mapping[str, Any] | None = None,
    platform: MockReviewPlatform | None = None,
    root_dir: str | Path | None = None,
    verifier: VerifierPort | None = None,
    risk_signals: Mapping[str, RiskSignals | Mapping[str, Any]] | None = None,
    calibration_policy: CalibrationPolicy | None = None,
    calibration_gate: CalibrationGateSnapshot | None = None,
) -> RunSummary:
    """Run a bounded mock batch with Root-owned side effects and ledger state.

    Calibration is opt-in. The injected verifier is advisory and read-only;
    Root retains repair, deterministic validation, ledger, outbox, and posting.
    """

    selected_mode = Mode.parse(mode)
    if selected_mode is Mode.LIVE:
        raise LiveAdapterUnavailable(
            "LIVE is blocked until read-only discovery verifies the platform adapter"
        )
    if not 1 <= workers <= 3:
        raise ValueError("workers must be between 1 and 3")

    calibration_requested = any(
        value is not None
        for value in (verifier, risk_signals, calibration_policy, calibration_gate)
    )
    policy = calibration_policy or CalibrationPolicy()
    if not isinstance(policy, CalibrationPolicy):
        raise TypeError("calibration_policy must be CalibrationPolicy")
    if calibration_gate is not None and not isinstance(
        calibration_gate, CalibrationGateSnapshot
    ):
        raise TypeError("calibration_gate must be CalibrationGateSnapshot")
    signal_map = dict(risk_signals or {})

    plan = dict(failure_plan or {})
    controlled_exit_after = plan.get("controlled_process_exit_after")
    if controlled_exit_after is not None:
        if selected_mode is not Mode.DRY_RUN:
            raise ValueError("controlled_process_exit_after is a DRY-RUN-only test hook")
        if (
            isinstance(controlled_exit_after, bool)
            or not isinstance(controlled_exit_after, int)
            or controlled_exit_after <= 0
        ):
            raise ValueError("controlled_process_exit_after must be a positive integer")

    assigned_ids = [_validate_paper_id(paper.get("paper_id")) for paper in papers]
    if len(set(assigned_ids)) != len(assigned_ids):
        raise ValueError("paper_id values must be unique")
    unknown_signal_ids = sorted(set(signal_map) - set(assigned_ids))
    if unknown_signal_ids:
        raise ValueError(f"risk signals reference unassigned paper IDs: {unknown_signal_ids}")
    for paper_id in signal_map:
        _risk_signals_for(paper_id, signal_map)

    destination = Path(output_dir)
    manifests_dir = destination / "manifests"
    outbox_dir = destination / "outbox"
    clipboard_dir = destination / "clipboard"
    for directory in (manifests_dir, outbox_dir, clipboard_dir):
        directory.mkdir(parents=True, exist_ok=True)

    mock = platform or MockReviewPlatform(plan)
    started = time.monotonic()
    ledger_path = destination / "ledger.jsonl"
    ledger = AtomicLedger(ledger_path)
    root = Path(root_dir) if root_dir is not None else Path.cwd()

    if selected_mode is Mode.BUILD:
        for paper in papers:
            paper_id = str(paper["paper_id"])
            resolved = _resolve_paper(root, paper, f"build-{paper_id}")
            freeze_manifest(
                manifests_dir / f"{paper_id}.json",
                paper_id=paper_id,
                paper_path=resolved["resolved_paper_path"],
                evidence_paths=resolved["resolved_evidence_paths"],
                agent_version=AGENT_VERSION,
                prompt_hash=PROMPT_SHA256,
                schema_hash=SCHEMA_SHA256,
            )
        summary = RunSummary(
            mode=selected_mode.value,
            assigned_count=len(assigned_ids),
            posted_verified=0,
            schema_valid_count=0,
            duplicate_post_attempts=0,
            duplicate_idempotency_keys=0,
            worker_timeout_recoveries=0,
            malformed_json_repairs=0,
            claim_timeout_reconciliations=0,
            post_timeout_reconciliations=0,
            restart_recoveries=0,
            calibration_adapter="none",
            verifier_cap=0,
            risk_scored_count=0,
            high_risk_count=0,
            verifier_selected_count=0,
            verifier_pass_count=0,
            verifier_repair_count=0,
            verifier_timeout_count=0,
            verifier_failure_count=0,
            verifier_malformed_count=0,
            verifier_max_active=0,
            schema_repair_count=0,
            calibration_repair_count=0,
            repair_budget_exhausted_count=0,
            verifier_bypass_counts={},
            failed_ids=(),
            elapsed_seconds=round(time.monotonic() - started, 6),
            latency_p50_seconds=0.0,
            latency_p95_seconds=0.0,
            success=True,
        )
        atomic_write_json(destination / "summary.json", summary.to_dict())
        return summary

    already_posted = ledger.posted_verified_ids()
    pending = deque(paper for paper in papers if str(paper["paper_id"]) not in already_posted)
    active: dict[
        Future[Mapping[str, Any] | str],
        tuple[dict[str, Any], dict[str, Any], int, float, str],
    ] = {}
    active_leases: set[str] = set()
    available_workers = deque(f"review-worker-{index}" for index in range(1, workers + 1))
    failures: set[str] = set()
    latencies: list[float] = []
    counters: Counter[str] = Counter()
    schema_valid_ids: set[str] = set()
    repair_used_ids = {
        str(event["paper_id"])
        for event in ledger.events
        if event.get("state") == "repair_attempt"
    }
    verifier_attempted_ids = {
        str(event["paper_id"])
        for event in ledger.events
        if event.get("state") == "verifier_attempt"
    }
    for paper_id in already_posted:
        manifest_path = manifests_dir / f"{paper_id}.json"
        outbox_path = outbox_dir / f"{paper_id}.json"
        if manifest_path.is_file() and outbox_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            review = json.loads(outbox_path.read_text(encoding="utf-8"))
            if not validate_review(review, manifest):
                schema_valid_ids.add(paper_id)
    processed_since_start = 0
    restart_after = plan.get("process_restart_after")
    restart_injected = False

    def record_processed() -> None:
        nonlocal ledger, processed_since_start, restart_injected
        processed_since_start += 1
        if (
            not restart_injected
            and isinstance(restart_after, int)
            and not isinstance(restart_after, bool)
            and restart_after > 0
            and processed_since_start >= restart_after
        ):
            # Compatibility-only fault: this reopens the ledger in-process. The
            # separate controlled exit hook is used to prove a real process resume.
            ledger = AtomicLedger(ledger_path)
            counters["restart_recoveries"] += 1
            restart_injected = True
        if (
            isinstance(controlled_exit_after, int)
            and processed_since_start >= controlled_exit_after
        ):
            raise ControlledProcessInterruption(len(ledger.posted_verified_ids()))

    def schedule(executor: ThreadPoolExecutor, paper_input: Mapping[str, Any], attempt: int = 1) -> None:
        nonlocal ledger
        paper_id = str(paper_input["paper_id"])
        if paper_id in ledger.posted_verified_ids():
            return
        lease_id = f"lease-{sha256_bytes(paper_id.encode('utf-8'))[:16]}"
        if lease_id in active_leases and attempt == 1:
            raise RuntimeError(f"duplicate active lease for {paper_id}")
        active_leases.add(lease_id)
        resolved = _resolve_paper(root, paper_input, lease_id)
        manifest = freeze_manifest(
            manifests_dir / f"{paper_id}.json",
            paper_id=paper_id,
            paper_path=resolved["resolved_paper_path"],
            evidence_paths=resolved["resolved_evidence_paths"],
            agent_version=AGENT_VERSION,
            prompt_hash=PROMPT_SHA256,
            schema_hash=SCHEMA_SHA256,
        )
        if attempt == 1:
            if mock.status(paper_id, "claimed"):
                ledger.append(paper_id, "claimed", reconciled_before_action=True)
            else:
                try:
                    mock.claim(paper_id)
                    ledger.append(paper_id, "claimed")
                except TimeoutError as exc:
                    ledger.append(paper_id, "claim_unknown", error=str(exc))
                    if not mock.status(paper_id, "claimed"):
                        failures.add(paper_id)
                        active_leases.discard(lease_id)
                        return
                    counters["claim_timeout_reconciliations"] += 1
                    ledger.append(paper_id, "claimed", reconciled=True)
            ledger.append(paper_id, "leased", lease_id=lease_id, input_hash=manifest["input_hash"])
        if not available_workers:
            raise RuntimeError("no logical Review Worker slot is available")
        worker_id = available_workers.popleft()
        try:
            future = executor.submit(mock.draft, resolved, manifest, worker_id)
        except BaseException:
            available_workers.appendleft(worker_id)
            raise
        active[future] = (resolved, manifest, attempt, time.monotonic(), worker_id)

    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="review-worker") as executor:
        while pending or active:
            while pending and len(active) < workers:
                schedule(executor, pending.popleft())
            if not active:
                break
            completed, _ = wait(tuple(active), return_when=FIRST_COMPLETED)
            for future in completed:
                resolved, manifest, attempt, draft_started, worker_id = active.pop(future)
                available_workers.append(worker_id)
                paper_id = str(resolved["paper_id"])
                try:
                    draft = future.result()
                except TimeoutError as exc:
                    ledger.append(paper_id, "worker_timeout", attempt=attempt, error=str(exc))
                    if attempt == 1:
                        counters["worker_timeout_recoveries"] += 1
                        schedule(executor, resolved, attempt=2)
                        continue
                    failures.add(paper_id)
                    active_leases.discard(str(resolved["lease_id"]))
                    continue

                validation_errors: list[str]
                if not isinstance(draft, Mapping):
                    validation_errors = ["review: expected object"]
                else:
                    validation_errors = validate_review(
                        draft,
                        manifest,
                        expected_lease_id=str(resolved["lease_id"]),
                    )
                if validation_errors:
                    blocking_errors = _blocking_identity_errors(validation_errors)
                    if blocking_errors:
                        ledger.append(paper_id, "identity_reject", errors=blocking_errors)
                        failures.add(paper_id)
                        active_leases.discard(str(resolved["lease_id"]))
                        continue
                    ledger.append(paper_id, "validator_reject", errors=validation_errors)
                    if paper_id in repair_used_ids:
                        ledger.append(
                            paper_id,
                            "repair_budget_exhausted",
                            source="schema",
                        )
                        failures.add(paper_id)
                        active_leases.discard(str(resolved["lease_id"]))
                        continue
                    ledger.append(paper_id, "repair_attempt", source="schema")
                    repair_used_ids.add(paper_id)
                    repaired = mock.repair(
                        resolved,
                        manifest,
                        str(draft.get("worker_id", "review-worker-repair"))
                        if isinstance(draft, Mapping)
                        else "review-worker-repair",
                        validation_errors,
                    )
                    repaired_errors = validate_review(
                        repaired,
                        manifest,
                        expected_lease_id=str(resolved["lease_id"]),
                    )
                    if repaired_errors:
                        blocking_errors = _blocking_identity_errors(repaired_errors)
                        if blocking_errors:
                            ledger.append(
                                paper_id,
                                "identity_reject",
                                errors=blocking_errors,
                                source="repair",
                            )
                            failures.add(paper_id)
                            active_leases.discard(str(resolved["lease_id"]))
                            continue
                        ledger.append(paper_id, "repair_failed", errors=repaired_errors)
                        failures.add(paper_id)
                        active_leases.discard(str(resolved["lease_id"]))
                        continue
                    draft = repaired
                    counters["malformed_json_repairs"] += 1

                review = dict(draft)
                schema_valid_ids.add(paper_id)
                if paper_id in verifier_attempted_ids and not calibration_requested:
                    ledger.append(
                        paper_id,
                        "calibration_resume_blocked",
                        reason="prior_verifier_attempt_without_verified_post",
                        fail_closed=True,
                    )
                    failures.add(paper_id)
                    active_leases.discard(str(resolved["lease_id"]))
                    continue
                if calibration_requested:
                    assessment = assess_risk(_risk_signals_for(paper_id, signal_map))
                    ledger.append(
                        paper_id,
                        "risk_assessed",
                        score=assessment.score,
                        reasons=list(assessment.reasons),
                    )
                    if paper_id in verifier_attempted_ids:
                        ledger.append(
                            paper_id,
                            "calibration_resume_blocked",
                            reason="prior_verifier_attempt_without_verified_post",
                            score=assessment.score,
                            fail_closed=True,
                        )
                        failures.add(paper_id)
                        active_leases.discard(str(resolved["lease_id"]))
                        continue
                    else:
                        gate = calibration_gate or CalibrationGateSnapshot(
                            elapsed_seconds=time.monotonic() - started,
                            validated_backlog=0,
                            posting_pace_on_target=True,
                            pending_draft_assignments=bool(pending),
                        )
                        selection = select_for_calibration(
                            policy,
                            assessment,
                            gate,
                            assigned_count=len(assigned_ids),
                            selected_count=len(verifier_attempted_ids),
                            repaired=paper_id in repair_used_ids,
                            verifier_available=verifier is not None,
                        )
                        if not selection.selected:
                            ledger.append(
                                paper_id,
                                "verifier_bypass",
                                reason=selection.reason,
                                score=assessment.score,
                                cap=selection.cap,
                            )
                        else:
                            assert verifier is not None
                            ledger.append(
                                paper_id,
                                "verifier_attempt",
                                score=assessment.score,
                                cap=selection.cap,
                                timeout_seconds=policy.timeout_seconds,
                                active=1,
                            )
                            verifier_attempted_ids.add(paper_id)
                            request = CalibrationRequest(
                                paper_id=paper_id,
                                paper_path=str(resolved["resolved_paper_path"]),
                                manifest=deepcopy(manifest),
                                lease_id=str(resolved["lease_id"]),
                                review=deepcopy(review),
                                risk=assessment,
                            )
                            try:
                                raw_decision = verifier.verify(
                                    request,
                                    timeout_seconds=policy.timeout_seconds,
                                )
                            except TimeoutError as exc:
                                ledger.append(
                                    paper_id,
                                    "verifier_timeout",
                                    error=str(exc),
                                    fail_open=True,
                                )
                            except Exception as exc:
                                ledger.append(
                                    paper_id,
                                    "verifier_failure",
                                    error=f"{type(exc).__name__}: {exc}",
                                    fail_open=True,
                                )
                            else:
                                try:
                                    decision = parse_verifier_decision(raw_decision)
                                except VerifierDecisionError as exc:
                                    ledger.append(
                                        paper_id,
                                        "verifier_malformed",
                                        errors=list(exc.errors),
                                        fail_open=True,
                                    )
                                else:
                                    if decision.verdict == "PASS":
                                        ledger.append(paper_id, "verifier_pass")
                                    else:
                                        finding_payload = [
                                            _finding_payload(finding)
                                            for finding in decision.findings
                                        ]
                                        ledger.append(
                                            paper_id,
                                            "verifier_repair_requested",
                                            findings=finding_payload,
                                        )
                                        if paper_id in repair_used_ids:
                                            ledger.append(
                                                paper_id,
                                                "repair_budget_exhausted",
                                                source="calibration",
                                            )
                                            failures.add(paper_id)
                                            active_leases.discard(str(resolved["lease_id"]))
                                            continue
                                        ledger.append(
                                            paper_id,
                                            "repair_attempt",
                                            source="calibration",
                                            fields=[
                                                finding.field_path
                                                for finding in decision.findings
                                            ],
                                        )
                                        repair_used_ids.add(paper_id)
                                        try:
                                            repaired = mock.repair_calibration(
                                                resolved,
                                                manifest,
                                                review,
                                                decision.findings,
                                            )
                                        except Exception as exc:
                                            ledger.append(
                                                paper_id,
                                                "calibration_repair_failed",
                                                error=f"{type(exc).__name__}: {exc}",
                                            )
                                            failures.add(paper_id)
                                            active_leases.discard(str(resolved["lease_id"]))
                                            continue
                                        changed = _changed_pointers(review, repaired)
                                        requested = {
                                            finding.field_path
                                            for finding in decision.findings
                                        }
                                        if not _changes_are_field_scoped(changed, requested):
                                            ledger.append(
                                                paper_id,
                                                "calibration_scope_reject",
                                                requested=sorted(requested),
                                                changed=sorted(changed),
                                            )
                                            failures.add(paper_id)
                                            active_leases.discard(str(resolved["lease_id"]))
                                            continue
                                        repaired_errors = validate_review(
                                            repaired,
                                            manifest,
                                            expected_lease_id=str(resolved["lease_id"]),
                                        )
                                        if repaired_errors:
                                            blocking_errors = _blocking_identity_errors(
                                                repaired_errors
                                            )
                                            ledger.append(
                                                paper_id,
                                                "identity_reject"
                                                if blocking_errors
                                                else "calibration_repair_failed",
                                                errors=blocking_errors or repaired_errors,
                                                source="calibration",
                                            )
                                            failures.add(paper_id)
                                            active_leases.discard(str(resolved["lease_id"]))
                                            continue
                                        review = dict(repaired)
                                        ledger.append(
                                            paper_id,
                                            "calibration_repair_validated",
                                            changed=sorted(changed),
                                        )
                review_hash = sha256_bytes(canonical_json_bytes(review))
                atomic_write_json(outbox_dir / f"{paper_id}.json", review)
                atomic_write_bytes(
                    clipboard_dir / f"{paper_id}.txt",
                    _clipboard_text(review).encode("utf-8"),
                )
                ledger.append(paper_id, "validated", review_hash=review_hash)
                idempotency_key = f"{paper_id}:{manifest['input_hash']}:{review_hash}"
                if mock.status(paper_id, "posted"):
                    ledger.append(
                        paper_id,
                        "posted_verified",
                        receipt={
                            "state": "posted",
                            "paper_id": paper_id,
                            "review_hash": review_hash,
                            "reconciled_before_action": True,
                        },
                    )
                    active_leases.discard(str(resolved["lease_id"]))
                    latencies.append(time.monotonic() - draft_started)
                    record_processed()
                    continue
                if ledger.has_state(paper_id, "post_attempt"):
                    failures.add(paper_id)
                    active_leases.discard(str(resolved["lease_id"]))
                    continue
                ledger.append(paper_id, "post_attempt", idempotency_key=idempotency_key)
                try:
                    receipt = mock.post(paper_id, review, idempotency_key)
                except TimeoutError as exc:
                    ledger.append(
                        paper_id,
                        "post_unknown",
                        idempotency_key=idempotency_key,
                        error=str(exc),
                    )
                    if not mock.status(paper_id, "posted"):
                        failures.add(paper_id)
                        active_leases.discard(str(resolved["lease_id"]))
                        continue
                    counters["post_timeout_reconciliations"] += 1
                    receipt = {
                        "state": "posted",
                        "paper_id": paper_id,
                        "review_hash": review_hash,
                        "idempotency_key": idempotency_key,
                        "reconciled": True,
                    }
                ledger.append(paper_id, "posted_verified", receipt=receipt)
                active_leases.discard(str(resolved["lease_id"]))
                latencies.append(time.monotonic() - draft_started)
                record_processed()

    audit = audit_ledger(ledger_path, assigned_ids)
    events = ledger.events
    event_states: Counter[str] = Counter(str(event.get("state")) for event in events)
    risk_events = [event for event in events if event.get("state") == "risk_assessed"]
    risk_scored_ids = {str(event["paper_id"]) for event in risk_events}
    high_risk_ids = {
        str(event["paper_id"])
        for event in risk_events
        if event.get("details", {}).get("score", -1) >= policy.risk_threshold
    }
    bypass_counts: Counter[str] = Counter(
        str(event.get("details", {}).get("reason", "unknown"))
        for event in events
        if event.get("state") == "verifier_bypass"
    )
    verifier_max_active = max(
        (
            int(event.get("details", {}).get("active", 0))
            for event in events
            if event.get("state") == "verifier_attempt"
        ),
        default=0,
    )
    repair_attempts = [
        event for event in events if event.get("state") == "repair_attempt"
    ]
    elapsed = time.monotonic() - started
    failed_ids = tuple(sorted(failures | set(audit["missing_ids"])))
    summary = RunSummary(
        mode=selected_mode.value,
        assigned_count=len(assigned_ids),
        posted_verified=int(audit["posted_verified"]),
        schema_valid_count=len(schema_valid_ids),
        duplicate_post_attempts=int(audit["duplicate_post_attempts_by_paper"]),
        duplicate_idempotency_keys=int(audit["duplicate_idempotency_keys"]),
        worker_timeout_recoveries=counters["worker_timeout_recoveries"],
        malformed_json_repairs=counters["malformed_json_repairs"],
        claim_timeout_reconciliations=counters["claim_timeout_reconciliations"],
        post_timeout_reconciliations=counters["post_timeout_reconciliations"],
        restart_recoveries=counters["restart_recoveries"],
        calibration_adapter=(
            _calibration_adapter_name(verifier) if calibration_requested else "none"
        ),
        verifier_cap=(
            calibration_cap(len(assigned_ids), policy) if calibration_requested else 0
        ),
        risk_scored_count=len(risk_scored_ids),
        high_risk_count=len(high_risk_ids),
        verifier_selected_count=event_states["verifier_attempt"],
        verifier_pass_count=event_states["verifier_pass"],
        verifier_repair_count=event_states["verifier_repair_requested"],
        verifier_timeout_count=event_states["verifier_timeout"],
        verifier_failure_count=event_states["verifier_failure"],
        verifier_malformed_count=event_states["verifier_malformed"],
        verifier_max_active=verifier_max_active,
        schema_repair_count=sum(
            event.get("details", {}).get("source") == "schema"
            for event in repair_attempts
        ),
        calibration_repair_count=sum(
            event.get("details", {}).get("source") == "calibration"
            for event in repair_attempts
        ),
        repair_budget_exhausted_count=event_states["repair_budget_exhausted"],
        verifier_bypass_counts=dict(sorted(bypass_counts.items())),
        failed_ids=failed_ids,
        elapsed_seconds=round(elapsed, 6),
        latency_p50_seconds=round(_percentile(latencies, 0.50), 6),
        latency_p95_seconds=round(_percentile(latencies, 0.95), 6),
        success=bool(audit["success"] and not failed_ids and len(schema_valid_ids) == len(assigned_ids)),
    )
    atomic_write_json(destination / "summary.json", summary.to_dict())
    return summary


def load_papers(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = payload.get("papers") if isinstance(payload, Mapping) else payload
    if not isinstance(papers, list) or not all(isinstance(item, Mapping) for item in papers):
        raise ValueError("papers input must be an array or an object containing a papers array")
    return [dict(item) for item in papers]
