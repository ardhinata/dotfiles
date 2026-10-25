---
status: draft
goal: Make the always-on agent instruction set effective for minimax-m3.1-flash on coding tasks
owner: ardhinata
last-updated: 2026-10-25
---

# Agent instruction set review for MiniMax M3.1 Flash

## Goal

Reduce the always-on instruction payload. Remove the rules that the daily model
cannot follow or does not need. Add the rules that counter the model's two
measured failure modes: confident invention and no-progress loops. The target
model is `openrouter/minimax/minimax-m3.1-flash`, set in
`dot_config/opencode/private_opencode.jsonc`.

## Problem background

Three facts together make the present arrangement a problem.

**The instruction set was written for a different class of model.** It grew
across two harness migrations. It carries 16 global rule files, four of which
are routers, plus two project files. Each file was justified on its own. No
step in the history asked whether the set as a whole fits a fast model with a
small reasoning budget.

**The daily model changed underneath it.** MiniMax M3.1 Flash arrived on
2026-10-19. It is the second most used model on OpenCode by token volume, and
it is now the default here. It scores 43 on the Artificial Analysis Index at
`max` effort. Its measured weaknesses are specific and unusual. It has the
best factual recall in its tier at 56.2% and the worst calibration at 92.8%.
It reasons for a long time at the default effort and sometimes stops making
progress. A rule set that suits a frontier model does not automatically suit
this one.

**Nothing in the set addresses either weakness.** No rule tells the model to
re-read a file it edited, to run a named check, or to cite a path and line.
No rule covers a destructive command. AGENTS.md line 34 actively tells the
model to commit the working tree after a refactor, with no gate.

The result is predictable. The model carries about 16,000 to 17,000 tokens of
instruction that never sheds, because `compaction.auto` is `false`. It spends
that budget on reference text and duplicates. It receives no instruction for
the two behaviours it gets wrong most often.

## Scope

- In: the 16 always-on rule files under `dot_agents/rules/` and
  `dot_agents/rules.personal.d/`, the repo `AGENTS.md`, the repo rule
  `.agents/rules/chezmoi-source-project.md`, the skill catalog under
  `dot_agents/skills/`, the `instructions` and `permissions` fields in
  `dot_config/opencode/private_opencode.jsonc`, and the reasoning effort for
  the default model.
- Out: the plugins (`cc-safety-net`, `aft-opencode`,
  `opencode-magic-context`, `ponytail`, `opencode-ensemble`), the chezmoi
  source layout, the encryption workflow, and the choice of model.

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
6. MiniMax M3.1 Flash has no published instruction-following score. There is
   no IFBench, BFCL, or multi-turn retention number for this model. Every
   claim about its instruction adherence is an inference.
7. OpenCode reports version v2.1.4. The config schema in that version marks
   the `permission` field as deprecated and exposes `permissions` instead.

## Research steps

The review ran five steps. Each step names the method, so a reader can repeat
it.

### Step 1. Measure the payload

Counted words and bytes for every deployed file, and for every layer that adds
tokens before the first user message.

- `wc -w` and `wc -c` over `~/.agents/rules/*.md` and
  `~/.agents/rules.personal.d/*.md`.
- `wc -w` and `wc -c` over `AGENTS.md` and
  `.agents/rules/chezmoi-source-project.md`.
- Byte count of each skill `description` block under `~/.agents/skills/*/`,
  summed to get the catalog cost.
- Byte count of the `ponytail-instructions.js` hook, which injects a fixed
  block into every session.
- `opencode debug config` to read the effective config, and to confirm the
  plugin list, the `instructions` globs, and `compaction.auto`.
- `opencode --version` and `opencode models` to confirm the version and the
  model variant ladder.

### Step 2. Model profile research

One research pass over public sources for MiniMax M3.1 Flash, released
2026-10-19. The pass answered seven questions: hard specs, instruction
adherence, tool-calling reliability, coding-agent failure modes, reasoning
effort trade-offs, speed against peers, and comparison against DeepSeek V4.1
Flash 1017 and GLM 5.3 Flash.

Sources were graded. Primary vendor documentation and Artificial Analysis
counted as high confidence. A measured blog test counted as medium. Reddit
reports counted as low. Every row in the model table carries a grade is not
shown, but this section lists the grading rule. The claims that could not be
verified are named in their own list below.

### Step 3. Prompt-design evidence research

One research pass over published guidance for writing instructions for
small and fast coding models. The pass covered seven questions: length budget,
routers against always-on text, instruction format, tool routing, verification
loops, context hygiene, and anti-patterns. The primary sources were the
IFScale study, Anthropic's context-engineering and Agent Skills writeups, the
OpenAI Codex and GPT-5.2 prompting guides, the agentskills.io specification,
the agents.md format, the Cursor rules documentation, and Chroma's context-rot
research.

### Step 4. Internal audit

A full read of all 18 always-on files, plus the six skills that the router
rules point at. The audit reported six things:

1. An inventory with word counts and load scope per file.
2. Contradictions, each quoted from both sides.
3. Redundancy between a router rule and the skill it points at.
4. Over-specification: text that a fast model would derive correctly anyway.
5. Missing triggers, and triggers that fire on almost every task.
6. A safety-critical inventory, with a dilution test per rule.

The audit closed with a ranked defect list of 31 items. This plan carries the
18 that change model behaviour.

### Step 5. Verify the technical claims

Two claims in the first draft were wrong. Both came from documentation pages
rather than the schema. Both were corrected by reading the live schema.

- Fetched `https://opencode.ai/config.json` and inspected the
  `Permission.Ruleset`, `Permission.Rule`, and `AgentConfig` definitions. The
  `permission` field is marked `"deprecated": true`. The live field is
  `permissions`, an ordered array of `{action, resource, effect}`.
- Inspected the root `model` definition. It accepts `{providerID, model,
  variant}`, so a global default effort works. An earlier claim that the root
  model cannot carry a variant was wrong for v2.1.4.

### What this review did not do

- No empirical test of rule adherence on this model. No such test exists in
  public, and none was run here. Phase 6 exists to close that gap.
- No read of the `cc-safety-net` policy source. Its block list was inferred
  from its bundled output by pattern search.
- No measurement of how often each rule fires in practice. The
  `asd-ste100-trigger` cost estimate is arithmetic, not observation.

## Findings

### Measured always-on payload

| Layer | Bytes | Approx. tokens |
|---|---|---|
| `dot_agents/rules/*.md` (8 files) | 17,376 | 4,700 |
| `dot_agents/rules.personal.d/*.md` (8 files) | 21,553 | 5,800 |
| `AGENTS.md` + `.agents/rules/chezmoi-source-project.md` | 5,801 | 1,600 |
| Skill catalog (11 descriptions) | 5,630 | 1,600 |
| `ponytail` plugin injection | 5,565 | 1,400 |
| AFT tool notice and tool descriptions | not measured | ~2,000 |
| **Total** | **~56,000** | **~16,000 to 17,000** |

The file-based part is 44,730 bytes across 18 files, or about 12,000 tokens.
The document-conventions skill gives rule files a target of 30 to 80 words and
a hard ceiling of 150. Nine of the 16 global rule files sit above that
ceiling.

### Model profile

| Property | Value | Note |
|---|---|---|
| Context window | 1,000,000 tokens | 512,000 on some providers |
| Reasoning effort | `low` to `max`, default `max` | Thinking cannot be disabled |
| Price per 1M | $0.15 in, $0.60 out, $0.015 cached | Flat, no long-context surcharge |
| AA Intelligence Index | 43 | At `max` effort only |
| AA-Omniscience accuracy | 56.2% | Best in its tier |
| AA-Omniscience hallucination rate | 92.8% | Worst in its tier. Predecessor M3 was 18.4% |
| Terminal-Bench 4.0 | 25.8% | DeepSeek V4.1 Flash 33.8%, GLM 5.3 Flash 32.8% |
| LiveBench Long Agentic | 34.7% | DeepSeek V4.1 Flash 50.9% |
| LiveBench 2.0 Coding | 83.9% | DeepSeek V4.1 Flash 96.0% |

### The five findings that drive the plan

**F-1. Prose guards make this model worse, not better.** One controlled test
added this line to the system prompt:

> If you are not sure that something exists or is true, say you don't know instead of guessing.

For M3.1 Flash, invented answers rose from 10 of 20 runs to 14 of 20. The
same line took DeepSeek from 6 of 20 down to 1 of 20. The model also failed a
plainly stated positive requirement (case insensitive units). It varied its
invented facts across runs, giving four different populations for one
invented town. Counters must be structural: re-read the file, run the
command, cite the path and line. A request for honesty is not a counter.

**F-2. The default reasoning effort is the worst setting.** At `max` the model
uses 48 times the reasoning tokens of `low`. It uses 12 times the wall clock.
It costs 7 times as much. Both levels passed 96 of 96 hidden tests. A
no-progress loop appeared in 3 of 3 `max` runs and in 0 of 3 `low` runs.
MiniMax's own Automation-Bench shows `max` beats `low` by 10 points on long
agentic runs. The setting must follow the task, and it must be explicit.

**F-3. Long context does not break comprehension, but rule count is
untested.** AA-LCR puts the model at 79.7% on 10k to 100k token documents.
LOCA-Bench 256K puts it at 60.3, the best in its tier. A 6,500-word rule set
is therefore survivable. What no study measures is instruction adherence at 16
rule files. The flash tier in the IFScale study holds 66% to 96% at 50
constraints and drops to 42% to 82% at 100. The safe direction is fewer
constraints, not shorter prose.

**F-4. The current set has no rule for the model's main failure.** Nothing in
the 18 always-on files tells the model to re-read a file it edited. Nothing
tells it to run a named check. Nothing tells it to cite the path and line
behind a claim about the repository. AGENTS.md covers `chezmoi diff` and
`chezmoi apply --dry-run` only. This is the gap that matters most for a model
with a 92.8% confident-wrong rate.

**F-5. The current set has no destructive-action rule.** Nothing covers
`rm -rf`, `git reset --hard`, `git clean -fd`, `git push --force`,
`chezmoi apply`, or `chezmoi re-encrypt`. The `cc-safety-net` plugin blocks
several of these. The plugin is a tool-layer backstop, not an instruction, and
it does not gate `sudo`. AGENTS.md line 34 also instructs the model to commit
the working tree after a refactor, with no gate.

### The audit defect list, ranked

| ID | File | Defect |
|---|---|---|
| D-1 | `AGENTS.md:34` | "Always commit after a structural refactor" collides with "Ask first: structural changes to the source directory layout". No precedence. The always-on instruction wins, so the ask-first gate is dead. |
| D-2 | `dot_agents/rules/document-conventions.md:17-23` | Copies 5 rows of the skill's decision matrix into an always-on file, one line after saying the skill's matrix is authoritative. The model answers from 5 rows and never loads the skill. |
| D-3 | `dot_agents/rules/document-conventions.md:23` | Points at `.agents/skills/<name>/SKILL.md`. The global path is `~/.agents/skills/<name>/SKILL.md`. The repo `.agents/skills/` holds 3 unrelated skills. |
| D-4 | `dot_agents/rules.personal.d/zsh-emulate-fallback.md` | 630 words, 8.5% of the global budget, for a trigger the file itself calls unreachable on this host. |
| D-5 | `dot_agents/rules.personal.d/ssh-agent-keys-location.md:21-47` | About 300 of 540 words are GnuPG internals, not rules. |
| D-6 | `dot_agents/rules.personal.d/asd-ste100-trigger.md:12` | Triggers on any reply over roughly 6 sentences. Each trigger loads a 3,301-word skill, which is 2.9 times the whole always-on set. |
| D-7 | `dot_agents/rules.personal.d/asd-ste100-trigger.md:20,22` | One clause appears twice in the same file. |
| D-8 | missing file | No destructive-action rule. |
| D-9 | `dot_agents/rules/long-running-tools.md:19-28` | The fan-out table lists the `subagent` tool. The prose above bans the fan-out facility for delegated research. No precedence. |
| D-10 | `dot_agents/rules.personal.d/scoped-searches.md:5` and `.template-resources/rtk_installed.md` | The dedicated-tool list names `glob`, `grep`, and `read`. It omits `aft_search`, `aft_outline`, and `aft_zoom`, which the harness tool notice names as the primary code path. |
| D-11 | `dot_agents/rules/rtk-rules.md` | 248 always-on words. Five of the 31 lines carry information the model does not already have. |
| D-12 | `dot_agents/rules.personal.d/scoped-searches.md:24` | The escalation table names `~/.gnupg/`, which contains the sealed tree banned 6 lines later. |
| D-13 | `dot_agents/rules.personal.d/scoped-searches.md:32-41` | Three answers to "no hit", with no stated order. |
| D-14 | `dot_agents/rules/web-verification.md:20-25,64-68` | Tells the model to create a cache directory and write files in any project. The escape clause "when project rules prohibit writes" names a rule that does not exist. |
| D-15 | `dot_agents/rules.personal.d/ssh-read-allowlist.md` and `ssh-agent-keys-location.md` | Two always-on rules grant and deny `~/.ssh/agent-keys/`. The repo rule bans any path containing "key", which is a third denial. |
| D-16 | `AGENTS.md:47` | "Never modify `.encryption_keys/` without understanding the re-encrypt workflow" is not checkable. A model can assert that it understood. |
| D-17 | `AGENTS.md:44` | The repo Never list names 3 extensions. The project rule names 12 patterns. A model that reads AGENTS.md alone under-protects. |
| D-18 | `dot_agents/skills/document-conventions/SKILL.md:176` vs `:98` | The skill names two different plan paths. |

## Conclusion

**Verdict.** The set is not optimal for this model. It is about twice the size
it needs to be. It omits the one rule that matters most for a model with a
92.8% confident-wrong rate. It carries three contradictions that the model
resolves by guessing.

**What the plan delivers.**

| Measure | Today | After |
|---|---|---|
| Global rule bytes | 38,929 | ~20,000 |
| Always-on rule files | 16 | 18 |
| Rules that gate a destructive command | 0 | 1 rule and 9 permission entries |
| Rules that require a check after an edit | 0 | 1 |
| Default reasoning effort | `max` | set per task type |

**What the plan does not do.** It does not make the model better. M3.1 Flash
remains the weakest in-tier model on code execution, at 25.8% on Terminal-Bench
against 33.8% for DeepSeek. The plan makes the harness fit the model. If
output quality on hard coding work matters more than speed and cost, the
decision belongs at the model choice, not at the instruction set.

### Confidence per recommendation

| # | Recommendation | Confidence | Basis |
|---|---|---|---|
| 1 | Cut 9 rule files to ~20,000 bytes | HIGH | Measured byte counts against the house budget of 150 words per rule |
| 2 | Fix the 8 contradictions | HIGH | Each is a quote pair in one or two adjacent files |
| 3 | Move reference text into skills | HIGH | Three of the four existing routers already use this pattern |
| 4 | Add a verify-before-claiming rule | MEDIUM | Follows from a 92.8% hallucination rate plus one causal test. The exact wording is untested on this model |
| 5 | Add a destructive-action rule | MEDIUM | The gap is certain. Whether the model obeys the rule is untested. The permission layer is the real guard |
| 6 | Use the v2 `permissions` array | HIGH | Read from the live schema at v2.1.4. `permission` is marked deprecated |
| 7 | Set effort globally to `high` | LOW | Two blog curves, each on one small task. The 10 point spread comes from the vendor |
| 8 | Measure before shipping | HIGH | No published adherence score exists for this model |

## Refined approach

Four rules drive every change.

1. **Structural counters, not prose counters.** F-1 shows that a request for
   honesty backfires on this model. Every counter must be a runnable command,
   a file re-read, or a path and line citation.
2. **Positive rules with a trigger.** A rule states what to do and when. A
   prohibition stays only where the model must not take an action at all, and
   it moves to the harness `permissions` layer.
3. **Routers point, they do not copy.** Three of the four existing routers
   already do this well. The two that copy skill content get cut to a pointer.
4. **Budget the always-on set.** Target 20,000 bytes of global rule text, down
   from 38,929. Keep every safety rule. Cut reference text, procedural text,
   and duplicates.

**Where the changes land.** Phases 1, 3, and 5 are global by construction. The
files they touch exist only in the global layer. Phase 2 is split. Three of
its eight fixes are in `AGENTS.md`, which is repo-scoped, so those three never
leave this repo. Phase 4 is a choice: the global OpenCode config applies to
every project, and the repo `.opencode/opencode.jsonc` applies to this one.
Note that a guard written as OpenCode config does not reach Codex or Claude
Code. The prose rules are the only portable layer, and prose is the weakest
layer for this model.

## Implementation steps

### Phase 1. Cut the payload

| File | Words now | Words after | Action |
|---|---|---|---|
| `rules.personal.d/zsh-emulate-fallback.md` | 630 | ~60 | Keep the host fact and the `bash -c` fallback. Delete the `emulate` semantics, the `man zshmisc` citation, and the option-leak detail. Git keeps the old text. |
| `rules.personal.d/ssh-agent-keys-location.md` | 540 | ~140 | Keep the placement rule and the 6-step process. Move the GnuPG internals to a new skill reference. |
| `rules.personal.d/ssh-stdbuf-disable-buffering.md` | 358 | ~80 | Keep the `stdbuf -oL -eL` rule and the static-linking fallback. Move the LD_PRELOAD and `-tt` caveats to the same new skill. |
| `rules.personal.d/asd-ste100-trigger.md` | 298 | ~200 | Replace the length threshold with an artifact list. Drop the repeated clause. |
| `rules/rtk-rules.md` | 248 | ~90 | Keep "never wrap the dedicated tools", "wrap each sub-command", and the diagnostic modes. Drop the 5 command categories. |
| `rules/document-conventions.md` | 258 | ~130 | Delete the inline matrix. Point at the skill. Fix the skill path to `~/.agents/skills/<name>/SKILL.md`. |
| `rules/web-verification.md` | 512 | ~330 | Drop the volatility taxonomy table. Keep the 6-month and 3-month thresholds. Scope the cache write. |
| `rules.personal.d/scoped-searches.md` | 482 | ~250 | Replace the 8-step process with 3 lines. Keep the escalation table with the `~/.gnupg/` row fixed. State the order for "no hit". |
| `rules/runtime-tools.md` | 389 | ~230 | Reduce the host section to one line per tool. Stop copying skill text. |

Expected result: 38,929 bytes down to about 20,000 bytes, a 49% cut. The
skill catalog gains one entry, about 100 tokens.

### Phase 2. Fix the contradictions

1. `AGENTS.md:34`. Replace with: "After a refactor that does not change the
   source directory layout, run `git status --short`, stage, and commit before
   you end the session. If the refactor changes the layout, ask first and do
   not commit."
2. `AGENTS.md:47`. Replace with: "Never modify `.encryption_keys/`. Adding a
   recipient key rewrites every encrypted file, so run `chezmoi re-encrypt`
   only after the user approves."
3. `AGENTS.md:44`. Replace the 3-extension list with a pointer to
   `.agents/rules/chezmoi-source-project.md`.
4. `long-running-tools.md`. Split the table into two rows. One row for
   parallel sessions and worktrees, on explicit user request. One row for
   delegated research through the `subagent` tool, always allowed.
5. `scoped-searches.md`. Replace the `~/.gnupg/` row with
   `~/.gnupg/gpg-agent.conf` and `~/.gnupg/gpg.conf`, and add "files, not the
   directory".
6. `ssh-read-allowlist.md`. Add `~/.ssh/agent-keys/` to the allowlist for
   directory listings and `*.pub` files only. State that this carve-out wins
   over the general `~/.ssh/` denial.
7. `web-verification.md`. Add: "Write a cache entry only in a repository that
   already has `.agents/docs/cache/`. Otherwise skip the cache and note the
   gap in your reply."
8. `document-conventions/SKILL.md:176`. Make the quick-reference path match
   line 98.

### Phase 3. Add the missing rules

**New file `dot_agents/rules.personal.d/destructive-actions.md`.** Short list,
ask first, each item one line.

- `rm -rf`, or `rm -r` on a path outside the working directory
- `git reset --hard`, `git clean -fd`, `git push --force`
- `git commit` when the user did not ask for a commit
- `chezmoi apply`, `chezmoi re-encrypt`, `chezmoi update`
- `sudo`, `doas`, `pkexec`
- `chmod`, `chown`, or `mv` on a path outside the working directory

Each line names the exact command and ends with: "Ask first. Print the exact
command in the reply so the user can run it."

**New file `dot_agents/rules/verify-before-claiming.md`.** The counter for
F-4. Wording is positive and structural, per F-1. It does not ask the model to
be careful or to admit doubt.

- After you edit a file, read the file back and check the change is there.
- After you change code, run the project test or check command. Do not report
  the change as done until the command exits 0.
- For each claim about this repository, give the file path and the line
  number.
- When a command fails, show the command and its output. Do not paraphrase an
  error you did not see.
- When a check cannot run, say so and name the reason. Do not report it as
  passed.
- End each task with one line that lists each promised check as done, blocked,
  or skipped.

**Update `dot_agents/rules.personal.d/scoped-searches.md` and
`dot_agents/rules/.template-resources/rtk_installed.md`.** Name the full tool
set. Use a harness-neutral phrase with the OpenCode names in parentheses, so
the rule still reads correctly in another harness:

> Use the harness symbol-search and outline tools before shell search. In
> OpenCode these are `aft_search`, `aft_outline`, and `aft_zoom`. Use `shell`
> for commands, tests, and git. Use shell `grep` only when the search tools
> return nothing.

### Phase 4. Move the guard to the harness layer

Prose is a probabilistic guard. The OpenCode `permissions` field is
deterministic. In v2.1.4 the deprecated `permission` object is replaced by
`permissions`, an ordered array of `{action, resource, effect}`. Add these
entries to `dot_config/opencode/private_opencode.jsonc`, after the existing
`external_directory` entry:

```jsonc
"permissions": [
  { "action": "external_directory", "resource": "~/.local/share/opencode/worktree/**", "effect": "allow" },
  { "action": "bash", "resource": "rm -rf *",            "effect": "deny" },
  { "action": "bash", "resource": "git reset --hard*",   "effect": "deny" },
  { "action": "bash", "resource": "git clean -fd*",      "effect": "deny" },
  { "action": "bash", "resource": "git push --force*",   "effect": "deny" },
  { "action": "bash", "resource": "git commit*",         "effect": "ask"  },
  { "action": "bash", "resource": "chezmoi apply*",      "effect": "ask"  },
  { "action": "bash", "resource": "chezmoi re-encrypt*", "effect": "ask"  },
  { "action": "bash", "resource": "sudo *",              "effect": "ask"  }
]
```

This is the fix for D-8 and for the missing `sudo` gate. The rule file becomes
the backstop. The permission array and the plugin become the guard.

The schema does not state whether the first or the last matching rule wins.
Test one `deny` entry with a throwaway command before trusting the array.

### Phase 5. Set the reasoning effort

The model defaults to `max`, and `max` is where the no-progress loops
appear. In v2.1.4 the root `model` accepts `{providerID, model, variant}`, and
the string form accepts `provider/model#variant`. A global default effort is
therefore possible. `AgentConfig.variant` also exists for a per-agent
override.

| Task type | Effort | Evidence |
|---|---|---|
| Read, search, single-file edit | `low` | 48 s and 1.3K reasoning tokens at `low` against 9.5 min and 60.6K at `max`, same result |
| Multi-file edit, bug hunt | `medium` or `high` | 10-point Automation-Bench spread from `low` to `max` |
| Long-horizon agent run | `max` | `max` scores 62.8% on Automation-Bench against 52.8% at `low` |

The `subagent` tool drops the parent variant when the subagent pins its own
model. Set the variant on each subagent definition, not only on the parent.

### Phase 6. Measure the result

This phase is optional. It answers the question that no published study
answers for this model: does the instruction set work here.

1. Pick 8 to 12 tasks from this repository that use the rules:
   - a chezmoi template edit
   - a shell script fix
   - a rule file edit
   - a read next to a secret file
   - a task that includes a destructive command
   - a doc write
   - a bug hunt
   - a multi-file refactor
2. Run each task 3 times with the current rules and 3 times with the new
   rules. Hold the effort, the model, and the temperature fixed.
3. Score each run on these points:
   - did the model follow the targeted rule
   - did the model run the named check
   - did the model invent a path or a flag
   - did the model stop in a loop
   - how long the task took
4. Store the results as a table. Decide on the numbers, not on the theory.

## Risks and mitigations

- **Risk:** a cut rule turns out to carry something the model needed.
  **Mitigation:** git keeps every removed paragraph. The change lands in one
  commit, so one revert restores the old text.
- **Risk:** the `permissions` entry blocks a workflow the user wants.
  **Mitigation:** use `ask` for the commands that have a legitimate case, and
  `deny` only for the four that destroy data.
- **Risk:** the verify rule adds a tool round to every task, so tasks take
  longer. **Mitigation:** the model is already slow at `max`. Phase 5 cuts the
  reasoning depth, which pays for the extra round.
- **Risk:** the effort change alters the feel of the model.
  **Mitigation:** Phase 5 maps effort to task type, so the change is a
  gradient, not a switch.
- **Risk:** a global rule change changes behavior in every project, not only
  this one. **Mitigation:** the user approves each global change, and this
  plan lists every file by path before any edit.
- **Risk:** a bare `chezmoi apply` deploys unrelated in-flight changes in the
  source tree, not only the instruction files. **Mitigation:** apply by target
  path. `chezmoi apply ~/.agents/rules ~/.agents/rules.personal.d` and
  `chezmoi apply ~/.config/opencode/opencode.jsonc`.

## Open questions

1. Which effort becomes the default: `max` as today, or `high`?
2. Is a 49% cut acceptable, or do you want a smaller cut that keeps the
   reference text in place?
3. Do you want the destructive-action rule global, so it loads in every
   project, or only in this repo?
4. Do you want the `permissions` array in the global OpenCode config, which
   applies to every project, or in the repo `.opencode/opencode.jsonc`?
5. Should Phase 6 run, or should the changes ship on the evidence alone?

## Decisions

- 2026-10-25: The plan is a draft. No file in `dot_agents/`, `AGENTS.md`, or
  the OpenCode config changed during the review.
- 2026-10-25: The global rules stay global. The user keeps one rule set for
  every project. The review changes the content, not the scope.
- 2026-10-25: Phase 4 uses the v2 `permissions` array, not the deprecated
  `permission` object. Basis: the v2.1.4 config schema.
- 2026-10-25: Phase 5 sets effort on the root `model`. The earlier claim that
  the root model cannot carry a variant was wrong. Basis: the v2.1.4 config
  schema.

## Deferred notes

- The skill catalog costs about 1,600 tokens on every session. No published
  study measures the damage of a large catalog on a flash model. A test with
  5 of the 11 skills disabled would answer it. That test is not in this plan.
- `~/.agents/rules.personal.d/asd-ste100-trigger.md` makes every reply over
  roughly 6 sentences load a 3,301-word skill. A count of how often that
  trigger fires would settle whether the Phase 1 cut costs prose quality.
- The `question` tool comes from the `opencode-magic-context` plugin, not
  from OpenCode. The `sudo-ask` and `ambiguity-resolution` rules depend on it
  with no fallback. A plain-text fallback sentence would close the gap.
- The `cc-safety-net` plugin blocks several destructive commands. The audit
  read its bundled output by pattern search rather than from the policy
  source. The Phase 4 list is written from the OpenCode permission schema, so
  the two lists do not need to agree.

## References

### Model

- MiniMax M3.1 Flash announcement — https://www.minimax.io/blog/minimax-m31f
- MiniMax text-generation guide (effort levels, thinking) —
  https://platform.minimax.io/docs/guides/text-generation
- MiniMax tool-use guide (`reasoning_content`, interleaved thinking) —
  https://platform.minimax.io/docs/guides/text-m3-function-call
- MiniMax M2 agent-generalization post —
  https://platform.minimax.io/docs/guides/text-m2-agent-generalization.md
- MiniMax Codex guide (512K against 1M context) —
  https://platform.minimax.io/docs/m-plan/codex.md
- Artificial Analysis model page —
  https://artificialanalysis.ai/models/minimax-m3-1-flash
- Artificial Analysis AA-Omniscience definition —
  https://artificialanalysis.ai/evaluations/omniscience
- Artificial Analysis launch thread —
  https://x.com/ArtificialAnlys/status/2112211865128608002
- VentureBeat launch report —
  https://venturebeat.com/technology/minimaxs-new-m3-1-flash-beats-deepseek-and-opus-5-on-a-key-business-benchmark-at-lower-cost-but-with-a-high-hallucination-rate
- AI/ML API hands-on review (the controlled "admit uncertainty" test, the
  effort ladder, the nonexistent-town test) —
  https://aimlapi.com/blog/minimax-m3-1-flash-review
- Atomic Agent test (low against max on one task, no-progress loop) —
  https://atomicagent.io/blog/minimax-m3-1-flash/
- Atomic Agent model comparison —
  https://atomicagent.io/blog/deepseek-v4-1-flash-vs-minimax-m3-1-flash/
- BenchLeader model page (Terminal-Bench, LiveBench, IFBench gap) —
  https://www.benchleader.com/models/minimax-m3-1-flash
- OpenCode public usage data —
  https://opencode.ai/data/minimax/minimax-m3-1-flash

### Prompt design

- IFScale, instruction density and degradation curves —
  https://arxiv.org/abs/2507.11538
- Anthropic, effective context engineering —
  https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
- Anthropic, Agent Skills —
  https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic, writing effective tools —
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, Claude Code best practices —
  https://www.anthropic.com/research/claude-code-best-practices
- OpenAI, Codex prompting guide (tool routing, plan closure) —
  https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- OpenAI, GPT-5.2 prompting guide —
  https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- agentskills.io specification (progressive disclosure, token limits) —
  https://agentskills.io/specification
- agents.md format —
  https://agents.md
- Cursor rules (activation modes, what to avoid) —
  https://cursor.com/docs/rules
- Aider conventions file —
  https://aider.chat/docs/usage/conventions.html
- Chroma, context rot —
  https://research.trychroma.com/context-rot
- NeQA, negation and inverse scaling —
  https://arxiv.org/abs/2305.17311

### Harness

- OpenCode config schema (the `permission`, `permissions`, and `AgentConfig`
  definitions) — https://opencode.ai/config.json
- OpenCode permissions — https://opencode.ai/docs/permissions
- OpenCode models and variants — https://opencode.ai/v2/docs/models
- OpenCode instructions — https://opencode.ai/v2/docs/instructions

### Internal

- `.agents/skills/document-conventions/references/structure-and-length.md` —
  the rule-file budget of 30 to 80 words with a 150-word ceiling
- `.agents/skills/document-conventions/SKILL.md` — the decision matrix and
  the harness-neutral rule policy
- `dot_agents/rules/.template-resources/` — the six host-rendered snippets
- `dot_config/opencode/private_opencode.jsonc` — the effective config

## Current status

Research, audit, and plan are done on 2026-10-25. The plan carries the problem
background, the five research steps, the findings, the conclusion with a
confidence grade per recommendation, and the reference list. Two technical
errors in the first draft are corrected: the Phase 4 permission shape and the
Phase 5 root-model variant. No file in `dot_agents/`, `AGENTS.md`, or the
OpenCode config changed during the review. Next action is the user's
go-ahead and the answers to the five open questions.
