#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h:h}"
cd "$ROOT"

# Launch Claude Code (Solar Open2 via claude-upstage) in interactive REPL mode.
# The watchdog (ralph-deadline-watchdog.sh) will:
# 1. Send the initial Ralph prompt via tmux send-keys (does not use CLI flags).
# 2. Monitor for permission prompts and auto-accept them ("Question Mode").
# 3. Send continuation prompts when inactive for >3 mins.
# 4. Hard-stop after 3 hours (based on script start time).
#
# NOTE: claude-upstage is launched WITHOUT flags because its parser
# does not recognize --allow-dangerously-skip-permissions.
# Permissions are handled interactively by the watchdog via tmux send-keys.
exec claude-upstage
