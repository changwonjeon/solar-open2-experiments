#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
cd "$ROOT"

goal_text="$(<RALPH_GOAL.md)"
task_text=$'$ralph\n\n'"$goal_text"
export OMX_RALPH_APPEND_INSTRUCTIONS_FILE="$ROOT/.omx/ralph/session-instructions.md"
exec codex -a never -s workspace-write -C "$ROOT" "$task_text"
