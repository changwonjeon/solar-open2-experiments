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
3. Parse P0 items from the spec. Each P0 gets a status: `pending | active | tests_passed | passed | failed | checkpoint_failed | deferred`. The distinction between `tests_passed` (tests passed, checkpoint not yet committed) and `passed` (tests passed AND checkpoint committed) is critical for `/git-checkpoint` gate validation.
4. Initialize `run-state.json` in `data/results/ralpthon/solar/<run-id>/`:
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
   - If `/git-checkpoint` returns a non-zero exit or refuses to commit, record the P0 status as `checkpoint_failed` in `p0_items`. Do **not** transition to `passed`. Record the rejection reason in the failure ledger and proceed to the failure handling path (reduction or deferral).
   - Select the next `pending` P0, mark it `active`, and proceed to the next `step` **without user input** (unless `step` has no ready P0, in which case report completion).
6. **On failure**:
   - Normalize the failure signature: `<p0-id>:<failure-type>:<short-description>` (e.g., `P0-3:test-failure:assertion-on-null-input`).
   - Append the signature to `failure-ledger.jsonl` in the run directory.
   - If the **same normalized signature** has appeared **twice before** in the ledger, stop attempting the original approach. Switch to a reduced-scope implementation or mark the P0 `deferred`.
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
   - Run `git rev-parse HEAD`. If `last_checkpoint_commit` is set, verify that it is an ancestor of HEAD (`git merge-base --is-ancestor <last_checkpoint_commit> HEAD`).
   - If the commit is **not** an ancestor, **do not auto-reset**. Mark the run `needs-operator` in state and terminate with a message explaining the mismatch.
4. **Reconcile worktree**:
   - Run `git status --porcelain=v1 -z`. If there are changes (tracked, untracked, renamed, deleted) that are **not attributable** to Solar's last checkpoint (i.e., no clear P0 mapping, or the author is uncertain), **do not attempt to stage or commit them**. Leave them untouched and set status to `needs-operator`.
5. **Reconcile active P0**:
   - If `active_p0` exists and its status is `active`, proceed to re-verify the P0's acceptance criteria before continuing implementation.
   - If `active_p0` is `null` or `passed`, select the next `pending` P0.
   - If `active_p0` is `tests_passed`, verify whether the checkpoint commit succeeded by checking `last_checkpoint_commit`. If the commit is present and the P0 still shows `tests_passed`, transition to `passed` and update `last_checkpoint_commit` in the state. If `last_checkpoint_commit` is null, the checkpoint failed — change status to `checkpoint_failed` and proceed to failure handling.
   - If `active_p0` is `checkpoint_failed`, do **not** re-attempt the same checkpoint. Proceed directly to failure handling (reduction or deferral).
6. **DO NOT trust conversation memory alone**. Re-read the task spec file, the state file, the failure ledger, and the current Git HEAD. Conversation context may be stale or compacted.
7. If reconciliation succeeds, proceed to **`step`** mode for the active P0.

**Contract:** `resume` is idempotent and safe to call multiple times. It never modifies worktree files or Git history unless reconciliation fails cleanly (in which case it writes `needs-operator` and stops).

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
   - Per-P0 table: `id | status | attempts | acceptance criteria | test commands | last result | commit (if any) | timestamps`. The status must reflect the final state: `pending`, `active`, `tests_passed`, `passed`, `failed`, `checkpoint_failed`, or `deferred`.
   - Failure summary: all entries from `failure-ledger.jsonl` with normalized signatures.
   - Unfinished work: P0s still in `pending`, `active`, `tests_passed`, or `checkpoint_failed` state.
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
pending → active → [passed | failed | deferred]
                  ↖_________________________|
                          (retry with reduction on repeated failure)
```

- A P0 enters `active` only when `step` selects it.
- A P0 leaves `active` only when `passed`, `failed`, or `deferred`.
- A P0 in `failed` state may be retried once with a reduced approach. If the same normalized failure signature recurs, it moves to `deferred`.
- A P0 in `deferred` status is not retried automatically. It is documented in HANDOFF.md as requiring operator follow-up.

---

## State Write Rules

- Every mutation to `run-state.json` is appended atomically (write to a temporary file, then rename).
- Every entry in `failure-ledger.jsonl` is a single JSON object per line, appended atomically.
- `events.jsonl` receives one JSON object per significant event (P0 activated, test started, test passed, test failed, checkpoint committed, resume reconciled, finalize triggered).
- **No secrets, prompt text, or personal identifiers are written to any state file.**
- State files are located in `data/results/ralpthon/solar/<run-id>/`. The `<run-id>` is generated at `start` time as `solar-ralph-<YYYYMMDD-HHMMSS>`.

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
