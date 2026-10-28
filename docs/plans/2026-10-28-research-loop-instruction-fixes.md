---
status: active
goal: Bound research depth and move the decision question to the first decision point
owner: ardhinata
last-updated: 2026-10-28
---

# Instruction fixes for the overlong research loop

## Revision note

This plan was revised on 2026-10-28 after a verification pass over every
load-bearing claim in it. The revision is not cosmetic. It changes the
recommended phase order. It changes the recommended step-cap value. It
withdraws one of the four corrections the first draft made to the post-mortem.

The verification used four sources: the OpenCode v2.1.4 source tree, the
deployed rule files, the exported transcript of the incident session, and the
upstream sources the plan cites. Every harness claim below was checked against
them. The file and line numbers are in the sections that follow.

### What the verification changed

**1. The phase order was inverted. The prose edits ship first, alone.**
The first draft ranked its three levers correctly in prose, then applied them
in the reverse order. It also bundled four changes into one plan, so a single
observation cannot attribute the effect to any one of them. The revised plan
ships the prose edits as one unit, measures, then decides on the harness cap.

**2. The recommended step cap was 30. The measurement says 40.**
The first draft derived 30 from an assumed calls-per-message ratio and from a
tag range it read as a call count. The exported transcript gives the real
numbers. A cap of 30 stops the turn before the decisive read. See
[the measured turn profile](#measured-turn-profile).

**3. One of the four post-mortem corrections is a misquote and is withdrawn.**
The first draft wrote that `verify-before-claiming.md` "refuses a closing
self-report because a model can fabricate it". The rule does not say that. It
says a claim is only worth what a check proves. It says a cited path must come
from a file opened in this session. It says a command must show its exit code.
A call count is not a claim about correctness. The rule has no clause against
counting. The conclusion survives on a narrower ground: no check the rule
recognises can confirm the number, so it is unverifiable noise rather than
forbidden evidence. The Decisions section now uses that wording.

**4. The step cap has an unstated blast radius.** The ensemble plugin spawns
every teammate with `agent: "build"` (`src/tools/team-spawn.ts:73`), so a cap
on `build` also caps teammates. A teammate on a legitimate long task hits the
wall and is forced into a summary. The first draft's risk section did not
mention this.

**5. The two stop rules can collide.** The ask rule says to ask at the first
decision point. The no-progress rule says to stop after two probes of one
hypothesis. The phase that produced the reusable cache entry was a sequence of
lookups, not a hypothesis test. A naive reading of the no-progress rule cuts
it short. The revised rule adds a lookup exception.

## Goal

Stop a session from spending an unbounded number of tool calls on a question
that one user turn would settle. The trigger incident is
[the 2026-10-28 post-mortem](../post-mortem/2026-10-28-overlong-variant-research-loop.md):
196 tool calls, three user interrupts, and no requested change written.

This plan reviews that document, corrects its action items, and gives the
edits to apply.

## Scope

- In: the ask rule, the no-progress rule, the source-order rule, one harness
  step cap (deferred to phase 3), one knowledge-cache entry, corrections to the
  post-mortem.
- Out: the payload cut proposed by the 2026-10-25 review. Model choice. The
  Ponytail plugin. Any change to a compiled prompt inside `/usr/bin/opencode`
  or a plugin `dist/`.

## What the post-mortem gets right

Each row is checkable against a file, not against the incident transcript.

| Claim | Verdict | Evidence |
|---|---|---|
| No rule stops on research depth | Confirmed | No file under `~/.agents/rules/` or `~/.agents/rules.personal.d/` holds a depth or call budget. `grep -n "budget\|call limit\|stop after"` matches only `document-conventions.md:14` (doc length) and `ensemble-teams.md:14` (message size). |
| The ask rule has no when-to-ask clause | Confirmed | `dot_agents/exact_rules/ambiguity-resolution.md` is 13 lines and every clause is a "do not ask" clause. |
| The cache was not written | Confirmed | `.agents/docs/cache/README.md` has no `opencode` topic and no ensemble entry. |
| A question is cheaper than the research it prevents | Confirmed by external data | Table 1 of Anthropic's 2026-02-18 autonomy study puts "present the user with a choice between proposed approaches" at 35% of agent-initiated stops. "Claude was slow, hanging, or excessive" accounts for 17% of human interruptions across 500k Claude Code sessions. |
| A cost model is the missing piece | Supported | Calibrate-Then-Act (arXiv 2602.16699) reports that making a cost-uncertainty tradeoff explicit changes agent behaviour. It also reports that agents do not learn this from standard training. |

## What the post-mortem gets wrong

Three of its nine action items should not be applied as written.

**Item 6, the Code Mode catalog notice, is already fixed upstream.** The notice
in the live prompt comes from `packages/core/src/codemode/instructions.ts:13`
in tag `v2.1.4`. It already reads: "The catalog is partial. Inside `execute`,
use `search(...)` to find a tool, then call it by the `path` in the result."
The text is compiled into `/usr/bin/opencode`, so no chezmoi file can change it.

The post-mortem also paraphrases the notice wrongly. The notice says the only
callable tools are those listed **or returned by `search`**. It also says that
tools shown outside the catalog must be ignored inside `execute`. Those are
different statements.

The mechanism explains the miss without a prompt defect. `catalog.ts:49` sets
`INLINE_BUDGET = 2_000` characters. `rankListings` at `catalog.ts:175` orders
each namespace by line cost, cheapest first. A long signature is dropped from
the inline listing while it stays in the runtime inventory and remains
searchable. `tools.opencode.models` was hidden by its own signature length.

**Item 7, the AFT notice, needs no exception.** The injected notice bans
`grep`/`rg`/`find`/`sed`/`awk`/`cat` through shell. It then states "Keep `bash`
for shell facts (git state, file metadata, processes)"
(`aft-opencode@0.62.0/dist/index.js:51810`). `git show <tag>:<path>` is not in
the ban list, so the rule was followable. The notice text is also fixed in the
plugin bundle.

**Item 9, the Ponytail reply rule, is a misreading.** The injected text
constrains the *closing lines* of a reply, not the body: "End your reply with
one or two lines". A research reply can carry a table above those lines.

## What the instruction set and the harness actually contain

Measured today, deployed tree:

| Layer | Size | Owner | Editable |
|---|---|---|---|
| `~/.agents/rules/*.md` | 11 files, 15,814 B | chezmoi `dot_agents/exact_rules/` | yes |
| `~/.agents/rules.personal.d/*.md` | 9 files, 8,386 B | chezmoi `dot_agents/rules.personal.d/` | yes |
| `~/.config/opencode/rules/*.md` | 1 file | chezmoi `dot_config/opencode/rules/` | yes |
| Project `AGENTS.md` + `.agents/rules/` | 6,618 B | this repo | yes |
| Code Mode notice + catalog | ~2,000 chars | compiled binary | no |
| AFT notice | ~2,500 B | plugin `dist/` | no |
| Ponytail injection | 2,861 B | plugin | no |
| Skill catalog descriptions | ~4,100 B | `dot_agents/skills/` | yes |

The harness already holds three levers the post-mortem did not name.

1. **A hard step cap exists.** `agents.<id>.steps` is a `PositiveInt`
   (`packages/schema/src/config/agent.ts:23`). It maps to `agent.steps` at
   `packages/core/src/config/plugin/agent.ts:121`. The harness enforces it at
   `packages/core/src/session/runner/llm.ts:221`. On the last step it appends
   `MAX_STEPS_PROMPT`, sets `toolChoice: "none"`, and requires a text summary
   (`max-steps.ts:1`). The counter resets to 1 on every user message
   (`llm.ts:110`), so the cap is per user turn.
2. **A subagent cannot ask the user.** `general` denies the `question` action
   explicitly (`packages/core/src/plugin/agent.ts:69`). `explore` denies
   everything and re-allows a list that omits `question` (`:81`).
3. **A catalog search sees every tool.** `search` indexes each tool's path,
   description, and input property names
   (`packages/codemode/src/tool-runtime.ts:287-300`). This is independent of the
   2,000-character inline listing.

## Measured turn profile

The first draft estimated the step cap from an assumed calls-per-message
ratio. The exported transcript gives the real numbers. One step is one
assistant message. The export lives at
`opencode session export ses_e832c76f3ffeox8m2Uk63uQDG7`.

### The incident turn

| Measure | Value |
|---|---|
| Assistant steps in the first user turn | 105 |
| Tool calls in the first user turn | 165 |
| Calls per step | 1.57 |
| `question` tool calls in that turn | 0 |

The agent never asked. The question it eventually asked came three user
interrupts later, in a turn of 8 steps.

### Where a cap would land

| Cap | Steps used | Tool calls reached | What was known at that point |
|---|---|---|---|
| 30 | 30 | 40 | Still reading `promptAsync` in the server package. The plugin's variant handling was not yet read. |
| 35 | 35 | 48 | Read the generated client types. The variant split in `Model.Ref` was visible. |
| **40** | **40** | **56** | Read `v2-client.ts` at step 38 and confirmed that `switchModel` passes no variant. This is the decisive fact. |
| 50 | 50 | 75 | Past the decision point, into effort plumbing. |

A cap of 30 stops the turn before the decisive read. A cap of 40 stops it four
steps after. The first draft recommended 30 and claimed that 30 sat "near" the
decisive read. Measured, it does not.

### Legitimate work the cap would also cut

Per-turn step counts on this host, same export, incident turn excluded:

```
 11  7 14 18 22 19  3 59  4 14  4  8 20 74  7
```

Median 14. Two legitimate turns exceed 40: one at 59 steps (the plugin source
inspection) and one at 74 (the plan verification). A cap of 40 truncates both.
A cap of 60 truncates the second only. The largest legitimate turn is 74
steps, so any cap below 75 cuts real work on this host. Both outliers are
research-shaped turns, which is exactly the shape this plan targets.

## Refined approach

Three rules, in this order of value:

1. **Name the order of operations, not the depth.** The incident's first 30
   calls were source archaeology. A dependency README and a catalog search cost
   under ten calls and carry the answer. This is the root-cause fix the
   post-mortem names itself.
2. **Give the ask rule a trigger, so it stops being pure brake.** Five "do not
   ask" clauses and no "when to ask" clause is a one-sided rule.
3. **Let the harness own the stop.** One config line bounds a turn. A prose
   budget cannot.

Every edit lands in an existing file. The global rule payload is 24,200 B
already (30,818 B with the two project files). The evidence in
`.agents/docs/cache/agent-instructions/2026-10-26-always-on-instruction-files.md`
says constraint count, not byte count, is the axis that degrades adherence.
Two new 20-to-30-line files would add 50 constraints to buy one.

The value order above is not the application order. The prose edits are cheap to
revert. The step cap changes how every session on this host behaves.

## Implementation steps

### Phase 1 — prose edits, shipped as one unit

No config change. Three edits to existing files. This phase is the whole point
of the plan. Measure it before touching the harness.

#### Give the ask rule a trigger

Edit `dot_agents/exact_rules/ambiguity-resolution.md`. Keep the first line and
the whole "Do not ask" list. Insert one section after line 3.

```markdown
Ask the user when the answer changes what you do next.

## When to ask

Ask at the first decision point that meets all three tests:

- Two or more outcomes change what you write, not how you phrase it.
- The cheapest check is done: the manual, the tool description, and one source
  read.
- The remaining search space is open. No named file, flag, or document closes
  it.

A question costs one user turn. The research that replaces a question has no
upper bound. Bias toward the question.

Report a spec deviation as soon as you find it, with the options you found. Do
not finish the research first.

State the next question before the next batch of calls. Keep one question per
phase. Do not mix a harness question with a task question.

## Do not ask
```

Add one clause to the "Do not ask" list, after the over-ask clause:

```markdown
- Do not ask twice in one phase. One question per decision point.
```

#### Give the no-progress rule a second trigger

Replace the body of `dot_agents/exact_rules/no-progress-stop.md` with:

```markdown
# No Progress Stop

Stop when the evidence stops. Report what blocked you. Stop at two. Do not run
a third attempt.

## Two triggers

- **Same failure twice.** The same step fails twice with the same error. A
  different error message counts as new progress.
- **Same hypothesis twice.** Two consecutive probes of one hypothesis add no
  new information. The output text may differ. The finding must not.

Name the hypothesis, and the result that would falsify it, before the first
probe. A second probe with no falsifier hit ends that hypothesis.

A lookup is not a probe. Reading a second file, a second catalog entry, or a
second source to collect facts about a named target is one lookup with several
reads. Stop only when a second lookup at the same target also stops narrowing
the answer.
```

The lookup exception is new. Without it the rule cuts against the phase that
produced the reusable cache entry. The models.dev facts came from a sequence of
lookups at one target, not from repeated tests of one hypothesis.

#### Put a dependency in the local-first order

Edit `dot_agents/exact_rules/local-first.md`. Insert after the priority list,
before "## Anti-Patterns":

```markdown
## A dependency is a local source

When the question is about an installed package, plugin, or CLI, its own docs
come before its source. Read the package README, the `--help` text, or the
config schema. The same order applies to the harness: search the tool catalog
before you read harness source.

To answer from a specific revision, `git show <tag>:<path>` is the correct
read. It is a shell fact, not a source search.
```

Why not a new file: `README.md` is already item 1 of this rule. The gap is
scope. The rule says "the project's docs" and says nothing about a dependency.

#### Verify and deploy phase 1

1. `chezmoi diff` — expect three rule files and no config file.
2. Read each edited source file back. Confirm the new sections are present.
3. Run `chezmoi apply --dry-run`. Report the plan.
4. **Ask the user to run `chezmoi apply`.** It is a destructive action under
   `destructive-actions.md` and the agent must not run it.
5. Read `~/.agents/rules/ambiguity-resolution.md` back after apply. Confirm the
   deployed copy matches the source.

#### Measure phase 1

Watch the next two research-shaped turns. The single question to answer: did
the agent ask within 30 steps? A pilot cannot measure adherence statistically
here. The 2026-10-25 review already showed that 8 to 12 tasks at 3 runs cannot
detect an adherence difference. Judge by the first turn that looks like the
incident.

If the answer is yes, phase 3 may not be needed.

### Phase 2 — knowledge-cache entry

Create `.agents/docs/cache/opencode-harness/2026-10-28-ensemble-model-pool-variant.md`.
Add one `### opencode-harness` section to `.agents/docs/cache/README.md`.

The entry records these verified facts:

- `modelPool` is `string[]` (`src/config.ts:27,71` in
  `@hueyexe/opencode-ensemble@0.20.0`). Each entry is rendered verbatim as a
  `question` option label (`src/system-prompt.ts:104-105`).
- `parseModelId` splits at the first `/` and keeps the remainder as `modelID`
  (`src/member-model.ts:14-18`). A `#variant` suffix therefore stays inside the
  model id. `openrouter/minimax/minimax-m3.1-flash#high` in the pool fails the
  model lookup instead of selecting the variant.
- Resolution order is `args.model` first, then `modelsByAgent`, then the
  rotate/random pool, then `defaultModel` (`src/tools/team-spawn.ts:16-31`).
  `team-spawn.ts:416-427` passes `{providerID, modelID}` only when it parses.
- The V2 client applies that model with
  `ctx.session.switchModel({ model: { providerID, modelID } })`
  (`src/v2-client.ts:216-219`), so no variant reaches the session.
- A session created with a bare provider/model gets
  `session.model.variant = "default"` (`packages/core/src/session/info.ts:30`).
  That is neither the root `#high` pin nor the model's own default.
- The HTTP API can carry a variant. `session.create` takes a `Model.Ref`
  (`packages/protocol/src/groups/session.ts:162`). `Model.Ref.parse` splits
  `#variant` correctly (`packages/schema/src/model.ts:27-41`). The plugin never
  builds one. An upstream patch is possible. Version 0.20.0 has none.
- To pin effort on a teammate today, set `agents.<agentName>.model` with a
  variant in the config. Pass no model from the pool. A session-level model
  beats an agent-level one (`packages/core/src/session/runner/model.ts:80-95`).

Index row:

```markdown
### opencode-harness

- [2026-10-28 — the ensemble model pool cannot carry a `#variant`](opencode-harness/2026-10-28-ensemble-model-pool-variant.md) — ...
```

### Phase 3 — harness step cap, decided on its own evidence

Deferred from phase 1 on purpose. Apply only if phase 1 did not stop the
behaviour. Re-measure the turn profile first, because phase 1 changes the
shape of the turns the cap would be sized against.

The value is **40**, not 30, for the reason in the measured table above.

```jsonc
  "agents": {
    "build": {
      // One step is one assistant message. The counter resets on each user
      // message, so this bounds a turn, not a session. At the cap the harness
      // disables tools and forces a text summary.
      //
      // 40 is the measured value: the incident's decisive read landed at step
      // 38. A cap of 30 stops before it.
      //
      // This also caps ensemble teammates, which run as build. A teammate on a
      // long task hits the wall and is forced to summarize.
      "steps": 40
    },
    "title": { ... }
  }
```

Two known costs, both measured:

- Legitimate work on this host reaches 59 and 74 steps. A cap of 40 truncates
  both. Raise the cap to 75 if a real task gets cut off.
- The cap binds teammates, because the ensemble plugin spawns them as `build`
  (`src/tools/team-spawn.ts:73`).

### Phase 4 — correct the post-mortem

Edit `docs/post-mortem/2026-10-28-overlong-variant-research-loop.md`:

1. Leave `status: open`. The plan is not the resolution of the incident, and
   editing a document does not close the incident.
2. Replace the "Action items" list with a pointer to this plan. Keep the
   corrections that hold: item 6 is already upstream, item 7 is not needed, and
   item 9 misreads the Ponytail text.
3. Add the two facts this plan's measurement produced. The post-mortem could
   not know them. The incident's first turn ran 105 steps and 165 calls with
   zero `question` calls, and the decisive read was at step 38.

A known-wrong action list in a document marked authoritative is a trap for the
next agent.

### Phase 5 — verify and deploy

1. `chezmoi diff` — expect three rule files, one cache entry, and one config
   file if phase 3 was applied.
2. Read each edited source file back. Confirm the new sections are present.
3. Run `chezmoi apply --dry-run`. Report the plan.
4. **Ask the user to run `chezmoi apply`.** It is a destructive action under
   `destructive-actions.md` and the agent must not run it.
5. Read `~/.agents/rules/ambiguity-resolution.md` back after apply. Confirm the
   deployed copy matches the source.

## Risks and mitigations

- **A step cap truncates real work.** Measured: legitimate turns reach 59 and
  74 steps. Mitigation: the forced summary keeps the work, and the user's next
  message resets the counter to 1. Verify on one multi-file task before
  keeping 40.
- **The step cap also binds teammates.** The ensemble plugin spawns every
  teammate as `build`. Mitigation: none available in config. The lead can pass
  a different `agent` to `team_spawn`, and the cap follows the agent id.
- **A looser ask rule invites over-asking.** Mitigation: the three tests are
  conjunctive, and one clause caps it at one question per phase.
- **Two stop rules disagree.** Mitigation: `no-progress-stop.md` owns "the
  evidence stopped moving" and now excepts lookups. `ambiguity-resolution.md`
  owns "a decision point appeared". Neither mentions the other.
- **The three tests are still prose, and the model can self-certify.** Stated
  honestly: this is one of the two levers that cannot be enforced. Only phase 3
  is enforced by code.
- **Shipping four changes at once hides which one worked.** Mitigation: phase 1
  ships alone and is measured before phase 3.

## Open questions

1. Is the cache README's stale mention of `tavily_*`, `firecrawl_*`, and
   `context7_*` worth fixing in the same pass? Those tools are gone. Out of
   scope here.
2. Should the step cap be measured again after phase 1 ships? The turn
   distribution changes once the agent asks earlier, so the value sized in
   phase 3 may be stale by the time it is applied. Recommendation: re-measure.
3. Does a cap on `build` survive a `default_agent` change? `default_agent` is a
   real config key (`packages/schema/src/config.ts:36`). The cap lives on the
   agent, so a different default agent with its own cap is possible. The
   plugin's `defaultModel` and the session's model are separate layers.

## Decisions

- 2026-10-28: Do not add the two new rule files that action items 1 and 3 ask
  for. Extend three existing files instead. Payload and constraint-count
  evidence, above.
- 2026-10-28: Do not edit a compiled prompt. Items 6 and 7 target text inside
  the binary and the plugin bundle.
- 2026-10-28: Do not require a closing call count. No check the rule
  recognises can confirm the number, so it is unverifiable noise. This
  supersedes the first draft's wording, which misquoted
  `verify-before-claiming.md` as refusing self-reports.
- 2026-10-28: Ship the prose edits before the harness cap. The first draft
  applied the cap first and bundled all four changes, which makes the effect
  of any one of them unmeasurable.
- 2026-10-28: Size the step cap at 40, not 30. The measured decisive read was
  at step 38 of the incident turn. The first draft's 30 came from an assumed
  calls-per-message ratio. It stops the turn before the decisive fact.
- 2026-10-28: Add the lookup exception to the no-progress rule. The facts
  that produced the cache entry came from a sequence of lookups at one target.
  A naive reading of the rule cuts it short.

## Deferred notes

- The post-mortem's own call counts and tag numbers were not re-derived from
  the transcript before the first draft of this plan. They are now.
- A pilot cannot measure this change statistically. Judge by whether the next
  research-shaped turn asks within 30 steps.
- The step cap was not measured against the two legitimate outliers (59 and 74
  steps). Both are research-shaped turns, so the cap's real cost on this host
  is unknown until phase 1 changes the distribution.

## Current status

Phases 0 to 5 are written and not applied. The verification pass on
2026-10-28 changed the phase order, the recommended step cap, and one
correction to the post-mortem. Waiting on phase 1 to be applied and measured
before phase 3 is decided.
