---
name: subagent-fleet-empirical-pass
description: >
  Run a per-role speed + cap probe (Phase A) and apply the locked cap
  values via chezmoi (Phase B) in a single workflow for the 4 research
  subagents (haru/natsu/aki/fuyu). Shiki is excluded — model is pinned
  at `openrouter/minimax/minimax-m3` and its cap stays at
  `steps: 40, maxTokens: 16000`. Phase A spawns each role 5× against a
  templated synthetic input, queries OpenRouter `/generation` per call,
  and aggregates latency / cost / `tokens_completion` /
  `native_tokens_reasoning`. Phase B applies the user-policy "conservative"
  cap formula (`steps = ceil(max_measured × 1.5)`,
  `maxTokens = ceil(max_measured × 1.5 + 500)`) per role and writes the
  result to the 4 agent files. Invoke after the max-turn-limit plan is
  drafted, after any model swap, or when the user says "lock the
  max-turn caps" or "run the empirical pass." Merges
  `.tmp/docs/plans/2026-08-30-inference-speed-benchmark.md` (now
  superseded) into this single command — no separate plan invocation.
mode: workflow
---

# Subagent Fleet — Empirical Pass + Speed Probe (merged)

Recurrent task: per-role latency + cap measurement and application for
the 4 research subagents. Originally two separate workflows (the
max-turn-limit plan's "Step 0 empirical pass" and the
inference-speed-benchmark plan). Merged 2026-08-30T05:01Z so the cap is
applied from the same probe data, not from a re-run. Shiki is excluded
from both measurement and application.

## Why this command exists

Two failure modes the workflow must bound:

- **Too low** — the role's output envelope exceeds the cap; shiki's
  `claims_table` truncates mid-row, verifier outputs are rejected by
  the main agent for incompleteness.
- **Too high** — a runaway loop on the cheapest viable model runs 100
  turns, drives cost from ~$0.0009/call to ~$0.05/call, 4× in
  parallel = $0.20/run. Bounded absolute cost, but unmeasured.

The 2026-08-30T05:01Z merger also fixes the timing bug in the
two-plan flow: the inference-speed-benchmark plan was **parked
pending cap-plan apply** (anti-pattern: "Probing while the cap plan is
still draft"). By merging measurement and application into one
workflow, the cap is applied from the same probe data that measured
the per-role latency — no parking, no separate runs.

## User input

**Always** parse `$ARGUMENTS` before proceeding. Optional flags:

- `--output-csv <path>` — write a CSV summary to `<path>` instead of
  the default `.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-speed-benchmark.csv`.
- `--calls <N>` — override the 5-call default (e.g., `--calls 10` after
  a schema change to widen the sample).
- `--roles <csv>` — limit the probe to a subset, e.g.,
  `--roles haru,aki` after a partial re-evaluation.
- `--inputs-version <v1|v2>` — pick which synthetic-inputs version to
  use (default `v2`, the 2026-08-30T05:01Z refresh; `v1` is the
  2026-08-30T04:33Z draft, kept for diff audit at
  `.tmp/docs/plans/2026-08-30-fleet-speed-benchmark-inputs.md`
  §"Comparison vs v1").

Any prose after the flags is treated as free-form context and surfaced
into the report's `Scope` section verbatim.

## Required context the user supplies each run

- Which model each role is currently running on (read from
  `dot_config/kilo/exact_agent/*.md` `model:` lines if not supplied).
- Whether the user has approved a model swap since the last run (read
  the most recent revaluation report's `status: applied` snapshot if
  not supplied).
- Whether the user wants the cap to be applied (`--apply`) or just
  measured (`--no-apply`).

## Outputs

- **Phase A CSV:** `.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-speed-benchmark.csv`
  — one row per probe (4 roles × 5 calls = 20 rows; schema below).
- **Phase A report:** `.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-speed-benchmark.md`
  — markdown report with the per-role latency / cost /
  `tokens_completion` / `native_tokens_reasoning` table, the aki
  slowness diagnosis (if any), the speed-vs-cost scorecard, and the
  per-role cap recommendation.
- **Phase A per-call JSON:** `.tmp/docs/subagent-runs/YYYYMMDD_HHMMSS-<role>-speed-<i>.json`
  — raw `/generation` response per call (gitignored, per-worktree).
- **Phase B proposed edits:** `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu}.md`
  `steps:` and `maxTokens:` frontmatter lines (only after user
  approval). **Shiki is excluded** — model is pinned and caps stay at
  `steps: 40, maxTokens: 16000` (see Step 6 §"Scope").
- **Memory pointer:** `kilo_memory_save` with the report path + the
  locked per-role values.

## Pre-flight

1. Confirm the rule the user wants this run to enforce. Defaults: 5
   calls per role, `--apply` (apply the cap after Phase A completes),
   v2 inputs.
2. Load the `openrouter-api` skill if not already loaded — the Phase A
   probe calls `/v1/chat/completions` indirectly via `task`
   subagent dispatch, and queries `/v1/generation` per call for the
   `gen-...` lookup.
3. Load the `synthetic-problem-inputs` skill if not already loaded —
   the 20 input templates and the per-role harness reminders live
   there.
4. Read `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` to
   understand the cap-plan context and the `+500` reasoning-token
   buffer rationale.
5. Read the four `dot_config/kilo/exact_agent/*.md` files for current
   `model:`, `temperature:`, `top_p:`, `variant:` lines per role. The
   probe uses these verbatim — do not synthesise new model picks in
   this command.
6. **Sanity-check the management key** with one `/activity?limit=1`
   request — if it returns 403, abort and surface "management key
   unavailable" (the benchmark's per-call `/generation` lookups will
   not work).
7. **Sanity-check the MITM proxy** (added 2026-08-30T05:54Z after the
   proxy infra was set up):
   - `mitmdump` listening on `127.0.0.1:8080`? → `ss -tlnp | grep 8080`
   - Today's log file `/tmp/kilo/gen-log-$(date -I).jsonl` exists or
     can be created (proxy script writes to it)?
   - Last call captured by the proxy routes to `openrouter.ai/api/v1/chat/completions`
     (filter the log for that URL)?
   - If proxy is down or log is empty, abort with "MITM proxy not
     routing kilo traffic — verify VSCode `http.proxy` is
     `http://127.0.0.1:8080` and the mitmproxy CA is trusted via
     `NODE_EXTRA_CA_CERTS` or the OS trust store". This is a hard
     block, not a warning.

## Steps

### Step 1 — Build the per-role prompt template

For each role, build a `task`-tool-compatible prompt that mirrors the
role's output envelope exactly. The probe's job is to measure runtime
shape, not to test the role's content correctness, so the prompt is
templated from the synthetic-inputs skill (default v2; use `--inputs-version`
to switch).

Per-role prompt shape (the model is given the role body via kilo's
`subagent_type: <role>` dispatch, so it already knows the envelope;
the reminder is for the model's final-answer sampler):

- **haru:** "The leading candidate is: `<v2 input #i>`. Produce 3
  ranked failure modes for this candidate. Output must follow the haru
  YAML envelope (3 findings, each with
  claim/evidence/confidence/load_bearing/open_questions)."
- **natsu:** "Synthesize 3 ranked candidate solutions for: `<v2 input
  #i>`. Output must follow the natsu YAML envelope (3 findings, each
  with claim/reasoning_summary/evidence/confidence/load_bearing/open_questions)."
- **aki:** "The problem statement is: `<v2 input #i>`. List 3 hidden
  assumptions. Output must follow the aki YAML envelope (3 findings,
  each with claim/why_it_matters/evidence/likely_wrong/what_changes_if_false/load_bearing/open_questions)."
- **fuyu:** "Compare Candidate A: `<v2 A #i>` and Candidate B: `<v2 B
  #i>` on the rubric {correctness, cost, risk, complexity}. Output
  must follow the fuyu comparison-table YAML envelope (4 criteria,
  2 candidates, ranked with ties surfaced)."

The synthetic candidates exist only to make the prompt content
non-trivial; the probe does not score correctness, only shape.

### Step 2 — Run the 5-call probe per role

For each of `haru`, `natsu`, `aki`, `fuyu`:

1. For `i = 1..N` (default N=5):
   - Pick the synthetic input `i` from the role-templates reference.
   - Spawn a real `task`-tool subagent with `subagent_type: <role>`.
     The subagent inherits the role body's permission block and the
     system prompt.
   - Capture: `start_ts` and `end_ts` at the call boundary, total
     wall-clock time, total tokens consumed, YAML parse-success.
   - **The `gen-...` id is recovered post-hoc from the MITM proxy log**
     (see "OpenRouter `gen-...` id recovery" below). Kilo's `task`
     tool does not surface the id in its response; the proxy captures
     it by intercepting the `POST /v1/chat/completions` response body
     at the HTTP layer.
   - Write per-run JSON to
     `.tmp/docs/subagent-runs/$(date +%Y%m%d_%H%M%S)-<role>-speed-<i>.json`.
2. After all calls complete, recover the `gen-...` ids and look up the
   per-call metadata:
   - Read the last `N` rows from
     `/tmp/kilo/gen-log-$(date -I).jsonl` (one row per probe; the
     proxy script writes them in dispatch order).
   - For each row, query
     `GET /v1/generation?id=<gen-...>` using the management key.
     Capture: `latency`, `generation_time`, `moderation_latency`,
     `tokens_prompt`, `tokens_completion`, `native_tokens_reasoning`,
     `total_cost`, `usage`, `provider_name`, `finish_reason`, `model`,
     `upstream_id`, `streamed`, `cached_tokens`.

**OpenRouter `gen-...` id recovery (MITM proxy setup, 2026-08-30T05:54Z).**

The proxy infra: `mitmdump` listens on `127.0.0.1:8080`, with the
addon script at `~/.local/share/kilo/bin/openrouter-gen-logger.py`
appended via `-s`. The script filters to `openrouter.ai/api/v1/chat/completions`
and writes one JSON row per response to
`/tmp/kilo/gen-log-{YYYY-MM-DD}.jsonl`. The Authorization header and
request body are intentionally never logged — only the response
metadata (`id`, `model`, `usage`, `finish_reason`, timestamps).

The proxy must be configured for **VSCode and its children** (per
user setup 2026-08-30T05:54Z) so the Kilo extension's `task`-tool
dispatches route through it. Set VSCode's `http.proxy` to
`http://127.0.0.1:8080` and `http.proxySupport` to `override` so
child processes inherit it; install the mitmproxy CA at
`~/.mitmproxy/mitmproxy-ca-cert.pem` via `NODE_EXTRA_CA_CERTS` in
VSCode's process env, or via the OS trust store.

**Sanity check before Phase A runs:**

```bash
curl -x http://127.0.0.1:8080 -sS -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer $OPENROUTER_API_KILO_CLI" \
  "https://openrouter.ai/api/v1/models?limit=1"
# expect: 200

wc -l /tmp/kilo/gen-log-$(date -I).jsonl
# expect: at least 1 row (proxy is logging)
```

If the sanity check returns non-200 or no rows log, abort and surface
"MITM proxy not routing kilo traffic". The workflow does not have a
fallback for this — proxy failure is a hard block, not a warning.

If the role's first call hits the cap, that is data, not failure —
record it and continue. Do not raise the cap mid-probe.

Wall-clock at the call boundary is measured at this layer (not from
`/generation`) because `/generation.latency` is **model inference
time**, not end-to-end subagent time. End-to-end includes the
subagent body prompt load, role tool-call resolution, reasoning trace
emission, final answer assembly, and kilo runtime framing. The
workflow captures **both**: `/generation.latency` for the model
layer, `end_ts - start_ts` for the subagent layer.

### Step 3 — Aggregate the data

For each role, compute over the 5 calls:

| Stat | Source |
|---|---|
| `p50 latency_ms` | `/generation.latency` p50 |
| `p95 latency_ms` | `/generation.latency` p95 |
| `p50 generation_time_ms` | `/generation.generation_time` p50 |
| `p50 wall_clock_ms` | measured at call boundary |
| `p50 reasoning_tokens` | `/generation.usage.native_tokens_reasoning` p50 |
| `p50 cost_usd` | `/generation.total_cost` p50 |
| `p50 prompt_tokens` | `/generation.usage.tokens_prompt` p50 |
| `p50 completion_tokens` | `/generation.usage.tokens_completion` p50 |
| `cache_hit_rate_pct` | `cached_tokens / prompt_tokens × 100` |
| `provider_name` | most-common (mode) per role |
| `finish_reason_breakdown` | count of `stop` / `length` / `error` per role |
| `max steps_used` | `/generation` turn counter — `max` over the 5 calls |
| `max tokens_used` | `tokens_completion + native_tokens_reasoning` — `max` |

If a role's calls split across multiple providers (fallback fired),
report both providers and the per-provider latency p50.

### Step 4 — Recommend per-role values

**Cap formula (user policy 2026-08-30T05:01Z — "conservative").**

The per-role cap is derived from the measured peak per call,
multiplied by 1.5, plus a fixed buffer for tokens:

```
steps_cap       = ceil(max_measured_steps × 1.5)
max_tokens_cap  = ceil(max_measured_tokens × 1.5 + 500)
```

Rationale: a model swap, a longer prompt, or a different reasoning
profile can change the actual `steps_used` and `tokens_consumed` on
the next run. Multiplying the measured peak by 1.5 (down from the
2026-08-30T04:57Z value of 2.0 after re-evaluation) gives headroom
for typical variation without over-budgeting by 2-5× when the
measurement is already at the cap. The `+ 500` token buffer is the
canonical reasoning-overhead floor from
`.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` §"Decisions"
("Conservative `max_tokens` floor") — reasoning-emitting models
observe ≥ 60 reasoning tokens for short prompts
(`inclusionai/ling-3.0-flash`, 2026-08-30), and 500 is the floor that
protects against `finish_reason: length` truncation.

The formula is **applied automatically at the end of Phase A** — no
manual decision step is required, as it was in the pre-merger
empirical-pass (which used a 4-band rule with manual override). The
two pre-2026-08-30 exceptions still apply:

- **`steps_cap` ceiling** — clamp at `100` regardless of formula
  output (per `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
  §4 anti-runaway guidance).
- **Reasoning-model `max_tokens` floor** — for reasoning-emitting
  models, `max_tokens_cap ≥ reasoning_overhead + 500 + answer_envelope`
  regardless of formula output.

**Scope (per user policy 2026-08-30T04:57Z, reaffirmed 2026-08-30T05:01Z).**

- Apply the formula to **haru, natsu, aki, fuyu only**.
- **Shiki is excluded** — model is pinned at
  `openrouter/minimax/minimax-m3` and will not change (speed-benchmark
  plan also skips shiki per the 2026-08-30T04:38Z decision). Shiki's
  caps stay at the values locked by the prior empirical pass
  (`steps: 40, maxTokens: 16000`).

**Inputs (preferred — from this Phase A probe).**

- `max_measured_steps` — `max(steps_used)` from Step 3.
- `max_measured_tokens` — `max(tokens_used)` from Step 3.

**Inputs (fallback — empirical-pass proxy, when Phase A is not run).**

- `max_measured_steps` — `max(wall_clock_s) / per_turn_latency_p50`,
  where `per_turn_latency_p50` is the per-provider p50 latency from
  `GET /models/<id>/endpoints`. Caveat: the empirical pass's
  wall-clock includes 25-way parallel contention; treat the fallback
  value as an upper bound.
- `max_measured_tokens` — `max(output_envelope_bytes) / 3` (YAML at
  ~3 chars/token) + the role's observed `native_tokens_reasoning` p50.

**Decision rule (when Phase A data is missing).**

If neither the Phase A CSV nor `/generation` data exists for the
role, refuse to apply the cap and surface the missing-data warning
to the user. **Do not fall back to wall-clock-derived proxies without
explicit user approval** — the proxies inflate the cap by the
contention factor (2-5× typical), wasting per-run budget.

Print a recommendation table:

| Role | max_measured_steps | max_measured_tokens | recommended `steps` | recommended `maxTokens` | data source |
|---|---|---|---|---|---|

### Step 5 — Write the report

Create a fresh file at
`.agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-speed-benchmark.md`.
No frontmatter required (cache entries are optional-frontmatter per
`~/.config/kilo/skills/document-conventions/references/frontmatter.md`),
but include:

```yaml
---
title: OpenRouter fleet-speed-benchmark
date: YYYY-MM-DD
task-slug: subagent-fleet-empirical-pass-speed-benchmark
related:
  - .tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md
  - docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md
  - .agents/kilo/command/subagent-fleet-reevaluate-models.md
inputs-version: v2 (2026-08-30T05:01Z)
cap-formula: steps = ceil(max × 1.5), maxTokens = ceil(max × 1.5 + 500)
roles-probed: [haru, natsu, aki, fuyu]   # shiki excluded
applied_at: null
status: pending-user-review
---
```

**Body sections, in this order:**

1. **Scope** — what triggered this pass; the per-role model picks; the
   synthetic-inputs version used.
2. **Inputs** — the flags passed; the synthetic-prompt template per
   role; the v2-vs-v1 diff (one paragraph).
3. **Per-role stats** — the table from Step 3.
4. **Speed-vs-cost scorecard** — the 2-axis plot for each role.
5. **Recommendation table** — from Step 4. Includes the
   `max_measured_steps`, `max_measured_tokens`, the formula input, and
   the formula output for audit.
6. **Decision callouts** — which roles are locked; which roles were
   skipped (shiki per the user policy at 2026-08-30T04:57Z).
7. **Aki slowness diagnosis** (when relevant) — p50/p95 latency vs
   the other 3 roles; per-call provider breakdown; reasoning-overhead
   ratio; `finish_reason` breakdown. Default recommendation if aki is
   consistently slow: the user can (a) raise aki's `maxTokens` further,
   or (b) re-pick aki from a faster family in the next revaluation.
   Surface both; do not pick.
8. **Per-run JSON refs** — list of `.tmp/docs/subagent-runs/...` paths
   for audit.
9. **Anti-patterns observed** — any role that ran the cap on every
   call, any role that ran < 25% of the cap, any reasoning-model
   interaction with `max_tokens`.
10. **Formula audit** — for each role, show
    `max_measured → ×1.5 → +500 → final cap`. Skipped roles (shiki) are
    called out here with the reason.
11. **Cost delta** — per-call cost × applied cap, vs the runaway
    100-step worst-case. A runaway 100-step call at $0.10/M out is
    ~$0.05; 4 in parallel = $0.20. Compute the actual delta for the
    new cap and surface it.

Commit via `kilo-shared save "empirical-pass speed-benchmark report:
YYYY-MM-DD"` (project rule for shared-context writes).

### Step 6 — Surface to the user

Use the `question` tool with these options:

1. **Adopt recommendations + apply** — edit the 4 agent files with the
   recommended `steps` and `maxTokens` from Step 4.
2. **Adopt with override** — user supplies specific per-role values.
3. **Re-probe** — run a second 5-call probe (perhaps with `--calls 10`)
   to widen the sample before deciding.
4. **Decline** — write a `status: declined` update in the report
   frontmatter and stop. No agent file edits.

Do not edit any agent file until the user picks 1 or 2. If the user
picks 3, run another 5-call probe (this command becomes a loop until
the user picks 1, 2, or 4). If `--no-apply` was passed, default to
option 4 (decline + no apply) — the user wants measurement only.

### Step 7 — Apply the picks (after user picks 1 or 2)

1. For each role file in scope
   (`dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu}.md`):
   - Insert `steps: <N>` and `maxTokens: <M>` after the `variant:`
     line in the frontmatter (matches existing frontmatter field order:
     description → mode → model → variant → temperature → top_p).
   - Use `edit`, not `write`, so the rest of the file is unchanged.
   - **Shiki file is not touched** — its `steps: 40, maxTokens: 16000`
     stay locked.
2. Run `chezmoi diff` against the chezmoi-managed copy of those files.
   Verify the diff shows only the new `steps:` and `maxTokens:` lines
   per file, nothing else. **Shiki must not appear in the diff** —
   confirms it was untouched.
3. Show the user the diff. **Stop and wait** for explicit confirmation.
4. After confirmation: `chezmoi apply`. Re-run `chezmoi diff` to confirm
   the diff is now empty (managed targets match source).
5. Update the report frontmatter with `status: applied` and the apply
   timestamp.
6. Restart kilo daemon + VSCode so the new caps are picked up at
   dispatch time (precedent: the 2026-08-30T04:13Z openrouter/ prefix
   fix required this).

### Step 7.5 — Refresh `references/model-picks.md`

After the agent files are applied (Step 7) and before the round-trip
verifications (Step 8), refresh the LOCKED assignments table at
`dot_config/kilo/exact_skills/subagent-fleet/references/model-picks.md`
so the reference stays in sync with the live agent files.

1. **Read the current table** in
   `dot_config/kilo/exact_skills/subagent-fleet/references/model-picks.md`.
   Note: the file is stale by definition (it pins a snapshot from a
   prior revaluation); Step 3 of the cap plan
   (`.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md`)
   already commits to refreshing it.
2. **Update the LOCKED assignments table** to:
   - Refresh the `Subagent` column's `model id` per role to match the
     live `dot_config/kilo/exact_agent/<role>.md` `model:` line.
   - Add a `steps` column with the per-role cap applied in Step 7.
   - Add a `maxTokens` column with the per-role cap applied in Step 7.
   - Use `edit`, not `write`, so the table body and the prose below
     it are preserved.
   - **Shiki is included** in the refresh (its cap stays at
     `steps: 40, maxTokens: 16000`; the table gets the same row
     refresh so all 5 rows are consistent).
3. **Run `chezmoi diff`** and verify the only changes to
   `references/model-picks.md` are:
   - Updated model id strings (if any)
   - The new `steps` and `maxTokens` columns
4. **`chezmoi apply`** the refresh in the same step as the agent-file
   apply from Step 7.4. After apply, `chezmoi diff` should be empty.
5. **Note**: this refresh is **documentation-only**. If the workflow
   is run with `--no-apply` (measurement only), Step 7.5 is skipped
   — there is no new cap to write into the table.

The cap plan's Step 3 ("Update `references/model-picks.md` LOCKED
table to add `steps` and `max_tokens` columns") is now satisfied by
this workflow step; the cap plan no longer needs a separate edit pass.

### Step 8 — Verify (one round-trip per role)

For each role in scope (`haru`, `natsu`, `aki`, `fuyu`), run one
`task`-tool call with the picked model and a sentinel prompt: "Reply
with only the word 'ok' and no other text." Confirm the response
parses. **Shiki is skipped** — its cap is not changed by this run.

If any probe fails:

1. Revert that subagent's `steps:` and `maxTokens:` lines to the
   prior values via `chezmoi diff -reverse` + `chezmoi apply`.
2. Set the report's `status: applied-with-failures`, note which slot
   and the error.
3. Re-open the report for the user.

### Step 9 — Memory pointer

`kilo_memory_save` with the *short* pointer only:

```
key: kilo.fleet.last_empirical_pass
text: Empirical pass {YYYY-MM-DD}; roles locked: haru={steps,maxTokens}, natsu={steps,maxTokens}, aki={steps,maxTokens}, fuyu={steps,maxTokens}; shiki=skipped-per-2026-08-30T04:57Z;
  report: .agents/docs/cache/openrouter/{YYYY-MM-DD}-fleet-speed-benchmark.md
```

No facts in the memory record — the report is the canonical store.

## Anti-patterns

- **Re-picking models in this command.** This command runs probes
  against the *current* model picks. Model changes are the
  revaluation workflow's job, not this one's. If a probe reveals the
  current pick is too weak (e.g., consistent YAML parse failure),
  surface it as an `Anti-patterns observed` entry and escalate to the
  revaluation workflow — don't change `model:` lines here.
- **Raising the cap mid-probe.** If the first call hits the cap,
  record it and continue. Mid-probe cap changes pollute the data.
- **Locking caps from fewer than 3 calls.** A 1-call sample is noise.
  If `--calls` is < 3, refuse and surface the warning.
- **Treating reasoning-model `max_tokens` as fixed.** Reasoning
  models' overhead varies by prompt. Re-verify the reasoning
  overhead after any role-body edit that changes the system prompt.
- **Skipping the cost delta calculation.** Per the max-turn-limit
  plan, a runaway 100-step call at $0.10/M out is ~$0.05. Compute the
  delta between the proposed cap and the maximum observed `steps_used`
  in the report's `Cost delta` section; surface it.
- **Applying the formula with proxy-derived inputs (wall-clock /
  envelope-bytes) without the user's explicit approval.** Wall-clock
  includes 25-way parallel contention in the empirical pass and inflates
  the cap by 2-5×. Phase A probe data (`/generation`-derived
  `steps_used` + `tokens_completion`) is the preferred input; refuse
  to apply the cap and surface the missing-data warning when it's
  absent (see Step 4 §"Decision rule").
- **Applying caps to shiki.** Shiki's model is pinned at
  `openrouter/minimax/minimax-m3` and will not change; its cap stays
  at `steps: 40, maxTokens: 16000` (per user policy 2026-08-30T04:57Z).
  Including shiki in the formula pass is a scope violation.
- **Using snake_case `max_tokens:` in agent frontmatter.** The schema
  is `maxTokens:` (camelCase) — see
  `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` §"Decisions"
  ("Schema field name") and the kilo `unstable/ai` schema at
  `McpSchema.ts:1551`. `steps:` is snake_case; the two are not
  symmetric.
- **Running Phase A without a management key.** Without
  `$OPENROUTER_MANAGEMENT_KEY`, the per-call `/generation` lookup
  fails with 403 and `steps_used` / `tokens_completion` are null.
  Sanity-check in Pre-flight step 6 before any spawn.

## Boundary

- **What this command does:** run a Phase A per-role speed probe
  (4×5=20 spawns, per-call `/generation` lookup, CSV + report), apply
  the Phase B `1.5× max + 500` cap formula per role via chezmoi, and
  restart kilo to pick up the new caps. Shiki is excluded.
- **What this command does NOT do:**
  - Re-pick models — that's the revaluation workflow
    (`.agents/kilo/command/subagent-fleet-reevaluate-models.md`).
  - Edit role bodies (`agent/<role>.md`) — that changes the role
    itself, not the cap. Belongs to plan §3.
  - Change sampling tilt (`temperature` / `top_p`) — also plan §3
    territory.
  - Promote picks back into the max-turn-limit plan — that's a
    separate commit after apply. Update the plan's "Per-role initial
    overrides" table from "initial" to "locked at <commit>".
  - Modify shiki's caps — out of scope per user policy
    2026-08-30T04:57Z.
  - Generate synthetic inputs — the `synthetic-problem-inputs` skill
    owns the 20 input seeds (v2 at
    `.agents/kilo/skills/synthetic-problem-inputs/references/role-templates.md`).
  - Cache hit-rate optimisation. Cache routing is kilo.jsonc's
    `provider.openrouter.models.<id>.options.provider` job; this
    command only measures, it does not reorder.
  - Live latency budgets in CI. This is a one-shot measurement +
    apply, not a continuous monitor.

## References

- `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` — the plan
  this command implements.
- `.tmp/docs/plans/2026-08-30-inference-speed-benchmark.md` —
  **superseded** by this merged workflow (2026-08-30T05:01Z). The
  parking state ("parked-pending-cap-apply") is resolved by the
  merger — no separate invocation needed.
- `.tmp/docs/plans/2026-08-30-fleet-speed-benchmark-inputs.md` — the
  v2 inputs plan with provenance trail (web search performed
  2026-08-30T05:01Z).
- `.agents/kilo/skills/synthetic-problem-inputs/SKILL.md` — owns the
  20 input seeds and harness contract.
- `.agents/kilo/skills/openrouter-api/SKILL.md` — `/v1/generation` and
  `/v1/activity` endpoints.
- `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
  §3 (roles), §5 (invocation), §7 (output contract), §8 (shiki).
- `.agents/kilo/command/subagent-fleet-reevaluate-models.md` —
  complementary workflow; this command runs after revaluation applies
  new picks, before the next revaluation.
- `.agents/docs/cache/README.md` — knowledge-cache convention.
- User policy 2026-08-30T04:57Z — cap formula
  (`steps = ceil(max × 2)`, `maxTokens = ceil(max × 2 + 500)`).
- User policy 2026-08-30T05:01Z — **revised** cap formula
  (`steps = ceil(max × 1.5)`, `maxTokens = ceil(max × 1.5 + 500)`);
  +500 token buffer retained; scope excludes shiki; workflow merges
  inference-speed-benchmark plan.