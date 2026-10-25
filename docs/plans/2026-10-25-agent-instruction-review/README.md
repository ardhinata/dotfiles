# Agent instruction review for MiniMax M3.1 Flash

A review of the always-on agent instruction set in this repository, measured
against the daily coding model `minimax/minimax-m3.1-flash`. The review covers
the 16 global rule files, the two project files, the skill catalog, and the
OpenCode configuration.

**Status: tranche 1 applied. Tranche 2 open.** Four independent reviewers
checked the first draft. All four found material errors. Two findings
removed the plan's central premise. One showed that the permission block
validated against the schema and blocked nothing.

No file in `dot_agents/`, `AGENTS.md`, or the OpenCode config changed during
the review.

## Index

| File | Contents |
|---|---|
| [01-problem-background.md](01-problem-background.md) | Why the arrangement is a problem. Scope and the existing constraints |
| [02-research-steps.md](02-research-steps.md) | The five steps, with the method for each so a reader can repeat them |
| [03-findings.md](03-findings.md) | The measured payload, the model profile, the findings that survive, the withdrawn finding, and the 18-item defect list |
| [04-cross-check-results.md](04-cross-check-results.md) | What each reviewer found, what it changed, and what survived all four |
| [05-conclusion.md](05-conclusion.md) | The verdict, the two-tranche split, the corrected arithmetic, and a confidence grade per recommendation |
| [06-implementation.md](06-implementation.md) | The six phases, the risks, the open questions, the decisions, and the deferred notes |
| [07-skills-analysis.md](07-skills-analysis.md) | The analysis of the 11 skills, the two dead ones, the duplication, and the proposed catalog changes |
| [08-references.md](08-references.md) | Sources for the model profile, the prompt-design evidence, and the harness claims |

## Executive summary

The instruction set is well written and well organised. It is also larger
than it needs to be, and it does not address the model's two measured failure
modes.

**The payload.** About 16,500 tokens load on every session and never shed,
because OpenCode re-injects the instruction files into every request.
Compaction replaces message history, not the system prompt, so turning
compaction on would not reduce this. That is 38,929 bytes of global rule
files, 5,801 bytes of project files, and a catalog of eleven skill
descriptions. All 16 global rule files broke the house standard of 150 words.
The shortest was 170 words.

**The gap.** No rule told the model to re-read a file it edited, to run a
named check, or to cite a path and line. No rule covered a destructive
command. Three always-on rules contradicted each other with no precedence.

**The model.** MiniMax M3.1 Flash scores 56.2% on factual recall, the best in
its tier. It also has the worst calibration in its tier: 92.8% of its misses
are inventions rather than abstentions, which is about 41% of all answers.
Its reasoning effort defaulted to `max`, where it costs 7 to 48 times what
`low` costs depending on the task.

**What the cross-check changed.** The first draft's central premise was that
prose guards backfire on this model. That rested on one 20-run test with
Fisher exact p near 0.33, confounded by an output-token cap. The premise is
withdrawn. The first draft also claimed the model family is weak at
instruction following. The predecessor M3 scores 82.9% on IFBench, rank 2 of
423. The claim is withdrawn too.

**What the cross-check found in the configuration.** The permission block
would have used the v1 action token `bash`. In OpenCode v2 the token is
`shell`. A `bash` deny passes schema validation and blocks nothing. The
reviewer proved it with a live test.

**The verdict.** Tranche 1 is applied. Tranche 2 is not. The contradiction
fixes, the destructive-command gate, the three new rules, the skill catalog
trim, and the effort pin are in. The byte cut and the wider restructuring are
still open.

## What changed while the plan was applied

Three findings came out of testing the permission layer on the live host.

1. **The scanner reads quoted strings.** A `*rm -*rf*` pattern denies any
   command whose text mentions the flag, including a commit message that
   documents the rule. The applied patterns are path-anchored.
2. **cc-safety-net already owns the git commands.** A live test with all
   OpenCode shell rules removed showed `git reset --hard`, `git clean -fd`,
   `git push --force`, and `git push -f` are already blocked by the plugin.
   The OpenCode layer now carries `rm` only.
3. **A stray test commit.** One permission probe ran `git commit` in this
   repository and swept up the new rule file. The file content was correct
   and deployed, but the commit message was wrong. The history was rewritten
   so the file sits in the commit that describes it.

## Open questions

1. Do you accept the two-tranche split, or do you want one change set?
2. Tranche 2: ship as hygiene, or gate behind a pilot?
3. Is a 33% cut worth the work, given seven files still breach the ceiling?
4. Should the ceiling be relaxed for the safety files, or enforced on all 16?
5. Global `permissions`, or repo `.opencode/opencode.jsonc`?
6. If code-execution quality matters more than latency, should the model swap
   be evaluated before this plan? The plan's own data favours the swap.
7. For the skills catalog: delete the two dead skills, or hide them first with
   `permission.skill`?

## Related

- `docs/agent-case-studies.md` — the retired subagent fleet and its lessons
- `.agents/skills/document-conventions/` — the conventions this document set
  follows
- `.agents/skills/project-layout/` — the canonical tree, including where a
  task directory belongs
