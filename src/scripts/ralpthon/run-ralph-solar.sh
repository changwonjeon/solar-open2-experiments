#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h:h}"
cd "$ROOT"

# claude-upstage는 파서가 --allow-dangerously-skip-permissions를 거부하므로 인자 없이 실행
# Watchdog가 tmux send-keys로 프롬프트 및 권한 승인을 자동 주입함 (Question Mode)
exec claude-upstage
