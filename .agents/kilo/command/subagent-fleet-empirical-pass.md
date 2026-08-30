---
name: subagent-fleet-empirical-pass
description: >
  Run a 5-call probe of each subagent role (haru/natsu/aki/fuyu/shiki)
  with the proposed `steps` and `max_tokens` runtime caps from the
  max-turn-limit plan. Measure whether each role's run hits the cap,
  falls under it, or terminates early. Lock per-role values from data,
  then edit the four agent files (and the verifier if applicable) with
  the locked values. Invoke after the max-turn-limit plan is drafted
  but before applying any frontmatter cap, after any model swap that
  changes the reasoning-trace profile, or when the user says "lock the
  max-turn caps" or "run the empirical pass."
mode: workflow
---

# Subagent Fleet — Empirical Pass (max-turn-limit Step 0)

Recurrent task: empirically lock the per-role `steps` and `max_tokens`
runtime caps proposed in
`.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md`. The plan
guesses at `steps: 25, max_tokens: 4000` as a shared default plus
per-role overrides; this command turns those guesses into measured
values.

## Why this command exists

The max-turn-limit plan cannot lock per-role caps without data. Picking
`steps: 25` because it "feels right" risks one of two failure modes:

- **Too low** — the role's output envelope exceeds the cap; shiki's
  `claims_table` truncates mid-row, verifier outputs are rejected by
  the main agent for incompleteness.
- **Too high** — a runaway loop on the cheapest viable model runs 100
  turns, drives cost from ~$0.0009/call to ~$0.05/call, 4× in
  parallel = $0.20/run. Bounded absolute cost, but unmeasured.

A 5-call probe per role answers both questions.

## User input

**Always** parse `$ARGUMENTS` before proceeding. Optional flags:

- `--output-csv <path>` — write a CSV summary to `<path>` instead of
  the default `.agents/docs/cache/kilo-subagents/<YYYY-MM-DD>-empirical-pass.csv`.
- `--calls <N>` — override the 5-call default (e.g., `--calls 10` after
  a schema change to widen the sample).
- `--roles <csv>` — limit the probe to a subset, e.g.,
  `--roles haru,aki` after a partial re-evaluation.

Any prose after the flags is treated as free-form context and surfaced
into the report's `Scope` section verbatim.

## Required context the user supplies each run

- Which model each role is currently running on (read from
  `dot_config/kilo/exact_agent/*.md` `model:` lines if not supplied).
- Whether the plan's Step 0 has been approved; if not, this command
  must surface the approval question before running probes.

## Outputs

- **Report:** `.agents/docs/cache/kilo-subagents/{YYYY-MM-DD}-empirical-pass.md`
  (cache convention: `.agents/docs/cache/README.md`). Never append to
  a prior report.
- **Per-run YAML:** `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>-empirical-<N>.yaml`
  for each probe (matches the canonical subagent-run path; ephemeral,
  gitignored).
- **Proposed edits:** `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`
  `steps:` and `max_tokens:` frontmatter lines (only after user
  approval).
- **Memory pointer:** `kilo_memory_save` with the report path + locked
  per-role values.

## Pre-flight

1. Confirm the rule the user wants this run to enforce. Defaults from
   the max-turn-limit plan; if the user supplied `--calls` or other
   flag, fold it in.
2. Load the `openrouter-api` skill if not already loaded — the probe
   calls `/v1/chat/completions` directly (cheaper than `task` subagent
   spawns) and the skill documents the contract.
3. Read `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` §"Per-role
   initial overrides" to know which values to probe.
4. Read the four `dot_config/kilo/exact_agent/*.md` files for current
   `model:`, `temperature:`, `top_p:`, `variant:` lines per role. The
   probe uses these verbatim — do not synthesise new model picks in
   this command.

## Steps

### Step 1 — Build the per-role prompt template

For each role, build a `task`-tool-compatible prompt that mirrors the
role's output envelope exactly. The probe's job is to measure runtime
shape, not to test the role's content correctness, so the prompt can
be templated:

- **haru:** "Produce 3 ranked failure modes for the candidate
  `[synthetic candidate A]`. Output must follow the haru YAML
  envelope in `~/.config/kilo/skills/subagent-fleet/references/fleet-roles.md`."
- **natsu:** "Produce 3 ranked candidate solutions for `[synthetic
  problem B]`. Output must follow the natsu YAML envelope."
- **aki:** "List the 3 hidden assumptions in `[synthetic problem C]`.
  Output must follow the aki YAML envelope."
- **fuyu:** "Compare `[synthetic candidate X]` and `[synthetic
  candidate Y]` on the rubric [correctness, cost, risk, complexity].
  Output must follow the fuyu comparison table."
- **shiki:** "Verify the haru YAML at
  `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-haru-empirical-1.yaml` per
  the shiki two-pass procedure."

The synthetic candidates exist only to make the prompt content non-
trivial; the probe does not score correctness, only shape.

### Step 2 — Run the 5-call probe per role

For each of `haru`, `natsu`, `aki`, `fuyu`, `shiki`:

1. For `i = 1..N` (default N=5):
   - Pick the synthetic input for role `r`, call `i`.
   - Spawn a real `task`-tool subagent with `subagent_type: <role>`.
     The subagent inherits the role body's permission block and the
     system prompt.
   - Capture: actual `steps` used, `max_tokens` cap hit or not, total
     wall-clock time, total tokens consumed, YAML parse-success.
   - Write per-run YAML to
     `.tmp/docs/subagent-runs/$(date +%Y%m%d_%H%M%S)-<role>-empirical-<i>.yaml`.

If the role's first call hits the cap, that is data, not failure —
record it and continue. Do not raise the cap mid-probe.

### Step 3 — Aggregate the data

For each role, compute over the 5 calls:

- **steps_used** — `min`, `median`, `max`, `p95`.
- **max_tokens_hit** — boolean per call; aggregate as a percentage.
- **wall_clock_s** — `min`, `median`, `max`.
- **tokens_consumed** — `min`, `median`, `max`.
- **yaml_parse_ok** — boolean per call; aggregate as a percentage.

Surface the medians and p95 in the report. Min/max only if the spread
is informative (e.g., one outlier dominates).

### Step 4 — Recommend per-role values

Decision rule, applied per role:

1. If `p95(steps_used) > 0.8 × proposed_steps` → the proposed value
   is binding in 80% of runs → **raise the proposed `steps` by 50%**
   and re-probe on the next empirical pass.
2. If `p95(steps_used) < 0.5 × proposed_steps` → the proposed value is
   wasteful → **lower the proposed `steps` to `ceil(2 × p95)`**.
3. If `0.5 × proposed ≤ p95(steps_used) ≤ 0.8 × proposed_steps` → the
   proposed value is in the productive band → **lock the proposed
   value**.
4. If `max_tokens_hit` rate > 50% → **raise `max_tokens` to the next
   sensible bucket** (4K → 6K → 8K → 12K). Reasoning models are an
   explicit exception: set `max_tokens ≥ reasoning_overhead + 500 +
   answer_envelope` even if the rule above says lower.

Print a recommendation table:

| Role | proposed `steps` | p95 actual | recommended `steps` | proposed `max_tokens` | max_tokens hit % | recommended `max_tokens` |
|---|---|---|---|---|---|---|

### Step 5 — Write the report

Create a fresh file at
`.agents/docs/cache/kilo-subagents/{YYYY-MM-DD}-empirical-pass.md`. No
frontmatter required (cache entries are optional-frontmatter per
`~/.config/kilo/skills/document-conventions/references/frontmatter.md`),
but include:

```yaml
---
source: subagent-fleet-empirical-pass
captured: YYYY-MM-DD
freshness: <90 days; re-run on model swap or plan §3 change>
related:
  - .tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md
  - docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md
---
```

**Body sections, in this order:**

1. **Scope** — what triggered this pass; the current model picks per
   role.
2. **Inputs** — the proposed per-role values being probed.
3. **Per-role data table** — the aggregated data from Step 3.
4. **Recommendation table** — from Step 4.
5. **Decision callouts** — which roles need re-probe next pass; which
   roles are locked.
6. **Per-run YAML refs** — list of `.tmp/docs/subagent-runs/...` paths
   for audit.
7. **Anti-patterns observed** — any role that ran the cap on every call,
   any role that ran < 25% of the cap (suggests the role envelope can
   tighten), any reasoning-model interaction with `max_tokens`.

### Step 6 — Surface to the user

Use the `question` tool with these options:

1. **Adopt recommendations** — edit the four agent files (and shiki if
   applicable) with the recommended `steps` and `max_tokens`.
2. **Adopt with override** — user supplies specific per-role values.
3. **Re-probe** — run a second 5-call probe (perhaps with `--calls 10`)
   to widen the sample before deciding.
4. **Decline** — write a `status: declined` update in the report front-
   matter and stop.

Do not edit any agent file until the user picks 1 or 2. If the user
picks 3, run another 5-call probe (this command becomes a loop until
the user picks 1, 2, or 4).

### Step 7 — Apply the picks (after user picks 1 or 2)

1. For each role file (`dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`):
   - Insert `steps: <N>` and `max_tokens: <M>` after the `variant:`
     line in the frontmatter (matches existing frontmatter field order:
     description → mode → model → variant → temperature → top_p).
   - Use `edit`, not `write`, so the rest of the file is unchanged.
2. Run `chezmoi diff` against the chezmoi-managed copy of those files.
   Verify the diff shows only the new `steps:` and `max_tokens:` lines
   per file, nothing else.
3. Show the user the diff. **Stop and wait** for explicit confirmation.
4. After confirmation: `chezmoi apply`. Re-run `chezmoi diff` to confirm
   the diff is now empty (managed targets match source).
5. Update the report frontmatter with `status: applied` and the apply
   timestamp.

### Step 8 — Verify (one round-trip per role)

For each role, run one `task`-tool call with the picked model and a
sentinel prompt: "Reply with only the word 'ok' and no other text."
Confirm the response parses. This is the same Step 9 verification as
the revaluation workflow; reused to confirm the new caps don't break
basic round-trip.

If any probe fails:

1. Revert that subagent's `steps:` and `max_tokens:` lines to the
   prior values via `chezmoi diff -reverse` + `chezmoi apply`.
2. Set the report's `status: applied-with-failures`, note which slot
   and the error.
3. Re-open the report for the user.

### Step 9 — Memory pointer

`kilo_memory_save` with the *short* pointer only:

```
key: kilo.fleet.last_empirical_pass
text: Empirical pass {YYYY-MM-DD}; roles locked: haru={steps,max_tokens}, ..., shiki={steps,max_tokens};
  report: .agents/docs/cache/kilo-subagents/{YYYY-MM-DD}-empirical-pass.md
```

No facts in the memory record — the report is the canonical store.

## Anti-patterns

- **Re-picking models in this command.** This command runs probes
  against the *current* model picks. Model changes are the
  revaluation workflow's job, not this one's. If a probe reveals the
  current pick is too weak (e.g., consistent YAML parse failure),
  surface it as an `Anti-patterns observed` entry and escalate to the
  revaluation workflow — don't change `model:` lines here.
- **Raising the cap mid-probe.** If the first call hits `steps: 25`,
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

## Boundary

- **What this command does:** probe each role with the proposed caps,
  aggregate runtime data, recommend per-role caps from data, apply the
  picks via chezmoi after user confirmation.
- **What this command does NOT do:**
  - Re-pick models — that's the revaluation workflow.
  - Edit role bodies (`agent/research-*.md`) — that changes the role
    itself, not the cap. Belongs to plan §3.
  - Change sampling tilt (`temperature` / `top_p`) — also plan §3
    territory.
  - Promote picks back into the max-turn-limit plan — that's a
    separate commit after apply. Update the plan's "Per-role initial
    overrides" table from "initial" to "locked at <commit>".

## References

- `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` — the plan
  this command implements.
- `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
  §3 (roles), §5 (invocation), §7 (output contract), §8 (shiki).
- `.agents/kilo/command/subagent-fleet-reevaluate-models.md` —
  complementary workflow; the empirical pass runs after revaluation
  applies new picks, before the next revaluation.
- `.agents/docs/cache/README.md` — knowledge-cache convention.
- `.agents/docs/cache/openrouter/<date>-fleet-revaluation.md` — most
  recent revaluation; check whether the picks being probed here match
  the revaluation's `status: applied` snapshot.