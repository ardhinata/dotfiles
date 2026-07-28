# Decision Matrix

The one-page answer to "what kind of doc am I writing?". Use the matrix
first; consult the per-type tables in
[`by-doc-type.md`](by-doc-type.md) only after picking a row.

## How to use this matrix

1. Identify the *intent* of the doc you're writing. Common intents:
   capture finding, plan work, record decision, propose design, cache
   research, encode rule, package workflow, introduce project, document
   release, document contribution.
2. Find the row that matches intent **and** scope (transient vs.
   persistent, internal vs. external).
3. Use the column links to jump straight to the per-type rule.

If two rows fit, prefer the more-verified, lower-overhead one. A
transient note beats a persistent doc if the finding may not survive
session restart anyway. A knowledge-cache entry beats a rule file if the
finding is web-sourced and may go stale.

## Decision matrix

| Intent | Scope / audience | Type | Path |
|---|---|---|---|
| Capture a verified, non-obvious, reusable finding | This task, this session | **Note** | `.tmp/notes/<YYYY-MM-DD>-<task-slug>.md` |
| Capture a verified finding but cannot pause safely | This task, deferred | **Deferred note** (block in active plan or scratchpad) | `.tmp/plans/...` or task scratchpad |
| Multi-step plan, ephemeral | This session, may not survive compaction | **Transient plan** | `.tmp/plans/<YYYY-MM-DD>-<task-slug>.md` |
| Multi-step plan, kept with the repo | Repo, user-approved | **Persistent plan** | user-specified (e.g. `docs/plans/<slug>.md`) |
| Decision with options + consequences, needs to be discoverable later | Repo, durable | **ADR** | `docs/adr/NNNN-<slug>.md` |
| Design proposal, needs team review | Repo, durable, reviewable | **RFC** | `docs/rfcs/NNNN-<slug>.md` |
| Design proposal, internal, lighter than an RFC | Repo, durable | **Design doc** | `docs/design/<slug>.md` |
| Reusable web-learned fact, may go stale in months | Repo knowledge cache | **Knowledge-cache entry** | `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` |
| Repo-wide rule, agent follows every session | Repo-wide, hot | **Kilo rule file** | `dot_config/kilo/rules/<slug>.md` |
| Workflow, agent loads on demand | Repo or global, on-demand | **Skill** | `dot_config/kilo/skills/<slug>/SKILL.md` |
| Project intro, install, getting started | Humans, first touch | **README.md** | root `README.md` |
| Project conventions, build/test commands, boundaries | Agents, hot | **AGENTS.md** | root `AGENTS.md` (and nested per monorepo package) |
| Sub-tree intro, table of contents for a doc folder | Humans | **Topic README** | `<dir>/README.md` |
| Release-by-release changes | Humans, users | **CHANGELOG.md** | root `CHANGELOG.md` |
| Contribution workflow | Humans, contributors | **CONTRIBUTING.md** | root `CONTRIBUTING.md` |
| Throwaway work in progress | This session, gitignored | **Scratch** | `.tmp/scratch/...` (no convention beyond "delete when done") |

## Decision heuristics

These rules resolve ambiguity when the matrix has two plausible rows.

### Plan vs. ADR

- A **plan** is forward-looking and disposable. It walks through *what
  we'll do*, in steps, with checkpoints. Plans can be revised without
  notice.
- An **ADR** is backward-looking and durable. It captures *what we
  decided and why*. ADRs are immutable once accepted; superseded ADRs
  are referenced by the new ADR.
- If the doc will outlive the decision, write an ADR. If it walks
  through *doing* the work, write a plan.

### Plan vs. note

- A **plan** has ordered steps and checkpoints. It describes work.
- A **note** is a discrete, reusable finding. It describes *a fact*.
- If the finding is "do these N steps in order", it's a plan. If it's
  "this tool has a quirk — here's why", it's a note.

### Note vs. knowledge-cache entry

- A **note** (`.tmp/notes/`) is gitignored and transient. It may not
  survive session restart.
- A **knowledge-cache entry** (`.agents/docs/cache/`) is gitignored but
  durable. It indexes into a topic `README.md` so future sessions can
  re-discover it.
- If the finding is reusable beyond the current session, cache it. If
  it's only useful for the current task, leave it as a note.

### ADR vs. design doc vs. RFC

- An **ADR** is short and structured: context, options, decision,
  consequences. ~50–200 lines. One decision per ADR. MADR format.
- A **design doc** is longer and exploratory: problem, motivation,
  alternative designs, trade-offs, recommended approach. Can run 1k+
  lines. No fixed structure.
- An **RFC** is the heavyweight version: same as a design doc but
  formally requested for review and comment, often with a deadline and
  reviewers.
- Use an ADR when the decision is captured; use a design doc when you
  need to *make* the decision; use an RFC when the decision affects
  many people and they need to weigh in.

### Kilo rule vs. SKILL

- A **rule** loads every session, in full, as part of the agent
  instruction set. It is for repo-wide "always / ask first / never"
  guidance. Keep it short (~50–150 lines).
- A **skill** loads only when triggered, in full when triggered, and
  can defer detail to `references/`. It is for workflows the agent
  follows sometimes.
- Use a rule for "do this on every task". Use a skill for "when you
  need to do X, here's how".

### AGENTS.md vs. README.md

- A **README.md** is for humans. Quick starts, project description,
  contribution norms.
- An **AGENTS.md** is for agents. Build steps, tests, conventions that
  would clutter a README.
- The two files must cross-reference each other (the
  [project-context skill](../../project-context/SKILL.md) makes this
  mandatory).

## When in doubt

- Default to the **lower-overhead, shorter-lived** option. Promote to a
  longer-lived doc only when the user asks, the finding clearly
  outlasts the session, or another doc explicitly references it.
- When two types fit and you cannot tell which, write a note and link
  to the plan, knowledge cache, or rule you would have written. The
  note captures the finding; the user or future session can promote
  it.