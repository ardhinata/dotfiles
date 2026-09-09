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

## The six roles at a glance

| Role | Stance | Pick when |
|---|---|---|
| `haru` (adversarial, 春) | Leading answer is wrong | Failure-mode search, security review, the obvious answer is suspicious |
| `natsu` (synthesizer, 夏) | Propose the most coherent candidate | Need a candidate synthesis, or the answer space is open |
| `aki` (assumption-auditor, 秋) | List unjustified assumptions | The problem statement itself may be wrong, or hidden assumptions block progress |
| `fuyu` (comparator, 冬) | Compare candidates on a fixed rubric | Two or more candidates are on the table and no rubric exists |
| `shiki` (verifier, 四季) | Neutral arbiter; consolidates N research subagents | N≥2 research subagents ran; **mandatory** channel back to the main agent |
| `reki` (second verifier, 暦) | Independent verifier; family-diverse from shiki | 2-verifier mode: N≥3 research, ≥3 load-bearing claims, or public-artifact answer |

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
