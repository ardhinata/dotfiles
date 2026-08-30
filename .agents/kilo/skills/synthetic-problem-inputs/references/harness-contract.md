# Harness Contract (Dispatch + Lookup)

The exact shape the benchmark harness uses to spawn one role-call and
record the post-call metadata. The skill does not own a script; this
reference documents the contract so a future benchmark can re-implement
or audit it.

## Per-call dispatch

The harness emits, for role `r` and call `i`:

```
[QUESTION TEMPLATE FILL-IN from references/role-templates.md]
Output must follow the <r> YAML envelope (<envelope reminder>).
```

and dispatches via:

```
task(subagent_type: r, description: "fleet speed-benchmark <r> <i>", prompt: <above>)
```

The subagent inherits the role body, permissions, and model via
kilo's `subagent_type` dispatch. No model override is passed at
dispatch time — the model pick lives in the role's frontmatter and
the benchmark measures the production-state model.

## Token cap

`maxTokens: 5000` is applied via the role's frontmatter before the
benchmark run. The benchmark plan's anti-pattern forbids running
without a cap (a runaway call can blow the latency sample). On
revocations: the cap reverts to the production state after the
benchmark; the cap-plan application is a separate workflow.

`steps:` floor in the frontmatter is not required for the speed
benchmark — the role body's "at most 3 findings" envelope is the
real ceiling, and the benchmark's 5 calls × 4 roles = 20 spawns
fits comfortably in the default `steps: 25` shared default from
the cap plan.

## Captured at the call boundary

- `start_ts` (wall-clock, ISO 8601) at the moment the `task` tool
  is invoked.
- `end_ts` at the moment the subagent's final assistant message
  arrives.
- The `gen-...` id from the subagent's last response. Kilo surfaces
  this in the response metadata. If the id is missing (shouldn't
  happen with `openrouter/*` model ids), the row's `gen_id` is
  `null` and `/generation` lookup is skipped.
- Any error string (timeout, refusal, tool failure).

## Post-call `/generation` lookup

After each call, with the management key:

```
curl -sS -G \
  -H "Authorization: Bearer $OPENROUTER_MANAGEMENT_KEY" \
  -d "id=$GEN_ID" \
  https://openrouter.ai/api/v1/generation
```

Extract into the CSV row:

- `latency_ms` ← `/generation.latency` (model inference time)
- `generation_time_ms` ← `/generation.generation_time` (server-side
  total, includes moderation)
- `prompt_tokens` ← `/generation.tokens_prompt`
- `completion_tokens` ← `/generation.tokens_completion`
- `reasoning_tokens` ← `/generation.native_tokens_reasoning` (0
  for non-reasoning models)
- `cost_usd` ← `/generation.total_cost`
- `provider_name` ← `/generation.provider_name`
- `finish_reason` ← `/generation.finish_reason`
- `wall_clock_ms` ← `end_ts - start_ts` measured at this layer

## CSV shape

Header: `role,model,provider,call_index,gen_id,latency_ms,generation_time_ms,prompt_tokens,completion_tokens,reasoning_tokens,cost_usd,finish_reason,wall_clock_ms`

One row per probe (4 roles × 5 calls = 20 rows).

## Failure modes

- `/generation` 403 → `latency_ms` and friends are `null`, the
  `provider` column records `error:403`. The benchmark's pre-flight
  step requires a sanity-checked management key; if 403 fires here,
  surface to the user (per benchmark plan pre-flight step 5).
- `finish_reason: length` → row is still valid; flag the call as
  "hit cap" in the per-call JSON, do not retry. If 3+ of 5 calls
  in a role hit length, the cap is too low — surface to user
  before continuing.
- Subagent produces a refusal / `bash: ask` block that never
  resolves → `wall_clock_ms` is set, `gen_id` is null, the row
  is excluded from p50/p95 but counted in `finish_reason_breakdown`
  as `error: refused`.

## Where the artifacts land

- Per-call raw response JSON: `.tmp/docs/subagent-runs/YYYYMMDD_HHMMSS-<role>-speed-<i>.json` (gitignored, per-worktree).
- Aggregated CSV: `.agents/docs/cache/openrouter/YYYY-MM-DD-fleet-speed-benchmark.csv`.
- Aggregated Markdown report: `.agents/docs/cache/openrouter/YYYY-MM-DD-fleet-speed-benchmark.md`.
- Inputs plan (this run's actual fill-in): `.tmp/docs/plans/YYYY-MM-DD-fleet-speed-benchmark-inputs.md`.
