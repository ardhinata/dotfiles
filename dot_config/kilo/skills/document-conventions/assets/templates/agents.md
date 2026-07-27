# AGENTS.md Template

Copy to `AGENTS.md` at repo root (and nested per monorepo package).
**Plain Markdown only — no frontmatter** per the
[agents.md spec](https://agents.md/).

```markdown
# <Project name>

## Purpose
<One sentence: what the project is.>

## Stack
- Language: <…>
- Runtime: <…>
- Package manager: <…>
- Lockfile: <…>

## Commands
- <Install>: `<exact command>`
- <Build>: `<exact command>`
- <Test>: `<exact command with flags>`
- <Lint>: `<exact command>`
- <Typecheck>: `<exact command>`
- <Single test>: `<exact command with pattern flag>`

## Code style
<One real code snippet beats three paragraphs of style description.>

## Testing rules
<How to run tests, when to run them, any quirks — fixtures,
integration prerequisites, flaky suites.>

## Boundaries

### ✅ Always
- <thing the agent must do on every task>

### ⚠️ Ask first
- <thing the agent must surface before doing>

### 🚫 Never
- <thing the agent must never do>

## Pointers
- [README.md](README.md) — required pointer
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution norms
- [docs/](docs/README.md) — project documentation
- [.agents/kilo/](.agents/kilo/README.md) — agent rules + skills
- [.agents/docs/cache/](.agents/docs/cache/README.md) — knowledge cache
```

**Length:** 40–80 lines target; 150 hard ceiling.

**Hard rules:**

- Every line must answer "would an agent get this wrong without this
  instruction?". Cut otherwise.
- No architecture overview or file tree.
- Use exact command flags (`pnpm vitest run -t "name"`, not `pnpm test`).
- One real code snippet for style beats three paragraphs.
- `Pointers` must include `README.md`.

**Verification:** manual review against [`../checklists.md`](../checklists.md)
and any project-context skill installed at `kilo/skills/project-context/SKILL.md`.