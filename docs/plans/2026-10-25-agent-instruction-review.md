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

## Scope

- In: the 16 always-on rule files under `dot_agents/rules/` and
  `dot_agents/rules.personal.d/`, the repo `AGENTS.md`, the repo rule
  `.agents/rules/chezmoi-source-project.md`, the skill catalog under
  `dot_agents/skills/`, the `instructions` and `permission` config in
  `dot_config/opencode/private_opencode.jsonc`, and the reasoning-effort
  setting for the default model.
- Out: the plugins themselves (`cc-safety-net`, `aft-opencode`,
  `opencode-magic-context`, `ponytail`, `opencode-ensemble`), the
  chezmoi source layout, the encryption workflow, and the choice of model.

## Existing constraints

1. `compaction.auto` is `false` in the OpenCode config. The always-on block
   never sheds during a session.
2. The rule files are global. They load in every project, not only this repo.
3. Global rules and skills must be edited in `dot_agents/` and applied with
   `chezmoi apply`. A `chezmoi add ~/.agents/...` lands in the non-deploying
   `.agents/` tree and never reaches `$HOME`.
4. `.chezmoiignore` and `.chezmoidata.yaml` need explicit approval.
5. The global rules carry no frontmatter. Skills require `name` and
   `description` frontmatter.
6. MiniMax M3.1 Flash has no published instruction-following score. There is
   no IFBench, BFCL, or multi-turn retention number for this model. Every
   claim about its instruction adherence is an inference.

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

### Model profile (MiniMax M3.1 Flash, released 2026-10-19)

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

For M3.1 Flash, invented answers rose from
10 of 20 runs to 14 of 20. The same line took DeepSeek from 6 of 20 down to 1
of 20. The model also failed a plainly stated positive requirement (case
insensitive units) and varied its invented facts across runs (four different
populations for one invented town). Counters must be structural: re-read the
file, run the command, cite the path and line. A request for honesty is not a
counter.

**F-2. The default reasoning effort is the worst setting.** At `max` the model
uses 48 times the reasoning tokens of `low`. It uses 12 times the wall clock.
It costs 7 times as much. Both levels passed 96 of 96 hidden tests.
A no-progress loop appeared in 3 of 3 `max` runs and in 0 of 3 `low` runs.
MiniMax's own Automation-Bench shows `max` beats `low` by 10 points on long
agentic runs. The setting must follow the task, and it must be explicit.

**F-3. Long context does not break comprehension, but rule count is
untested.** AA-LCR puts the model at 79.7% on 10k to 100k token documents, and
LOCA-Bench 256K puts it at 60.3, the best in its tier. A 6,500-word rule set
is therefore survivable. What no study measures is instruction adherence at 16
rule files. The flash tier in the IFScale study holds 66% to 96% at 50
constraints and drops to 42% to 82% at 100. The safe direction is fewer
constraints, not shorter prose.

**F-4. The current set has no rule for the model's main failure.** Nothing in
the 18 always-on files tells the model to re-read a file it edited. Nothing
tells it to run a named check. Nothing tells it to cite the path and line
behind a claim about the repository.
AGENTS.md covers `chezmoi diff` and `chezmoi apply --dry-run` only. This is the
gap that matters most for a model with a 92.8% confident-wrong rate.

**F-5. The current set has no destructive-action rule.** Nothing covers
`rm -rf`, `git reset --hard`, `git clean -fd`, `git push --force`,
`chezmoi apply`, or `chezmoi re-encrypt`. The `cc-safety-net` plugin blocks
several of these, but the plugin is a tool-layer backstop, not an instruction,
and it does not gate `sudo`. AGENTS.md line 34 also instructs the model to
commit the working tree after a refactor, with no gate.

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
| D-10 | `dot_agents/rules.personal.d/scoped-searches.md:5` and `.template-resources/rtk_installed.md` | The dedicated-tool list names `glob`, `grep`, and `read`. It omits `aft_search`, `aft_outline`, and `aft_zoom`, which the harness tool notice names as the primary code path and tells the model not to replace with shell `grep`. |
| D-11 | `dot_agents/rules/rtk-rules.md` | 248 always-on words. Five of the 31 lines carry information the model does not already have. |
| D-12 | `dot_agents/rules.personal.d/scoped-searches.md:24` | The escalation table names `~/.gnupg/`, which contains the sealed tree banned 6 lines later. |
| D-13 | `dot_agents/rules.personal.d/scoped-searches.md:32-41` | Three answers to "no hit", with no stated order. |
| D-14 | `dot_agents/rules/web-verification.md:20-25,64-68` | Tells the model to create a cache directory and write files in any project. The escape clause "when project rules prohibit writes" names a rule that does not exist. |
| D-15 | `dot_agents/rules.personal.d/ssh-read-allowlist.md` and `ssh-agent-keys-location.md` | Two always-on rules grant and deny `~/.ssh/agent-keys/`. The repo rule bans any path containing "key", which is a third denial. |
| D-16 | `AGENTS.md:47` | "Never modify `.encryption_keys/` without understanding the re-encrypt workflow" is not checkable. A model can assert that it understood. |
| D-17 | `AGENTS.md:44` | The repo Never list names 3 extensions. The project rule names 12 patterns. A model that reads AGENTS.md alone under-protects. |
| D-18 | `dot_agents/skills/document-conventions/SKILL.md:176` vs `:98` | The skill names two different plan paths. |

## Refined approach

Four rules drive every change.

1. **Structural counters, not prose counters.** F-1 shows that a request for
   honesty backfires on this model. Every counter must be a runnable command,
   a file re-read, or a path and line citation.
2. **Positive rules with a trigger.** A rule states what to do and when. A
   prohibition stays only where the model must not take an action at all, and
   it moves to the harness `permission` layer.
3. **Routers point, they do not copy.** Three of the four existing routers
   already do this well. The two that copy skill content get cut to a pointer.
4. **Budget the always-on set.** Target 20,000 bytes of global rule text, down
   from 38,929. Keep every safety rule. Cut reference text, procedural text,
   and duplicates.

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

- `rm -rf`, `rm -r` on a path outside the working directory
- `git reset --hard`, `git clean -fd`, `git push --force`
- `git commit` when the user did not ask for a commit
- `chezmoi apply`, `chezmoi re-encrypt`, `chezmoi update`
- `sudo`, `doas`, `pkexec`
- `chmod`, `chown`, or `mv` on a path outside the working directory

Each line names the exact command and ends with "Ask first. Print the exact
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
set: `aft_search`, `aft_outline`, `aft_zoom`, `read`, `glob`, `grep`. State
the fallback in positive form: "Use `aft_search` to find code. Use `aft_zoom`
to read a symbol. Use `shell` for commands, tests, and git. Use shell `grep`
only when the search tools return nothing."

### Phase 4. Move the guard to the harness layer

Prose is a probabilistic guard. The OpenCode `permission` config is
deterministic. Add to `dot_config/opencode/private_opencode.jsonc`:

```jsonc
"permission": {
  "bash": {
    "*": "allow",
    "rm -rf *": "deny",
    "rm -fr *": "deny",
    "git reset --hard*": "deny",
    "git clean -fd*": "deny",
    "git push --force*": "deny",
    "git commit*": "ask",
    "chezmoi apply*": "ask",
    "chezmoi re-encrypt*": "ask",
    "chezmoi update*": "ask",
    "sudo *": "ask",
    "doas *": "ask"
  }
}
```

This is the fix for D-8, D-9, and the missing `sudo` gate. The rule file
becomes the backstop, and the plugin and the config become the real guard.

### Phase 5. Set the reasoning effort

The model defaults to `max`, and `max` is where the no-progress loops
appear. OpenCode exposes the effort as a model variant. Set the default
variant in `dot_config/opencode/private_opencode.jsonc` and give the
sub-agents their own effort.

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
- **Risk:** the `permission` block blocks a workflow the user wants.
  **Mitigation:** use `ask` for the commands that have a legitimate case, and
  `deny` only for the four that destroy data.
- **Risk:** the verify rule adds a tool round to every task, so tasks take
  longer. **Mitigation:** the model is already slow at `max`. Phase 5 cuts the
  reasoning depth, which pays for the extra round.
- **Risk:** the effort change alters the feel of the model.
  **Mitigation:** Phase 5 maps effort to task type, so the change is a
  gradient, not a switch.
- **Risk:** a global rule change changes behavior in every project, not only
  this one. **Mitigation:** the user approves each global change, and the plan
  lists every file by path before any edit.
- **Risk:** the verify rule pushes the model to run a check that does not
  exist. **Mitigation:** the rule says to name the reason, so a missing
  command becomes a reported blocked item, not a silent pass.

## Open questions

1. Which effort becomes the default: `max` as today, or `high`?
2. Is a 49% cut acceptable, or do you want a smaller cut that keeps the
   reference text in place?
3. Do you want the destructive-action rule global, so it loads in every
   project, or only in this repo?
4. Do you want the `permission` block in the global OpenCode config, which
   applies to every project, or in the repo `.opencode/opencode.jsonc`?
5. Should Phase 6 run, or should the changes ship on the evidence alone?

## Decisions

- 2026-10-25: The plan is a draft. No file in `dot_agents/`, `AGENTS.md`, or
  the OpenCode config changed during the review.
- 2026-10-25: The global rules stay global. The user keeps one rule set for
  every project. The review changes the content, not the scope.

## Deferred notes

- The skill catalog costs about 1,600 tokens on every session. No published
  study measures the damage of a large catalog on a flash model. A test with
  5 of the 11 skills disabled would answer it. That test is not in this plan.
- `~/.agents/rules.personal.d/asd-ste100-trigger.md` makes every reply over
  roughly 6 sentences load a 3,301-word skill. A separate measurement of how
  often that trigger fires would settle whether the cut in Phase 1 is worth
  the prose-quality cost.
- The `question` tool comes from the `opencode-magic-context` plugin, not
  from OpenCode. The `sudo-ask` and `ambiguity-resolution` rules depend on it
  with no fallback. A plain-text fallback sentence would close the gap.
- The `cc-safety-net` plugin blocks several destructive commands, but the
  audit read its bundled output by pattern search rather than from the policy
  source. The block list in Phase 4 is written from OpenCode's own permission
  mechanism, not from the plugin, so the two do not need to agree.

## Current status

Research phase done on 2026-10-25. Three parallel research passes produced the
model profile, the prompt-design evidence, and the internal audit. The plan
above is the proposed change set. No file changed yet. Next action is the
user's go-ahead and the answers to the five open questions.
