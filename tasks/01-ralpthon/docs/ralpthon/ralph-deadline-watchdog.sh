#!/bin/zsh
set -euo pipefail

# This file is prepared before the event but is not started until the user
# explicitly starts Ralph. Ralph owns its normal 15:20/15:28 shutdown gates.

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
cd "$ROOT"

sleep_until() {
  local target="$1"
  local now target_epoch delta
  now="$(date +%s)"
  target_epoch="$(date -j -f '%Y-%m-%d %H:%M:%S' "2026-07-12 $target" +%s)"
  delta=$(( target_epoch - now ))
  if (( delta > 0 )); then
    sleep "$delta"
  fi
}

sleep_until "15:20:00"
omx state write --input '{"mode":"ralph","current_phase":"verifying"}' --json || true

sleep_until "15:28:00"
omx state write --input '{"mode":"ralph","current_phase":"verifying"}' --json || true

sleep_until "15:30:00"
omx cancel || true
if tmux has-session -t ralphthon-loop 2>/dev/null; then
  tmux send-keys -t ralphthon-loop C-c
  sleep 5
fi
if tmux has-session -t ralphthon-loop 2>/dev/null; then
  tmux kill-session -t ralphthon-loop
fi
if tmux has-session -t ralphthon-awake 2>/dev/null; then
  tmux kill-session -t ralphthon-awake
fi
