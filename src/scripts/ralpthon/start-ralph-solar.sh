#!/bin/zsh
set -euo pipefail

# Robust SCRIPT_DIR and ROOT resolution
if [[ -n "${ZSH_VERSION:-}" ]]; then
  SCRIPT_DIR="${0:A:h}"
else
  _script_path="$0"
  if [[ "$_script_path" != /* ]]; then
    _script_path="$(pwd)/$_script_path"
  fi
  SCRIPT_DIR="$(cd "$(dirname "$_script_path")" && pwd)"
fi
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Debug logging (nohup-safe: all stderr goes to file only)
exec 2>/tmp/ralph-start-debug.log
echo "[DEBUG] SCRIPT_DIR=$SCRIPT_DIR" >&2
echo "[DEBUG] ROOT=$ROOT" >&2
echo "[DEBUG] pwd=$PWD" >&2
echo "[DEBUG] \$0=$0" >&2
echo "[DEBUG] RALPH_GOAL_PATH=$ROOT/docs/experiments/ralphthon/RALPH_GOAL.md" >&2

mkdir -p "$ROOT/data/results/ralphthon/solar/checkpoints"
mkdir -p "$ROOT/data/results/ralphthon/solar"

CONFIRMATION="${1:-}"
RALPH_GOAL_PATH="$ROOT/docs/experiments/ralphthon/RALPH_GOAL.md"
SESSION_LOG="$ROOT/data/results/ralphthon/solar/session.log"

if [[ "$CONFIRMATION" != "START-RALPH" ]]; then
  echo "User start signal required. Run only after the event operator says to start." >&2
  exit 2
fi

if [[ ! -s "$RALPH_GOAL_PATH" ]]; then
  echo "RALPH_GOAL.md is missing at: $RALPH_GOAL_PATH" >&2
  exit 3
fi

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Working tree has uncommitted tracked changes. Commit or stash first." >&2
  exit 4
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] Ralph Loop (Solar) starting..." >> "$SESSION_LOG"

# Check tmux sessions
for session in ralphthon-loop ralphthon-deadline; do
  if tmux has-session -t "$session" 2>/dev/null; then
    echo "$session already exists. Stop it first: tmux kill-session -t $session" >&2
    exit 5
  fi
done

# Launch Ralph Loop in tmux
tmux new-session -d -s ralphthon-loop -c "$ROOT" "$ROOT/src/scripts/ralpthon/run-ralph-solar.sh"
tmux new-session -d -s ralphthon-deadline "$ROOT/src/scripts/ralpthon/ralph-deadline-watchdog.sh"

# Wait for claude-upstage to initialize
sleep 10

# Load initial prompt into tmux buffer
BUFFER_NAME="ralph_initial_prompt"
printf '\$ralph\n\n' | tmux load-buffer -b "$BUFFER_NAME" -
cat "$RALPH_GOAL_PATH" | tmux load-buffer -b "$BUFFER_NAME" -a -

# Paste buffer into ralphthon-loop session
tmux paste-buffer -b "$BUFFER_NAME" -t ralphthon-loop
tmux send-keys -t ralphthon-loop Enter
sleep 2

# Auto-accept permission prompts if detected (Question Mode)
if tmux capture-pane -t ralphthon-loop -p 2>/dev/null | grep -qiE "permission|confirm|permanent|y/N|abort"; then
  tmux send-keys -t ralphthon-loop "y"
  tmux send-keys -t ralphthon-loop Enter
  sleep 2
fi

echo "Ralph (Solar) started in tmux session: ralphthon-loop"
echo "Deadline watcher: ralphthon-deadline (3-hour timeout)"
echo "Read-only inspection: tmux attach -t ralphthon-loop"
echo "Read-only inspection: tmux attach -t ralphthon-deadline"
echo "Session log: $SESSION_LOG"
echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] Ralph Loop (Solar) launched successfully." >> "$SESSION_LOG"
