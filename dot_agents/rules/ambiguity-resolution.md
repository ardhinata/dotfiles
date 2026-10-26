# Ambiguity Resolution

When the `question` tool is the right channel, this rule governs the **shape**
of the call. The tool defines the contract. This rule adds what the tool does
not.

## Dependency rule

If the answer to one question can change the content, options, or relevance of
the next question, do not batch. Ask one `question` at a time. Let the next
call's options adjust to what you learned.

Examples of dependency:

- A choice between frameworks changes the follow-up about which ORM and lint
  config to adopt.
- A scope decision changes which conventions apply.
- An "are we doing this at all?" question gates everything after it.

## Batch shape

Ask at most three independent questions in one call. When more remain, put
them in plain text.

## Do not ask

- Do not force an open-ended ask into `question`. When the user must explain,
  justify, or describe, plain text is the only honest format.
- Do not over-ask. Three plain-text asks in a row mean the agent is doing the
  user's job. Reconsider whether the task is well scoped.
- Do not ask about trivia, style, or details that do not affect correctness.
- Do not ask when there is an obvious default with no meaningful trade-off.
