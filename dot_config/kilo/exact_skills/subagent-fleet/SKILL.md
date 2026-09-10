---
name: subagent-fleet
description: >
  Load when an agent wants to invoke the haru/natsu/aki/fuyu/shiki
  subagent fleet (or the 2-verifier mode with reki) for stuck-task
  recovery or load-bearing verification, or when an agent in another
  project needs the fleet design, role definitions, invocation
  pattern, or model assignments. Triggers: "use a subagent", "launch
  the fleet", "haru", "natsu", "aki", "fuyu", "shiki", "reki",
  "verifier", "verifier pair", "second opinion", "adversarial
  review", "compare candidates", "audit assumptions", "load-bearing
  claim", "stuck task". Key terms include subagent, fleet, four
  seasons, RCAF, verifier, research subagent, parallel fan-out,
  disagreement resolution.
---

# Subagent Fleet Skill

Portable reference for the haru/natsu/aki/fuyu + shiki (+ optional
reki) subagent fleet. The fleet provides stuck-task recovery and
load-bearing verification through 4 prompt-conditioned research roles
+ 1 mandatory verifier (shiki) + 1 opt-in second verifier (reki,
2-verifier mode only). This skill is the entry point; the canonical
plan is the source of truth.

## When to load

- An agent wants to invoke one or more research subagents and needs to
  pick the right role for the failure shape.
- An agent needs the fleet's invocation pattern (N research + shiki at
  N≥2, optional reki at N≥3 or high-stakes).
- An agent needs the current model assignments or permission block.
- An agent needs the disagreement-resolution rule for shiki+reki
  verifier-pair output.
- A new project Kilo instance needs the fleet essentials without
  reading the full plan.

## Source of truth

The canonical plan is
`docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` in
the chezmoi repo (`~/.local/share/chezmoi/` on machines with the
dotfiles repo applied). **Caveat:** that plan was abandoned on
2026-09-01 in favour of a from-scratch rebuild (see
`dot_config/kilo/exact_agent/README.md` "Plan history"). When the
plan is reachable, treat it as the canonical-design-history source;
when it is not reachable (other projects), use the bundled references
below as the source of truth. **For the 2-verifier extension (reki,
added 2026-09-09), the authoritative reference is the cache entries**
under `.agents/docs/cache/kilo-subagents/2026-09-09-*.md` (or
`~/.local/share/chezmoi/.agents/docs/cache/kilo-subagents/2026-09-09-*.md`
when the cache is chezmoi-tracked).

## References

Load on demand. Do not load all of them at once.

| File | Load when |
|---|---|
| `references/fleet-roles.md` | Picking which role fits the failure shape (haru/natsu/aki/fuyu/shiki/reki). |
| `references/invocation-pattern.md` | About to spawn research subagents — need the N-research + shiki rules, the 2-verifier mode trigger, and the output contracts. |
| `references/model-picks.md` | Need the current model id, family, `variant:`, or sampling tilt for each role. |
| `references/permission-block.md` | Need the permission allowlist shared by all 6 subagents (or the operational discipline preamble). |
| `references/task-prompt-budget.md` | About to compose a `task` prompt for any of the 6 subagents — must read before any spawn (≤ 15 lines, no body-duplication, no output-path or filename-format overrides). |

## Failure-shape → role mapping

Pick the research subagent whose stance fits the failure shape. The
trigger rule owns the *when*; this table owns the *which*.

| Failure shape | First pick | Optional second pick |
|---|---|---|
| Leading answer may be wrong | `haru` (adversarial) | `shiki` verifier on haru's output |
| Need a coherent answer / candidate synthesis | `natsu` (synthesizer) | `aki` (assumption-auditor) |
| Multiple candidates on the table, no rubric | `fuyu` (comparator) | `shiki` verifier |
| Problem statement itself may be wrong | `aki` (assumption-auditor) | `natsu` or `fuyu` |
| A single load-bearing claim needs verification | `haru` (find failure modes) + `shiki` verifier | — |
| **High-stakes public artifact (commit, PR, doc), or ≥3 `load_bearing: true` claims expected** | **the full N-research fan-out + `shiki` + `reki`** | — |

`shiki` is mandatory at N≥2; `reki` is opt-in, family-diverse from
shiki, run in parallel with shiki over the same research YAMLs.

## Invocation (one-line summary)

Spawn N research subagents in parallel (N picked by failure shape,
default 1 if only one trigger fires, default 2-4 when both stuck and
load-bearing fire). When N≥2, spawn `shiki` (verifier, mandatory)
after. **Opt-in:** spawn `reki` (second verifier) in parallel with
shiki when the 2-verifier mode trigger fires. Read only the verifier
pair's `recommendation` + `open_questions_for_main_agent` — never the
raw research artefacts. Current model assignments and sampling live
in `references/model-picks.md`.

Full procedure and anti-patterns in `references/invocation-pattern.md`.
