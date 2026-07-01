# Project Context Setup

When starting work in a project, assess its current agent context and documentation state. Do not modify files automatically — always suggest to the user first.

#### Loading model

AGENTS.md, `.kilo/rules/`, and registered `instructions` files are **all loaded at session start** — treat them as a shared token budget. Keep each file small; collectively they should stay under ~60 lines for typical projects. Move detailed subsystem knowledge to `.kilo/skills/` instead — skills are truly on-demand: the agent reads the full `SKILL.md` only when a task matches its description.

## Phase 1: AGENTS.md / CLAUDE.md Detection

Check for `AGENTS.md`, `CLAUDE.md`, or `CONTEXT.md` at the workspace root.

### Scenario A: Neither exists (clean project)

Suggest creating an `AGENTS.md`. It should be agent-agnostic — describe the project, not Kilo or any specific tool. Cover the six core areas that research shows matter most:

```markdown
# <project>

- **Purpose**: <1 sentence>
- **Stack**: <language, framework, key deps, versions>
- **Commands**: test/lint/build (exact flags)
- **Code style**: only rules deviating from language defaults
- **Project structure**: key directories and what they contain
- **Testing**: framework, how to run, conventions
- **Git workflow**: branch naming, commit style, PR process
- **Boundaries**: files/folders never to modify
- **Pointers**: link to detailed docs, `.kilo/rules/`, `.kilo/skills/`, knowledge cache directory (e.g., `.kilo/cache/`)
```

Target 40-60 lines total. The headings above should each be 1-4 lines — concise bullets, not paragraphs. Move deeper detail (security models, API specs, complex CI workflows) to pointer-referenced docs or on-demand `.kilo/skills/`.

AGENTS.md is agent-agnostic — it describes the project, not a particular coding agent. Keep Kilo-specific instructions in `.kilo/rules/` and `.kilo/skills/`. Only add sections the agent consistently gets wrong — human-written AGENTS.md improves task success by ~4%, while LLM-generated fluff hurts performance.

### Knowledge Cache

Projects benefit from a **knowledge cache** — a directory where the agent stores facts it learned from the web that future sessions may need again (tool version quirks, API changes, deprecation notices). This avoids repeated web searches and reduces latency/cost.

The AGENTS.md **Pointers** section should reference this directory. Common names: `.kilo/cache/`, `.help/`, or `docs/cache/`. File per topic, date-tagged entries. The agent discovers the location by reading AGENTS.md's Pointers — do not hardcode a path in tool rules.

If the project has no cache directory yet, suggest creating one during Phase 1 setup. The `web-tools-priority.md` rule instructs the agent to use this directory after fetching fresh information from the web.

### Scenario B: CLAUDE.md exists, no AGENTS.md

`CLAUDE.md` is Kilo-supported but `AGENTS.md` follows the [open AGENTS.md standard](https://agents.md) and works across more tools (Codex, Cursor, Windsurf, etc.). Suggest:

1. **Create AGENTS.md** derived from `CLAUDE.md` — extract conventions, commands, and structure. Keep it 40-60 lines. For repos with very detailed `CLAUDE.md`, the file can simply contain `@AGENTS.md` to delegate.
2. **Create `.kilo/rules/` files** — extract Kilo-specific conventions (naming, patterns, restricted files) from `CLAUDE.md`, `CONTRIBUTING.md`, or any `docs/` directory. Keep `AGENTS.md` agent-agnostic.
3. **Create `.kilo/skills/`** — if the project has complex subsystems (e.g., custom build system, DSL, encryption flow), create a `SKILL.md` following the [Agent Skills spec](https://agentskills.io/specification).
4. **If this is an external repo** (not user-controlled), hide `.kilo/` and `AGENTS.md` from version control:
   - If `.gitignore` is already gitignored (repo ships one): add entries to `.git/info/exclude`
   - If the repo has no `.gitignore` or a user-editable one: add to `.gitignore`
   - Entries: `.kilo/`, `AGENTS.md`

### Scenario C: AGENTS.md exists

No action needed. If it appears stale or incomplete, offer to update it.

## Phase 2: Project Documentation

After Phase 1 (or if AGENTS.md already exists), assess if the project has existing docs the agent should know about.

### Scenario D: Check for existing documentation

Search for `CONTRIBUTING.md`, `ARCHITECTURE.md`, `docs/`, `SECURITY.md`, `README.md`, or any `*.md` files in a `contributing-docs/` or `docs/` directory. These already describe the project — don't duplicate them.

Suggest adding **pointer references** to AGENTS.md:

```markdown
## References

- [`contributing-docs/05_pull_requests.rst`](contributing-docs/05_pull_requests.rst)
- [`airflow-core/docs/security/security_model.rst`](airflow-core/docs/security/security_model.rst)
```

This is how real projects handle it — they keep AGENTS.md focused on the six core areas (commands, testing, project structure, code style, git workflow, boundaries) and point to existing docs for deep reference. The goal is to keep AGENTS.md small enough that it costs minimal tokens every session, while the agent loads reference docs only when the task actually needs them.

### Scenario E: No docs exist, but conventions are complex

If the project has complex, non-obvious conventions that would clutter AGENTS.md (e.g., API protocol specs, security models, deployment playbooks), suggest creating **targeted doc files** — only what the project genuinely needs. Don't prescribe a fixed directory structure. Common patterns:

- `docs/SECURITY.md` — threat model, auth flows, hard boundaries
- `docs/ARCHITECTURE.md` — system design, component relationships, data flow
- `docs/QUIRKS.md` — undocumented edge cases, gotchas, non-obvious behaviors

Add pointer references from AGENTS.md to each. Keep doc files narrowly scoped (one topic per file) — the agent loads them on demand via the pointer, never pre-loaded into every session.

## Phase 3: Rules and Skills Integration

After creating docs or AGENTS.md — keep Kilo-specific content in `.kilo/`, not in `AGENTS.md`:

1. **Add a pointer rule** — create `.kilo/rules/project-docs.md`:
   ```markdown
   # Project Documentation

   Deep documentation lives outside AGENTS.md to avoid per-session token cost.
   Load specific files on demand when the task requires them:
   - `docs/ARCHITECTURE.md` — system design and component relationships
   - `docs/SECURITY.md` — threat model and auth flows
   ```
   Keep each doc file narrowly scoped so the agent loads only what the task needs.
2. **Register rules** — ensure `kilo.jsonc` has `"instructions": [".kilo/rules/*.md"]`
3. **Identify skill candidates** — if the project has reusable domain patterns (e.g., custom build pipeline, proprietary protocol, specialized testing setup), suggest creating a `.kilo/skills/<name>/SKILL.md`

## When to Suggest

Prioritize this workflow when:
- Starting work in a project for the first time (no context files exist)
- The agent needs to explore the project structure on the first turn — discovery work that context files would eliminate
- The project has conventions that aren't obvious from the directory structure
- You spend more than 2 turns explaining project-specific patterns

Keep suggestions brief. Example: "This project has a `CLAUDE.md` but no `AGENTS.md`. I can create an optimized AGENTS.md and extract conventions into `.kilo/rules/`. These files would be hidden via `.gitignore`. Want me to set this up?"
