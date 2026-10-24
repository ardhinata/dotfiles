# ASD-STE100 Trigger

Load the `asd-ste100` skill before producing any user-facing prose that is meant to be read carefully — documentation, commit/PR messages, or explanations.

## When

Load the skill when any of these is true:

- **Authoring project docs**: writing or substantially updating a README, doc page, ADR, RFC, CHANGELOG entry, docstring, wiki entry, `AGENTS.md` draft, knowledge-cache entry, or persistent plan under `docs/plans/`.
- **Authoring rules or skills**: writing or substantially updating any file under `~/.agents/rules/`, `~/.agents/rules.personal.d/`, or `~/.agents/skills/<name>/SKILL.md` and its references.
- **Writing a non-trivial commit message or PR description.**
- **Producing a long assistant message** — any reply that exceeds roughly 6 sentences or ~150 words of explanation (design rationale, debugging walkthrough, trade-off analysis, comparison, verdict), whether the user asked for it or the agent chose to write it. Short status updates and one-line answers do not count.

## How

- Load the `asd-ste100` skill.
- Pick the mode the skill defines, do not relitigate it:
  - **Strict** — procedures, error messages, tool/function descriptions, safety text.
  - **STE-flavored** — READMEs, PR descriptions, explanatory prose, user-facing explanations.
- Apply it to your own draft before emitting prose — the lowest-cost place to disambiguate, since no human is in the loop afterward.
- For explanations specifically: STE-flavored mode. Short sentences, one idea per, plainest available word.
- **Self-check first.** Before emitting the prose, scan for the six habits in the skill's `Scan Checklist` (synonym rotation, hedge stacking, nominalization, marketing adjectives, run-on sentences, soft phrasal verbs). Fix them in your draft — the lowest-cost place to disambiguate, since no human is in the loop afterward.

## When NOT to load

- Trivial prose: typo fixes, single-word edits, formatting-only diffs.
- Code-only changes with no prose diff.
- The user wants existing skill output copied back, not new prose.
