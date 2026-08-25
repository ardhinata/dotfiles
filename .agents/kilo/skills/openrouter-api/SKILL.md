---
name: openrouter-api
description: >
  Query the OpenRouter REST API to discover models, providers, endpoints,
  benchmarks, datasets, classifications, and workspaces. Authenticates
  with $OPENROUTER_API_KILO_CLI. Use when planning subagents that need
  specific model ids, listing available providers/endpoints for a model,
  looking up benchmark scores, inspecting dataset rankings, or
  reading/updating workspaces. Key terms include openrouter, models,
  providers, endpoints, benchmarks, datasets, subagent, model selection,
  and OPENROUTER_API_KILO_CLI.
---

# OpenRouter API

Read-only and workspace-management access to OpenRouter's REST API
(`https://openrouter.ai/api/v1`). Covers 7 groups: **benchmarks**,
**classifications**, **datasets**, **endpoints**, **models**,
**providers**, **workspaces**. Use it to pick exact model IDs for
subagents, inspect provider routing, or manage workspaces.

## When to load

- A subagent, plan, or prompt needs a specific model id (e.g. "use Sonnet
  4.5", "the cheapest GPT-class model that supports tools").
- Comparing providers, endpoints, or pricing for a known model.
- Looking up benchmark scores (Artificial Analysis, Design Arena,
  OpenRouter tau-bench / GPQA / web-search).
- Listing dataset rankings (apps, daily top models, session cost).
- Listing / reading / writing workspaces (read or the user asks).

**Don't load** for raw `/chat/completions` or `/messages` inference calls —
that's the OpenAI/Anthropic SDK pattern and lives outside this skill. The
exception is `models/user`, which surfaces the user's provider-sorted view
and is useful for routing decisions even before any inference happens.

## Auth

Env var: **`$OPENROUTER_API_KILO_CLI`** — read-only or workspace-scoped
OpenRouter API key. If unset, stop and ask the user to export it; do not
guess or fall back to a different var.

```
Authorization: Bearer $OPENROUTER_API_KILO_CLI
HTTP-Referer:    <your app url>     # optional but recommended for rankings
X-OpenRouter-Title: <app name>      # optional
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
| Workspaces *(needs management key)* | `GET /workspaces` |

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

## Drift recovery

When the API drifts from what this skill describes — a 404 where the
catalog says 200, a new field that doesn't appear in the snapshot, or a
known-good curl starting to fail — do this:

1. **Run the probe driver**:
   ```bash
   cd .agents/kilo/skills/openrouter-api
   bin/probe-openrouter-api.sh                # run all testpoints
   bin/probe-openrouter-api.sh 13-model-unencoded  # run one
   ```
   The script reads `$OPENROUTER_API_KILO_CLI`, replays every
   testpoint in `references/testpoints/`, and prints `PASS`/`FAIL`
   per endpoint. Exits non-zero on any FAIL.
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
- **`/workspaces` returns 401 with the CLI key** — workspace-scoped
  write/admin endpoints require a key with management scope, not the
  read-only CLI key. Don't pretend the CLI key can list workspaces; tell
  the user which scope is needed.

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
  attach the bundled 7-group subset when the user explicitly asks.
- Recreating subagent specs from training data. The model id space
  changes weekly; always re-fetch `/models` before picking a model.

## References

- [references/verified-endpoints.md](references/verified-endpoints.md) —
  per-endpoint HTTP contract (status, body size, shape, drift class),
  generated from the 2026-08-25 probe snapshot. **Load this when you
  need to confirm an endpoint's response shape before parsing it.**
- [references/testpoints/](references/testpoints/) — replayable
  curl fixtures + `.expected.json` shape markers. One dir per
  endpoint or query-shape probe. Run
  `bin/probe-openrouter-api.sh` to verify the contract still holds.
- [references/openrouter-openapi.yaml](references/openrouter-openapi.yaml) —
  stripped OpenAPI 3.x spec (7 groups; 19 paths, ~15k lines). Read this
  when you need the canonical field names or rate-limit notes for a
  specific endpoint. **Note: this bundled spec may carry the same
  encoding bugs that were fixed in the prose; verify against the live
  API before trusting field claims from it.**
- <https://openrouter.ai/docs/api-reference> — official docs index.
- <https://openrouter.ai/models> — human-browseable model list; useful
  for "what new model just dropped" before hitting `/models`.
