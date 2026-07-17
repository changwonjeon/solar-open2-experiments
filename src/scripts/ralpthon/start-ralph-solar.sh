#!/bin/zsh
set -euo pipefail

# Portable path resolution: works in zsh, bash, sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$ROOT"

CONFIRMATION="${1:-}"
RALPH_GOAL_PATH="$ROOT/docs/experiments/ralpthon/RALPH_GOAL.md"
SESSION_LOG="$ROOT/data/results/ralpthon/solar/session.log"

if [[ "$CONFIRMATION" != "START-RALPH" ]]; then
  print -u2 "User start signal required. Run only after the event operator says to start."
  exit 2
fi

# Preflight checks
if [[ ! -s "$RALPH_GOAL_PATH" ]]; then
  print -u2 "RALPH_GOAL.md is missing at: $RALPH_GOAL_PATH"
  exit 3
fi

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  print -u2 "Working tree has uncommitted tracked changes. Commit or stash first."
  exit 4
fi

# Ensure output directories exist
mkdir -p "$ROOT/data/results/ralpthon/solar/checkpoints"
mkdir -p "$ROOT/data/results/ralpthon/solar"

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 🟢 Ralph Loop (Solar) starting..." >> "$SESSION_LOG"

# Check tmux sessions
for session in ralphthon-loop ralphthon-deadline; do
  if tmux has-session -t "$session" 2>/dev/null; then
    print -u2 "$session already exists. Stop it first: tmux kill-session -t $session"
    exit 5
  fi
done

# Launch Ralph Loop in tmux
# -c "$ROOT": 작업 디렉토리를 프로젝트 루트로 설정
# run-ralph-solar.sh 내부에서 claude-upstage를 인터랙티브 모드로 실행
tmux new-session -d -s ralphthon-loop -c "$ROOT" "$ROOT/src/scripts/ralpthon/run-ralph-solar.sh"
tmux new-session -d -s ralphthon-deadline "$ROOT/src/scripts/ralpthon/ralph-deadline-watchdog.sh"

# claude-upstage가 초기화되고 대화형 프롬프트가 뜰 때까지 대기
sleep 10

# 초기 랄프 프롬프트를 tmux 버퍼에 로드
# `print`는 zsh 내장 명령어로, \n을 항상 개행으로 해석함 (printf와 달리 %s 없이도 동작)
BUFFER_NAME="ralph_initial_prompt"
print -N '$ralph' '' '' | tmux load-buffer -b "$BUFFER_NAME" -
# RALPH_GOAL.md 내용을 동일한 버퍼에 이어서 추가
cat "$RALPH_GOAL_PATH" | tmux load-buffer -b "$BUFFER_NAME" -a -

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
