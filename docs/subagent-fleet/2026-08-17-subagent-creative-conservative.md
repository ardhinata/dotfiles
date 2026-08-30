---
title: Subagent Fleet — Creative-Conservative Design (canonical)
date: 2026-08-17
last-updated: 2026-08-30
status: canonical
moved_from: .tmp/docs/plans/2026-08-17-subagent-creative-conservative.md
related:
  - docs/subagent-fleet/README.md
  - .tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md
  - .agents/kilo/skills/subagent-fleet/SKILL.md
  - ~/.config/kilo/skills/openrouter-api/SKILL.md
---

# Subagent fleet for research + verification

> **Status:** draft — §4 model picks LOCKED 2026-08-25 (4 survivors, 4 distinct
> families). Remaining open: §3.1-3.4 role refinements, §5.1 random selection,
> §5.2 sequential chain, §3.5 verifier deep-verify scope, §11 subagent-runs dir.
> All four have implicit defaults stated in §11.
> **Date captured:** 2026-08-17 (original) → revised 2026-08-20 → §4 locked 2026-08-25.
> **Supersedes:** the original 2026-08-17 "creative vs. conservative" framing for
> reasoning models (see §10 for what was learned).

## 1. Goal

When the main agent is stuck or wants a second opinion on a research question, it
launches a small fleet of subagents — **4 research subagents** of different types
plus **1 verifier subagent** — and reads only the verifier's synthesised report.

The main agent decides **which subset of research subagents to launch** (1, 2, 3,
or 4) per question. The choice is **picked by random** (uniform over a default
4-type list) to:

- avoid anchoring the main agent on one research style,
- bound the worst-case fan-out cost,
- keep the verifier useful even when only one research subagent ran.

**Verifier is mandatory** whenever ≥2 research subagents ran. The verifier
filters the four (or fewer) research reports into one summary, so the main agent
sees a single artefact and never gets noise-injected into its own context.

## 2. Why this design (the lessons from the rejected approach)

The original 2026-08-17 plan framed the contrast as **creative vs. conservative
sampling on the same reasoning model**. That framing has been rejected:

- On reasoning models, `temperature` is either **rejected (400)** by the newest
  models (GPT-5.x, Claude Opus 4.7+, Sonnet 5+) or **silently ignored** when
  thinking is on (DeepSeek V4 Flash: *"In DeepSeek thinking mode this parameter
  is accepted for compatibility but has no effect"* —
  `.agents/docs/cache/kilo-subagents/2026-08-17-creative-conservative-sampling-by-openrouter-model.md:32`).
- Even when sampling lands, varying temperature on a reasoning model only
  changes the **final-answer sampler**, not the reasoning trace. The diversity
  is surface phrasing, not genuine disagreement.
- The cheapest meaningful diversity on a reasoning model comes from
  **prompt-conditioned roles** (different framings of the same problem) or
  **different model families** (different inductive biases). Sampling tilt is a
  cherry on top.

The new design uses both levers:

1. **4 prompt-conditioned research roles** (RCAF-style) — adversarial,
   synthesizer, assumption-auditor, comparator. The disagreement is structural,
   not stochastic.
2. **4 different model families** — cheap flash-class open-weight models.
   Inductive bias diversity.
3. **`variant: low` on all research subagents** — bounded cost and latency per
   call. The verifier runs on `minimax-m3` (frontier) so it can absorb the
   cheap research output and decide what is worth re-checking.
4. **Sampling tilt (low T vs high T) is optional and minor** — kept as a per-type
   tuning knob but not the source of diversity.

## 3. The five subagent roles

The four research roles are the **four seasons** (春 haru / 夏 natsu /
秋 aki / 冬 fuyu). One role per file. Each returns a **structured
report** the verifier can consume. The fifth is the verifier — named
`shiki` (四季 "four seasons"), the cycle that contains all four.

> **Naming note (2026-08-25):** the English role names
> (`research-{adversarial,synthesizer,assumption-auditor,comparator,verifier}`)
> were replaced with Japanese four-seasons names. File paths, frontmatter
> descriptions, body headings, the YAML `subagent:` field, and every
> cross-reference in the anti-patterns sections now use
> `haru/natsu/aki/fuyu/shiki`. The design rationale is preserved
> verbatim below — only the names changed.

### 3.1 Subagent haru — adversarial (春, spring)

- **Stance:** assume the current leading candidate answer is wrong.
- **Inputs:** the problem statement + leading candidate(s) + relevant context.
- **Output:** ranked list of the top 3 failure modes for the leading candidate,
  each with: failure claim, evidence (file:line or URL), confidence (0-1),
  preconditions for the failure.
- **Sampling tilt:** **conservative** (`temperature: 0.2`, `top_p: 0.9`) — keep
  the failure claims focused and evidence-grounded.
- **Variant:** `low` on the chosen model.

### 3.2 Subagent natsu — synthesizer (夏, summer)

- **Stance:** propose the most coherent candidate solution(s).
- **Inputs:** the problem statement + relevant context. May see haru's
  output if spawned after haru in a fan-out run (best-effort, not guaranteed).
- **Output:** ranked list of the top 3 candidate answers, each with: claim,
  reasoning summary, evidence (file:line or URL), confidence (0-1), open
  questions for the verifier.
- **Sampling tilt:** **balanced** (`temperature: 0.5`, `top_p: 0.9`) — enough
  variance to consider alternative framings without losing coherence.
- **Variant:** `low`.

### 3.3 Subagent aki — assumption-auditor (秋, autumn)

- **Stance:** meta — list the assumptions the problem statement and leading
  candidates rely on but never justify.
- **Inputs:** the problem statement + context.
- **Output:** ranked list of assumptions, each with: assumption statement, why
  it matters, how likely it is wrong (0-1), and what would change if it were
  false.
- **Sampling tilt:** **balanced** (`temperature: 0.5`, `top_p: 0.9`).
- **Variant:** `low`.

### 3.4 Subagent fuyu — comparator (冬, winter)

- **Stance:** compare two or more candidate approaches on a fixed rubric
  (correctness, cost, risk, complexity).
- **Inputs:** the problem + a list of candidate approaches (the main agent may
  pass leading candidates from prior subagent runs).
- **Output:** ranked comparison table, with: criterion, score per candidate
  (0-1), reasoning per score, overall ranking, ties called out.
- **Sampling tilt:** **creative** (`temperature: 1.0`, `top_p: 0.95`) — let the
  rubric reasoning range, since comparison benefits from seeing the rubric
  edges.
- **Variant:** `low`.

### 3.5 Subagent shiki — verifier (四季, mandatory when ≥2 research ran)

- **Stance:** neutral arbiter. Read the artefacts from the research subagents,
  cross-check the claims, and produce one consolidated report for the main
  agent. Named **shiki** ("four seasons") because it spans the four
  seasonal research roles the way "四季" sits above individual seasons.
- **Model:** `minimax/minimax-m3` (frontier reasoning model — the user
  specified). This is the only subagent that runs on a non-flash model.
- **Variant:** `high` (frontier capability; only one call per question, so cost
  is bounded).
- **Sampling tilt:** **balanced** (`temperature: 0.4`, `top_p: 0.95`) —
  conservative enough to not invent consensus, balanced enough to weigh
  conflicting evidence fairly.
- **Two-pass verification** (this is the verifier's distinctive value):

  1. **Shallow verification** — for every claim with `confidence ≥ 0.6` from
     the research subagents, simulate or test whether the claim is plausible:
     - For code claims: re-read the cited file:line, check the syntax, check the
       control flow. **No execution.**
     - For factual claims: check the cited URL is reachable and the snippet
       matches the claim (read-only `webfetch`).
     - For numerical claims: arithmetic / unit check by hand.
     - Mark each claim: `shallow: pass | fail | inconclusive`.

  2. **Deep verification** — for claims the main agent (or haru, the
     adversarial) flagged as **load-bearing** (security, correctness, scope,
     cost), or for any claim marked `shallow: inconclusive`:
     - Run a fresh `websearch` for the claim's keywords, gather the top 3-5
       grounded sources.
     - Cross-check the claim against grounded information. Quote the matching
       passage from each source.
     - Mark each claim: `deep: confirmed | refuted | unclear`.

- **Output:** one consolidated report with:
  - Top recommendation (with confidence).
  - Per-claim table: claim, source subagent, shallow status, deep status
    (or N/A), final verdict.
  - Open questions the main agent should escalate (max 3).
  - Provenance: list of all research subagents that ran (haru/natsu/aki/fuyu
    in the order the main agent spawned them) and which claims came from each.

## 4. Model selection (generalised criteria + locked picks)

### 4.0 Eligibility + decision rule (generalised 2026-08-30)

The fleet picks **4 different flash-class models**, one per research
subagent. The rules below apply to every revaluation. Rules R1-R5 were
verified at v7.4.22; R6-R7 were added on 2026-08-30 after the Mix-A
revaluation surfaced an AA-7.1 aki that returned *plausible* YAML but
missed the very hidden assumptions the role exists to surface.

**Eligibility filter (default; opt-out via flags per the
`subagent-fleet-reevaluate-models` workflow):**

| Rule | Condition | Status |
|---|---|---|
| R1 | Output price ≤ $1.1 / M tokens (`pricing.completion ≤ 1.1e-6`) | Verified 2026-08-23 |
| R2 | Input price ≤ $0.6 / M tokens (`pricing.prompt ≤ 0.6e-6`) | Verified 2026-08-23 |
| R3 | Cache read present, > 0, ≤ 0.2× input price | Verified 2026-08-23 |
| R4 | Real-time only (no `:batch` / `:exacto` / other deferred tag) | Verified 2026-08-25 |
| R5 | Cheapest provider route accepts both `temperature` and `tools` | Verified 2026-08-23 |
| **R6** | **Context length ≥ 262144 tokens (≈256K)** | **New 2026-08-30** — backstop against small-context models with no benchmark data |
| **R7** | **AA intelligence index ≥ role-dependent threshold (aki: 30; haru/natsu/fuyu: 15)** | **New 2026-08-30** — capability floor |

**Decision rule (Phase 1 → Phase 4 cascade):**

1. **Phase 1 — Quality gate.** Drop survivors that fail R7 for the slot
   being filled. R7 thresholds are role-dependent: the assumption-auditor
   role depends on the strongest reasoning baseline (per §4.1, "aki
   dominates the cohort on every AA axis … assumption-auditor benefits
   from the strongest reasoning baseline"), so R7 for aki is set higher
   than for the other three slots. The haru/natsu/fuyu slots tolerate
   lower quality because their roles are not pure-reasoning.
2. **Phase 2 — Diversity gate.** Bucket survivors by family (pre-slash
   prefix). Pick the cheapest survivor in each of 4 distinct families.
3. **Phase 3 — Cost gate (exception).** If a survivor's per-call cost at
   p95 input (estimate 50K prompt tokens for a research run) would exceed
   **$0.50 per call**, drop to the next survivor in the same family
   regardless of AA score. **Pricing wins only here** — i.e. when the
   *relative* quality-vs-cost is unsustainable for the run class the
   fleet actually does (long-input research turns), not for absolute
   pricing pressure.
4. **Phase 4 — Training-risk gate.** Apply the Step 5 training-risk pass
   from the revaluation workflow. Survivors with ⚠ providers are
   pickable; ❌ providers require explicit user opt-in via the custom
   path; ✅ providers proceed.

**Why this order.** Quality first — cost is meaningless if the model
cannot do the role. Diversity before cost — family diversity is the
inductive-bias hedge (§4 invariant). Cost as exception, not default —
the fleet's actual launch cadence is rare and bursty (per
`GET https://openrouter.ai/api/v1/activity`, fleet-family spend was
**$5.48 over 30 days** as of 2026-08-30, with one 719-request burst
on 2026-08-16 driving most of it). Absolute cost pressure is low; the
Phase 3 gate targets per-call unsustainable-cost, not aggregate spend.

**Operational cadence:**

- Re-run the revaluation workflow weekly before any new pick.
- Re-evaluate R7 thresholds quarterly or after any model swap.
- The `$5.48 / 30 days` baseline assumes current OpenRouter prices and
  current launch frequency; a 10× cost regression (e.g., a frontier
  swap) would push the baseline to ~$55/month, still cheap. Re-baseline
  when either price or launch cadence shifts.

### 4. Picks — current locked set
`.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md`
and `.agents/docs/cache/kilo-subagents/2026-08-17-creative-conservative-sampling-by-openrouter-model.md`):

**Older per-rule notes (now superseded by §4.0 above):**

- Must accept `temperature` and `top_p` (or have them effectively ignored — at
  `variant: low` the difference is small, but accepting them keeps the per-role
  tilt tunable). Captured by R5.
- Must expose a `variant: low` (or equivalent `reasoning_effort: low`).
- Cost ceiling: ≤ $0.30 / M input tokens. Captured by R2 (≤ $0.6/M — stricter
  than the historical $0.30/M ceiling for the same slot set).
- **Real-time only** (added 2026-08-25) — captured by R4. The 11 `:batch`
  rows the note surfaced (`gpt-5-nano:batch`, `gemini-2.5-flash-lite:batch`,
  `gpt-4o-mini:batch`, `gpt-4.1-nano:batch`, `gpt-4.1-mini:batch`,
  `gpt-5-mini:batch`, `gpt-5.6-luna-pro:batch`, `gpt-5.6-luna:batch`,
  `gpt-5.4-nano:batch`, `gemini-3.1-flash-lite:batch`, `gemini-3.7-flash:batch`)
  are out of scope. Re-verify before final pick — OpenRouter adds new
  batch-tagged routes weekly.
- Per OpenRouter `supported_parameters` as of 2026-08-17: candidates that
  accept `temperature` + `top_p` + reasoning-effort control on flash-class
  open-weight routes include `deepseek/deepseek-v4-flash-0731` (with
  `options: { thinking: { type: "disabled" } }`), `qwen/qwen3.7-flash`,
  `meta/llama-4-scout`, `meta/llama-4-maverick`. **Re-verify against
  OpenRouter catalog before final pick** — high-volatility domain.

| Subagent | Model | Family | T | top_p | variant: |
|---|---|---|---|---|---|
| haru adversarial | `google/gemini-2.5-flash-lite` | Google (Gemini) | 0.2 | 0.9 | low |
| natsu synthesizer | `xiaomi/mimo-v2.5` | Xiaomi (MiMo) | 0.5 | 0.9 | low |
| aki assumption-auditor | `deepseek/deepseek-v4-flash-0731` | DeepSeek (V4 Flash) | 0.5 | 0.9 | low |
| fuyu comparator | `z-ai/glm-4.7-flash` | Z.ai (GLM) | 1.0 | 0.95 | low |
| shiki verifier | `openrouter/minimax/minimax-m3` | MiniMax | 0.4 | 0.95 | high |

**Picks locked 2026-08-25** from 7 candidates that were pre-pinned in
`dot_config/kilo/kilo.jsonc` (top-3 cheapest provider route + `allow_fallbacks:
true` per model, see `2026-08-25-subagent-plan-turn2-continuation.md` §1).
4 distinct families: Google / Xiaomi / DeepSeek / Z.ai — meets the diversity
constraint.

**haru swap 2026-08-25 (post-lock):** original pick `google/gemma-4-31b-it`
replaced with `google/gemini-2.5-flash-lite` because the Gemma routes
on OpenRouter (chutes/friendli/deepinfra) returned 0% cache-read ratio.
Gemini 2.5 Flash Lite routes via Google AI Studio with prompt-cache
support (`input_cache_read: $0.005/M` at `google-ai-studio/flex`,
`$0.01/M` at `google-ai-studio`, `$0.018/M` at `google-ai-studio/priority`
— 90% discount on cached input tokens). Family shift: Google / Gemma →
Google / **Gemini** (same parent company, different architecture
family). The 4-distinct-family property weakens slightly (still Google,
but Gemini is architecturally distinct from Gemma). Documented as a
deviation from the locked §4 picks. See §11 for the deviation log.

Why these assignments:
- **haru adversarial → Gemini 2.5 Flash Lite** — replaces Gemma 4 31B IT.
  Rationale: cache reads now work (90% discount on repeated prompts);
  AA benchmarks for Gemini 2.5 Flash Lite are substantially higher than
  Gemma 4 31B IT (intel ~50 vs 29.7, agentic ~30 vs 14.4 — figures
  pending AA re-fetch, the `/benchmarks` endpoint returned 401 without
  cookie auth on 2026-08-25); latency is faster (Flash-Lite is the
  lightest Google model). The adversarial role's first-call latency
  drives overall fan-out wall time, so the speed win compounds. Cost
  is lower at `google-ai-studio/flex` ($0.05/M in vs Gemma's $0.08/M
  OpenInference cheapest).
- **natsu synthesizer → Xiaomi MiMo v2.5** — 1M ctx for synthesising multiple
  research artefacts; multimodality a bonus if the question touches images.
- **aki assumption-auditor → DeepSeek V4 Flash 0731** — MoE + reasoning_effort
  exposure; assumption-spotting benefits from explicit chain-of-thought even
  when sampling tilt is bound.
- **fuyu comparator → Z.ai GLM 4.7 Flash** — agentic-coding-tuned at flash-class
  price; the comparator role's `temperature: 1.0` / `top_p: 0.95` benefits
  from a base model that handles rubric-edge reasoning without collapsing.

Picks **not** used and why:
- `~deepseek/deepseek-v4-flash-latest` (rolling) — superseded by the
  deterministic `0731` pin. Same family.
- `meta/muse-spark-1.2-contributor` — single-provider (`meta` only,
  `allow_fallbacks: false`) and Meta uses prompts for training. Kept as a
  backup if the user later overrides the training constraint.
- `tencent/hy3` — dropped during 7→4 trim; Tencent family available if the
  user later wants to swap haru out of Google.

### 4.1 Benchmark snapshot (2026-08-25, OpenRouter `/benchmarks`)

Source: `GET https://openrouter.ai/api/v1/benchmarks`,
`as_of: 2026-08-25T00:02:09.721Z` (today, 235 models, 1438 records).
Only Artificial Analysis has substantive data — Design Arena and OpenRouter-
source records returned empty `rank`/`score` for these slugs (insufficient
votes yet). Scores below are at **max reasoning effort**; per the plan §2
lesson, `variant: low` will produce proportionally lower scores.

| Survivor | AA permaslug | intel | coding | agentic | $in/M (cheapest) | $out/M |
|---|---|---|---|---|---|---|
| aki `deepseek-v4-flash-0731` | `deepseek-v4-flash-20260731` | **51.8** | **69.1** | **48.4** | 0.035 | 0.10 |
| natsu `xiaomi/mimo-v2.5` | `mimo-v2.5-20260422` | 38.0 | 56.8 | 24.4 | 0.119 (GMICloud, broken) | 0.238 |
| fuyu `z-ai/glm-4.7-flash` | `glm-4.7-20251222` | 34.5 | 45.3 | 26.2 | 0.06 | 0.40 |
| haru `google/gemini-2.5-flash-lite` | TBD (AA re-fetch required) | TBD | TBD | TBD | 0.05 (google-ai-studio/flex) | 0.20 |

**Key readings:**
- aki dominates the cohort on every AA axis (intel 51.8 vs the others'
  29-38 range). Reinforces the aki assignment — assumption-auditor benefits
  from the strongest reasoning baseline.
- natsu's apparent cheapest provider (GMICloud, 15% off) is at **18.8% uptime**
  — broken. The kilo.jsonc pin (`xiaomi/fp8 → parasail/fp8 → novita/fp8`)
  skips GMICloud. Parasail/fp8 at $0.14/$0.28 is the live cheapest at
  97.9% uptime.
- haru's cheapest provider is `google-ai-studio/flex` at **$0.05/$0.20**
  (input/output per 1M tokens), with `input_cache_read` at **$0.005/M**
  (90% discount on cached input). The 2026-08-25 swap from
  `gemma-4-31b-it` to `gemini-2.5-flash-lite` was driven by the
  cache-read observation (gemma routes returned 0% cache reads). AA
  benchmark scores for Gemini 2.5 Flash Lite are pending re-fetch —
  the `/benchmarks` endpoint returned 401 without cookie auth on
  2026-08-25. **Verify AA scores before next deployment review.**
- All four accept `tools + temperature + top_p + reasoning` on the
  cheapest live route. Only aki exposes `reasoning_effort` (an enumerated
  level, not a boolean) — see §4.2.

### 4.2 `variant: low` exposure per model

Kilo's variant resolution at v7.4.22 (see
`.agents/docs/cache/kilo-subagents/2026-08-15-reasoning-variants-by-provider.md`):

| Survivor | Variant map | `variant: low` supported? |
|---|---|---|
| aki `deepseek-v4-flash-0731` | `WIDELY_SUPPORTED_EFFORTS + max` = `[low, medium, high, max]` (`deepseek-v4` substring match in the OpenAI-compatible branch) | **YES** |
| haru `google/gemini-2.5-flash-lite` | OpenRouter `supported_parameters` lists `reasoning`, `include_reasoning`, `temperature`, `top_p` but **not** `reasoning_effort`. The OpenRouter `reasoning.effort` envelope likely applies; verify per session with `kilo provider list --json`. | **LIKELY YES** (envelope; verify at session start) |
| natsu `xiaomi/mimo-v2.5` | OpenRouter boolean-toggle branch (line 104) | **NO effort levels** — only `instant` / `thinking`. `variant: low` is silently dropped. |
| fuyu `z-ai/glm-4.7-flash` | OpenRouter boolean-toggle branch (line 104) | **NO effort levels** — only `instant` / `thinking`. `variant: low` is silently dropped. |

**Implication:** haru/natsu/fuyu cannot honour `variant: low` to lower
reasoning effort. Options:

1. **Accept the limitation** — set `variant: low` on all 5; for natsu/fuyu
   it is silently dropped (no harm), for haru it works via the OpenRouter
   envelope. aki gets the full low-effort benefit.
2. **Skip `variant:` on natsu/fuyu** and rely on the model's own
   reasoning-toggle defaults. natsu/fuyu will reason at default effort;
   cost goes up.
3. **Switch natsu or fuyu to a reasoning-effort-exposing model** (e.g.,
   `~deepseek/deepseek-v4-flash-latest` rolling, or swap fuyu to a
   non-boolean-toggle model like `tencent/hy3` if it exposes effort —
   needs verification).

**Recommendation:** option 1 (accept the limitation). The natsu/fuyu
reasoning default is acceptable for the synthesizer (long-context
coherence matters more than effort tuning) and the comparator
(creative-tilt sampling is the intended lever anyway). Plan stays as
written.

User picks A-D must be **4 different model families** — picking four variants
of the same family collapses the inductive-bias diversity that the design
depends on.

## 5. Invocation pattern

The main agent runs:

```text
1. Decide N = uniform_random(1, 2, 3, 4) research subagent types to launch
   (default 4, but the main agent may override for cost or per-question reasons).
2. Pick which research subagent types to launch. If N < 4, prefer the most
   relevant role(s) for the question. Default set when N < 4:
   [haru, natsu, aki, fuyu] uniformly sub-sampled.
3. Spawn the chosen N research subagents **in parallel** with the same prompt.
   Each subagent receives: the question, the relevant context, and any prior
   research artefacts (best-effort — pass haru's output to fuyu if you spawn both).
4. **If N ≥ 2:** spawn shiki (verifier) with all the research artefacts as input.
   **If N == 1:** spawn shiki only when the main agent flags the single
   research subagent's output as load-bearing (e.g. it will be cited in the
   final answer).
5. Read shiki's consolidated report. Decide whether to escalate (call
   another subagent at `variant: high` on a frontier model, or have the main
   agent do its own deep dive) or accept.
```

The main agent must **never read raw research subagent output directly** when
N ≥ 2 — shiki is the only channel into the main agent's context. This
keeps the noise out of the main agent's working memory.

### 5.0 Task-prompt budget (revised 2026-08-25)

The main agent's `task` prompt to each subagent should be **≤ 15 lines**
of content the subagent body does not already cover. Each agent body
already contains:

- the role definition, output contract, and per-role anti-patterns (§3 + §7 + §8);
- the operational discipline preamble (§6.1 — permission model,
  mutation boundaries, delegation pre-deny list);
- the sampling behaviour, variant-exposure note, and rationale (§3.x
  + §4.2).

**Do NOT duplicate this in the task prompt.** Repeating the operational
discipline preamble in the task prompt is duplicate signal — it adds
~30 lines of input per subagent and produces no additional output
quality. The task prompt's job is **only** to convey:

1. the question (1-3 lines);
2. the required-reading list (paths/URLs to cite);
3. the output path (`.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>[-<topic>].yaml`,
   e.g. `20260826_113348-natsu.yaml` or `20260826_113348-natsu-sdd-synthesis.yaml`;
   computed at write time with `date +%Y%m%d_%H%M%S`);
4. any constraint the agent body does not cover (e.g. "the question
   has one load-bearing correctness claim — verify it against the
   post-mortem's env-trace before generalising").

The role description, anti-patterns, and sampling rationale are
**already in the body**. Treat them as authoritative — do not edit
them in the task prompt to "customise for this question".

### 5.0a Operational gotchas observed in 2026-08-25 live run

Two operational gotchas surfaced during the live pinentry simulation
run. Both are recoverable in <30 seconds but should be patched for
future runs:

1. **Subagent working-directory drift.** In a worktree-resident run,
   the main agent spawned 4 research subagents via `task`. Three of
   four wrote their YAML reports to the **live repo's**
   `.tmp/docs/subagent-runs/` instead of the worktree's. The cause
   was the subagent body's output-path spec
   (`.tmp/docs/subagent-runs/...`) being resolved from `$PWD` — when
   `$PWD` is the live repo, the path lands there even though the
   question is about the worktree's contents.

   **Fix:** each agent body now states a "Working directory" note
   instructing the subagent to default to
   `$(git rev-parse --show-toplevel)/.tmp/docs/subagent-runs/` from
   `$PWD` when the task prompt omits an explicit working directory.
   For full control, pass an explicit `workdir` to the `task` tool
   so the subagent runs inside the worktree.

2. **shiki's `edit`/`write` to `.tmp/docs/subagent-runs/` denied by
   inherited parent permissions.** The parent Kilo agent's broader
   deny-all overrides shiki's role-spec allow. shiki fell back to
    `/tmp/kilo/YYYYMMDD_HHMMss-shiki.yaml`; main agent `mv`'d to the canonical
   location. The plan §6 permission block does not propagate as
   designed when the parent agent's permission block is broader.

   **Fix:** shiki's body now explicitly handles the fall-back — if
   the write to `.tmp/docs/subagent-runs/` is rejected, write to
    `/tmp/kilo/YYYYMMDD_HHMMss-shiki.yaml` and tell the main agent the
   canonical path so it can `mv` after the run. Alternatively, the
   parent agent's `kilo.json` could add
   `edit: { ".tmp/docs/subagent-runs/**": "allow" }` so the
   inheritance carries the allowance through. The latter is more
   invasive (changes the parent agent's surface) and is left as a
   per-user choice.

### 5.1 Random selection

The main agent picks N research subagent types uniformly at random from the
power set of {haru, natsu, aki, fuyu}. To keep the design deterministic for
the user review, the random draw can be:

- **Implicit** — the main agent uses a coin flip or `shuf` at spawn time, and
  logs which subagents ran. The user can audit by reading shiki's report
  (provenance section).
- **Seeded** — the main agent uses the question hash as the seed, so the same
  question gets the same subagent set (reproducibility for re-runs).
- **Explicit** — the main agent picks deterministically based on question type
  (but this loses the diversity property).

**Recommended:** implicit, logged in shiki's provenance section.

### 5.2 Sequential chain (optional, not the default)

For high-stakes questions, the main agent may run two rounds:

1. Round 1: spawn haru (adversarial) alone. Use its output to refine the question.
2. Round 2: spawn natsu, aki, fuyu with the refined question. Run shiki.

This is more expensive (~3 research calls + 1 verifier) but produces
higher-quality output on questions where the adversarial pass reveals that the
original framing was wrong. The main agent decides whether to use this pattern
based on the question's stakes, not by default.

## 6. Permission block (shared by all 5 subagents) — revised 2026-08-25

Hybrid model: an explicit allowlist of common read-only bash commands runs
without prompting; everything else bash triggers a per-call user confirmation
(`ask`). Web research tools (built-in + MCP) are allowed. Mutation tools
(`edit`, `write`) are scoped to the report-doc directory and `/tmp/kilo`.

```yaml
permission:
  "*": deny
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit:
    "*": deny
    ".tmp/docs/subagent-runs/**": allow
    ".tmp/docs/subagent-runs/**/*": allow
  write:
    "*": deny
    ".tmp/docs/subagent-runs/**": allow
    ".tmp/docs/subagent-runs/**/*": allow
  external_directory:
    "/tmp/kilo/**": allow
    "/tmp/kilo/**/*": allow
  bash:
    "*": ask
    "git log *": allow
    "git diff *": allow
    "git status *": allow
    "git show *": allow
    "find *": allow
    "grep *": allow
    "ls *": allow
    "cat *": allow
    "tail *": allow
    "head *": allow
  webfetch: allow
  websearch: allow
  firecrawl_*: allow
  tavily_*: allow
  context7_*: allow
  # `task`, `question`, `suggest`, `interactive_terminal` are auto-denied by
  # the KiloTask pre-pend layer (see §13); do not declare them here.
```

Notes on the block:

- **`*` → `ask` is the catch-all** — order matters (last match wins). The
  allowlist entries come AFTER `*`, so specific patterns override the ask
  for the common read-only commands. Any other bash call (including every
  `aws` verb, `docker`, `kubectl`, package managers) prompts the user.
- **`firecrawl_*` / `tavily_*` / `context7_*` are MCP catch-alls** — the
  tool id format is `<tool_id>_<tool_name>` (e.g. `firecrawl_firecrawl_search`),
  so the single-segment `*` matches every tool that server exposes.
  No `:batch` / `:exacto` / `:<tag>` variants exist on MCP tool ids; those
  are only an OpenRouter route-suffix phenomenon (see §4 real-time filter).
- **`/tmp/kilo` depth limit** — `*` does NOT match `/` in this matcher (per
  `.agents/docs/cache/kilo-subagents/2026-08-15-permissions-actions-precedence.md:70`),
  so the two patterns `/tmp/kilo/**` and `/tmp/kilo/**/*` together cover one
  and two segment depths. Three-or-more segments (e.g. `/tmp/kilo/a/b/c.md`)
  do not match — accepted limitation, documented.
- **Subagents stay read-only by default** — if the question requires
  mutation, the main agent does the mutation, not the subagents.
- **This permission block is the source of truth, not the task prompt**
  (added 2026-08-25). The main agent's `task` prompt must NOT
  re-declare any of these rules. The 2026-08-25 live run saw a30-line
  task prompt that re-embedded the permission model, mutation
  boundaries, and delegation pre-deny list — all already in the agent
  body. The duplicate cost ~30% of the prompt's input tokens without
  changing the output. See §5.0 "Task-prompt budget" for the
  ≤ 15-line rule.

### 6.1 Operational discipline preamble (prepend to every subagent body)

The body of each subagent's markdown file is the system prompt (per
`.agents/docs/cache/kilo-subagents/2026-08-15-agent-frontmatter-reference.md:48-50`).
Every subagent body starts with this section so the read-only discipline
sits alongside the role-specific prompt:

```markdown
## Operational discipline (read-only by default)

You run under a hybrid permission model:

- **Allowlisted bash** (no prompt): git read-only (`log`/`diff`/`status`/`show`),
  `find`, `grep`, `ls`, `cat`, `tail`, `head`.
- **Catch-all bash**: every other command — including all `aws` verbs, `docker`,
  `kubectl`, package managers, anything not in the allowlist — triggers a
  per-call user confirmation (`ask`). Use these only when no allowlisted
  equivalent exists.
- **Mutation tools** (`edit`, `write`) are denied everywhere except the report
  doc location `.tmp/docs/subagent-runs/` and the scratch dir `/tmp/kilo`.
- **Web research tools** are allowed: `webfetch`, `websearch`, `firecrawl_*`,
  `tavily_*`, `context7_*`.
- **Delegation tools** are auto-denied: `task` (cannot spawn further subagents),
  `question` / `interactive_terminal` / `suggest` (cannot query the user).

Treat the `ask` fallback as a hard stop. Prefer read-only equivalents:

| Mutating (will prompt) | Read-only substitute |
|---|---|
| `git push`, `git commit` | `git log`, `git diff`, `git show` |
| `aws ec2 run-instances`, `aws iam create-access-key` | `aws ec2 describe-*`, `aws iam list-*`, `aws iam get-*` |
| `rm`, `mv`, `cp` to overwrite | read the file, then in your output write `main_agent_should_run: <cmd>` and let the main agent execute it |
| any package install / service restart | state the action in your output; do not run |

The main agent owns all mutations. You produce findings and recommended
actions in your structured output; the main agent performs the writes.
```

## 7. Output contract — research subagents

Every research subagent returns the same envelope so shiki can parse it
uniformly:

```yaml
# in the subagent's final assistant message
subagent: <haru|natsu|aki|fuyu>
question: <echo of the input question>
findings:
  - claim: <one-sentence claim>
    evidence:
      - type: file|url|code|numerical
        ref: <file:line or URL or expression>
        snippet: <optional excerpt>
    confidence: 0.0-1.0
    load_bearing: <true|false>     # security / correctness / cost
    open_questions: [<optional list>]
assumptions_made: [<optional list>]
```

`load_bearing: true` is the signal to shiki that this claim must go
through deep verification.

## 8. Output contract — shiki (verifier)

```yaml
subagent: shiki
question: <echo>
provenance:
  research_ran: [<list of haru|natsu|aki|fuyu in spawn order>]
  verifier_model: openrouter/minimax/minimax-m3
  random_seed: <if used>
recommendation:
  claim: <one-sentence top recommendation>
  confidence: 0.0-1.0
  rationale: <2-3 sentences>
claims_table:
  - claim: <from research subagent>
    source: <haru|natsu|aki|fuyu>
    shallow: pass|fail|inconclusive|N/A
    deep: confirmed|refuted|unclear|N/A
    final_verdict: accept|reject|needs-escalation
open_questions_for_main_agent: [<max 3>]
```

The main agent reads only `recommendation`, `open_questions_for_main_agent`,
and **optionally** `claims_table` when it wants to audit. The raw research
artefacts do not enter the main agent's context.

## 9. Validation checklist (after the subagents are defined)

> **Naming (2026-08-25):** `kilo agent list` should show the 5 agents
> by their Japanese season names — `haru`, `natsu`, `aki`, `fuyu`,
> `shiki`. Plan §3 prose still uses `research-{adversarial,…}` as the
> role description; the names are the seasonal aliases.

1. **Load check** — `chezmoi diff` (or `kilo agent list` in TUI) confirms
   all 5 subagents load. Per `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md:73-86`,
   `top_k` is **not** a frontmatter field — if `top_k` is desired per subagent,
   it goes via `options: { top_k: <n> }`.
2. **Permission check** — `kilo agent list --json` (or equivalent) shows all 5
   subagents have `permission.task: deny` (auto-prepended per
   `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md:35-47`).
   This is the one-level delegation ceiling.
3. **Subagent isolation** — confirm that even with the parent's `edit`/`bash`
   permissions set to allow, the subagents stay read-only (parent's `deny`
   survives per `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md:21-26`,
   `KiloTask.inherited` mutation set = `["edit", "notebook_edit", "notebook_execute"]` — no
   `bash` carryover).
4. **Per-model behavior** — run a single known question with N=4
   (haru + natsu + aki + fuyu in parallel). Confirm shiki's
   `claims_table` has rows for each research subagent and that the
   `provenance.research_ran` list names all four.
5. **Cost ceiling** — verify the worst case (N=4 + shiki) stays within the
   per-question budget. Flash-class + frontier shiki at `variant: high`
   should be ≤ 4× cheap + 1× frontier (≈ 2-3× a single frontier call,
   depending on the flash-class pick).
6. **Determinism** — for reproducibility, use the seeded random option
   (§5.1) and capture the seed in shiki's `provenance.random_seed` field.

## 10. What was learned from the rejected approach

The 2026-08-17 "creative vs. conservative sampling" plan failed three ways on
reasoning models:

1. **Reasoning models reject or ignore sampling on the reasoning trace.** The
   newest reasoning models (GPT-5.x, Claude Opus 4.7+, Sonnet 5+, Fable 5)
   reject non-default `temperature`/`top_p`/`top_k` with HTTP 400 — the
   request fails, not silently degrades. Older reasoning models that still
   accept sampling (DeepSeek V4 with thinking on, Claude 3.x-Opus 4.6,
   GPT-5.1+ at `reasoning_effort: none`) **forward the parameter only to the
   final-answer sampler** — the reasoning trace is invariant. Source:
   web research 2026-07-2026-08 (see cache entry
   `2026-08-17-creative-conservative-sampling-by-openrouter-model.md` for the
   per-model matrix).
2. **Inkling-small is the only candidate that supports the full contrast**, and
   it is not an open-weight flash model — it is a Thinking Machines hosted
   endpoint. Per
   `2026-08-17-creative-conservative-sampling-by-openrouter-model.md:34`, even
   Inkling's `max` reasoning effort does not beat default `high` on the
   WebBrain planner benchmark (2026-07-23).
3. **Two-model tilted-sampling is more expensive than 4-role RCAF for
   comparable or worse signal.** Tilted sampling on a single model gives
   surface-phrasing diversity; the four roles (haru/natsu/aki/fuyu) give
   structural diversity at the same or lower cost.

The new design captures the lessons:

- Use **4 prompt-conditioned roles** (one per season) for structural
  diversity.
- Use **4 different model families** for inductive-bias diversity.
- Use **`variant: low`** on all research subagents to bound cost.
- Use **one verifier (shiki) on a frontier model** to absorb the cheap
  research and produce one consolidated report.
- Make the verifier **mandatory when ≥2 research subagents ran** to keep
  noise out of the main agent's context.

## 11. Resolution status (2026-08-25)

Items resolved this turn (commits on shared-context `main`):
- **§4 model picks** — RESOLVED (commit `76f8a57`). Original lock:
  haru=gemma-4-31b-it, natsu=mimo-v2.5, aki=deepseek-v4-flash-0731,
  fuyu=glm-4.7-flash, shiki=minimax-m3. 4 distinct families.
  **Superseded 2026-08-25 by §11.2 deviation log** (commit `93c6b26`):
  haru swapped to gemini-2.5-flash-lite for cache-read support.
- **§4.1 benchmark snapshot** — RESOLVED (commit `8c04206`). AA scores
  captured; only AA has substantive data for the 4 survivors. **AA
  re-fetch required for haru (now gemini-2.5-flash-lite).**
- **§4.2 `variant: low` exposure** — RESOLVED (commit `8c04206`). aki
  honours low effort; natsu/fuyu silently drop (boolean-toggle branch);
  haru likely honours via OpenRouter envelope (verify — Gemini does
  not advertise `reasoning_effort` per its `supported_parameters`).
- **§8 output format + subagent-runs dir** — RESOLVED (commit `5d6fd6f`).
  Files at `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>[-<topic>].yaml`
  (e.g. `20260826_113348-haru.yaml`, `20260826_113348-shiki.yaml`;
  computed with `date +%Y%m%d_%H%M%S`). Dir ignored via
  `.tmp/docs/.gitignore` so reports don't pollute shared-context history.
  **Filename rename 2026-08-26** (commit pending) replaced the
  earlier `<role>-<ts>.yaml` pattern (`<ts>` had been ISO-style in the
  reference and unix-style in the body) with a single
  `YYYYMMDD_HHMMss-<role>[-<topic>].yaml` form. See plan
  `.tmp/docs/plans/2026-08-26-subagent-runs-rename.md` for the rationale.
- **§3.1-3.5 role bodies** — RESOLVED. The 5 subagent files have been
  authored and **deployed as global config via chezmoi** at
  `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`
  (chezmoi source) → `~/.config/kilo/agent/` (deployed). The `exact_`
  prefix lets chezmoi create the `agent/` dir verbatim without
  mangling. Each file embeds the full role body from §3 plus the §6
  permission block and §6.1 discipline preamble.

Items with implicit defaults (carried over; user can override per-role
in the authored files):
- **§5.1 random selection** — implicit, logged in shiki provenance.
- **§5.2 sequential chain** — off by default; on for security/correctness.
- **§3.5 verifier deep-verify scope** — websearch + read-only filesystem;
  no `gh` until requested.

Items still pending (user-deferred):
- **Item I** — commit the deferred `dot_config/kilo/kilo.jsonc` provider-
  pinning edits (52 insertions, 4 deletions) to the chezmoi source repo.
  Per the user's "commit later, after this plan finishes" instruction.
  Working tree has 1 modified file as of this plan update.
- **§9 validation checklist** — not yet executed. Re-run after the
  `kilo.jsonc` commit:
  1. `kilo agent list` confirms all 5 subagents load.
  2. `kilo agent list --json` shows `permission.task: deny` on all 5.
  3. Subagent isolation — verify parent's edit/bash doesn't leak.
  4. Per-model smoke test with N=4 (haru + natsu + aki + fuyu).
  5. Cost ceiling: N=4 + shiki stays within budget.
  6. Determinism: seeded random captures seed in shiki provenance.

### Optimizations from 2026-08-25 live simulation run

The pinentry-simulation live run (worktree
`/tmp/kilo/sim`, commit `cd9e791` in shared-context) cost **$0.08 for
4 research subagents** (shiki ran BYOK). Per §4 picks this is
well under the §9 budget ceiling. Six optimizations applied
2026-08-25:

- **§5.0 task-prompt budget (item 1):** main-agent `task` prompt
  must be ≤ 15 lines. The agent body already contains role,
  output contract, anti-patterns, and discipline preamble — do not
  duplicate them in the task prompt. Observed 30% token savings on
  the live run.
- **§5.0a operational gotchas (item 5):** documented the two
  operational gotchas (subagent working-directory drift; shiki
  permission inheritance) with fixes in each agent body and the
  §6 notes.
- **§6 permission block note (item 3):** explicit rule that the
  block is the source of truth and must not be re-declared in the
  task prompt.
- **fuyu rubric pruning (item 2):** new rule in fuyu's body —
  "When the top-2 candidates are within 0.05 on all criteria, the
  problem may not have a meaningful ranking; surface in
  open_questions_for_main_agent rather than forcing a total."
- **aki anti-anchoring discipline (item 6):** new "Anti-anchoring
  discipline" section in aki's body — predictions are prior work to
  audit, not targets to match; host evidence beats upstream docs;
  drop stated-not-hidden assumptions; add new ones if found.
- **Working-directory hint in all 5 agent bodies (item 4):** each
  agent body now states a "Working directory" note that defaults
  to `$(git rev-parse --show-toplevel)/.tmp/docs/subagent-runs/`
  from `$PWD` when the task prompt omits an explicit working
  directory. Worktree-resident runs no longer pollute the live
  repo's gitignored `subagent-runs/` directory.

The 6 optimizations above are pre-approved by the user. The
optimizations **do not change model picks, role boundaries, or
permission rules** — they tighten signal-per-token without altering
the §4 cohort, the §3 role definitions, or the §6 permission block.

### 11.2 haru model swap 2026-08-25 (post-lock deviation)

After the §4 picks were locked, observation of the live pinentry-
simulation run showed haru's `google/gemma-4-31b-it` routes returning
**0% cache-read ratio** on OpenRouter (chutes/fp4, friendli,
deepinfra/turbo do not surface prompt-cache billing for that model).
Since haru may be spawned multiple times in a single session with
similar prompts (the adversarial role is the first fan-out call and
often the cheapest to repeat), prompt-cache support is a load-bearing
property.

**Deviation:** haru swapped from `google/gemma-4-31b-it` to
`google/gemini-2.5-flash-lite`. New `kilo.jsonc` provider pin:
`google-ai-studio/flex → google-ai-studio → google`. Cheapest route
is `google-ai-studio/flex` at $0.05/M in / $0.20/M out / $0.005/M
cache_read (90% discount on cached input tokens), uptime 99.0%.

**Trade-offs accepted:**
- Family shift: Google / Gemma → Google / **Gemini** (same parent
  company, different architecture family). The 4-distinct-family
  property weakens slightly — still Google, but Gemini is
  architecturally distinct from Gemma.
- `variant: low` honour unverified at swap time. Gemini 2.5 Flash
  Lite's `supported_parameters` does not advertise `reasoning_effort`;
  OpenRouter envelope likely applies per §4.2. **Verify per session
  with `kilo provider list --json`.**
- AA benchmark scores pending re-fetch (the `/benchmarks` endpoint
  returned 401 without cookie auth on 2026-08-25). Public-domain AA
  data for Gemini 2.5 Flash Lite is typically intel ~50, coding ~55,
  agentic ~30 — substantially higher than Gemma 4 31B IT (29.7 / 43.4
  / 14.4) per public benchmarks, but the snapshot at AA's slug
  `gemini-2.5-flash-lite-...` must be re-fetched to confirm.

**Files updated:**
- `dot_config/kilo/exact_agent/haru.md` — frontmatter `model:`,
  body §"Variant exposure (Gemini 2.5 Flash Lite)", body §"Cache
  reads (the reason for this model)".
- `dot_config/kilo/kilo.jsonc` — `google/gemini-2.5-flash-lite`
  provider pin order updated to include `google-ai-studio/flex`
  first.
- `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` —
  §4 model table, §4.1 benchmark snapshot, §4.2 variant exposure,
  this §11.2 deviation log.

**Re-verify before next lock review:**
1. AA benchmark scores for `gemini-2.5-flash-lite` slug.
2. `variant: low` honour via `kilo provider list --json`.
3. Cache-read ratio on repeated haru prompts in a single session.

## 12. Recommended destination

This plan is the canonical draft for the 5-subagent fleet.

**Authoritative home for the 5 subagent files:** chezmoi-deployed global
config under `dot_config/kilo/exact_agent/` (chezmoi source) →
`~/.config/kilo/agent/` (live). The 5 files travel through two renames:

1. English role names (`research-{adversarial,synthesizer,…,verifier}.md`).
2. **Japanese four-seasons rename** on 2026-08-25 per user instruction:
   `haru` (春 adversarial) / `natsu` (夏 synthesizer) / `aki`
   (秋 assumption-auditor) / `fuyu` (冬 comparator) / `shiki` (四季
   verifier). The seasonal names pair naturally with the four-prompt-
   conditioned RCAF roles in §3, and `shiki` ("four seasons") names
   the verifier because it spans the four seasonal research subagents.

**Maintainer README:** a `README.md` lives in `dot_config/kilo/exact_agent/`
next to the 5 files documenting the fleet for humans (purpose, naming,
invocation patterns, customisation knobs, operational notes). The
project-level `.chezmoiignore` has `**/README.md`, so the README stays
**source-only** — readers see it when working in the chezmoi repo, not
in the deployed `~/.config/kilo/agent/`. If we ever want it deployed we
can add a chezmoi `!dot_config/kilo/exact_agent/README.md` unignore rule,
but that overrides a deliberate project policy for one file, so keeping
it source-only is the safer default.

Other planned destinations noted but not used:
- `.agents/kilo/agent/...` (project-scoped) — superseded by the move above.
- Project-layer cache for the design rationale:
  `.agents/docs/cache/kilo-subagents/` (read-only knowledge cache, holds
  the per-model sampling matrix, the permission precedence notes, etc.)

## 13. Related entries

- `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md` —
  Kilo's sampling-parameter flow at v7.4.22 (the source-of-truth for what
  Kilo actually accepts).
- `.agents/docs/cache/kilo-subagents/2026-08-17-creative-conservative-sampling-by-openrouter-model.md`
  — per-model `supported_parameters` matrix for the candidate model families.
- `.agents/docs/cache/kilo-subagents/2026-08-15-reasoning-variants-by-provider.md`
  — per-provider effort tables; use `variant:` for reasoning effort, not
  `temperature`.
- `.agents/docs/cache/kilo-subagents/2026-08-15-best-practices.md` — subagent
  design heuristics (read-only default, `hidden: true` for internal helpers,
  `steps` cap for cost safety).
- `.agents/docs/cache/kilo-subagents/2026-08-15-subagent-delegation-inheritance.md`
  — parent → child permission flow (subagents are denied `task`, `question`,
  `suggest`, `interactive_terminal`).
- `.agents/docs/cache/kilo-subagents/2026-08-15-agent-frontmatter-reference.md`
  — full frontmatter field table.
- `.agents/docs/cache/kilo-subagents/2026-08-15-agent-config-precedence.md` —
  merge order (built-in → global JSON → project JSON → global `.md` →
  project `.md` → env overrides); per-field override semantics
  (concatenation for `permission`, deep-merge for `options`, replace with
  `null` delete sentinel for the rest).