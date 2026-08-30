# Model Picks (snapshot 2026-08-25, LOCKED)

> Re-verify against `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` §4
> when reachable. OpenRouter adds new routes weekly; the `:batch` filter
> below must be re-applied before any new pick.

## Locked assignments (4 distinct families)

| Subagent | Model id | Family | T | top_p | variant: |
|---|---|---|---|---|---|
| `haru` adversarial | `google/gemma-4-31b-it` | Google (Gemma) | 0.2 | 0.9 | low |
| `natsu` synthesizer | `xiaomi/mimo-v2.5` | Xiaomi (MiMo) | 0.5 | 0.9 | low |
| `aki` assumption-auditor | `deepseek/deepseek-v4-flash-0731` | DeepSeek (V4 Flash) | 0.5 | 0.9 | low |
| `fuyu` comparator | `z-ai/glm-4.7-flash` | Z.ai (GLM) | 1.0 | 0.95 | low |
| `shiki` verifier | `openrouter/minimax/minimax-m3` | MiniMax | 0.4 | 0.95 | high |

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

- **`haru` → Gemma 4 31B IT** — high-precision, low-hallucination
  family; adversarial role punishes confident-but-wrong outputs.
- **`natsu` → Xiaomi MiMo v2.5** — 1M context for synthesising
  multiple research artefacts.
- **`aki` → DeepSeek V4 Flash 0731** — strongest AA intel/coding scores
  in the cohort (51.8 / 69.1 / 48.4); assumption-spotting benefits
  from the strongest reasoning baseline.
- **`fuyu` → Z.ai GLM 4.7 Flash** — agentic-coding-tuned at flash-class
  price; the comparator's `temperature: 1.0` benefits from a base
  model that handles rubric-edge reasoning without collapsing.
- **`shiki` → `minimax/minimax-m3`** — frontier reasoning model, the
  only non-flash subagent. Runs once per question with `variant: high`.

## Provider routing

Pins live in `dot_config/kilo/kilo.jsonc` (chezmoi source) →
`~/.config/kilo/kilo.jsonc` (deployed). Each model lists its top-3
cheapest provider route with `allow_fallbacks: true`. The
`provider_selection_strategy` decision is recorded in
`~/.config/kilo/rules.personal.d/` history — top-3 providers with
explicit ordering; cheapest wins by default.

## Cost ceiling (N=4 + shiki)

Flash-class research + frontier shiki at `variant: high` stays ≤ 4× cheap
+ 1× frontier (≈ 2-3× a single frontier call, depending on flash-class
pick). The cheapest survivor (`aki`) is at $0.035 / M input tokens.

## Re-verification cadence

- OpenRouter `:batch` routes: re-filter weekly before any new pick.
- `variant: low` exposure: re-verify against the live model at session
  start — the OpenRouter `supported_parameters` matrix drifts.
- Benchmark snapshot: re-pull `GET https://openrouter.ai/api/v1/benchmarks`
  before any model swap. Only Artificial Analysis has substantive data
  for the current 4 survivors.
