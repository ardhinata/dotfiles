---
last-verified: 2026-08-30
source-of-truth: 27 curl probes saved under references/testpoints/snapshot-2026-08-30/
---

# Verified Endpoints Catalog

Per-endpoint HTTP contract observed against the live OpenRouter API on
2026-08-30. **Every entry is regenerated from
`bin/probe-openrouter-api.sh` against the snapshot;** if the snapshot is
refreshed, re-run the probe and update both this catalog and the
testpoints.

Conventions:
- **Auth** — "CLI key" means `$OPENROUTER_API_KILO_CLI` (the project's
  read-only / own-generation key). "management key" means
  `$OPENROUTER_MANAGEMENT_KEY` (account-admin scope — covers
  `/activity`, `/keys`, `/workspaces`, and any-ID `/generation` lookups).
  Per-testpoint auth lives in `references/testpoints/<name>/.expected.json`
  as the `auth` field; the probe script picks the env var accordingly.
- **Status** — observed HTTP code with the relevant key unless otherwise
  noted. Management-key testpoints flip to 401/403 with the CLI key;
  CLI-key testpoints for `/generation` flip to 403 with the CLI key when
  the ID was authored by a different key.
- **Shape** — top-level JSON type and required top-level keys.
- **Drift class** — what used to be wrong about this endpoint.

---

## GET /models

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: ~690 KB default; ~13 KB with `?limit=10`.
- **Shape**: object `{data: array, links: object, total_count: int}`.
  `data[]` carries 419 model records with fields:
  `id, canonical_slug, name, description, context_length,
  architecture.{input_modalities, output_modalities, tokenizer},
  pricing.{prompt, completion, request, image, web_search,
  input_cache_read, …}, supported_parameters, default_parameters,
  top_provider.{context_length, max_completion_tokens, is_moderated},
  reasoning, per_request_limits, knowledge_cutoff, expiration_date`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/models
  ```
- **Drift class**: pagination (Bug #5). Use `?limit=N`, not `per_page` or
  `page`. See testpoints 18, 21.

→ testpoint: [01-models](../testpoints/01-models/), [18-limit-pagination](../testpoints/18-limit-pagination/), [21-models-page-query](../testpoints/21-models-page-query/)

---

## GET /models/count

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: 22 bytes.
- **Shape**: object `{data: {count: int}}`. As of 2026-08-25: `count=419`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/models/count
  ```
- **Drift class**: none observed.

→ testpoint: [02-models-count](../testpoints/02-models-count/)

---

## GET /models/user

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: ~546 KB.
- **Shape**: object `{data: array, links: object, total_count: int}` —
  same shape as `/models`, but `data[]` is pre-sorted by the workspace's
  `default_provider_sort`. When the key has no workspace or no provider
  preferences set, falls back to all models.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/models/user
  ```
- **Drift class**: none observed.

→ testpoint: [03-models-user](../testpoints/03-models-user/)

---

## GET /providers

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: ~24 KB.
- **Shape**: object `{data: [...]}` — array of 103 provider records under
  `data`. Each: `data[].{slug, name, headquarters, datacenters,
  privacy_policy_url, terms_of_service_url, status_page_url}`.
  **No `pricing`, no `uptime`.**
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/providers
  ```
- **Drift class**: none observed.

→ testpoint: [04-providers](../testpoints/04-providers/)

---

## GET /endpoints/zdr

- **Auth**: CLI key.
- **Status**: 200. POST returns 404 (Bug #6).
- **Body size**: ~703 KB.
- **Shape**: object `{data: [...]}` — array of 784 endpoint records
  (ZDR-eligible only), wrapped under `data`. Each:
  `data[].{provider_name, model_id, model_name, name, context_length,
  pricing, quantization, max_completion_tokens, max_prompt_tokens,
  supported_parameters, status, uptime_last_{30m,5m,1d},
  latency_last_30m.{p50,p75,p90,p99},
  throughput_last_30m.{p50,…}, supports_implicit_caching,
  supports_voice_cloning, tag}`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/endpoints/zdr
  ```
- **Drift class**: GET-only (Bug #6). No `/endpoints` sibling (Bug #4).

→ testpoint: [05-endpoints-zdr](../testpoints/05-endpoints-zdr/)

---

## GET /model/{author}/{slug}

- **Auth**: CLI key.
- **Status**: 200 (unencoded slash) / 404 (`%2F`).
- **Body size**: ~2.6 KB (anthropic/claude-sonnet-4.5 sample).
- **Shape**: object `{data: {id, name, created, description, architecture, …}}` —
  single model wrapped under the top-level `data` key. Use
  `.data.id` (not `.data[0].id`) to read fields.
- **Curl** (correct — unencoded):
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/model/anthropic/claude-sonnet-4.5
  ```
- **Drift class**: encoding (Bug #1). The slash between `{author}` and
  `{slug}` must be **unencoded**. Encoding it as `%2F` returns 404.

→ testpoints: [12-model-encoded](../testpoints/12-model-encoded/), [13-model-unencoded](../testpoints/13-model-unencoded/), [16-models-by-id-enc](../testpoints/16-models-by-id-enc/), [17-models-by-id-unenc](../testpoints/17-models-by-id-unenc/)

---

## GET /models/{author}/{slug}/endpoints

- **Auth**: CLI key.
- **Status**: 200 (unencoded slash) / 404 (`%2F`).
- **Body size**: ~8 KB.
- **Shape**: object `{data: {id, name, description, endpoints: array}}`.
  Read fields under `.data`; the per-endpoint records are at
  `.data.endpoints[]`. Each endpoint: `name, model_id, model_name,
  context_length, pricing, provider_name, tag, quantization,
  max_completion_tokens, max_prompt_tokens, supported_parameters,
  status, uptime_last_{30m, 5m, 1d}, latency_last_30m.{p50,…},
  throughput_last_30m.{p50,…}, supports_implicit_caching,
  supports_voice_cloning`.
- **Curl** (correct — unencoded):
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/models/anthropic/claude-sonnet-4.5/endpoints
  ```
- **Drift class**: encoding (Bug #2). Same direction as Bug #1.

→ testpoints: [14-endp-encoded](../testpoints/14-endp-encoded/), [15-endp-unencoded](../testpoints/15-endp-unencoded/)

---

## GET /benchmarks

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: ~502 KB default; ~34 KB with `?source=artificial-analysis`;
  ~87 KB with `?category=coding`.
- **Shape**: object `{data: array, meta: object}`. `data[]` carries
  ~1439 benchmark items with **per-source shape variants**:
  - `artificial-analysis` items: `model_permaslug, intelligence_index,
    coding_index, agentic_index, pricing, source, display_name`.
  - `design-arena` items: different field set (display + ranking).
  - `openrouter` items: `model_permaslug, benchmark_type, task_type,
    search_engine, search_surface, score, display_name`.
- **Query params (confirmed honored)**: `source`, `task_type`,
  `benchmark_type`, `search_engine`, `search_surface`, `arena`,
  `category`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/benchmarks
  ```
- **Drift class**: none on path; field-shape variants noted (see Deferred
  Notes in the plan).

→ testpoints: [06-benchmarks](../testpoints/06-benchmarks/), [19-benchmarks-AA-query](../testpoints/19-benchmarks-AA-query/), [20-benchmarks-coding-query](../testpoints/20-benchmarks-coding-query/)

---

## GET /classifications/task

- **Auth**: CLI key.
- **Status**: 200.
- **Body size**: ~31 KB.
- **Shape**: object `{data: {classifications: array, macro_categories: array, window_days: int, as_of: string}}`. `classifications[]` carries
  `tag, display_name, macro_category, usage_share, token_share,
  category_usage_share, category_token_share, models[]` where
  `models[].{id, tag_usage_share, tag_token_share}`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/classifications/task
  ```
- **Drift class**: none observed.

→ testpoint: [07-classifications](../testpoints/07-classifications/)

---

## GET /datasets/{app-rankings, rankings-daily, session-cost}

- **Auth**: CLI key.
- **Status**: 200 for all three.
- **Body sizes**: `app-rankings` ~5.6 KB (smallest), `session-cost`
  ~16.5 KB, `rankings-daily` ~157 KB (largest). All CC BY 4.0 licensed.
- **Shape**: object `{data: <NDJSON-as-string>}`. The `data` field is a
  JSON-encoded string holding an array of records; parse twice to get
  rows.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/datasets/app-rankings | jq '.data | fromjson | .[0:3]'
  ```
- **Drift class**: none observed.

→ testpoints: [08-datasets-app](../testpoints/08-datasets-app/), [09-datasets-daily](../testpoints/09-datasets-daily/), [10-datasets-cost](../testpoints/10-datasets-cost/)

---

## GET /workspaces  *(negative testpoint)*

- **Auth**: **management key** (not the CLI key).  *(negative
  testpoint uses the CLI key on purpose to confirm the 401.)*
- **Status with CLI key**: **401**
  `{error: {message: "Invalid management key", code: 401}}`.
- **Status with management key**: **200**, body `{data:[…], total_count:N}`.
- **Shape (401)**: object `{error: {message, code}}`.
- **Shape (200)**: object `{data: array, total_count: int}`. Each
  workspace record carries
  `{id, name, slug, description, default_text_model, default_image_model,
  default_provider_sort, is_observability_io_logging_enabled,
  is_observability_broadcast_enabled, is_data_discount_logging_enabled,
  include_byok_in_budgets, io_logging_sampling_rate,
  io_logging_api_key_ids, created_at, updated_at, created_by}`.
- **Curl (negative)**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    https://openrouter.ai/api/v1/workspaces
  ```
- **Curl (positive)**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
    https://openrouter.ai/api/v1/workspaces
  ```
- **Drift class**: auth scope (Bug #7). `/workspaces/*` requires a key
  with management scope; the read-only CLI key returns 401. This is
  expected, not a failure — call this out in user-facing answers rather
  than implying the CLI key can list workspaces.

→ testpoints: [11-workspaces](../testpoints/11-workspaces/),
[27-workspaces-mgmt](../testpoints/27-workspaces-mgmt/)

---

## GET /generation?id=<gen-...>

- **Auth**: CLI key (for IDs the key itself authored) **or** management
  key (for any ID in the account). Same endpoint, different key
  scope.
- **Status with id**: **200**.
- **Status without id**: **400** with Zod envelope
  `{success:false, error:{name:"ZodError", message: …}}`. **Not 404.**
- **Status with unknown id**: **404** with
  `{error:{message:"Generation <id> not found", code:404}}`.
- **Body size (200)**: ~1.5–2.5 KB per record.
- **Shape**: object `{data: object}` with the generation record under
  `.data`. Required fields (full set per the 2026-08-30 spec):
  `id, upstream_id, total_cost, cache_discount, upstream_inference_cost,
  created_at, model, app_id, streamed, cancelled, provider_name,
  latency, moderation_latency, generation_time, finish_reason,
  service_tier, tokens_prompt, tokens_completion,
  native_tokens_prompt, native_tokens_completion,
  native_tokens_completion_images, native_tokens_reasoning,
  native_tokens_cached, num_media_prompt, num_input_audio_prompt,
  num_media_completion, num_search_results, num_fetches,
  web_search_engine, origin, usage, is_byok, native_finish_reason,
  external_user, api_type, preset_id, router, provider_responses,
  user_agent, http_referer, data_region, workspace_id`.
  `provider_responses[]` is an **array** of `{provider_name, latency,
  status, model_permaslug, endpoint_id, id, is_byok, routed_service_tier}`
  covering fallback attempts.
- **Curl**:
  ```bash
  curl -sS -G \
    -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    -d "id=$GENERATION_ID" \
    https://openrouter.ai/api/v1/generation
  ```
- **Drift class**: required-param (Zod 400 without `?id=`). Don't
  treat the 400 as a normal response — pass `?id=<gen-...>`.

→ testpoints: [24-generation-no-id](../testpoints/24-generation-no-id/),
[25-generation-unknown](../testpoints/25-generation-unknown/)

---

## GET /generation/content?id=<gen-...>

- **Auth**: CLI key (for IDs the key itself authored) **or** management
  key (for any ID in the account).
- **Status with id**: **200** (or 404 with unknown id).
- **Status without id**: **400** Zod envelope, same as `/generation`.
- **Shape**: object `{data: {id, prompt?, completion?, reasoning?}}`.
  Content fields are intentionally **null/missing** for ZDR-enabled
  requests — ZDR is a retention opt-out, not a permission error.
- **Curl**:
  ```bash
  curl -sS -G \
    -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
    -d "id=$GENERATION_ID" \
    https://openrouter.ai/api/v1/generation/content
  ```
- **Drift class**: same required-param caveat as `/generation`.

→ testpoint: [26-generation-content-no-id](../testpoints/26-generation-content-no-id/)

---

## GET /activity  *(management-only)*

- **Auth**: **management key** (the CLI key returns **403** with
  `Only management keys can fetch activity for an account`).
- **Status with management key**: **200**.
- **Body size**: a few KB per day of history (response grows linearly
  with activity-window depth).
- **Shape**: object `{data: array}` — daily-rolled rows. Each row:
  `{date (YYYY-MM-DD HH:MM:SS), model_permaslug, model,
  endpoint_id, provider_name, usage, byok_usage_inference, requests,
  byok_requests, prompt_tokens, completion_tokens, reasoning_tokens}`.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
    https://openrouter.ai/api/v1/activity
  ```
- **Drift class**: auth scope. The CLI key is 403 (not 401) here — the
  error message literally names "management keys" so the agent can
  pivot without guessing.

→ testpoint: [23-activity](../testpoints/23-activity/)

---

## GET /keys  *(management-only)*

- **Auth**: **management key** (the CLI key returns **401**
  `Invalid API key`).
- **Status with management key**: **200**.
- **Body size**: scales with the account's key fleet; the
  2026-08-30 snapshot returns ~10 B (zero keys) and grows to ~2 KB
  for a single key.
- **Shape**: object `{data: array}` of API key records. Each key
  record carries `name, label, hash, disabled, limit, limit_reset,
  include_byok_in_budgets, usage, byok_usage, expires_at, created_at,
  updated_at, created_by`. The plaintext key is **never** returned by
  this endpoint — only by `POST /keys` at creation time.
- **Curl**:
  ```bash
  curl -sS -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
    https://openrouter.ai/api/v1/keys
  ```
- **Drift class**: auth scope. Same caveat as `/workspaces`. The
  management key cannot be used for inference — it is admin-only.

→ testpoint: [22-keys](../testpoints/22-keys/)

---

## What this catalog does NOT cover

- `/chat/completions`, `/messages`, `/images`, `/videos`,
  `/audio/speech`, `/audio/transcriptions`, `/embeddings`, and other
  inference endpoints — out of scope; the OpenAI/Anthropic SDK patterns
  apply.
- **Write** admin endpoints (`POST /keys`, `PATCH /keys/{hash}`,
  `POST /workspaces`, `POST /workspaces/{id}/members`,
  `POST /generation/{id}/feedback`, etc.) — same auth-scope caveat as
  the GETs above. The probe script only covers GETs because every
  write needs a fixture ID and a deliberate choice.
- `/analytics` — returned **404** on 2026-08-30 with both the CLI key
  and the management key. The endpoint is documented but not currently
  exposed under that path; some clients see a beta `/analytics` shape
  elsewhere on the dashboard. Don't claim `/analytics` works on the
  public REST API until it returns 200.
- `references/openrouter-openapi.yaml` (bundled 15k-line spec) — may
  carry the same encoding bugs as the prose skill did. Verification is
  a separate follow-up.
