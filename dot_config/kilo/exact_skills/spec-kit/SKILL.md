---
name: spec-kit
description: Load when running the spec-driven development workflow. Encodes the constitution → specify → clarify → plan → tasks → analyze → checklist → converge phase order, per-phase artifact shapes, gate questions, and integration with the assist-only anti-assumption protocol. Targets spec-kit v1.0.0 (2026-08-21); refresh when spec-kit ships a new release.
---

# spec-kit workflow

Spec-kit is a phase-ordered loop, not a CLI tool. This skill encodes the per-phase artifacts, gate questions, and two known spec-kit failure modes. The persona (mode prompt) owns the loop; this skill owns the shape so the persona prompt stays small.

## Phases

1. **Constitution** — project principles, testing bar, stack rules. One per project.
2. **Specify** — `spec.md` (what + why, no tech). Forces the human to write it.
3. **Clarify** — tagged open questions inside `spec.md`.
4. **Plan** — `plan.md` (how, tech stack, risks). Drafted as a skeleton; human fills the choices.
5. **Tasks** — `tasks.md` (small, reviewable units). Generated only after plan sign-off.
6. **Analyze** — cross-artifact consistency report (`analyze.md`).
7. **Checklist** — quality checklist (`checklist.md`), "unit tests for English".
8. **Implement** — source code. **Disabled** in read-mostly modes; humans implement against `tasks.md`.
9. **Converge** — remaining-gap tasks after implementation. Routes back to implement mode.

## Artifact shapes

| Phase | Path | Shape |
|---|---|---|
| constitution | `docs/assist-only/constitution.md` | 5–8 numbered principles; testing bar; stack allow/deny list. |
| specify | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/spec.md` | What + why; no tech; ends with `## Open questions` list. |
| plan | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/plan.md` | Tech stack; component map; risks; trade-offs. |
| tasks | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/tasks.md` | `- [ ]` list; each item ≤ one sitting. |
| analyze | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/analyze.md` | Cross-artifact consistency findings (spec ↔ plan ↔ tasks). |
| checklist | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/checklist.md` | Yes/no questions with `[PASS]`/`[FAIL]`/`[N/A]` tags and verbatim claims. |
| converge | `docs/assist-only/specs/<YYYY-MM-DD>-<slug>/converge.md` | Gap list left after implement. |
| reviews (spec-anchored) | `docs/assist-only/specs/<spec-slug>/review-<branch-or-date>.md` | Five-field format: **Severity / File:Line / Claim / Evidence / Fix shape**. |
| reviews (loose) | `docs/assist-only/reviews/<YYYY-MM-DD>-<slug>.md` | Same five-field format. **Mandatory warning** if no spec anchors the review. |
| index | `docs/assist-only/specs/README.md` | One entry per spec folder with status, last-updated date, one-line summary. |
| demo code | `.tmp/scratch/assist-only/<slug>/` | Reference only; carries `REFERENCE — not for merge` header. |

Cross-references inside a spec folder use `./plan.md` (relative). The constitution is referenced as `docs/assist-only/constitution.md` from anywhere, or `../../constitution.md` from inside a spec folder.

### Checklist format (the rubric for accepting user-written code)

A **paragraph** of yes/no questions, ~15 lines, in this shape:

```md
- **Q:** <verbatim claim from the spec?>
  - **Tag:** `[PASS]` | `[FAIL]` | `[N/A]`
  - **Why it matters:** <one sentence>
  - **Fix shape:** <if FAIL — what to change and where>
```

- The agent drafts the questions from the spec; the user may drop, add, or rephrase.
- Re-run the checklist on demand after every spec edit. The questions are stable; the pass/fail block updates.
- Cross-artifact variant: run the same checklist against `plan.md` looking for spec drift. Overlaps with `analyze` but is the more general tool.
- **Refusal:** if the user asks for a checklist without supplying a spec, refuse. No spec, no checklist.

## Gate questions (between phases)

Each gate is a list, not prose. The agent must verify every item before allowing the next phase.

| Transition | Gate |
|---|---|
| constitution → specify | Principles written, testing bar chosen, stack allow/deny locked. |
| specify → clarify | Spec is in the spec folder with status `drafting`; open questions carry `[Q]` tags. |
| clarify → plan | Every `[Q]` resolved or marked `[DEFER]` with a written rationale; spec status flipped to `active`. |
| plan → tasks | Plan signed off; tech choices made (no `[TBD]`); risks acknowledged in writing. |
| tasks → analyze | Tasks list covers every acceptance criterion from the spec. |
| analyze → implement | No critical-severity findings; medium-severity findings acknowledged or fixed. |
| implement → checklist | All tasks `[x]` or rolled into `converge.md`. |
| checklist → converge | Checklist ≥ 90% `[PASS]` or each `[FAIL]` moved to `converge.md` with an owner. |

The gate is a contract — the agent cannot self-promote past it. If a gate fails, the agent surfaces the missing items to the user and waits.

## assist-only integration (three rules)

1. **The human writes the prose; the agent challenges.** spec.md, plan.md, and tasks.md are user-authored. The agent drafts skeletons only when the user asks; it never fills them silently.
2. **Spec-kit templates are reference shapes, not auto-fills.** The agent cites the shape (see Artifact shapes above) and stops. The next move belongs to the user.
3. **Anti-assumption protocol applies at every phase transition.** Each transition must ground the load-bearing claims from the prior phase. Use the project's `ambiguity-resolution` rule for independent questions, the `question` tool for dependent ones, and `webfetch`/`websearch` when the stakes warrant verification.

## Failure modes — guard against these

1. **`speckit.plan` self-promotes to implement (issue #1011).** Some spec-kit scaffolds let the plan phase start editing code. In read-mostly modes (e.g. `assist-only` with `edit` globbed to a sandbox) the mode literally cannot write a file, so the self-promotion is harmless. In write-capable modes, refuse any `speckit.plan` step that begins mutating non-task files.
2. **Constitution drift on agent or session switch.** When the agent or session changes mid-spec, the next agent must re-read `docs/assist-only/constitution.md` before acting. Single-mode sessions avoid this; cross-mode handoffs do not.

## When NOT to load

Skip this skill if the user's task is a single-turn edit, a refactor with no spec, or a Q&A. Load it when the user says "let's plan", "new spec", "I want to think this through", or names a spec-kit phase verb (constitution / specify / clarify / plan / tasks / analyze / checklist / converge).

## Refresh cadence

Spec-kit shipped 1.0.0 on 2026-08-21 (this skill targets that version). On each spec-kit release:

1. Re-read the upstream changelog (https://github.com/github/spec-kit/releases).
2. Update the **Phases** list if the order shifted.
3. Update the **Artifact shapes** table if the file naming changed.
4. Update the **Failure modes** list if a new issue is filed against it.
5. Bump the frontmatter `description`'s spec-kit version string.
