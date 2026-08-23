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
(`https://openrouter.ai/api/v1`). Loads a stripped OpenAPI spec covering 7
groups: **benchmarks**, **classifications**, **datasets**, **endpoints**,
**models**, **providers**, **workspaces**. Use it to pick exact model IDs
for subagents, inspect provider routing, or manage workspaces.

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

## Workflow

### 1. Identify what you need

| Need | Endpoint |
|---|---|
| All available models + per-model metadata | `GET /models` |
| One model by `<author>/<slug>` | `GET /model/{author}/{slug}` |
| Total model count | `GET /models/count` |
| User's provider-sorted view (privacy / sort prefs) | `GET /models/user` |
| Providers that serve a model | `GET /models/{author}/{slug}/endpoints` |
| ZDR-eligible endpoints preview | `GET /endpoints/zdr` |
| Benchmark scores (AA / Design Arena / OpenRouter) | `GET /benchmarks` |
| Task market-share classifications | `GET /classifications/task` |
| App token rankings, daily model rankings, session cost | `GET /datasets/{app-rankings,rankings-daily,session-cost}` |
| All providers | `GET /providers` |
| Workspaces CRUD + budgets + members | `/workspaces/*` |

For per-model provider routing or pricing deltas, always fetch both
`GET /models/{author}/{slug}` and `GET /models/{author}/{slug}/endpoints`
— the first gives the canonical/aggregate pricing, the second gives the
per-provider breakdown (`pricing.prompt` per provider, latency
quantiles, supported parameters, etc.).

### 2. Pick the model id

Model IDs are `<author>/<slug>`, e.g. `anthropic/claude-sonnet-4.5`,
`openai/gpt-5.2`, `meta-llama/llama-3.3-70b-instruct`. The slash is
mandatory and must be URL-encoded as `%2F` in path params
(`/model/{author}/{slug}` → `/model/anthropic%2Fclaude-sonnet-4.5`).

Each model record contains:

```
id, canonical_slug, name, description,
context_length, architecture.{input_modalities,output_modalities,tokenizer},
pricing.{prompt,completion,request,image,web_search,input_cache_read,...},
supported_parameters,         # ["tools","tool_choice","response_format",
                             #  "structured_outputs","reasoning","include_reasoning",
                             #  "temperature","top_p","top_k","max_tokens",...]
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
3. `pricing.prompt` / `pricing.completion` — strings; `tonumber` before
   comparing. Input cache pricing lives in `pricing.input_cache_read`.
4. `architecture.input_modalities` — array of `text|image|file|audio|video|pdf`;
   confirm a model can read images/PDFs before sending them.

### 3. Resolve providers when routing matters

```bash
curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  "https://openrouter.ai/api/v1/models/anthropic%2Fclaude-sonnet-4.5/endpoints" \
  | jq '.data.endpoints[] | {
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

### 4. Quote exact ids back

When you tell the user (or a subagent config) which model to use, quote
the `id` value verbatim. Do not paraphrase, downgrade, or substitute a
"similar" model — the user is planning subagent fan-out and needs the
exact slug. If you must suggest an alternative, name both the original
and the alternative so the user can confirm.

### 5. Refresh the bundled spec (when needed)

The bundled `references/openrouter-openapi.yaml` is generated from
`https://openrouter.ai/openapi.yaml` and pinned to whatever was current
at skill-install time. If you hit a 404, an unknown operationId, or a
field that isn't in the spec, refresh it:

```bash
redocly bundle --config /dev/stdin -o references/openrouter-openapi.yaml \
  /tmp/openrouter-openapi.yaml 2>/dev/null <<'YAML'
apis:
  openrouter@v1:
    root: /tmp/openrouter-openapi.yaml
    decorators:
      filter-in:
        property: tags
        value: [Benchmarks, Classifications, Datasets, Endpoints,
                Models, Providers, Workspaces]
YAML
```

(After downloading `/tmp/openrouter-openapi.yaml` from
`https://openrouter.ai/openapi.yaml` and running
`redocly bundle --remove-unused-components --force` to drop unused
schemas.) For local experimentation the equivalent fully-pipelined form
is checked into `references/openrouter-openapi.yaml`.

## Edge cases

- **`$OPENROUTER_API_KILO_CLI` unset** — the API returns 401 and the
  spec becomes unusable. Stop and tell the user to export the var; do
  not retry with a different var name.
- **Path slashes** — `{author}/{slug}` must be URL-encoded (`%2F`) in
  the path. Forgetting this hits `/model/{author}/{slug}` literally and
  OpenRouter returns 404.
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

## Anti-patterns

- Hardcoding a model id because you remember it. Always look it up via
  `GET /models` so the user gets a model that actually exists *now*.
- Falling back to `cheapest`/`fastest` based on a single field — read
  `pricing`, `latency_last_30m`, and `context_length` together, and
  confirm `supported_parameters` covers the agent's tool use.
- Sending the raw OpenAPI spec to the user — it's 39k lines. Cite
  fields by name (`pricing.prompt`, `supported_parameters`) and only
  attach the bundled 7-group subset when the user explicitly asks.
- Recreating subagent specs from training data. The model id space
  changes weekly; always re-fetch `/models` before picking a model.

## References

- [references/openrouter-openapi.yaml](references/openrouter-openapi.yaml) —
  stripped OpenAPI 3.x spec (7 groups; 19 paths, ~15k lines). Read this
  when you need the canonical field names, response shapes, or rate-limit
  notes for a specific endpoint.
- <https://openrouter.ai/docs/api-reference> — official docs index.
  Cross-check field names against the bundled spec when they disagree.
- <https://openrouter.ai/models> — human-browseable model list; useful
  for "what new model just dropped" before hitting `/models`.
</content>
</invoke>