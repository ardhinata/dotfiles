# Ambiguity Resolution

When the `question` tool is the right channel, this rule governs the **shape** of the call. The tool itself defines the contract; this rule adds only what the tool does not.

## Dependency rule

If the answer to one question can **change the content, options, or relevance of subsequent questions**, do not batch. Ask one `question` at a time and let the next call's options adjust to what you learned.

Examples of dependency:

- A choice between frameworks changes the follow-up about which ORM/lint config to adopt.
- A scope decision changes which conventions are even applicable.
- An "are we doing this at all?" question gates everything that follows.

## Cap

**Max 8 questions per task.** The cap counts across all three modes (batched `question` calls + sequential `question` calls + plain-text asks). After 8, state what remains unclear, then proceed on the best interpretation.

## Anti-patterns

- **Do not force open-ended asks into `question`** — when the user must explain, justify, or describe, plain text is the only honest format.
- **Do not over-ask** — if three plain-text asks in a row are needed, the user may be doing the agent's job; reconsider whether the task is well-scoped at all.
- Do not ask about trivia, style, or details that don't affect correctness.
- Do not ask when there is an obvious default with no meaningful trade-off.
- Do not ask what the codebase or project conventions already answer — read those first.
- Do not confuse `question` (asks the user a question) with `suggest` (offers a code review).
