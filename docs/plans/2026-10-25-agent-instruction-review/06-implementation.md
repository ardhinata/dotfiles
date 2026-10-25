# Implementation steps

The six phases, the risks, the open questions, the decisions, and the deferred
notes.

Part of the agent instruction review. See [README.md](README.md) for the index.
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

**APPLIED in commit `d00aed8`.**

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

**APPLIED in commit `25724dd`.**

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

**APPLIED. The shape below changed during implementation. Three corrections
were verified live on the host; each is in the commit message.**

**The action token is `shell`, not `bash`.** A block written with `bash`
validates against the schema and blocks nothing. This was proven live. A
`bash` deny let `echo` run. The same deny with `shell` blocked it.

**Ordering is last-match-wins.** Load order is project, then global, then
agent. A global rule therefore beats a project rule on conflict.

**The patterns must be path-anchored.** The shell scanner pulls words out of
quoted strings, so a command whose text mentions the flag is treated as a
compound command. A `*rm -*rf*` pattern denies any command whose text
mentions the flag, including a commit message that documents the rule. The
applied patterns require an absolute path, `~/`, `./`, or `../` after the
flag.

```jsonc
"permissions": [
  { "action": "shell", "resource": "rm -*rf /*",  "effect": "deny" },
  { "action": "shell", "resource": "rm -*rf ~*",  "effect": "deny" },
  { "action": "shell", "resource": "rm -*rf ./*", "effect": "deny" },
  { "action": "shell", "resource": "rm -*rf ../*","effect": "deny" },
  { "action": "shell", "resource": "rm -*fr /*",  "effect": "deny" },
  { "action": "shell", "resource": "rm -*fr ~*",  "effect": "deny" },
  { "action": "shell", "resource": "rm -*fr ./*", "effect": "deny" },
  { "action": "shell", "resource": "rm -*fr ../*","effect": "deny" }
]
```

**Only `rm` belongs here.** A live test with all OpenCode shell rules
removed showed that cc-safety-net already blocks `git reset --hard`,
`git clean -fd`, `git push --force`, and `git push -f`. The git rules were
dropped as redundant. The plugin also blocks `rm -rf /` and `rm -rf ~`.

**A bare relative name is not caught.** `rm -rf build` is not distinguishable
from quoted text, so the `destructive-actions.md` rule covers it.

**Do not add `git commit*` here.** It contradicts Phase 2 item 1, and in a
subagent run there is nobody to answer the prompt.

**For a gate that cannot be overridden, use `policies`.** Only policies turn
an allow into a deny, and they survive saved approvals and project config:

```jsonc
"policies": [ { "action": "tool.use", "resource": "shell:sudo *", "effect": "deny" } ]
```

**Do not ship a catch-all `deny`.** A blanket
`{ "action": "shell", "resource": "*", "effect": "deny" }` stalled
`opencode run` for over five minutes. Narrow denies fail in under a second.

**Known limit:** global permissions load after project rules, so a project
with its own shell rule overrides this block. State that in the commit
message rather than calling the guard absolute.

### Phase 5. Reasoning effort

**APPLIED in commit `70d16db`.** The root model is pinned to
`openrouter/minimax/minimax-m3.1-flash#high`. The `title` agent is pinned to
`openrouter/qwen/qwen3.7-flash#none`, because that model exposes a toggle
rather than an effort ladder. Both forms were verified against the live
config loader.

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

