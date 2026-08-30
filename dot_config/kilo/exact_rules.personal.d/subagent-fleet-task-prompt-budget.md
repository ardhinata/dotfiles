---
description: Per-spawn task-prompt budget for haru/natsu/aki/fuyu/shiki — caps the task-tool prompt at ≤ 15 lines of non-body content and forbids output-path / filename-format overrides
---

# Subagent-fleet task-prompt budget

When the main agent spawns any of `haru`, `natsu`, `aki`, `fuyu`, or `shiki` via the `task` tool, the `prompt` argument MUST be **≤ 15 lines** of content the agent body does not already cover.

## Why

The agent body (in `dot_config/kilo/exact_agent/<role>.md`) already declares:

- the role definition, output contract, and per-role anti-patterns
- the operational discipline preamble (permission model, mutation boundaries, delegation pre-deny list)
- the sampling behaviour, `variant:` exposure note, and rationale

Repeating any of the above in the task prompt is duplicate signal — it inflates input tokens per subagent and produces no additional output quality. Empirically confirmed in the 2026-08-26 natsu smoke run (`ses_fc2d12b1cffeeeDNH0fzXKsYZJ`): the budget-form prompt produced a clean 8-finding report at the canonical body path, while the pre-budget form (71 lines, ~7.7 KB) duplicated the body and misdirected the subagent to `/tmp/kilo/` instead of `.tmp/docs/subagent-runs/`.

## What the task prompt MUST contain

Only the four things the body does not know:

1. **The question** — 1-3 lines. Without this, the subagent has no job.
2. **The required-reading list** — paths and URLs the agent must cite. The body does not know which sources are relevant to *this* question.
3. **Per-run constraints the body does not cover** — e.g. "verify this load-bearing claim against the spec-kit post-mortem", "must_adopt target is `assist-only.md`, evidence ≤ 1 source per finding".
4. **The report filename slug**, if any (e.g. `natsu-sdd-synthesis`). Append to the body's canonical path pattern `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>[-<slug>].yaml`, computed at write time with `date +%Y%m%d_%H%M%S` (NOT `<unix-ts>` — different epoch, different format).

## What the task prompt MUST NOT contain

- The role description — already in the body.
- The operational discipline preamble — already in the body.
- The output YAML schema — already in the body.
- The anti-patterns — already in the body.
- The sampling caveats / model declaration — already in the body.
- **The output path.** The body says `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>.yaml`. Do not restate as `/tmp/kilo/...` or any other path. The 2026-08-26 trace showed this kind of override caused the subagent to write to the wrong directory.
- **The filename format.** The body uses `YYYYMMDD_HHMMss` (local clock). Do not specify `<unix-ts>` or any other format. The slug is the only per-run filename override.

## Worked example

Canonical example at `.tmp/docs/user_cache/sample-subagent-natsu/user-message-1.md` (committed 2026-08-26). The natsu subagent produced `20260826_152801-natsu-sdd-synthesis.yaml` at the canonical body path with 8 findings in 2.5 min wall clock.

## Rationale and worked examples

Full design rationale, the prompt-pre-budget trace, and the budget-form rewrite: `.tmp/docs/plans/2026-08-26-natsu-prompt-deduplication.md`. If this rule and the plan disagree, **this rule wins** — and the plan is updated on the next revision pass.

## Anti-patterns

- Restating the agent's role in the task prompt — "You are natsu, the synthesizer, your job is to…" — duplicate of body lines 45-55.
- Specifying a different output path than `.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<role>.yaml` — leads to the 2026-08-26 path-misdirection bug.
- Specifying a different filename format than `YYYYMMDD_HHMMss-<role>[-<slug>].yaml` — produces files that the canonical-finder cannot locate.
- Pasting the entire `Instructions from:` block or `<env>` block from the parent agent's context into the task prompt — these are auto-injected; re-pasting them costs tokens without effect.
- Adding "If you cannot find X, fall back to Y" guidance that the body already has in its `Inputs` or `Anti-patterns` section.

## Boundary

- **The budget itself** (this rule).
- **When to call the fleet** → `dot_config/kilo/exact_rules.personal.d/subagent-fleet-trigger.md`.
- **How the fleet is configured, role definitions, sampling rationale** → `dot_config/kilo/exact_agent/{haru,natsu,aki,fuyu,shiki}.md`.
- **Fleet design, model picks, provider routing, full prompt-design history** → `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` (canonical plan).
