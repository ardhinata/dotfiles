# Persist Plans During Planning Phases

For any planning phase or multi-step task, **always** persist the plan and context so an unexpected problem (compaction, crash, session restart) does not erase them. Plans live in **transient** locations by default, but the user may ask for a **persistent** plan — handle both.

## Locations

- **Transient (default):** `.tmp/plans/<YYYY-MM-DD>-<task-slug>.md` — gitignored, ephemeral, safe to assume scratch.
- **Persistent (user-requested):** when the user says "persistent plan", "keep this plan", "save this plan in the repo", or names a path, use **that** location instead (e.g. `docs/plans/<task-slug>.md`, a project `plans/` dir, or whatever the user specifies). Confirm the path if ambiguous. Persistent plans **may be committed** — write them with the project's normal conventions (frontmatter, headings, code style).

## Workflow

- **Before planning starts (mandatory):** scan **both** candidate locations — list `.tmp/plans/` and any user-specified persistent dir — and `head -n 10` each existing file to check whether a duplicate or in-progress plan already exists for the same task. If it does — **merge into it** instead of creating a new one, or surface the conflict to the user before proceeding. This prevents duplicate plans, conflicting assumptions, and wasted work.
- **At planning start:** write the plan to the appropriate location (transient or persistent). Keep it concise: goal, scope, steps, open questions, assumptions, risks.
- **At every checkpoint / milestone:** update that file in place with what changed, what was completed, and what is next. Do not let it drift from reality. The same checkpoint rule applies to both transient and persistent plans.
- **If a memory tool is exposed** (e.g. `kilo_memory_save`): also call it at planning start and at each milestone with a short durable summary (goal + current step + next step), **plus the file path** so resume can jump straight to it. Skip only if the task is trivial or ephemeral.
- **Resuming after interruption:** read the memory entry first (to get the path), then load the file at that path before asking the user any context-recovery question.
- **Promotion:** if a transient plan becomes important enough to keep, copy it to the persistent location on user request — do not silently switch locations mid-task.
