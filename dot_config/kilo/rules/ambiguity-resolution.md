# Ambiguity Resolution

When a task has ambiguity that could cause an incorrect implementation, **ask the user** via the `question` tool before proceeding.

## When to Ask

- Two or more valid interpretations exist, each producing a meaningfully different result
- A missing detail would force guessing at behavior, convention, or scope that affects correctness
- Ambiguous terminology maps to multiple concrete choices (library, framework, pattern)

## How to Ask

Use `question` (interactive multiple-choice). Each question:

- Clear header (30 chars max)
- 2–5 distinct options, each with a short label and a one-line consequence
- **Recommend one** as best choice — place it first, append `(Recommended)`
- Custom answer enabled by default (do not add an "Other" option)

## Limits

- **Max 8 questions per task.** Batch related ambiguities into a single call.
- After 8, state what remains unclear, then proceed on the best interpretation.

## Anti-Patterns

- Do not ask about trivia, style, or details that don't affect correctness
- Do not ask when there is an obvious default with no meaningful trade-off
- Do not ask what the codebase or project conventions already answer — read those first
- Do not confuse `question` (need an answer) with `suggest` (offer a code review only)
