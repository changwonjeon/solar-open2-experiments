#!/bin/zsh
set -euo pipefail

# preflight.sh -- Git safety preflight for git-checkpoint skill
#
# Verifies that the repository is in a safe state for a Ralph Loop
# checkpoint commit. Runs before commit-gate.sh. Does not modify the
# worktree or Git history.
#
# Usage:
#   preflight.sh --last-checkpoint <commit> --run-state <path>
#
# Arguments:
#   --last-checkpoint <commit>  Full SHA-1 of the last checkpoint commit (REQUIRED)
#   --run-state <path>          Repository-relative path to run-state.json (REQUIRED)
#   --help, -h                  Show this help
#
# Gates:
#   1. Branch matches experiment/solar-ralph-*
#   2. HEAD is not detached
#   3. Upstream is configured (via @{u})
#   4. Upstream baseline integrity:
#      - baseline_commit from run-state.json must equal the upstream commit
#      - last-checkpoint must be a descendant of the upstream commit
#      - last-checkpoint must be an ancestor of HEAD
#      - last-checkpoint must be on the same branch (not ahead of baseline)
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
      LAST_CHECKPOINT="$2"
      shift 2 || { print -r -u2 "ERROR: --last-checkpoint requires an argument" >&2; exit 2; }
      ;;
    --run-state)
      RUN_STATE_PATH="$2"
      shift 2 || { print -r -u2 "ERROR: --run-state requires an argument" >&2; exit 2; }
      ;;
    --help|-h)
      print -r -u2 "Usage: preflight.sh --last-checkpoint <commit> --run-state <path>"
      print -r -u2 ""
      print -r -u2 "OPTIONS:"
      print -r -u2 "  --last-checkpoint <commit>"
      print -r -u2 "      Full SHA-1 of the last checkpoint commit. REQUIRED."
      print -r -u2 "      The last checkpoint is the most recent commit made by a prior"
      print -r -u2 "      git-checkpoint invocation in this run. The run must resume from"
      print -r -u2 "      this commit as the baseline."
      print -r -u2 "  --run-state <path>"
      print -r -u2 "      Repository-relative path to run-state.json. REQUIRED."
      print -r -u2 "      Used to retrieve the baseline_commit and branch name."
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

# --- Retrieve baseline from run-state.json ---
BASELINE_COMMIT=""
RUN_BRANCH=""
if [[ -f "$RUN_STATE_PATH" ]]; then
  RS_CONTENT="$(python3 -c "
import json, sys, os
rs_path = os.environ['RUN_STATE_PATH']
try:
    with open(rs_path, 'r') as f:
        state = json.load(f)
    print(state.get('baseline_commit', ''))
    print(state.get('branch', ''))
    print(state.get('run_id', ''))
except Exception:
    print('')
    print('')
" 2>/dev/null || echo "")"
  # Parse the output: first line = baseline_commit, second = branch, third = run_id
  BASELINE_COMMIT="$(echo "$RS_CONTENT" | sed -n '1p')"
  RUN_BRANCH="$(echo "$RS_CONTENT" | sed -n '2p')"
else
  print -r -u2 "ERROR: --run-state file does not exist: $RUN_STATE_PATH" >&2
  exit 2
fi

if [[ -z "$BASELINE_COMMIT" ]]; then
  print -r -u2 "ERROR: Could not read baseline_commit from run-state.json" >&2
  exit 1
fi

# --- Gate 1: Branch pattern ---
BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || echo "")"
if [[ -z "$BRANCH" ]]; then
  print -r -u2 "ERROR: GATE 1 FAILED -- Unable to determine branch name" >&2
  exit 1
fi
if ! [[ "$BRANCH" =~ ^experiment/solar-ralph- ]]; then
  print -r -u2 "ERROR: GATE 1 FAILED -- Branch '$BRANCH' does not match 'experiment/solar-ralph-*' pattern" >&2
  print -r -u2 "       Expected a branch like: experiment/solar-ralph-20260719-143022" >&2
  print -r -u2 "       Create one with: git checkout -b experiment/solar-ralph-\$(date +%Y%m%d-%H%M%S)" >&2
  exit 1
fi
echo "PASS: Gate 1 -- Branch '$BRANCH' matches 'experiment/solar-ralph-*'"

# --- Gate 2: Not detached HEAD ---
if ! git symbolic-ref HEAD >/dev/null 2>&1; then
  print -r -u2 "ERROR: GATE 2 FAILED -- HEAD is detached. Checkpoint commits must be on a named branch." >&2
  exit 1
fi
echo "PASS: Gate 2 -- HEAD is on named branch '$BRANCH' (not detached)"

# --- Gate 3: Upstream configured ---
UPSTREAM_REF="$(git rev-parse --verify @{u} 2>/dev/null || echo "")"
if [[ -z "$UPSTREAM_REF" ]]; then
  print -r -u2 "ERROR: GATE 3 FAILED -- No upstream configured for branch '$BRANCH'" >&2
  print -r -u2 "       The baseline must have been pushed before the run started." >&2
  print -r -u2 "       Run: git push -u origin $BRANCH" >&2
  exit 1
fi
echo "PASS: Gate 3 -- Upstream configured: $UPSTREAM_REF"

# --- Gate 4: Upstream baseline integrity ---
# The baseline_commit recorded in run-state.json must match the upstream commit.
# This ensures the remote branch has not been modified externally during the run.
# We resolve @{u} directly (not origin/<branch>) to get the actual upstream ref.
# We also verify:
#   a) last-checkpoint is an ancestor of HEAD
#   b) last-checkpoint is a descendant of the baseline (not before it)
#   c) last-checkpoint is on the same branch (not ahead of upstream)

# Verify that the last-checkpoint commit exists
if ! git rev-parse --verify "$LAST_CHECKPOINT" >/dev/null 2>&1; then
  print -r -u2 "ERROR: GATE 4 FAILED -- last-checkpoint commit '$LAST_CHECKPOINT' does not exist" >&2
  exit 1
fi

# Resolve the upstream commit via @{u} (not origin/<branch>)
UPSTREAM_COMMIT="$(git rev-parse "${UPSTREAM_REF}^{commit}" 2>/dev/null || echo "")"
if [[ -z "$UPSTREAM_COMMIT" ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- Could not resolve upstream commit from @{u}" >&2
  exit 1
fi

# Check (a): baseline_commit must equal upstream commit
if [[ "$BASELINE_COMMIT" != "$UPSTREAM_COMMIT" ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- baseline_commit does not match upstream commit" >&2
  print -r -u2 "       baseline_commit: $BASELINE_COMMIT" >&2
  print -r -u2 "       upstream commit:  $UPSTREAM_COMMIT" >&2
  print -r -u2 "       The remote branch may have advanced since the run started." >&2
  print -r -u2 "       Remote Git operations are prohibited during the run." >&2
  exit 1
fi
echo "PASS: Gate 4a -- baseline_commit matches upstream commit ($BASELINE_COMMIT)"

# Check (b): last-checkpoint must be a descendant of the baseline
# If the baseline is NOT an ancestor of the last-checkpoint, the
# last-checkpoint was made on a different branch or the baseline
# was reached after the last-checkpoint.
if [[ -n "$LAST_CHECKPOINT" ]]; then
  if ! git merge-base --is-ancestor "$BASELINE_COMMIT" "$LAST_CHECKPOINT" 2>/dev/null; then
    print -r -u2 "ERROR: GATE 4 FAILED -- last-checkpoint is not a descendant of baseline" >&2
    print -r -u2 "       baseline:         $BASELINE_COMMIT" >&2
    print -r -u2 "       last-checkpoint:  $LAST_CHECKPOINT" >&2
    print -r -u2 "       The last-checkpoint was made before or outside the baseline branch." >&2
    exit 1
  fi
  echo "PASS: Gate 4b -- last-checkpoint is a descendant of baseline"
fi

# Check (c): last-checkpoint must be an ancestor of HEAD
# This ensures we're resuming from a valid checkpoint and the HEAD
# has not been reset or rebased to a different commit.
if ! git merge-base --is-ancestor "$LAST_CHECKPOINT" HEAD 2>/dev/null; then
  print -r -u2 "ERROR: GATE 4 FAILED -- last-checkpoint is not an ancestor of HEAD" >&2
  print -r -u2 "       last-checkpoint: $LAST_CHECKPOINT" >&2
  print -r -u2 "       HEAD:             $(git rev-parse HEAD)" >&2
  print -r -u2 "       The working tree has moved past the last checkpoint." >&2
  exit 1
fi
echo "PASS: Gate 4c -- last-checkpoint is an ancestor of HEAD ($(git rev-parse HEAD))"

# Check (d): last-checkpoint must not be ahead of the upstream commit
# This ensures the checkpoint was created on this branch and not on a
# diverged branch or after a rebase.
if git merge-base --is-ancestor "$UPSTREAM_COMMIT" "$LAST_CHECKPOINT" 2>/dev/null; then
  # last-checkpoint is ahead of or equal to upstream -- this means we
  # have made progress beyond the baseline, which is expected.
  echo "PASS: Gate 4d -- last-checkpoint is reachable from upstream"
else
  # last-checkpoint is behind upstream. This can happen if the upstream
  # was force-pushed after the last-checkpoint was created. This is a
  # baseline violation.
  print -r -u2 "ERROR: GATE 4 FAILED -- last-checkpoint is not reachable from upstream" >&2
  print -r -u2 "       last-checkpoint: $LAST_CHECKPOINT" >&2
  print -r -u2 "       upstream commit:  $UPSTREAM_COMMIT" >&2
  print -r -u2 "       The last-checkpoint was created outside the current branch history." >&2
  exit 1
fi

echo ""
echo "=== Preflight complete: all gates passed ==="
exit 0
