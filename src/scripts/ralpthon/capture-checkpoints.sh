#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
DATA_DIR="$ROOT/data/results/ralpthon/solar"
CHECKPOINT_DIR="$DATA_DIR/checkpoints"
SESSION_LOG="$DATA_DIR/session.log"

# Configuration
POLL_INTERVAL="${POLL_INTERVAL:-30}"
MAX_CHECKPOINTS="${MAX_CHECKPOINTS:-14}"  # P0 개수 (RALPH_GOAL.md의 14개 P0 항목)

usage() {
  cat <<EOF
Usage: $(basename "$0") [COMMAND] [OPTIONS]

Commands:
  start               Start checkpoint capture monitoring
  stop                Stop checkpoint capture
  status              Check monitoring status
  list                List captured checkpoints
  trigger [N]         Manually trigger checkpoint N capture

Options:
  --poll-interval SEC  Set polling interval in seconds (default: 30)
  --max-checkpoints N  Set max number of checkpoints (default: 14)
  --output DIR         Set output directory (default: data/results/ralpthon/solar/checkpoints/)

Environment:
  POLL_INTERVAL        Polling interval in seconds (default: 30)
  MAX_CHECKPOINTS      Maximum number of checkpoints (default: 14)

Examples:
  $(basename "$0") start                          # Start monitoring
  $(basename "$0") start --poll-interval 10       # Poll every 10 seconds
  $(basename "$0") stop                           # Stop monitoring
  $(basename "$0") list                           # List checkpoints
  $(basename "$0") trigger 1                      # Manually capture checkpoint 1
EOF
  exit 0
}

# Parse arguments
COMMAND="${1:-}"
shift 2>/dev/null || true

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --poll-interval) POLL_INTERVAL="$2"; shift 2 ;;
    --max-checkpoints) MAX_CHECKPOINTS="$2"; shift 2 ;;
    --output) CHECKPOINT_DIR="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Output directory setup
mkdir -p "$CHECKPOINT_DIR"

# P0 리스트 파싱 (RALPH_GOAL.md에서 "- "로 시작하는 항목 추출)
# 실제 P0 번호는 스크립트에서 순서대로 할당
P0_LIST=()
if [[ -f "$ROOT/RALPH_GOAL.md" ]]; then
  while IFS= read -r line; do
    # P0 Deliverables 섹션의 항목 추출
    if [[ "$line" =~ ^-\ \[.\](.*) ]] || [[ "$line" =~ ^-\ `.*`\ 을 ]]; then
      continue  # 이미 처리된 항목 스킵
    fi
    if [[ "$line" =~ ^-\ ..*을.* ]] || [[ "$line" =~ ^-\ ..*를.* ]] || [[ "$line" =~ ^-\ ..*$ ]]; then
      P0_LIST+=("$line")
    fi
  done < <(sed -n '/^# P0 Deliverables$/,/^#/p' "$ROOT/RALPH_GOAL.md" | tail -n +2 | head -n -1)
fi

# 대체: 하드코딩된 P0 리스트 (14개)
if [[ ${#P0_LIST[@]} -eq 0 ]]; then
  P0_LIST=(
    "P0-1: .codex/skills/auto-research/ upstream subtree 설치 및 hash 검증"
    "P0-2: .codex/skills/ralphthon-track2-review-agent/ wrapper Skill, references, assets, validators 생성"
    "P0-3: .codex/agents/ live Review Worker와 build verifier/auditor 생성"
    "P0-4: canonical schema 보존 (Contribution, Significance, Originality, Comment)"
    "P0-5: 각 논문 input/evidence hash per-paper manifest 동결"
    "P0-6: Root만 claim/post/status/ledger 소유, Worker 3개는 ReviewDraft만 반환"
    "P0-7: mock adapter, bounded queue, lease, atomic ledger, idempotency, claim/post status-first reconciliation 구현"
    "P0-8: gold fixture 동결, naive single-pass baseline, TP/FP/FN, location-match 규칙, threshold 기록"
    "P0-9: submission/technical-report.tex와 submission/technical-report.pdf 생성"
    "P0-10: submission/TITLE.txt, submission/ABSTRACT.txt, review-agent.md, README.md, MANUAL_PLATFORM.md, HANDOFF.md 생성"
    "P0-11: outbox/<paper_id>.json과 clipboard-ready text fallback 생성"
    "P0-12: mock 10편 3회 실행, assigned count 전체 완료, schema 100%, duplicate 0건 확인"
    "P0-13: malformed JSON, Worker timeout, claim timeout, post timeout, process restart 주입 테스트"
    "P0-14: Tectonic PDF 빌드, pdfinfo 페이지 확인, 익명성·placeholder 검사"
  )
fi

# P0 번호 → 설명 매핑 생성
p0_map=()
for i in $(seq 1 ${#P0_LIST[@]}); do
  p0_map[$i]="${P0_LIST[$((i-1))]}"
done

# 상태 파일
STATE_FILE="$DATA_DIR/checkpoint-monitor.state"
PID_FILE="$DATA_DIR/checkpoint-monitor.pid"

# 이전 파일 크기 저장 (변경 감지용)
prev_size_file="$DATA_DIR/.session_log_prev_size"

capture_checkpoint() {
  local checkpoint_num="$1"
  local timestamp
  timestamp="$(date -Iseconds)"
  local checkpoint_file="$CHECKPOINT_DIR/checkpoint-${checkpoint_num}.json"
  local log_snippet=""

  # session.log가 있으면 최근 로그 추출
  if [[ -f "$SESSION_LOG" ]]; then
    local log_size
    log_size="$(wc -c < "$SESSION_LOG")"
    local prev_size=0
    [[ -f "$prev_size_file" ]] && prev_size="$(cat "$prev_size_file")"

    if [[ "$log_size" -gt "$prev_size" ]]; then
      # 변경된 부분 추출 (간단한 방식: 최근 50줄)
      log_snippet="$(tail -n 50 "$SESSION_LOG" 2>/dev/null | head -n 30 || echo '')"
    fi
    echo "$log_size" > "$prev_size_file"
  fi

  # 체크포인트 JSON 생성
  cat > "$checkpoint_file" <<EOF
{
  "checkpoint_number": $checkpoint_num,
  "checkpoint_description": "${p0_map[$checkpoint_num]:-}",
  "timestamp": "$timestamp",
  "source": "capture-checkpoints.sh",
  "detection_method": "polling",
  "session_log_changed": $([[ -f "$SESSION_LOG" ]] && echo "true" || echo "false"),
  "p0_mapping": {
    "number": $checkpoint_num,
    "description": "${p0_map[$checkpoint_num]:-}"
  },
  "log_snippet": $(echo "$log_snippet" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo 'null'),
  "session_log_size": $([[ -f "$SESSION_LOG" ]] && wc -c < "$SESSION_LOG" || echo "0"),
  "data_dir": "$DATA_DIR",
  "checkpoint_dir": "$CHECKPOINT_DIR"
}
EOF

  echo "✅ Checkpoint $checkpoint_num captured: $checkpoint_file"
  echo "   Description: ${p0_map[$checkpoint_num]:-}"
  echo "   Timestamp: $timestamp"

  # 상태 업데이트
  echo "{\"last_checkpoint\": $checkpoint_num, \"timestamp\": \"$timestamp\"}" > "$STATE_FILE"

  # 체크리스트 업데이트
  local checklist_file="$DATA_DIR/checkpoint-checklist.md"
  if [[ ! -f "$checklist_file" ]]; then
    echo "# Checkpoint Checklist" > "$checklist_file"
    echo "" >> "$checklist_file"
    echo "| # | P0 Description | Status | Timestamp |" >> "$checklist_file"
    echo "|---|----------------|--------|-----------|" >> "$checklist_file"
  fi

  # 해당 체크포인트 상태 업데이트
  if grep -q "^| $checkpoint_num |" "$checklist_file" 2>/dev/null; then
    sed -i "s/^| $checkpoint_num |.*| .*|/| $checkpoint_num | ${p0_map[$checkpoint_num]:-} | ✅ Completed | $timestamp |/" "$checklist_file"
  else
    echo "| $checkpoint_num | ${p0_map[$checkpoint_num]:-} | ✅ Completed | $timestamp |" >> "$checklist_file"
  fi
}

# 모니터링 시작
start_monitoring() {
  echo "🔍 Starting checkpoint monitoring..."
  echo "   Poll interval: ${POLL_INTERVAL}s"
  echo "   Max checkpoints: $MAX_CHECKPOINTS"
  echo "   Output directory: $CHECKPOINT_DIR"
  echo "   Session log: $SESSION_LOG"
  echo ""

  # 이미 실행 중인지 확인
  if [[ -f "$PID_FILE" ]]; then
    local old_pid
    old_pid="$(cat "$PID_FILE")"
    if kill -0 "$old_pid" 2>/dev/null; then
      echo "⚠️  Monitor already running (PID: $old_pid). Use 'stop' to stop first."
      exit 1
    else
      echo "⚠️  Stale PID file found. Removing..."
      rm -f "$PID_FILE"
    fi
  fi

  # state 초기화
  echo "{\"last_checkpoint\": 0, \"timestamp\": \"$(date -Iseconds)\"}" > "$STATE_FILE"
  echo "$$" > "$PID_FILE"

  # P0 체크리스트 초기화
  local checklist_file="$DATA_DIR/checkpoint-checklist.md"
  echo "# Checkpoint Checklist (P0 Deliverables)" > "$checklist_file"
  echo "" >> "$checklist_file"
  echo "| # | P0 Description | Status | Timestamp |" >> "$checklist_file"
  echo "|---|----------------|--------|-----------|" >> "$checklist_file"
  for i in $(seq 1 ${#P0_LIST[@]}); do
    echo "| $i | ${p0_map[$i]:-} | ⏳ Pending | - |" >> "$checklist_file"
  done

  # session.log가 없으면 생성
  mkdir -p "$DATA_DIR"
  touch "$SESSION_LOG"

  # 이전 파일 크기 초기화
  echo "0" > "$prev_size_file"

  echo ""
  echo "📊 Monitoring started. Capturing checkpoints as P0 items complete."
  echo "   Use '$(basename "$0") stop' to stop monitoring."
  echo ""

  # 메인 모니터링 루프
  last_checkpoint=0
  consecutive_no_change=0
  max_consecutive_no_change=10  # 10회 연속 변화 없으면 종료

  while true; do
    # 이미 모든 체크포인트 캡처 완료
    if [[ $last_checkpoint -ge $MAX_CHECKPOINTS ]]; then
      echo "✅ All $MAX_CHECKPOINTS checkpoints captured. Monitoring complete."
      break
    fi

    # session.log 변경 감지
    if [[ -f "$SESSION_LOG" ]]; then
      local current_size
      current_size="$(wc -c < "$SESSION_LOG")"
      local prev_size=0
      [[ -f "$prev_size_file" ]] && prev_size="$(cat "$prev_size_file")"

      if [[ "$current_size" -gt "$prev_size" ]]; then
        echo "📝 Session log changed: ${prev_size} → ${current_size} bytes"

        # P0 완료 패턴 감지 (간단한 휴리스틱)
        local new_checkpoint=0
        for i in $(seq $((last_checkpoint + 1)) $MAX_CHECKPOINTS); do
          # 로그에 P0 완료 키워드 또는 체크리스트 패턴 감지
          if grep -qi "P0.*$i.*완료\|checkpoint.*$i.*captured\|✓.*P0.*$i\|P0-$i.*done\|✅.*P0.*$i" "$SESSION_LOG" 2>/dev/null; then
            new_checkpoint=$i
            break
          fi
        done

        # 체크포인트가 발견되면 캡처
        if [[ $new_checkpoint -gt $last_checkpoint ]]; then
          capture_checkpoint "$new_checkpoint"
          last_checkpoint=$new_checkpoint
          consecutive_no_change=0
        else
          consecutive_no_change=$((consecutive_no_change + 1))
        fi

        # 변화 저장
        echo "$current_size" > "$prev_size_file"
      else
        consecutive_no_change=$((consecutive_no_change + 1))
      fi
    fi

    # timeout 체크 (선택적)
    if [[ $consecutive_no_change -ge $max_consecutive_no_change ]]; then
      echo "⚠️  No changes detected for $((consecutive_no_change * POLL_INTERVAL))s. Consider stopping."
    fi

    sleep "$POLL_INTERVAL"
  done

  # 정리
  rm -f "$PID_FILE"
  echo "📊 Monitoring stopped."
}

# 모니터링 중지
stop_monitoring() {
  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "🛑 Stopping checkpoint monitor (PID: $pid)..."
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -9 "$pid" 2>/dev/null || true
      rm -f "$PID_FILE"
      echo "✅ Monitor stopped."
    else
      echo "⚠️  Monitor not running (stale PID: $pid). Cleaning up..."
      rm -f "$PID_FILE"
    fi
  else
    echo "ℹ️  No monitor running."
  fi
}

# 상태 확인
show_status() {
  echo "🔍 Checkpoint Monitor Status"
  echo ""

  if [[ -f "$PID_FILE" ]]; then
    local pid
    pid="$(cat "$PID_FILE")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "   Status: 🟢 Running (PID: $pid)"
    else
      echo "   Status: 🟡 Stale PID (not running)"
    fi
  else
    echo "   Status: ⚪ Not running"
  fi

  echo ""
  echo "   Poll interval: ${POLL_INTERVAL}s"
  echo "   Max checkpoints: $MAX_CHECKPOINTS"
  echo "   Output directory: $CHECKPOINT_DIR"
  echo ""

  if [[ -f "$STATE_FILE" ]]; then
    echo "   Last checkpoint: $(cat "$STATE_FILE" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"{d.get("last_checkpoint", 0)}/{MAX_CHECKPOINTS}")' 2>/dev/null || echo 'N/A')"
    echo "   Last update: $(cat "$STATE_FILE" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("timestamp", "N/A"))' 2>/dev/null || echo 'N/A')"
  fi

  echo ""
  if [[ -f "$CHECKPOINT_DIR/checkpoint-checklist.md" ]]; then
    echo "📊 Checkpoint Checklist:"
    cat "$CHECKPOINT_DIR/checkpoint-checklist.md"
  else
    echo "   No checklist found."
  fi
}

# 체크포인트 목록
list_checkpoints() {
  echo "📋 Captured Checkpoints:"
  echo ""

  local count=0
  for f in "$CHECKPOINT_DIR"/checkpoint-*.json; do
    [[ -f "$f" ]] || continue
    count=$((count + 1))
    local num
    num="$(basename "$f" | sed 's/checkpoint-\([0-9]*\).json/\1/')"
    local timestamp
    timestamp="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("timestamp", "N/A"))' "$f" 2>/dev/null || echo 'N/A')"
    local desc
    desc="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("p0_mapping", {}).get("description", "N/A"))' "$f" 2>/dev/null || echo 'N/A')"
    echo "   [$num] $timestamp — $desc"
  done

  if [[ $count -eq 0 ]]; then
    echo "   No checkpoints captured yet."
  else
    echo ""
    echo "   Total: $count checkpoint(s)"
  fi
}

# 수동 트리거
trigger_checkpoint() {
  local checkpoint_num="${1:-1}"
  echo "🎯 Manually triggering checkpoint $checkpoint_num..."
  capture_checkpoint "$checkpoint_num"
}

# 명령어 처리
case "$COMMAND" in
  start)
    start_monitoring
    ;;
  stop)
    stop_monitoring
    ;;
  status)
    show_status
    ;;
  list)
    list_checkpoints
    ;;
  trigger)
    trigger_checkpoint "${1:-1}"
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown command: $COMMAND"
    usage
    ;;
esac

