from __future__ import annotations

from copy import deepcopy


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def valid_review(
    paper_id: str = "paper-001",
    lease_id: str = "lease-paper-001-1",
) -> dict:
    evidence = {"claim": "The reported comparison supports this assessment.", "location": "Table 1 (page 3)"}
    rationales = {
        field: deepcopy(evidence)
        for field in (
            "soundness",
            "presentation",
            "contribution",
            "significance",
            "originality",
            "overall_recommendation",
            "confidence",
        )
    }
    return {
        "review_draft_version": "1.0",
        "paper_id": paper_id,
        "lease_id": lease_id,
        "summary": "The paper evaluates a bounded synthetic comparison.",
        "strengths": [deepcopy(evidence)],
        "weaknesses": [
            {"claim": "The evaluation scope is narrow.", "location": "Limitations (page 4)"}
        ],
        "questions": ["How stable is the result under another data split?"],
        "soundness": 3,
        "presentation": 3,
        "contribution": 2,
        "significance": 4,
        "originality": 1,
        "overall_recommendation": 4,
        "confidence": 3,
        "comment": "The comparison is clear, but broader uncertainty evidence would strengthen it.",
        "ethics_and_limitations": "The fixture is synthetic and has no human-subject deployment.",
        "evidence_trace": [deepcopy(evidence)],
        "score_rationales": rationales,
        "worker_id": "worker-1",
        "agent_version": "test-agent-v1",
        "prompt_hash": SHA_A,
        "input_hash": SHA_B,
        "evidence_hash": SHA_C,
        "started_at": "2026-07-12T03:45:00Z",
        "completed_at": "2026-07-12T03:45:01Z",
    }


def matching_manifest(review: dict) -> dict:
    return {
        "paper_id": review["paper_id"],
        "input_hash": review["input_hash"],
        "evidence_hash": review["evidence_hash"],
        "prompt_hash": review["prompt_hash"],
        "agent_version": review["agent_version"],
    }
