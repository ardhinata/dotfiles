#!/usr/bin/env bash
set -u

# Replay OpenRouter API testpoints and diff against .expected.json shape.
# Reads $OPENROUTER_API_KILO_CLI. Writes nothing to git (no auth headers,
# no bodies committed outside the snapshot).
#
# Usage:
#   bin/probe-openrouter-api.sh                # run all testpoints
#   bin/probe-openrouter-api.sh 02-models-count  # run one
#   bin/probe-openrouter-api.sh --list         # list known testpoints
#
# Testpoint layout (one dir per endpoint or query-shape probe):
#   references/testpoints/<name>/
#     request.sh    - bash script that prints the path segment to GET
#     .expected.json - {"status": <int>, "keys_required": [...], "shape": "object"|"array"}
#     README.md     - one-paragraph note on what it checks

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTPOINTS_DIR="$SKILL_DIR/references/testpoints"
BASE_URL="https://openrouter.ai/api/v1"

if [[ "${1:-}" == "--list" ]]; then
  for d in "$TESTPOINTS_DIR"/*/; do
    n="$(basename "$d")"
    [[ "$n" == snapshot-* ]] && continue
    echo "$n"
  done | sort
  exit 0
fi

if [[ -z "${OPENROUTER_API_KILO_CLI:-}" ]]; then
  echo "FAIL: \$OPENROUTER_API_KILO_CLI is unset. Export the API key and retry." >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "FAIL: jq is required." >&2
  exit 2
fi
if ! command -v curl >/dev/null 2>&1; then
  echo "FAIL: curl is required." >&2
  exit 2
fi

run_one() {
  local tp_dir="$1"
  local name
  name="$(basename "$tp_dir")"
  local request="$tp_dir/request.sh"
  local expected="$tp_dir/.expected.json"

  if [[ ! -f "$request" || ! -f "$expected" ]]; then
    echo "SKIP  $name (missing request.sh or .expected.json)"
    return 0
  fi

  local path
  path="$(cat "$request")"
  # Trim trailing newline / whitespace
  path="${path//[[:space:]]/}"
  if [[ -z "$path" ]]; then
    echo "FAIL  $name (request.sh is empty)"
    return 1
  fi

  local raw status body expected_status missing k
  raw="$(curl -sS -w '\n%{http_code}' \
    -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    -H "HTTP-Referer: https://kilo.local/probe" \
    -H "X-OpenRouter-Title: kilo-probe" \
    --max-time 30 \
    -X GET \
    "$BASE_URL$path")"
  status="${raw##*$'\n'}"
  body="${raw%$'\n'*}"

  expected_status="$(jq -r '.status // 200' "$expected")"
  if [[ "$status" != "$expected_status" ]]; then
    echo "FAIL  $name  path=$path  status=$status (expected $expected_status)"
    return 1
  fi

  # Required-key check (skip for non-2xx where body is an error envelope)
  # keys_required entries are jq expressions that evaluate to truthy when the
  # expected key/field is present. Use bare "data" for top-level, ".data.id"
  # for nested. Anything else is treated as a literal jq expr evaluated with
  # `jq -e`.
  if [[ "$status" =~ ^2 ]]; then
    missing=()
    while IFS= read -r k; do
      [[ -z "$k" ]] && continue
      local probe_expr
      if [[ "$k" == .* ]]; then
        probe_expr="$k | type == \"object\" and has(\"${k#.}\")"
      else
        # Bare key: accept if top-level has it, OR .data has it, OR .data[0] has it
        probe_expr="has(\"$k\") or (.data | type == \"object\" and has(\"$k\")) or ((.data | type) == \"array\" and (.data[0] | type == \"object\") and (.data[0] | has(\"$k\")))"
      fi
      if ! jq -e "$probe_expr" <<<"$body" >/dev/null 2>&1; then
        missing+=("$k")
      fi
    done < <(jq -r '.keys_required // [] | .[]' "$expected")

    if (( ${#missing[@]} > 0 )); then
      echo "FAIL  $name  missing keys: ${missing[*]}"
      return 1
    fi
  fi

  local summary
  summary="$(jq -c 'if type=="array" then "array(\(length))"
                 elif type=="object" then "object(keys=\(keys|length))"
                 else type end' <<<"$body" 2>/dev/null || echo "non-json")"
  echo "PASS  $name  status=$status  body=$summary"
}

filter="${1:-}"
ran=0
failed=0
for tp in "$TESTPOINTS_DIR"/*/; do
  [[ "$(basename "$tp")" == snapshot-* ]] && continue
  if [[ -n "$filter" ]] && [[ "$(basename "$tp")" != "$filter" ]]; then
    continue
  fi
  if run_one "$tp"; then
    ran=$((ran+1))
  else
    ran=$((ran+1))
    failed=$((failed+1))
  fi
done

if (( ran == 0 )); then
  echo "No testpoints matched (filter='$filter'). Try --list." >&2
  exit 2
fi

echo "----"
echo "Ran $ran, failed $failed"
exit $(( failed > 0 ? 1 : 0 ))
