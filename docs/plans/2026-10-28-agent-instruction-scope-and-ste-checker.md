---
status: active
goal: Record the agent-instruction scope split and the asd-ste100 checker work, with the open items
owner: ardhinata
last-updated: 2026-10-29
---

# Agent instruction scope split and the asd-ste100 checker

## Status

The work is applied to `$HOME` and verified. Two source files are pending:
the `asd-ste100` skill and its checker script. The change is not committed,
because it alters the source directory layout and AGENTS.md asks first in that
case.

## What changed

| Area | Change | State |
|---|---|---|
| `dot_agents/exact_rules.opencode/` | new directory, 6 files | applied |
| `dot_agents/exact_rules/ensemble-teams.md` | moved into that directory | applied |
| `dot_agents/exact_rules/rtk-rules.md.tmpl` + 2 template resources | deleted, `rtk` was never used | applied |
| `dot_agents/exact_rules/` | 4 rules generalised to drop tool names | applied |
| `dot_agents/rules.personal.d/` | 5 rules changed: 4 generalised, 1 de-duplicated | applied |
| `dot_config/opencode/private_opencode.jsonc` | `rules.opencode` glob added, `websearch` provider unpinned | applied |
| `dot_agents/skills/asd-ste100/` | `--print-prose` added, inline-code split bug fixed, second-pass section added | **pending** |

## The scope split

The question was which rule files name one harness's tools. Six were
OpenCode-specific and now live in `dot_agents/exact_rules.opencode/`, which
deploys to `~/.agents/rules.opencode/`:

`ensemble-teams.md` (moved whole), `long-running-tools.md`, `rtk-rules.md`
(deleted with the rule it belonged to), `scoped-searches.md`, `sudo-ask.md`,
`web-verification.md`, `zsh-emulate-fallback.md`.

Each shared rule kept its concept and lost the tool name. "The harness's
background-process facility" replaces `shell({ background: true })`. "The
harness's dedicated search and read tools" replaces the list of AFT tool names.

### The byte result

| | before | after | change |
|---|---|---|---|
| shared rules, every harness | 26,914 B | 21,811 B | −5,103 B (−19%) |
| OpenCode-scoped | — | 5,101 B | new |
| OpenCode always-on total | 26,914 B | 26,912 B | −2 B |

OpenCode's payload ends where it started. Every other harness drops 5.1 kB.

### Why the split matters less than it looks

No harness discovers `~/.agents/rules/` natively. Each one loads it through
its own `instructions` mechanism, and on this host only OpenCode has one. The
shared rule tree is, in practice, OpenCode's own load path. The split is a
clarity and cost decision, not a compatibility fix.

## The deletions

- **`rtk-rules.md` and its two template resources.** The `rtk` proxy was never
  invoked, on this host or in the retired Kilo tree. The rule's only durable
  content was the instruction not to wrap the harness's own tools.
- **`ssh-stdbuf-disable-buffering.md`.** The `ssh` skill owns the live-output
  table, and its description is always-on in the skill catalog. The rule kept
  the recipe without the reasons, which is what produced the reported failure:
  `stdbuf` works through `LD_PRELOAD`, so it cannot affect an application that
  buffers on its own. The skill states that cause. The rule did not.

## The asd-ste100 work

The question was whether to use the local checker script or the upstream
[asd-ste100-checker](https://github.com/sourdough-bread/asd-ste100-checker).
The answer was both: the local script stays the default checker, and the
upstream CLI adds an optional second pass for the dictionary and the
part-of-speech rules.

- The upstream CLI is installed at `~/.local/bin/ste100`, pinned to commit
  `e193ecdd66b09ce81b7c611f1c841efd8ba84cc7`, with `en_core_web_sm` 3.8.0 in the
  tool environment. The package is **not on PyPI**, and `ste100 setup` fails
  under `uv tool install`. The install commands in the skill are therefore not
  the ones in upstream's README.
- `--print-prose` was added to the local script. It prints the prose of a
  Markdown file without the markup. That is what upstream needs, because
  upstream has no Markdown support and would read code fences and table pipes
  as prose.
- A bug in the local script was fixed: it split sentences inside inline code,
  so `writing-rules.md` and every URL broke a sentence in two. That produced
  bogus excerpts and noun-cluster findings, and it hid real length violations
  by counting a long sentence as several short ones. The error counts across
  the tree now rise, because real violations are visible.

## Open items

1. **Apply the pending files.** `chezmoi diff` lists 40 files: the whole
   review, the STE campaign, and your own edits of today. Run
   `chezmoi apply --force`, because chezmoi asks for a confirmation and the
   tool shell has no TTY.
2. ~~**Fix the `AGENTS.md` pointer.**~~ Done on 2026-10-29. The Boundaries
   section named `dot_agents/rules/`, a directory that does not exist. The
   shared rules live in `dot_agents/exact_rules/`, and a harness-specific
   rule now goes in `dot_agents/exact_rules.<vendor>/` or
   `dot_config/<vendor>/rules/`.
3. ~~**Fix `document-conventions/SKILL.md` line 62.**~~ Done on 2026-10-29.
   The rule now states that no harness discovers `~/.agents/rules/` on its
   own. A rule naming one harness's tool belongs in that harness's own rule
   tree.
4. **Withdraw the 2026-10-25 review finding D-10.** It wanted more OpenCode
   names in the shared rules. This pass moved them out, so the finding points
   the other way now.
5. ~~**Decide about the tools the shared skills name.**~~ Done on 2026-10-29.
   The `github`, `project-context`, `project-layout` and
   `gitignore-toptal-api` files no longer name a harness tool. The shared
   `web-verification.md` rule names no tool, and the OpenCode supplement
   lists only `websearch` and `webfetch`.
6. **Decide where a host-tool bootstrap belongs.** The `ste100` install is
   host state that nothing in this repo reproduces.
7. **Optional.** The `ste100` MCP and LSP servers were not evaluated. The CLI
   is what this setup uses.
8. **The STE campaign had a narrower scope than it claimed.** It covered
   `dot_agents/` only. Still open: the live `openrouter-api` skill has 59
   errors, `.agents/skills/chezmoi/SKILL.md` has 4, and the project tree
   `.agents/docs/cache/` has 21. The `docs/` tree has 214 more, mostly in
   dated post-mortems and case studies. Rewriting a dated record is wrong,
   so treat those as exempt by design. Fix the live skills.

## Commits

Both landed on 2026-10-29, in two commits:

- `refactor(agents)` — the instructions and skills review, the
  document-conventions standards work, the asd-ste100 checker fix, and the
  STE campaign.
- `feat(cortexkit)` — `diagnostics_on_edit` in the AFT config, and the
  encrypted work SSH key.

## The document-conventions verification (2026-10-29)

Two research subagents checked every reference and template in the
`document-conventions` skill against its cited source. The skill is broadly
accurate but carried **11 wrong or unsupported citations**, all now fixed.

The durable artifact is `dot_agents/skills/document-conventions/references/standards-map.md`:
a per-doc-type and per-template verdict, the list of wrong citations with
their live replacements, and the types that deliberately ship no template.
The evidence sits in
`.agents/docs/cache/document-conventions/2026-10-29-standards-verification.md`.

Two templates were added, because the research showed a real gap:
`postmortem.md` (blameless, action items with an owner, a priority and a
tracking issue) and `design-doc.md` (goals and non-goals, trade-offs, and the
security, privacy, internationalization and storage questions).

No Diátaxis quadrant templates were added, on purpose: diataxis.fr asks for
no imposed structure.

The skill's own pre-existing STE violations were left alone. The files I
touched gained no new ones.

## The STE debt campaign (2026-10-29)

The whole agent tree now reports **zero** STE errors under
`ste_check.py --mode descriptive --errors-only`:

```
python3 dot_agents/skills/asd-ste100/scripts/ste_check.py --mode descriptive --errors-only <file>
```

About 320 errors across 42 files, paid with four parallel subagents on
disjoint file sets. What was fixed: semicolons split into two sentences.
Contractions expanded. Over-long sentences split. Compound verb forms
replaced with simple ones. Passive voice made active where the actor is
known. Latin abbreviations expanded.

What was not touched:

- `asd-ste100/examples/before-after.md` shows deliberate bad examples. Its
  explanatory prose is now clean, but the examples stay.
- `asd-ste100/NOTICE` and `LICENSE` are verbatim legal text.
- The quotes in `document-conventions/references/title-and-filename.md` are
  now blockquotes. The quoted words are unchanged, and the checker no longer
  reads them as the file's own prose.

The remaining 1373 warnings are advisory: "-ing" verb forms, noun clusters,
passive voice with an unknown actor, and words the checker cannot judge
without the official dictionary.

## See also

- `.agents/docs/cache/asd-ste100/2026-10-28-upstream-checker-capabilities.md`
- `.agents/docs/cache/agent-instructions/2026-10-28-harness-rule-discovery.md`
- `.agents/docs/cache/agent-instructions/2026-10-26-always-on-instruction-files.md`
