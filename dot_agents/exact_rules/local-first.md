# Local First, Don't Assume

When the user asks something, read the project's readily-available docs
**before assuming or searching the web**. Apply this on the **first turn** of
any project-scoped question — before web tools and before clarifying
questions.

This rule owns the **priority order of local sources**.

## Priority

In roughly this order, read what exists and skip what does not:

1. **`README.md`** — setup, intent, structure, conventions in one pass.
2. **Agent-instruction file** — `AGENTS.md`. Ignore vendor-specific files
   such as `CLAUDE.md` or `.cursorrules`. They may import `AGENTS.md`, but
   they must not be a second source of truth.
3. **Executable manifests** — `package.json` (`scripts` block), `Cargo.toml`,
   `go.mod`, `pyproject.toml`, `composer.json`. The `scripts` block is
   executable truth and cannot drift like prose.
4. **Task runners** — `Makefile`, `Taskfile.yml`, `justfile`.
5. **`CONTRIBUTING.md`** — workflow, branch and PR rules, style, test
   requirements.
6. **`CHANGELOG.md` / `RELEASES.md`** — recent behavior, deprecations,
   breaking changes.
7. **`.env.example` / `.env.template`** — required env vars, no secrets.
8. **`docs/` index** — skim filenames and titles only.
9. **Code itself** — when the above do not cover it.

## A dependency is a local source

When the question is about an installed package, plugin, or CLI, its own docs
come before its source. Read the package README, the `--help` text, or the
config schema. The same order applies to the harness: search the tool catalog
before you read harness source.

To answer from a specific revision, `git show <tag>:<path>` is the correct
read. It is a shell fact, not a source search.

## When local is not enough

Local-first orders the local sources. It does not forbid an external lookup.
Go to the web when:

- the local copy is a snapshot of an older version
- the question is about a release newer than the local copy
- the local sources do not answer it

The `web-verification.md` rule owns that lookup policy and its staleness table.

## Anti-Patterns

- Assuming project structure from filenames alone.
- Jumping to web search for a question the project's own docs resolve.
- Asking the user something stated in `README.md` or `AGENTS.md`.
- Trusting a README's "how to build" over the actual `package.json` scripts.
