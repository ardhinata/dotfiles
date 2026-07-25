<!-- Template only — copy verbatim into the project root as `AGENTS.md`. Keep ≤60 lines; ≤150 in monorepos. -->

# AGENTS.md

## Purpose
<one sentence: what the project is>

## Stack
- Language / runtime: <e.g. TypeScript 5.7, Node 22>
- Framework: <e.g. Next.js 15 App Router>
- Package manager: <e.g. pnpm only — never npm/yarn>
- Lockfile: <e.g. pnpm-lock.yaml>

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
- <e.g. named exports only, no defaults>
- <e.g. files under 300 lines>

## Testing rules
- <e.g. unit tests for every new function>
- <e.g. mock external services at the boundary>

## Boundaries
### ✅ Always
- <e.g. run lint + typecheck before commit>
- <e.g. list only human authors in git commits>
- **Recreate vendor symlinks if missing on a fresh clone**, e.g. `ln -s .agents/kilo .kilo` — vendor tool directories at the root are symlinks into `.agents/`. If `ls <vendor>/` fails, fix the link before reading vendor config.

### ⚠️ Ask first
- <e.g. database schema changes>
- <e.g. new top-level dependencies>
- <e.g. deleting files>

### 🚫 Never
- <e.g. commit secrets, `.env`, credentials>
- <e.g. force-push to main>
- <e.g. modify `vendor/`, `dist/`, `build/`>

## Pointers
- **`README.md`** — required. The project's human-facing narrative (problem, audience, getting started). `AGENTS.md` complements but never duplicates the README.
- Deeper docs: `docs/README.md` index, or `<relative/path/to/ARCHITECTURE.md>`
- Conventions: `<relative/path/to/CONTRIBUTING.md>`
- Knowledge cache: `.agents/docs/cache/README.md` index — date-tagged web-learned facts (see `web-tools-priority` rule and `references/knowledge-cache.md`)
- Vendor config: `.agents/<vendor>/` (e.g. `.agents/kilo/`) — `<vendor-name>/` at the root is a symlink to it
- `.gitignore` workflow: see the project's gitignore reference (template, Toptal API, OS/IDE/framework catalog).