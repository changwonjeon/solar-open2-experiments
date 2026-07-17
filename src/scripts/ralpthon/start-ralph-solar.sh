#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
# 스크립트 위치: src/scripts/ralpthon/ → 상위 3단계 이동 → _Upstage (프로젝트 루트)
ROOT="${SCRIPT_DIR:h:h:h}"
CONFIRMATION="${1:-}"
RALPH_GOAL_PATH="$ROOT/docs/experiments/ralphthon/RALPH_GOAL.md"
SESSION_LOG="$ROOT/data/results/ralpthon/solar/session.log"

if [[ "$CONFIRMATION" != "START-RALPH" ]]; then
  print -u2 "User start signal required. Run only after the event operator says to start."
  exit 2
fi

cd "$ROOT"

# Preflight checks
if [[ ! -s "$RALPH_GOAL_PATH" ]]; then
  print -u2 "RALPH_GOAL.md is missing at: $RALPH_GOAL_PATH"
  exit 3
fi

# Skip git status check for untracked execution artifacts (ralphthon directories).
# We only care about tracked files being clean for reproducibility.
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  print -u2 "Working tree has uncommitted tracked changes. Commit or stash first."
  exit 4
fi

# Ensure output directories exist
mkdir -p "$ROOT/data/results/ralpthon/solar/checkpoints"
mkdir -p "$ROOT/data/results/ralpthon/solar"

# Record start time
echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🟢 Ralph Loop (Solar) starting..." >> "$SESSION_LOG"

# Check tmux sessions
for session in ralphthon-loop ralphthon-deadline; do
  if tmux has-session -t "$session" 2>/dev/null; then
    print -u2 "$session already exists. Stop it first: tmux kill-session -t $session"
    exit 5
  fi
done

# Launch Ralph Loop in tmux
tmux new-session -d -s ralphthon-loop -c "$ROOT" "$ROOT/src/scripts/ralpthon/run-ralph-solar.sh"
tmux new-session -d -s ralphthon-deadline "$ROOT/src/scripts/ralpthon/ralph-deadline-watchdog.sh"

# claude-upstage가 초기화되고 대화형 프롬프트가 뜰 때까지 대기
sleep 10

# 초기 랄프 프롬프트를 tmux 버퍼에 로드
BUFFER_NAME="ralph_initial_prompt"
printf '$ralph

' | tmux load-buffer -b "$BUFFER_NAME"
cat "$RALPH_GOAL_PATH" | tmux load-buffer -b "$BUFFER_NAME" -a

# 버퍼를 ralphthon-loop 세션에 붙여넣기
tmux paste-buffer -b "$BUFFER_NAME" -t ralphthon-loop
tmux send-keys -t ralphthon-loop Enter
sleep 2

# 권한 프롬프트 감지 시 자동 응답 (Question Mode)
if tmux capture-pane -t ralphthon-loop -p 2>/dev/null | grep -qiE "permission|confirm|permanent|y\/N|abort"; then
  tmux send-keys -t ralphthon-loop "y"
  tmux send-keys -t ralphthon-loop Enter
  sleep 2
fi

print "✅ Ralph (Solar) started in tmux session: ralphthon-loop"
print "✅ Deadline watcher: ralphthon-deadline (3-hour timeout)"
print "📋 Read-only inspection: tmux attach -t ralphthon-loop"
print "📋 Read-only inspection: tmux attach -t ralphthon-deadline"
print "📊 Session log: $SESSION_LOG"
print ""
echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] ✅ Ralph Loop (Solar) launched successfully." >> "$SESSION_LOG"
