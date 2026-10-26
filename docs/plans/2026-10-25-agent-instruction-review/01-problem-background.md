# Problem background

Why the always-on instruction set is a problem for MiniMax M3.1 Flash.

Part of the agent instruction review. See [README.md](README.md) for the index.
## Problem background

**The instruction set was written for a different class of model.** It grew
across two harness migrations. It carries 16 global rule files, four of which
are routers, plus two project files. Each file was justified on its own. No
step in the history asked whether the set as a whole fits a fast model.

**No rule file breaks the house length standard.** The document-conventions
skill sets 30 to 80 *lines* as the target and 150 *lines* as the ceiling for
a rule file. All 19 global rule files are inside the ceiling. The longest is
`runtime-tools.md` at 77 lines.

An earlier draft of this review measured words instead of lines and reported
that all 16 rule files breached the ceiling. They did not. The payload
concern below is real; the convention-breach claim was not.

**The daily model changed on 2026-10-19.** MiniMax M3.1 Flash is now the
default here and the second most used model on OpenCode by token volume. Its
calibration is the worst in its comparison set: 92.8% of its misses are
inventions rather than abstentions. That is about 41% of all answers, not 93%.

**Nothing in the set addresses a destructive command.** No rule mentions
`rm -rf`, `git reset --hard`, `git clean -fd`, `git push --force`, or a bare
`chezmoi apply`. AGENTS.md line 34 tells the model to commit the working tree
after a refactor, with no gate.

**What the cross-check removed.** The first draft claimed that prose guards
backfire on this model, based on one test. That test is underpowered and
confounded. The draft also claimed the family is weak at instruction
following. The predecessor model scores 82.9% on IFBench, rank 2 of 423. Both
claims are withdrawn. See "Cross-check results".

## Scope

- In: the 16 always-on rule files under `dot_agents/rules/` and
  `dot_agents/rules.personal.d/`, the repo `AGENTS.md`, the repo rule
  `.agents/rules/chezmoi-source-project.md`, the `permissions` and `policies`
  fields in `dot_config/opencode/private_opencode.jsonc`, and the reasoning
  effort for the default model.
- Out: the plugins, the chezmoi source layout, the encryption workflow, and
  the choice of model. The model choice is out of scope for action. It stays
  in scope for one comparison paragraph, because the cross-check found that
  the first draft dismissed it without an argument.

## Existing constraints

1. `compaction.auto` is `false` in the OpenCode config. The always-on block
   never sheds during a session.
2. The rule files are global. They load in every project, not only this repo.
3. Global rules and skills are edited in `dot_agents/` and applied with
   `chezmoi apply`. A `chezmoi add ~/.agents/...` lands in the
   non-deploying `.agents/` tree and never reaches `$HOME`.
4. `.chezmoiignore` and `.chezmoidata.yaml` need explicit approval.
5. The global rules carry no frontmatter. Skills require `name` and
   `description` frontmatter.
6. OpenCode is v2.1.4. In v2 the permission action tokens are `shell` and
   `subagent`. The v1 tokens `bash` and `task` are inert.
7. Global `permissions` are appended before project config. A project
   `.opencode/opencode.jsonc` can override this block. The guard is therefore
   not absolute.

