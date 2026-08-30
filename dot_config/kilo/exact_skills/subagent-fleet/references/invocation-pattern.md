# Invocation Pattern (snapshot 2026-08-25)

> Re-verify against `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` §5
> when reachable.

## Procedure

1. **Decide N** — number of research subagents to launch. The
   `subagent-fleet-trigger` rule's "Pick" table maps failure shapes to
   first/second picks:
   - One trigger (stuck or load-bearing) fires → default N=1 with the
     role matching the failure shape.
   - Both triggers fire, or stakes are high → N=2-4.
   - For comparison tasks with no rubric → N=1 with `fuyu`, plus `haru`
     when the leading candidate is load-bearing.

2. **Pick which roles** — if N<4, sub-sample from `{haru, natsu, aki,
   fuyu}` weighted toward the failure shape.

3. **Spawn in parallel** — same prompt for each. Pass `haru`'s output
   to `fuyu` when both run in the same fan-out.

4. **Mandatory `shiki` when N≥2.** When N=1, spawn `shiki` only when
   the agent flags the single research subagent's output as load-bearing
   (cited in the final answer).

5. **Read only `shiki`'s consolidated report.** Decide whether to
   escalate (another subagent at `variant: high` on a frontier model)
   or accept.

## Hard rules

- **Never read raw research subagent output when N≥2.** `shiki` is the
  only channel into the main agent's context. This keeps noise out of
  working memory.
- **Pass `haru`'s output to `fuyu`** when both spawn in the same
  fan-out (best-effort, not guaranteed by Kilo's parallel scheduler).
- **Cap on shiki escalation.** When shiki returns `deep: unclear` on a
  `load_bearing: true` claim, escalate to the user; do not loop another
  shiki call indefinitely.

## Sequential chain (optional, not default)

For high-stakes questions:

1. Round 1: spawn `haru` alone. Use its output to refine the question.
2. Round 2: spawn `natsu`, `aki`, `fuyu` with the refined question.
   Run `shiki`.

Cost: ~3 research calls + 1 verifier. Higher quality on questions
where the adversarial pass reveals the original framing was wrong.
Default off; on for security/correctness stakes.

## Reports go to `.tmp/docs/subagent-runs/`

Each subagent writes its report to
`.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>[-<topic>].yaml`
(e.g. `20260826_113348-haru.yaml` or
`20260826_113348-natsu-sdd-synthesis.yaml`). The `YYYYMMDD_HHMMss`
segment is computed at write time with `date +%Y%m%d_%H%M%S` (local
clock; do not use `date +%s`). The optional `<topic>` slug is a short
disambiguator derived from the question — omit when the role alone is
clear. `shiki` never takes a topic slug. The dir is `.gitignore`d in
`.tmp/docs/.gitignore` so reports do not pollute shared-context
history. On other projects, the same path works if
`.tmp/docs/subagent-runs/` exists with the gitignore applied.

## Anti-patterns

- Skipping `shiki` because "it's only two subagents" — the plan makes
  shiki mandatory at N≥2 to keep noise out of the main agent's context.
- Reading raw research subagent output into the main agent's context.
- Launching all four research subagents by default for trivial questions
  — cost ceiling is bounded by the failure shape.
- Treating `shiki`'s recommendation as final when `deep: unclear` on a
  `load_bearing: true` claim — re-run or escalate.
