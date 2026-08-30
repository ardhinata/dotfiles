# docs/subagent-fleet/

Canonical design + workflow for the haru / natsu / aki / fuyu / shiki
research subagent fleet. Used by the revaluation workflow
(`.agents/kilo/command/subagent-fleet-reevaluate-models.md`), the
trigger rule
(`dot_config/kilo/exact_rules.personal.d/subagent-fleet-trigger.md`),
and every subagent body
(`dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`).

## Documents

| File | Purpose |
|---|---|
| [`2026-08-17-subagent-creative-conservative.md`](2026-08-17-subagent-creative-conservative.md) | **Canonical design** — 5 subagent roles, output contracts, model-selection rules, invocation pattern, permission block. Frequently referenced. Migrated here 2026-08-30 from `.tmp/docs/plans/`. |

## Shared-context augmentations (ephemeral)

The canonical design above is augmented by shared-context plans in
`.tmp/docs/plans/`. These plan augmentations are git-tracked across
Agent Manager worktrees but are not project-tracked; they target
specific operational changes without rewriting the canonical design.

| Plan | Purpose |
|---|---|
| `.tmp/docs/plans/2026-08-30-subagent-max-turn-limit.md` | Add explicit `steps` / `max_tokens` per-agent runtime caps (currently implicit; defaults to `steps: 25, max_tokens: 4000`). |
| `.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md` | **Old location** of the canonical design — kept readable as a `moved_from:` pointer until the migration is verified end-to-end. Will be deleted after the next revaluation confirms no site still points at the old path. |

## Why this directory exists

Before 2026-08-30, the canonical design lived at
`.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md`. That
location is right for ephemeral plans (per-worktree, git-tracked across
worktrees via the shared-context repo), but the design document is
referenced from 11+ places across the project — agent bodies, skill
references, a workflow command, a personal rule, AGENTS.md. A reference
that lives in shared-context can be lost when a worktree is destroyed,
and reading the doc requires knowing the shared-context repo exists.
Persistent location in `docs/` makes the document part of the project's
source-of-truth documentation, indexed by `README.md` and
`AGENTS.md`.

## Pointer maintenance

If you change the canonical file's path (rename or relocation), update:

1. Every cross-reference listed in
   [`.agents/kilo/command/subagent-fleet-reevaluate-models.md`](../../.agents/kilo/command/subagent-fleet-reevaluate-models.md)
   (3 sites).
2. `dot_config/kilo/exact_agent/README.md` (3 sites).
3. `dot_config/kilo/exact_agent/haru.md` (1 site — references §4 model picks).
4. `dot_config/kilo/exact_skills/subagent-fleet/SKILL.md` (1 site).
5. `dot_config/kilo/exact_skills/subagent-fleet/references/*.md` (4 sites — one per role reference).
6. `dot_config/kilo/exact_rules.personal.d/subagent-fleet-trigger.md` (2 sites).
7. `dot_config/kilo/exact_rules.personal.d/subagent-fleet-task-prompt-budget.md` (1 site).
8. `AGENTS.md` (1 site in the Pointers section).

Use `grep -r "2026-08-17-subagent-creative-conservative"` to verify
post-migration that no stale reference remains.

## Related

- Skill: `~/.config/kilo/skills/subagent-fleet/SKILL.md`
- Workflow: `.agents/kilo/command/subagent-fleet-reevaluate-models.md`
- Trigger rule: `dot_config/kilo/exact_rules.personal.d/subagent-fleet-trigger.md`
- Knowledge cache: `.agents/docs/cache/kilo-subagents/`,
  `.agents/docs/cache/openrouter/`