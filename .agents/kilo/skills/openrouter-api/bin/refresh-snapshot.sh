#!/usr/bin/env bash
# Refresh the snapshot from the live API. Re-reads every request.sh under
# references/testpoints/ and saves the live response under
# references/testpoints/snapshot-<DATE>/<name>.json.
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TP_DIR="$SKILL_DIR/references/testpoints"
DATE="$(date -u +%Y-%m-%d)"
SNAP="$TP_DIR/snapshot-$DATE"

mkdir -p "$SNAP"

if [[ -z "${OPENROUTER_API_KILO_CLI:-}" ]]; then
  echo "FAIL: \$OPENROUTER_API_KILO_CLI is unset." >&2
  exit 2
fi

count=0
for d in "$TP_DIR"/*/; do
  name="$(basename "$d")"
  [[ "$name" == snapshot-* ]] && continue
  request="$d/request.sh"
  [[ -f "$request" ]] || continue
  path="$(cat "$request")"
  path="${path//[[:space:]]/}"
  [[ -n "$path" ]] || continue
  body="$(curl -sS \
    -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    -H "HTTP-Referer: https://kilo.local/refresh-snapshot" \
    -H "X-OpenRouter-Title: kilo-snapshot" \
    --max-time 30 \
    "https://openrouter.ai/api/v1$path")"
  printf '%s' "$body" > "$SNAP/$name.json"
  printf '%s -> %d bytes\n' "$name" "$(stat -c%s "$SNAP/$name.json")"
  count=$((count+1))
done

echo "Refreshed $count testpoints into $SNAP"
