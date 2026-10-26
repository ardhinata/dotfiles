# Skills catalog analysis

An analysis of the 11 skills under `dot_agents/skills/`, deployed to
`~/.agents/skills/`. Part of the agent instruction review. See
[README.md](README.md) for the index.

## Status

**The catalog changes are applied** in commits `70d16db` and `5f84870`.

| Change | Applied |
|---|---|
| Correct the four broken `gh` commands | Yes |
| Correct the six stale `zsh-stack` line anchors | Yes |
| Delete `tavily-defaults` and `spec-kit` | Yes, plus `skill` permission denies |
| Merge `fnm` into the `runtime-tools` rule | Yes |
| Trim the four long skill descriptions | Yes |
| Remove the three re-inlined tables from `document-conventions` | Yes |
| Remove the duplicate AGENTS.md template | Yes |
| Move the vendor-unification procedure to `project-layout` | Yes |
| Move the `zsh-stack` reference tables to `references/` | Yes |
| Fix the `ste_check.py` relative path | Yes |
| Fix the stale description quote and the `$ARGUMENTS` residue | Yes |
| Merge `container-tools` into the rule | **No.** See below |

**`container-tools` was kept as a skill.** The analysis recommended merging
it into the `runtime-tools` rule, on the grounds that the host has already
resolved the runtime question. That is true of the *detection* half. The
compose-variant table, the OCI image reference rules, the SELinux relabel
notes, and the rootless port limits are not derivable and are not covered by
the rule. The rule points at the skill instead. The cost is 69 always-paid
tokens; the alternative was to move roughly 40 lines of reference material
into an always-on rule.

## Summary

The catalog is well built but has three structural problems. One skill documents
tools that do not exist on this host. One skill describes a tool that was
retired six weeks ago. Two more are so small they belong in a rule file. The
rest carry about 14 KB of duplicated body text.

The catalog costs about 1,240 tokens per request, paid whether or not any
skill ever fires. Deleting two dead skills and merging two small ones removes
15% of that cost and four skill bodies from disk.

| Measure | Value |
|---|---|
| Skills | 11, now 9 |
| Total directory bytes | 304,451 |
| Catalog cost, always paid | 4,995 bytes, about 1,240 tokens, now 4,143 bytes |
| Largest single activation | `zsh-stack`, about 4,450 tokens, now about 3,700 |
| Avoidable duplication | about 14 KB of body text |
| Dead skills | 2 (`tavily-defaults`, `spec-kit`) |

## Method

- Read all 11 `SKILL.md` bodies and every file under each `references/`,
  `assets/`, and `examples/` directory.
- Measured duplication with 5-gram shingle overlap between file pairs.
- Verified every factual claim inside the skills against the live host:
  `opencode mcp list`, `opencode --version`, `gh --help`, `fnm --help`,
  `podman --version`, and the actual line numbers of the files the skills cite.
- Compared each skill against the four router rules in `dot_agents/rules/`.
- Cross-checked the design against the published skill-design literature. The
  sources and their confidence grades are in
  [08-references.md](08-references.md).

## Per-skill verdict

| Skill | Dir bytes | SKILL.md lines | Desc chars | Purpose | Verdict | Reason |
|---|---:|---:|---:|---|---|---|
| `asd-ste100` | 64,610 | 343 | 828 | Rewrite English to ASD-STE100 controlled language | TRIM | Trigger sits at char 350 of 828. Under a 400-char cut the skill becomes undiscoverable. Body restates `references/writing-rules.md` |
| `container-tools` | 5,385 | 120 | 276 | Pick podman vs docker | MERGE | The host already resolved this. Its one live value is the compose cheat sheet, which fits the `runtime-tools` rule |
| `document-conventions` | 99,775 | 259 | 714 | Filename, frontmatter, section, and length rules per doc type | SPLIT | 99 KB across 20 files, but SKILL.md re-inlines three of its own references. Two AGENTS.md templates compete |
| `fnm` | 1,980 | 58 | 129 | Node version management | KEEP | Small, correct, one clear trigger. But the shell auto-switches versions, so the trigger is broader than needed |
| `github` | 8,760 | 204 | 341 | `gh` CLI recipes | TRIM | Three documented commands fail on the installed `gh` 2.102.1. 204 lines of CLI syntax that `gh help` covers |
| `opencode-ensemble` | 20,717 | 124 | 234 | Coordinate multi-agent teams | KEEP | Byte-identical to upstream. The plugin and the skill are designed to coexist |
| `project-context` | 42,271 | 218 | 712 | AGENTS.md lifecycle and research phase | TRIM | 106 duplicated 5-grams against `project-layout`. Still holds the procedure that the router rule assigns elsewhere |
| `project-layout` | 9,581 | 156 | 620 | Canonical on-disk project tree | KEEP | Cleanest skill in the set. 55% of its content is non-derivable |
| `spec-kit` | 8,573 | 104 | 348 | Spec-driven development workflow | DELETE | Documents a retired tool. Every path is wrong for the tool it describes |
| `tavily-defaults` | 11,742 | 188 | 348 | Per-tool Tavily MCP parameter defaults | DELETE | The MCP server does not exist on this host. Every tool it documents is absent |
| `zsh-stack` | 27,056 | 323 | 413 | zgenom, prezto, and p10k configuration | KEEP | Highest-value skill. 70% non-derivable. Several line-number claims are stale |

## The two dead skills

### `tavily-defaults` documents tools that do not exist

`opencode mcp list` reports "No MCP servers configured". No `mcp` block exists
in `~/.config/opencode/opencode.jsonc`, in `.opencode/opencode.jsonc`, or in
`~/.config/kilo/kilo.jsonc`. `TAVILY_API_KEY` is unset.

The skill documents five tools: `tavily_search`, `tavily_extract`,
`tavily_crawl`, `tavily_map`, and `tavily_research`. None of them is
registered. The only Tavily on this host is OpenCode's built-in `websearch`
provider, which hard-codes `search_depth: "basic"`, `chunks_per_source: 3`,
and `max_results: 8` in the binary. The agent cannot pass any of the
parameters this skill teaches.

The rule `dot_agents/rules/web-verification.md:44-45` routes the agent to this
skill for "the Tavily tools". That route points at a dead end.

**Fix:** delete the skill. Rewrite the rule to name the built-in provider's
actual fixed defaults in one line.

### `spec-kit` describes a retired tool

`specify` 1.0.13 is installed, but no `.specify/` project exists on the host
and `specify init` was never run. The skill cites:

- `docs/assist-only/constitution.md` as the artifact root. Kilo was dismantled
  in commit `cb73e93`. The spec-kit OpenCode integration installs into
  `.opencode/commands/`, and its artifact root is `specs/`.
- `speckit.plan`, `speckit-analyze`, and `speckit-checklist` as slash
  commands. Those are Kilo command names.
- "spec-kit v1.0.0 (2026-08-21)" as the version anchor. PyPI has no 1.0.0
  release. The installed version is 1.0.13 and the latest is 1.2.3. Six
  releases were missed.
- Upstream issues #1671, #2114, and #1619. All three are GitHub discussions,
  not issues.

**Fix:** delete the skill. There is no project for it. If a spec-kit project
appears later, re-point it at the real layout.

## Description quality

All 11 descriptions are third person. None uses "I", "my", "we", or "our".
That part of the Anthropic convention is met everywhere.

The harder test is whether the description names a condition the model can
detect. Five of 11 fail that test.

| Skill | Score | Notes |
|---|---:|---|
| `opencode-ensemble` | 5 | "Use when coordinating multiple coding agents". Clean and conditional |
| `container-tools` | 4 | Enumerates the four tool names |
| `fnm` | 4 | Enumerates the five package-manager commands |
| `zsh-stack` | 4 | Enumerates the files |
| `spec-kit` | 4 | Clear, but the tool does not exist here |
| `project-layout` | 4 | Good, but 620 characters |
| `project-context` | 3 | Goal phrasing. The triggers live in the body, not the description |
| `github` | 3 | "Any GitHub-related action" is unbounded. No `Use when` phrase |
| `tavily-defaults` | 3 | Precise, but the tools do not exist here |
| `document-conventions` | 2 | Opens with a goal. The trigger starts at character 188 |
| `asd-ste100` | 1 | Trigger at character 350 of 828 |

Five descriptions exceed 400 characters: `asd-ste100` at 828,
`document-conventions` at 714, `project-context` at 712, `project-layout` at
620, and `zsh-stack` at 413.

This matters because Codex shortens descriptions when its catalog budget
tightens, and it front-loads the key use case for that reason. Under a
400-character cut, the only matchable terms in the `asd-ste100` description
are cut away entirely.

### The three worst, verbatim

**`asd-ste100`, 828 characters. The trigger is buried.**

> Write, rewrite, and audit technical English under ASD-STE100 Simplified Technical English. Apply the 53 writing rules of Issue 9 (Jan 2025): one meaning per word, one part of speech per word, simple tenses only, no "-ing" verbs, active voice, ≤20 words for procedures and ≤25 for descriptions, no semicolons, no phrasal verbs, ≤3-word noun clusters. Use when the user asks for Simplified Technical English, STE, ASD-STE100, controlled language, plain English, or text for readers who do not speak English as a first language, or when text will be parsed by another agent or translation pipeline and misreading has a real cost. Use to audit text and report each rule violation sentence by sentence. Use it for procedures, runbooks, README files, release notes, error messages, and safety text. Not for creative or marketing copy.

The first 350 characters enumerate rules the skill body already holds.

**`document-conventions`, 714 characters. Opens with a noun phrase.**

> Document and filename conventions for every doc type the agent authors or edits — filename rules, frontmatter policy, section order, length budget, decision matrix, templates, checklists. Use when starting a new document, choosing between doc types (plan, ADR, RFC, README, CHANGELOG, knowledge-cache entry, rule file, skill), validating a filename or frontmatter against the project convention, or reviewing an existing document and wondering what shape it should take. Does not own project-tree placement — for "where does this file live in a project", load the `project-layout` skill. For prose clarity in the body of the document (active voice, one idea per sentence, plain words), load the `asd-ste100` skill.

**`github`, 341 characters. Unbounded trigger, no "Use when" clause.**

> GitHub work via the official `gh` CLI. Load for any GitHub-related action — opening/closing/listing issues and PRs, viewing repos, releases, Actions runs, code/repo/issue/PR search, clones, gists, secrets, and arbitrary GitHub REST/GraphQL calls. Always prefer `gh` over `curl`, `git`, or webfetch for github.com / GitHub Enterprise targets.

## Progressive disclosure compliance

Every skill is under 500 lines and under 5,000 tokens. No `references/`
directory nests deeper than one level. The spec's hard limits hold everywhere.

The failures run the other way. Content that belongs in `references/` sits in
the `SKILL.md` body.

| Skill | Body lines | Body tokens | Violation |
|---|---:|---:|---|
| `asd-ste100` | 322 | 4,330 | The "Core rewrite rules" tables at lines 111-156 restate `references/writing-rules.md` |
| `document-conventions` | 256 | 2,480 | Decision matrix, filename table, and frontmatter table all re-inline their own references |
| `github` | 200 | 1,710 | 204 lines of CLI recipes with no `references/` directory at all |
| `zsh-stack` | 320 | 4,450 | The p10k tunables table and the zstyle API table are pure reference material inlined in the body |
| `project-context` | 214 | 3,740 | Lines 134-154 hold the full vendor-unification procedure that `project-layout` owns |

One skill does progressive disclosure well. `document-conventions` has a "When
to read" table at lines 79-89 that names the need-condition for each
reference file.

## Cross-skill duplication

About 14 KB of body text is duplicated. The largest overlaps, by 5-gram
shingle count:

```text
project-context/SKILL.md       <> project-layout/SKILL.md          106  (~3.7 KB)
document-conventions/SKILL.md  <> references/frontmatter.md          77  (~2.7 KB)
document-conventions/SKILL.md  <> references/by-doc-type.md          45  (~1.6 KB)
asd-ste100/SKILL.md           <> references/writing-rules.md        31  (~1.1 KB)
document-conventions/SKILL.md  <> references/anti-patterns.md        29  (~1.0 KB)
asd-ste100/SKILL.md           <> references/examples.md             25  (~0.9 KB)
```

### The duplication that matters

| Passage | Location A | Location B | Winner |
|---|---|---|---|
| The "Harness config directory" paragraph | `document-conventions/SKILL.md:48-50` | `project-context/SKILL.md:50-51` and `project-layout/SKILL.md:41-42`, byte-identical in all three | `project-layout` |
| The vendor-unification four-step procedure | `project-context/SKILL.md:149-152` | `project-layout/SKILL.md:107-110` | `project-layout`. The router rule at `dot_agents/rules/project-context.md:22` already assigns it there |
| The AGENTS.md template | `document-conventions/assets/templates/agents.md`, 64 lines | `project-context/assets/templates/agents.md`, 55 lines | `project-context`. The `document-conventions` copy points at `<vendor>/skills/project-context/SKILL.md`, a path that does not exist |
| The six-habit Scan Checklist | `asd-ste100/SKILL.md:158-178` | `document-conventions/SKILL.md:215-219` and `dot_agents/rules.personal.d/asd-ste100-trigger.md:22` | `asd-ste100` |
| The AGENTS.md length budget | `project-context/SKILL.md`, six places, plus `references/anti-patterns.md` | `document-conventions/references/structure-and-length.md:37` and `references/by-doc-type.md:103` | `project-context` owns AGENTS.md |
| The decision matrix | `dot_agents/rules/document-conventions.md:17-23`, 5 rows | `document-conventions/SKILL.md:95-110`, 14 rows | The skill. The rule should be a pointer |

Two of these are already divergent, not merely duplicated. The
`document-conventions` SKILL.md says ADR frontmatter is "Optional but
recommended" while `references/frontmatter.md:15` says "Optional". The
SKILL.md decision matrix lacks the "Design doc" row that its own reference
has.

### Router rules against the skills they point at

Four rules route to skills. Two carry byte-identical trigger lines that also
appear in the skill body:

- `dot_agents/rules/runtime-tools.md.tmpl:13` and
  `container-tools/SKILL.md:14` share the container-tool trigger line exactly.
- `dot_agents/rules.personal.d/zsh-stack.md:9-10` and
  `zsh-stack/SKILL.md:14-15` share two trigger lines exactly.

The rule copy is the one that matters, because the rule is always in context
and the skill is not.

## Stale facts inside the skills

The `zsh-stack` skill is the highest-value skill and it cites line numbers in
the zsh config. Several are wrong.

| Claim | Actual |
|---|---|
| `dot_zshrc:80` sources `~/.p10k.zsh` | Line 82 does. Line 80 is blank |
| The zshrc body runs to line 73 | It runs to line 74 |
| `00-before-zgenom.zsh:11` prepends the completion path | Line 7 does. Line 11 is inside a comment |
| The prezto module list is at `dot_zshrc:49-60` and holds 12 modules | Lines 49-61 hold 13 modules. The range excludes `zgenom prezto prompt`, the module the skill's own diagram ends on |
| The cross-reference table lists the sourced zsh files | It omits `20-ejson-environment-load.zsh`, which `dot_zshrc:79` sources |
| "Authoritative evidence" points at a research archive under `~/Playground/backup/` | That repo was dismantled. The path does not exist on a fresh machine |

The `github` skill documents three commands that fail on the installed
`gh` 2.102.1:

| Documented | Result | Correct form |
|---|---|---|
| `gh repo read-file owner/repo path` | "accepts 1 arg(s), received 2" | `gh repo read-file <path> --repo owner/repo` |
| `gh browse -n main path` | "accepts at most 1 arg(s), received 2" | `gh browse path -b main -n` |
| `gh issue develop 123 --branch fix/123` | "unknown flag: --branch" | `gh issue develop 123 --name fix/123` |

A model that copies these verbatim fails on first use. That costs the user
trust in the whole skill.

## Over-specification

| Skill | Non-derivable | Model would do anyway | Edge cases |
|---|---:|---:|---:|
| `zsh-stack` | 70% | 20% | 10% |
| `tavily-defaults` | 60% | 25% | 15% |
| `project-layout` | 55% | 25% | 20% |
| `opencode-ensemble` | 50% | 30% | 20% |
| `spec-kit` | 50% | 30% | 20% |
| `github` | 45% | 45% | 10% |
| `fnm` | 45% | 40% | 15% |
| `asd-ste100` | 40% | 30% | 30% |
| `document-conventions` | 35% | 35% | 30% |
| `project-context` | 30% | 45% | 25% |
| `container-tools` | 20% | 55% | 25% |

`zsh-stack` has the best ratio in the set. `container-tools` has the worst:
55% of its content is shim detection the model can run in one command, for a
question the host has already answered.

## Catalog cost

### Always paid

OpenCode injects every skill's name and description into the `skill` tool
description on every request. It does this whether or not any skill fires.

| Skill | Desc bytes | Desc tokens | Body tokens on activation |
|---|---:|---:|---:|
| `asd-ste100` | 834 | 207 | 4,727 |
| `document-conventions` | 718 | 179 | 3,502 |
| `project-context` | 714 | 178 | 4,895 |
| `project-layout` | 620 | 155 | 2,230 |
| `zsh-stack` | 415 | 103 | 6,651 |
| `spec-kit` | 362 | 87 | 2,044 |
| `tavily-defaults` | 350 | 87 | 2,837 |
| `github` | 343 | 85 | 2,096 |
| `container-tools` | 276 | 69 | 1,266 |
| `opencode-ensemble` | 234 | 59 | 1,433 |
| `fnm` | 129 | 32 | 455 |
| **Total** | **4,995** | **1,241** | **32,134** |

About 1,240 tokens per request for eleven description strings, plus roughly 250
tokens of `<available_skills>` XML scaffolding.

### Ranked by always-paid cost against value

| Rank | Skill | Always paid | Value | Action |
|---|---|---:|---|---|
| 1 | `asd-ste100` | 207 | High, and it has a working checker | Cut the description to about 120 characters. Save 90 tokens per request |
| 2 | `document-conventions` | 179 | Medium | Cut to about 130. Save 50 |
| 3 | `project-context` | 178 | Medium | Cut to about 120. Save 60 |
| 4 | `project-layout` | 155 | High | Trim to about 110. Save 45 |
| 5 | `zsh-stack` | 103 | Highest | Keep the description |
| 6 | `tavily-defaults` | 87 | Zero on this host | Delete. Save 87 |
| 7 | `spec-kit` | 87 | Low | Delete. Save 87 |
| 8 | `github` | 85 | High | Keep the description. Fix the body |
| 9 | `container-tools` | 69 | Low | Merge into the rule. Save 69 |
| 10 | `opencode-ensemble` | 59 | High | Keep |
| 11 | `fnm` | 32 | Low | Merge into the rule. Save 32 |

Deleting the two dead skills and merging the two small ones removes about 188
tokens per request. That is a 15% cut of the catalog cost, and it removes four
skill bodies from disk.

## Skills that should be rules

Two skills are too small to justify a catalog entry.

**`fnm`, 58 lines.** The shell already switches versions:
`dot_shell/zsh/10-common-export.zsh:22` runs
`eval "$(fnm env --use-on-cd --shell zsh)"`. The body is a command cheat sheet
that `fnm install --help` covers. The skill description fires on any
`node`/`npm`/`npx` call, which is broader than the rule's trigger of "a
project with a `.node-version`, `.nvmrc`, or `package.json#engines.node`".
The rule has the better trigger. **Move the version-resolution note into
`runtime-tools.md.tmpl` and delete the skill.**

**`container-tools`, 120 lines.** The host has already answered the
runtime question: `docker` is a podman shim, and the skill's own decision
table says to use podman natively. The live value is the compose and image
convention cheat sheet, which is reference material. **Merge it into
`runtime-tools.md.tmpl` or into a `references/` file.**

## Rules that should be skills

Three rules in `dot_agents/rules.personal.d/` are rare-branch procedures that
are paid for in every session.

| Rule | Bytes | Why |
|---|---:|---|
| `ssh-agent-keys-location.md` | 3,992 | A multi-step procedure with side effects: `mkdir`, `ssh-keygen`, `chmod`, `ssh-add`, `gpg-connect-agent keyattr`. Needed a few times a year, paid every session |
| `zsh-emulate-fallback.md` | 3,967 | A decision procedure with a lookup table, needed only when a zsh-specific error appears |
| `ssh-stdbuf-disable-buffering.md` | 2,200 | A procedure with a decision table, needed only over ssh |

Together they cost about 2,100 tokens per request for three rare branches.
This is the same finding as D-4 and D-5 in the rules audit, seen from the
other side.

## What the literature says about this catalog

### The strongest finding

OctoBench (arXiv 2601.10343) measures instruction adherence per injection
channel, on the Claude Code scaffold, with the same model across channels:

| Channel | MiniMax-M2.1 ISR | CSR |
|---|---:|---:|
| Memory | 98.15 | 99.38 |
| Claude.md | 82.98 | 96.37 |
| Tool schema | 71.47 | 94.88 |
| User query | 67.84 | 86.62 |
| System reminder | 87.76 | 95.68 |
| **Skill.md** | **12.33** | **21.73** |

For the same model on the same scaffold, an always-loaded rule file scores
82.98 and a skill scores 12.33. The skill body is harder to comply with than
the always-loaded rule, and the gap is not only about activation. A skill
scored 21.73 on constraint satisfaction means the model often loaded the
skill and then failed the workflow inside it.

The practical reading: this catalog is being asked to carry rules that the
evidence says a skill body carries badly. That argues for moving invariants
into `AGENTS.md` and for keeping skills narrow.

### Interference is real and catalog-wide

A measured run over roughly 20 skills with about 1,000 labelled prompts found
that one extra sentence per description moved micro-recall from 46.3% to
67.3%. The number of skills clearing 70% recall rose from 4 to 11. Editing
one description re-routes prompts that belong to skills nobody touched.

A "router" skill that claimed the capabilities of four specialists fired on
its own two prompts and on three belonging to specialists. Its precision was
0.40. Broad descriptions absorb specialists.

That is the failure mode for this catalog. `project-context` and
`project-layout` describe overlapping ground. `document-conventions` covers
`AGENTS.md`, which `project-context` also owns.

### Structural exclusion is available in OpenCode

Every harness except Cursor has a deterministic way to take the routing
decision away from the model. In OpenCode it is `permission.skill`:

- `{"action": "skill", "resource": "<name>", "effect": "deny"}` hides one
  skill from the agent.
- `{"tools": {"skill": false}}` removes the whole `<available_skills>` block.

For a model whose measured weakness is confidently wrong routing, this is a
first-class lever. It also gives a clean way to park the two dead skills
before deleting them, and to gate `spec-kit` until a project exists.

### What is not known

The literature has no measurement of skill-catalog size against selection
accuracy for any model. OctoBench holds the catalog size constant.
SRA-Bench measures a 26,262-skill corpus but with retrieval rather than
in-context enumeration. The tool-count literature uses tool schemas with full
JSON Schema, not bare descriptions.

Nothing is published about skill selection for MiniMax M3 or M3.1 Flash. There
is also no published IFBench, BFCL, or multi-turn retention score for
M3.1 Flash. The "picked correctly from 91 tools" claim could not be traced to
a primary source.

The closest relevant measurement is that skill-loading behaviour shows no
monotonic trend with model size in SRA-Bench. "Small models are worse at skill
routing" is not supported by the direct evidence.

## Defect list

Ranked by impact on the daily model.

| # | Skill and line | Defect | Fix |
|---|---|---|---|
| 1 | `tavily-defaults` (whole file) | Documents five MCP tools that do not exist here. The `web-verification` rule routes to it | Delete the skill. Name the built-in provider's fixed defaults in the rule |
| 2 | `spec-kit` lines 3, 26-34, 82-90 | Every path and command is Kilo-legacy. The version anchor does not exist. Three upstream "issues" are discussions | Delete the skill. Re-point it when a project exists |
| 3 | `github` lines 183, 184, 190, 69 | Three documented commands fail on the installed `gh` | Rewrite the four command forms |
| 4 | `asd-ste100` line 3 | 828-character description. The trigger is at character 350 | Cut to about 340 characters with the trigger first |
| 5 | `document-conventions` lines 91-114, 155-195 | Three tables re-inline their own references, and two have already diverged from them | Delete the tables. Point at the references |
| 6 | `project-context` lines 134-154 | Holds the vendor-unification procedure that `project-layout` owns and that the router rule assigns there | Replace with a pointer |
| 7 | `document-conventions/assets/templates/agents.md` | A second AGENTS.md template pointing at a path that does not exist | Delete it. Point the by-doc-type reference at the `project-context` copy |
| 8 | `zsh-stack` lines 34, 61, 96, 108, 153, 208, 248, 257, 258, 275, 280, 311 | Six stale line-number claims. A cross-reference table omits a sourced file. The "authoritative evidence" path is in a dismantled repo | Fix the line numbers. Add the missing file. Replace the archive path with in-repo evidence |
| 9 | `asd-ste100` lines 122-156 | The structural-rules table restates `references/writing-rules.md` and drops ten rules in the process | Keep the structural-versus-lexical distinction. Delete the table |
| 10 | `zsh-stack` lines 134-149, 212-231 | 34 lines of reference tables inlined in the largest body in the set, with no `references/` directory | Create `references/prezto-zstyle-api.md` and `references/p10k-tunables.md` |
| 11 | `document-conventions`, `project-context`, `project-layout` | The "Harness config directory" paragraph is byte-identical in all three | Keep it once, in `project-layout` |
| 12 | `github` line 3 | "Any GitHub-related action" is unbounded. No "Use when" clause | Rewrite with the trigger first |
| 13 | `fnm` (whole file) | 58 lines for a shell that auto-switches versions. Its trigger is broader than the rule's | Merge into `runtime-tools.md.tmpl`. Delete the skill |
| 14 | `container-tools` (whole file) | 120 lines for a question the host has answered. 55% of the body is shim detection | Merge the cheat sheet into the rule. Delete the skill |
| 15 | `document-conventions/references/frontmatter.md:56` | Quotes a stale copy of the skill's own description | Re-paste the current text or drop the example |
| 16 | `project-context/SKILL.md:75-77` | A literal `$ARGUMENTS` placeholder, a Kilo slash-command residue | Delete the block |
| 17 | `document-conventions/SKILL.md:105` | A malformed table row renders as literal `**README.md` | Close the bold markers |
| 18 | `asd-ste100/SKILL.md:211-212` | `python3 scripts/ste_check.py` is a relative path. A model running it from the project cwd gets "No such file or directory" | Use the absolute path, or say to run from the skill base directory |
| 19 | `opencode-ensemble` (whole directory) | Untracked in git. The only skill of the 11 that is not committed | Add and commit it |
| 20 | `opencode-ensemble/README.md` | Excluded by the `.chezmoiignore` `**/README.md` pattern, so it deploys but chezmoi will never update or remove it | Add a negation for the skills path, or delete the file |

## Proposed changes

| Change | Effect |
|---|---|
| Delete `tavily-defaults` and `spec-kit` | −174 tokens per request. −4,881 tokens of activation cost |
| Merge `fnm` and `container-tools` into `runtime-tools.md.tmpl` | −101 tokens per request. −1,721 tokens of activation cost |
| Rewrite the `asd-ste100`, `document-conventions`, `project-context`, and `project-layout` descriptions with the trigger first | −195 tokens per request |
| Fix the four broken `gh` commands | The skill stops failing on first use |
| Fix the six stale `zsh-stack` line references | The skill's own anchors work again |
| Move three rule procedures into skills | −2,100 tokens per request. They become load-on-demand |
| Delete the three re-inlined tables from `document-conventions` | −1,100 bytes of body. Removes two drifted duplicates |
| Add `permission.skill` denies for the two dead skills before deleting them | A reversible first step |

Net effect on the catalog: 11 skills to 9. About 470 tokens per request saved,
a 38% cut of the catalog cost. About 14 KB of duplicated body text removed.
Four skills either deleted or merged.

## Risks

- **Risk:** a deleted skill was the right choice for a task the reviewer did
  not consider. **Mitigation:** `permission.skill` with `deny` hides a skill
  without deleting it. Gate the two deletions behind one session first.
- **Risk:** trimming a description past its trigger words makes it
  undiscoverable. **Mitigation:** keep the trigger keywords in the first 200
  characters. Test with the labelled-query method from the agentskills.io
  description guide.
- **Risk:** merging `fnm` and `container-tools` into the rule file pushes the
  rule back over the 150-line ceiling. **Mitigation:** the ceiling is not at
  risk. Every rule file is inside it, and the budget counts lines, not
  words.
- **Risk:** the description edits re-route prompts to other skills, which is
  the measured interference effect. **Mitigation:** edit one description at a
  time and re-run the trigger eval after each.
