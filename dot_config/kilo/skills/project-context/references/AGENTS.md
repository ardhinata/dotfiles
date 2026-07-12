<!-- Template only — copy verbatim into the project root as `AGENTS.md`.
This file is *not* a project AGENTS.md and is not auto-loaded by Kilo. -->

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
- Deeper docs: `<relative/path/to/ARCHITECTURE.md>`
- Conventions: `<relative/path/to/CONTRIBUTING.md>`
- Knowledge cache: `.tmp/doc-cache/` (see `web-tools-priority` rule)
