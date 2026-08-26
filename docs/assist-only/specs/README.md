# assist-only specs — index

Active and archived spec folders for the assist-only mode. The agent updates this index whenever it creates or updates a spec folder.

## Format

| Folder | Status | Last updated | Summary |
|---|---|---|---|
| `<YYYY-MM-DD>-<slug>/` | `drafting` / `active` / `converged` / `abandoned` | `<YYYY-MM-DD>` | <one-line summary> |

## Specs

_No specs yet. Create the first one with: `mkdir -p docs/assist-only/specs/$(date +%F)-<slug>` and start with `spec.md`._

## See also

- [Constitution](../constitution.md) — locked principles the specs inherit from.
- [spec-kit skill](../../dot_config/kilo/exact_skills/spec-kit/SKILL.md) — phase order and gate questions.

## Status legend

- **`drafting`** — `spec.md` exists, open questions are still being resolved.
- **`active`** — `spec.md` + `plan.md` are signed off; `tasks.md` may be in progress.
- **`converged`** — every task is `[x]` or has been rolled into `converge.md` with an owner.
- **`abandoned`** — the user stopped the work and the reasons are written into `converge.md`'s first section.
