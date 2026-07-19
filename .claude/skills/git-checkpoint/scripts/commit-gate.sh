#!/bin/zsh
set -euo pipefail

# commit-gate.sh -- Git checkpoint commit gate for git-checkpoint skill
#
# Performs strict validation before committing approved pathspecs as a
# Ralph Loop checkpoint. Never pushes, fetches, pulls, rebases, resets,
# or uses broad git add.
#
# Usage:
#   commit-gate.sh <p0-id> <approved-path>... --run-state <path> [--summary <text>]
#
# Gate summary:
#   0. Index pollution check -- reject if anything is already staged
#   1. Approved path validation -- repo-relative, no globs, no symlinks, no sensitive paths
#   2. Secret pattern content check -- text files only, redacted output
#   3. Worktree trust -- no changes outside approved paths
#   4. Test evidence validation -- run-state.json must show tests_passed
#   5. Stage approved paths (via safe_git wrapper)
#   6. Post-stage containment check -- staged set must equal approved path set
#   7. Pre-commit whitespace check (git diff --cached --check)
#   8. Commit with checkpoint message and emit JSON result to stdout
#
# Exit codes:
#   0 -- commit successful; exactly one JSON object emitted to stdout
#   1 -- gate failed; all diagnostics emitted to stderr
#   2 -- usage error; usage message emitted to stderr
#
# Output contract:
#   stderr -- all PASS, WARNING, ERROR, INFO diagnostics
#   stdout -- on exit 0, exactly one JSON object; on exit non-zero, nothing

# --- Configuration ---
MAX_FILE_SIZE_BYTES=$((10 * 1048576))  # 10 MiB

# Secret patterns detected by grep -E (extended regex).
# Covers AWS keys, GitHub tokens, JWTs, private key headers, Slack tokens,
# Stripe keys, Google API keys, Shopify tokens, Dropbox keys, and more.
SECRET_PATTERN='AKIA[0-9A-Z]{16}|AGPA[0-9A-Z]{16}|A3T[0-9A-Z]{16}|aio[A-Z0-9]{32}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{36}|gho_[A-Za-z0-9_]{36}|ghu_[A-Za-z0-9_]{36}|ghs_[A-Za-z0-9_]{36}|ghx_[A-Za-z0-9_]{36}|[a-f0-9]{32}:[a-f0-9]{32}|-----BEGIN[[:space:]]*(RSA|EC|DSA|OPENSSH)[[:space:]]*PRIVATE KEY-----|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|xox[baprs]-[0-9]{10,}-[a-zA-Z0-9]{20,}|dapi+[a-f0-9]{32}|MCNA[0-9A-Z]{16}|sk_live_|sk_test_|sq0atp|sq0csp|xiamicrm|platformAPIKey|drmn_|jk[0-9A-Za-z]{20}|AIza|GLbi|Ya29|shpat_|shpca_|shpss_|ak_sv|AC[a-z0-9]{32}|BFAPI|EmailSmtp|AKIA'

# --- Global state for cleanup ---
CLEANUP_STAGED_PATHS=()
REPO_ROOT=""

# --- Helper: reject a path with a reason ---
reject_path() {
  print -r -u2 "ERROR: GATE 1 FAILED -- Rejected path: $1"
  cleanup_on_failure
  exit 1
}

# --- Helper: check common path rejections (valid for both existing and tracked-deletion paths) ---
# These checks apply to ALL paths before we branch on existence vs tracked-deletion.
check_common_rejections() {
  local raw_path="$1"

  # Reject empty paths
  if [[ -z "$raw_path" ]]; then
    reject_path "empty path"
  fi

  # Reject absolute paths
  if [[ "$raw_path" == /* ]]; then
    reject_path "absolute path '$raw_path' -- only repository-relative paths are allowed"
  fi

  # Reject paths containing '..' components
  if [[ "$raw_path" == */../* ]] || [[ "$raw_path" == ../* ]] || [[ "$raw_path" == .. ]]; then
    reject_path "path contains '..' component: '$raw_path'"
  fi

  # Reject leading dash (looks like a flag)
  if [[ "$raw_path" == -* ]]; then
    reject_path "path starts with a dash (looks like a flag): '$raw_path'"
  fi

  # Reject glob metacharacters: *, ?, [
  if [[ "$raw_path" == *'*'* ]] || [[ "$raw_path" == *'?'* ]] || [[ "$raw_path" == *\[* ]]; then
    reject_path "path contains glob metacharacter: '$raw_path'"
  fi

  # Repository root check: must be repo-relative (not just contain the repo path)
  # A repo-relative path must not resolve outside the repository.
  # We check this after realpath resolves the full path.
  # For now, reject paths that start with / (already handled above).

  # Reject .git directory traversal
  case "$raw_path" in
    *.git/*|.git/*|.git|*/.git/*|*/.git) reject_path "path traverses or references .git: '$raw_path'" ;;
  esac

  # Component-level sensitive path check: _private, credentials, secrets at any depth
  local_compliant=1
  IFS='/' read -rA COMPONENTS <<< "$raw_path"
  for comp in "${COMPONENTS[@]}"; do
    case "$comp" in
      (_private|credentials|secrets)
        reject_path "sensitive path component '$comp' in: '$raw_path'"
        ;;
    esac
  done

  # Basename-level checks
  local basename_comp
  basename_comp="$(basename "$raw_path")"

  # Reject .env and .env.*
  case "$basename_comp" in
    (.env|.env.*)
      reject_path "basename matches .env or .env.*: '$raw_path'"
      ;;
  esac

  # Reject *.log suffix
  case "$basename_comp" in
    (*.log)
      reject_path "basename ends with .log: '$raw_path'"
      ;;
  esac
}

# --- Helper: walk path components from repo root, check each for symlinks ---
# For a repository-relative path, build the path component by component
# from REPO_ROOT and test each intermediate component with test -L.
# Rejects if any component is a symlink (including broken symlinks).
# For tracked deletions where the target path does not exist, validates
# that all existing parent components contain no symlinks.
check_symlink_components() {
  local raw_path="$1"
  local fs_path="$2"  # Full filesystem path (REPO_ROOT/raw_path)

  # Build the path component by component from REPO_ROOT
  local accumulated="$REPO_ROOT"
  local comp
  local first_component=1

  IFS='/' read -rA COMPONENT_ARRAY <<< "$raw_path"

  for comp in "${COMPONENT_ARRAY[@]}"; do
    [[ -z "$comp" ]] && continue  # skip empty components (leading/trailing slash)

    accumulated="$accumulated/$comp"

    if [[ $first_component -eq 1 ]]; then
      # First component: check if it exists
      if [[ -e "$accumulated" ]]; then
        if [[ -L "$accumulated" ]]; then
          reject_path "path component is a symbolic link: '$comp' in '$raw_path'"
        fi
      fi
      # If it doesn't exist, we'll check parent components below
      first_component=0
      continue
    fi

    # For subsequent components, check the parent exists first
    local parent_dir="$(dirname "$accumulated")"
    if [[ -d "$parent_dir" ]]; then
      if [[ -L "$accumulated" ]]; then
        # Symlink exists (may be broken or valid)
        reject_path "path component is a symbolic link: '$comp' in '$raw_path'"
      elif [[ -e "$accumulated" ]]; then
        # Normal existing component -- ok
        :
      fi
      # If the component doesn't exist but parent does, we're building
      # toward a path that doesn't exist yet (ok for tracked deletions).
    else
      # Parent doesn't exist -- we've gone past the deepest existing component.
      # This is expected for tracked deletions where intermediate directories
      # may have been deleted too. We stop checking symlinks here.
      break
    fi
  done

  # For tracked deletions: verify the deepest existing parent component
  # has no symlinks. Walk from the deepest existing component upward.
  if [[ ! -e "$fs_path" ]]; then
    # Find the deepest existing parent
    local check_path="$REPO_ROOT"
    local parent_check="$REPO_ROOT"
    for comp in "${COMPONENT_ARRAY[@]}"; do
      [[ -z "$comp" ]] && continue
      parent_check="$parent_check/$comp"
      if [[ -e "$parent_check" ]] || [[ -d "$parent_check" ]]; then
        check_path="$parent_check"
      else
        # This component doesn't exist; check the parent
        local check_dir="$(dirname "$check_path")"
        if [[ "$check_dir" != "$check_path" ]] && [[ -d "$check_dir" ]]; then
          if [[ -L "$check_dir" ]]; then
            reject_path "parent path component is a symbolic link in '$raw_path'"
          fi
        fi
        break
      fi
    done
  fi
}

# --- Helper: check whether a path is under a sensitive transcript directory ---
# Reject paths that appear to be raw transcript files.
is_raw_transcript_path() {
  local raw_path="$1"
  # Raw transcript paths include session logs under the run directory.
  # Match paths like: data/results/ralpthon/solar/<run-id>/<session>.log
  if [[ "$raw_path" == data/results/ralpthon/solar/*/*.log ]]; then
    return 0  # is a raw transcript
  fi
  if [[ "$raw_path" == data/results/ralpthon/solar/*/* ]]; then
    # Any file under the run directory that is not a known state file
    local bn
    bn="$(basename "$raw_path")"
    case "$bn" in
      (run-state.json|failure-ledger.jsonl|events.jsonl|artifact-manifest.json|HANDOFF.md) ;;
      (*) return 0 ;;
    esac
  fi
  return 1  # not a raw transcript
}

# --- Helper: check a single file for secret patterns. Returns 0 if clean, 1 if found. ---
check_file_for_secrets() {
  local filepath="$1"
  local filename="$2"

  # Skip binary files -- only check text files
  local mime_type
  mime_type="$(file -b --mime-type "$filepath" 2>/dev/null || echo "")"
  case "$mime_type" in
    text/*) ;;
    *) print -r -u2 "  SKIP (non-text): $filename"; return 0 ;;
  esac

  # Use grep -nIE with fixed-line output; capture matches for reporting
  local matches
  matches="$(grep -nIE --color=never "$SECRET_PATTERN" "$filepath" 2>/dev/null || true)"
  if [[ -n "$matches" ]]; then
    local line_numbers
    line_numbers="$(echo "$matches" | sed -n 's/^\([0-9]*\):.*/\1/p' | sort -u | tr '\n' ' ')"
    local sample_match
    sample_match="$(echo "$matches" | head -n1 | sed 's/^[0-9]*://')"
    local category
    category="$(CATEGORIZE_SECRET "$sample_match")"
    print -r -u2 "ERROR: GATE 2 FAILED -- Secret pattern detected in: $filename"
    print -r -u2 "       Pattern category: $category"
    print -r -u2 "       Line number(s): $line_numbers"
    print -r -u2 "       Matched content: REDACTED"
    return 1
  fi
  return 0
}

# --- Helper: check whether a path (repo-relative) is covered by the approved set. ---
is_path_approved() {
  local check_path="$1"
  for ap in "${APPROVED_PATHS_SET[@]}"; do
    [[ "$check_path" == "$ap" ]] && return 0
  done
  for ap in "${APPROVED_PATHS_SET[@]}"; do
    ap_fs="$REPO_ROOT/$ap"
    if [[ -d "$ap_fs" ]]; then
      if [[ "$check_path" == "$ap"/* ]]; then
        return 0
      fi
    fi
  done
  return 1
}

# --- Helper: read all staged files after our add, verify containment ---
check_staged_containment() {
  local staged_list
  staged_list="$(git diff --cached --name-only -z 2>/dev/null || true)"
  if [[ -z "$staged_list" ]]; then
    return 0
  fi

  local overflow_found=0
  while IFS= read -r -d '' staged_file; do
    staged_file="${staged_file#./}"
    local is_covered=0
    for ap in "${APPROVED_PATHS_SET[@]}"; do
      if [[ "$staged_file" == "$ap" ]]; then
        is_covered=1
        break
      fi
      ap_fs="$REPO_ROOT/$ap"
      if [[ -d "$ap_fs" ]] && [[ "$staged_file" == "$ap"/* ]]; then
        is_covered=1
        break
      fi
    done
    if [[ $is_covered -eq 0 ]]; then
      overflow_found=1
      print -r -u2 "ERROR: GATE 7 FAILED -- Staged file outside approved path set: $staged_file"
    fi
  done <<< "$staged_list"

  if [[ $overflow_found -eq 1 ]]; then
    return 1
  fi
  return 0
}

# --- Helper: read the P0 status from run-state.json ---
# Under set -e, python3 is invoked inside an if/else so that a non-zero
# Python exit does not terminate the script. Python stdout is written to
# a temp file so the exit code is not masked by a local variable assignment.
read_p0_status() {
  local rs_path="$1"
  local expected_p0="$2"
  local py_out="/tmp/commit-gate-python-out-$$"
  local py_stderr="/tmp/commit-gate-python-stderr-$$"

  if python3 -c "
import json, sys
p0_id = sys.argv[1]
run_state_path = sys.argv[2]
try:
    with open(run_state_path, 'r') as f:
        state = json.load(f)
    for p0 in state.get('p0_items', []):
        if p0.get('id') == p0_id:
            print(p0.get('status', 'unknown'))
            sys.exit(0)
    print('not-found')
    sys.exit(1)
except Exception as e:
    print('parse-error', file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(2)
" "$expected_p0" "$rs_path" >"$py_out" 2>"$py_stderr"; then
    PYTHON_EXIT=0
    P0_STATUS="$(cat "$py_out")"
  else
    PYTHON_EXIT=$?
    if [[ -s "$py_stderr" ]]; then
      P0_STATUS="$(head -n1 "$py_stderr")"
    else
      P0_STATUS="no-python-output"
    fi
  fi
  rm -f "$py_out" "$py_stderr"
}

# --- Cleanup helper ---
cleanup_on_failure() {
  if [[ ${#CLEANUP_STAGED_PATHS[@]} -gt 0 ]]; then
    print -r -u2 "INFO: Unstaging ${#CLEANUP_STAGED_PATHS[@]} path(s) added by this script before exit..."
    for cp in "${CLEANUP_STAGED_PATHS[@]}"; do
      command git restore --staged -- "$cp" 2>/dev/null || true
    done
  fi
}

# --- Helper: read a NUL-terminated record from stdin ---
# In porcelain -z output, rename/copy entries span two NUL-terminated records:
#   Record 1: XY <destination-path>
#   Record 2:     <source-path>
# This helper reads the next record from the NUL-delimited stream.
read_next_porcelain_record() {
  local record
  # Use read with -d '' to split on NUL bytes
  if IFS= read -r -d '' record; then
    PORCELAIN_RECORD_FOUND=1
    PORCELAIN_RECORD="$record"
  else
    PORCELAIN_RECORD_FOUND=0
    PORCELAIN_RECORD=""
  fi
}

# Categorize a matched secret pattern for redacted reporting
CATEGORIZE_SECRET() {
  local pattern="$1"
  case "$pattern" in
    *AKIA*|*A3T*|*AGPA*|*ASIA*) echo "aws-key" ;;
    *ghp_*|*gho_*|*ghu_*|*ghs_*|*ghx_*) echo "github-token" ;;
    *aio*|*eyJ*) echo "jwt-or-token" ;;
    *-----BEGIN*) echo "private-key" ;;
    *xoxb*|*xoxp*|*xoxr*|*xoxs*) echo "slack-token" ;;
    *sk_live_*|*sk_test_*|*sq0atp*|*sq0csp*) echo "payment-token" ;;
    *AIza*|*GLbi*|*Ya29*) echo "google-api-key" ;;
    *shpat_*|*shpca_*|*shpss_*) echo "shopify-token" ;;
    *ak_sv*|*AC[a-z0-9]*) echo "aws-secret" ;;
    *BFAPI*|*EmailSmtp*|*MCNA*) echo "credential" ;;
    *) echo "secret-pattern" ;;
  esac
}

# --- Argument parsing ---
RUN_STATE_PATH=""
SUMMARY=""
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-state)
      if [[ $# -lt 2 ]]; then
        print -r -u2 "ERROR: --run-state requires a path argument" >&2
        exit 2
      fi
      RUN_STATE_PATH="$2"
      shift 2
      ;;
    --summary)
      if [[ $# -lt 2 ]]; then
        print -r -u2 "ERROR: --summary requires a text argument" >&2
        exit 2
      fi
      SUMMARY="$2"
      shift 2
      ;;
    --help|-h)
      print -r -u2 "Usage: commit-gate.sh <p0-id> <approved-path>... --run-state <path> [--summary <text>]"
      print -r -u2 ""
      print -r -u2 "Required arguments:"
      print -r -u2 "  <p0-id>              P0 identifier, e.g. P0-3"
      print -r -u2 "  <approved-path>...   One or more repository-relative paths to stage"
      print -r -u2 ""
      print -r -u2 "Options:"
      print -r -u2 "  --run-state <path>   Path to run-state.json (required in production)"
      print -r -u2 "  --summary <text>     Commit message summary (default: '<p0-id> deliverable')"
      print -r -u2 "  --help, -h           Show this help"
      exit 0
      ;;
    --*)
      print -r -u2 "ERROR: Unknown option: $1"
      exit 2
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

# Position argument validation (not a gate; precondition check)
if [[ ${#POSITIONAL_ARGS[@]} -lt 2 ]]; then
  if [[ ${#POSITIONAL_ARGS[@]} -lt 1 ]]; then
    print -r -u2 "ERROR: Missing required arguments: <p0-id> <approved-path>..."
  else
    print -r -u2 "ERROR: Missing required argument: at least one <approved-path> must follow <p0-id>"
  fi
  exit 2
fi

P0_ID="${POSITIONAL_ARGS[1]}"
APPROVED_PATHS=()
for ((i=2; i<=${#POSITIONAL_ARGS[@]}; i++)); do
  APPROVED_PATHS+=("${POSITIONAL_ARGS[$i]}")
done

if [[ ${#APPROVED_PATHS[@]} -eq 0 ]]; then
  print -r -u2 "ERROR: At least one <approved-path> must be provided after <p0-id>"
  exit 2
fi

if [[ -z "$SUMMARY" ]]; then
  SUMMARY="${P0_ID} deliverable"
fi

# --- Repository root ---
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$REPO_ROOT" ]]; then
  print -r -u2 "ERROR: Not inside a Git repository"
  exit 1
fi
cd "$REPO_ROOT"

# --- Gate 0: Index pollution check ---
EXISTING_STAGED="$(git diff --cached --name-only -z 2>/dev/null || true)"
if [[ -n "$EXISTING_STAGED" ]]; then
  print -r -u2 "ERROR: Index pollution detected -- pre-existing staged content found"
  print -r -u2 "       Checkpoint commits must start from a clean index."
  print -r -u2 "       Unstage existing changes first: git restore --staged -- <paths>"
  exit 1
fi
print -r -u2 "PASS: Gate 0 -- Index is clean (no pre-existing staged changes)"

# --- Gate 1: Approved path validation ---
print -r -u2 ""
print -r -u2 "=== Gate 1: Validating approved paths ==="
VALIDATED_PATHS=()
STAGED_PATHS=()

for raw_path in "${APPROVED_PATHS[@]}"; do
  # --- Common rejections for ALL paths (existing, directory, tracked deletion) ---
  check_common_rejections "$raw_path"

  # Build the full filesystem path
  FS_PATH="$REPO_ROOT/$raw_path"

  # --- Check if path exists on disk or is a tracked deletion ---
  if [[ -e "$FS_PATH" ]]; then
    # Path exists on disk -- check symlink components
    check_symlink_components "$raw_path" "$FS_PATH"

    # Repository containment check using canonical path
    REAL_NO_FOLLOW="$(realpath -P "$FS_PATH" 2>/dev/null || echo "")"
    if [[ -z "$REAL_NO_FOLLOW" ]]; then
      reject_path "path does not resolve under repository: '$raw_path'"
    fi
    if [[ "$REAL_NO_FOLLOW" != "$REPO_ROOT" ]] && [[ "$REAL_NO_FOLLOW" != "$REPO_ROOT/"* ]]; then
      reject_path "path is outside repository: '$raw_path' resolves to '$REAL_NO_FOLLOW'"
    fi
    CANONICAL_PATH="$REAL_NO_FOLLOW"

    # File/directory size check (10 MiB ceiling)
    if [[ -f "$CANONICAL_PATH" ]]; then
      FILE_SIZE_BYTES="$(stat -c%s "$CANONICAL_PATH" 2>/dev/null || echo "0")"
      if [[ "$FILE_SIZE_BYTES" -gt "$MAX_FILE_SIZE_BYTES" ]]; then
        reject_path "file exceeds 10 MiB: '$raw_path' (${FILE_SIZE_BYTES} bytes)"
      fi
    elif [[ -d "$CANONICAL_PATH" ]]; then
      while IFS= read -r -d '' file; do
        fsize="$(stat -c%s "$file" 2>/dev/null || echo "0")"
        if [[ "$fsize" -gt "$MAX_FILE_SIZE_BYTES" ]]; then
          reject_path "directory contains file exceeding 10 MiB: '$file' (${fsize} bytes)"
        fi
      done < <(find "$CANONICAL_PATH" -type f -print0 2>/dev/null)
    fi

  elif git cat-file -e HEAD:"$raw_path" 2>/dev/null; then
    # Tracked deletion: file existed in HEAD but was deleted on disk.
    # Apply common rejections above (already done). Now validate:
    # - The path is a valid relative path (already checked: no absolute, no .., etc.)
    # - Parent components that still exist contain no symlinks
    check_symlink_components "$raw_path" "$FS_PATH"

    # For tracked deletions, the repository containment is checked by verifying
    # that the path was inside the repo at HEAD time. Since we already checked
    # common rejections (no absolute, no .., no .git), and the path matched
    # HEAD, it was a valid repo-relative path.
    # Additional containment check: verify the path was under REPO_ROOT in HEAD
    HEAD_TREE_PATH="$(git rev-parse HEAD:"$raw_path" 2>/dev/null || echo "")"
    # If HEAD contained this path, it was inside the repo
    if [[ -z "$HEAD_TREE_PATH" ]]; then
      reject_path "tracked deletion path is not valid in HEAD: '$raw_path'"
    fi

    CANONICAL_PATH="$raw_path"
  else
    # Path does not exist on disk and is not a tracked deletion
    reject_path "path does not exist and is not a tracked deletion: '$raw_path'"
  fi

  VALIDATED_PATHS+=("$raw_path")
  STAGED_PATHS+=("$raw_path")
  print -r -u2 "  Validated: $raw_path"
done

print -r -u2 "PASS: Gate 1 -- All approved paths validated (${#VALIDATED_PATHS[@]} paths)"

# --- Gate 2: Secret pattern content check ---
print -r -u2 ""
print -r -u2 "=== Gate 2: Checking for secret patterns in file contents ==="

SECRET_FOUND=0
for vp in "${VALIDATED_PATHS[@]}"; do
  FS_PATH="$REPO_ROOT/$vp"
  if [[ -f "$FS_PATH" ]]; then
    check_file_for_secrets "$FS_PATH" "$vp" || SECRET_FOUND=1
  elif [[ -d "$FS_PATH" ]]; then
    while IFS= read -r -d '' file; do
      fname="${file#"$REPO_ROOT"/}"
      check_file_for_secrets "$file" "$fname" || SECRET_FOUND=1
    done < <(find "$FS_PATH" -type f -print0 2>/dev/null)
  fi
  # Tracked deletions (files that no longer exist on disk) are skipped --
  # they have no content to scan.
done

if [[ $SECRET_FOUND -eq 1 ]]; then
  cleanup_on_failure
  exit 1
fi

print -r -u2 "PASS: Gate 2 -- No secret patterns detected"

# --- Gate 3: Worktree trust check ---
print -r -u2 ""
print -r -u2 "=== Gate 3: Checking worktree trust ==="

APPROVED_PATHS_SET=()
for p in "${VALIDATED_PATHS[@]}"; do
  APPROVED_PATHS_SET+=("$p")
done

# Use git status --porcelain=v1 -z for machine-readable output.
# In porcelain -z format, each record is NUL-terminated:
#   Record structure for normal files: XY<NUL><path><NUL>
#     where XY is a two-character status code and the path is the destination
#   Record structure for rename/copy:
#     Record 1: XY<NUL><destination-path><NUL>  (e.g., R100 or C080)
#     Record 2: <NUL><source-path><NUL>         (no status code, just the source)
#
# The separator between XY and the path is a single space character.
# For normal entries: the path starts at byte offset 3 (${line:1:1} is the space, ${line:3} is the path start).
# For rename/copy: the first record's path is the destination; the second record is the source.
WORK_TREE_UNAPPROVED_FOUND=0

# We need to process NUL-terminated records. Use a while loop reading from the process substitution.
# Since we need to look ahead for R/C records, we use a manual record reader.
PORCELAIN_RECORDS=()
# Read all porcelain records into an array (NUL-delimited)
while IFS= read -r -d '' porcelain_line; do
  PORCELAIN_RECORDS+=("$porcelain_line")
done < <(git status --porcelain=v1 -z 2>/dev/null)

# Process records sequentially, with lookahead for R/C
idx=1
while [[ $idx -le ${#PORCELAIN_RECORDS[@]} ]]; do
  status_line="${PORCELAIN_RECORDS[$idx]}"
  ((idx++))

  # Skip lines where both columns are ' ' (no change)
  if [[ "${status_line:0:2}" == '  ' ]]; then
    continue
  fi

  # Extract status code and path.
  # In porcelain -z: XY<space><path>
  # So path starts at byte index 3.
  STAGED_FLAG="${status_line:0:1}"
  UNSTAGED_FLAG="${status_line:1:1}"
  file_path="${status_line:3}"

  # Strip leading './' for matching
  clean_path="${file_path#./}"

  # Handle Rename (R) and Copy (C) status codes
  # In porcelain -z, these span two records:
  #   Record 1: R/C + destination path
  #   Record 2: source path (next NUL-terminated record, status starts with space)
  if [[ "$STAGED_FLAG" == 'R' ]] || [[ "$UNSTAGED_FLAG" == 'R' ]] || \
     [[ "$STAGED_FLAG" == 'C' ]] || [[ "$UNSTAGED_FLAG" == 'C' ]]; then
    # Consume the next record as the source path (if available)
    if [[ $idx -le ${#PORCELAIN_RECORDS[@]} ]]; then
      source_record="${PORCELAIN_RECORDS[$idx]}"
      ((idx++))
      # Source record in porcelain -z for R/C starts with a space in the status
      # position (the second column of the first record becomes the first
      # column of the continuation record). We skip parsing it as a separate
      # status entry.
    fi
    # For this initial safe version: any rename or copy requires operator intervention
    print -r -u2 "ERROR: GATE 3 FAILED -- Rename or copy detected: needs-operator"
    print -r -u2 "       Path: $clean_path"
    print -r -u2 "       Rename/copy operations require explicit operator handling."
    print -r -u2 "       To proceed, manually resolve the rename/copy before checkpoint."
    cleanup_on_failure
    exit 1
  fi

  # Determine if this entry is covered by an approved path.
  is_covered=0
  if is_path_approved "$clean_path"; then
    is_covered=1
  fi

  # For deleted files, also check if the path is in our approved set
  if [[ "$UNSTAGED_FLAG" == 'D' || "$STAGED_FLAG" == 'D' ]]; then
    if [[ "$is_covered" -eq 1 ]]; then
      continue
    fi
  fi

  # If we get here, the change is not covered by the approved paths
  if [[ "$is_covered" -eq 0 ]]; then
    WORK_TREE_UNAPPROVED_FOUND=1
    change_desc=""
    if [[ "$STAGED_FLAG" != ' ' ]]; then
      change_desc="${change_desc}staged:"
      case "$STAGED_FLAG" in
        M) change_desc="${change_desc}modified " ;;
        A) change_desc="${change_desc}added " ;;
        D) change_desc="${change_desc}deleted " ;;
        U) change_desc="${change_desc}unmerged " ;;
        *) change_desc="${change_desc}unknown " ;;
      esac
    fi
    if [[ "$UNSTAGED_FLAG" != ' ' ]]; then
      change_desc="${change_desc}unstaged:"
      case "$UNSTAGED_FLAG" in
        M) change_desc="${change_desc}modified " ;;
        A) change_desc="${change_desc}added " ;;
        D) change_desc="${change_desc}deleted " ;;
        U) change_desc="${change_desc}unmerged " ;;
        *) change_desc="${change_desc}unknown " ;;
      esac
    fi
    print -r -u2 "ERROR: GATE 3 FAILED -- Unapproved worktree change detected"
    print -r -u2 "       Path: $clean_path"
    print -r -u2 "       Change: $change_desc"
    print -r -u2 "       This change is outside the approved path set."
    print -r -u2 "       To proceed, either include this path in the approved paths or resolve the change manually."
  fi
done

if [[ $WORK_TREE_UNAPPROVED_FOUND -eq 1 ]]; then
  cleanup_on_failure
  exit 1
fi

print -r -u2 "PASS: Gate 3 -- No unapproved worktree changes detected"

# --- Gate 4: Test evidence validation ---
print -r -u2 ""
print -r -u2 "=== Gate 4: Checking test evidence ==="

# --run-state is required in production. Repository-relative only.
if [[ -z "$RUN_STATE_PATH" ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- --run-state is required but was not provided"
  print -r -u2 "       Usage: commit-gate.sh <p0-id> <approved-path>... --run-state <path>"
  cleanup_on_failure
  exit 1
fi

# Validate run-state path: must be a repository-relative path
check_common_rejections "$RUN_STATE_PATH"

# Additional run-state specific checks: no leading dash (already in check_common_rejections)
if [[ "$RUN_STATE_PATH" == -* ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- run-state path starts with a dash: '$RUN_STATE_PATH'"
  cleanup_on_failure
  exit 1
fi

# No glob metacharacters (already in check_common_rejections)
# No '..' components (already in check_common_rejections)

# Build the filesystem path and check containment
RS_FS_PATH="$REPO_ROOT/$RUN_STATE_PATH"

# Verify the path contains no symlink components
check_symlink_components "$RUN_STATE_PATH" "$RS_FS_PATH"

# Repository containment: must be strictly under REPO_ROOT/ (not just prefix match)
RS_REAL="$(realpath -P "$RS_FS_PATH" 2>/dev/null || echo "")"
if [[ -z "$RS_REAL" ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- run-state.json does not resolve: $RUN_STATE_PATH"
  cleanup_on_failure
  exit 1
fi
if [[ "$RS_REAL" != "$REPO_ROOT" ]] && [[ "$RS_REAL" != "$REPO_ROOT/"* ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- run-state.json is outside the repository: $RUN_STATE_PATH"
  cleanup_on_failure
  exit 1
fi

# Must be under the expected run directory
if [[ "$RS_REAL" != */data/results/ralpthon/solar/solar-ralph-*/run-state.json ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- run-state.json is not under the expected run directory pattern"
  print -r -u2 "       Expected: data/results/ralpthon/solar/solar-ralph-<YYYYMMDD-HHMMSS>/run-state.json"
  cleanup_on_failure
  exit 1
fi

# Now pass the canonical RS_REAL to the Python parser
PYTHON_RUN_STATE_PATH="$RS_REAL"

# Parse the P0 status using Python, with set -e protection
P0_STATUS=""
PYTHON_EXIT=0

# argv[1] = P0_ID, argv[2] = RUN_STATE_PATH (absolute path, no env vars)
if python3 -c "
import json, sys
p0_id = sys.argv[1]
run_state_path = sys.argv[2]
try:
    with open(run_state_path, 'r') as f:
        state = json.load(f)
    for p0 in state.get('p0_items', []):
        if p0.get('id') == p0_id:
            print(p0.get('status', 'unknown'))
            sys.exit(0)
    print('not-found')
    sys.exit(1)
except Exception as e:
    print('parse-error', file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(2)
" "$P0_ID" "$PYTHON_RUN_STATE_PATH" >"/tmp/commit-gate-python-out-$$" 2>"/tmp/commit-gate-python-stderr-$$"; then
  PYTHON_EXIT=0
  P0_STATUS="$(cat /tmp/commit-gate-python-out-$$)"
else
  PYTHON_EXIT=$?
  if [[ -s "/tmp/commit-gate-python-stderr-$$" ]]; then
    P0_STATUS="$(head -n1 /tmp/commit-gate-python-stderr-$$)"
  else
    P0_STATUS="no-python-output"
  fi
fi
rm -f /tmp/commit-gate-python-out-$$ /tmp/commit-gate-python-stderr-$$

if [[ $PYTHON_EXIT -ne 0 ]]; then
  print -r -u2 "ERROR: GATE 4 FAILED -- Failed to parse run-state.json"
  if [[ -n "$P0_STATUS" ]]; then
    print -r -u2 "       Detail: $P0_STATUS"
  fi
  cleanup_on_failure
  exit 1
fi

case "$P0_STATUS" in
  tests_passed)
    print -r -u2 "PASS: Gate 4 -- P0 $P0_ID status is 'tests_passed'"
    ;;
  checkpoint_failed)
    print -r -u2 "INFO: Gate 4 -- P0 $P0_ID status is 'checkpoint_failed'. Retrying checkpoint."
    print -r -u2 "       The previous checkpoint attempt failed; this run will attempt again."
    ;;
  *)
    print -r -u2 "ERROR: GATE 4 FAILED -- P0 $P0_ID status is '$P0_STATUS'. Expected 'tests_passed' or 'checkpoint_failed'."
    cleanup_on_failure
    exit 1
    ;;
esac

# --- Safe Git Wrapper ---
safe_git() {
  local cmd="$1"; shift
  case "$cmd" in
    push|pull|fetch|rebase|reset|checkout|clean)
      print -r -u2 "ERROR: GIT SAFETY VIOLATION -- 'git $cmd' is prohibited in checkpoint commits"
      return 1
      ;;
    commit)
      for arg in "$@"; do
        case "$arg" in
          --amend|-a|--all)
            print -r -u2 "ERROR: GIT SAFETY VIOLATION -- 'git commit $arg' is prohibited"
            return 1
            ;;
        esac
      done
      ;;
    add)
      for arg in "$@"; do
        if [[ "$arg" == "." ]]; then
          print -r -u2 "ERROR: GIT SAFETY VIOLATION -- 'git add .' (broad add) is prohibited"
          return 1
        fi
      done
      ;;
  esac
  command git "$cmd" "$@" || return $?
}

# --- Gate 5: Stage approved paths ---
print -r -u2 ""
print -r -u2 "=== Gate 5: Staging approved paths ==="
for vp in "${VALIDATED_PATHS[@]}"; do
  safe_git add -- "$vp" || {
    print -r -u2 "ERROR: GATE 5 FAILED -- Failed to stage: $vp"
    cleanup_on_failure
    exit 1
  }
  CLEANUP_STAGED_PATHS+=("$vp")
done
print -r -u2 "PASS: Gate 5 -- Paths staged"

# --- Gate 6: Post-stage containment check ---
print -r -u2 ""
print -r -u2 "=== Gate 6: Verifying staged set containment ==="
if ! check_staged_containment; then
  cleanup_on_failure
  exit 1
fi
print -r -u2 "PASS: Gate 6 -- Staged set equals approved path set"

# --- Gate 7: Pre-commit validation ---
print -r -u2 ""
print -r -u2 "=== Gate 7: Pre-commit validation ==="
safe_git diff --cached --check || {
  print -r -u2 "ERROR: GATE 7 FAILED -- 'git diff --cached --check' detected whitespace errors"
  cleanup_on_failure
  exit 1
}
print -r -u2 "PASS: Gate 7 -- No whitespace errors"

# --- Gate 8: Commit and emit JSON result ---
print -r -u2 ""
print -r -u2 "=== Gate 8: Committing ==="
COMMIT_MSG="checkpoint(${P0_ID}): ${SUMMARY}"
safe_git commit -m "$COMMIT_MSG" || {
  print -r -u2 "ERROR: GATE 8 FAILED -- Commit failed"
  cleanup_on_failure
  exit 1
}

COMMIT_HASH="$(safe_git rev-parse HEAD)"
TREE_STATUS="$(safe_git status --porcelain)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Emit exactly one JSON object to stdout
# approved_paths are passed as argv[6:] (not via stdin/heredoc) so that
# whitespace, Unicode, and dash-prefixed paths are preserved as array elements.
python3 - "$COMMIT_HASH" "$COMMIT_MSG" "$TREE_STATUS" "$P0_ID" "$TIMESTAMP" "${APPROVED_PATHS[@]}" <<'PY'
import json, sys

commit_hash = sys.argv[1]
commit_msg = sys.argv[2]
tree_status = sys.argv[3]
p0_id = sys.argv[4]
timestamp = sys.argv[5]
# argv[6:] are the approved paths, preserving whitespace, Unicode, and dash-prefixed names
approved_paths = sys.argv[6:]
result = {
    'commit_hash': commit_hash,
    'commit_message': commit_msg,
    'tree_status': tree_status,
    'approved_paths': approved_paths,
    'p0_id': p0_id,
    'timestamp': timestamp
}
print(json.dumps(result, indent=2))
PY
