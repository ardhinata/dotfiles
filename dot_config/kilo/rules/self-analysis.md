# Self-Analysis (3-Why)

When you're uncertain about understanding or a decision, interrogate it with up to 3 "why" questions before acting. Each surface-level answer masks a deeper cause — stop at 3 or when you reach an actionable root.

## Process

1. **State your current understanding** of the problem or decision.
2. **Ask "why?"** — why is this the right path? Why do I believe this?
3. **Repeat up to 2 more times**, each time asking why the previous answer is true.
4. **Identify gaps** — where does your answer rely on assumption rather than fact?
5. **Resolve gaps immediately** before proceeding.

## When a Gap Surfaces, Fetch

| Source | How |
|---|---|
| **Documentation** | `semantic_search` to find relevant docs, then `read` any `.md`, `.txt`, `.rst`, or similar text file that may hold the answer |
| **Project state** | `git log --oneline`, opened files (`git diff`, `git status`), user's prior behavior and context |
| **The web** | Use `webfetch` / `firecrawl_scrape` / `tavily_search` sparingly — only when the answer cannot be found locally |

## Examples

**Without 3-Why (surface fix):**
> Bug: build fails with missing import.
> → "I'll add the import." *(gap: why was it missing?)*

**With 3-Why:**
> Why 1: Why is the import missing? — File was moved.
> Why 2: Why was the file moved? — Refactor 3 commits ago.
> Why 3: Why didn't references update? — No tooling caught it.
> → Fix: add import **and** add an import-check lint rule.

**Uncertain architecture decision:**
> Why 1: Why use lib X? — It's the team's standard.
> Why 2: Why is it standard? — *(gap: assumption — check git log, package.json, or docs)*
> Result: lib X was replaced last month; use lib Y instead.

## Anti-Patterns

- Skipping the 3-why and guessing a fix
- Accepting your first answer without probing for assumptions
- Fetching from the web when the answer is already in the repo
- Asking the user before exhausting local discovery
