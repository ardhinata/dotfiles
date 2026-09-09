# Model Picks (snapshot 2026-09-09)

> **Drift-prone metadata only.** The cohort table (role → model →
> variant → sampling) lives in `dot_config/kilo/exact_agent/README.md`
> §"The six subagents". This file keeps the *why*, *routes*, *cost*,
> and *re-verification cadence* — the parts that drift weekly and
> don't fit in the README's reference table.
>
> OpenRouter adds new routes weekly; the `:batch` filter must be
> re-applied before any new pick. Re-verify against
> `dot_config/kilo/exact_agent/README.md` "The six subagents" first.
>
> **2026-09-09 changes:**
> - Added `reki` (second verifier, `z-ai/glm-5.3-flash`).
> - Re-verified shiki's `deepseek/deepseek-v4-flash-0731` pick
>   (`.agents/docs/cache/kilo-subagents/2026-09-09-shiki-m3-reasoning-effort-revisit.md`):
>   the 2026-09-01 "M3 silently drops reasoning_effort" claim was
>   based on a single-sample 1-token probe and is withdrawn. M3
>   honours the field as a binary thinking toggle; the swap to
>   V4-Flash-0731 stays because V4-Flash has 3 real depth tiers
>   (Non-think / High / Max) and M3 does not.
> - R1-R7 eligibility filter is now **soft** — the prior "4 distinct
>   families" hard invariant is advisory, not binding.

## Route pin block (verified healthy as of 2026-09-09)

| Model | Verified-healthy routes | Dropped routes | Reason for drop |
|---|---|---|---|
| `xiaomi/mimo-v2.5-pro` (haru) | (re-verify at next cohort swap) | — | — |
| `z-ai/glm-5.3-flash` (natsu, fuyu, reki) | `parasail/fp8`, `deepinfra/fp8`, `novita/fp8` | — | — |
| `deepseek/deepseek-v4-flash-0731` (aki, shiki) | `relace/fp4`, `streamlake/fp8` | `sail-research/fp4`, `akashml/fp8` | 429 / 503 (route probe 2026-09-09) |

Pins live in `dot_config/kilo/kilo.jsonc` (chezmoi source) →
`~/.config/kilo/kilo.jsonc` (deployed). Per-model `options.provider.only`
lists the verified-healthy routes; routing mode is hard-restricted
(`only`). Routing-strategy rationale in
`.agents/docs/cache/kilo-subagents/2026-09-01-shiki-route-probe.md`.

## Why these assignments (2026-09-09)

- **`haru` → xiaomi/mimo-v2.5-pro** — boolean-toggle reasoning (no
  effort lever), but it just thinks regardless and produces 24-30
  reasoning tokens on a 1-token probe. Cheap, stable, the
  adversarial-stance prompt does the real work. Variant field is
  intentionally omitted from frontmatter (would be silently dropped).
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
