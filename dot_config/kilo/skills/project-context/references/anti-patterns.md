# AGENTS.md Anti-patterns

Avoid all of the following when drafting, reviewing, or updating an `AGENTS.md`.

## Do not auto-generate

Do not run `/init` or any equivalent and commit the output blind. Repository context files — human- or LLM-written — raise inference cost by over 20% and tend to reduce task success vs no context; LLM-generated files reduce it further (Gloaguen et al., ICLR 2026 Workshop, arXiv:2602.11988). Human-curated, verified, minimal content is the only thing that earns the cost.

## Do not duplicate README.md or `docs/`

`AGENTS.md` complements, it does not restate. Re-stating the README's why or duplicating `docs/` content measurably reduces task success (the Gloaguen paper showed LLM-generated files only helped when *all* other docs were removed). Use pointers, not copies.

## Do not add a Project structure or Architecture overview section

Agents navigate the tree themselves; restating it costs tokens without helping. ETH Zurich found codebase overviews did not help agents find files faster.

## Do not append rules reactively

"Add another rule when the agent makes a mistake" leads to drift-and-append, the most common failure mode. Prune stale rules.

## Stay under 150 lines in the root AGENTS.md

Target ~40–80 lines. The MSR '26 survey of 466 OSS projects found a mean of 142 lines — 150 is the empirical boundary between "monolithic works fine" and "start fragmenting." Allow growth up to 150 when the project genuinely benefits from keeping guidance co-located rather than splitting it into supplemental files. Past 150, split into nested per-package files (see `Monorepos` in `SKILL.md`). Augment Code's real-world upper bound for monolithic files is ~200 lines; HumanLayer's outer cap is ~300; both flag that beyond ~200, modular organization becomes necessary for token-budget reasons (Gloaguen et al., arXiv:2602.11988; Lulla et al., arXiv:2601.20404).

## Do not rely on vendor-specific agent files

`CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `GEMINI.md`, `.github/copilot-instructions.md` are vendor lock-in. Put universal content in `AGENTS.md` and have the vendor file import it (e.g. `@AGENTS.md`). Vendor-specific overrides belong in `.agents/<vendor>/`, not at the root.

## Do not write agent content into public `docs/`

`docs/` is human-readable project documentation. Auto-generated API references, fetched references, and other agent-only material belong in `.agents/docs/` or `.agents/docs/cache/`. Keep `docs/` hand-written and on-topic.

## Do not commit vendor symlinks

After unifying `.kilo/` → `.agents/kilo/` (or any vendor), the root-level symlink must be in `.gitignore` so it is recreated locally on each clone — not committed as a checked-in symlink.

## Do not skip the `✅ Always` vendor-symlink rule

If the project unifies vendor directories under `.agents/`, `AGENTS.md` must include a `✅ Always` rule to recreate the symlink on fresh clones. Without it, the next session cannot find the vendor config.