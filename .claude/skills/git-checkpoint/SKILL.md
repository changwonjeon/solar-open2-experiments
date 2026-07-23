---
name: git-checkpoint
description: "Narrow-purpose Git checkpoint for Ralph Loop. Called by /solar-ralph step only after a P0's tests pass. Accepts a P0 ID and one or more explicit approved pathspecs. Commits locally with strict safety gates — no remote operations, no broad git add, no destructive commands. Rejects untrusted worktree state without attempting repair."
---

# /git-checkpoint

> Local Git checkpoint for Ralph Loop P0 deliverables. **Narrow scope.** Only called by `/solar-ralph` after test verification. Does not start autonomously.

## Invocation Arguments

Claude Code invokes this skill with the arguments following the slash command:

```
/git-checkpoint $ARGUMENTS
```

| Position | Content | Required | Description |
|----------|---------|----------|-------------|
| 1 | `<p0-id>` | Yes | P0 identifier, e.g. `P0-3`. Must match the active P0 in `run-state.json`. Must conform to `P0-<number>` format. |
| 2..n | `<approved-path>...` | Yes (at least one) | One or more repository-relative paths to stage. Each path is passed individually to `git add -- <path>`. No globs, no `git add .`. |
| — | `--run-state <path>` | Yes | Path to `run-state.json` (e.g., `data/results/ralphthon/solar/solar-ralph-20260719-143022/run-state.json`). Required for Gate 5 validation. |
| — | `--summary <text>` | No | Commit message summary. Defaults to `<p0-id> deliverable` if omitted. |

**Argument handling:** `/git-checkpoint` parses `$ARGUMENTS` by first collecting all non-option arguments (positions 1 and 2..n) as `<p0-id>` and `<approved-path>...`, then processing `--run-state` and `--summary` options from the remaining tokens. If `<p0-id>` is missing, or fewer than one `<approved-path>` is provided, or `--run-state` is missing, the skill prints a usage error to stderr and exits with code 2.

**Example invocation from `/solar-ralph step`:**

```
/git-checkpoint P0-3 src/lib/foo.py src/lib/bar.py --run-state data/results/ralphthon/solar/solar-ralph-20260719-143022/run-state.json --summary "implement null-input assertion"
```

## Interface

### Execution Sequence

`/git-checkpoint` MUST be invoked as a two-script sequence. No part of the checkpoint may be executed independently:

1. **preflight.sh** runs FIRST with `--last-checkpoint <commit> --run-state <path>`. It verifies branch pattern, non-detached HEAD, upstream configuration, and baseline integrity (baseline_commit in run-state.json must equal the upstream commit; last-checkpoint must be a descendant of baseline and an ancestor of HEAD).
2. **commit-gate.sh** runs ONLY if preflight exits with code 0, passing the positional args and `--run-state <path>`. It validates approved paths, scans for secrets, verifies worktree trust, checks test evidence, stages, and commits.
3. **No invocation of either script is valid** if called with only positional arguments or missing required options.

```
/git-checkpoint <p0-id> <approved-path>...
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `<p0-id>` | string | The P0 identifier (e.g., `P0-3`). Must match the active P0 in `run-state.json`. |
| `<approved-path>...` | string (one or more) | Explicit file or directory paths to stage. Each path is passed individually to `git add`. No globs, no `git add .`. |

### Exit Behavior

- **Success (exit 0):** Commits locally. Emits exactly one JSON object to stdout containing the commit hash, approved paths, and metadata. The JSON is consumed by `/solar-ralph` to update `run-state.json`.
- **Failure (exit non-zero):** Does not commit. Emits all diagnostics to stderr. `/solar-ralph` treats this as a failure condition and records it in the failure ledger.

---

## Gates (all must pass)

The following gates are evaluated in order. The preflight must pass before commit-gate runs. If any gate fails, the checkpoint is rejected and no commit is made.

### Execution order

1. **preflight.sh** (gates A–C): Verifies branch safety and upstream baseline integrity. Exits 0 on success; on failure, emits diagnostics to stderr and exits 1. No paths are staged.
2. **commit-gate.sh** (gates 0–8): Once preflight passes, runs the full validation and commit sequence. On failure, unstages only the paths added by this invocation and leaves the worktree untouched.

### preflight.sh gates

#### Gate A: Branch pattern

The current branch must match `experiment/solar-ralph-*` pattern. If on `main`, `master`, or any other non-experiment branch, reject. Use `git symbolic-ref --short HEAD` to determine the branch name.

#### Gate B: Not detached HEAD

HEAD must not be detached. If `git symbolic-ref HEAD` fails, reject. Checkpoint commits must be on a named branch.

#### Gate C: Upstream baseline integrity

The branch must have an upstream configured via `@{u}`. The `baseline_commit` recorded in `run-state.json` must equal the upstream commit resolved via `git rev-parse --verify @{u}`. Additionally:
- The `last-checkpoint` commit must be a descendant of the baseline commit (verified via `git merge-base --is-ancestor`).
- The `last-checkpoint` commit must be an ancestor of HEAD.
- The `last-checkpoint` commit must be reachable from the upstream commit (not created on a diverged branch or after a rebase).

No remote Git commands (`fetch`, `pull`, `push`) are executed during this check.

### commit-gate.sh gates

#### Gate 0: Index pollution

At startup, `git diff --cached --name-only -z` must return empty. If any content is already staged in the index, hard fail. The checkpoint commit must start from a clean index so that only the approved paths are included. If a previous invocation of `commit-gate.sh` staged paths and then failed, the caller must have unstaged them before retrying.

#### Gate 1: Approved path validation

Each `<approved-path>` argument is validated as follows (all checks run in this order for every path before checking existence or tracked-deletion status):
- Must not be empty.
- Must not be an absolute path (must be repository-relative).
- Must not start with a dash (would be interpreted as a flag).
- Must not contain `..` components.
- Must not contain glob metacharacters (`*`, `?`, `[`).
- Must not traverse or reference `.git/` in any component.
- Each path component is checked against sensitive directory names: `_private`, `credentials`, `secrets`.
- The **basename** is checked: must not match `.env` or `.env.*`.
- The **basename** is checked: must not end with `.log`.
- Each component of the path is walked from REPO_ROOT using `test -L` to detect symlinks. A path is rejected if any component is a symlink (including broken symlinks). For tracked deletions where the full path does not exist, parent components that still exist are checked.
- Repository containment is verified by canonicalizing the path with `realpath -P` and confirming the result equals `$REPO_ROOT` or starts with `$REPO_ROOT/`.
- The path must exist on disk, or must be a tracked deletion (verified via `git cat-file -e HEAD:<path>`). Tracked deletions must have a valid path in HEAD and all persistent parent components must contain no symlinks.
- Files larger than 10 MiB are rejected. Directories are recursively scanned for oversized files.

All paths are passed to `git add` with the `--` separator to prevent ambiguity with flags.

#### Gate 2: Secret pattern content check

For each approved path that resolves to a file or directory on disk:
- Only **text files** are scanned. Binary files (detected via `file -b --mime-type`) are skipped with an informational log.
- Each text file is scanned with `grep -nIE` against a composite regex covering AWS keys, GitHub tokens, JWTs, private key headers, Slack tokens, Stripe keys, Google API keys, Shopify tokens, and other common secret formats.
- On detection, output to stderr includes **only**: the file path, line number(s), and a pattern category (e.g., `aws-key`, `github-token`). The matched content is **not** output — it is replaced with `REDACTED`.
- Symlink content is not scanned separately (symlinks are already rejected by Gate 5).

### Gate 3: Worktree trust (commit-gate.sh)

After reading the current index state (which must be empty from Gate 0), inspect the working tree using `git status --porcelain=v1 -z`. This covers:
- **Tracked modifications** (staged or unstaged)
- **Untracked files**
- **Renamed files** (format: `old_path -> new_path`)
- **Copied files** (format: `old_path -> new_path`)
- **Deleted files** (staged or unstaged)

In porcelain `-z` format, each record is NUL-terminated. For normal entries the structure is `XY<space><path><NUL>`, where the path starts at byte offset 3 (the first two characters are the status code, one space separator, then the path). For rename (`R`) and copy (`C`) entries in porcelain `-z`, the output spans **two NUL-terminated records**: the first record contains the destination path, and the second record contains the source path. Both records must be consumed as a single logical rename/copy event.

**Rename/copy handling:** If any entry has status `R` (renamed) or `C` (copied), the gate **hard fails with `needs-operator`**. The rename/copy is documented as an **operator task** — it must be manually resolved before the checkpoint can proceed. The second record (source path) is consumed by the parser but is not checked against the approved path set as an independent entry. This prevents inconsistent state where the source and destination are both treated as separate worktree changes.

For each remaining entry, determine if the path (or the path for deletions) is covered by the approved path set. An entry is covered if:
- The path exactly matches an approved path, or
- The path is under an approved directory, or
- The entry is a tracked deletion of an approved path.

If any entry is **not** covered, hard fail with `needs-operator` status. Report the path, the change type (staged/unstaged, modified/added/deleted/renamed/copied/unmerged), and the fact that it falls outside the approved set.

Note: `preflight.sh` uses `git diff --name-only <commit> HEAD` only as an **informational** aid to detect sensitive-path changes. The authoritative worktree trust check is Gate 3 in `commit-gate.sh`, which uses `git status --porcelain=v1 -z` to inspect the actual worktree state.

### Gate 4: Test evidence validation (commit-gate.sh)

The P0's test commands must have passed. This is verified by reading `run-state.json`:
- `--run-state` is **required**. Auto-discovery of the latest run directory is not performed.
- The run-state path is validated: it must exist, must not be a symlink, must be inside the repository, and must match the pattern `data/results/ralphthon/solar/solar-ralph-*/run-state.json`.
- The P0 entry must exist and its `status` field must be `tests_passed` or `checkpoint_failed`.
  - `tests_passed`: tests passed, ready for checkpoint. Proceed.
  - `checkpoint_failed`: previous checkpoint was rejected. Allow retry.
  - Any other status (`pending`, `active`, `failed`, `deferred`, `passed`) causes rejection.
- `--run-state` is parsed using Python in an `if/else` block so that a non-zero Python exit is not masked by a local variable assignment under `set -e`.

### Gate 5: Stage approved paths (commit-gate.sh)

Stage only the validated approved paths using `git add -- <path>` (with the `--` separator). Each path is staged individually. After staging, record the staged paths in a cleanup list so that on failure, only these paths are unstaged via `git restore --staged -- <path>`.

### Gate 6: Post-stage containment check (commit-gate.sh)

After staging, re-read the index with `git diff --cached --name-only -z` and verify that every staged file is covered by the approved path set (exact match or under an approved directory). If any staged file falls outside the approved set, unstage all paths added by this script and hard fail.

### Gate 7: Pre-commit validation and commit (commit-gate.sh)

1. `git diff --cached --check` must pass without whitespace or conflict marker errors.
2. Commit with `git commit -m "checkpoint(<p0-id>): <summary>"`. The `safe_git` wrapper enforces that `--amend`, `-a`, `--all`, and other prohibited options are not used.
3. Capture the commit hash (`git rev-parse HEAD`), tree status (`git status --porcelain`), and timestamp (`date -u +"%Y-%m-%dT%H:%M:%SZ"`).
4. Emit **exactly one JSON object** to stdout:

```json
{
  "commit_hash": "<sha>",
  "commit_message": "checkpoint(<p0-id>): <summary>",
  "tree_status": "<porcelain output>",
  "approved_paths": ["<path1>", "<path2>"],
  "p0_id": "<p0-id>",
  "timestamp": "<ISO-8601>"
}
```

5. On any failure after staging (gates 6–7), unstages only the paths added by this script via the cleanup list. The worktree is not modified.

---

## Commit Execution

When all gates pass:

1. Stage only the approved paths: `git add <approved-path>...` (one call per path or one call with explicit paths, never `git add .`).
2. Verify the staging area: `git diff --cached --stat` for confirmation.
3. Commit: `git commit -m "checkpoint(<p0-id>): <summary>"`.
4. Capture the resulting commit hash: `git rev-parse HEAD`.
5. Capture the tree status: `git status --porcelain`.
6. Output a JSON object to stdout (for `/solar-ralph` to parse):

```json
{
  "commit_hash": "<sha>",
  "commit_message": "checkpoint(<p0-id>): <summary>",
  "tree_status": "<porcelain output>",
  "approved_paths": ["<path1>", "<path2>"],
  "p0_id": "<p0-id>",
  "timestamp": "<ISO-8601>"
}
```

7. Return exit code 0.

---

## Prohibited Actions (Summary)

| Prohibited | Reason |
|------------|--------|
| `git push` | Remote mutation contaminates experiment isolation |
| `git pull` | Merges external changes into the run |
| `git fetch` | Alters remote tracking state |
| `git rebase` | Rewrites commit history |
| `git reset --hard` | Destructive, loses work |
| `git checkout -- <path>` | Discards uncommitted changes |
| `git clean` | Destructive, removes untracked files |
| `git commit --amend` | Rewrites commit history |
| Force options (`-f`, `--force`, `+<ref>`) | Bypasses safety checks |
| `git add .` | Stages unapproved files |
| `git add <glob>` | Broad pattern, bypasses pathspec validation |
| External `detect-secret-patterns` command | Must be self-contained in commit-gate.sh |

---

## Interaction with /solar-ralph

- Called **only** by `/solar-ralph step` after a P0's tests pass.
- Does not maintain its own state file. It reads `run-state.json` for the last checkpoint commit and P0 status.
- Does not create or modify `run-state.json`, `failure-ledger.jsonl`, or `events.jsonl`. Those are `/solar-ralph`'s responsibility.
- Does not discover or parse the task spec. It receives the P0 ID and approved paths as arguments.
- Is **not** a general-purpose Git commit tool. It exists solely to safely checkpoint Ralph Loop deliverables.

---

## References

This skill has no external references. All logic, including secret pattern detection and pathspec validation, is implemented internally in `preflight.sh` and `commit-gate.sh`.
