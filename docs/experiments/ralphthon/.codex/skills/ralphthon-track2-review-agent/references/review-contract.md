# Canonical Review Contract

The official upstream Track 2 result requires Summary, Strengths, Weaknesses, Questions, Soundness, Presentation, Contribution, Overall Recommendation, Confidence, Ethics/Limitations, and Evidence Trace. The event form additionally requires Significance, Originality, and Comment.

## ReviewDraft fields

Every draft contains:

- identity: `review_draft_version`, `paper_id`, `lease_id`;
- review: `summary`, `strengths`, `weaknesses`, `questions`, `comment`, `ethics_and_limitations`;
- scores: `soundness`, `presentation`, `contribution`, `significance`, `originality`, `overall_recommendation`, `confidence`;
- evidence: `evidence_trace`, one evidence-backed entry per `score_rationales` key;
- provenance: `worker_id`, `agent_version`, `prompt_hash`, `input_hash`, `evidence_hash`, `started_at`, `completed_at`.

Score ranges are Soundness, Presentation, Contribution, Significance, and Originality 1–4; Overall Recommendation 1–6; Confidence 1–5. Booleans, strings, floats, missing scores, and out-of-range values fail validation.

`contribution`, `significance`, and `originality` are separate judgments. No conversion rule exists. A platform payload may omit an internal upstream field only when the observed live form does not accept it; the local ReviewDraft must retain it.

Each strength, weakness, trace, and score rationale is an object with non-empty `claim` and `location`. Locations name a page, section, table, figure, appendix, or saved result. Missing support lowers confidence and is stated as a limitation; it is never invented.

The JSON Schema source of truth is [../assets/review-draft.schema.json](../assets/review-draft.schema.json). Its manifest identity is SHA-256 over UTF-8 canonical JSON (`sort_keys=true`, separators `,` and `:`, no insignificant whitespace): `cd19220f5435dc1da4146bd7c1e467cf4bea0ac0ecb69b2ac518b53922363d24`. The canonical task-prompt asset is [../assets/review-worker-prompt.md](../assets/review-worker-prompt.md); its per-paper `prompt_hash` hashes the UTF-8 model prompt bytes, which are the asset bytes excluding the single required final LF: `29e116b4b25663b65ff9920057a87d2b850080b97be836b364149cb95d9d914a`. Both manifest producers reject a supplied asset whose exact content differs from these frozen definitions.

The native Worker developer instructions, including evidence-first calibration, are a separate execution surface and are not represented by per-paper `prompt_hash`. Their exact staged and installed bytes are frozen by `staging/ralphthon-track2-review-agent.sha256`; Root verifies that manifest and records its SHA in batch run metadata.

## Authority boundary

The immutable per-paper manifest freezes paper/evidence identity, agent version, canonical task-prompt asset hash, and schema hash; it does not contain a lease or the wrapper-package hash. Root separately grants one active lease, passes its ID to the Worker, and requires the returned or repaired `lease_id` to equal that active value before validation can pass.

Worker input is one frozen paper manifest plus one separately granted active lease. Worker output is one ReviewDraft. Worker has no platform adapter or ledger handle. Root alone freezes manifests, grants or expires leases, validates draft lease equality, produces platform payloads, writes outbox/receipts, calls status/claim/post, and appends ledger events.

A mismatch in `paper_id`, active `lease_id`, `input_hash`, `evidence_hash`, `prompt_hash`, or `agent_version` is a blocking identity rejection and is never sent through repair. Only non-identity schema or formatting errors are eligible for the single targeted repair.

After a draft is deterministically valid, Root may route a bounded high-risk subset to the read-only verifier. The verifier receives only one frozen paper identity and ReviewDraft, returns advisory PASS or field-scoped REPAIR findings, and cannot rewrite, post, query the platform, or mutate the ledger. Schema and calibration repairs share the same one-repair-per-paper budget; Root always reruns deterministic validation after that repair.
