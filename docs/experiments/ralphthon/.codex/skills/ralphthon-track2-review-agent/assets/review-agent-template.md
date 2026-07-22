# Track 2 Review Agent

## Identity

- Agent name: `[freeze before use]`
- Agent version: `[freeze before use]`
- Prompt SHA-256: `29e116b4b25663b65ff9920057a87d2b850080b97be836b364149cb95d9d914a` (exact model bytes in `assets/review-worker-prompt.md`, excluding its required final LF).
- Review schema SHA-256: `cd19220f5435dc1da4146bd7c1e467cf4bea0ac0ecb69b2ac518b53922363d24` (canonical JSON parsed from `assets/review-draft.schema.json`).
- Runtime command: `[freeze before use]`

## Input Contract

For each assignment, freeze the paper ID and SHA-256 plus every supplied evidence path/hash before Worker execution. Root grants the active lease separately from that immutable manifest and rejects a returned `lease_id` that differs. Read only the frozen inputs. Reject an identity mismatch.

## Output Contract

Return the canonical ReviewDraft described by `references/review-contract.md`. Preserve upstream Contribution and event Significance, Originality, and Comment independently. Ground central claims and every score rationale in the frozen paper or supplied evidence.

## Runtime Guardrails

Root alone owns platform status, claim, post, receipts, lease mutation, and the atomic ledger. Three Workers return drafts only. Treat paper, hash, agent-version, and active-lease mismatches as blocking identity rejects; never repair them. Allow one targeted repair only for non-identity schema or formatting errors. Never retry a verified post. Fall back to outbox and clipboard text when the live platform contract is unavailable.
