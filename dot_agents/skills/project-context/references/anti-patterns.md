# AGENTS.md Anti-patterns

Avoid all of the following when drafting, reviewing, or updating an `AGENTS.md`.

## Do not auto-generate

Do not run `/init` or any equivalent and commit the output blind. Repository context files — human- or LLM-written — raise inference cost by over 20%. They do not reliably improve task success either: the paper found no significant gain, and developer-written files beat generated ones by 7% (Gloaguen and others, arXiv:2602.11988). Human-curated, verified, minimal content is the only thing that earns the cost.

## Do not duplicate README.md or `docs/`

`AGENTS.md` complements, it does not restate. Re-stating the README's why or duplicating `docs/` content adds cost without gain. The Gloaguen paper found no significant task-success effect from LLM-generated files. They helped by 2.7% only when *all* other documentation was removed. Use pointers, not copies.

## Do not add a Project structure or Architecture overview section

Agents navigate the tree themselves. Restating it costs tokens without helping. ETH Zurich found codebase overviews did not help agents find files faster.

## Do not append rules reactively

"Add another rule when the agent makes a mistake" leads to drift-and-append, the most common failure mode. Prune stale rules.

## Stay under 150 lines in the root AGENTS.md

Target ~40–80 lines. The MSR '26 survey of 466 OSS projects found `AGENTS.md` files averaging 142 lines. The standard deviation was 231, and the survey found no settled content structure (Context Engineering for AI Agents in Open-Source Software, arXiv:2510.21413). The 150 ceiling is a house boundary, not a published one. Allow growth up to 150 when the project genuinely benefits from keeping guidance co-located rather than splitting it into supplemental files. Past 150, split into nested per-package files (see `Monorepos` in `SKILL.md`). Augment Code's real-world upper bound for monolithic files is ~200 lines. HumanLayer reports a general consensus of under 300 lines. Both flag that beyond ~200, modular organization becomes necessary for token-budget reasons (Gloaguen and others, arXiv:2602.11988, Lulla and others, arXiv:2601.20404).

## Do not rely on vendor-specific agent files

`CLAUDE.md`, `.cursorrules`, `.windsurfrules`, `GEMINI.md`, `.github/copilot-instructions.md` are vendor lock-in. Put universal content in `AGENTS.md` and have the vendor file import it (for example, `@AGENTS.md`). Vendor-specific overrides belong in `.agents/<vendor>/`, not at the root.

## Do not write agent content into public `docs/`

`docs/` is human-readable project documentation. Auto-generated API references, fetched references, and other agent-only material belong in `.agents/docs/` or `.agents/docs/cache/`. Keep `docs/` hand-written and on-topic.

## Do not commit vendor symlinks

After unifying `.cursor/` → `.agents/<vendor>/` (or any vendor), the root-level symlink must be in `.gitignore` so it is recreated locally on each clone. Do not commit it as a checked-in symlink.

## Do not skip the `✅ Always` vendor-symlink rule

If the project unifies vendor directories under `.agents/`, `AGENTS.md` must include a `✅ Always` rule to recreate the symlink on fresh clones. Without it, the next session cannot find the vendor config.