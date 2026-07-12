# AGENTS.md Anti-patterns

Avoid all of the following when drafting, reviewing, or updating an `AGENTS.md`.

## Do not auto-generate

Do not run `/init` or any equivalent and commit the output blind. Repository context files — human- or LLM-written — raise inference cost by over 20% and tend to reduce task success vs no context; LLM-generated files reduce it further (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988). Human-curated, verified, minimal content is the only thing that earns the cost.

## Do not add a Project structure or Architecture overview section

Agents navigate the tree themselves; restating it costs tokens without helping.

## Do not append rules reactively

"Add another rule when the agent makes a mistake" leads to drift-and-append, the most common failure mode. Prune stale rules.

## Do not exceed 60 lines in the root AGENTS.md

Past that, split into nested per-package files (see `Monorepos` in `SKILL.md`).

## Do not duplicate content that already lives in `README.md` or other docs

Add pointers instead. Duplication costs both writers and readers.
