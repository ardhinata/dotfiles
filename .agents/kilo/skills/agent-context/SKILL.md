---
name: agent-context
description: Create and improve AGENTS.md (per agents.md open standard) and SKILL.md (per agentskills.io spec). Load when asked to create, review, or improve agent instruction files, project documentation for agents, or .kilo/skills/ SKILL.md files.
---

# Agent Context Skill

Load when creating, reviewing, or improving `AGENTS.md` or `SKILL.md` files. Covers the [agents.md](https://agents.md) open standard (AGENTS.md) and the [agentskills.io](https://agentskills.io/specification) spec + best practices (SKILL.md).

## When to Load

- User asks to create/update/review `AGENTS.md`
- User asks to create/update/review a skill's `SKILL.md`
- Setting up agent documentation for a new project
- Reviewing existing agent-context files for staleness or spec compliance

## AGENTS.md — the Open Standard

`AGENTS.md` is a README for agents — a dedicated place for build steps, tests, and conventions that complement (never duplicate) `README.md`. It is plain Markdown; no frontmatter required.

### Structure

Use the Kilo template at `~/.config/kilo/skills/project-context/references/AGENTS.md` as starting material. Fill every section from verified project facts, never imagination:

| Section | Purpose |
|---|---|
| **Purpose** | One sentence: what the project is |
| **Stack** | Language, runtime, framework, package manager, lockfile |
| **Commands** | Exact commands with flags (`pnpm vitest run -t "pattern"`, not `pnpm test`) |
| **Code style** | One real code snippet beats three paragraphs; note conventions that differ from defaults |
| **Testing rules** | How to run tests, when to run them, any quirks |
| **Boundaries** | 3-tier: ✅ Always / ⚠️ Ask first / 🚫 Never |
| **Pointers** | `README.md` (required), deeper docs, conventions, knowledge cache |

### Key rules

- **40–60 lines max.** Deeper subsystem docs belong in `.kilo/skills/`.
- **Every line must pass the question:** "Would an agent get this wrong without this instruction?" If no, cut it.
- **Executable truth over prose.** Trust `package.json` scripts over README paragraphs.
- **No architecture overviews or file trees.** Agents navigate the tree themselves.
- **Monorepos**: nested `AGENTS.md` in each package. Agent reads the closest file to the file being edited.
- **README.md pointer is mandatory.** AGENTS.md complements, never duplicates, the README.

## SKILL.md — the agentskills.io Spec

A skill is a directory with a `SKILL.md` file containing **YAML frontmatter** followed by Markdown instructions.

### Directory structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: on-demand docs
└── assets/           # Optional: templates, resources
```

### YAML frontmatter (required fields)

```yaml
---
name: skill-name          # 1-64 chars, lowercase/hyphens only, matches directory name
description: What and when # 1-1024 chars, include keywords agents use to decide activation
---
```

Optional: `license`, `compatibility` (max 500 chars, only if env requirements exist), `metadata` (arbitrary k/v), `allowed-tools` (experimental).

### Progressive disclosure

Skills load in layers — structure to exploit this:

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup
2. **Instructions** (< 5000 tokens): `SKILL.md` body loaded on activation
3. **Resources** (as needed): files in `scripts/`, `references/`, `assets/` loaded on demand

**Keep SKILL.md under 500 lines.** Move reference material to separate files and tell the agent *when* to load each: "Read `references/api-errors.md` if the API returns a non-200" beats "see references/ for details."

## Best Practices for Skill Creation

### Start from real expertise

Don't ask an LLM to generate a skill from its training knowledge — feed domain-specific context. Extract from:

- **Completed tasks**: Steps that worked, corrections you made, context you provided
- **Existing artifacts**: Internal docs, API specs, code review comments, patch history, real failure cases

### Spending context wisely

Every token competes for attention. **Add what the agent lacks, omit what it knows.** You don't need to explain what a PDF is or how HTTP works. Skip generic advice ("handle errors appropriately"). Include concrete corrections to mistakes the agent will make.

### Match specificity to fragility

- **Give freedom** when multiple approaches work (explain *why*, not just *what*)
- **Be prescriptive** when operations are fragile or sequence matters (exact commands, exact flags)
- **Provide defaults, not menus.** Pick one tool and mention alternatives as fallbacks, not equal options.

### Favor procedures over declarations

Teach *how to approach* a problem class, not *what to produce* for one instance. A reusable method beats a specific answer.

### Effective patterns

| Pattern | When to use |
|---|---|
| **Gotchas section** | Non-obvious facts that defy reasonable assumptions (naming mismatches, soft-deletes, misleading health endpoints) |
| **Output templates** | When output must follow a specific format (more reliable than prose descriptions) |
| **Checklists** | Multi-step workflows with dependencies or validation gates |
| **Validation loops** | Agent validates its own work before proceeding (run validator → fix → repeat) |
| **Plan-validate-execute** | Batch/destructive operations — create plan, validate against source of truth, then execute |
| **Bundled scripts** | When agents repeatedly reinvent the same logic across runs |

### Iteration: refine with real execution

Run the skill against real tasks, read agent execution traces (not just final outputs), feed results back. Add corrections to the gotchas section. A single pass of execute-then-revise noticeably improves quality.

## Workflow for Creating/Updating Agent Context

1. **Investigate first**: Read `README.md`, root manifests, build config, CI, existing instruction files. Prefer executable truth over prose.
2. **Draft from template**: Use `~/.config/kilo/skills/project-context/references/AGENTS.md` for AGENTS.md; follow the spec above for SKILL.md.
3. **Verify every claim**: Never copy a claim you couldn't verify against the repo.
4. **Keep it tight**: Every line must answer "Would an agent get this wrong without it?" When in doubt, omit.
5. **Human review required**: LLM-generated context files reduce task success (Gloaguen et al., arXiv:2602.11988). Flag this when suggesting.

## Validation

For SKILL.md files, validate with the reference library:

```bash
skills-ref validate ./my-skill
```

Checks frontmatter validity and naming conventions per the agentskills.io spec.
