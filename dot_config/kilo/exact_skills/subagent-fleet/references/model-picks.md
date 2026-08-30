# Model Picks (snapshot 2026-08-30T06:52Z, LOCKED)

> Refreshed to live Mix B picks after the 2026-08-30 empirical pass.
> Aki swap to `poolside/laguna-s-2.1` applied 2026-08-30T06:36Z (was
> `poolside/laguna-xs-2.1` since the 13:14Z lock); rationale and cost
> delta in the "Why these assignments" and "Cost ceiling" sections
> below.
> Haru swap to `deepseek/deepseek-v4-flash-0731` applied
> 2026-08-30T06:42Z (was `inclusionai/ling-3.0-flash` since the 13:14Z
> lock); rationale and cost delta below. Provider pin in
> `dot_config/kilo/kilo.jsonc` retargeted to top-3 v4-flash routes
> (OpenInference / Baidu / Relace).
> Natsu swap to `z-ai/glm-5.3-flash` applied 2026-08-30T06:52Z (was
> `nex-agi/nex-n2-mini` since the 13:14Z lock); rationale and cost
> delta below. Provider pin retargeted to top-3 glm-5.3-flash routes
> (Relace / Modal / Novita). Open risk: glm-5.3-flash released
> 2026-08-26 (4 days old at apply time) — no community-validated
> failure history; the next revaluation pass should re-probe the
> doom-loop class that broke nex-n2-mini on probe 2 of the empirical
> pass.
> `steps` and `maxTokens` columns reflect the **by-hand frontmatter
> values** applied 2026-08-30T13:14Z (see
> `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`).
>
> The 2026-08-30 fleet speed benchmark
> (`.agents/docs/cache/openrouter/2026-08-30-fleet-speed-benchmark.md`)
> recommended tighter per-role caps (steps 6/18/10/7) derived from
> observed max-measured runtime shape. The by-hand frontmatter
> supersedes the empirical recommendations with a uniform `steps: 40`
> ceiling for the four research subagents and per-role `maxTokens`
> floors (3000/8000/3000/600); the speed-benchmark's maxTokens column
> is preserved in the table below as the empirical ceiling for future
> revaluations.
>
> Natsu's `maxTokens` is capped at 16,000 (below the raw formula
> value of 48,500) to bound the doom-loop class observed on probe 2.
>
> Re-verify against `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` §4
> when reachable. OpenRouter adds new routes weekly; the `:batch` filter
> below must be re-applied before any new pick.

## Locked assignments (4 distinct families)

| Subagent | Model id | Family | T | top_p | variant: | steps (applied) | maxTokens (applied) | steps (empirical) | maxTokens (empirical) |
|---|---|---|---|---|---|---|---|---|---|
| `haru` adversarial | `openrouter/deepseek/deepseek-v4-flash-0731` | DeepSeek (V4 Flash) | 0.2 | 0.9 | low | 40 | 3000 | 6 | 2518 |
| `natsu` synthesizer | `openrouter/z-ai/glm-5.3-flash` | z-ai (GLM) | 0.5 | 0.9 | low | 40 | 8000 | 18 | 16000 |
| `aki` assumption-auditor | `openrouter/poolside/laguna-s-2.1` | poolside | 0.5 | 0.9 | low | 40 | 3000 | 10 | 1894 |
| `fuyu` comparator | `openrouter/qwen/qwen3.7-flash` | qwen | 1.0 | 0.95 | low | 40 | 600 | 7 | 5603 |
| `shiki` verifier | `openrouter/minimax/minimax-m3` | MiniMax | 0.4 | 0.95 | high | 40 | 16000 | — | — |

> **Shiki is excluded from the cap-selection formula** (user policy
> 2026-08-30T04:57Z): model is pinned, will not change, cap stays at
> `steps: 40, maxTokens: 16000` (no frontmatter `steps:` / `maxTokens:`
> lines on `shiki.md`; the values above are the de-facto cap until
> shiki frontmatter is updated).

## Constraints (verified at v7.4.22)

- Must accept `temperature` and `top_p` (or have them effectively
  ignored — at `variant: low` the difference is small).
- Must expose a `variant: low` (or equivalent `reasoning_effort: low`).
  Some models (`xiaomi/mimo-v2.5`, `z-ai/glm-4.7-flash`) silently drop
  `variant: low` because they only expose boolean reasoning toggles —
  this is accepted.
- Cost ceiling: ≤ $0.30 / M input tokens.
- **Real-time only** — must not carry a `:batch` suffix. `:batch` routes
  have a 24h latency SLA and break the subagent latency budget.
- Must be from 4 distinct families — picking four variants of the same
  family collapses inductive-bias diversity.

## Why these assignments

- **`haru` → deepseek/deepseek-v4-flash-0731** — 284B/13B-active
  coding-agent MoE; AA Intelligence 51.8, Coding 69.1, Agentic 48.4;
  GPQA Diamond 90.8%, AA-LCR 74.3%, SciCode 49.9%. Adversarial role
  punishes confident-but-wrong outputs and benefits directly from
  the model's exposed `reasoning_effort` parameter. Top provider
  OpenInference: $0.030 / $0.160 per M tokens ($0.01 cache read);
  p50 latency 0.64s, throughput 18 tok/s. Picked over
  `inclusionai/ling-3.0-flash` (the prior pick) on quality (GPQA
  90.8% vs no disclosed benchmark) and resilience (30 providers vs
  2; without-routing 88.89% → with-routing 99.91%); cost is
  comparable (~$0.00026/call at haru's prompt size, -22% vs ling).
  Provider pin in `dot_config/kilo/kilo.jsonc` orders
  `["OpenInference", "Baidu", "Relace"]` (listed-price top 3; Baidu's
  68% off promo excluded as not guaranteed). Note: cache-read ratio
  is 0.33× prompt (over the §4.0 0.2× cap) — grandfathered in this
  fleet snapshot, but the next revaluation should consider a
  `--cache-r-max-ratio` flag or a §4.0 rule update before this pick
  is re-locked.
- **`natsu` → z-ai/glm-5.3-flash** — 2026-08-26 release (4 days old
  at apply time); AA Intelligence 57.5 (top 8%), Coding 71.5
  (top 15%), Agentic 58.2 (top 4%). GPQA Diamond 91.2%, AA-LCR
  78.0%, Non-Hall 72.4%. Synthesizer role depends on long-context
  reasoning across multiple research artefacts; glm-5.3-flash was
  trained for exactly that workload ("efficient coding and
  long-horizon agent tasks"). 1.31M context, 131K max completion,
  $0.075/$0.25 per M tokens top-provider (Relace); cache-r ratio
  0.20× — passes the relaxed §4.0 0.5× cap. 20 providers; routing
  availability 99.90% (vs nex-n2-mini's single-provider pick —
  primary reason for the swap; the empirical pass probe 2 hit a
  32K-token doom-loop on nex-n2-mini that a multi-provider pick
  would have isolated). Top production apps driving the model:
  Hermes Agent (712B tokens), Claude Code (355B), Cline (294B),
  omp, DeepSeek Harness. Picked over `nex-agi/nex-n2-mini` on
  quality (AA Intelligence 57.5 vs no disclosed score), resilience
  (20 providers vs 1), and reasoning-trace control (`reasoning_effort`
  exposed). Cost is +180% per-call ($0.000575 vs $0.000205 at
  natsu's prompt size) — roughly +$0.55/month at fleet cadence.
  **Open risk**: glm-5.3-flash was 4 days old at apply time; no
  community-validated failure history. The doom-loop class that
  broke nex-n2-mini has not been re-probed on glm-5.3-flash. The
  next empirical pass (Step 2½ in the revaluation workflow) should
  run the same 5-probe synthetic natsu inputs against this model
  before the fleet lock is renewed.
- **`aki` → poolside/laguna-s-2.1** — 118B/8B-active coding-agent
  model (70.2% Terminal-Bench 2.1, 40.4% DeepSWE). Larger than the
  prior `laguna-xs-2.1` (33B/3B-active) — picked on 2026-08-30 for
  stronger reasoning on the assumption-auditing role. 1M context,
  131K max completion, $0.09/$0.18 per M tokens, $0.009 cache read
  (0.1× prompt — clears the §4.0 cache-r ratio filter, unlike XS at
  0.5×). Single-provider (Poolside direct); uptime 100% (3d), p50
  latency 310ms, throughput 75 tok/s. R7 (AA-30 threshold) deferred —
  the empirical pass's runtime-shape proxy is the only quality signal
  at this time.
- **`fuyu` → qwen/qwen3.7-flash** — qwen family; comparator's
  `temperature: 1.0` benefits from a base model that handles
  rubric-edge reasoning without collapsing. $0.030/$0.130 per M
  tokens (Alibaba).
- **`shiki` → `openrouter/minimax/minimax-m3`** — frontier reasoning
  model, the only non-flash subagent. Runs once per question with
  `variant: high`. Pinned — will not change without an explicit
  reevaluation.

## Provider routing

Pins live in `dot_config/kilo/kilo.jsonc` (chezmoi source) →
`~/.config/kilo/kilo.jsonc` (deployed). Each model lists its top-3
cheapest provider route with `allow_fallbacks: true`. The
`provider_selection_strategy` decision is recorded in
`~/.config/kilo/rules.personal.d/` history — top-3 providers with
explicit ordering; cheapest wins by default.

## Cost ceiling (N=4 + shiki)

Flash-class research (haru/natsu/aki/fuyu) + frontier shiki at
`variant: high` stays within the 4-distinct-family / real-time /
cache-eligible envelope. Per-call cost (Mix B):

- haru: $0.030 / $0.160 per M tokens (v4-flash top-provider OpenInference;
  -22% per-call vs ling at haru's prompt size)
- natsu: $0.075 / $0.250 per M tokens (glm-5.3-flash top-provider Relace;
  +180% per-call vs nex-n2-mini at natsu's prompt size; ~$0.55/month
  at fleet cadence)
- aki: $0.090 / $0.180 per M tokens (single-provider Poolside direct;
  1.5× the XS rate; negligible at subagent prompt sizes)
- fuyu: $0.030 / $0.130 per M tokens
- shiki: frontier pricing (kilo-internal); consumed once per question

The cheapest survivor in Mix B is haru at $0.030 / M input tokens
(was $0.021 with ling; +43% on the listed rate, but -22% on the
weighted-average per-call rate at haru's prompt size because v4-flash
is more cache-friendly). aki's input price rose from $0.030 (Mix A)
→ $0.060 (Mix B XS) → $0.090 (Mix B S); at the typical subagent
prompt size (~5K tokens × ~100 calls/day), the input-cost delta is
~$0.045/day or ~$1.35/month — small relative to the wall-clock win
from the latency swap and the quality uplift from the larger model.
Natsu's per-call cost rose from $0.000205 to $0.000575 with the
glm-5.3-flash swap; ~$0.55/month extra at fleet cadence. Aggregate
monthly fleet cost delta vs the original 13:14Z lock: ~$1.90/month
across all four research subagents (haru, natsu, aki, fuyu) — small
relative to the quality + resilience uplift across the fleet.

## Re-verification cadence

- OpenRouter `:batch` routes: re-filter weekly before any new pick.
- `variant: low` exposure: re-verify against the live model at session
  start — the OpenRouter `supported_parameters` matrix drifts.
- Benchmark snapshot: re-pull `GET https://openrouter.ai/api/v1/benchmarks`
  before any model swap. Only Artificial Analysis has substantive data
  for the current 4 survivors.
