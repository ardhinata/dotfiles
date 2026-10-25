---
status: draft
goal: Make the always-on agent instruction set effective for minimax-m3.1-flash on coding tasks
owner: ardhinata
last-updated: 2026-10-25
---

# Agent instruction set review for MiniMax M3.1 Flash

> **Status: reworked after cross-check. Not approved.** Four independent
> reviewers checked the first draft. All four found material errors. Two
> findings removed the plan's central premise, and one showed that the
> permission block would have validated and done nothing. This version carries
> the corrected numbers and the two-tranche split. Read "Cross-check results"
> before "Implementation steps".

## Goal

Cut the always-on instruction payload and fix the defects in it. Add a gate for
destructive commands. Do not claim an effectiveness gain that the evidence
cannot support. The target model is `openrouter/minimax/minimax-m3.1-flash`, set
in `dot_config/opencode/private_opencode.jsonc`.

The earlier goal said "make the instruction set effective on coding tasks".
The cross-check showed that no evidence supports that claim. The goal now
matches what the plan can prove.

## Problem background

**The instruction set was written for a different class of model.** It grew
across two harness migrations. It carries 16 global rule files, four of which
are routers, plus two project files. Each file was justified on its own. No
step in the history asked whether the set as a whole fits a fast model.

**Every rule file breaks the house length standard.** The
document-conventions skill sets 30 to 80 words as the target and 150 words as
the ceiling for a rule file. All 16 global files exceed 150. The shortest is
`long-running-tools.md` at 170 words. The longest is
`zsh-emulate-fallback.md` at 630.

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

## Research steps

### Step 1. Measure the payload

Commands used:

- `wc -c -w` over `~/.agents/rules/*.md` and
  `~/.agents/rules.personal.d/*.md`. The deployed tree is the correct one to
  measure. The `.tmpl` sources are pre-render inputs, and
  `rtk-rules.md.tmpl` is 197 bytes against 1,780 bytes deployed.
- `wc -c -w -l` over `AGENTS.md` and
  `.agents/rules/chezmoi-source-project.md`.
- YAML parse of each `~/.agents/skills/*/SKILL.md` `description`.
- `node -e "require(...).getPonytailInstructions('full')"` to get the byte
  length of the block that is actually injected, not the size of the hook
  script.
- `opencode debug config`, `opencode --version`, `opencode models`.
- `chezmoi managed` to confirm which rule files deploy.

### Step 2. Model profile research

One research pass over public sources for MiniMax M3.1 Flash. It answered
seven questions: specs, instruction adherence, tool-calling reliability,
coding failure modes, effort trade-offs, speed, and comparison against
DeepSeek V4.1 Flash 1017 and GLM 5.3 Flash.

### Step 3. Prompt-design research

One research pass over published guidance: IFScale, Anthropic's
context-engineering and Agent Skills writeups, the OpenAI Codex and GPT-5.2
guides, the agentskills.io specification, the agents.md format, the Cursor
rules documentation, and Chroma's context-rot research.

### Step 4. Internal audit

A full read of all 18 always-on files plus the six skills the routers point
at. Output: an inventory, contradictions, redundancy, over-specification,
missing triggers, a safety inventory, and a ranked defect list.

### Step 5. Four independent cross-checks

Four reviewers with non-overlapping scope: external facts, internal
measurements, the live OpenCode technical surface, and an adversarial review
of the reasoning. Their findings are in "Cross-check results".

### What this review did not do

- No empirical test of rule adherence on this model.
- No read of the `cc-safety-net` policy source. Its block list was inferred
  from bundled output by pattern search.
- No tokenizer. The token figures use a uniform 3.6 to 3.7 bytes per token
  ratio and are approximations.
- No live test of the `policies` layer.

## Findings

### Measured always-on payload

| Layer | Bytes | Note |
|---|---|---|
| `~/.agents/rules/*.md` (8 files) | 17,376 | deployed; source `.md` glob is only 6 files |
| `~/.agents/rules.personal.d/*.md` (8 files) | 21,553 | deployed equals source |
| Global rule subtotal | **38,929** | |
| `AGENTS.md` + project rule | 5,801 | 704 words, 84 lines |
| Skill catalog (11 descriptions) | 4,995 | YAML-parsed values |
| `ponytail` injected block | 2,861 | 493 words. The 5,565 figure was the hook script |
| AFT tool notice | not measured | ~2,000 by estimate |
| **Total** | **~52,600** | **~16,500 tokens** |

The file-based part is 44,730 bytes across 18 files. The token total is an
estimate because the AFT row is unmeasured.

### Model profile

| Property | Value | Note |
|---|---|---|
| Context window | 1,000,000 tokens | 512K is MiniMax's recommended client window for coding, not a provider limit. 512K is also the max output |
| Reasoning effort | `low` to `max`, default `max` | Thinking cannot be disabled. `none` returns HTTP 400 |
| Price per 1M | $0.15 in, $0.60 out, $0.015 cached | Flat, no long-context surcharge |
| AA Intelligence Index | 43 | 42 at launch. AA revised it. Date any citation |
| AA-Omniscience accuracy | 56.2% | |
| AA-Omniscience hallucination rate | 92.8% | Of misses, not of all answers. About 41% of all answers are wrong |
| Predecessor M3 hallucination rate | 18.4% | |
| Terminal-Bench 4.0 | 25.8% | DeepSeek V4.1 Flash 33.8%, GLM 5.3 Flash 32.8% |
| LiveBench Long Agentic | 34.7% | DeepSeek V4.1 Flash 50.9% |
| LiveBench 2.0 Coding | 83.9% | DeepSeek V4.1 Flash 96.0% |
| IFBench (predecessor M3) | 82.9%, rank 2 of 423 | The family is strong at instruction following. This model has no score |

### The findings that survive

**F-1. Instruction adherence is unmeasured for this model, and the family is
strong at it.** The first draft's opposite claim is withdrawn. MiniMax M3
scores 82.9% on IFBench, rank 2 of 423 configurations. M3.1 Flash has no
IFBench, BFCL, or multi-turn retention score. Treat any assumption about how
it handles 18 rule files as untested, in both directions.

**F-2. The default reasoning effort is expensive, and the multiplier is
disputed.** One measurement on one small task found 48 times the reasoning
tokens and 12 times the wall clock of `low`. It found 7 times the cost. The
result was identical at 96 of 96.
A separate measurement across 8 coding tasks found
7.7 times the reasoning tokens and 3.7 times the wall clock. Cite a range. The
48 times figure is the outlier.

**F-3. The loop finding is not specific to this model.** A no-progress loop
fired in 3 of 3 `max` runs and 0 of 3 `low` runs. The same detector fired in
2 of 3 runs for MiniMax M3 and GLM 5.3 Flash. It is a long-reasoning
signature, not a defect of this model. It still deserves a counter, because
the harness can supply one cheaply.

**F-4. Long context is survivable. Constraint count is untested.** AA-LCR puts
the model at 79.7% on 10k to 100k token documents. A 6,500-word rule set is
therefore not the problem. What no study measures is instruction adherence at
18 rule files, and IFScale shows the flash cohort dropping from 66-96% at 50
constraints to 42-82% at 100. Constraint count, not byte count, is the axis
the evidence points at.

**F-5. No rule gates a destructive command.** This is the largest certain gap.
The `cc-safety-net` plugin blocks several, but it is a tool-layer backstop and
it does not gate `sudo`. `sudo-ask.md` does gate `sudo`, so the gap is the
destructive shell command, not privilege escalation.

### The withdrawn finding

The first draft claimed, as its central premise, that "prose guards make this
model worse". Basis: one test where adding an instruction to admit uncertainty
raised invented answers from 10 of 20 to 14 of 20. Three problems:

1. **Power.** A four-run swing on twenty runs gives Fisher exact p about 0.33.
   The DeepSeek control arm is p about 0.09. Neither is significant.
2. **Confound.** Six of 40 runs hit the 8,192-token output cap and returned a
   guess. Declines stayed at 5 of 20. The prompt converted truncated runs
   into answers. It did not change a willingness to abstain.
3. **Source.** One blog post. No independent reproduction.

The premise is withdrawn. Structural counters are still recommended, because
they are cheap and testable, not because prose is disproven.

### The audit defect list

| ID | File | Defect |
|---|---|---|
| D-1 | `AGENTS.md:34` | "Commit the working tree after a refactor" collides with "Ask first: structural changes to the source directory layout" at lines 38-41. No precedence. |
| D-2 | `document-conventions.md:19-23` | Copies 5 rows of the skill's decision matrix. The "authoritative picker" sentence is at line 9. |
| D-3 | `document-conventions.md:23` | Points at `.agents/skills/<name>/SKILL.md`. Line 22 of the same table uses `~/.agents/`. The repo `.agents/skills/` holds 3 unrelated skills. |
| D-4 | `zsh-emulate-fallback.md` | 630 words, 10.2% of the rule budget. The file records that the host pins bash, which makes its own trigger near-unreachable. |
| D-5 | `ssh-agent-keys-location.md:21-46` | 220 words of GnuPG reference, 41% of the file, not rules. |
| D-6 | `asd-ste100-trigger.md:12` | Fires on any reply over roughly 6 sentences. Each firing loads a 3,301-word skill, which is 0.57 times the entire rule set. |
| D-7 | `asd-ste100-trigger.md:20,22` | One clause appears twice in the same file. |
| D-8 | missing file | No destructive-action rule. Confirmed by grep. |
| D-9 | `long-running-tools.md:19-28` | Line 28 lists `subagent` in the fan-out table. Lines 23-24 ban fan-out for delegated research. |
| D-10 | `scoped-searches.md:5`, `rtk_installed.md` | Names only `glob`, `grep`, `read`. Omits `aft_search`, `aft_outline`, `aft_zoom`. |
| D-11 | `rtk-rules.md` | 248 words, 31 lines. Five lines carry information the model does not already have. |
| D-12 | `scoped-searches.md:24,30` | Line 24 names `~/.gnupg/`. Line 30 bans recursing into `~/.gnupg/private-keys-v1.d/`. Six lines apart. |
| D-13 | `scoped-searches.md:32-41` | The three miss responses sit inside a numbered list, so the order is stated. Low severity. |
| D-14 | `web-verification.md:20-23,64-68` | Tells the model to create a cache directory in any project. The escape clause "when project rules prohibit writes" is the only hit for `prohibit` in all 18 files. |
| D-15 | `ssh-read-allowlist.md`, `ssh-agent-keys-location.md` | Two rules grant and deny `~/.ssh/agent-keys/`. The project rule's `key` substring ban is a third denial. |
| D-16 | `AGENTS.md:47` | "Without understanding the re-encrypt workflow" is not checkable. |
| D-17 | `AGENTS.md:44` | Names 3 extensions. The project rule line 11 names 15 patterns. |
| D-18 | `document-conventions/SKILL.md:98,176` | Two different plan paths. |

## Cross-check results

Four reviewers, non-overlapping scope, all four found material errors.

| Reviewer | Scope | Verdict | Material errors |
|---|---|---|---|
| Adversarial logic | Does each recommendation follow from its evidence | Rework | F-1 is p about 0.33 and confounded. The plan optimises bytes while its own F-3 names constraints. `git commit` ask deadlocks the Phase 2 commit rule. `git push --force*` blocks the safe `--force-with-lease` form. Loops get no rule. Phase 6 is underpowered. |
| External facts | 26 claims against primary sources | Major corrections | The 92.8% figure is misused by a factor of 2.3. The pivotal test is underpowered and confounded. 48 times is an outlier. "512,000 on some providers" is wrong. NeQA is overstated. The family scores 82.9% on IFBench, which undercuts the premise. |
| Internal measurement | 8 payload figures, 9 word counts, 18 defect claims | Minor corrections | "9 of 16 above the ceiling" is really 16 of 16. The ponytail injection is 2,861 bytes, not 5,565. 3,301 words is 0.57 times the rule set, not 2.9 times. All 18 defect line references were confirmed. |
| OpenCode technical | Live v2.1.4 binary and schema | **The block is inert** | `action: "bash"` does nothing; v2 uses `"shell"`. Ordering is documented: last match wins. Patterns are whole-value anchored. A deny-list is the wrong shape. `agents.variant` is invalid. |

### What each reviewer changed

| Correction | Effect on the plan |
|---|---|
| `bash` to `shell` | Phase 4 rewritten. Proven by a live A/B test: a `bash` deny let the command run, a `shell` deny blocked it |
| Deny-list to default-ask plus allowlist | Phase 4 rewritten. The docs warn against recognising every dangerous command by pattern |
| "9 of 16" to "16 of 16" | Recommendation 1 downgraded from HIGH to MEDIUM. The byte target no longer follows from the ceiling |
| 49% to 33% | The 20,000-byte target is withdrawn. Recomputed below |
| ponytail 5,565 to 2,861 | The payload total drops to ~52,600 bytes |
| 2.9 times to 0.57 times | The `asd-ste100` argument weakens. It is still the largest single on-demand load |
| F-1 withdrawn | "Structural, not prose" is no longer a design law. The two new rules lose their justification as a class |
| IFBench 82.9% for the family | The premise that a fast model needs a smaller set is unsupported |
| `git commit` ask dropped | Conflicts with Phase 2. Phase 2 gets fixed first |
| `agents.variant` moved inside `model` | Phase 5 snippet corrected |

### What survived all four reviews

D-1, D-2, D-3, D-7, D-12, and D-18. These are quote-level defects with no
theory attached. They ship in tranche 1 regardless of what happens to the
rest. The choice of the four worst-value files to cut also survived:
`zsh-emulate-fallback`, the GnuPG block, the `stdbuf` caveats, and the
`rtk-rules` command categories.

## Conclusion

**Verdict.** Do not apply as written. Apply in two tranches.

### Tranche 1: safe today

Independent of every contested inference. Ship this.

1. Phase 2, items 1 to 8. The contradiction and path fixes.
2. A destructive-action gate with repaired patterns.
3. A loop stop-condition rule of one sentence.
4. The `git commit` question left alone until Phase 2 item 1 lands.

### Tranche 2: contested

Gate this behind a decision.

1. The byte cut. The target is no longer 20,000 bytes. See below.
2. The two new rules, which no longer rest on a design law.
3. The effort change, which is the weakest evidence in the document.

### The corrected arithmetic

The Phase 1 table's word targets sum to 3,715 words down to 1,510. Those nine
files hold about 24,700 bytes. Applying the same bytes-per-word ratio to the
survivor counts saves about 14,700 bytes, leaving about 24,300. The two new
rules add about 1,700 bytes. **Landed total is about 26,000 bytes, a 33% cut.**

That is a real cut. It is not 49%. Reaching 20,000 would need another ~950
words from files Phase 1 never lists: `local-first` 388, `sudo-ask` 413,
`project-context` 316, `ambiguity-resolution` 262, `ssh-read-allowlist` 264,
`zsh-stack` 257, `long-running-tools` 170.

After a 9-file cut, **seven files still breach the 150-word ceiling**, and two
of those are safety files this plan deliberately protects. State that
trade-off rather than calling the cut complete.

### The model question

The plan's own numbers say DeepSeek V4.1 Flash 1017 is better on every
code-execution metric: Terminal-Bench 33.8 against 25.8, LiveBench Coding 96.0
against 83.9, Long Agentic 50.9 against 34.7. The first draft put the model
choice out of scope without comparing anything.

The honest position is a trigger, not silence. If code-execution quality on
hard tasks matters more than the latency and price difference, the swap beats
this plan's instruction work. Holding the model fixed is defensible for a
single-variable test. It is not defensible as a permanent default.

### What the plan does not deliver

It does not make the model better, and it does not deliver a measured
effectiveness gain. It delivers a smaller rule set, a real destructive-command
gate, and a loop stop-condition.

### Confidence per recommendation

| # | Recommendation | Confidence | Basis |
|---|---|---|---|
| 1 | Fix the contradictions and path defects | HIGH | Quote-level. All confirmed by measurement |
| 2 | Add a destructive-action gate | HIGH | The gap is certain. The permission mechanism was proven live |
| 3 | Add a loop stop-condition | MEDIUM | The base rate is shared with two other models. The counter is cheap |
| 4 | Cut the nine worst-value files | MEDIUM | Per-file word counts confirmed. The 33% total is arithmetic, not measurement |
| 5 | Add a verify-before-claiming rule | LOW | The motivating experiment is withdrawn. Keep only the unlaunderable parts |
| 6 | Change the default effort | LOW | Two blog curves on different tasks. The plan's own Phase 6 cannot test it |

## Refined approach

Three rules drive the changes.

1. **Ship what is provable.** A defect confirmed by reading the file ships now.
   A behaviour change that depends on one underpowered test waits.
2. **Structural where possible, honest where not.** A re-read and a named
   command are testable. A closing self-report is not. Keep the first, label
   the second.
3. **One owner per guard.** If the harness can enforce a command, the harness
   owns it. The rule file covers only what the harness cannot express. Three
   drifting lists is worse than one.

**Where the changes land.** Phases 1, 3, and 5 are global by construction.
Phase 2 is split: three of its eight fixes are in `AGENTS.md`, which is
repo-scoped. Phase 4 is a choice between the global config and
`.opencode/opencode.jsonc`. A guard written as OpenCode config does not reach
Codex or Claude Code.

## Implementation steps

### Phase 1. Cut the payload

Target: **about 26,000 bytes, a 33% cut.** Not 20,000. Count constraints, not
just words.

| File | Words now | Words after | Action |
|---|---|---|---|
| `zsh-emulate-fallback.md` | 630 | ~60 | Keep the host fact and the `bash -c` fallback. Delete the `emulate` semantics and the option-leak detail. |
| `ssh-agent-keys-location.md` | 540 | ~140 | Keep the placement rule and the 6-step process. Move the GnuPG internals to a skill reference. |
| `ssh-stdbuf-disable-buffering.md` | 358 | ~80 | Keep the `stdbuf -oL -eL` rule and the static-linking fallback. Move the caveats to the same skill. |
| `asd-ste100-trigger.md` | 298 | ~200 | Replace the length threshold with an artifact list. Drop the repeated clause. |
| `rtk-rules.md` | 248 | ~90 | Keep "never wrap the dedicated tools", "wrap each sub-command", and the diagnostic modes. |
| `document-conventions.md` | 258 | ~130 | Delete the inline matrix. Point at the skill. Fix the skill path. |
| `web-verification.md` | 512 | ~330 | Drop the volatility table. Keep the two thresholds. Scope the cache write. |
| `scoped-searches.md` | 482 | ~250 | Replace the 8-step process with 3 lines. Fix the `~/.gnupg/` row. |
| `runtime-tools.md` | 389 | ~230 | One line per tool. Stop copying skill text. |

New files add about 1,700 bytes. Seven untouched files still breach the
ceiling. Say so in the commit message.

### Phase 2. Fix the contradictions

1. `AGENTS.md:34`. Replace with: "After a refactor that does not change the
   source directory layout, run `git status --short`, stage, and commit before
   you end the session. If the refactor changes the layout, ask first and do
   not commit."
2. `AGENTS.md:47`. Replace with: "Never modify `.encryption_keys/`. Adding a
   recipient key rewrites every encrypted file, so run `chezmoi re-encrypt`
   only after the user approves."
3. `AGENTS.md:44`. Replace the 3-extension list with a pointer to
   `.agents/rules/chezmoi-source-project.md`, which names 15 patterns.
4. `long-running-tools.md`. Split the table. One row for worktrees on explicit
   request. One row for delegated research through `subagent`, always allowed.
5. `scoped-searches.md:24`. Replace `~/.gnupg/` with
   `~/.gnupg/gpg-agent.conf` and `~/.gnupg/gpg.conf`, and add "files, not the
   directory".
6. `ssh-read-allowlist.md`. Add `~/.ssh/agent-keys/` for directory listings
   and `*.pub` files only. State that this carve-out beats the general denial.
7. `web-verification.md`. Add: "Write a cache entry only in a repository that
   already has `.agents/docs/cache/`. Otherwise skip the cache and note the
   gap in your reply."
8. `document-conventions/SKILL.md:176`. Match line 98.

### Phase 3. Add three rules

**`dot_agents/rules.personal.d/destructive-actions.md`.** One line per
command. Each ends: "Ask first. Print the exact command in the reply so the
user can run it."

- `rm -rf`, `rm -fr`, `rm -r -f`, or `rm -r` on a path outside the working directory
- `git reset --hard`, `git clean -fd`, `git push --force`, `git push -f`
- `chezmoi apply`, `chezmoi re-encrypt`, `chezmoi update`
- `chmod`, `chown`, or `mv` on a path outside the working directory

Do not list `sudo` here. `sudo-ask.md` already owns it, and this plan should
not duplicate a guard that already works.

**`dot_agents/rules/verify-before-claiming.md`.** Keep only the unlaunderable
parts. A model that invents a path can invent a line number for it, so a
citation is not proof on its own.

- After you edit a file, read it back and check the change is there.
- After you change code, run the project test or check command. Do not report
  the change as done until the command exits 0.
- Cite only paths and line numbers that a tool returned in this session. If
  you have not opened the file, open it first.
- When you run a command, show the command and its exit code.
- When a check cannot run, say so and name the reason.

Do not add a closing self-report line. The cross-check showed it is the class
of evidence a model can fabricate without detection.

**`dot_agents/rules/no-progress-stop.md`.** One sentence, and the only
structural counter for the loop failure:

> If two consecutive attempts at the same step produce no new tool evidence,
> stop and report what is blocked.

### Phase 4. Move the guard to the harness layer

**The action token is `shell`, not `bash`.** A block written with `bash`
validates against the schema and blocks nothing. This was proven live. A
`bash` deny let `echo` run. The same deny with `shell` blocked it.

**Ordering is last-match-wins.** Global rules load first, then project rules,
then agent rules. Put the broad rule first and the specific exceptions after
it.

**Use default-ask plus an allowlist, not a deny-list.** The OpenCode docs warn
against patterns that try to recognise every dangerous command. A deny-list
misses `rm -fr`, `rm -r -f`, `sudo rm -rf x`, and `cd /tmp && rm -rf x`,
because matching is whole-value anchored.

```jsonc
"permissions": [
  // broad default: ask before any shell command
  { "action": "shell", "resource": "*",                        "effect": "ask" },

  // routine, read-only, no prompt
  { "action": "shell", "resource": "git status*",              "effect": "allow" },
  { "action": "shell", "resource": "git diff*",                "effect": "allow" },
  { "action": "shell", "resource": "git log*",                 "effect": "allow" },
  { "action": "shell", "resource": "chezmoi diff*",            "effect": "allow" },
  { "action": "shell", "resource": "chezmoi apply --dry-run*", "effect": "allow" },

  // destructive: deny last so it beats the broad ask
  { "action": "shell", "resource": "*rm -*rf*",                "effect": "deny" },
  { "action": "shell", "resource": "*rm -*fr*",                "effect": "deny" },
  { "action": "shell", "resource": "*git reset --hard*",       "effect": "deny" },
  { "action": "shell", "resource": "*git clean -*",            "effect": "deny" },
  { "action": "shell", "resource": "*git push --force*",       "effect": "deny" },
  { "action": "shell", "resource": "*git push -f*",            "effect": "deny" }
]
```

The leading `*` is load-bearing. Without it, `sudo rm -rf x` is not caught.
The `chezmoi apply --dry-run` allow must sit after the broad ask, or it is
dead.

**Do not add `git commit*` here.** It contradicts Phase 2 item 1, and in a
subagent run there is nobody to answer the prompt. Fix `AGENTS.md:34` first,
then let the broad `ask` cover commits.

**For a gate that cannot be overridden, use `policies`.** Only policies turn
an allow into a deny, and they survive saved approvals and project config:

```jsonc
"policies": [ { "action": "tool.use", "resource": "shell:sudo *", "effect": "deny" } ]
```

**Do not ship a catch-all `deny`.** A blanket
`{ "action": "shell", "resource": "*", "effect": "deny" }` stalled
`opencode run` for over five minutes. Narrow denies fail in under a second.

**Known limit:** global permissions are appended before project rules, so a
project with its own shell rule overrides this block. State that in the commit
message rather than calling the guard absolute.

### Phase 5. Reasoning effort

**The variant goes inside `model`, not beside it.** `agents.<name>.variant` is
rejected by the schema; `agents` uses `Config.AgentEncoded`, which does not
allow it.

```jsonc
// global default, either form is valid
"model": "openrouter/minimax/minimax-m3.1-flash#high"
"model": { "providerID": "openrouter", "model": "minimax/minimax-m3.1-flash", "variant": "high" }

// per-agent override
"agents": {
  "title": {
    "model": { "providerID": "openrouter", "model": "qwen/qwen3.7-flash", "variant": "low" }
  }
}
```

A subagent that pins its own model loses the parent variant. That is
documented behaviour.

| Task type | Effort | Evidence |
|---|---|---|
| Read, search, single-file edit | `low` | 48 s and 1.3K reasoning tokens at `low`, against 9.5 min and 60.6K at `max`, same result |
| Multi-file edit, bug hunt | `medium` or `high` | Vendor Automation-Bench spread of 10 points from `low` to `max` |
| Long-horizon agent run | `max` | Vendor data puts `max` 10 points above `low` here |

This table cannot be expressed as one global default. OpenCode has one root
model. A global `high` overrides the `max` row. Choose: either accept `high`
everywhere and drop the third row, or set the root to `max` and override per
agent.

Grade this LOW. Do not ship it in tranche 1.

### Phase 6. Pilot, not measurement

Relabel this phase. It cannot detect the effects the plan claims.

At 8 to 12 tasks and 3 runs per arm, two proportions near 50% give a minimum
detectable effect of about 31 percentage points. Near the 92.8% ceiling it
detects nothing at all. Three runs per task are also correlated by task
difficulty, so the effective sample is closer to 12 than 36.

What the phase can do:

- Surface qualitative failures and build a harness for later work.
- Test the destructive gate, where 0 of 3 against 3 of 3 is weak but visible.

What it cannot do:

- Test the effort change, because the design holds effort fixed.
- Detect an adherence improvement.

If this becomes evidence rather than instrumentation, it needs three things.
Pre-register a single primary metric. Analyse paired by task. Budget at least
100 runs per arm for the invention metric.

### Phases that are now out of scope

The first draft's "structural counters, not prose counters" premise is
withdrawn. Do not rewrite the existing rules to remove prose. That work has no
evidence behind it.

## Risks and mitigations

- **Risk:** a cut rule carries something the model needed. **Mitigation:** one
  commit. One revert restores the old text.
- **Risk:** the `permissions` block prompts on every command and makes the
  session unusable. **Mitigation:** the allowlist covers the five read-only
  commands that dominate a session. Add to it as needed.
- **Risk:** a project `.opencode/opencode.jsonc` silently overrides the global
  block. **Mitigation:** use `policies` for the rules that must hold.
- **Risk:** the deny patterns miss a variant. **Mitigation:** the broad `ask`
  is the real guard. The denies are defence in depth.
- **Risk:** tranche 2 ships without evidence, as tranche 1 did. **Mitigation:**
  the confidence table says LOW for both contested items. Ship them as hygiene
  changes and say so.
- **Risk:** a bare `chezmoi apply` deploys unrelated in-flight changes.
  **Mitigation:** apply by target. `chezmoi apply ~/.agents/rules` and
  `chezmoi apply ~/.config/opencode/opencode.jsonc`.

## Open questions

1. Do you accept the two-tranche split, or do you want one change set?
2. Tranche 2: ship as hygiene, or gate behind a pilot?
3. Is a 33% cut worth the work, given seven files still breach the ceiling?
4. Should the ceiling itself be relaxed for the safety files, or enforced on
   all 16?
5. Global `permissions`, or repo `.opencode/opencode.jsonc`?
6. If code-execution quality matters more than latency, should the model swap
   be evaluated before this plan? The plan's own data favours the swap.

## Decisions

- 2026-10-25: The plan is a draft and is not approved. No file in
  `dot_agents/`, `AGENTS.md`, or the OpenCode config changed during the
  review.
- 2026-10-25: Phase 4 uses `action: "shell"`. The v1 token `bash` validates
  and does nothing.
- 2026-10-25: Phase 4 uses default-ask plus an allowlist. A deny-list cannot
  express the policy, because matching is whole-value anchored.
- 2026-10-25: Phase 5 puts `variant` inside `model`. `agents.<name>.variant`
  fails schema validation.
- 2026-10-25: F-1 is withdrawn. The motivating experiment is p about 0.33 and
  confounded by the output-token cap.
- 2026-10-25: The 20,000-byte target is withdrawn. The arithmetic lands at
  about 26,000 bytes, a 33% cut.
- 2026-10-25: The `git commit` permission entry is dropped. It conflicts with
  the session-end commit rule and stalls unattended runs.

## Deferred notes

- The skill catalog costs about 5,000 bytes, roughly 1,300 tokens, on every
  session. No published study measures the damage of a large catalog on a
  flash model.
- OctoBench (arXiv 2601.10343) measures instruction adherence per injection
  channel: system prompt, Agents.md, memory, tool schema. It covers
  MiniMax-M2.1, not M3.1 Flash. It is the right design for a future Phase 6.
- `asd-ste100-trigger.md` loads a 3,301-word skill on any reply over about 6
  sentences. That is 0.57 times the whole rule set. Whether it fires often
  enough to matter is unmeasured.
- The `cc-safety-net` plugin and the `permissions` array are two guards over
  the same commands. They should not both be maintained. Pick one owner.
- The `question` tool comes from the `opencode-magic-context` plugin, not
  OpenCode. `sudo-ask.md` and `ambiguity-resolution.md` depend on it with no
  fallback.

## References

### Model

- MiniMax M3.1 Flash announcement — https://www.minimax.io/blog/minimax-m31f
- MiniMax Codex guide (effort ladder, 512K client window) —
  https://platform.minimax.io/docs/m-plan/codex.md
- MiniMax tool-use guide (`reasoning_content`, interleaved thinking) —
  https://platform.minimax.io/docs/guides/text-m3-function-call
- MiniMax text-generation guide —
  https://platform.minimax.io/docs/guides/text-generation
- Artificial Analysis model page —
  https://artificialanalysis.ai/models/minimax-m3-1-flash
- AA-Omniscience definition —
  https://artificialanalysis.ai/evaluations/omniscience
- Artificial Analysis launch thread —
  https://x.com/ArtificialAnlys/status/2112211865128608002
- AI/ML API hands-on review (the controlled admit-uncertainty test, the effort
  ladder, the effect-ladder comparison) —
  https://aimlapi.com/blog/minimax-m3-1-flash-review
- Atomic Agent test (low against max on one task, loop detector) —
  https://atomicagent.io/blog/minimax-m3-1-flash/
- BenchLeader model page (Terminal-Bench, LiveBench, IFBench gap) —
  https://www.benchleader.com/models/minimax-m3-1-flash
- BenchLeader IFBench leaderboard (MiniMax M3 at 82.9%, rank 2) —
  https://www.benchleader.com/benchmarks/aa_ifbench
- OpenCode public usage data —
  https://opencode.ai/data/minimax/minimax-m3-1-flash

### Prompt design

- IFScale — https://arxiv.org/abs/2507.11538
- OctoBench, scaffold-aware instruction following in repository-grounded
  agentic coding — https://arxiv.org/abs/2601.10343
- Anthropic, effective context engineering —
  https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
- Anthropic, Agent Skills —
  https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic, writing effective tools —
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, Claude Code best practices —
  https://www.anthropic.com/research/claude-code-best-practices
- OpenAI, Codex prompting guide —
  https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- OpenAI, GPT-5.2 prompting guide —
  https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- agentskills.io specification — https://agentskills.io/specification
- agents.md — https://agents.md
- Cursor rules — https://cursor.com/docs/rules
- Chroma, context rot — https://research.trychroma.com/context-rot

### Harness

- OpenCode config schema — https://opencode.ai/config.json
- OpenCode permissions (v2 action names `shell` and `subagent`, last match
  wins) — https://opencode.ai/docs/permissions
- OpenCode policies — https://opencode.ai/docs/policies
- OpenCode models and variants — https://opencode.ai/v2/docs/models
- OpenCode instructions — https://opencode.ai/v2/docs/instructions

### Internal

- `.agents/skills/document-conventions/references/structure-and-length.md` —
  the 30-80 word target and 150-word ceiling
- `dot_agents/rules/.template-resources/` — six host-rendered snippets, not
  deployed (`chezmoi managed` count is 0)
- `dot_config/opencode/private_opencode.jsonc` — the effective config

## Current status

Reworked after four independent cross-checks on 2026-10-25. Two findings
removed the plan's central premise: the motivating experiment is p about 0.33
and confounded, and the model family scores 82.9% on IFBench. One finding
showed that the permission block would be inert under the v1 action token:
`action: "bash"` does nothing in v2. The plan is split into a safe tranche and
a contested tranche. No file in `dot_agents/`, `AGENTS.md`, or the OpenCode
config changed. Next action is the user's answers to the six open questions.
