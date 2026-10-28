---
severity: medium
status: open
date: 2026-10-28
---

# Overlong research loop on the OpenCode variant question — post-mortem

## Summary

The user asked for two changes to the OpenCode configuration. The first change needed one token in one file. The second change needed one question.

The agent made 196 tool calls for this task. The user interrupted three times. No requested change reached the file.

The research did answer the question. It answered it about 130 calls later than it needed to.

Three findings carry the cost.

1. The plugin documentation answered the central question. The agent read that document 30 calls into the research.
2. The decisive tool call appeared in the first catalog search result. The agent used that tool 30 calls later.
3. A tangent about the harness consumed 40 calls and one background job. AFT killed that job after 30 minutes. It gave no result for the task.

No rule controlled when to stop. The agent stopped because the user told it to.

## Scope

The task: set the OpenCode default model to medium. Set the pool variant to medium for every entry in the ensemble model pool.

The agent worked from a clean research question. The task had a small decidable core and one research question with a discoverable answer.

The agent did not ask a question until after the research finished. The user had to ask for the question explicitly.

## Timeline

| Phase | Tags | Calls | Outcome |
|---|---|---|---|
| A. Harness and plugin names | 238–277 | 40 | Tangent. One job killed after 30 min |
| B. Core variant mechanism | 279–327 | 49 | The decisive fact. The plugin drops the variant |
| C. Provider packages in the checkout | 328–363 | 36 | Negative result. 12 calls on one hypothesis |
| D. Model catalog | 364–367 | 4 | The variant table. This belonged in phase one |
| E. Effort plumbing | 368–404 | 37 | Needed only for the option chosen at the end |
| F. After "wrap it faster" | 406–427 | 22 | The same work continues |
| G. After "ask me if out of spec" | 429–436 | 8 | The same work continues |
| H. The question | 438–439 | 0 | One turn, one answer |

Call counts by tool: 108 shell, 38 grep, 35 read, 12 execute, 1 aft_zoom, 1 ctx_reduce.

Three user interrupts sit inside that window:

- Tag 405: `Can you wrap-it faster?`
- Tag 428: `Ask me if there's out of spec`
- Tag 437: `Halt for a sec`

## Finding 1 — When to ask the user, and does asking make the task faster

**The answer is yes on both counts, and the question came 138 calls too late.**

The question at tag 438 was the right question. It named the real constraint. It offered four implementations that conflict with each other. It put the recommended option first. The user answered it in one turn. That answer selected the implementation path and ended the research.

The facts that made the question answerable existed at tag 290. The read at that tag showed the plugin call `switchModel` with a provider and a model id. It carried no variant. The read at tag 351 showed the OpenCode config schema accept a `#variant` suffix. Those two reads together are enough to state the constraint.

So the earliest defensible moment to ask was tag 300. The agent asked at tag 438. The gap is 138 calls.

Does asking make the task faster? Yes, by a wide margin.

| Path | Cost |
|---|---|
| Ask at tag 300 | 60 calls, then 1 question, then about 15 calls to implement |
| Ask at tag 438 | 196 calls, then 1 question, then about 15 calls to implement |

The question cost one turn. The research that avoided the question cost 138 extra calls and two user interrupts.

The instruction set pushes the wrong way here. `ambiguity-resolution.md` says to ask only when the answer changes what you do next. The same file warns that three asks in a row mean the agent is doing the user's job. Both clauses are correct. Neither clause says when to ask. The agent read them as a brake on asking. In this task the question was the cheap action and the research was the expensive one. The rule gives no price for either.

A rule that fits both clauses reads like this.

> Ask as soon as a decision point appears with two or more materially different outcomes, and the cheapest check is complete. One question costs one turn. The research that a question would prevent costs an unknown number of turns.

A second rule that fits the same clauses reads like this.

> Report a spec deviation as soon as you find it, with the options you found. Do not finish the research first.

The user asked for exactly this at tag 428, after the agent had already finished the research. The rule moves the question forward by 138 calls.

## Finding 2 — The longest stretch on one problem

**Phase C, tags 328–363. 36 calls, 12 of them on one hypothesis with no new information.**

The hypothesis: the `opencode-go` provider has a checked-in package in the OpenCode source tree.

The agent searched `packages/core/src`. Then it searched the whole `packages/` tree. Then it searched `packages/core/src/plugin/provider/`. Then it added a sparse checkout for `packages/providers`. Then it ran two `git ls-tree` calls. Then it searched again in `packages/core/src/*.ts`, in `packages/core/src/provider.ts`, and in `packages/schema/src/provider.ts`. Then it ran another sparse checkout, listed `packages/ai/src`, and searched the whole repo for the provider id.

The provider has no checked-in package. The `opencode-go` provider comes from the models.dev catalog. Its package is `@opencode/ai/providers/openai-compatible`. That fact was in the models.dev payload the agent fetched at tag 423. It was also in the catalog output the agent printed at tag 429.

The negative result was knowable in two calls. One `git grep` for the provider id across the tree shows a single hit in `packages/core/src/model.ts` and no hit in any provider directory.

Phase A, tags 238–277, took 40 calls. A visible part of it chased the harness `bash_status` tool. The probe at tag 249 scanned the npm cache tree. That command ran past 15 seconds, became a background job, and AFT killed it after 30 minutes. It gave no answer about the task.

Two problems compound here. The agent had no rule for a failed search. `no-progress-stop.md` fires only when the same step fails twice with the same error text. Six probes of one hypothesis each returned different output, so the rule never fired. The rule needs a second trigger.

> Stop when two consecutive probes of one hypothesis add no new information, whatever the output text says.

The second problem is that the phase mixed two unrelated questions. The harness question and the variant question share no evidence. The rule set has no statement that one session turn serves one question.

> Keep one question per phase. State the next question before the next batch of calls.

## Finding 3 — Contradictory system messages

Four places in the instruction set pull in different directions. Two come from harness text. Two come from house rules.

### 3.1 The Code Mode catalog versus the direct tools

The Code Mode notice says that the agent cannot call the listed tools directly. It says that tools shown outside the catalog do not exist inside an execute block. The catalog was partial. It listed 8 opencode tools and showed 5. The tool that answered the central question, `tools.opencode.models`, was not among the 5 shown.

The consequence is real. The agent searched the catalog for the tool it needed, and the search returned it at tag 239. The agent then used shell and grep on the OpenCode checkout for 30 calls before it called that tool at tag 365.

The fix is small. The catalog notice could name the search rule in one line.

> The catalog is partial. Search it for the tool that answers the question before you read source code.

### 3.2 The AFT notice versus reading a tagged revision

The AFT notice forbids shell for code search and points at `aft_search`, `aft_outline`, and `aft_zoom`. It offers a `path` argument for another project. The AFT notice cannot read a git tag. The task needed the file content at tag v2.1.4, and `git show v2.1.4:path` was the only accurate route.

So the rule was partly unfollowable, and the agent did not say so. It also did not use `aft_search` with `path` for the untagged questions. That tool was available and gives ranked results.

The rule can keep its intent and state the exception.

> Use `aft_search`, `aft_outline`, and `aft_zoom` for code reads. Use `git show <tag>:<path>` when the answer must come from a specific revision. State the exception in your reply.

### 3.3 The research budget against "do a research when necessary"

The user asked for research. No rule caps the depth. The Ponytail injection says to read the code the change touches. Its reply rule asks for one or two lines at the end. Neither sets a limit.

The result is what the report describes. The agent read 196 tool results and no rule objected. Only the user stopped the loop.

### 3.4 The knowledge-cache rule against the reuse of findings

`web-verification.md` asks the agent to write a dated cache entry after any lookup that produces reusable information. It asks the agent to read the cache index first. The agent did neither. The ensemble plugin cannot carry a `#variant`. That fact is reusable, and it is not cached. The next session pays the same 138 calls again.

The rule was live and loaded. It lost to the pull of the current task.

## Finding 4 — Faster options that the instruction set limited or forbade

Four options were available. The instruction set points at three of them. The agent used none of them for the first 30 calls.

**The catalog search.** `search()` inside `execute` finds tools by capability. The agent ran it at tag 239 and read the result. The result named `tools.opencode.models`, the tool that lists every model with its variants. The agent used it at tag 365. The gap is 126 calls.

**The delegated research tool.** `long-running-tools.md` lists `subagent` as the delegated research facility for OpenCode. The harness notice also says to fan out to a research subagent for multi-source synthesis. The task spanned three codebases: the plugin package, the OpenCode core, and the models.dev catalog. The agent used one serial thread for all three.

**The plugin README.** The npm package ships a README next to `dist/`. Its config table lists the model pool keys. Its model section states the resolution order and the `provider/model` format. That is the answer to the central question, in prose, in one read. The agent read it at tag 307, after 70 calls.

**The direct answer in the first reply.** The agent could reply at tag 240 with the change it can make, the constraint it found, and one question. That reply costs one turn. The task was two tokens and one question.

One more limit deserves naming. The `question` tool rule says to ask one question at a time when the answers depend on each other. The agent asked one question with four options, so the rule was met. The tool was never the problem. The timing was.

## Root cause

The task had a small decidable core and one research question with a discoverable answer. The instruction set gives no bound on research depth. It names no moment when the answer is known enough to ask.

So the stopping point came from the agent's own confidence rather than from a rule. Confidence rises with evidence. The agent gathered evidence past the point of usefulness because no rule said to stop. The OpenCode source tree is also large enough to suggest a plausible next step at every turn.

The second root cause is the first step. The agent began with source archaeology instead of the plugin README and a tool catalog search. Both produce the answer in under ten calls. A rule that names the order of operations fixes this more reliably than a rule that caps depth.

## Impact

- 196 tool calls for a change that needs two tokens and one question.
- 108 of those calls ran shell commands. 38 ran grep. 35 read files.
- One background job ran 30 minutes and was killed with no result.
- Two user interrupts asked for speed. The third asked for a stop.
- Zero requested changes reached the configuration file.
- The knowledge cache has no entry about the plugin model handling. The next session pays the same cost.
- The working tree still holds two uncommitted files from the earlier task in this session: `dot_config/opencode/private_opencode.jsonc` and `dot_config/zed/private_settings.json`.

## Action items

Each item names the file to change and the change to make. The first three carry most of the value.

1. **Add a research budget to the instruction set.** Add a rule file under `~/.agents/rules/`. Set a call limit for research tasks. Require the agent to state the planned number of calls in the first reply. Require the agent to report the count at the end. Target: 30 lines.

2. **Add an ask-trigger rule.** Ask at the first decision point with two or more materially different outcomes, once the cheapest check is done. One question costs one turn. Report a spec deviation as soon as the agent finds it. Merge with `ambiguity-resolution.md` rather than adding a separate file, to keep the payload flat.

3. **Add a first-step rule for plugin and CLI work.** Read the README or the tool description first. Do not grep the source before that. Search the tool catalog before you read any source. Target: 20 lines.

4. **Extend `no-progress-stop.md`.** Add the second trigger: two consecutive probes of one hypothesis that add no information, whatever the output text says.

5. **Add a one-question-per-phase rule.** State the next question before the next batch of calls. Do not mix a harness question with a task question in one phase.

6. **Fix the Code Mode catalog notice.** Name the search rule in one line: the catalog is partial, so search it for the tool that answers the question before reading source code.

7. **Fix the AFT notice.** State the git-tag exception: use `git show <tag>:<path>` when the answer must come from a specific revision, and say so in the reply.

8. **Write the knowledge-cache entry.** Record that the ensemble plugin cannot carry a `#variant` on a pool model. Record that its model pool entries take a plain `provider/model` string. Add the entry to the cache index.

9. **Reconcile the Ponytail reply rule with research tasks.** The Ponytail injection asks for one or two lines at the end. A research reply needs the call count and the negative results. Let a research reply carry a short table instead.

## Lessons learned

- **A question is the cheapest tool in the set.** One turn buys a decision that otherwise costs an unbounded number of turns of source reads.
- **The cheapest check ends the debate.** The decisive fact was two file reads. Everything after it served no purpose.
- **Negative results need a stop rule.** A failed search that returns different text each time never trips a rule that keys on error text.
- **A catalog search beats source archaeology.** The tool that answers the question was in the first search result. The agent used it 126 calls later.
- **Read the manual first.** The plugin README answered the question in prose. The agent reached it after 70 calls of source work.
- **Report a spec deviation when you find it.** The user asked for this at tag 428. The agent had the answer by tag 300.

## See also

- `docs/plans/2026-10-25-agent-instruction-review/` — the earlier review of the same instruction set, including the contradictions it found
- `~/.agents/rules/ambiguity-resolution.md` — the ask rule that needs a trigger clause
- `~/.agents/rules/no-progress-stop.md` — the rule that needs a second trigger
- `~/.agents/rules/local-first.md` — the rule that was loaded but not followed for the cache read
- `~/.agents/rules/long-running-tools.md` — the delegated research facility the agent did not use
