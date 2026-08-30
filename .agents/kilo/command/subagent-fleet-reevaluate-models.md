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
command is the callable entry point — the canonical source of truth is
the plan `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
§4 (model picks) and §11 (subagent file locations).

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
  - `--cache-r-max-ratio <0..1>` — override the default `0.2` cap.
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
   (Step 2 below). If the user supplied `--cache-r-max-ratio` or other
   flag, fold it in.
2. Load the `openrouter-api` skill if not already loaded — the catalog
   endpoints, the per-model `supported_parameters` shape, and the
   `/endpoints/zdr` route live there.
3. Re-read `references/model-picks.md` from the `subagent-fleet` skill
   (in `.agents/kilo/skills/subagent-fleet/references/`). Compare to
   what the catalog will say — that's the delta the report needs to
   cover.

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

Reject any model where **any** rule fires. Lower-case ids before
matching the suffix rules.

| Rule | Condition |
|---|---|
| Output price | `pricing.completion > $1.1/M` (i.e., `0.0000011` per token) |
| Input price | `pricing.prompt > $0.6/M` (i.e., `0.0000006` per token) |
| Cache read missing | `pricing.input_cache_read` absent, null, empty string, or parses to 0 |
| Cache read ratio | `pricing.input_cache_read > 0.2 × pricing.prompt` |
| Real-time routes only | id matches `:batch`, `:exacto`, or any suffix tagged as deferred |
| Parameter support | cheapest provider route's `supported_parameters` does NOT include both `temperature` and `tools` |

The user-definable knobs at invocation change these:
- `--no-bench`: leaves Step 2 unchanged (it's about eligibility, not
  benchmarking).
- `--allow-batch`: drops the `Real-time routes only` row for `:batch`
  endpoints only. Keeps the other rules. Mark each survivor in the
  report with `latency_profile: batch-24h`.
- `--cache-r-max-ratio <x>`: replaces the `0.2` in the cache read ratio
  rule with `<x>`. Caller is responsible for noting why.

Print the **filter revision string** at the top of the report (e.g.,
`filter_revision: "default-2026-08-30"` or `filter_revision:
"default-with-cache-r-ratio-0.5"`). New rule changes belong in this
field, not as free-form text in the body.

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

Pick 4 distinct families. **Two mixes** are produced so the user can
choose between lowest-cost (Mix A) and more-diverse (Mix B).

**Mix A — strict lowest-cost.** Greedy fill: pick the family whose
cheapest survivor has the lowest `pricing.completion`; mark that
survivor as `R1 = haru` (adversarial). Repeat for `R2 = natsu`
(synthesizer), `R3 = aki` (assumption-auditor), `R4 = fuyu`
(comparator) until 4 distinct families are filled. Stop early if fewer
than 4 families survive — drop the mix and explain in the report.

**Mix B — leverage new families surfaced by the relaxed filter.**
Same R1-R4 assignment rule as Mix A, but with these carve-outs:
- **R2 = natsu** gets the cheapest coding- or reasoning-tuned
  non-flash survivor in the cheapest family (not the cheapest
  survivor).
- If any family surfaced by Step 3 was not present in the prior
  report, that family gets a slot — prefer it over repeating an
  existing slot.
- Drop a mix if Mix B's R2 price exceeds the user's per-run ceiling
  (default: same as the eligibility cap of $1.1/M out).

**Tie-break precedence** when two survivors have identical
`pricing.completion`:
1. If Step 2½ ran and both have `bench_verified: true` → use the higher
   `bench_score` *only for R1 and R2*. R3 and R4 stay on price.
2. Lower `pricing.input_cache_read`.
3. Longer context length.
4. Family not used yet (alphabetical).

Record both mixes as full tables in the report — same column shape as
2026-08-23's note (id, family, `/M in`, `/M out`, `/M cache_r`, `/
M cache_w`, ctx, T/Tb/R, training-risk, bench_score, why).

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
12. **Recommended destination** — once a mix is applied, promote
    the chosen rows into plan §4 and commit the plan update.
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
  fits Step 2's `≤ 0.2×` rule one week may slip above the cap the next;
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
  - Promote picks back into plan §4. That's a separate commit after
    apply — see Step 11 of the plan.
  - Re-pin providers for models that were not picked this run.
    Step 9 only touches the 4 picked ids; legacy `order:` blocks
    for other models are unchanged.

## References

- `~/.config/kilo/skills/openrouter-api/SKILL.md` — OpenRouter REST
  surface, model endpoints, ZDR preview list.
- `.agents/kilo/skills/subagent-fleet/SKILL.md` — fleet role definitions,
  current model picks (`references/model-picks.md`).
- `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` §4 —
  plan §4 model picks; canonical pick record after each revaluation.
- `.tmp/docs/notes/2026-08-23-subagent-flash-model-picks.md` — Rev 1
  (flash-class only) + Rev 2 (relaxed filter) research record; basis for
  the default filter rule values.
- `.agents/docs/cache/README.md` — knowledge-cache convention.
- `.agents/docs/cache/kilo-subagents/` — agent frontmatter
  semantics, subagent model resolution rules, sampling parameter
  rejection patterns.
