---
name: openrouter-api
description: >
  Query the OpenRouter REST API to discover models, providers, endpoints,
  benchmarks, datasets, classifications, and inference history. Uses
  $OPENROUTER_API_KILO_CLI for read-only discovery and model picks, and
  $OPENROUTER_MANAGEMENT_KEY for account-admin endpoints — the per-user
  inference log (`/activity`), per-generation request & usage metadata
  (`/generation`, `/generation/content`), API key CRUD (`/keys`), and
  workspace management (`/workspaces`). Use when planning subagents that
  need specific model ids, listing available providers/endpoints for a
  model, looking up benchmark scores, inspecting dataset rankings,
  auditing per-generation cost and latency, reading the daily inference
  log, or managing API keys / workspaces. Key terms include openrouter,
  models, providers, endpoints, benchmarks, datasets, subagent, model
  selection, OPENROUTER_API_KILO_CLI, OPENROUTER_MANAGEMENT_KEY, generation,
  activity, inference log.
---

# OpenRouter API

Read-only discovery and account-admin access to OpenRouter's REST API
(`https://openrouter.ai/api/v1`). Covers 9 groups: **activity**,
**benchmarks**, **classifications**, **datasets**, **endpoints**,
**generation**, **keys**, **models**, **providers**, **workspaces**. Use
it to pick exact model IDs for subagents, inspect provider routing,
audit per-generation cost / latency / token usage, browse the daily
inference log, or manage API keys and workspaces.

Two auth scopes are in play:

- **CLI key** — `$OPENROUTER_API_KILO_CLI`. Read-only discovery, plus
  per-generation lookups for IDs the key itself owns.
- **Management key** — `$OPENROUTER_MANAGEMENT_KEY`. Account-admin
  endpoints (inference log, key / workspace CRUD) and per-generation
  lookups across any ID in the account. Cannot be used for inference
  (`/chat/completions`, etc.) — it is admin-only by design.

## When to load

- A subagent, plan, or prompt needs a specific model id (e.g. "use Sonnet
  4.5", "the cheapest GPT-class model that supports tools").
- Comparing providers, endpoints, or pricing for a known model.
- Looking up benchmark scores (Artificial Analysis, Design Arena,
  OpenRouter tau-bench / GPQA / web-search).
- Listing dataset rankings (apps, daily top models, session cost).
- Auditing a specific `gen-...` request — token counts, cost, latency,
  provider routing, the actual prompt / completion text.
- Reading the account-wide daily inference log (`/activity`) to debug
  spend or attribute a run to a model + provider.
- Listing / creating / deleting API keys (`/keys`) — provisioning
  customers, rotating keys, or auditing the key fleet.
- Reading workspaces (`/workspaces`).

**Don't load** for raw `/chat/completions` or `/messages` inference calls —
that's the OpenAI/Anthropic SDK pattern and lives outside this skill. The
exception is `models/user`, which surfaces the user's provider-sorted view
and is useful for routing decisions even before any inference happens.

## Auth

Two env vars, picked per endpoint by auth scope:

| Env var | Scope | Endpoints |
|---|---|---|
| `$OPENROUTER_API_KILO_CLI` | read-only discovery + own-generation lookup | `/models*`, `/providers`, `/endpoints/zdr`, `/benchmarks`, `/classifications`, `/datasets/*`, `/generation` (own IDs), `/generation/content` (own IDs) |
| `$OPENROUTER_MANAGEMENT_KEY` | account admin — inference log, any-generation lookup, key / workspace CRUD | `/activity`, `/keys/*`, `/workspaces*`, `/generation` (any ID), `/generation/content` (any ID) |

Stop and ask the user to export the relevant var if it's unset; do not
guess or fall back to a different var. The management key cannot make
inference calls — it is rejected at `/chat/completions` by design.

```
Authorization: Bearer $OPENROUTER_API_KILO_CLI          # or
Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY
HTTP-Referer:       <your app url>     # optional but recommended for rankings
X-OpenRouter-Title: <app name>         # optional
```

`HTTP-Referer` and `X-OpenRouter-Title` are global headers defined as
parameters in the spec; send them on every request when you want your
agent's calls to be attributable on the OpenRouter dashboard.

Base URL: **`https://openrouter.ai/api/v1`** (no trailing slash on the
prefix).

## Quick start

```bash
# list models, sort by prompt price, show first 5
curl -sS \
  -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  "https://openrouter.ai/api/v1/models" \
  | jq '.data | sort_by(.pricing.prompt | tonumber) | .[0:5]
        | map({id, name, ctx: .context_length, in: .pricing.prompt, out: .pricing.completion})'
```

## Endpoints

For full per-endpoint contract (status codes, body sizes, field shapes,
worked curl, drift class) see
[references/verified-endpoints.md](references/verified-endpoints.md).
One-line summary:

| Need | Endpoint |
|---|---|
| All models + per-model metadata | `GET /models` |
| Total model count | `GET /models/count` |
| One model by `<author>/<slug>` | `GET /model/{author}/{slug}` |
| Per-provider routing for a model | `GET /models/{author}/{slug}/endpoints` |
| Workspace-sorted view | `GET /models/user` |
| All providers | `GET /providers` |
| ZDR-eligible endpoints | `GET /endpoints/zdr` |
| Benchmark scores (AA / Design Arena / OpenRouter) | `GET /benchmarks` |
| Task market-share classifications | `GET /classifications/task` |
| App / daily / session-cost rankings | `GET /datasets/{app-rankings,rankings-daily,session-cost}` |
| Per-generation request & usage metadata *(own ID — CLI key works)* | `GET /generation?id=<gen-...>` |
| Per-generation prompt + completion text *(own ID — CLI key works)* | `GET /generation/content?id=<gen-...>` |
| Account-wide daily inference log *(needs management key)* | `GET /activity` |
| API keys — list / get / create / update / delete *(needs management key)* | `GET/POST /keys`, `GET/PATCH/DELETE /keys/{hash}` |
| Workspaces — list / get / create / update / delete *(needs management key)* | `GET /workspaces` |

For per-model provider routing or pricing deltas, always fetch both
`GET /model/{author}/{slug}` and `GET /models/{author}/{slug}/endpoints`
— the first gives the canonical/aggregate pricing, the second gives the
per-provider breakdown (`pricing.prompt` per provider, latency
quantiles, supported parameters, etc.).

## Path slashes — the corrected rule

**The slash between `{author}` and `{slug}` must stay UNENCODED.**
Encoding it as `%2F` returns 404. Both `/model/{author}/{slug}` and
`/models/{author}/{slug}/endpoints` follow the same rule.

```
# CORRECT  (200)
GET /model/anthropic/claude-sonnet-4.5
GET /models/anthropic/claude-sonnet-4.5/endpoints

# WRONG    (404)
GET /model/anthropic%2Fclaude-sonnet-4.5
GET /models/anthropic%2Fclaude-sonnet-4.5/endpoints
GET /models/anthropic%2Fclaude-sonnet-4.5          # also 404 — plural doesn't exist
```

Verified by 6 testpoints
([12](../references/testpoints/12-model-encoded/)–
[17](../references/testpoints/17-models-by-id-unenc/)).

## Pagination

Use `?limit=N`. **Not** `?per_page=N`, `?page=N`, or `?offset=N` —
those are silently ignored. `?limit=10` returns ~13 KB; default
(omitted) returns ~690 KB (419 models).

Verified by
[18-limit-pagination](../references/testpoints/18-limit-pagination/) and
[21-models-page-query](../references/testpoints/21-models-page-query/).

## Picking a model id

Model IDs are `<author>/<slug>`, e.g. `anthropic/claude-sonnet-4.5`,
`openai/gpt-5.2`, `meta-llama/llama-3.3-70b-instruct`.

Each model record contains:

```
id, canonical_slug, name, description,
context_length, architecture.{input_modalities, output_modalities, tokenizer},
pricing.{prompt, completion, request, image, web_search, input_cache_read, …},
supported_parameters,         # ["tools", "tool_choice", "response_format",
                              #  "structured_outputs", "reasoning", "include_reasoning",
                              #  "temperature", "top_p", "top_k", "max_tokens", …]
default_parameters,
top_provider.{context_length, max_completion_tokens, is_moderated},
reasoning,                    # length / effort if model reasons by default
per_request_limits,
knowledge_cutoff, expiration_date,
```

For subagent selection the four fields that matter most:

1. `id` — pass verbatim to the subagent's `model:` field.
2. `supported_parameters` — must include `tools` for tool-using agents,
   `response_format`/`structured_outputs` for JSON-mode agents,
   `reasoning`/`include_reasoning` for chain-of-thought agents.
3. `pricing.prompt` / `pricing.completion` — **strings**, not numbers;
   `tonumber` before comparing. Input cache pricing lives in
   `pricing.input_cache_read`.
4. `architecture.input_modalities` — array of
   `text|image|file|audio|video|pdf`; confirm a model can read
   images/PDFs before sending them.

## Resolving providers when routing matters

```bash
curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  "https://openrouter.ai/api/v1/models/anthropic/claude-sonnet-4.5/endpoints" \
  | jq '.endpoints[] | {
      name, provider_name,
      price_in: .pricing.prompt, price_out: .pricing.completion,
      p50: .latency_last_30m.p50,
      context: .context_length
    }'
```

If you only care about the user's preference order (cheapest, lowest
latency, throughput, etc.), prefer `GET /models/user` — it returns
endpoints pre-sorted according to the workspace's
`default_provider_sort` and filters out providers the user has marked
non-private.

## Quote exact ids back

When you tell the user (or a subagent config) which model to use, quote
the `id` value verbatim. Do not paraphrase, downgrade, or substitute a
"similar" model — the user is planning subagent fan-out and needs the
exact slug. If you must suggest an alternative, name both the original
and the alternative so the user can confirm.

## Generation lookups (per-request audit)

Every `/chat/completions` (and `/messages`) response carries a top-level
`id` of the form `gen-...`. Two endpoints resolve that ID into
inspectable detail:

```bash
# Request & usage metadata (model, provider, latency, tokens, cost)
curl -sS -G \
  -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  -d "id=$GENERATION_ID" \
  https://openrouter.ai/api/v1/generation \
  | jq '.data | {id, model, provider_name, tokens_prompt, tokens_completion,
                  latency, generation_time, total_cost, finish_reason,
                  upstream_id, request_id, session_id}'

# Stored prompt and completion text (only if ZDR was NOT enabled)
curl -sS -G \
  -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  -d "id=$GENERATION_ID" \
  https://openrouter.ai/api/v1/generation/content \
  | jq '.data | {id, completion, reasoning}'
```

Both endpoints need `?id=<gen-...>` — omitting it returns a Zod
validation 400, not 404. The CLI key can read IDs that the key itself
authored; the management key can read any ID in the account.

Useful fields in the metadata response (per the 2026-08-30 snapshot):

| Field | Type | Use |
|---|---|---|
| `model` | string | The canonical model slug that served the request (`openai/gpt-5.2`, …). |
| `provider_name` | string\|null | The provider that handled the request (`OpenAI`, `Infermatic`, `deepseek`, …). |
| `tokens_prompt` / `tokens_completion` | int | Native tokenizer counts for billing. |
| `native_tokens_cached` | int | Cached-prompt tokens (drives `cache_discount`). |
| `native_tokens_reasoning` | int | Reasoning tokens, when the model exposes them. |
| `latency` / `generation_time` / `moderation_latency` | number (ms) | Total wall time vs model-inference time vs moderation overhead. |
| `total_cost` / `upstream_inference_cost` | number (USD) | What the user paid vs what OpenRouter paid upstream. |
| `usage` | number (USD) | Effective billed amount (after discounts). |
| `cache_discount` | number\|null | Savings from prompt-cache hits. |
| `provider_responses[]` | array | Per-attempt record for fallbacks (`provider_name`, `latency`, `status`, `model_permaslug`). |
| `upstream_id` | string | The provider's own ID (e.g. `chatcmpl-…`). |
| `request_id` / `session_id` | string | Group generations that share an API request or user session. |
| `streamed` / `cancelled` / `is_byok` | bool | Streaming, cancellation, BYOK flag. |
| `origin` / `http_referer` / `user_agent` | string | Caller-side attribution headers. |
| `workspace_id` / `app_id` / `external_user` | string\|null | Workspace / app / external-user attribution. |

The content response returns the actual stored `prompt`, `completion`,
and `reasoning` strings. ZDR-disabled requests are the only ones with
content; for ZDR-enabled requests the field comes back empty.

## Inference log (`/activity`)

The CLI key returns **403** with `Only management keys can fetch activity
for an account`. The management key returns a daily-rolled-up activity
log, one row per `(date, model, endpoint)`:

```bash
curl -sS -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
  https://openrouter.ai/api/v1/activity \
  | jq '.data | sort_by(-.date) | .[0:5]
        | map({date, model, provider_name, requests, usage, prompt_tokens,
               completion_tokens, reasoning_tokens})'
```

Per-row fields:

| Field | Description |
|---|---|
| `date` | UTC date the row aggregates (e.g. `2026-08-28 00:00:00`). |
| `model_permaslug` / `model` | Canonical slug and the more readable short name. |
| `endpoint_id` / `provider_name` | Which endpoint / provider served the row. |
| `usage` | Billed USD (BYOK excluded). |
| `byok_usage_inference` | BYOK-attributed USD. |
| `requests` / `byok_requests` | Request counts (BYOK vs non-BYOK). |
| `prompt_tokens` / `completion_tokens` / `reasoning_tokens` | Token totals. |

Use it to attribute spend to a model + provider, debug a sudden spike,
or audit what BYOK vs non-BYOK traffic looked like. The endpoint returns
the full history (no pagination parameter is documented — clients that
need windows should filter client-side or use `/analytics` when
available).

## Drift recovery

When the API drifts from what this skill describes — a 404 where the
catalog says 200, a new field that doesn't appear in the snapshot, or a
known-good curl starting to fail — do this:

1. **Run the probe driver**:
   ```bash
   cd .agents/kilo/skills/openrouter-api
   bin/probe-openrouter-api.sh                # run all testpoints (CLI + mgmt)
   bin/probe-openrouter-api.sh 13-model-unencoded  # run one
   ```
   The script reads `$OPENROUTER_API_KILO_CLI` and
   `$OPENROUTER_MANAGEMENT_KEY`, replays every testpoint in
   `references/testpoints/` (CLI-key testpoints and management-key
   testpoints are separate), and prints `PASS`/`FAIL` per endpoint.
   Exits non-zero on any FAIL.
2. **Diff the catalog against the new probe output**: if a testpoint
   started FAILing, check `references/verified-endpoints.md` —
   the drift class field tells you what used to be wrong and is now
   wrong again.
3. **Update both**: edit `.expected.json` to match the new reality
   (rename the field, add the new key, etc.) and amend the catalog
   entry. Don't change the testpoint's status to make it pass — fix
   the catalog to describe what the API now does.
4. **Refresh the snapshot** by saving the new probe body to
   `references/testpoints/snapshot-2026-08-26/` (date-stamped) so the
   next regeneration has a stable source.

The probe script and the snapshot live in-tree; the catalog is the
authoritative prose, the testpoints are the executable contract. They
must agree.

## Edge cases

- **`$OPENROUTER_API_KILO_CLI` unset** — the API returns 401 and the
  spec becomes unusable. Stop and tell the user to export the var; do
  not retry with a different var name.
- **`$OPENROUTER_MANAGEMENT_KEY` unset** — admin endpoints return 401
  (`/keys`, `/workspaces`) or 403 (`/activity`). Stop and tell the user
  to export the var; do not try `/keys` with the CLI key.
- **`/models/user` empty result** — the key has no workspace, or the
  workspace has no provider preferences set. Fall back to
  `GET /models/{author}/{slug}/endpoints` for the same routing data.
- **Pricing strings** — `pricing.*` values are strings, not numbers, so
  JSON `sort_by(.pricing.prompt)` sorts lexicographically
  ("0.00003" < "0.0001" < "0.001" but "0.01" < "0.001"). Always
  `tonumber` before comparing.
- **Models with `expiration_date` in the past** — present but
  non-functional; surface `expiration_date` and recommend a replacement.
- **429 from `/benchmarks` or `/datasets/*`** — spec rate-limits these
  to 30 req/min per key, 500 req/day per account. Slow down or cache.
- **`/endpoints/zdr` is a preview** — the doc note says "preview the
  impact of ZDR"; treat the listing as advisory, not authoritative.
- **`/workspaces` returns 401 with the CLI key**, **`/activity` returns
  403 with the CLI key**, **`/keys` returns 401 with the CLI key** —
  all three require `$OPENROUTER_MANAGEMENT_KEY`. Don't pretend the CLI
  key can list workspaces or read the inference log; tell the user which
  scope is needed.
- **`/generation` without `?id=...`** — returns **400** with a Zod
  validation envelope (`{success:false, error:{name:"ZodError", …}}`),
  not 404. Always pass `?id=<gen-...>`.
- **`/generation` with an unknown ID** — returns **404** with
  `{error:{message:"Generation <id> not found", code:404}}`. The CLI
  key may also get 403 if the ID was authored by a different key in
  the same account — use the management key in that case.
- **`/generation/content` for ZDR-enabled requests** — content is
  intentionally empty (`completion`, `reasoning`, `prompt` all
  null/missing). ZDR is a retention opt-out, not a permission error.
- **Management key used at `/chat/completions`** — rejected by design.
  The key has no inference scope; it is admin-only.

## Anti-patterns

- Hardcoding a model id because you remember it. Always look it up via
  `GET /models` so the user gets a model that actually exists *now*.
- Falling back to `cheapest`/`fastest` based on a single field — read
  `pricing`, `latency_last_30m`, and `context_length` together, and
  confirm `supported_parameters` covers the agent's tool use.
- Encoding the `/` in `<author>/<slug>` as `%2F`. The API rejects it.
- Treating the verified-endpoints catalog as a replacement for the
  `/models` re-fetch before picking a model id — the catalog is for
  *what shape the response has*, not for *which models exist*.
- Sending the raw OpenAPI spec to the user — it's 39k lines. Cite
  fields by name (`pricing.prompt`, `supported_parameters`) and only
  attach the bundled 9-group subset when the user explicitly asks.
- Recreating subagent specs from training data. The model id space
  changes weekly; always re-fetch `/models` before picking a model.
- Calling `/activity`, `/keys`, or `/workspaces` with the CLI key and
  silently switching to the management key on 401/403 — the auth
  scope is a property of the request, not the response. Pick the key
  first, name the env var, and only then probe.
- Hitting `/generation` without `?id=...` and reasoning from the 400
  Zod envelope as if it were a real response. Always pass an id; if
  the id is unknown the response is 404, not 400.
- Reading `provider_responses[]` as a single record — it is an array
  covering fallback attempts. `provider_name` and `latency` at the top
  level of `/generation` are the *successful* attempt, not the
  aggregate.

## References

- [references/verified-endpoints.md](references/verified-endpoints.md) —
  per-endpoint HTTP contract (status, body size, shape, drift class),
  generated from the 2026-08-30 probe snapshot. **Load this when you
  need to confirm an endpoint's response shape before parsing it.**
- [references/testpoints/](references/testpoints/) — replayable
  curl fixtures + `.expected.json` shape markers. One dir per
  endpoint or query-shape probe. Run
  `bin/probe-openrouter-api.sh` to verify the contract still holds.
- [references/openrouter-openapi.yaml](references/openrouter-openapi.yaml) —
  stripped OpenAPI 3.x spec (9 groups; 19 paths, ~15k lines). Read this
  when you need the canonical field names or rate-limit notes for a
  specific endpoint. **Note: this bundled spec may carry the same
  encoding bugs that were fixed in the prose; verify against the live
  API before trusting field claims from it.**
- <https://openrouter.ai/docs/api-reference> — official docs index.
- <https://openrouter.ai/models> — human-browseable model list; useful
  for "what new model just dropped" before hitting `/models`.
