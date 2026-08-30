---
name: subagent-fleet-reevaluate-models
description: >
  Re-pull the OpenRouter catalog, filter for fleet eligibility (pricing +
  cache_read + real-time + parameter support), run an optional benchmark
  cross-check against OpenRouter's `benchmarks` field and Hugging Face
  model cards, propose Mix A (lowest cost) and Mix B (more diverse) 4-family
  picks for haru/natsu/aki/fuyu, write a dated report to
  `.agents/docs/cache/openrouter/`, and after user pick, update the four
  `dot_config/kilo/exact_agent/*.md` `model:` lines via chezmoi. Invoke
  when the OpenRouter catalog has shifted (model ids, prices, or training
  posture), when current subagent picks feel stale, when the user says
  "re-evaluate fleet models" or "refresh subagent picks", or after any
  change to the plan §4 eligibility rules.
mode: workflow
---

# Subagent Fleet — Re-evaluate Model Picks

Recurrent task: pick 4 model-family-distinct, real-time, cache-eligible
OpenRouter models for the haru/natsu/aki/fuyu research subagents. This
command is the callable entry point.

## Source of truth (single source for eligibility + decision rule)

All eligibility rules, role-dependent quality thresholds, and the
phase-cascade decision rule live in
`docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
**§4.0** (Eligibility + decision rule). This workflow does **not**
duplicate the rule definitions inline — Step 2 / Step 4 below read
§4.0 dynamically so any rule added to §4.0 (R6, R7, future R8+, or
Phase 5+) propagates without re-editing this command file.

§4 (the locked-picks table) and §11 (subagent file locations) are
the secondary references used only in Step 6 (write report — frontmatter)
and Step 8 (apply — file paths).

When the canonical plan is not reachable (e.g., another project using
the bundled skill references), fall back to
`.agents/kilo/skills/subagent-fleet/references/model-picks.md`
bundled snapshot (stale past 2026-08-25 — explicitly note the fallback
in the report's Uncertainty section).

## Why this command exists

OpenRouter's catalog shifts weekly. Manually repeating the 2026-08-23
filter process every time costs turns and risk of drift. This workflow
encodes the filter as code so each run is reproducible and the diff
between runs is auditable in the dated report.

This is a **state-mutating** command — it overwrites `model:` lines in
chezmoi-managed files. The confirmation step (Step 7) and the
`chezmoi diff` preview (Step 8) exist precisely because of that.

## User input

**Always** parse `$ARGUMENTS` before proceeding. If the user supplied
flags or prose, they override the defaults below — and the flag-driven
defaults below already encode them. If user input conflicts with the
filter rules in Step 2, prefer user input and flag the discrepancy
in the report's `Uncertainty` section before drafting.

```text
$ARGUMENTS
```

Supported flags (case-sensitive):

- `--pick <mix-id>` — skip Step 7 and apply that mix directly. Only
  use when the user has already approved a mix out of band.
- `--no-bench` — skip Step 2½ (benchmark cross-check).
- `--allow-batch` — include `:batch` endpoints (violates the
  real-time constraint, see Step 2).
- `--cache-r-max-ratio <0..1>` — override the default `0.2` cap.
- `--skip-provider-pin` — skip Step 9 (provider pinning into
  `dot_config/kilo/kilo.jsonc`). Step 8's `model:` line apply still
  runs.
- `--provider-uptime-min <0..1>` — override the default `0.99`
  uptime floor used in Step 9.

Anything else in `$ARGUMENTS` is treated as free-form context (the
"why this revaluation is needed" line), surfaced verbatim into the
report's `Scope` section.

## Inputs

- **Trigger phrases:** "re-evaluate fleet models", "refresh subagent
  picks", "openrouter catalog changed", "renew fleet picks", or any
  mention of stale/expensive subagent models.
- **Optional inputs** at invocation:
  - `--pick <mix-id>` — skip Step 7 and apply that mix directly.
    Use only when the user has already approved a mix out of band.
  - `--no-bench` — skip Step 2½ (benchmark cross-check).
  - `--allow-batch` — include `:batch` endpoints (violates the
    real-time constraint, see Step 2).
  - `--cache-r-max-ratio <0..1>` — override the default `0.5` cap.
- **Required context the user supplies each run:**
  - Why the revaluation is needed (catalog drift, new family surfaced,
    budget change, training-posture change, etc.).
  - Approval of the picked mix before Step 8 applies anything.

## Outputs

- **Report:** `.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-revaluation.md`
  (cache convention: `.agents/docs/cache/README.md`). Never append to an
  older report.
- **Memory pointer:** `kilo_memory_save` with the report path + picked
  mix ids. Facts live in the report, not memory.
- **Chezmoi edits:** `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu}.md`
  `model:` lines replaced. Diff pre-applied; user approves; `chezmoi
  apply` only on confirmation.
- **Kilo provider pinning:** `dot_config/kilo/kilo.jsonc`
  `provider.openrouter.models` block gets the top-3 cheapest-with-good-
  uptime provider `order` lists added or refreshed for each picked
  model. Diff pre-applied; user approves; `chezmoi apply` only on
  confirmation.
- **Shared-context commits:** one after the report (Step 6), one after
  the apply (Step 8). Both run via `kilo-shared save "<message>"`.

## Pre-flight

1. Confirm the rule the user wants this run to enforce. Default rules
   (Step 2 below, sourced from plan §4.0). If the user supplied
   `--cache-r-max-ratio` or other flag, fold it in.
2. Load the `openrouter-api` skill if not already loaded — the catalog
   endpoints, the per-model `supported_parameters` shape, and the
   `/endpoints/zdr` route live there.
3. Re-read `references/model-picks.md` from the `subagent-fleet` skill
   (in `.agents/kilo/skills/subagent-fleet/references/`). Compare to
   what the catalog will say — that's the delta the report needs to
   cover.
4. **Re-read plan §4.0** at
   `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
   §4.0 (Eligibility + decision rule) to capture the current rule set
   (R1-Rn) and Phase 1-4 cascade. The `filter_revision` field in the
   report must reflect the §4.0 version read — if §4.0 was edited
   since the previous revaluation, bump `filter_revision` and note the
   diff in the report's Scope section.

## Steps

### Step 1 — Pull the catalog

- `GET openrouter://api/v1/models` — full list. Note response header
  `X-OpenRouter-Updated-At` (or the body field if present). If no
  updated-at indicator, store the request timestamp as a fallback.
- `GET openrouter://api/v1/providers` — capture each provider's
  `privacy_policy_url`, `slug`, and `name`. Used in Step 5.
- `GET openrouter://api/v1/endpoints/zdr` only when the user wants a
  ZDR filter.
- Store both responses in the report's Evidence section.

**Staleness guard.** If `X-OpenRouter-Updated-At` (or cache freshness
from any other recent catalog pull) is more than 7 days old, stop and
ask the user via `question`: "Catalog is N days old — proceed anyway
with stale data, or wait for a fresh pull?" The guard is a sanity check,
not a refusal; an explicit yes allows continuing.

### Step 2 — Apply the eligibility filter

Apply **every rule listed in plan §4.0** (R1, R2, ..., Rn as defined
at the time of this run). Reject any model where **any** rule fires.
Lower-case ids before matching the suffix rules.

§4.0 is the single source of truth for the rule definitions, the
default thresholds, and the role-dependent overrides (e.g., R7 may
have per-slot thresholds that differ from the default). Do **not**
hard-code the rule values here — read §4.0 at run time.

If §4.0 is not reachable, fall back to
`.agents/kilo/skills/subagent-fleet/references/model-picks.md`
bundled snapshot (stale past 2026-08-25 — note the fallback in the
report's Uncertainty section and **stop**, do not invent rules from
training data).

The user-definable knobs at invocation change §4.0 defaults only as
documented; rule definitions and ordering come from §4.0:

- `--no-bench`: leaves §4.0 unchanged (benchmarks are not in §4.0 —
  they're a Step 2½ cross-check).
- `--allow-batch`: drops the **Real-time routes only** rule for
  `:batch` endpoints only. Keeps the other §4.0 rules. Mark each
  survivor in the report with `latency_profile: batch-24h`.
- `--cache-r-max-ratio <x>`: replaces the `0.5` in the cache read
  ratio rule with `<x>`. Caller is responsible for noting why.
- `--provider-uptime-min <x>`: replaces the `0.99` uptime floor in
  Step 9 with `<x>`. Lowering below `0.95` is discouraged and the
  report must flag it.

Print the **filter revision string** at the top of the report,
formatted as `"<plan-§4.0-version>-<flag-summary>"`. The plan-§4.0-
version is the date of the §4.0 section last-updated field (or the
plan frontmatter `last-updated` if §4.0 has no per-section date).
Example: `filter_revision: "default-2026-08-30"` or
`filter_revision: "2026-08-30-with-cache-r-ratio-0.7"`. New rule
changes belong in §4.0 — bump §4.0's `last-updated`, not this file.

**Quality floor is non-negotiable.** R7 (the AA intelligence index
floor per role) drops a survivor from the mix at any cost. A cheap
model that fails R7 cannot be picked, cannot be carried into Mix B,
and cannot be saved by a provider-pinning override. If a model is
cheap enough to matter, that is a signal to raise the R7 floor, not
to lower it. The user-facing principle: a subagent that returns
confident-but-wrong output wastes more downstream cost than it
saves on input tokens.

### Step 2½ — OPTIONAL: Benchmark cross-check

Skip if `--no-bench` was passed, or if the user didn't ask for the
benchmark pass. The default is **off** — opt in by saying "include
benchmark check" at invocation or by accepting the Step-3 prompt that
mentions it.

When enabled:

1. For each survivor from Step 2, look up `GET
   openrouter://api/v1/models/{id}`. If the response has a `benchmarks`
   field (object with per-skill scores), record it as `bench_score` and
   `bench_verified: true`. Missing field is `?` not inferred.
2. For any survivor where `benchmarks` is missing, sparse, or stale,
   fetch the model's Hugging Face card at
   `https://huggingface.co/{org}/{repo}` via `webfetch`. Extract:
   parameter count, license, the "Use cases" bullets, evaluation-table
   cells if present. Inline as `hf_card_excerpt`. Mark
   `bench_verified: true` only if the card has eval tables; otherwise
   `bench_verified: false`.
3. Don't invent scores. Empty benchmarks plus empty HF card → leave
   `bench_score: null` and `bench_verified: false`. Absence of a
   benchmark is data; report it.
4. Add a **Step 2½ — Benchmark pass** sub-section to the report
   *between* **Eligibility rules applied** and **Candidates table**.
   One line per survivor: `id | bench_verified | bench_score source
   (openrouter|hf_card|null) | hf_card_excerpt (≤ 200 chars)`.

Step 4 (next) reads `bench_verified` from this section.

### Step 3 — Score by family diversity

1. Bucket survivors by `model.id` family: everything before the first
   `/` (`deepseek/deepseek-v4-flash` → `deepseek`). Family names are
   the provider/author prefix; treat case-insensitively.
2. Within each bucket, sort by `pricing.completion` ascending.
3. Take the **top 3** of each bucket for the **Candidates table**.
4. The full survivor list goes into a per-bucket tail in the report
   (collapsed markdown list — no inline tables for > 3 rows per
   family).

Captured data per survivor (one row per family):

| Field | Source |
|---|---|
| id | `model.id` |
| family | pre-slash prefix |
| best provider | cheapest `pricing.completion` row of the `endpoints[]` |
| $/M in | `pricing.prompt × 1e6` |
| $/M out | `pricing.completion × 1e6` |
| $/M cache_r | `pricing.input_cache_read × 1e6` |
| $/M cache_w | `pricing.input_cache_write × 1e6` (or `—` if absent) |
| ctx | `top_provider.context_length` or `model.context_length` |
| T/Tb/R | `temperature` / `tools` / `reasoning` accepted on cheapest route |
| bench_score | from Step 2½; `?` if `bench_verified: false` |
| training-risk | from Step 5 (filled after Step 5 finishes) |

### Step 4 — Compose Mix A and Mix B

Apply **the Phase 1-4 cascade defined in plan §4.0** (Quality →
Diversity → Cost → Training-risk). §4.0 is authoritative for the
phase ordering, the per-phase gates, and the per-slot R7 thresholds.
Do **not** hard-code the cascade here — read §4.0 at run time.

§4.0 produces **one canonical mix** (the 4-family pick after Phase 1-4).
This workflow's Step 4 surfaces that mix as **Mix A** so the user
sees a stable label across revaluations, and additionally proposes
**Mix B** as a workflow-side carve-out (not part of §4.0) for users
who want to explore a non-flash R2 option before the next §4.0
revision captures it.

**Mix A — §4.0 cascade output.** Run §4.0's Phase 1-4 cascade over
the Step 2 survivors. The cascade produces 4 distinct families, one
per slot (haru/natsu/aki/fuyu), with quality/diversity/cost/training
gates applied in order. Slot labels: R1 = haru, R2 = natsu, R3 = aki,
R4 = fuyu. If fewer than 4 families survive, drop Mix A and explain
in the report's Scope section.

**Mix B — workflow-side non-flash carve-out (optional).** Same
R1-R4 assignment as Mix A but with this single carve-out: **R2 =
natsu** gets the cheapest coding- or reasoning-tuned non-flash
survivor in the cheapest family (instead of the cheapest survivor).
If any family surfaced by Step 3 was not present in the prior report,
that family gets a slot in Mix B — prefer it over repeating an
existing slot. Drop Mix B if its R2 price exceeds the user's per-run
ceiling (default: same as the §4.0 eligibility cap on output price).

**Tie-break precedence** when two survivors tie on the §4.0 sort key:
1. If Step 2½ ran and both have `bench_verified: true` → use the higher
   `bench_score` *only for R1 and R2*. R3 and R4 stay on the §4.0 sort
   key.
2. §4.0's secondary tie-breaks (typically: lower cache_read, longer
   context, family not used yet alphabetical) — read §4.0 to confirm
   the current ordering before applying.

Record Mix A as a full table in the report — same column shape as the
table in §4.0 (id, family, `/M in`, `/M out`, `/M cache_r`, `/M
cache_w`, ctx, T/Tb/R, training-risk, bench_score, why). If Mix B
is rendered, use the same column shape.

### Step 5 — Training-risk pass

For each survivor in Mix A and Mix B's tables:

1. Find the cheapest-provider row from Step 2's `endpoints[]`.
2. Match that provider's `name`/`slug` against `GET
   openrouter://api/v1/providers` from Step 1.
3. Read the matched provider's `privacy_policy_url`.
4. Mark inline:
   - ✅ when the policy explicitly states **no training on prompts**
     (e.g., MiniMax).
   - ⚠ when the policy says opt-in / opt-out / unclear / unknown.
   - ❌ when the policy explicitly states **training on prompts** by
     default. Survivors marked ❌ are demoted: include them in the
     report but exclude from Mix A and Mix B.
5. The user retains `❌` survivors only via explicit `custom` pick in
   Step 7.

Inline the privacy-policy URL for every marker. This satisfies the
"may-train is acceptable but mark it" constraint from the
2026-08-23 note's audit pass.

### Step 6 — Write the report

Create a fresh file at
`.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-revaluation.md`.
**Do not** append to or modify
`.tmp/docs/notes/2026-08-23-subagent-flash-model-picks.md` or any prior
report.

**Frontmatter:**

```yaml
---
title: OpenRouter fleet-revaluation (mix draft)
date: YYYY-MM-DD
task-slug: subagent-fleet-revaluate-models
related:
  - docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md
  - .agents/kilo/skills/subagent-fleet/SKILL.md
  - ~/.config/kilo/skills/openrouter-api/SKILL.md
openrouter_updated_at: <from Step 1 header>
filter_revision: <from Step 2>
candidates_count: <survivor count from Step 2>
mixes_proposed: ["A", "B"]
picked_mix: null
applied_at: null
status: pending-user-pick
provider_pin_status: null
provider_pin: null
provider_pin_strategy: null
---
```

**Body sections, in this order:**

1. **Scope** — what changed since the last revaluation (1-3 lines).
2. **Filter (this run)** — list every rule from Step 2 verbatim and
   the value of any flag that overrode a default.
3. **Eligibility rules applied** — restate the rules. No edits.
4. **Step 2½ — Benchmark pass** (omit entirely if the step was
   skipped) — copy from Step 2½ output 4.
5. **Candidates table** — top-3-per-family survivors only. Full tail
   collapsed under each family heading.
6. **Recommended 4-family mix A** — table from Step 4.
7. **Recommended 4-family mix B** (omit if no R2 carve-out applied)
   — table from Step 4.
8. **What you still need to decide** — copy forward open items from
   prior revaluations that don't block this pick (role refinements,
   random-selection strategy, verifier scope, output format).
9. **Evidence** — paths/URLs of everything fetched (Step 1 endpoints,
   HF card URLs for any survivor that needed it, the current subagent
   model lines for diff context).
10. **Step 9 — Provider pin** (omit if `--skip-provider-pin` was
    passed or step was skipped) — per-model pinned-provider tables.
11. **Uncertainty / re-verify** — anything ⚠ in training-risk, anything
    missing in bench_score, anything else not closed.
12. **Recommended destination** — once a mix is applied, refresh the
    §4 locked-picks table with the chosen rows (or note the post-
    cascade pick in §11 if §4 itself was not updated by this
    revaluation). The §4.0 eligibility + decision rule is the
    source of truth and should **not** be edited by this revaluation
    unless a new rule was discovered — in which case edit §4.0 first
    and bump its `last-updated`, then re-run this command.
13. **Date captured** — ISO date, for staleness tracking.

After writing the file, commit via `kilo-shared save "checkpoint:
revaluation report: YYYY-MM-DD"`.

### Step 7 — Surface to the user

Use the `question` tool with exactly these 4 options:

1. **Adopt Mix A** (Recommended, first) — apply Mix A.
2. **Adopt Mix B** — apply Mix B.
3. **Keep current picks** — stop here, write a no-op report update
   (set `picked_mix: null`, `status: declined`), commit.
4. **Custom** — user supplies their own per-slot assignment.
   The Type-your-own-answer input is enabled by default; no extra
   options needed.

Do not edit any subagent file until the user picks 1, 2, or 4. If the
user picks option 3, jump to Step 11 without touching subagent files.

### Step 8 — Apply the pick (after user picks 1, 2, or 4)

1. For each of the four files
   `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu}.md`:
   - Locate the `model:` line in the frontmatter.
   - Replace its value with the picked id. Preserve the `model: ` key,
     leading whitespace, and trailing newline.
   - Use `edit`, not `write`, so the rest of the file is unchanged.
2. Run `chezmoi diff` against the chezmoi-managed copy of those four
   files (`chezmoi diff` from the source root). Verify the diff shows
   exactly the four `model:` lines changing — nothing else.
3. Show the user the diff. **Stop and wait** for explicit confirmation.
4. Only after the user confirms: `chezmoi apply`. Re-run `chezmoi diff`
   to confirm the diff is now empty (managed targets match source).
5. Update the report frontmatter:
   - `picked_mix: "A"` or `"B"` or `"custom"`
   - `applied_at: <ISO timestamp>`
   - `status: applied`
6. Commit via `kilo-shared save "checkpoint: applied {picked_mix}
   YYYY-MM-DD"`.

### Step 9 — Pin top-3 providers in `kilo.jsonc`

Each picked model can route to several OpenRouter providers. The
fleet runs many cheap, latency-sensitive calls per day, so the cheapest
route on paper is not always the cheapest in practice — a flaky
provider inflates retries, burns cache budget, and stalls subagent
turns. This step pins the top-3 providers per picked model into
`dot_config/kilo/kilo.jsonc` `provider.openrouter.models.<id>.options.provider.order`,
ordered cheapest-with-good-uptime first, so Kilo falls over to the next
provider on the first 429/5xx instead of round-tripping through every
endpoint.

Skip if `--skip-provider-pin` was passed.

**Eligibility rules for a pinned provider:**

| Rule | Condition |
|---|---|
| Cheapest candidates | include any provider where `endpoints[]` for this model lists it |
| Uptime floor | provider's published uptime / availability ≥ `--provider-uptime-min` (default `0.99`) over the last 30 days |
| Capability floor | provider's `endpoints[].supported_parameters` includes both `temperature` and `tools` (mirrors Step 2 rule) |
| ZDR preference | when two providers tie on uptime, prefer the one marked ZDR (Zero Data Retention) in `/endpoints/zdr` |
| Sort key | primary: `pricing.completion` ascending; secondary: uptime descending; tertiary: alphabetical |

The user-definable knob at invocation:

- `--provider-uptime-min <x>`: replaces the `0.99` floor with `<x>`.
  Lowering below `0.95` is discouraged and the report must flag it.

If a model has only one eligible provider (no fallback exists), set
`allow_fallbacks: false` for that entry instead of fabricating a list.
Do not pad with a higher-priced or low-uptime provider just to reach
length 3.

**Process:**

1. For each of the 4 picked models, fetch `GET
   openrouter://api/v1/models/{id}` and read the `endpoints[]` array.
   Pull each provider's `name`, `pricing.completion`, and any
   per-endpoint uptime / availability / `supported_parameters` fields
   the API exposes. (If the catalog surface does not expose per-provider
   uptime, fall back to the provider-level uptime from `GET
   openrouter://api/v1/providers`; if neither is available, mark the
   missing field `?` and proceed without the floor for that provider
   only — flag it in the report.)
2. Apply the eligibility table. Drop providers that fail any rule.
   Record survivors as `{provider_slug, $/M_out, uptime_source,
   uptime_value, zdr: bool}`.
3. Sort survivors by the sort key. Take the top 3 (or fewer if < 3
   survivors remain).
4. For each of the 4 models, render a `kilo.jsonc` patch that adds or
   replaces the `provider.openrouter.models.<id>.options.provider`
   block with:
   ```jsonc
   {
     "options": {
       "provider": {
         "order": ["<cheapest-uptime-1>", "<cheapest-uptime-2>", "<cheapest-uptime-3>"],
         "allow_fallbacks": true
       },
     },
   }
   ```
   Use `allow_fallbacks: false` when fewer than 2 survivors were found.
5. `chezmoi diff dot_config/kilo/kilo.jsonc` to preview. Verify only
   the 4 `provider.openrouter.models.<id>.options.provider.order`
   blocks (and their `allow_fallbacks` flags) are changing — never
   touch `apiKey`, MCP blocks, `indexing`, or any sibling field.
6. Show the diff to the user. **Stop and wait** for explicit
   confirmation. The provider pin is committed-by-apply, just like the
   `model:` line apply; never auto-apply.
7. On confirmation: `chezmoi apply`. Re-run `chezmoi diff` to confirm
   the diff is now empty for `kilo.jsonc`.
8. Update the report frontmatter:
   - `provider_pin_status: applied | applied-with-failures | skipped`
   - `provider_pin: { "<model-id>": ["<p1>", "<p2>", "<p3>"], ... }`
9. Add a **Step 9 — Provider pin** section to the report body (after
   the **Evidence** section, before **Uncertainty**) with one table
   per picked model: columns `provider | $/M out | uptime | uptime
   source | zdr | picked_position`.
10. Commit via `kilo-shared save "checkpoint: provider pin
    YYYY-MM-DD"`.

**Failure handling.** If the catalog surface has no per-provider
uptime for any of the 4 models, surface the gap to the user via
`question` before proceeding: "OpenRouter does not expose uptime for
these models in this catalog pull — pin by price alone, or wait for a
later catalog version that exposes uptime?" The user must pick one.
The chosen path is recorded in `provider_pin_strategy` frontmatter
field with one of `price-only` / `uptime-pending`.

### Step 10 — Verify

For each of the four subagents, run one cheap probe via the `task`
tool with the picked model and a sentinel prompt: "Reply with only
the word 'ok' and no other text." Confirm the response is parseable
and matches. Capture the probe prompt + first 80 chars of the
response into the report's **Step 10 — Verification** section. If any
probe fails:

1. Revert that subagent's `model:` line to the prior id using `chezmoi
   diff -reverse` + `chezmoi apply` (one subagent at a time).
2. Set the report's `status: applied-with-failures`, note which slot
   and the probe error.
3. Re-open the report for the user — do **not** re-apply.

### Step 11 — Memory pointer

`kilo_memory_save` with the *short* pointer only:

```
key: kilo.fleet.last_model_revaluation
text: Fleet model revaluation {YYYY-MM-DD} picked {mix-A|mix-B|custom};
  report: .agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-revaluation.md;
  provider_pin: {applied|skipped|applied-with-failures}
```

No facts in the memory record — the report is the canonical store.
One memory entry per revaluation, never overwrite (each date becomes
its own entry in the catalog).

## Pre-flight that runs every step

- `chezmoi --version` ≥ 2.70.4 (project requirement).
- `kilo-shared save` available; if not, fall back to `git -C
  .tmp/docs/ commit -m "..."` and note the fallback in the report.
- The `kilo-shared` wrapper is at `~/.local/share/kilo/bin/`; if
  missing, skip the commit and warn.

## Anti-patterns

- **Appending to the 2026-08-23 note.** That note is a finished
  research record. New runs always emit a new dated report.
- **Editing `model:` without the `chezmoi diff` preview.** The user
  has been bitten by surprise writes before.
- **Picking a mix without a cache_read ratio check.** A survivor that
  fits Step 2's `≤ 0.5×` rule one week may slip above the cap the next;
  the Step 2 filter must re-run, even when only `pricing.prompt`
  changed.
- **Skipping Step 2½ silently.** If the user said "include benchmark
  check", run it or stop and surface why (e.g., all catalog rows had
  empty `benchmarks` *and* all HF card fetches failed).
- **Treating ❌ training-risk survivors as pickable.** Step 5 demotes
  them — the user has to opt back in via the custom path with an
  explicit reason.
- **Inferring `bench_score` from model size or family reputation.**
  Empty is data, not a default.
- **Mix A and Mix B picking from overlapping subagent slots.** Mix B
  must be **strictly** more diverse than Mix A on families or
  capability tilt, never a relabel.
- **Committing the report without `kilo-shared save`.** Per the
  shared-context rule, an uncommitted report is in-flight and may be
  lost on worktree destroy.
- **Pinning providers without an uptime check.** Sorting by
  `pricing.completion` alone is the cheapest-in-name-only path; the
  2026-08-26 natsu smoke run showed that the lowest-cost provider
  (parasail/fp8) was the most rate-limited in practice. The 0.99
  uptime floor in Step 9 exists for that reason.
- **Pinning more than 3 providers.** A 3-deep list is the budget;
  deeper lists dilute the cost signal and increase the chance a
  fallback to a low-quality route is taken. Add a 4th only when the
  user names it explicitly.
- **Reordering existing `order:` blocks that were set by hand for a
  reason.** Many `kilo.jsonc` entries (e.g. `xiaomi/mimo-v2.5`,
  `google/gemini-2.5-flash-lite`) carry a comment explaining the
  ordering; preserve the comment when the new pin is the same as the
  old. If the new pin disagrees with the old, keep the old comment as
  a `// superseded YYYY-MM-DD: <reason>` line above the new `order:`
  so the audit trail survives.
- **Skipping `chezmoi diff` on the `kilo.jsonc` patch.** The
  `kilo.jsonc` file is shared with the main agent and indexing; a
  misordered edit can break the primary session. The diff is the
  only safety net.
- **Pinning a model that did not get picked.** Step 9 only touches
  the 4 picked `model:` ids, never every model block in the file.

## Boundary

- **What this command does:** pulls OpenRouter data, filters, scores,
  proposes 4-family mixes, applies via chezmoi after confirmation,
  and pins the top-3 cheapest-good-uptime providers per picked model
  into `dot_config/kilo/kilo.jsonc`.
- **What this command does NOT do:**
  - Edit role bodies (`.agents/kilo/agent/research-*.md`). Out of
    scope for fleet-revaluation; belongs to plan §3.
  - Change sampling tilt (`temperature` / `top_p`). Belongs to plan
    §4 and only on user request.
  - Re-validate the permission block. Stays in plan §3.5 and
    `references/permission-block.md`.
  - Promote picks back into plan §4 (the locked-picks table).
    That's a separate commit after apply — see Step 11 of the plan.
    **This command does NOT edit §4.0** (the eligibility + decision
    rule); §4.0 is the source of truth and changes to it require a
    separate review pass.
  - Re-pin providers for models that were not picked this run.
    Step 9 only touches the 4 picked ids; legacy `order:` blocks
    for other models are unchanged.

## References

- `~/.config/kilo/skills/openrouter-api/SKILL.md` — OpenRouter REST
  surface, model endpoints, ZDR preview list.
- `.agents/kilo/skills/subagent-fleet/SKILL.md` — fleet role definitions,
  current model picks (`references/model-picks.md`).
- `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
  - **§4.0** (Eligibility + decision rule) — single source of truth for
    eligibility rules (R1-Rn), role-dependent quality thresholds, and
    the Phase 1-4 cascade. **This workflow reads §4.0 dynamically** —
    do not duplicate the rules inline.
  - **§4** (Locked-picks table) — secondary reference; refreshed by
    Step 6 / Step 11 after each revaluation.
  - **§11** (Subagent file locations) — file paths for Step 8 apply.
- `.tmp/docs/notes/2026-08-23-subagent-flash-model-picks.md` — Rev 1
  (flash-class only) + Rev 2 (relaxed filter) research record; basis for
  the default filter rule values.
- `.agents/docs/cache/README.md` — knowledge-cache convention.
- `.agents/docs/cache/kilo-subagents/` — agent frontmatter
  semantics, subagent model resolution rules, sampling parameter
  rejection patterns.
