# ASD-STE100 Trigger

Load the `asd-ste100` skill before producing any user-facing prose that is meant to be read carefully — documentation, commit/PR messages, or explanations.

## When

- Creating or substantially updating any documentation (README, doc page, plan, ADR, CHANGELOG, docstring, wiki entry).
- Writing a non-trivial commit message or PR description.
- The user asks for an explanation of a tool, workflow, concept, or prior work.

## How

- Use the Kilo `skill` tool with `name: "asd-ste100"`.
- Pick the mode the skill defines, do not relitigate it:
  - **Strict** — procedures, error messages, tool/function descriptions, safety text.
  - **STE-flavored** — READMEs, PR descriptions, explanatory prose, user-facing explanations.
- Apply it to your own draft before emitting prose — the lowest-cost place to disambiguate, since no human is in the loop afterward.
- For explanations specifically: STE-flavored mode. Short sentences, one idea per, plainest available word.

## When NOT to load

- Trivial prose: typo fixes, single-word edits, formatting-only diffs.
- Code-only changes with no prose diff.
- The user wants existing skill output copied back, not new prose.
