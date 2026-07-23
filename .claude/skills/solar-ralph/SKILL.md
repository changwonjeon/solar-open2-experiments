---
name: solar-ralph
description: "Ralph Loop autonomous task execution for Solar Open2. User explicitly invokes /solar-ralph start <task-spec-path> <deadline-seconds>. Guides one P0 at a time through implementation, verification, and checkpoint. Handles failure reduction and final handoff. Does not auto-start, does not push remotely, and prioritizes state+Git over conversation memory on resume."
disable-model-invocation: true
---

# /solar-ralph

> Autonomous Ralph Loop execution skill. **Requires explicit user invocation.** Never starts on its own.

## Invocation Arguments

Claude Code invokes this skill with the arguments following the slash command. The first argument determines the mode:

```
/solar-ralph $ARGUMENTS
```

| Position 1 | Remaining arguments | Mode selected |
|------------|---------------------|---------------|
| `help` | — | `help` |
| `start` | `<task-spec-path> <deadline-seconds>` | `start` |
| `step` | — | `step` |
| `resume` | — | `resume` |
| `finalize` | `<reason>` | `finalize` |

**Validation:** If `$ARGUMENTS` is empty or the first token does not match one of `help`, `start`, `step`, `resume`, `finalize`, print the `help` output and exit.

**Argument parsing:**
- `start`: Position 2 is `<task-spec-path>` (absolute or repo-relative path to the task spec file). Position 3 is `<deadline-seconds>` (a positive integer). Any additional tokens are an error.
- `finalize`: Position 2 onward is joined with spaces to form `<reason>`.
- `step`, `resume`, `help`: No further arguments accepted.

## Interface

```
/solar-ralph help                          # Show this help
/solar-ralph start <task-spec-path> <deadline-seconds>   # Initialize a new Ralph Loop run
/solar-ralph step                           # Execute one P0 cycle (implement → verify → checkpoint)
/solar-ralph resume                         # Reconcile state after session interruption
/solar-ralph finalize <reason>              # Produce handoff and stop
```

## Modes

### `start <task-spec-path> <deadline-seconds>`

**Preconditions (verify before proceeding):**

1. Repository root, branch, and clean baseline are confirmed.
2. `<task-spec-path>` exists and is readable.
3. `<deadline-seconds>` is a positive integer.

**Actions:**

1. **Read references**: Load `references/runtime-contract.md`, `references/state-contract.md`, and `references/failure-and-handoff.md`. These define the runtime environment, state file schemas, failure normalization rules, and handoff format that govern the entire run. Keep them in context throughout the run.
2. Read the task spec file at `<task-spec-path>`. **Do not modify it.**
3. Parse P0 items from the spec. Each P0 gets a status: `pending | active | tests_passed | passed | failed | checkpoint_failed | deferred | needs-operator`. The distinction between `tests_passed` (tests passed, checkpoint not yet committed) and `passed` (tests passed AND checkpoint committed) is critical for `/git-checkpoint` gate validation. The `needs-operator` status indicates a condition that requires human intervention — no auto-retry is attempted.
4. Initialize `run-state.json` in `data/results/ralphthon/solar/<run-id>/`:
   - `schema_version`, `run_id`, `model`, `harness`
   - `task_spec_path`, `task_spec_sha256`
   - `baseline_commit`, `branch`
   - `started_at`, `deadline_at`, `status: "running"`
   - `active_p0: null`, `p0_items[]`, `last_checkpoint_commit: null`
   - `operator_interventions: []`
5. Record the baseline HEAD commit and monotonic start timestamp.
6. Select the **first ready P0** (status `pending`) and mark it `active`.
7. Record acceptance criteria and test commands for this P0 in the state file.
8. Proceed directly to **`step`** mode — do not return to the user until the step completes or fails.

**Contract:** Only one P0 is `active` at any time. Never activate a second P0 while one is already active.

---

### `step`

**Preconditions:**

1. `run-state.json` exists and `status` is `running`.
2. An `active_p0` is set, OR no P0 is active (in which case select the first `pending` P0).

**Actions (in order):**

1. **Reconcile**: If `active_p0` is already set, re-read it from state. If no active P0, select the first `pending` P0 and mark it `active`.
2. **Record acceptance criteria**: Write the P0's acceptance criteria and test commands into `run-state.json` **before** making any code changes. This is the pre-commitment.
3. **Implement**: Make the **minimum change** required to satisfy the P0. Do not add generic improvements or refactor adjacent code unless the P0 explicitly requires it.
4. **Verify**: Execute the recorded test commands. Static analysis and linting run as applicable.
5. **On success**:
   - Mark the P0 `tests_passed` in `p0_items` (not `passed` — the P0 is not fully complete until the checkpoint commit succeeds).
   - Call `/git-checkpoint <p0-id> <approved-path>... --run-state <path-to-run-state.json>` with the paths modified in this step.
   - **Checkpoints are executed as a two-script sequence**: `preflight.sh` **must** run first with `--last-checkpoint <last-commit> --run-state <run-state.json>` to verify baseline integrity, branch safety, and HEAD ancestry. If preflight exits non-zero, record the rejection as a checkpoint failure. If preflight exits 0, run `commit-gate.sh` with the positional args and `--run-state <run-state.json>` to validate paths, scan for secrets, verify worktree trust, check tests, stage, and commit.
   - **Clean baseline requirement:** The run must start from a clean baseline (HEAD matches `baseline_commit`). Preflight enforces this. If the baseline has changed since the run started, the checkpoint is rejected.
   - **Rename/copy handling:** If the worktree contains any renamed or copied files, `/git-checkpoint` rejects the checkpoint with `needs-operator` status. The rename/copy must be manually resolved before retrying. This is treated as an operator task, not an auto-resolvable condition.
   - If `/git-checkpoint` returns a commit hash (exit 0), record the commit hash in `last_checkpoint_commit` and in the P0's state, **then** transition the P0 status from `tests_passed` to `passed`.
   - If `/git-checkpoint` returns a non-zero exit or refuses to commit, record the P0 status as `checkpoint_failed` in `p0_items`. Do **not** transition to `passed`. Record the rejection reason in the failure ledger.
   - **Checkpoint retry rules:** If the checkpoint failure is transient and reparable (e.g., a temporary index.lock conflict, a brief local filesystem I/O error), auto-retry **once**. If the retry succeeds, transition `checkpoint_failed → tests_passed` and proceed with the checkpoint. If the same failure signature occurs once more (i.e., this is the second time this signature has been recorded overall), transition `checkpoint_failed → needs-operator` and stop.
   - **No auto-retry for:** rename/copy detection, sensitive path changes, unapproved path changes, branch/baseline mismatches, or any failure that requires manual resolution or policy decision. These immediately transition to `needs-operator` on first occurrence. Note: a transient network issue during commit is not a valid transient failure — `git commit` is a local operation and does not involve the network.
   - **Resume reconciliation:** When `/solar-ralph resume` processes a P0, the following four comparisons must **all** succeed individually to restore a P0 to `passed` status. If any comparison fails, or if the checkpoint event for the P0 is missing or ambiguous (e.g., duplicate entries in `events.jsonl` prevent identifying a single authoritative event), do **not** auto-resolve or auto-commit — transition the run to `needs-operator`.
     - Comparison 1: `P0.commit` (from the P0's `commit` field in `p0_items`) equals `run-state.last_checkpoint_commit`
     - Comparison 2: `HEAD` (from `git rev-parse HEAD`) equals `run-state.last_checkpoint_commit`
     - Comparison 3: The checkpoint event's `p0_id` field equals the P0's `id` field
     - Comparison 4: The checkpoint event's `commit` field equals the P0's `commit` field
   - Select the next `pending` P0, mark it `active`, and proceed to the next `step` **without user input** (unless `step` has no ready P0, in which case report completion).
6. **On failure**:
   - Normalize the failure signature: `<p0-id>:<failure-type>:<short-description>` (e.g., `P0-3:test-failure:assertion-on-null-input`).
   - Append the signature to `failure-ledger.jsonl` in the run directory.
   - If the **same normalized signature** has been recorded **once already** (i.e., this is the second overall occurrence), stop attempting the original approach. Switch to a reduced-scope implementation or mark the P0 `deferred`.
   - Record the reduced approach or deferred decision in the P0 state.
   - If time remains (deadline not within 10 minutes), select the next `pending` P0 or retry the reduced approach.
7. **Deadline proximity**: If fewer than 600 seconds (10 minutes) remain, **do not start any new implementation**. Proceed directly to `finalize deadline`.

**Contract:** Every `step` produces a verifiable outcome recorded in state. No step leaves the P0 in an ambiguous status.

---

### `resume`

**Purpose:** Recover from session interruption (context compaction, crash, prolonged pause) by reconciling state, HEAD, and worktree before proceeding.

**Actions (in order):**

1. **Read references**: Load `references/runtime-contract.md` (for tmux/watchdog environment context), `references/state-contract.md` (for state file schemas), and `references/failure-and-handoff.md` (for failure normalization and handoff format). These are essential because context compaction may have discarded earlier skill context.
2. **Read state**: Load `run-state.json` from the run directory. Read `last_checkpoint_commit`, `active_p0`, and all P0 statuses. Pay special attention to P0s in `tests_passed` (tests passed, checkpoint not yet committed) and `checkpoint_failed` (checkpoint rejected, needs retry) states.
3. **Reconcile Git HEAD**:
   - Run `git rev-parse HEAD` to get the current HEAD commit.
   - **Resume consistency contract:** To restore a P0 to `passed` status, the following values must **all** match exactly:
     - `P0.commit` (the P0's recorded commit hash in `p0_items`)
     - `run-state.last_checkpoint_commit`
     - `HEAD` (the current Git HEAD commit)
     - The `p0_id` and `commit` hash recorded in the checkpoint event for that P0
   - If **any** of these values differ, do **not** auto-reset, auto-stage, or auto-commit. Record the mismatch, set run status to `needs-operator`, and terminate with a message explaining which values were inconsistent.
   - If `last_checkpoint_commit` is set, verify that it **exactly equals** HEAD (not just an ancestor). The preflight contract requires `last_checkpoint_commit == HEAD`; any deviation is a hard failure.
   - If the values all match, reconciliation succeeds and the run continues.
4. **Reconcile worktree**:
   - Run `git status --porcelain=v1 -z`. If there are changes (tracked, untracked, renamed, deleted) that are **not attributable** to Solar's last checkpoint (i.e., no clear P0 mapping, or the author is uncertain), **do not attempt to stage or commit them**. Leave them untouched and set status to `needs-operator`.
5. **Reconcile active P0**:
   - If `active_p0` exists and its status is `active`, proceed to re-verify the P0's acceptance criteria before continuing implementation.
   - If `active_p0` is `null` or `passed`, select the next `pending` P0.
   - If `active_p0` is `tests_passed`, verify whether the checkpoint commit succeeded by performing the four resume comparisons (P0.commit == last_checkpoint_commit, HEAD == last_checkpoint_commit, checkpoint_event.p0_id == P0.id, checkpoint_event.commit == P0.commit). If all four comparisons succeed, transition to `passed`. If any comparison fails, or if the checkpoint event for this P0 is missing or ambiguous (e.g., duplicate entries in `events.jsonl` prevent identifying a single authoritative event), set status to `needs-operator` and stop.
   - If `active_p0` is `checkpoint_failed`, evaluate the failure before proceeding. If the failure was transient and reparable (e.g., temporary index.lock conflict, brief local filesystem I/O error), auto-retry the checkpoint **once**. If the same normalized failure signature is recorded once already (i.e., this is the second overall occurrence), transition to `needs-operator`. If the failure is not transient — rename/copy, sensitive path, unapproved path, branch/baseline mismatch, or any policy/scope decision — transition immediately to `needs-operator` without retry.
6. **DO NOT trust conversation memory alone**. Re-read the task spec file, the state file, the failure ledger, and the current Git HEAD. Conversation context may be stale or compacted.
7. If reconciliation succeeds, proceed to **`step`** mode for the active P0.

**Contract:** `resume` is idempotent and safe to call multiple times. It **never** modifies worktree files or Git history — on success or on failure. On failure, it records the `needs-operator` diagnosis in `run-state.json` and `events.jsonl`, then stops. No staging, committing, resetting, or file modification occurs as part of `resume`, regardless of outcome.

---

### `finalize <reason>`

**Purpose:** Produce a complete handoff and stop further work. Called on deadline, user request, or unrecoverable error.

**Actions (in order):**

1. **Read references**: Load `references/failure-and-handoff.md` for the HANDOFF.md template and content requirements. Load `references/state-contract.md` for the artifact manifest schema. These references are required to produce a correct handoff.
2. **Stop all new implementation immediately.** Do not start or continue any P0.
3. **Run final verification**: Execute the test commands for the currently `active` P0 (if any) and record the result. Do not modify the P0 status to `passed` unless the test succeeds and a checkpoint commit succeeds. Leave the P0 in its current status (`active`, `tests_passed`, `failed`, or `checkpoint_failed`) if verification fails, or transition to `passed` only after a successful checkpoint.
4. **Audit artifact manifest**: Generate or update `artifact-manifest.json` listing all files created or modified during the run, their sizes, and their paths.
5. **Generate HANDOFF.md** in the run directory containing:
   - Run ID, model, harness, start time, end time, deadline, reason for finalization.
   - Per-P0 table: `id | status | attempts | acceptance criteria | test commands | last result | commit (if any) | timestamps`. The status must reflect the final state: `pending`, `active`, `tests_passed`, `passed`, `failed`, `checkpoint_failed`, `deferred`, or `needs-operator`.
   - Failure summary: all entries from `failure-ledger.jsonl` with normalized signatures.
   - Unfinished work: P0s still in `pending`, `active`, `tests_passed`, `checkpoint_failed`, or `needs-operator` state.
   - Uncommitted changes: list of files modified but not committed, with their paths.
   - Operator follow-up items: any action that requires human intervention (e.g., `needs-operator` state, unclear worktree changes, P0s deferred due to repeated failure).
   - **Do not** represent incomplete work as complete. Do not fabricate test results.
6. **Set run status** to `finalized` in `run-state.json` with `finalized_at` and `finalized_reason`.
7. **Terminate**: Report the handoff location and summary to the user. Do not request further action from the user within this skill invocation.

**Contract:** `finalize` is the terminal mode. After it completes, no further `/solar-ralph step` or `/solar-ralph start` should be issued in the same run. A new run requires a new `start`.

---

### `help`

Outputs the interface summary:

```
/solar-ralph — Ralph Loop autonomous task execution

Commands:
  /solar-ralph help
  /solar-ralph start <task-spec-path> <deadline-seconds>
  /solar-ralph step
  /solar-ralph resume
  /solar-ralph finalize <reason>

Rules:
  - One P0 active at a time.
  - Acceptance criteria and test commands are recorded before implementation.
  - Verified changes only go to /git-checkpoint.
  - Transitions: pending → active → tests_passed → passed (via checkpoint).
  - checkpoint_failed → tests_passed (once, transient only) or → needs-operator.
  - active → failed or deferred (no direct active → passed).
  - Repeated failures trigger reduction or deferral.
  - Resume reconciles state, HEAD, and worktree — never auto-modifies.
  - Finalize produces an honest handoff. No fabrication.
  - No remote push. Ever.

References:
  - runtime-contract.md — tmux, watchdog, deadline environment
  - state-contract.md — run-state.json, failure-ledger.jsonl, events.jsonl schemas
  - failure-and-handoff.md — failure signatures, reduction paths, HANDOFF.md template
```

---

## P0 Lifecycle

```
pending → active → tests_passed → passed
                  ↘
                   → failed → deferred

tests_passed → checkpoint_failed → tests_passed  (retry after transient failure)
                           ↘
                            → needs-operator  (unrecoverable or repeated failure)

active → failed  (test commands fail; may retry with reduction)
active → deferred  (same failure repeated, reduction not viable)
```

### Transition Rules

| From | To | Trigger |
|------|----|---------|
| `pending` | `active` | `step` selects this P0 |
| `active` | `tests_passed` | Test commands pass; checkpoint not yet committed |
| `active` | `failed` | Test commands fail on implementation attempt |
| `active` | `deferred` | Same normalized failure signature repeated; reduction not viable |
| `tests_passed` | `passed` | Checkpoint commit succeeds via `/git-checkpoint` |
| `tests_passed` | `checkpoint_failed` | Checkpoint commit rejected by `/git-checkpoint` |
| `checkpoint_failed` | `tests_passed` | Transient/reparable failure; auto-retry succeeded once |
| `checkpoint_failed` | `needs-operator` | Same failure signature repeated (2nd occurrence), or failure is not transient (rename/copy, sensitive path, branch/baseline mismatch) |
| `failed` | `active` | Retry with reduced approach (attempts incremented). Only once for the same failure signature. |

### Rules

- A P0 enters `active` only when `step` selects it.
- A P0 leaves `active` only when `tests_passed`, `failed`, or `deferred`. There is **no** direct `active → passed` transition — a checkpoint commit is always required.
- A P0 in `failed` state may be retried once with a reduced approach. If the same normalized failure signature recurs, it moves to `deferred`.
- A P0 in `deferred` status is not retried automatically. It is documented in HANDOFF.md as requiring operator follow-up.
- A P0 in `checkpoint_failed` status may be retried once if the failure is transient and reparable (e.g., temporary index.lock conflict, brief local filesystem I/O error). If the same failure signature occurs twice, the P0 transitions to `needs-operator`.
- Rename/copy, sensitive path, unapproved path, or branch/baseline mismatches in `checkpoint_failed` are **never** auto-retried — they immediately require `needs-operator`.
- A transient network issue is not a valid transient failure reason: `git commit` is a local operation with no network phase.

---

## State Write Rules

- Every mutation to `run-state.json` is written atomically: the complete new JSON is written to a temporary file in the same directory, then renamed (moved) over the original. This prevents corruption if the process is interrupted mid-write.
- Every entry in `failure-ledger.jsonl` is appended as a single line (append-only). Do not read, modify, and rewrite the file.
- Every entry in `events.jsonl` is appended as a single line (append-only). Do not read, modify, and rewrite the file.
- `events.jsonl` receives one JSON object per significant event (P0 activated, test started, test passed, test failed, checkpoint committed, resume reconciled, finalize triggered).
- **No secrets, prompt text, or personal identifiers are written to any state file.**
- State files are located in `data/results/ralphthon/solar/<run-id>/`. The `<run-id>` is generated at `start` time as `solar-ralph-<YYYYMMDD-HHMMSS>`.

---

## Remote Push Prohibition

- `/solar-ralph` **never** invokes `git push`, `git fetch`, `git pull`, or any remote-affecting Git command.
- `/solar-ralph` **never** suggests or requests that the user push remotely.
- If a downstream skill or script attempts a remote Git operation, `solar-ralph` treats it as an error condition and records it in the failure ledger.
- The handoff may include instructions for a human to push after reviewing the run, but this is documentary only — no automated or semi-automated push is performed.

---

## Interaction with /git-checkpoint

- `/solar-ralph step` calls `/git-checkpoint <p0-id> <approved-path>...` **only after** the P0's test commands have passed.
- The approved paths are the exact files modified in this P0 cycle, passed as individual arguments (no globs, no `git add .`).
- `/solar-ralph` does not inspect or modify the output of `/git-checkpoint` beyond recording the returned commit hash and status in `run-state.json`.
- If `/git-checkpoint` returns a non-zero exit or refuses to commit (e.g., due to untrusted worktree state), `/solar-ralph` records the rejection in the failure ledger and does **not** mark the P0 as `passed`. It proceeds to the failure handling path.

---

## References

- [runtime-contract.md](references/runtime-contract.md) — tmux session lifecycle, watchdog behavior, deadline enforcement, launcher interface
- [state-contract.md](references/state-contract.md) — `run-state.json` schema, `failure-ledger.jsonl` format, `events.jsonl` event types, `artifact-manifest.json` structure
- [failure-and-handoff.md](references/failure-and-handoff.md) — failure signature normalization rules, reduction strategies, `HANDOFF.md` template and content requirements
