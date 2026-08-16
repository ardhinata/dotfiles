# Persist Plans During Planning Phases

For any planning phase or multi-step task, **always** persist the plan and context so an unexpected problem (compaction, crash, session restart) does not erase them. Plans live in **shared-context** locations by default — they survive across worktrees and machines via the shared context repo (see `~/.config/kilo/skills/project-layout/SKILL.md` §"Shared context repo"). The user may ask for a plan outside that mechanism (a project `docs/plans/`, a path they name, etc.) — handle both.

## Locations

- **Shared context (default):** `.tmp/docs/plans/<YYYY-MM-DD>-<task-slug>.md` — git-tracked in the per-project shared context repo (`~/.local/share/kilo/shared-context/<project-slug>.git/`), one branch per Agent Manager worktree, persisted across worktrees and machines. **Every write must end with `kilo-shared-save "<short-message>"`** (per the `project-layout` skill and `shared-context` skill).
- **Persistent (user-requested):** when the user says "persistent plan", "keep this plan", "save this plan in the repo", or names a path, use **that** location instead (e.g. `docs/plans/<task-slug>.md`, a project `plans/` dir, or whatever the user specifies). Confirm the path if ambiguous. Persistent plans **may be committed** to the project repo — write them with the project's normal conventions (frontmatter, headings, code style).

"Transient" vs "persistent" no longer means "ephemeral vs durable" — both are durable. The distinction is now **scope**: shared-context plans are visible across worktrees via git; persistent (project-tracked) plans are part of the project's source-of-truth documentation.

## Workflow

- **Before planning starts (mandatory):** run `kilo-shared-pull origin main` (or `git fetch origin main` from `.tmp/docs/` if the wrapper is unavailable) to surface any cross-worktree collisions, then scan `.tmp/docs/plans/` (and any user-specified persistent dir) and `head -n 10` each existing file to check whether a duplicate or in-progress plan already exists for the same task. If it does — **merge into it** instead of creating a new one, or surface the conflict to the user before proceeding. This prevents duplicate plans, conflicting assumptions, and wasted work.
- **At planning start:** write the plan to `.tmp/docs/plans/<YYYY-MM-DD>-<task-slug>.md` (or the persistent location). Keep it concise: goal, scope, steps, open questions, assumptions, risks.
- **At every checkpoint / milestone:** update that file in place with what changed, what was completed, and what is next. **After each in-place update, run `kilo-shared-save "checkpoint: <one-line summary>"`** to commit the milestone. Do not let the file drift from reality. The same checkpoint rule applies to both shared-context and persistent plans.
- **If a memory tool is exposed** (e.g. `kilo_memory_save`): also call it at planning start and at each milestone with a short durable summary (goal + current step + next step), **plus the file path** so resume can jump straight to it. Skip only if the task is trivial or ephemeral.
- **Resuming after interruption:** read the memory entry first (to get the path), then load the file at that path before asking the user any context-recovery question.
- **Promotion:** if a shared-context plan becomes important enough to graduate into project documentation (e.g. an ADR or a `docs/plans/` doc), copy it to the persistent location on user request — do not silently switch locations mid-task. The original commit in `.tmp/docs/plans/` stays as audit history.
