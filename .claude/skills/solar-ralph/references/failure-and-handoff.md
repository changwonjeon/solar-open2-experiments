# Failure Handling and Handoff

> Failure signature normalization, reduction strategies, and HANDOFF.md generation rules for `/solar-ralph`. Read-only reference.

## Failure Signature Normalization

### Purpose

To distinguish genuinely distinct failures from variations of the same underlying problem, so that repeated attempts at the same root cause trigger reduction or deferral rather than infinite retry.

### Normalization Algorithm

Given a raw failure description (e.g., from a test command's stderr, a compiler error, or an observed runtime behavior):

1. **Extract the P0 ID**: Identify which P0 is failing. If the failure occurs during a P0's test execution, the P0 ID is known. If it occurs outside a test (e.g., during implementation), associate it with the active P0.
2. **Classify the failure type** into one of the following categories:
   - `test-failure`: A test command returned a non-zero exit code.
   - `compilation-error`: Source code failed to compile or parse.
   - `runtime-error`: The code compiled but crashed at runtime (segfault, uncaught exception, etc.).
   - `timeout`: A command or process exceeded its allotted time.
   - `permission-denied`: A tool or file operation was denied by the OS or the Claude Code runtime.
   - `file-not-found`: A required file, module, or dependency could not be located.
   - `invalid-input`: The implementation produced output that violated the acceptance criteria or expected schema.
   - `unexpected-output`: The implementation produced output that was technically valid but semantically wrong.
   - `checkpoint-rejected`: `/git-checkpoint` refused to commit (see `git-checkpoint` skill for rejection reasons).
   - `state-corruption`: The `run-state.json` or other state file was corrupted or inconsistent.
   - `environment-error`: The failure was caused by the runtime environment (e.g., missing tool, incompatible version) rather than the implementation.
3. **Extract the short description**: From the raw failure message, extract the most informative snippet that distinguishes this failure from others of the same type on the same P0. Examples:
   - `assertion-on-null-input` (from `AssertionError: expected non-null, got None`)
   - `missing-dependency-requests` (from `ModuleNotFoundError: No module named 'requests'`)
   - `timeout-after-30s` (from `TimeoutExpired: command '...' timed out after 30s`)
4. **Normalize the description**:
   - Convert to lowercase.
   - Replace variable values with placeholders: specific numbers → `<N>`, IP addresses → `<ip>`, UUIDs → `<uuid>`, tokens/API keys → `<secret>`, file paths with volatile components → `<path>`.
   - Remove timestamps and memory addresses.
   - Truncate to 60 characters maximum.
5. **Assemble the signature**: `<p0-id>:<failure-type>:<normalized-description>`.

### Examples

| Raw Failure | Normalized Signature |
|-------------|---------------------|
| `AssertionError: expected non-null, got None at line 42` | `P0-3:test-failure:assertion-on-null-input` |
| `ModuleNotFoundError: No module named 'requests'` | `P0-3:test-failure:missing-dependency-requests` |
| `TimeoutExpired: command 'pytest tests/' timed out after 30.5s` | `P0-3:test-failure:timeout-after-30s` |
| `PermissionError: [Errno 13] Permission denied: '/etc/shadow'` | `P0-3:permission-denied:permission-denied-etc-shadow` |
| `git push origin experiment/solar-ralph-20260719-143022` (rejected by settings.deny) | `P0-3:checkpoint-rejected:remote-push-attempted` |

### Deduplication Logic

When a failure is recorded in `failure_ledger.jsonl`:

1. Compute its normalized signature as above.
2. Read the existing `failure_ledger.jsonl` and check if any entry has the same `signature` value.
3. If no match is found, append the new failure. This is the **first occurrence**.
4. If a match is found, this is the **second occurrence**. Trigger the reduction/deferral path (see below). Do not append a duplicate entry; instead, update the existing entry's `context` field with a note that this is a repeated failure, or append a new entry with `"is_repeat": true`.

---

## Reduction and Deferral Strategies

### When to Reduce

When the **same normalized failure signature** occurs for the **second time** on the same P0:

1. Do **not** retry the exact same implementation approach.
2. Evaluate whether the failure can be addressed with a **reduced scope**:
   - Can the P0 be satisfied with a simpler implementation that avoids the failure trigger?
   - Can the failing test case be narrowed to exclude the edge case that triggers the failure?
   - Can the P0 be split into two smaller P0s, with the currently failing part deferred?
3. If a reduction is viable, record the reduction plan in the P0's state (`reduction_plan` field) and proceed with the reduced implementation.
4. If no reduction is viable, mark the P0 as `deferred`.

### Reduction Examples

| Original Approach | Repeated Failure | Reduced Approach |
|-------------------|-----------------|------------------|
| Implement full error handling for all HTTP status codes | Repeated timeouts on 503 responses | Implement retry logic for 503 only; handle other codes later |
| Write comprehensive unit tests for all edge cases | Repeated test failures due to mocking complexity | Write integration tests for the happy path only |
| Refactor module to use async I/O | Repeated `ImportError` on the async library in the test environment | Keep synchronous implementation; defer async refactor |

### Deferral

A P0 marked `deferred`:

1. Is **not** retried automatically in the current run.
2. Is documented in the HANDOFF.md as requiring operator follow-up.
3. May be revisited in a future run if the operator explicitly includes it in a new task spec.
4. The reason for deferral is recorded in the P0's state and in the HANDOFF.md.

---

## HANDOFF.md Template

> Generated by `/solar-ralph finalize`. Must be written to `data/results/ralphthon/solar/<run-id>/HANDOFF.md`.

```markdown
# HANDOFF: <run-id>

## Run Metadata

| Field | Value |
|-------|-------|
| Run ID | `<run-id>` |
| Model | `<model>` |
| Harness | `<harness>` |
| Task Spec | `<task-spec-path>` (SHA-256: `<task-spec-sha256>`) |
| Branch | `<branch>` (baseline commit: `<baseline-commit>`) |
| Started At | `<started-at>` |
| Finalized At | `<finalized-at>` |
| Deadline | `<deadline-at>` |
| Finalized Reason | `<finalized-reason>` |

## P0 Status Summary

| P0 ID | Status | Attempts | Checkpoint Commit | Notes |
|-------|--------|----------|-------------------|-------|
| P0-1 | passed | 1 | `<sha>` | — |
| P0-2 | active | 2 | — | Last test failed: `<signature>` |
| P0-3 | deferred | 3 | — | Repeated failure: `<signature>`. Reduction not viable. |
| P0-4 | pending | 0 | — | Not yet started. |
| ... | ... | ... | ... | ... |

## Failure Summary

| Signature | P0 | Type | Occurrences | Last Context |
|-----------|-----|------|-------------|-------------|
| `<signature>` | P0-2 | test-failure | 2 | `<truncated context>` |
| `<signature>` | P0-3 | compilation-error | 3 | `<truncated context>` |
| ... | ... | ... | ... | ... |

## Unfinished Work

- P0(s) still `active` at finalization: `<list or "none">`
- P0(s) still `pending` at finalization: `<list or "none">`
- P0(s) `deferred`: `<list or "none">`

## Uncommitted Changes

> Files modified during the run but not committed to a checkpoint.

| File Path | Status | Last Modified |
|-----------|--------|---------------|
| `<path>` | modified | `<timestamp>` |
| ... | ... | ... |

> **Note**: Uncommitted changes have **not** been pushed remotely. The operator should review these files before deciding whether to commit them manually.

## Operator Follow-Up Items

1. **P0-3**: Deferred due to repeated `<signature>` failure. Requires human review of the test environment or implementation approach before retry.
2. **P0-2**: Active at finalization. Last test failed with `<signature>`. May be resumable if the failure is transient.
3. **Uncommitted changes**: Review `src/some/file.py` (modified but not committed) before pushing or discarding.
4. **...**: `<additional items>`

## State File Locations

All run state is located in `data/results/ralphthon/solar/<run-id>/`:

- `run-state.json` — Full state machine
- `failure-ledger.jsonl` — Normalized failure signatures
- `events.jsonl` — Event log
- `artifact-manifest.json` — File inventory
- `HANDOFF.md` — This document

## Recovery Instructions

To resume this run in a future session:

1. Start a new `claude-upstage` session in the repository root.
2. Invoke `/solar-ralph resume`.
3. The skill will reconcile `run-state.json`, Git HEAD, and the worktree.
4. If reconciliation succeeds, the skill will proceed to the active P0.
5. If reconciliation fails (e.g., due to worktree mismatch), the skill will set status to `needs-operator` and print a diagnostic message.

> **Do not** attempt to manually edit `run-state.json` or `failure-ledger.jsonl` to "fix" a failed run. If reconciliation fails, use the `needs-operator` status to request human intervention. Manual edits to state files can cause further inconsistency.
```

---

## Honesty Requirements

The handoff must be **honest and complete**. Specifically:

1. **Do not represent incomplete work as complete.** If a P0 is `active` at finalization, do not mark it `passed`. If a test was not run, do not fabricate a result.
2. **Do not omit failures.** Every entry in `failure_ledger.jsonl` must be summarized in the HANDOFF.md failure table.
3. **Do not omit uncommitted changes.** The HANDOFF.md must list all files modified during the run that were not committed, even if they appear trivial.
4. **Do not omit deferred P0s.** Every deferred P0 must be listed in the unfinished work section with its reason.
5. **Do not claim remote push was performed.** The HANDOFF.md must state that no remote push was executed during the run.
6. **Do not fabricate timestamps, commit hashes, or test results.** Every value in the HANDOFF.md must be traceable to a state file, Git commit, or test output.

---

## Interaction with /git-checkpoint on Failure

When `/solar-ralph step` calls `/git-checkpoint` and it rejects the commit:

1. `/solar-ralph` records the rejection reason in the failure ledger with `failure_type: "checkpoint-rejected"`.
2. `/solar-ralph` does **not** mark the P0 as `passed`.
3. `/solar-ralph` evaluates whether the rejection reason is transient (e.g., a temporary worktree state issue) or persistent (e.g., the implementation genuinely violates a safety gate). If transient, it may retry the checkpoint once. If persistent, it treats the P0 as failed and proceeds to failure handling (reduction or deferral).
4. The rejection reason and the retry decision are recorded in `events.jsonl` as `checkpoint_rejected` and potentially `p0_failed`.

---

## Failure Recovery Across Resume

When `/solar-ralph resume` is invoked after a session interruption:

1. The skill reads `run-state.json` and identifies the `active_p0` and its status.
2. If the P0 is `active` and its `last_result` is `null`, the skill assumes no test has been run yet and proceeds to implementation.
3. If the P0 is `active` and its `last_result` indicates a test failure, the skill evaluates whether to retry, reduce, or defer based on the failure ledger (exactly as in `step` mode).
4. If the P0 is `passed` but no checkpoint commit exists in the state, the skill flags this as a potential inconsistency and may re-run the test before proceeding.
5. If the P0 is `deferred`, the skill skips it and selects the next `pending` P0.
6. If the P0 is `failed` and this is the first failure, the skill may retry with the same approach (unless the failure ledger indicates the same signature has already occurred twice).

The resume logic is **state-driven**, not memory-driven. The skill does not rely on conversation context to determine what happened before the interruption. It re-reads all state files and Git state from scratch.
