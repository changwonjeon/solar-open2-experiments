#!/bin/zsh
set -euo pipefail

# preflight.sh -- Git safety preflight for git-checkpoint skill
#
# Verifies that the repository is in a safe state for a Ralph Loop
# checkpoint commit. Runs before commit-gate.sh. Does not modify the
# worktree or Git history. Does NOT execute any remote Git commands
# (fetch, pull, push); all checks are local-only.
#
# Usage:
#   preflight.sh --last-checkpoint <commit> --run-state <path>
#
# Arguments:
#   --last-checkpoint <commit>  Full SHA-1 of the last checkpoint commit (REQUIRED).
#                               For the first checkpoint in a run this must equal
#                               baseline_commit; for subsequent checkpoints it must
#                               equal last_checkpoint_commit from run-state.json.
#   --run-state <path>          Repository-relative path to run-state.json (REQUIRED)
#   --help, -h                  Show this help
#
# Gates:
#   1. Branch pattern + exact match:
#      - Condition A: current branch must match 'experiment/solar-ralph-*' pattern.
#        Prevents checkpointing on main, master, or any non-experiment branch.
#      - Condition B: current branch must exactly equal run-state.branch.
#        Prevents branch switching or mismatched run-state after start.
#   2. Not detached HEAD: HEAD must be on a named branch.
#   3. Known local baseline integrity (via @{u}):
#      - Verifies that baseline_commit from run-state.json equals git rev-parse @{u}^{commit}.
#      - This is a required local gate — upstream absence or baseline mismatch is a hard failure.
#      - WARNING: @{u} reflects the local upstream-tracking ref only. It does NOT
#        prove the remote branch is at the same commit. No fetch/pull/push is
#        executed. The @{u} value is a local cached ref that may be stale if the
#        remote was updated without the local ref being refreshed.
#   4. Checkpoint baseline integrity:
#      - Uses last_checkpoint_commit from run-state.json to determine checkpoint type.
#      - First checkpoint (null): --last-checkpoint == baseline_commit AND HEAD == baseline_commit.
#      - Subsequent checkpoint (non-null SHA): --last-checkpoint == LAST_CHECKPOINT_COMMIT_FROM_STATE AND HEAD == LAST_CHECKPOINT_COMMIT_FROM_STATE.
#      - All comparisons are independent. Mismatch on any is a hard failure.
#      - No auto-reset, no auto-commit, no remote Git operations.
#
# Exit codes:
#   0 -- all gates passed
#   1 -- a gate failed; diagnostics emitted to stderr
#   2 -- usage error
#
# Output contract:
#   stderr -- all PASS, WARNING, ERROR, INFO diagnostics
#   stdout -- none

# --- Argument parsing ---
LAST_CHECKPOINT=""
RUN_STATE_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --last-checkpoint)
      if [[ $# -lt 2 ]]; then
        print -r -u2 "ERROR: --last-checkpoint requires an argument" >&2
        exit 2
      fi
      LAST_CHECKPOINT="$2"
      shift 2
      ;;
    --run-state)
      if [[ $# -lt 2 ]]; then
        print -r -u2 "ERROR: --run-state requires an argument" >&2
        exit 2
      fi
      RUN_STATE_PATH="$2"
      shift 2
      ;;
    --help|-h)
      print -r -u2 "Usage: preflight.sh --last-checkpoint <commit> --run-state <path>"
      print -r -u2 ""
      print -r -u2 "OPTIONS:"
      print -r -u2 "  --last-checkpoint <commit>"
      print -r -u2 "      Full SHA-1 of the checkpoint baseline commit. REQUIRED."
      print -r -u2 "      For the first checkpoint: must equal baseline_commit from run-state.json."
      print -r -u2 "      For subsequent checkpoints: must equal last_checkpoint_commit from run-state.json."
      print -r -u2 "      HEAD must exactly equal this value. No ancestry checks are performed."
      print -r -u2 "  --run-state <path>"
      print -r -u2 "      Repository-relative path to run-state.json. REQUIRED."
      print -r -u2 "      Used to retrieve baseline_commit, branch, run_id, and last_checkpoint_commit."
      print -r -u2 "      Must be a repository-relative path (not absolute)."
      print -r -u2 "  --help, -h"
      print -r -u2 "      Show this help and exit."
      exit 0
      ;;
    --*)
      print -r -u2 "ERROR: Unknown option: $1" >&2
      exit 2
      ;;
    *)
      print -r -u2 "ERROR: Unexpected argument: $1" >&2
      exit 2
      ;;
  esac
done

# --- Argument validation ---
if [[ -z "$LAST_CHECKPOINT" ]]; then
  print -r -u2 "ERROR: --last-checkpoint is required"
  print -r -u2 "Usage: preflight.sh --last-checkpoint <commit> --run-state <path>"
  exit 2
fi

if [[ -z "$RUN_STATE_PATH" ]]; then
  print -r -u2 "ERROR: --run-state is required"
  print -r -u2 "Usage: preflight.sh --last-checkpoint <commit> --run-state <path>"
  exit 2
fi

# --- Determine repository root ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  print -r -u2 "ERROR: Not inside a Git repository" >&2
  exit 1
fi
cd "$REPO_ROOT"

# --- Retrieve and validate values from run-state.json ---
# Reads 4 fields from run-state.json and validates the schema strictly:
#   baseline_commit  : required, must be a non-null, non-empty string
#   branch           : required, must be a non-null, non-empty string
#   run_id           : required, must be a non-null, non-empty string
#   last_checkpoint_commit: required; null → first checkpoint; non-null string → subsequent checkpoint;
#                           missing / empty / non-string → error
# Python is invoked with the path as argv[1] (not via an environment variable).
# On any validation failure, Python exits non-zero with a redacted diagnostic on stderr.
# The caller inspects the exit code: non-zero → hard fail, zero → use the 4 printed lines.
BASELINE_COMMIT=""
RUN_BRANCH=""
LAST_CHECKPOINT_COMMIT_FROM_STATE=""
RUN_ID_RAW=""
if [[ -f "$RUN_STATE_PATH" ]]; then
  RS_EXIT=0
  RS_CONTENT="$(python3 - "$RUN_STATE_PATH" <<'PY' || RS_EXIT=$?
import json, sys

rs_path = sys.argv[1]
try:
    with open(rs_path, 'r') as f:
        state = json.load(f)
except Exception:
    # Redact the actual error; the path itself is the identifier.
    print("PARSE_ERROR", file=sys.stderr)
    sys.exit(1)

REQUIRED_STR_FIELDS = ['baseline_commit', 'branch', 'run_id']
for key in REQUIRED_STR_FIELDS:
    if key not in state:
        print(f"MISSING:{key}", file=sys.stderr)
        sys.exit(1)
    val = state[key]
    if val is None or not isinstance(val, str) or val == "":
        print(f"INVALID:{key}", file=sys.stderr)
        sys.exit(1)
    print(val)

# last_checkpoint_commit: required field, but null is valid (first checkpoint).
if 'last_checkpoint_commit' not in state:
    print("MISSING:last_checkpoint_commit", file=sys.stderr)
    sys.exit(1)
val = state['last_checkpoint_commit']
if val is None:
    # JSON null → first checkpoint sentinel
    print("__NULL__")
elif isinstance(val, str) and val != "":
    print(val)
else:
    # empty string or non-string type → error
    print("INVALID:last_checkpoint_commit", file=sys.stderr)
    sys.exit(1)
PY
)"
  if [[ $RS_EXIT -ne 0 ]]; then
    # Python exited non-zero: schema/parse error. The redacted diagnostic is on
    # stderr (already emitted by Python). We do not attempt to parse stdout.
    print -r -u2 "ERROR: run-state.json schema validation failed" >&2
    print -r -u2 "       The file at $RUN_STATE_PATH is missing required fields,"
    print -r -u2 "       contains null or empty values where strings are required,"
    print -r -u2 "       or has a type mismatch. See Python stderr above for details." >&2
    exit 1
  fi
  # Parse the 4-line output (always exactly 4 lines on success)
  RS_LINES=("${(@f)RS_CONTENT}")
  BASELINE_COMMIT="${RS_LINES[1]}"
  RUN_BRANCH="${RS_LINES[2]}"
  RUN_ID_RAW="${RS_LINES[3]}"
  LAST_CHECKPOINT_COMMIT_FROM_STATE="${RS_LINES[4]}"
else
  print -r -u2 "ERROR: --run-state file does not exist: $RUN_STATE_PATH" >&2
  exit 2
fi

if [[ -z "$BASELINE_COMMIT" ]]; then
  print -r -u2 "ERROR: Could not read baseline_commit from run-state.json" >&2
  exit 1
fi

# --- Gate 1: Branch pattern + exact match ---
BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || echo "")"
if [[ -z "$BRANCH" ]]; then
  print -r -u2 "ERROR: GATE 1 FAILED -- Unable to determine branch name" >&2
  exit 1
fi

# Condition A: current branch must match the experiment/solar-ralph-* pattern.
# This prevents checkpointing on main, master, or any non-experiment branch.
if ! [[ "$BRANCH" =~ ^experiment/solar-ralph- ]]; then
  print -r -u2 "ERROR: GATE 1 FAILED -- Branch '$BRANCH' does not match 'experiment/solar-ralph-*' pattern" >&2
  print -r -u2 "       Checkpoint commits are only allowed on experiment/solar-ralph-* branches." >&2
  exit 1
fi

# Condition B: current branch must exactly equal run-state.branch.
# run-state.branch is required (validated by the schema parser before Gate 1 runs).
# This prevents a scenario where the user manually switched branches after start,
# or where run-state records a different experiment branch than the one currently checked out.
if [[ "$BRANCH" != "$RUN_BRANCH" ]]; then
  print -r -u2 "ERROR: GATE 1 FAILED -- Branch mismatch with run-state" >&2
  print -r -u2 "       current branch:    $BRANCH" >&2
  print -r -u2 "       run-state.branch:  $RUN_BRANCH" >&2
  print -r -u2 "       The two must be identical. No branch creation or switching is allowed during the run." >&2
  exit 1
fi

print -r -u2 "PASS: Gate 1 -- Branch '$BRANCH' matches pattern and run-state.branch"

# --- Gate 2: Not detached HEAD ---
if ! git symbolic-ref HEAD >/dev/null 2>&1; then
  print -r -u2 "ERROR: GATE 2 FAILED -- HEAD is detached. Checkpoint commits must be on a named branch." >&2
  exit 1
fi
print -r -u2 "PASS: Gate 2 -- HEAD is on named branch '$BRANCH' (not detached)"

# --- Gate 3: Known local baseline integrity (via @{u}) ---
# Verifies that the baseline_commit recorded in run-state.json equals the
# commit resolved via the local upstream-tracking ref @{u}.
# This is a required local gate — upstream absence or baseline mismatch is a hard failure.
# WARNING: @{u} reflects the local upstream-tracking ref only. It does NOT
# prove the remote branch is at the same commit. No fetch/pull/push is
# executed. The @{u} value is a local cached ref that may be stale if the
# remote was updated without the local ref being refreshed.

UPSTREAM_REF="$(git rev-parse --verify @{u} 2>/dev/null || echo "")"
if [[ -z "$UPSTREAM_REF" ]]; then
  print -r -u2 "ERROR: GATE 3 FAILED -- No upstream configured for branch '$BRANCH'" >&2
  print -r -u2 "       The baseline must have been pushed before the run started." >&2
  print -r -u2 "       Run: git push -u origin $BRANCH" >&2
  exit 1
fi
print -r -u2 "PASS: Gate 3 -- Upstream configured: $UPSTREAM_REF"

# Resolve the upstream commit via @{u}^{commit}
UPSTREAM_COMMIT="$(git rev-parse "${UPSTREAM_REF}^{commit}" 2>/dev/null || echo "")"
if [[ -z "$UPSTREAM_COMMIT" ]]; then
  print -r -u2 "ERROR: GATE 3 FAILED -- Could not resolve upstream commit from @{u}" >&2
  exit 1
fi

# Check: baseline_commit must equal the upstream commit.
# This ensures the local baseline recorded at start matches the upstream-tracking ref.
if [[ "$BASELINE_COMMIT" != "$UPSTREAM_COMMIT" ]]; then
  print -r -u2 "ERROR: GATE 3 FAILED -- baseline_commit does not match upstream commit" >&2
  print -r -u2 "       baseline_commit: $BASELINE_COMMIT" >&2
  print -r -u2 "       upstream commit:  $UPSTREAM_COMMIT" >&2
  print -r -u2 "       The baseline recorded in run-state.json does not match the upstream-tracking ref." >&2
  print -r -u2 "       This is a local integrity check — no fetch/pull/push was executed." >&2
  print -r -u2 "       The @{u} value is a local cached ref and may be stale if the remote was recently updated." >&2
  exit 1
fi
print -r -u2 "PASS: Gate 3 -- baseline_commit matches upstream commit ($BASELINE_COMMIT)"

# --- Gate 4: Checkpoint baseline integrity ---
# Validates the checkpoint baseline based on whether this is the first or
# a subsequent checkpoint, using last_checkpoint_commit from run-state.json.
#
# First checkpoint (last_checkpoint_commit is null):
#   1. --last-checkpoint must equal baseline_commit
#   2. HEAD must equal baseline_commit
#   Invariant: baseline_commit == --last-checkpoint == HEAD
#
# Subsequent checkpoint (last_checkpoint_commit is non-null):
#   1. --last-checkpoint must equal last_checkpoint_commit from run-state
#   2. HEAD must equal last_checkpoint_commit from run-state
#   Invariant: LAST_CHECKPOINT_COMMIT_FROM_STATE == --last-checkpoint == HEAD
#
# All three comparisons are independent. A mismatch on any is a hard failure.
# No auto-reset, no auto-commit, no remote Git operations.

HEAD_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo "")"
if [[ -z "$HEAD_COMMIT" ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- Could not resolve HEAD commit" >&2
  exit 1
fi

# Verify that --last-checkpoint exists in the repository
if ! git rev-parse --verify "$LAST_CHECKPOINT" >/dev/null 2>&1; then
  print -r -u2 "ERROR: GATE 4 FAILED -- --last-checkpoint commit '$LAST_CHECKPOINT' does not exist in this repository" >&2
  exit 1
fi

# Verify that baseline_commit exists in the repository
if ! git rev-parse --verify "$BASELINE_COMMIT" >/dev/null 2>&1; then
  print -r -u2 "ERROR: GATE 4 FAILED -- baseline_commit from run-state.json does not exist" >&2
  print -r -u2 "       baseline_commit: $BASELINE_COMMIT" >&2
  exit 1
fi

# Determine checkpoint type from last_checkpoint_commit in run-state.json
# null (__NULL__ sentinel → empty string) = first checkpoint
# non-null SHA = subsequent checkpoint
if [[ -z "$LAST_CHECKPOINT_COMMIT_FROM_STATE" ]]; then
  # === FIRST CHECKPOINT ===
  print -r -u2 "INFO: Gate 4 -- First checkpoint detected (last_checkpoint_commit is null)"

  # Comparison 1: --last-checkpoint must equal baseline_commit
  if [[ "$LAST_CHECKPOINT" != "$BASELINE_COMMIT" ]]; then
    print -r -u2 "ERROR: GATE 4 FAILED -- First checkpoint: --last-checkpoint != baseline_commit" >&2
    print -r -u2 "       --last-checkpoint:        $LAST_CHECKPOINT" >&2
    print -r -u2 "       baseline_commit:          $BASELINE_COMMIT" >&2
    print -r -u2 "       For the first checkpoint, --last-checkpoint must equal baseline_commit." >&2
    exit 1
  fi
  print -r -u2 "PASS: Gate 4 -- First checkpoint: --last-checkpoint equals baseline_commit"

  # Comparison 2: HEAD must equal baseline_commit
  if [[ "$HEAD_COMMIT" != "$BASELINE_COMMIT" ]]; then
    print -r -u2 "ERROR: GATE 4 FAILED -- First checkpoint: HEAD != baseline_commit" >&2
    print -r -u2 "       HEAD:                     $HEAD_COMMIT" >&2
    print -r -u2 "       baseline_commit:          $BASELINE_COMMIT" >&2
    print -r -u2 "       For the first checkpoint, HEAD must equal baseline_commit." >&2
    print -r -u2 "       No auto-reset, no auto-commit, and no remote Git operations are performed." >&2
    exit 1
  fi
  print -r -u2 "PASS: Gate 4 -- First checkpoint: HEAD equals baseline_commit ($HEAD_COMMIT) [run-id: $RUN_ID_RAW]"
else
  # === SUBSEQUENT CHECKPOINT ===
  print -r -u2 "INFO: Gate 4 -- Subsequent checkpoint detected (last_checkpoint_commit is set)"

  # Comparison 1: --last-checkpoint must equal last_checkpoint_commit from run-state
  if [[ "$LAST_CHECKPOINT" != "$LAST_CHECKPOINT_COMMIT_FROM_STATE" ]]; then
    print -r -u2 "ERROR: GATE 4 FAILED -- Subsequent checkpoint: --last-checkpoint != last_checkpoint_commit" >&2
    print -r -u2 "       --last-checkpoint:               $LAST_CHECKPOINT" >&2
    print -r -u2 "       last_checkpoint_commit (state): $LAST_CHECKPOINT_COMMIT_FROM_STATE" >&2
    print -r -u2 "       For a subsequent checkpoint, --last-checkpoint must equal last_checkpoint_commit from run-state.json." >&2
    exit 1
  fi
  print -r -u2 "PASS: Gate 4 -- Subsequent checkpoint: --last-checkpoint equals last_checkpoint_commit"

  # Comparison 2: HEAD must equal last_checkpoint_commit from run-state
  if [[ "$HEAD_COMMIT" != "$LAST_CHECKPOINT_COMMIT_FROM_STATE" ]]; then
    print -r -u2 "ERROR: GATE 4 FAILED -- Subsequent checkpoint: HEAD != last_checkpoint_commit" >&2
    print -r -u2 "       HEAD:                            $HEAD_COMMIT" >&2
    print -r -u2 "       last_checkpoint_commit (state):  $LAST_CHECKPOINT_COMMIT_FROM_STATE" >&2
    print -r -u2 "       For a subsequent checkpoint, HEAD must equal last_checkpoint_commit from run-state.json." >&2
    print -r -u2 "       No auto-reset, no auto-commit, and no remote Git operations are performed." >&2
    exit 1
  fi
  print -r -u2 "PASS: Gate 4 -- Subsequent checkpoint: HEAD equals last_checkpoint_commit ($HEAD_COMMIT)"
fi

print -r -u2 ""
print -r -u2 "=== Preflight complete: all gates passed ==="
print -r -u2 "INFO: No remote Git commands (fetch/pull/push) were executed."
exit 0
