# Ambiguity Resolution

When a task has ambiguity that could cause an incorrect implementation, **ask the user** before proceeding — but the *format* depends on the nature of the question. There are three modes; pick the one that matches.

## When to Ask

- Two or more valid interpretations exist, each producing a meaningfully different result
- A missing detail would force guessing at behavior, convention, or scope that affects correctness
- Ambiguous terminology maps to multiple concrete choices (library, framework, pattern)

## Choose a Format

### 1. Independent questions → batch with `question`

Use the `question` tool when the candidate questions are **independent** — answering one does not change what the others should ask or how they should be phrased.

Each question:

- Clear header (30 chars max)
- 2–5 distinct options, each with a short label and a one-line consequence
- **Recommend one** as best choice — place it first, append `(Recommended)`
- Custom answer enabled by default (do not add an "Other" option)

### 2. Dependent questions → one `question` at a time

If the answer to a question can **change the content, options, or relevance of subsequent questions**, do not batch. Ask one `question` at a time and let the next call's options adjust to what you learned.

Examples of dependency:

- A choice between frameworks changes the follow-up about which ORM/lint config to adopt
- A scope decision changes which conventions are even applicable
- An "are we doing this at all?" question gates everything that follows

### 3. Open-ended questions → ask in plain text

If the question is **open-ended** — the answer is free-form prose, a design rationale, a brainstorming request, a trade-off discussion, or context the agent cannot enumerate into 2–5 options — **skip the `question` tool** and ask in ordinary text. Multiple-choice is a poor fit when the user needs to explain, justify, or describe rather than pick.

Ask in plain text when any of these is true:

- The user needs to provide context, rationale, or background the agent does not have
- The choices are not enumerable from project knowledge
- The question is "explain what you want" or "tell me how you'd approach this"
- Branching is needed based on the user's narrative answer, not a discrete pick

## Limits

- **Max 8 questions per task.** The cap counts across all three modes (batched `question` calls + sequential `question` calls + plain-text asks).
- After 8, state what remains unclear, then proceed on the best interpretation.

## Anti-Patterns

- Do not ask about trivia, style, or details that don't affect correctness
- Do not ask when there is an obvious default with no meaningful trade-off
- Do not ask what the codebase or project conventions already answer — read those first
- Do not confuse `question` (asks the user a question) with `suggest` (offers a code review)
- **Do not batch dependent questions** — a single `question` call must contain only questions whose options stay valid regardless of how the others are answered
- **Do not force open-ended asks into `question`** — when the user must explain or describe, plain text is the only honest format
- **Do not over-ask** — if three plain-text asks in a row are needed, the user may be doing the agent's job; reconsider whether the task is well-scoped at all
