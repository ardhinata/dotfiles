# Ambiguity Resolution

When executing a task, if you encounter ambiguity that could lead to an incorrect implementation or answer, **ask the user for clarification** using the `question` tool.

## When to Ask

- Two or more valid interpretations of the user's intent exist, and each would produce a meaningfully different result
- A missing detail would cause you to guess at behavior, convention, or scope that affects correctness
- The user's request uses ambiguous terminology that maps to multiple concrete choices (e.g., library, framework, pattern)

## How to Ask

Use the `question` tool with an interactive multiple-choice format. Each question must:

- Present a clear, specific header (30 chars max)
- Offer 2-5 distinct options, each with a short label and a brief description of the consequence
- **Recommend one option** as the best choice based on best practices, simplicity, or elegance — place it first in the list and append `(Recommended)` to its label. If no option clearly stands out, pick the most pragmatic one.
- Allow the user to provide a custom answer (enabled by default via `custom: true`)

## Limits

- **Maximum 8 questions per task.** Gather related ambiguities and batch them into a single `question` call where possible.
- If ambiguity persists after 8 questions, inform the user of what remains unclear, then proceed using the best interpretation based on all information gathered so far.

## Anti-Patterns

- Do not ask about trivia, style preferences, or details that don't affect correctness
- Do not ask when there is an obvious default with no meaningful trade-off
- Do not ask questions answerable by reading the codebase or project conventions first
