# Decision Matrix

The one-page answer to "what kind of doc am I writing?". Use the matrix
first. Consult the per-type tables in
[`by-doc-type.md`](by-doc-type.md) only after picking a row.

## How to use this matrix

1. Identify the *intent* of the doc you are writing. Common intents:
   capture finding, plan work, record decision, propose design, cache
   research, encode rule, package workflow, introduce project, document
   release, document contribution.
2. Find the row that matches intent **and** scope (task-only compared to
   repo-durable, internal compared to external).
3. Use the column links to jump straight to the per-type rule.

If two rows fit, prefer the more-verified, lower-overhead one. A
knowledge-cache entry beats a rule file if the finding is web-sourced and
may go stale.

## Decision matrix

| Intent | Scope / audience | Type | Path |
|---|---|---|---|
| Capture a verified, non-obvious, reusable finding | Repo knowledge cache, durable | **Knowledge-cache entry** | `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` |
| Multi-step plan | Repo, user-approved | **Persistent plan** | `docs/plans/<YYYY-MM-DD>-<task-slug>.md` |
| Plan in flight, may be discarded | This worktree, gitignored, never commit | **Transient plan** | `.tmp/scratch/<YYYY-MM-DD>-<task-slug>.md` |
| Decision with options + consequences, needs to be discoverable later | Repo, durable | **ADR** | `docs/adr/NNNN-<slug>.md` |
| Design proposal, needs team review | Repo, durable, reviewable | **RFC** | `docs/rfcs/NNNN-<slug>.md` |
| Design proposal, internal, lighter than an RFC | Repo, durable | **Design doc** | `docs/design/<slug>.md` |
| Reusable web-learned fact, may go stale in months | Repo knowledge cache | **Knowledge-cache entry** | `.agents/docs/cache/<topic>/YYYY-MM-DD-<slug>.md` |
| Repo-wide rule, agent follows every session | Repo-wide, hot | **Rule file** | `~/.agents/rules/<slug>.md` |
| Workflow, agent loads on demand | Repo or global, on-demand | **Skill** | `~/.agents/skills/<slug>/SKILL.md` |
| Project intro, install, getting started | Humans, first touch | **README.md** | root `README.md` |
| Project conventions, build/test commands, boundaries | Agents, hot | **AGENTS.md** | root `AGENTS.md` (and nested per monorepo package) |
| Sub-tree intro, table of contents for a doc folder | Humans | **Topic README** | `<dir>/README.md` |
| Release-by-release changes | Humans, users | **CHANGELOG.md** | root `CHANGELOG.md` |
| Contribution workflow | Humans, contributors | **CONTRIBUTING.md** | root `CONTRIBUTING.md` |
| Throwaway work in progress | This worktree, gitignored, never commit | **Scratch** | `.tmp/scratch/...` (no convention beyond "delete when done") |
| Incident write-up | Repo, durable | **Postmortem** | `docs/post-mortem/<YYYY-MM-DD>-<slug>.md` |

## Decision heuristics

These rules resolve ambiguity when the matrix has two plausible rows.

### Plan vs. ADR

- A **plan** is forward-looking and disposable. It walks through *what
  we will do*, in steps, with checkpoints. Plans can be revised without
  notice.
- An **ADR** is backward-looking and durable. It captures *what we
  decided and why*. ADRs are immutable once accepted. Superseded ADRs
  are referenced by the new ADR.
- If the doc will outlive the decision, write an ADR. If it walks
  through *doing* the work, write a plan.

### Persistent plan vs. transient plan

- A **persistent plan** is committed and reviewable. It records the work
  that was executed.
- A **transient plan** lives in `.tmp/scratch/` and is never committed. It
  records work that is still being written and may be discarded.
- Start in `.tmp/scratch/`. Move the file to `docs/plans/` before the work
  starts, keeping the filename, so a reviewer sees what the agent intended
  to do.

### One file or a directory

- **One file** when the doc is under its type's hard ceiling. A split
  doc costs a reader one extra hop, so it is not free.
- **A directory** when the doc passed its hard ceiling and holds one
  subject with many sections. The directory name is the slug the single
  file would have had. Inside it, an index `README.md` plus numbered
  section files.
- **Separate linked docs** when the doc holds several subjects that
  happen to meet in one file. A plan that contains an ADR's worth of
  decision records links to `docs/adr/`. It does not absorb them.

Do not split a doc that fits. Do not fold two subjects into one
directory to avoid writing a second doc.

### Plan vs. knowledge-cache entry

- A **plan** contains ordered steps and checkpoints. It describes work.
- A **knowledge-cache entry** is a discrete, reusable finding. It describes *a fact*.
- If the content is "do these N steps in order", it is a plan. If it is
  "this tool has a quirk — here's why", it is a cache entry.

### Knowledge-cache entry vs. rule file

- A **knowledge-cache entry** (`.agents/docs/cache/`) is gitignored (per the
  project-layout skill) but durable within the working tree. It indexes into
  a topic `README.md` so future sessions can re-discover it.
- A **rule file** (`~/.agents/rules/`) loads every session and is global, not
  project-scoped.
- If the finding is reusable beyond the current session, cache it. Promote
  it to a rule only when it must hold in every session.

### ADR vs. design doc vs. RFC

- An **ADR** is short and structured: context, options, decision,
  consequences. ~50–200 lines. One decision per ADR. MADR format.
- A **design doc** is longer and exploratory: problem, motivation,
  alternative designs, trade-offs, recommended approach. Can run 1k+
  lines. No fixed structure.
- An **RFC** is the heavyweight version: same as a design doc but
  formally requested for review and comment, often with a deadline and
  reviewers.
- Use an ADR when the decision is captured. Use a design doc when you
  need to *make* the decision. Use an RFC when the decision affects
  many people and they need to weigh in.

### Rule file vs. SKILL

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
- When two types fit and you cannot tell which, write a cache entry. Link
  to the plan, knowledge cache, or rule that you would write instead. The
  cache entry captures the finding. The user or future session can
  promote it.
- Cross-worktree compared to cross-machine: nothing in the agent layer is
  cross-worktree by default any more. A finding that must survive a
  machine loss belongs in the project repo (`docs/`). The knowledge cache
  is gitignored, so it survives a worktree but not a machine loss. A
  per-worktree scratch directory survives neither.