# Model Picks (snapshot 2026-09-10)

> **Drift-prone metadata only.** The cohort table (role → model →
> variant → sampling → steps/maxTokens) lives in
> `dot_config/kilo/exact_agent/README.md` §"The six subagents". This
> file keeps the *why*, *routes*, *cost*, and *re-verification
> cadence* — the parts that drift weekly and don't fit in the
> README's reference table.
>
> OpenRouter adds new routes weekly; the `:batch` filter must be
> re-applied before any new pick. Re-verify against
> `dot_config/kilo/exact_agent/README.md` "The six subagents" first.
>
> **2026-09-10 changes:**
> - Swapped `haru` from `xiaomi/mimo-v2.5-pro` to
>   `deepseek/deepseek-v4-flash-0731` at `variant: low` (Non-think).
>   Rationale: haru's adversarial-stance prompt is the primary
>   lever; reasoning-channel churn on MiMo produced unstable
>   structured output. Non-think V4-Flash exits directly into YAML.
>   Cohort collapses from 3 families to 2 (Z.ai GLM + DeepSeek V4).
>   `aki` and `haru` now share a model at opposite effort tiers —
>   deliberate contrast, not redundancy.
> - **Cohort cap harmonised 2026-09-10T08:07Z (user):** all four
>   research subagents set to `steps: 30, maxTokens: 6144`. Prior
>   values: haru/aki 50/4096, natsu 50/8192, fuyu 50/6144. The cap
>   is the binding worst-case — paired with the `task_id`
>   continuation channel (≤ 2 continuations per spawn; the 3rd
>   escalates to user) and the `verifier: refuse-on-partial` default
>   in shiki/reki. Plan:
>   `.tmp/docs/plans/2026-09-10-subagent-30step-6k-continuation.md`.
>   Empirical pass at 30 × 6144: haru/natsu/fuyu completed cleanly
>   in one batch (no truncation); aki ran ~22 min on a `variant:
>   high` probe and hit the steps cap before writing the file —
>   signal that 6144 is near the floor for aki at `variant: high`,
>   and that the batched-output / continuation protocol is load-bearing
>   for that role (no probe truncation observed, only a steps-cap
>   overrun that continuation would resolve).
> - **Continuation protocol switched to true `task_id` continuation
>   2026-09-10T09:16Z (user):** the kilocode runtime preserves the
>   subagent's full message history and tool outputs when the parent
>   re-spawns with `task_id=<prior_sessionID>`
>   (`packages/opencode/src/tool/task.ts:55-60, 166-173, 213-220`,
>   guard at `packages/opencode/src/kilocode/task-resume.ts:1`). The
>   prior simulated-continuation design (re-spawn + reconstruct from
>   a `past_steps:` array) is dropped — it was duplicate signal
>   (the subagent already sees its own past tool calls in the
>   resumed session). Envelope drops the `past_steps:` field; the
>   parent prompt becomes a single `task_id=<id>` re-spawn.

## Route pin block (verified healthy as of 2026-09-09)

| Model | Verified-healthy routes | Dropped routes | Reason for drop |
|---|---|---|---|
| `z-ai/glm-5.3-flash` (natsu, fuyu, reki) | `parasail/fp8`, `deepinfra/fp8`, `novita/fp8` | — | — |
| `deepseek/deepseek-v4-flash-0731` (haru, aki, shiki) | `relace/fp4`, `streamlake/fp8` | `sail-research/fp4`, `akashml/fp8` | 429 / 503 (route probe 2026-09-09) |

Pins live in `dot_config/kilo/kilo.jsonc` (chezmoi source) →
`~/.config/kilo/kilo.jsonc` (deployed). Per-model `options.provider.only`
lists the verified-healthy routes; routing mode is hard-restricted
(`only`). Routing-strategy rationale in
`.agents/docs/cache/kilo-subagents/2026-09-01-shiki-route-probe.md`.

## Why these assignments (2026-09-09)

- **`haru` → deepseek/deepseek-v4-flash-0731 (`variant: low`)** —
  Non-think tier; reasoning channel disabled, so the adversarial
  stance in the prompt produces structured YAML directly. Pairs
  with `aki` on the same model at `variant: high` — the deliberate
  effort contrast (attack without deep reflection vs audit with
  full reflection) is the design intent. Cost drops vs the prior
  MiMo pick on cache reads.
- **`natsu` → z-ai/glm-5.3-flash** — AA Intelligence 57.5 (highest of
  the 3-model cohort), supports `temperature`/`top_p`/`reasoning_effort`
  (forwarded on the routes above). 1.31M context, 131K max completion,
  $0.075/$0.25 per M tokens top-provider. Synthesizer role depends on
  long-context reasoning; glm-5.3-flash was trained for exactly that
  workload. `low` effort is cheap; the synthesis lever is the
  prompt-conditioned role, not deep reasoning.
- **`aki` → deepseek/deepseek-v4-flash-0731** — only cohort model with
  enumerated depth tiers (Non-think / High / Max). The `variant: high`
  mapping to Think Max is the assumption-auditor's primary lever for
  surfacing hidden assumptions. AA 51.8. `high` effort for deep
  assumption-hunting.
- **`fuyu` → z-ai/glm-5.3-flash** — same model as natsu, but `T=1.0`
  to range over the rubric edges. Avoids the qwen3.7-flash doom-loop
  risk that the v2 aki assumption audit flagged (qwen defaults to
  >60% reasoning tokens regardless of effort).
- **`shiki` → deepseek/deepseek-v4-flash-0731** — **previously
  `minimax/minimax-m3`** (2026-09-01 → 2026-09-09) and `minimax-m3` was
  itself the 2026-08-17 pick before that. The 2026-09-01 swap was
  based on "M3 silently drops `reasoning_effort`" which the 2026-09-09
  revisit proved wrong. **Corrected rationale:** M3 has only a binary
  thinking toggle (no depth tier), while V4-Flash-0731 has 3 real
  tiers (Non-think / High / Max). Shiki's two-pass verification on
  `load_bearing: true` claims benefits from a real Max tier.
  Token-plan-on-M3 advantage does not offset the loss of the depth
  lever. `temperature: 0.4` is non-recommended for M3 but is within
  the accepted range and works as a "deterministic verifier" choice
  for V4-Flash too.
- **`reki` → z-ai/glm-5.3-flash** — second verifier, family-diverse
  from shiki. T=1.0 (creative) vs shiki's T=0.4 (deterministic) —
  divergent phrasing on agreeing verdicts surfaces latent
  uncertainty. Highest AA intelligence in the cohort (57.5). Shares
  route pin with natsu/fuyu. New (2026-09-09).

## Cost ceiling (N=4 + 2-verifier pair)

| Per-call | Single-verifier | 2-verifier pair |
|---|---|---|
| Research tier (N=4): ~$0.018 | research + shiki = ~$0.028 | research + shiki + reki = ~$0.033 |
| Per-month (40 fan-outs): ~$1.00–1.50 | — | +$0.20–0.60 |
| Wall-clock (verifier step): ~50–60s | — | unchanged (parallel) |

Aki and shiki share `deepseek-v4-flash-0731` at `variant: high`
($0.065/M prompt + ~$0.016/M cache_read). Reki is on glm-5.3-flash at
`variant: high`. Worst-case 4-call research + 1 shiki ≈ $0.30/M
aggregate. Well within the per-question budget.

## Re-verification cadence

- OpenRouter `:batch` routes: re-filter weekly before any new pick.
- `variant: high` exposure: re-verify against the live model at
  session start — the OpenRouter `supported_parameters` matrix drifts.
- Benchmark snapshot: re-pull
  `GET https://openrouter.ai/api/v1/benchmarks` before any model
  swap. Only Artificial Analysis has substantive data for the current
  3 survivors.
- Reasoning-effort semantics: re-verify on the upstream API docs
  (MiniMax, DeepSeek, Z.ai) every 3-6 months — vendors change the
  depth semantics without OpenRouter changing passthrough. The
  2026-09-09 M3 revisit was triggered by exactly this kind of drift.
