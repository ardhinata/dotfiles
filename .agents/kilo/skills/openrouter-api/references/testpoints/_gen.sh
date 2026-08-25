#!/usr/bin/env bash
# Generates testpoint request.sh + .expected.json + README.md files.
# Run once from the skill root: bash references/testpoints/_gen.sh

set -euo pipefail
cd "$(dirname "$0")"

# Helper: write_request <path>  -- request.sh prints the path
# Helper: write_expected <status> <keys_csv>  -- .expected.json shape + required keys
# Helper: write_readme <note>

write_request() {
  printf '%s\n' "$1" > "$2/request.sh"
}

write_expected() {
  local status="$1" shape="$2" dir="$3"
  shift 3
  local keys_json="["
  local first=1
  for k in "$@"; do
    [[ -z "$k" ]] && continue
    if [[ $first -eq 1 ]]; then first=0; else keys_json+=","; fi
    keys_json+="\"$k\""
  done
  keys_json+="]"
  jq -n --arg status "$status" --arg shape "$shape" --argjson keys "$keys_json" \
    '{status: ($status|tonumber), shape: $shape, keys_required: $keys}' > "$dir/.expected.json"
}

write_readme() {
  cat > "$1/README.md" <<'EOF'
# Testpoint: NAME

NOTE

Expected status: 'STATUS'.
Expected body shape: 'SHAPE'.
Required keys: 'KEYS'.
Last verified: 2026-08-25.
EOF
  # Substitute placeholders
  sed -i "s|^# Testpoint: NAME|# Testpoint: $2|; s|^NOTE|$3|; s|'STATUS'|'$4'|; s|'SHAPE'|'$5'|; s|'KEYS'|'$6'|" "$1/README.md"
}

# 01-models  -- GET /models (default)
write_request "/models" "01-models"
write_expected 200 object "01-models" data links total_count
write_readme "01-models" "/models" "Default '/models' listing. Confirms 'data[]', 'links', 'total_count' shape and array length ~400+." 200 "object{keys=3}" "data,links,total_count"

# 02-models-count  -- GET /models/count
write_request "/models/count" "02-models-count"
write_expected 200 object "02-models-count" data
write_readme "02-models-count" "/models/count" "Total model count. Body is '{\"data\":{\"count\":<int>}}'." 200 "object{keys=1}" "data"

# 03-models-user  -- GET /models/user
write_request "/models/user" "03-models-user"
write_expected 200 object "03-models-user" data links total_count
write_readme "03-models-user" "/models/user" "Workspace-sorted view. Same shape as '/models'; falls back to all models when workspace has no provider preferences." 200 "object{keys=3}" "data,links,total_count"

# 04-providers  -- GET /providers
write_request "/providers" "04-providers"
write_expected 200 array "04-providers" slug name headquarters datacenters
write_readme "04-providers" "/providers" "All provider records. ~100 entries. No 'pricing'/'uptime' fields." 200 "array(~103)" "slug,name,headquarters,datacenters"

# 05-endpoints-zdr  -- GET /endpoints/zdr
write_request "/endpoints/zdr" "05-endpoints-zdr"
write_expected 200 array "05-endpoints-zdr" provider_name model_id pricing
write_readme "05-endpoints-zdr" "/endpoints/zdr" "ZDR-eligible endpoints only. Flat array, no 'id'/'name' envelope." 200 "array(~784)" "provider_name,model_id,pricing"

# 06-benchmarks  -- GET /benchmarks (no filter)
write_request "/benchmarks" "06-benchmarks"
write_expected 200 object "06-benchmarks" data meta
write_readme "06-benchmarks" "/benchmarks (no filter)" "Default benchmarks listing. 'data[]' carries per-source variants (artificial-analysis, design-arena, openrouter). 'meta' carries query echo." 200 "object{keys=2}" "data,meta"

# 07-classifications  -- GET /classifications/task
write_request "/classifications/task" "07-classifications"
write_expected 200 object "07-classifications" data
write_readme "07-classifications" "/classifications/task" "Task market-share data. 'data.classifications[]' and 'data.macro_categories[]'." 200 "object{keys=1,data}" "data"

# 08-datasets-app  -- GET /datasets/app-rankings
write_request "/datasets/app-rankings" "08-datasets-app"
write_expected 200 object "08-datasets-app" data
write_readme "08-datasets-app" "/datasets/app-rankings" "App token rankings (CC BY 4.0). Smallest of the three datasets (~5.5KB). 'data' is a JSON-as-string (NDJSON-style). Top-level keys=1." 200 "object{keys=1}" "data"

# 09-datasets-daily  -- GET /datasets/rankings-daily
write_request "/datasets/rankings-daily" "09-datasets-daily"
write_expected 200 object "09-datasets-daily" data
write_readme "09-datasets-daily" "/datasets/rankings-daily" "Daily model rankings. Largest of the three datasets (~157KB)." 200 "object{keys=1}" "data"

# 10-datasets-cost  -- GET /datasets/session-cost
write_request "/datasets/session-cost" "10-datasets-cost"
write_expected 200 object "10-datasets-cost" data
write_readme "10-datasets-cost" "/datasets/session-cost" "Per-session cost rankings (~16.5KB)." 200 "object{keys=1}" "data"

# 11-workspaces  -- GET /workspaces (negative testpoint)
write_request "/workspaces" "11-workspaces"
write_expected 401 object "11-workspaces" error
write_readme "11-workspaces" "/workspaces (negative)" "Negative testpoint: CLI key returns 401 with 'error.{message,code}'. Workspace-scoped write/admin endpoints need a different key scope." 401 "object{keys=1,error}" "error"

# 12-model-encoded  -- GET /model/anthropic%2Fclaude-sonnet-4.5  (expected: 404)
write_request "/model/anthropic%2Fclaude-sonnet-4.5" "12-model-encoded"
write_expected 404 object "12-model-encoded" error
write_readme "12-model-encoded" "/model/{a}/{s} with %2F" "Path-encoding probe: '%2F' between author and slug returns 404. The slash must stay **unencoded**." 404 "object{keys=1,error}" "error"

# 13-model-unencoded  -- GET /model/anthropic/claude-sonnet-4.5  (expected: 200)
write_request "/model/anthropic/claude-sonnet-4.5" "13-model-unencoded"
write_expected 200 object "13-model-unencoded" id name created
write_readme "13-model-unencoded" "/model/{a}/{s} unencoded" "Correct form: unencoded slash. Returns the model object directly (not wrapped in 'data[]')." 200 "object" "id,name,created"

# 14-endp-encoded  -- GET /models/anthropic%2Fclaude-sonnet-4.5/endpoints  (expected: 404)
write_request "/models/anthropic%2Fclaude-sonnet-4.5/endpoints" "14-endp-encoded"
write_expected 404 object "14-endp-encoded" error
write_readme "14-endp-encoded" "/models/{a}/{s}/endpoints with %2F" "Path-encoding probe for endpoints listing: '%2F' returns 404." 404 "object{keys=1,error}" "error"

# 15-endp-unencoded  -- GET /models/anthropic/claude-sonnet-4.5/endpoints  (expected: 200)
write_request "/models/anthropic/claude-sonnet-4.5/endpoints" "15-endp-unencoded"
write_expected 200 object "15-endp-unencoded" id endpoints
write_readme "15-endp-unencoded" "/models/{a}/{s}/endpoints unencoded" "Correct form: unencoded slash. Returns '{id, name, endpoints[]}' envelope." 200 "object" "id,endpoints"

# 16-models-by-id-enc  -- GET /models/anthropic%2Fclaude-sonnet-4.5  (plural with %2F; expected: 404)
write_request "/models/anthropic%2Fclaude-sonnet-4.5" "16-models-by-id-enc"
write_expected 404 object "16-models-by-id-enc" error
write_readme "16-models-by-id-enc" "/models/{a}/{s} with %2F (plural)" "Plural '/models/...' does not exist regardless of encoding. Use singular '/model/...'." 404 "object{keys=1,error}" "error"

# 17-models-by-id-unenc  -- GET /models/anthropic/claude-sonnet-4.5  (plural unencoded; expected: 404)
write_request "/models/anthropic/claude-sonnet-4.5" "17-models-by-id-unenc"
write_expected 404 object "17-models-by-id-unenc" error
write_readme "17-models-by-id-unenc" "/models/{a}/{s} unencoded (plural)" "Plural '/models/...' does not exist regardless of encoding. Use singular '/model/...'." 404 "object{keys=1,error}" "error"

# 18-limit-pagination  -- GET /models?limit=10  (expected: 200, body ~13KB)
write_request "/models?limit=10" "18-limit-pagination"
write_expected 200 object "18-limit-pagination" data links total_count
write_readme "18-limit-pagination" "/models?limit=10" "Pagination probe: 'limit=10' returns ~13KB. 'per_page=10/50/500' and 'page=2/5/999' are silently ignored (~690KB identical payload)." 200 "object{keys=3}" "data,links,total_count"

# 19-benchmarks-AA-query  -- GET /benchmarks?source=artificial-analysis
write_request "/benchmarks?source=artificial-analysis" "19-benchmarks-AA-query"
write_expected 200 object "19-benchmarks-AA-query" data meta
write_readme "19-benchmarks-AA-query" "/benchmarks?source=artificial-analysis" "Query-param probe: source filter. 'data' shrinks (~33KB vs ~500KB default). Confirms 'source' query param is honored." 200 "object{keys=2}" "data,meta"

# 20-benchmarks-coding-query  -- GET /benchmarks?category=coding
write_request "/benchmarks?category=coding" "20-benchmarks-coding-query"
write_expected 200 object "20-benchmarks-coding-query" data meta
write_readme "20-benchmarks-coding-query" "/benchmarks?category=coding" "Query-param probe: category filter. 'data' shrinks (~86KB)." 200 "object{keys=2}" "data,meta"

# 21-models-page-query  -- GET /models?page=2  (expected: identical to default; pagination broken)
write_request "/models?page=2" "21-models-page-query"
write_expected 200 object "21-models-page-query" data links total_count
write_readme "21-models-page-query" "/models?page=2" "Negative pagination probe: 'page=2' is silently ignored. Response is the same 690KB payload as no-param. Use 'limit' instead." 200 "object{keys=3}" "data,links,total_count"

echo "Wrote 21 testpoints."
