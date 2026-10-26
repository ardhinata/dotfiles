# Question Tool — Call Shape

The `question` tool asks the user a set of choices. This rule adds the call
shape that the tool description does not cover.

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

## Options

- The tool adds a "Type your own answer" option by itself. Do not add a
  separate option for free-form answers.
- Put the recommended option first and add "(Recommended)" to its label.
