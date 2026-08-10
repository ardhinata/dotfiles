# Proactive Note Capture

A finding worth recording is one that is **verified, non-obvious, reusable, and likely to change a future decision or save investigation** — for example, a hidden constraint, a tool quirk, an environment difference, a contradicting assumption, or a piece of recovered context.

This rule governs *task-time note capture*. It does **not** grant permission to edit persistent documentation, knowledge caches, or project-context files. Those destinations still follow their own rules (`web-tools-priority.md`, `project-context.md`, etc.).

## When to capture

Capture during a task when **all** of the following hold:

- The finding is **verified** (do not record speculation as fact; mark uncertainty explicitly).
- It is **non-obvious** (future sessions or the resumed session will miss it without help).
- It is **reusable** beyond this single turn, OR it is **task-critical** and could be lost to compaction, session restart, or task switching.
- It does **not** belong to an excluded category below.

If only some hold — or capture would derail the active work — defer instead (next section).

## Capture mode: immediate

When capture is safe and low-cost, write it **right now** to a shared-context task note.

- **Path**: `.tmp/docs/notes/<YYYY-MM-DD>-<task-slug>.md` (or update the file already created for that task). The dir is the working tree of the per-project shared context repo (see `~/.config/kilo/skills/project-layout/SKILL.md` §"Shared context repo").
- **Before creating**: run `kilo-shared-pull origin main` to surface any cross-worktree collisions, then list `.tmp/docs/notes/`, `head -n 10` each file, and reuse / merge into an existing note on the same task. Do not duplicate.
- **After creating**: run `kilo-shared-save "<short-message>"` from the project root to commit the new note. Per the `proactive-note-capture` enforcement rule, **every write to `.tmp/docs/` must end with a commit** — uncommitted notes are flagged as in-flight in the shared context repo's status.
- **Sections to fill** — keep tight:
  1. **Finding** — one or two sentences, plain language.
  2. **Evidence** — exact file paths, command outputs, URLs, or code locations that justify it.
  3. **Why it matters** — which future decision or behavior this changes.
  4. **Scope** — repo, machine profile, language/runtime, condition (e.g., `if podman`, `if Docker shim`).
  5. **Uncertainty** — what is still unverified, what would re-validate it.
  6. **Recommended destination** — see "Destination precedence".
  7. **Date captured** (ISO) — for staleness checks later.

Stop as soon as the note is sufficient. Do not promote findings to persistent docs from here.

**Never** write notes to `.tmp/scratch/` — that dir is per-worktree ephemeral and excluded from commits by the pre-commit hook. Notes belong in `.tmp/docs/notes/` (or in a persistent location the user names).

## Capture mode: deferred

When immediate capture is unsafe, blocked, or would interrupt the active task, **defer with enough context to act later**.

1. Add a `Deferred documentation` block to the active plan in `.tmp/docs/plans/<YYYY-MM-DD>-<task-slug>.md` (see `plans.md`), or — when there is no plan — append a `## Deferred notes` section to the closest task scratchpad in `.tmp/scratch/`.
2. The block must contain: the same seven fields as a captured note (finding, evidence, why it matters, scope, uncertainty, recommended destination, date).
3. **If a memory tool is exposed** (`kilo_memory_save`): save a short pointer with the deferred topic, current state, next action, and a relative path to the file that holds the detail. Memory is a *pointer*, never the canonical record.
4. Do not create a transient note file just to record the deferral — the plan/scratchpad block plus memory pointer is enough.

## Promotion (later, on user request)

When the user asks to update docs, references, or notes:

1. Search `.tmp/docs/notes/`, the active `.tmp/docs/plans/` directory, and memory entries for matching topics.
2. Verify the finding against current project state (`git status`, `git diff`, `chezmoi diff`, source files) — deferrals from stale contexts must be re-checked.
3. Route each finding to its **recommended destination** following that destination's owning rule (see **Destination precedence** below). The owning rule owns its own destination — this rule does not redefine routing.
4. After promotion, **mark the deferred item resolved** in its source plan/note (e.g., `→ promoted to AGENTS.md` with date) or remove the block. Do not leave stale deferrals.

## Destination precedence

| Finding type | Destination | Owning rule / skill |
|---|---|---|
| Reusable web fact / volatile API | `.agents/docs/cache/` | `web-tools-priority.md` |
| Repo-wide convention | `AGENTS.md` (proposal only) | `project-context.md` + `project-context` skill |
| File-specific guidance | Skill `SKILL.md` / references | `agent-context` skill |
| Personal preference / habit | `personal-quirks.md` | (this directory) |
| Task-only scratch (committed, cross-worktree) | `.tmp/docs/{notes,plans}/` | (this rule + `plans.md`) |
| Task-only scratch (per-worktree, never commit) | `.tmp/scratch/` | (this rule) |

When two destinations both fit, prefer the **more verified** and the **lower-overhead** one. A web-cache entry does not belong in `AGENTS.md`; a global convention does not belong in `.tmp/docs/notes/`.

## Exclusions — do not capture

- Secrets, credentials, tokens, private keys, key fingerprints, or any value matching the **Sensitive File Handling** list in `.kilo/rules/chezmoi-source-project.md`.
- Trivia obvious from filenames, manpages, or first-party docs.
- Disposable shell output, full-file dumps, or trivial commands.
- Speculation framed as fact. Mark uncertainty instead.
- Anything that requires edits to `AGENTS.md`, persistent docs, or git history without the user’s approval — those are *promotion*, not capture.
- Anything belonging in `.tmp/scratch/` — that dir is gitignored and never committed; capture for `.tmp/scratch/` is not a note, it's throwaway work (use the scratchpad, not a structured note).

## Anti-patterns

- Recording a note and never resolving it: deferrals without a promotion path.
- Promoting a deferral without re-verifying — the world moves; the record may be stale.
- Writing a memory entry as the canonical store instead of a pointer to a file.
- Creating `.tmp/docs/notes/` files for things that belong in `.tmp/docs/plans/` (plans) or `.agents/docs/cache/` (reusable facts).
- **Writing to `.tmp/docs/` and not running `kilo-shared-save`** — uncommitted notes vanish on worktree destroy and don't reach sibling worktrees.
- **Writing to `.tmp/notes/`** (legacy path) instead of `.tmp/docs/notes/` — the legacy path is no longer mounted; the file silently lives only in the current worktree and is lost on destroy.
