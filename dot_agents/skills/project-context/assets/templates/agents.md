<!-- Template only — copy verbatim into the project root as `AGENTS.md`. Target ~40–80 lines. Allow up to 150 when keeping guidance co-located helps the project. Past 150, split per-package (see SKILL.md → Monorepos). -->

# AGENTS.md

## Purpose
<one sentence: what the project is>

## Stack
- Language / runtime: <for example, TypeScript 5.7, Node 22>
- Framework: <for example, Next.js 15 App Router>
- Package manager: <for example, pnpm only — never npm/yarn>
- Lockfile: <for example, pnpm-lock.yaml>

## Commands
- Install: `pnpm install`
- Dev: `pnpm dev`
- Build: `pnpm build`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Test all: `pnpm test`
- Test one file: `pnpm vitest run path/to/file.test.ts`
- Test by name: `pnpm vitest run -t "name pattern"`

## Code style
[one real code snippet from this codebase that exemplifies the dominant style — beats three paragraphs describing it]
- <for example, named exports only, no defaults>
- <for example, files under 300 lines>

## Testing rules
- <for example, unit tests for every new function>
- <for example, mock external services at the boundary>

## Boundaries
### ✅ Always
- <for example, run lint + typecheck before commit>
- <for example, list only human authors in git commits>
- **Recreate vendor symlinks if missing on a fresh clone**, for example, `ln -s .agents/<vendor> .<vendor>` — vendor tool directories at the root are symlinks into `.agents/`. If `ls <vendor>/` fails, fix the link before reading vendor config.

### ⚠️ Ask first
- <for example, database schema changes>
- <for example, new top-level dependencies>
- <for example, deleting files>

### 🚫 Never
- <for example, commit secrets, `.env`, credentials>
- <for example, force-push to main>
- <for example, modify `vendor/`, `dist/`, `build/`>

## Pointers
- **`README.md`** — required. The project's human-facing narrative (problem, audience, getting started). `AGENTS.md` complements but never duplicates the README.
- Deeper docs: `docs/README.md` index, or `<relative/path/to/ARCHITECTURE.md>`
- Conventions: `<relative/path/to/CONTRIBUTING.md>`
- Knowledge cache: see the project's cache index (placement convention in the `project-layout` skill, date-tagged web-learned facts). See the `web-verification` rule and `references/knowledge-cache.md`
- Vendor config: `.agents/<vendor>/` (for example, `.agents/<vendor>/`) — `<vendor-name>/` at the root is a symlink to it (mechanics in the `project-layout` skill)
- `.gitignore` workflow: see the project's gitignore reference (template, Toptal API, OS/IDE/framework catalog).