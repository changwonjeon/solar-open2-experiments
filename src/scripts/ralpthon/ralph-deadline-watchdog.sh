#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
# 상위 3단계 이동: src/scripts/ralpthon -> src/scripts -> src -> _Upstage
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DATA_DIR="$ROOT/data/results/ralpthon/solar"
SESSION_LOG="$DATA_DIR/session.log"
WATCHDOG_LOG="$DATA_DIR/watchdog.log"
SESSION="ralphthon-loop"
TOTAL_DURATION=10800  # 3 hours in seconds
CHECK_INTERVAL=60     # Check every 60 seconds
INACTIVITY_THRESHOLD=180  # 3 minutes of no output before prompting to continue

mkdir -p "$DATA_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🟢 Watchdog started. Duration: ${TOTAL_DURATION}s, Check: ${CHECK_INTERVAL}s" >> "$WATCHDOG_LOG"

# 실행 시점 기준 3시간 측정 (start_time은 1회만 캡처되어 루프 내에서 변하지 않음)
start_time=$(date +%s)
last_activity_time=$start_time
last_content_len=0

while true; do
  current_time=$(date +%s)
  elapsed=$((current_time - start_time))
  
  # Hard stop at 3 hours
  if [ $elapsed -ge $TOTAL_DURATION ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🛑 3-hour duration (${elapsed}s) reached. Initiating graceful shutdown." >> "$WATCHDOG_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🛑 3-hour duration reached. Terminating Ralph Loop." >> "$SESSION_LOG"
    tmux send-keys -t "$SESSION" C-c
    sleep 2
    tmux send-keys -t "$SESSION" C-c
    sleep 1
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    tmux kill-session -t ralphthon-deadline 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] ✅ Ralph Loop sessions terminated. Watchdog exiting." >> "$WATCHDOG_LOG"
    exit 0
  fi
  
  # Check session activity
  current_content=$(tmux capture-pane -t "$SESSION" -p 2>/dev/null || echo "")
  current_content_len=${#current_content}
  
  # Question Mode: 권한/허가 프롬프트 감지 시 자동 승인 ('y' + Enter)
  if echo "$current_content" | grep -qiE "permission|allow|Permanent|Confirm|do you want|abort|denied|yes/no|y/N|y/n"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] ⚠️  Permission prompt detected. Auto-accepting (y)..." >> "$WATCHDOG_LOG"
    tmux send-keys -t "$SESSION" "y"
    tmux send-keys -t "$SESSION" Enter
    sleep 2
    last_activity_time=$(date +%s)
    last_content_len=$current_content_len
    continue
  fi
  
  if [ $current_content_len -gt $last_content_len ]; then
    last_activity_time=$current_time
    last_content_len=$current_content_len
  fi
  
  # If inactive for INACTIVITY_THRESHOLD, send a continuation prompt
  inactivity=$((current_time - last_activity_time))
  if [ $inactivity -ge $INACTIVITY_THRESHOLD ]; then
    remaining=$((TOTAL_DURATION - elapsed))
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] ⚠️  No activity for ${inactivity}s. Sending continue prompt (${remaining}s remaining)." >> "$WATCHDOG_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🔄 Auto-continuing after ${inactivity}s inactivity. ${remaining}s remaining." >> "$SESSION_LOG"
    continue_prompt="You have been working for ${elapsed} seconds. You have ${remaining} seconds remaining until the 3-hour Ralph Loop deadline. Review the RALPH_GOAL.md and continue working on the next P0 deliverable. Output a brief status update of what you are doing next."
    tmux send-keys -t "$SESSION" "$continue_prompt"
    sleep 1
    tmux send-keys -t "$SESSION" Enter
    last_activity_time=$current_time
    last_content_len=$current_content_len
  fi
  
  sleep $CHECK_INTERVAL
done
