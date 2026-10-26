# ASD-STE100 Trigger

Load the `asd-ste100` skill before producing user-facing prose that must be
read carefully.

## When

- Authoring or updating a README, doc page, ADR, RFC, CHANGELOG entry,
  docstring, `AGENTS.md` draft, knowledge-cache entry, or plan under
  `docs/plans/`.
- Authoring or updating a file under `~/.agents/rules/`,
  `~/.agents/rules.personal.d/`, or `~/.agents/skills/<name>/`.
- Writing a non-trivial commit message or PR description.
- Writing an assistant reply longer than 150 words. Scan it, do not rewrite
  it.

## How

- Load the skill and use the mode it defines: Strict for procedures, error
  messages, tool and function descriptions, and safety text. STE-flavored for
  READMEs, PR descriptions, and explanatory prose.
- Scan the draft against the skill's `Scan Checklist` before you emit it, and
  fix the six habits in the draft.
