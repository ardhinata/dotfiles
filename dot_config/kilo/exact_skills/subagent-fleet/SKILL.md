---
name: subagent-fleet
description: >
  Load when an agent wants to invoke the haru/natsu/aki/fuyu/shiki
  subagent fleet for stuck-task recovery or load-bearing verification,
  or when an agent in another project needs the fleet design, role
  definitions, invocation pattern, or model assignments. Triggers:
  "use a subagent", "launch the fleet", "haru", "natsu", "aki", "fuyu",
  "shiki", "verifier", "second opinion", "adversarial review", "compare
  candidates", "audit assumptions", "load-bearing claim", "stuck task".
  Key terms include subagent, fleet, four seasons, RCAF, verifier,
  research subagent, parallel fan-out.
---

# Subagent Fleet Skill

Portable reference for the haru/natsu/aki/fuyu/shiki subagent fleet.
The fleet provides stuck-task recovery and load-bearing verification
through 4 prompt-conditioned research roles + 1 verifier. This skill
is the entry point; the canonical plan is the source of truth.

## When to load

- An agent wants to invoke one or more research subagents and needs to
  pick the right role for the failure shape.
- An agent needs the fleet's invocation pattern (N research + shiki at
  N≥2).
- An agent needs the current model assignments or permission block.
- A new project Kilo instance needs the fleet essentials without
  reading the full plan.

## Source of truth

The canonical plan is
`.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md` in the
chezmoi repo (`~/.local/share/chezmoi/` on machines with the dotfiles
repo applied). When that file is reachable, treat it as authoritative
and ignore the bundled references. When it is not reachable (other
projects), use the bundled references below as the source of truth.

## References

Load on demand. Do not load all of them at once.

| File | Load when |
|---|---|
| `references/fleet-roles.md` | Picking which role fits the failure shape (haru/natsu/aki/fuyu/shiki). |
| `references/invocation-pattern.md` | About to spawn research subagents — need the N-research + shiki rules and the output contracts. |
| `references/model-picks.md` | Need the current model id, family, `variant:`, or sampling tilt for each role. |
| `references/permission-block.md` | Need the permission allowlist shared by all 5 subagents (or the operational discipline preamble). |

## The five roles at a glance

| Role | Stance | Pick when |
|---|---|---|
| `haru` (adversarial, 春) | Leading answer is wrong | Failure-mode search, security review, the obvious answer is suspicious |
| `natsu` (synthesizer, 夏) | Propose the most coherent candidate | Need a candidate synthesis, or the answer space is open |
| `aki` (assumption-auditor, 秋) | List unjustified assumptions | The problem statement itself may be wrong, or hidden assumptions block progress |
| `fuyu` (comparator, 冬) | Compare candidates on a fixed rubric | Two or more candidates are on the table and no rubric exists |
| `shiki` (verifier, 四季) | Neutral arbiter; consolidates N research subagents | N≥2 research subagents ran; mandatory channel back to the main agent |

## Invocation (one-line summary)

Spawn N research subagents in parallel (N picked by failure shape, default
1 if only one trigger fires, default 2-4 when both stuck and load-bearing
fire). When N≥2, spawn `shiki` (verifier, `minimax-m3`, `variant: high`)
after. Read only shiki's report — never the raw research artefacts.

Full procedure and anti-patterns in `references/invocation-pattern.md`.
