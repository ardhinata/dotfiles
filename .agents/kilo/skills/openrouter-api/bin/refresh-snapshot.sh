#!/usr/bin/env bash
# Refresh the snapshot from the live API. Re-reads every request.sh under
# references/testpoints/ and saves the live response under
# references/testpoints/snapshot-<DATE>/<name>.json. Picks the auth env
# var per testpoint from `.expected.json`'s `auth` field:
#   - "cli"  -> $OPENROUTER_API_KILO_CLI       (default)
#   - "mgmt" -> $OPENROUTER_MANAGEMENT_KEY
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TP_DIR="$SKILL_DIR/references/testpoints"
DATE="$(date -u +%Y-%m-%d)"
SNAP="$TP_DIR/snapshot-$DATE"

mkdir -p "$SNAP"

if [[ -z "${OPENROUTER_API_KILO_CLI:-}" && -z "${OPENROUTER_MANAGEMENT_KEY:-}" ]]; then
  echo "FAIL: both \$OPENROUTER_API_KILO_CLI and \$OPENROUTER_MANAGEMENT_KEY are unset." >&2
  exit 2
fi

count=0
for d in "$TP_DIR"/*/; do
  name="$(basename "$d")"
  [[ "$name" == snapshot-* ]] && continue
  request="$d/request.sh"
  expected="$d/.expected.json"
  [[ -f "$request" ]] || continue
  [[ -f "$expected" ]] || continue
  path="$(cat "$request")"
  path="${path//[[:space:]]/}"
  [[ -n "$path" ]] || continue

  auth="$(jq -r '.auth // "cli"' "$expected")"
  case "$auth" in
    mgmt)
      key_var="OPENROUTER_MANAGEMENT_KEY"
      ;;
    cli)
      key_var="OPENROUTER_API_KILO_CLI"
      ;;
    *)
      echo "FAIL: unknown auth='$auth' in $name/.expected.json" >&2
      exit 2
      ;;
  esac
  key_value="${!key_var:-}"
  if [[ -z "$key_value" ]]; then
    printf 'SKIP %s  (auth=%s, $%s unset)\n' "$name" "$auth" "$key_var"
    continue
  fi

  body="$(curl -sS \
    -H "Authorization: Bearer $key_value" \
    -H "HTTP-Referer: https://kilo.local/refresh-snapshot" \
    -H "X-OpenRouter-Title: kilo-snapshot" \
    --max-time 30 \
    "https://openrouter.ai/api/v1$path")"
  printf '%s' "$body" > "$SNAP/$name.json"
  printf '%s -> %d bytes  auth=%s\n' "$name" "$(stat -c%s "$SNAP/$name.json")" "$auth"
  count=$((count+1))
done

echo "Refreshed $count testpoints into $SNAP"
