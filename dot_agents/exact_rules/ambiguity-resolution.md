# Ambiguity Resolution

Ask the user only when the answer changes what you do next.

## When to ask

Ask at the first decision point that meets all three tests:

- Two or more outcomes change what you write, not how you phrase it.
- The cheapest check is done: the manual, the tool description, and one source
  read.
- The remaining search space is open. No named file, flag, or document closes
  it.

A question costs one user turn. The research that replaces a question has no
upper bound. Bias toward the question.

Report a spec deviation as soon as you find it, with the options you found. Do
not finish the research first.

State the next question before the next batch of calls. Keep one question per
phase. Do not mix a harness question with a task question.

## Do not ask

- Do not ask about trivia, style, or details that do not affect correctness.
- Do not ask when there is an obvious default with no meaningful trade-off.
- Do not ask what the project docs already answer. Read them first.
- Do not over-ask. Three plain-text asks in a row mean the agent is doing the
  user's job. Reconsider whether the task is well scoped.
- Do not ask twice in one phase. One question per decision point.
- When the user must explain, justify, or describe something, use plain text.
  A picker of closed options cannot carry it.
