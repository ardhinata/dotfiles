#!/bin/sh
# kilo-helper-shared-detect — agent-only detection for the kilo-shared CLI.
#
# Prints the absolute path of an installed wrapper on stdout, or a remediation
# hint on stderr with exit 1.
#
# Two-tier detection (mirrors spec-kit's check_tool):
#   Tier 1: $HOME/.local/share/kilo/bin/kilo-shared exists & executable → print
#   Tier 2: otherwise → look for the asset in the chezmoi source, emit a hint
#
# Usage:
#   kilo-helper-shared-detect kilo-shared           → prints wrapper path
#   kilo-helper-shared-detect kilo-helper-shared-detect
#
# Hidden-prefix (`kilo-helper-*`) marks this as agent infrastructure; users
# never invoke it directly. The wrapper's own error path surfaces a clear
# "wrapper missing, run chezmoi apply" message — most callers can skip this
# helper entirely.

set -e

if [ $# -lt 1 ]; then
  echo "kilo-helper-shared-detect: usage: kilo-helper-shared-detect <name>" >&2
  exit 2
fi

name="$1"
bin="$HOME/.local/share/kilo/bin/$name"

if [ -x "$bin" ]; then
  printf '%s\n' "$bin"
  exit 0
fi

asset="$HOME/.local/share/chezmoi/dot_config/kilo/exact_skills/shared-context/assets/kilo-shared.sh"
if [ -f "$asset" ]; then
  echo "$name not installed. Run: chezmoi apply" >&2
else
  echo "$name asset missing at $asset" >&2
fi
exit 1
