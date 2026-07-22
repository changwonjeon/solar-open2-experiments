---
name: ralphthon-track2-review-agent
description: "Build, dry-run, validate, and operate an evidence-bound Ralphthon ICML Track 2 review-agent batch with frozen paper manifests, three Review Workers, deterministic ReviewDraft validation, idempotent Root-owned posting, restart recovery, and manual outbox fallback. Use for Track 2-only frozen-paper reviews, mock throughput or failure-injection runs, review schema checks, receipt audits, and the time-bounded live review window."
---

# Ralphthon Track 2 Review Agent

Preserve the official `$auto-research` Track 2-only path. Review only frozen papers and supplied evidence; do not start training, VESSL, GPU, W&B, or new experiments.

## Load the contract

Read [references/review-contract.md](references/review-contract.md) before generating or validating a draft. Read [references/runtime-runbook.md](references/runtime-runbook.md) before a batch run. Read [references/submission-contract.md](references/submission-contract.md) only when preparing submission artifacts.

## Select one mode

- `BUILD`: freeze schema, prompts, paper/evidence manifests, and local artifacts. Perform no platform side effects.
- `DRY-RUN`: use only the mock adapter. Exercise the three-worker queue, validator, ledger, failure recovery, outbox, and restart behavior without platform side effects.
- `LIVE`: enter only during the authorized live window after actual UI discovery. Root alone may claim, post, query status, or mutate the ledger. Never invent an endpoint or selector.

Use `scripts/run_batch.py` for deterministic BUILD and mock-only DRY-RUN execution. The bundled CLI rejects `LIVE` unconditionally; no programmatic production adapter is implemented. At the authorized live start, use this Skill for read-only discovery and the manual lane rather than implying that the CLI can perform live actions.

## Freeze before Worker execution

For every paper, hash the paper, evidence bundle, schema, canonical task-prompt asset, and agent version into a per-paper manifest. Separately verify `staging/ralphthon-track2-review-agent.sha256` and record that wrapper-manifest SHA in batch metadata; it freezes the native developer instructions that are not represented by per-paper `prompt_hash`. Refuse a rerun when an existing manifest identity differs. Pass the immutable manifest and one active lease to a Worker.

## Enforce authority

Run at most three persistent Review Workers. A Worker reads one frozen paper and returns only `ReviewDraft`; it must not claim, post, query platform status, write receipts, or mutate shared state. Root owns candidate discovery, the bounded queue, leases, manifest persistence, validation, posting, reconciliation, receipts, and the atomic ledger.

Before claim or post, query status. After a claim or post timeout, query status again before any retry. Treat `posted_verified == assigned_count` as success. Never retry a successful or status-reconciled post.

## Validate without field conversion

Keep upstream `contribution` and event `significance`, `originality`, and `comment` as independent fields. Never derive, alias, average, or convert them. Validate every score, evidence location, frozen hash, paper ID, lease ID, and timestamp with `scripts/validate_review.py` before Root creates a platform payload.

Allow one targeted repair for malformed or invalid Worker output. If it remains invalid, preserve the failure and continue the batch.

## Risk-gated calibration

Run the deterministic validator first. Do not send every draft to the verifier. Root assigns a risk score and sends only a schema-valid draft scoring at least 3 to `track2-review-verifier` in draft-calibration mode:

- +3 when a central numerical, table, proof, or citation claim lacks a matching evidence location or conflicts with that location;
- +2 when extraction is degraded or the Worker explicitly marks central evidence uncertain;
- +2 when an extreme recommendation conflicts with the axis scores or lacks a rationale;
- +1 when a borderline axis score lacks a borderline rationale; and
- +1 when high confidence has fewer than two auditable evidence locations.

Values such as `confidence <= 3`, `overall_recommendation <= 2`, or `overall_recommendation >= 5` are indicators only and never sufficient by themselves. Bound verifier work to `min(3, ceil(assigned_count * 0.3))` papers, one verifier at a time, 20 seconds and three findings per paper. Use it only before T+15 while validated backlog is at most two and posting pace is on target; bypass it in fast/emergency mode or after any repair. With a four-slot Root-plus-three-Worker budget, reuse a Worker slot only after that Worker has no pending draft assignment.

Keep the Python and native verifier surfaces distinct. The Python DRY-RUN runtime uses only an explicitly enabled deterministic mock verifier to exercise selection, gating, repair, and revalidation; it does not start or impersonate a native Codex agent. During a native Codex run, Root orchestrates the read-only `track2-review-verifier` role directly and retains every authority-bearing action.

Require every mock or native verifier response to validate against [assets/verifier-result.schema.json](assets/verifier-result.schema.json). Accept advisory PASS or REPAIR only. PASS preserves the ReviewDraft unchanged. REPAIR identifies one to three mutable review fields by exact JSON Pointer-style paths and cites paper locations; it never returns a rewritten review and cannot target identity or provenance fields.

Call the verifier at most once per paper. On timeout, runtime error, or malformed verifier output, record the outcome, release the unchanged deterministically valid draft, and do not retry; calibration is advisory and therefore fails open. Schema repair and calibration repair share one targeted-repair budget per paper. Bypass calibration after a schema repair. For REPAIR, Root may request only the named fields once, then reruns deterministic validation without invoking the verifier again. Reject an invalid or identity-changing repaired draft instead of posting it. Identity errors never enter this path.

## Preserve fallback artifacts

Write `outbox/<paper_id>.json` and `clipboard/<paper_id>.txt` before any post attempt. If live browser automation is unavailable or its contract remains unknown, stop automated platform side effects and continue producing validated outbox artifacts for the manual lane.

## Audit completion

Run `scripts/audit_receipts.py` over the ledger and assigned paper IDs. Report mock measurements only as mock evidence. Do not describe planned behavior or mock results as live platform performance.
