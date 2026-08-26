# Before and after

Worked rewrites for software text. Each example names the rules that it corrects.

## A procedure with stacked clauses

**Before** (38 words, one sentence, a semicolon, a gerund, and a phrasal verb):

> Before setting up the client, you'll want to grab the API key from the dashboard; it's under
> Settings, and once you've got it you can go ahead and configure the client with it.

Errors: 5.1 (too long), 5.2 (many instructions), 4.2 (contractions), 8.1 (semicolon), 3.5 (`setting`),
9.3 (`set up`, `grab`, `go ahead`), 3.2 (`you've got`, present perfect).

**After** (three instructions, each under 20 words):

> 1. Open the Settings page of the dashboard.
> 2. Get the API key.
> 3. Configure the client with this key.

## A description with a long noun cluster

**Before**:

> The WebSocket API Gateway connection context table item retention period is configurable.

Errors: 2.1 (seven nouns in one cluster), 3.6 (weak passive construction).

**After**:

> The connection table keeps each item for a fixed time. You can change this time.

## A note that gives an instruction

**Before**:

> Note: you should always delete the test route before you deploy.

Errors: 5.5 (a note must not instruct).

**After** — move the action into the procedure, and keep the note for information:

> 4. Delete the test route.
>
> Note: the stage does not include the test route until the next deployment.

## Safety text in the wrong order

**Before**:

> Run the migration script. This will drop the table if it already exists, so make sure you have a
> backup first.

Errors: 7.2 (the risk comes after the command), 3.2 (`will drop` is acceptable, but `you have` here
is a complex construction), 5.2 (two instructions in one sentence).

**After**:

> WARNING: the migration script removes the table. You lose all data in the table.
>
> 1. Make a backup of the table.
> 2. Run the migration script.

## Hedged and padded prose

**Before** (31 words):

> It's worth noting that, due to the fact that the authorizer is currently disabled, it's probably
> the case that all connections are effectively sharing one single user identity at this time.

Errors: 6.3 (too long), 4.2 (contractions), 9.17 (`due to the fact that`), unapproved words
(`currently`, `effectively`), hedge stacking.

**After** (two sentences, 9 and 8 words):

> The authorizer is off now. Therefore all connections use one user identity.

## Passive voice with a known agent

**Before**:

> The permission must be added by the team that owns the function.

Errors: 3.6 (the agent is known, so the passive voice is not permitted).

**After**:

> The team that owns the function must add the permission.

## Passive voice with an unknown agent — permitted

This sentence is correct in descriptive text. The agent is genuinely unknown.

> During the transmission, the data was corrupted.

## Synonym rotation

**Before**:

> First, verify the config. Then confirm that the tables exist. Finally, ensure the role has access.

Errors: 1.11 and 9.4 (three words for one action), 1.2 (`verify`, `confirm`, `ensure` are not
approved).

**After**:

> 1. Make sure that the configuration is correct.
> 2. Make sure that the tables exist.
> 3. Make sure that the role has access.

Repetition is correct in STE. Repetition is not a style error.

## A word count that looks wrong but is correct

> Set the timeout to 3000 ms (three seconds) for the read-only replica.

Count: `Set`, `the`, `timeout`, `to`, `3000 ms` (rule 8.6, one word), `(three seconds)` (rule 8.5,
one word), `for`, `the`, `read-only` (rule 8.7, one word), `replica` = 10 words. The sentence
conforms to rule 5.1.

Apply rules 8.4 to 8.7 before you report a sentence as too long.

## An identifier that must not change

**Before**, an attempt to simplify a technical noun:

> Update the route for the connect action on the web socket interface.

**After** — keep the exact identifiers:

> Set the authorization type of the route `$connect` to `CUSTOM`. The route ID is `0svif9c`.

Rules 1.5 and 1.6 permit `$connect` and `0svif9c` as technical nouns. Rule 1.11 tells you to use the
same name every time.
