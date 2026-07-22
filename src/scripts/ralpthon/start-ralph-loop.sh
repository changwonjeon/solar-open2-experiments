#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
CONFIRMATION="${1:-}"

if [[ "$CONFIRMATION" != "START-RALPH" ]]; then
  print -u2 "User start signal required. Run only after the event operator says to start."
  exit 2
fi

cd "$ROOT"

if [[ ! -s RALPH_GOAL.md ]]; then
  print -u2 "RALPH_GOAL.md is missing."
  exit 3
fi

if [[ -n "$(git status --porcelain)" ]]; then
  print -u2 "Working tree is not clean. Freeze and commit preflight artifacts first."
  exit 4
fi

if ! tmux has-session -t ralphthon-awake 2>/dev/null; then
  tmux new-session -d -s ralphthon-awake "/usr/bin/caffeinate -dimsu -t 11400"
fi

for session in ralphthon-loop ralphthon-deadline; do
  if tmux has-session -t "$session" 2>/dev/null; then
    print -u2 "$session already exists."
    exit 5
  fi
done

tmux new-session -d -s ralphthon-loop -c "$ROOT" "$ROOT/work/run-ralph-direct.sh"
tmux new-session -d -s ralphthon-deadline "$ROOT/work/ralph-deadline-watchdog.sh"

print "Ralph started in tmux session: ralphthon-loop"
print "Deadline watcher: ralphthon-deadline"
print "Read-only inspection: tmux attach -t ralphthon-loop"
