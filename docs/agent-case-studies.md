---
title: Agent design case studies
date: 2026-10-23
last-updated: 2026-10-23
status: active
related:
  - docs/subagent-fleet/README.md
  - docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md
  - docs/assist-only/constitution.md
---

# Agent design case studies

## Why this document exists

Seven agents were written for the Kilo harness between 2026-08 and 2026-09:
the six research-fleet members (`haru`, `natsu`, `aki`, `fuyu`, `shiki`,
`reki`) plus the read-mostly primary agent `assist-only`.

On 2026-10-23 the OpenCode migration was scoped down. The fleet is **not**
being ported to OpenCode: the harness already ships `general` and `explore`
subagents, and the fleet's marginal value did not justify a second parallel
agent system with its own permission model and its own output contract.

That decision is not a reason to lose the design work. Every rule below was
paid for with a model re-evaluation cycle and a revalidation pass. This
document harvests them so the next agent — for any harness — starts from
what worked instead of from zero.

It is a **case study**, not a spec. The agents it describes remain live in
Kilo (`dot_config/kilo/exact_agent/`); the canonical fleet design remains
[`docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`](subagent-fleet/2026-08-17-subagent-creative-conservative.md).

## The seven agents at a glance

| Agent | Role | Mode | Model | `steps` / `maxTokens` |
|---|---|---|---|---|
| `haru` (春) | Adversarial — top failure modes | subagent | `deepseek-v4-flash-0731` | 30 / 6144 |
| `natsu` (夏) | Synthesizer — candidate answers | subagent | `glm-5.3-flash` | 30 / 6144 |
| `aki` (秋) | Assumption-auditor | subagent | `deepseek-v4-flash-0731` | 30 / 6144 |
| `fuyu` (冬) | Comparator — ranked rubric | subagent | `glm-5.3-flash` | 30 / 6144 |
| `shiki` (四季) | Verifier 1 | subagent | `deepseek-v4-flash-0731` | 50 / 8192 |
| `reki` (暦) | Verifier 2 | subagent | `glm-5.3-flash` | 50 / 8192 |
| `assist-only` | Read-mostly principal engineer | primary | `minimax-m3` | — |

The research agents share one model per stance (`haru`/`aki` adversarial-ish
cheap flash, `natsu`/`fuyu` synthesis-ish cheap flash); the verifiers are
deliberately split across families.

## Case studies

### haru — the adversarial role earns its keep only with evidence

`haru` assumes the leading candidate answer is wrong and returns the top
three failure modes.

The load-bearing rule is **evidence-or-drop**:

> If you cannot point to evidence, drop the finding — speculation is not
> useful for the verifier.

This is what separates an adversarial role from a worrier. An agent that
returns "this might be a security issue" with no pointer adds noise that the
verifier must filter, and filtering is the expensive step. The cap of three
findings is the second half of the same idea: **more is noise; the verifier
filters anyway.**

The contract adds two fields that pay for themselves downstream:

- `confidence` (0.0–1.0) — the verifier's Pass 1 threshold is `≥ 0.6`, so
  the researcher pre-sorts the work.
- `load_bearing: true` — set when the failure mode threatens security,
  correctness, or cost. This flag alone decides whether the verifier pays
  for a deep web search.

**Lesson.** An adversarial role is only worth a spawn if its output is
checkable. Pair the stance with an evidence requirement and a hard cap, or
do not spawn it at all.

### natsu — require the reasoning, not just the claim

`natsu` proposes candidate answers. Its contract adds a `reasoning_summary`
field that `haru` does not have.

The reason is downstream arbitrage. A verifier cannot adjudicate between
two bare claims — it can only pick one or reject both. A two-to-three
sentence rationale gives the verifier something to check, so it can reject
the reasoning while keeping the claim.

`natsu` is also ranked by **coherence, not novelty** — the most defensible
candidate goes first. A synthesizer that puts its most creative answer at
the top makes the verifier's job harder for no gain.

**Lesson.** If a downstream agent consumes this output, put the reasoning in
the contract, not in the agent's head.

### aki — scope exclusions stop the agent restating the prompt

`aki` lists the assumptions the problem statement and candidates rely on but
never justify.

Its own anti-pattern list contains the rule that makes it work:

> Don't surface assumptions that are explicit in the problem statement —
> your job is the **hidden** ones.

Without that exclusion, an assumption-auditor degenerates into a paraphrase
of the input. Findings are also ranked by `likely_wrong` × impact, which is
a different ordering than `haru`'s likelihood × impact — a hidden assumption
can be very likely to be wrong and still not matter.

**Lesson.** Every agent that audits something needs an explicit exclusion for
the trivial case. State what is out of scope in the contract, not in the
preamble.

### fuyu — minimums beat open-ended instructions

`fuyu` compares two or more candidate approaches on a fixed rubric.

Two rules make it more than a ranker:

- **At least three criteria.** "Comparison without multiple axes is just
  ranking by gut."
- **Ties must be surfaced.** If two candidates land within 0.05 on the
  total, the report must say so explicitly.

The tie rule is the important one. An agent asked to rank will always
produce a ranking, even when the inputs do not support one. Requiring the
agent to report a tie forces it to disclose when its own output is not
meaningful, which is information the caller needs.

**Lesson.** When an agent can produce a wrong-shaped output no matter what,
constrain the shape (minimum axes) and require it to declare when the
output does not apply.

### shiki — tier the verification cost, and refuse bad input

`shiki` reads the research artefacts and produces one consolidated report.

**Two passes, priced by stakes.** Pass 1 (shallow) re-reads each cited
`file:line` or URL — no execution. Pass 2 (deep) runs a fresh web search
and cross-checks, but only for claims flagged `load_bearing: true` or left
`inconclusive` by Pass 1. Verification cost scales with the claim's
consequence, not with the claim count.

**Refusal is a feature.** Before Pass 1, `shiki` checks each research
YAML's `status`. On `status: partial` it refuses: it marks the claims
`N/A`, emits one escalation item, and does not run either pass. The
opt-out to proceed anyway must be an explicit flag in the parent's task
prompt — absence of the flag means refuse. The refusal exists because a
verifier asked to summarise half-finished research launders it into a
confident report.

**Lesson.** An agent that consumes other agents' output needs a stated
policy for degraded input, and the default has to be the conservative one.

### reki — diversity by model family, disagreement as the product

`reki` is the second verifier, paired with `shiki`.

The design lever is **family diversity**, not sampling. `reki`'s own
anti-pattern list forbids it:

> Don't run with a single-model sampling split from shiki (e.g. the same
> model with a different temperature) — same-model instances share
> training-data blind spots and the disagreement signal is noise-prone.

**They must not see each other.** In the canonical parallel mode `shiki`'s
YAML is not on disk when `reki` runs, so the anchor risk is against
`reki`'s *anticipation* of `shiki`, not against `shiki`'s text. This turns
out to be the strongest constraint in the fleet: it removes the cheapest
route to two agreeable verifiers.

**Disagreement is the deliverable.** `reki` must not silently agree. If it
accepts every claim, the most likely cause is its own anchoring, so it
re-reads at least one original source per run. When verdicts differ, the
difference goes into `disagreements_with_reki` and the main agent resolves
it. The verifier never resolves it.

**Lesson.** A second reviewer only pays for itself if it is decorrelated
from the first. Block the cheapest decorrelation (seeing the other's
output), and make disagreement a required output rather than a tolerated
one.

### assist-only — hold the persona divergence, and carve out the trivial channel

`assist-only` is a `primary` agent, not a subagent. It is a read-mostly
principal engineer: the user writes production code, the agent challenges.

**The divergence is explicit and defended.** Upstream spec-kit / Kiro
guidance has the *agent* generate `spec.md` / `plan.md` / `tasks.md` and the
*human* review them. This mode inverts it. The agent body says why, in
advance, so it does not drift toward agent-generated prose to be helpful:
"because then we lose the friction that forces you to think it through."

**The permission map is a deny-list, not an allow-list.** Sensitive paths
are denied explicitly — `.age`, `.asc`, `.encrypted_data/`, `dot_ssh/keys/`,
and anything matching `token`, `secret`, `credential`, `password`, `key`,
`cert`, `pem` — with a wildcard allow underneath. A session-start
non-skippable reminder restates the rule to the user, so the technical
backstop has a matching audit trail.

**One named exception, with a marker.** Demonstrative code is allowed, but
only under `.tmp/scratch/assist-only/<slug>/`, only with a
`REFERENCE — not for merge` header, and only announced with a `REFERENCE:`
banner. Inline patches in chat are refused even when asked directly: "the
boundary does not bend for convenience."

**The trivial-channel carve-out** is the most reusable rule here. Some
outputs mutate state; others only re-shape information the user already has
access to (transcripts, JSON dumps, stack traces, prompt text). The test is
one sentence — *does the request mutate state, or re-shape information you
already have?* — and it resolves a whole class of requests without a
per-case rule.

**Lesson.** A persona that inverts a dominant pattern has to defend itself
in the body, or it drifts. A hard boundary needs exactly one named
exception, and a carve-out for information-only work beats a long
exclusion list.

## Transferable rules

1. **Roles must be disjoint.** Every agent's anti-pattern list names its
   siblings' jobs. Without that, a fan-out produces four overlapping
   opinions instead of four views.
2. **Evidence or drop.** No finding without a pointer. Speculation costs the
   consumer more than it gives.
3. **Hard caps on output.** Three findings, four criteria. The consumer
   filters; the producer should not dump.
4. **File-based handoff.** The YAML artefact is canonical. Message content
   is a marker (for continuation) and a fallback echo, never the payload.
5. **Tier verification by stakes.** Shallow re-read for everything, deep
   fresh search only for load-bearing or inconclusive claims.
6. **Refuse degraded input by default.** An opt-out must be explicit, never
   inferred from context.
7. **Decorrelate reviewers by model family.** Sampling tweaks are not
   diversity. Block reviewers from seeing each other's output.
8. **Sandbox in the runtime, not in the prompt.** The permission map does
   the work; the prompt states it for the audit trail.
9. **Read-only by default; mutations confined to a scratch directory.** The
   parent owns every change to the user's tree.
10. **One test for the trivial channel.** Re-shape versus mutate.
11. **Require the reasoning field when a downstream agent arbitrates.**
    Claims without rationale cannot be adjudicated.
12. **State the exclusions.** An auditing agent needs to be told what the
    trivial case is.

## What we would do differently

**Extract the shared permission block.** All six fleet agents carry a
byte-identical 40-line permission map (verified: same checksum across
`haru`, `natsu`, `aki`, `fuyu`, `shiki`, `reki`) — including the two
verifiers, whose roles and step budgets differ. The canonical design
already calls it a shared block (§6), so the implementation drifts from its
own spec. A permission block duplicated across files is a security bug
waiting to happen: one edit lands in six of seven places.

**Stop copy-pasting the output contract.** The "Batched output" and
"Continuation protocol" sections repeat across the four research agents
with only the noun swapped (`findings` / `candidates`). Same drift risk,
same cost.

**Gate the second verifier.** Two verifiers double the cost of every
question to produce a disagreement signal that only appears on load-bearing
claims. Running `reki` only when Pass 1 leaves at least one
`load_bearing: true` claim would cut cost and lose nothing.

**Prefer two research roles over four, until a case justifies more.** The
fourth research role's marginal contribution dropped after the model
re-evaluation. Two roles plus a verifier is the smallest fan-out that
still produces structural disagreement.

**Pick token caps from the model's real ceiling.** `maxTokens: 6144` was a
round number chosen before the final model picks. The caps now sit close to
the models' actual output ceiling, so the batch-and-continue path fires
often — it is a normal path, not an edge case, and should be budgeted for.

## Related

- Canonical fleet design: [`docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`](subagent-fleet/2026-08-17-subagent-creative-conservative.md)
- Fleet index and pointer maintenance: [`docs/subagent-fleet/README.md`](subagent-fleet/README.md)
- Agent sources (still live in Kilo): `dot_config/kilo/exact_agent/`
- assist-only constitution: [`docs/assist-only/constitution.md`](assist-only/constitution.md)
