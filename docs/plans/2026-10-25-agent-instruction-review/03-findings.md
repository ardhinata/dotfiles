# Findings

The measured payload, the model profile, the findings that survive the
cross-check, and the finding that was withdrawn.

Part of the agent instruction review. See [README.md](README.md) for the index.
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

