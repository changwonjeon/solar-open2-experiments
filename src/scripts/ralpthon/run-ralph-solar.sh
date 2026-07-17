#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h:h}"
cd "$ROOT"

# Launch claude-upstage WITHOUT any flags (Question Mode approach)
# The watchdog will inject the prompt and handle permissions via tmux
exec claude-upstage
