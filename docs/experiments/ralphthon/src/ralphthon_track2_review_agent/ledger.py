"""Root-owned append-only event ledger with an atomic read model."""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .io_utils import atomic_write_json, canonical_json_bytes


class LedgerOwnershipError(PermissionError):
    """Raised when a non-root authority attempts to mutate the ledger."""


class AtomicLedger:
    """Append each event with one O_APPEND write and atomically replace its snapshot."""

    def __init__(self, path: str | Path, *, owner: str = "root-coordinator") -> None:
        if owner != "root-coordinator":
            raise LedgerOwnershipError("only root-coordinator may own the ledger")
        self.path = Path(path)
        self.snapshot_path = self.path.with_name(f"{self.path.stem}.state.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._lock = threading.RLock()
        self._events = self._load_events()
        self._latest = self._rebuild_latest(self._events)
        self._write_snapshot()

    def _load_events(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid ledger JSON at line {line_number}") from exc
                if not isinstance(event, dict):
                    raise ValueError(f"ledger line {line_number} is not an object")
                events.append(event)
        return events

    @staticmethod
    def _rebuild_latest(events: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for event in events:
            paper_id = event.get("paper_id")
            if isinstance(paper_id, str) and paper_id:
                latest[paper_id] = dict(event)
        return latest

    def _write_snapshot(self) -> None:
        atomic_write_json(
            self.snapshot_path,
            {
                "event_count": len(self._events),
                "latest": self._latest,
            },
        )

    def append(self, paper_id: str, state: str, **details: Any) -> dict[str, Any]:
        if not paper_id or not state:
            raise ValueError("paper_id and state are required")
        with self._lock:
            event = {
                "sequence": len(self._events) + 1,
                "event_uuid": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "paper_id": paper_id,
                "state": state,
                "details": details,
            }
            encoded = canonical_json_bytes(event) + b"\n"
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
            try:
                written = os.write(descriptor, encoded)
                if written != len(encoded):
                    raise OSError("short atomic ledger write")
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            self._events.append(event)
            self._latest[paper_id] = event
            self._write_snapshot()
            return event

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(event) for event in self._events)

    def latest(self, paper_id: str) -> dict[str, Any] | None:
        event = self._latest.get(paper_id)
        return dict(event) if event else None

    def has_state(self, paper_id: str, state: str) -> bool:
        return any(
            event.get("paper_id") == paper_id and event.get("state") == state
            for event in self._events
        )

    def posted_verified_ids(self) -> set[str]:
        return {
            str(event["paper_id"])
            for event in self._events
            if event.get("state") == "posted_verified"
        }

    def idempotency_keys(self) -> set[str]:
        keys: set[str] = set()
        for event in self._events:
            key = event.get("details", {}).get("idempotency_key")
            if isinstance(key, str):
                keys.add(key)
        return keys


def audit_ledger(path: str | Path, assigned_ids: Iterable[str] | None = None) -> dict[str, Any]:
    ledger = AtomicLedger(path)
    events = ledger.events
    assigned = set(assigned_ids or (event["paper_id"] for event in events))
    posted = ledger.posted_verified_ids()
    post_events = [event for event in events if event.get("state") == "post_attempt"]
    keys = [event.get("details", {}).get("idempotency_key") for event in post_events]
    nonempty_keys = [key for key in keys if isinstance(key, str) and key]
    duplicate_keys = len(nonempty_keys) - len(set(nonempty_keys))
    duplicate_papers = len(post_events) - len({event["paper_id"] for event in post_events})
    return {
        "assigned_count": len(assigned),
        "posted_verified": len(posted & assigned),
        "missing_ids": sorted(assigned - posted),
        "unexpected_posted_ids": sorted(posted - assigned),
        "post_attempt_count": len(post_events),
        "duplicate_idempotency_keys": duplicate_keys,
        "duplicate_post_attempts_by_paper": duplicate_papers,
        "success": assigned == posted and duplicate_keys == 0 and duplicate_papers == 0,
    }
