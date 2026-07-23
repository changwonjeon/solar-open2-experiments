"""Pure contracts for bounded, risk-gated review calibration.

The runtime owns scheduling, repair authorization, deterministic ReviewDraft
validation, and posting.  This module only represents explicit risk signals,
decides whether the advisory verifier lane is eligible, validates the
verifier's small response contract, and supplies a deterministic test double.
It deliberately does not infer semantic paper risk from review prose.
"""

from __future__ import annotations

import math
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, Union, runtime_checkable

RISK_WEIGHTS = {
    "central_evidence_mismatch": 3,
    "extraction_degraded": 2,
    "extreme_score_conflict": 2,
    "borderline_rationale_missing": 1,
    "high_confidence_thin_evidence": 1,
}

_MUTABLE_ROOT_POINTERS = frozenset(
    {
        "/summary",
        "/strengths",
        "/weaknesses",
        "/questions",
        "/soundness",
        "/presentation",
        "/contribution",
        "/significance",
        "/originality",
        "/overall_recommendation",
        "/confidence",
        "/comment",
        "/ethics_and_limitations",
        "/evidence_trace",
    }
)
_MUTABLE_NESTED_POINTERS = (
    re.compile(r"\A/(?:strengths|weaknesses|evidence_trace)/[0-9]+(?:/(?:claim|location))?\Z"),
    re.compile(r"\A/questions/[0-9]+\Z"),
    re.compile(
        r"\A/score_rationales/(?:soundness|presentation|contribution|significance|"
        r"originality|overall_recommendation|confidence)(?:/(?:claim|location))?\Z"
    ),
)
_VERIFIER_LOCATION = re.compile(
    r"(?:[Pp]age|[Pp]\.|[Ss]ection|[Tt]able|[Ff]igure|[Aa]ppendix|[Ss]aved result)"
)
_FINDING_FIELDS = frozenset({"field_path", "problem", "location", "instruction"})
_DECISION_FIELDS = frozenset({"verdict", "findings"})


@dataclass(frozen=True)
class RiskSignals:
    """Externally established signals; no signal is inferred in this module."""

    central_evidence_mismatch: bool = False
    extraction_degraded: bool = False
    extreme_score_conflict: bool = False
    borderline_rationale_missing: bool = False
    high_confidence_thin_evidence: bool = False

    def __post_init__(self) -> None:
        invalid = [
            name
            for name in RISK_WEIGHTS
            if not isinstance(getattr(self, name), bool)
        ]
        if invalid:
            raise ValueError(f"risk signals must be boolean: {invalid}")


@dataclass(frozen=True)
class RiskAssessment:
    """Deterministic weighted assessment of explicit risk signals."""

    score: int
    reasons: tuple[str, ...]
    signals: RiskSignals


@dataclass(frozen=True)
class CalibrationPolicy:
    """Run-level verifier budget and fast-path gates."""

    enabled: bool = True
    fast_mode: bool = False
    emergency_mode: bool = False
    risk_threshold: int = 3
    max_papers: int = 3
    assignment_fraction: float = 0.30
    timeout_seconds: float = 20.0
    window_seconds: float = 15.0 * 60.0
    max_validated_backlog: int = 2

    def __post_init__(self) -> None:
        for name in ("enabled", "fast_mode", "emergency_mode"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be boolean")
        if (
            isinstance(self.risk_threshold, bool)
            or not isinstance(self.risk_threshold, int)
            or self.risk_threshold < 0
        ):
            raise ValueError("risk_threshold must be a non-negative integer")
        if (
            isinstance(self.max_papers, bool)
            or not isinstance(self.max_papers, int)
            or self.max_papers < 0
        ):
            raise ValueError("max_papers must be a non-negative integer")
        if (
            isinstance(self.assignment_fraction, bool)
            or not isinstance(self.assignment_fraction, (int, float))
            or not math.isfinite(self.assignment_fraction)
            or not 0 < self.assignment_fraction <= 1
        ):
            raise ValueError("assignment_fraction must be in (0, 1]")
        if (
            isinstance(self.timeout_seconds, bool)
            or not isinstance(self.timeout_seconds, (int, float))
            or not math.isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be positive and finite")
        if (
            isinstance(self.window_seconds, bool)
            or not isinstance(self.window_seconds, (int, float))
            or not math.isfinite(self.window_seconds)
            or self.window_seconds < 0
        ):
            raise ValueError("window_seconds must be non-negative and finite")
        if (
            isinstance(self.max_validated_backlog, bool)
            or not isinstance(self.max_validated_backlog, int)
            or self.max_validated_backlog < 0
        ):
            raise ValueError("max_validated_backlog must be a non-negative integer")


@dataclass(frozen=True)
class CalibrationGateSnapshot:
    """Observable scheduling state captured immediately before selection."""

    elapsed_seconds: float
    validated_backlog: int
    posting_pace_on_target: bool
    pending_draft_assignments: bool = False

    def __post_init__(self) -> None:
        if (
            isinstance(self.elapsed_seconds, bool)
            or not isinstance(self.elapsed_seconds, (int, float))
            or not math.isfinite(self.elapsed_seconds)
            or self.elapsed_seconds < 0
        ):
            raise ValueError("elapsed_seconds must be non-negative and finite")
        if (
            isinstance(self.validated_backlog, bool)
            or not isinstance(self.validated_backlog, int)
            or self.validated_backlog < 0
        ):
            raise ValueError("validated_backlog must be a non-negative integer")
        if not isinstance(self.posting_pace_on_target, bool):
            raise ValueError("posting_pace_on_target must be boolean")
        if not isinstance(self.pending_draft_assignments, bool):
            raise ValueError("pending_draft_assignments must be boolean")


@dataclass(frozen=True)
class CalibrationRequest:
    """Read-only input envelope for one independent verifier call."""

    paper_id: str
    paper_path: str
    manifest: Mapping[str, Any]
    lease_id: str
    review: Mapping[str, Any]
    risk: RiskAssessment


@dataclass(frozen=True)
class VerifierFinding:
    """One field-scoped correction request tied to a paper location."""

    field_path: str
    problem: str
    location: str
    instruction: str


@dataclass(frozen=True)
class VerifierDecision:
    """Strict advisory result.  PASS contains no findings; REPAIR contains 1..3."""

    verdict: str
    findings: tuple[VerifierFinding, ...] = ()


@dataclass(frozen=True)
class CalibrationSelection:
    """Pure policy result suitable for ledger counters."""

    selected: bool
    reason: str
    cap: int


class VerifierDecisionError(ValueError):
    """Raised when verifier output violates the bounded response contract."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@runtime_checkable
class VerifierPort(Protocol):
    """Narrow dependency-injection boundary; it has no mutation authority."""

    def verify(
        self,
        request: CalibrationRequest,
        timeout_seconds: float = 20.0,
    ) -> Union[VerifierDecision, Mapping[str, Any]]:
        ...


def assess_risk(signals: RiskSignals) -> RiskAssessment:
    """Return the weighted sum of explicit signals in stable rubric order."""

    if not isinstance(signals, RiskSignals):
        raise TypeError("signals must be RiskSignals")
    reasons = tuple(name for name in RISK_WEIGHTS if getattr(signals, name))
    score = sum(RISK_WEIGHTS[name] for name in reasons)
    return RiskAssessment(score=score, reasons=reasons, signals=signals)


def calibration_cap(
    assigned_count: int,
    policy: CalibrationPolicy | None = None,
) -> int:
    """Return ``min(3, ceil(30% * assignments))`` under the supplied policy."""

    if isinstance(assigned_count, bool) or not isinstance(assigned_count, int):
        raise TypeError("assigned_count must be an integer")
    if assigned_count < 0:
        raise ValueError("assigned_count must be non-negative")
    effective_policy = policy or CalibrationPolicy()
    return min(
        effective_policy.max_papers,
        int(math.ceil(assigned_count * effective_policy.assignment_fraction)),
    )


def select_for_calibration(
    policy: CalibrationPolicy,
    risk: RiskAssessment,
    gate: CalibrationGateSnapshot,
    *,
    assigned_count: int,
    selected_count: int,
    repaired: bool = False,
    verifier_available: bool = True,
) -> CalibrationSelection:
    """Apply all fast-path gates without side effects.

    Boundary semantics are intentional: risk equal to the threshold qualifies,
    elapsed time equal to the window does not, backlog equal to the maximum does,
    and the cap is fixed from the original assignment count.
    """

    if not isinstance(policy, CalibrationPolicy):
        raise TypeError("policy must be CalibrationPolicy")
    if not isinstance(risk, RiskAssessment):
        raise TypeError("risk must be RiskAssessment")
    if not isinstance(gate, CalibrationGateSnapshot):
        raise TypeError("gate must be CalibrationGateSnapshot")
    if isinstance(selected_count, bool) or not isinstance(selected_count, int):
        raise TypeError("selected_count must be an integer")
    if selected_count < 0:
        raise ValueError("selected_count must be non-negative")
    if not isinstance(repaired, bool) or not isinstance(verifier_available, bool):
        raise TypeError("repaired and verifier_available must be boolean")

    cap = calibration_cap(assigned_count, policy)
    if not policy.enabled or not verifier_available:
        return CalibrationSelection(False, "unavailable", cap)
    if policy.fast_mode:
        return CalibrationSelection(False, "fast", cap)
    if policy.emergency_mode:
        return CalibrationSelection(False, "emergency", cap)
    if gate.pending_draft_assignments:
        return CalibrationSelection(False, "pending_drafts", cap)
    if risk.score < policy.risk_threshold:
        return CalibrationSelection(False, "below_threshold", cap)
    if gate.elapsed_seconds >= policy.window_seconds:
        return CalibrationSelection(False, "t15", cap)
    if gate.validated_backlog > policy.max_validated_backlog:
        return CalibrationSelection(False, "backlog", cap)
    if not gate.posting_pace_on_target:
        return CalibrationSelection(False, "slow_pace", cap)
    if repaired:
        return CalibrationSelection(False, "prior_repair", cap)
    if selected_count >= cap:
        return CalibrationSelection(False, "budget_exhausted", cap)
    return CalibrationSelection(True, "selected", cap)


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_mutable_pointer(value: str) -> bool:
    return value in _MUTABLE_ROOT_POINTERS or any(
        pattern.fullmatch(value) for pattern in _MUTABLE_NESTED_POINTERS
    )


def _parse_finding(raw: Any, index: int, errors: list[str]) -> VerifierFinding | None:
    label = f"findings[{index}]"
    if not isinstance(raw, Mapping):
        errors.append(f"{label}: expected object")
        return None
    fields = frozenset(raw)
    missing = sorted(_FINDING_FIELDS - fields, key=str)
    extra = sorted(fields - _FINDING_FIELDS, key=str)
    if missing:
        errors.append(f"{label}: missing fields {missing}")
    if extra:
        errors.append(f"{label}: unexpected fields {extra}")

    for name in _FINDING_FIELDS:
        if not _nonempty_text(raw.get(name)):
            errors.append(f"{label}.{name}: expected non-empty string")
    field_path = raw.get("field_path")
    if _nonempty_text(field_path):
        assert isinstance(field_path, str)
        if not _is_mutable_pointer(field_path):
            errors.append(f"{label}.field_path: expected allowed RFC 6901 ReviewDraft pointer")
    location = raw.get("location")
    for name, maximum in (("problem", 1000), ("location", 500), ("instruction", 1000)):
        value = raw.get(name)
        if isinstance(value, str) and len(value) > maximum:
            errors.append(f"{label}.{name}: exceeds {maximum} characters")
    if _nonempty_text(location) and not _VERIFIER_LOCATION.search(location):
        errors.append(
            f"{label}.location: expected page, section, table, figure, appendix, or saved result"
        )
    if missing or extra or any(
        not _nonempty_text(raw.get(name)) for name in _FINDING_FIELDS
    ):
        return None
    if not isinstance(field_path, str) or not _is_mutable_pointer(field_path):
        return None
    if not isinstance(location, str) or not _VERIFIER_LOCATION.search(location):
        return None
    if any(
        not isinstance(raw.get(name), str) or len(raw[name]) > maximum
        for name, maximum in (("problem", 1000), ("location", 500), ("instruction", 1000))
    ):
        return None
    return VerifierFinding(
        field_path=field_path,
        problem=str(raw["problem"]).strip(),
        location=location.strip(),
        instruction=str(raw["instruction"]).strip(),
    )


def parse_verifier_decision(raw: Any) -> VerifierDecision:
    """Validate and normalize one PASS/REPAIR verifier response.

    Unknown fields, non-allowlisted RFC 6901 pointers, untraceable locations,
    oversized text, duplicate paths, and more than three findings are rejected.
    """

    if isinstance(raw, VerifierDecision):
        raw = {
            "verdict": raw.verdict,
            "findings": [
                {
                    "field_path": finding.field_path,
                    "problem": finding.problem,
                    "location": finding.location,
                    "instruction": finding.instruction,
                }
                for finding in raw.findings
            ],
        }
    if not isinstance(raw, Mapping):
        raise VerifierDecisionError(["decision: expected object"])

    errors: list[str] = []
    fields = frozenset(raw)
    missing = sorted(_DECISION_FIELDS - fields, key=str)
    extra = sorted(fields - _DECISION_FIELDS, key=str)
    if missing:
        errors.append(f"decision: missing fields {missing}")
    if extra:
        errors.append(f"decision: unexpected fields {extra}")

    verdict = raw.get("verdict")
    if not isinstance(verdict, str) or verdict not in {"PASS", "REPAIR"}:
        errors.append("verdict: expected 'PASS' or 'REPAIR'")
    raw_findings = raw.get("findings")
    if not isinstance(raw_findings, list):
        errors.append("findings: expected array")
        raw_findings = ()

    findings: list[VerifierFinding] = []
    for index, item in enumerate(raw_findings):
        parsed = _parse_finding(item, index, errors)
        if parsed is not None:
            findings.append(parsed)
    if verdict == "PASS" and raw_findings:
        errors.append("findings: PASS must contain no findings")
    if verdict == "REPAIR" and not 1 <= len(raw_findings) <= 3:
        errors.append("findings: REPAIR must contain 1..3 findings")
    paths = [finding.field_path for finding in findings]
    if len(paths) != len(set(paths)):
        errors.append("findings: duplicate field paths are forbidden")

    if errors:
        raise VerifierDecisionError(errors)
    assert isinstance(verdict, str)
    return VerifierDecision(verdict=verdict, findings=tuple(findings))


class MockVerifier:
    """Deterministic DRY-RUN verifier test double with observable calls.

    ``scripts`` maps paper IDs to a decision, raw mapping, exception, or one of
    the fault tokens ``timeout``, ``failure``, and ``malformed``.  Missing paper
    IDs receive PASS.  No network, model, filesystem, or platform call occurs.
    """

    adapter_name = "mock"

    def __init__(
        self,
        scripts: Mapping[str, Any] | None = None,
        *,
        delay_seconds: float = 0.0,
    ) -> None:
        if (
            isinstance(delay_seconds, bool)
            or not isinstance(delay_seconds, (int, float))
            or not math.isfinite(delay_seconds)
            or delay_seconds < 0
        ):
            raise ValueError("delay_seconds must be non-negative and finite")
        self.scripts = dict(scripts or {})
        self.delay_seconds = delay_seconds
        self.calls: list[str] = []
        self.max_active = 0
        self._active = 0
        self._lock = threading.Lock()

    def verify(
        self,
        request: CalibrationRequest,
        timeout_seconds: float = 20.0,
    ) -> Union[VerifierDecision, Mapping[str, Any]]:
        if not isinstance(request, CalibrationRequest):
            raise TypeError("request must be CalibrationRequest")
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds)
            or timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be positive and finite")
        with self._lock:
            self.calls.append(request.paper_id)
            self._active += 1
            self.max_active = max(self.max_active, self._active)
        try:
            if self.delay_seconds > timeout_seconds:
                raise TimeoutError(f"mock verifier timeout for {request.paper_id}")
            if self.delay_seconds:
                time.sleep(self.delay_seconds)
            scripted = self.scripts.get(request.paper_id, VerifierDecision("PASS"))
            if isinstance(scripted, BaseException):
                raise scripted
            if scripted == "timeout":
                raise TimeoutError(f"mock verifier timeout for {request.paper_id}")
            if scripted == "failure":
                raise RuntimeError(f"mock verifier failure for {request.paper_id}")
            if scripted == "malformed":
                return {"verdict": "PASS", "findings": "not-an-array"}
            if not isinstance(scripted, (VerifierDecision, Mapping)):
                raise TypeError(
                    "mock verifier script must be a decision, mapping, exception, or fault token"
                )
            return scripted
        finally:
            with self._lock:
                self._active -= 1
