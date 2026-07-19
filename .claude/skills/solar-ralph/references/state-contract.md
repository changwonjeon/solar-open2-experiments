# State Contract

> Schema and format definitions for `/solar-ralph`'s persistent state files. All state files are located in `data/results/ralpthon/solar/<run-id>/`, where `<run-id>` is generated at `start` time as `solar-ralph-<YYYYMMDD-HHMMSS>`.

## File Inventory

| File | Format | Purpose |
|------|--------|---------|
| `run-state.json` | JSON (atomic write) | Primary state machine: P0 statuses, checkpoint commit, timestamps, run metadata |
| `failure-ledger.jsonl` | JSONL (append-only) | Normalized failure signatures with timestamps and context |
| `events.jsonl` | JSONL (append-only) | Significant events during the run (P0 activation, test execution, checkpoint, resume, finalize) |
| `artifact-manifest.json` | JSON (generated at finalize) | Complete inventory of files created or modified during the run |
| `HANDOFF.md` | Markdown (generated at finalize) | Human-readable handoff document |

---

## run-state.json

### Top-Level Schema

```json
{
  "schema_version": "1.0",
  "run_id": "solar-ralph-20260719-143022",
  "model": "solar-open2",
  "harness": "claude-upstage",
  "task_spec_path": "docs/experiments/ralphthon/RALPH_GOAL.md",
  "task_spec_sha256": "<hex digest of the task spec file contents at start time>",
  "baseline_commit": "<git rev-parse HEAD at start time>",
  "branch": "<git symbolic-ref --short HEAD at start time>",
  "started_at": "<ISO-8601 timestamp of run start>",
  "deadline_at": "<ISO-8601 timestamp of deadline>",
  "status": "running",
  "active_p0": "P0-3",
  "p0_items": [
    {
      "id": "P0-3",
      "status": "active",
      "attempts": 1,
      "acceptance_criteria": ["<criterion 1>", "<criterion 2>"],
      "test_commands": ["<command 1>", "<command 2>"],
      "last_result": null,
      "commit": null,
      "created_at": "<ISO-8601>",
      "updated_at": "<ISO-8601>"
    }
  ],
  "last_checkpoint_commit": null,
  "operator_interventions": [],
  "finalized_at": null,
  "finalized_reason": null
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | Schema version for forward compatibility. Current: `"1.0"`. |
| `run_id` | string | Yes | Unique run identifier. Generated at `start` as `solar-ralph-<YYYYMMDD-HHMMSS>`. |
| `model` | string | Yes | The model executing the run. Set to `"solar-open2"`. |
| `harness` | string | Yes | The execution harness. Set to `"claude-upstage"`. |
| `task_spec_path` | string | Yes | Absolute or repo-relative path to the task spec file provided to `start`. |
| `task_spec_sha256` | string | Yes | SHA-256 hex digest of the task spec file contents at `start` time. Used to detect spec modification during the run. |
| `baseline_commit` | string | Yes | Full SHA-1 of HEAD at `start` time. |
| `branch` | string | Yes | Short branch name at `start` time. |
| `started_at` | string | Yes | ISO-8601 timestamp (UTC) when `start` was invoked. |
| `deadline_at` | string | Yes | ISO-8601 timestamp (UTC) when the deadline expires (`started_at + deadline-seconds`). |
| `status` | string | Yes | Run-level status. One of: `"running"`, `"needs-operator"`, `"finalized"`. |
| `active_p0` | string or null | Yes | ID of the currently active P0, or `null` if no P0 is active. |
| `p0_items` | array | Yes | Array of P0 objects (see below). Order is stable and reflects the task spec's P0 ordering. |
| `last_checkpoint_commit` | string or null | Yes | Full SHA-1 of the most recent checkpoint commit, or `null` if no checkpoint has been made. |
| `operator_interventions` | array | Yes | List of human interventions during the run. Each entry: `{"timestamp": "<ISO-8601>", "action": "<description>"}`. |
| `finalized_at` | string or null | Yes | ISO-8601 timestamp when `finalize` was invoked, or `null` if the run is not finalized. |
| `finalized_reason` | string or null | Yes | Reason string passed to `finalize`, or `null` if not finalized. |

### P0 Item Schema

Each entry in `p0_items` is an object with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | P0 identifier (e.g., `"P0-3"`). Derived from the task spec. |
| `status` | string | Yes | One of: `"pending"`, `"active"`, `"tests_passed"`, `"passed"`, `"failed"`, `"checkpoint_failed"`, `"deferred"`. |
| | | | `"tests_passed"` — test commands passed but checkpoint commit not yet made. Transitional state. |
| | | | `"passed"` — test commands passed AND checkpoint commit successfully made. Terminal state. |
| | | | `"checkpoint_failed"` — test commands passed but checkpoint commit was rejected by `/git-checkpoint`. Retryable. |
| `attempts` | integer | Yes | Number of times this P0 has been attempted (including the current attempt). Incremented each time `step` starts working on this P0. |
| `acceptance_criteria` | array of strings | Yes | The acceptance criteria for this P0, as extracted from the task spec. Recorded at P0 activation and never modified. |
| `test_commands` | array of strings | Yes | The shell commands to verify this P0, as extracted from the task spec. Recorded at P0 activation and never modified. |
| `last_result` | object or null | Yes | Result of the most recent test execution. `null` if no test has been run yet. When set: `{"status": "passed\|failed", "output": "<truncated stdout/stderr summary>", "executed_at": "<ISO-8601>"}`. |
| `commit` | string or null | Yes | Full SHA-1 of the checkpoint commit for this P0, or `null` if no checkpoint has been made. |
| `created_at` | string | Yes | ISO-8601 timestamp when this P0 was first added to the state. |
| `updated_at` | string | Yes | ISO-8601 timestamp of the most recent state mutation for this P0. |
| `failure_signatures` | array of strings | No | Normalized failure signatures accumulated for this P0 (only present if `attempts > 0` and at least one failure occurred). Each entry: `"<p0-id>:<failure-type>:<short-description>"`. |
| `reduction_plan` | string or null | No | If the P0 was switched to a reduced-scope approach after repeated failure, this field describes the reduction. `null` otherwise. |

### Status Transitions

```
pending → active     (step selects this P0)
active → passed      (test commands pass, checkpoint committed)
active → failed      (test commands fail)
active → deferred    (same failure signature repeated, reduction not viable)
failed → active      (retry with reduced approach; attempts incremented)
deferred → (terminal) (no automatic retry)
passed → (terminal)  (no retry)
```

### Atomic Write Requirement

- Updates to `run-state.json` must be written atomically: write the new content to a temporary file in the same directory, then `mv` (rename) it over the original. This prevents corruption if the process is interrupted mid-write.
- After each mutation, the new `updated_at` timestamp must be set to the current UTC time.

---

## failure-ledger.jsonl

### Format

Each line is a valid JSON object (one per line, no comma separators between lines):

```json
{"timestamp": "2026-07-19T14:35:22Z", "signature": "P0-3:test-failure:assertion-on-null-input", "p0_id": "P0-3", "failure_type": "test-failure", "description": "assertion-on-null-input", "context": "Test command 'pytest tests/test_foo.py::test_null_input' returned exit code 1', "attempt": 1}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | string | Yes | ISO-8601 UTC timestamp when the failure was recorded. |
| `signature` | string | Yes | Normalized failure signature: `<p0-id>:<failure-type>:<short-description>`. This is the key used for deduplication. |
| `p0_id` | string | Yes | The P0 that failed. |
| `failure_type` | string | Yes | Category of failure. Suggestions: `"test-failure"`, `"compilation-error"`, `"runtime-error"`, `"timeout"`, `"permission-denied"`, `"file-not-found"`, `"invalid-input"`, `"unexpected-output"`, `"checkpoint-rejected"`. |
| `description` | string | Yes | Short human-readable description of the failure. Enough to distinguish it from other failures of the same type on the same P0. |
| `context` | string | No | Additional context (e.g., the test command that failed, the error message summary). Truncate to a reasonable length. |
| `attempt` | integer | Yes | The attempt number on which this failure occurred. |

### Deduplication Rule

- A failure is considered "the same" as a previous failure if its `signature` field matches exactly.
- The `signature` normalization rules are:
  1. `<p0-id>`: The P0 identifier (e.g., `P0-3`).
  2. `<failure-type>`: The category from the table above.
  3. `<short-description>`: A short, normalized description. Normalize by: lowercasing, removing variable values (e.g., replace specific numbers, IP addresses, tokens with placeholders), removing timestamps.
- When a new failure is recorded, check if its `signature` already exists in the ledger. If it does, increment the failure count for that signature. If the count reaches **2** (i.e., this is the second occurrence), trigger the reduction/deferral path in `/solar-ralph step`.

### Write Requirement

- Append each new failure as a single line to the file. Do not read the entire file, modify it, and rewrite it. Use shell `>>` redirection or a file append operation.
- If the file does not exist, create it with the first entry.

---

## events.jsonl

### Format

Each line is a valid JSON object:

```json
{"timestamp": "2026-07-19T14:31:00Z", "event": "p0_activated", "p0_id": "P0-3", "details": {"previous_active": null, "reason": "first-pending-selected"}}
```

### Event Types

| Event | Fields | Description |
|-------|--------|-------------|
| `run_started` | `run_id`, `model`, `harness`, `task_spec_path`, `baseline_commit`, `branch` | Emitted once at the end of `start`. |
| `p0_activated` | `p0_id`, `previous_active`, `reason` | Emitted when a P0 transitions to `active`. `previous_active` is the previously active P0 ID or `null`. |
| `acceptance_criteria_recorded` | `p0_id`, `criteria_count` | Emitted after acceptance criteria and test commands are written to state, before implementation begins. |
| `implementation_started` | `p0_id` | Emitted when the model begins making code changes for the active P0. |
| `test_started` | `p0_id`, `test_commands` | Emitted before executing the P0's test commands. |
| `test_passed` | `p0_id`, `duration_seconds` | Emitted when all test commands pass. |
| `test_failed` | `p0_id`, `failure_type`, `failure_description`, `exit_code` | Emitted when any test command fails. |
| `failure_recorded` | `p0_id`, `signature`, `is_duplicate` | Emitted when a failure is appended to the ledger. `is_duplicate` is `true` if the signature already existed. |
| `reduction_planned` | `p0_id`, `original_signature`, `reduction_description` | Emitted when the same failure signature occurs twice and a reduced approach is planned. |
| `p0_deferred` | `p0_id`, `reason` | Emitted when a P0 is marked `deferred`. |
| `p0_passed` | `p0_id`, `commit_hash` | Emitted when a P0 is marked `passed` and a checkpoint commit is made. |
| `checkpoint_committed` | `p0_id`, `commit_hash`, `approved_paths` | Emitted by `/git-checkpoint` upon successful commit. |
| `checkpoint_rejected` | `p0_id`, `reason` | Emitted when `/git-checkpoint` rejects the commit. |
| `p0_selected_next` | `p0_id` | Emitted when `step` selects the next pending P0 after the current one passes. |
| `deadline_proximity_warning` | `remaining_seconds` | Emitted when fewer than 600 seconds remain. |
| `resume_started` | `reason` | Emitted when `resume` is invoked. |
| `resume_reconciled` | `active_p0`, `last_checkpoint_commit`, `head_commit` | Emitted when `resume` successfully reconciles state and HEAD. |
| `resume_failed` | `reason` | Emitted when `resume` detects a mismatch and sets status to `needs-operator`. |
| `run_finalized` | `reason`, `p0_summary` | Emitted at the end of `finalize`. `p0_summary` is a brief count of P0s by status. |
| `operator_intervention` | `action` | Emitted when the user manually intervenes (e.g., modifies state, changes branch, provides input). |

### Write Requirement

- Append each event as a single line to the file. Use shell `>>` redirection or a file append operation.
- If the file does not exist, create it with the first entry.

---

## artifact-manifest.json

### Format

Generated at `finalize` time. A JSON object:

```json
{
  "run_id": "solar-ralph-20260719-143022",
  "generated_at": "2026-07-19T15:30:00Z",
  "files": [
    {
      "path": "src/some/file.py",
      "size_bytes": 1234,
      "status": "modified",
      "checkpoint_commit": "abc123..."
    }
  ],
  "total_files": 12,
  "total_size_bytes": 45678
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | The run ID. |
| `generated_at` | string | ISO-8601 timestamp when the manifest was generated. |
| `files` | array | List of files created or modified during the run. Each entry has `path`, `size_bytes`, `status` (`"modified"` or `"created"`), and `checkpoint_commit` (the commit hash that last touched this file, or `null`). |
| `total_files` | integer | Number of entries in `files`. |
| `total_size_bytes` | integer | Sum of `size_bytes` across all entries. |

### Generation

- Generated by `/solar-ralph finalize` by running `git diff --name-only <baseline_commit> HEAD` and `git diff --stat` to collect file paths and sizes.
- Does not include files in `_private/`, `data/results/ralpthon/solar/<run-id>/` itself, or other ignored/excluded paths.
- Does not include untracked files unless explicitly requested by the user during finalization.

---

## HANDOFF.md

### Location

`data/results/ralpthon/solar/<run-id>/HANDOFF.md`

### Content Template

See [failure-and-handoff.md](failure-and-handoff.md) for the full template and content requirements.

---

## Secrets and PII Prohibition

**No secrets, API keys, tokens, personal identifiers, or prompt text are written to any state file.**

- `run-state.json`: No prompt text, no conversation content, no API keys. Only structured data about P0s, commits, and timestamps.
- `failure_ledger.jsonl`: No prompt text. The `context` field may contain a truncated error message summary but must not include the full stderr/stdout of a failed test command.
- `events.jsonl`: No prompt text, no conversation content. Only structured event data.
- `artifact-manifest.json`: File paths and sizes only. No file contents.
- `HANDOFF.md`: May reference P0 descriptions and failure summaries but must not include raw prompts, conversation transcripts, or secret values.

If a P0's acceptance criteria or test commands contain a secret (e.g., an API key used in a test), the `/solar-ralph` skill must **not** write that secret to the state file. It should record only the fact that the criterion exists, not its full text.
