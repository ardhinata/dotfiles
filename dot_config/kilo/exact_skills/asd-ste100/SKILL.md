---
name: asd-ste100
description: >-
  Write, rewrite, and audit technical English under ASD-STE100 Simplified Technical English.
  Apply the 53 writing rules of Issue 9 (Jan 2025): one meaning per word, one part of speech per
  word, simple tenses only, no "-ing" verbs, active voice, ≤20 words for procedures and ≤25 for
  descriptions, no semicolons, no phrasal verbs, ≤3-word noun clusters. Use when the user asks for
  Simplified Technical English, STE, ASD-STE100, controlled language, plain English, or text for
  readers who do not speak English as a first language, or when text will be parsed by another
  agent or translation pipeline and misreading has a real cost. Use to audit text and report each
  rule violation sentence by sentence. Use it for procedures, runbooks, README files, release
  notes, error messages, and safety text. Not for creative or marketing copy.
license: MIT. LICENSE has the complete terms.
compatibility: The checker script needs Python 3.9 or later. It uses the standard library only.
metadata:
  standard: ASD-STE100 Issue 9 (January 2025)
  rules: 53 rules in 9 sections
  dictionary-included: "no"
  version: "1.0.0"
allowed-tools: Read Write Bash(python3:*)
---

# ASD-STE100 Simplified Technical English

ASD-STE100 is a controlled-language standard built by ASD (the AeroSpace and Defence Industries
Association of Europe) to stop maintenance technicians from misreading English instructions. The
standard removes the two biggest sources of misreading: words with more than one meaning, and
sentences with more than one possible structure.

This skill borrows that discipline for a different reader: an **AI agent or a downstream system**
that has to parse an English string — an error message, a tool description, an inter-agent
instruction, a status report — without a human in the loop to resolve ambiguity. If a maintenance
technician can misread "close the valve" as an adjective ("the valve that is near") instead of a
command, so can a language model.

## What the standard contains

ASD-STE100 has two parts:

| Part | Contents | Control |
| --- | --- | --- |
| Part 1 — writing rules | 53 rules in 9 sections | Grammar, sentence structure, style, layout |
| Part 2 — dictionary | About 900 approved words | One meaning and one part of speech per word |

**This skill does not contain the dictionary.** The dictionary is the core of the standard. Without
it you cannot claim full conformance. Apply the writing rules, apply the substitutions in
[references/word-substitutions.md](references/word-substitutions.md), and tell the user which parts
you could not check. Get the official specification free of charge from `asd-ste100.org`. See
[NOTICE](NOTICE) for the licensing boundary.

## Two modes

Pick a mode before rewriting. If the user does not say which, infer from the text type and state
the choice in one line.

**Strict** — procedures, error messages, tool and function descriptions, inter-agent instructions,
safety text. Anywhere a wrong reading has a cost. Apply every rule, including the hard length caps
and one-word-one-meaning discipline.

**STE-flavored** — READMEs, PR descriptions, changelogs, explanatory prose. Apply the structural
rules in full and treat the lexical rules as advisory (see Core Rewrite Rules for that split). In
practice that means keeping the sentence length caps, active voice, simple tenses, no phrasal
verbs, no semicolons, no nominalization and no marketing adjectives, while dropping the
one-word-one-meaning lockdown: prose needs some range, and a strict rewrite of prose reads as a
personality transplant rather than a clarification.

## Step 1 — classify the text

Do this first. The limits differ per type. Do not mix the two types in one passage.

| | Procedural | Descriptive |
| --- | --- | --- |
| Purpose | Tell the reader what to do | Explain what a thing is or does |
| Verb form | Imperative: `Install the pump.` | Simple present, simple past, or simple future |
| Words per sentence | 20 | 25 |
| Other limits | One instruction per sentence | One topic per paragraph. Six sentences per paragraph. |

A note inside a procedure is descriptive text. A note gives information. A note must not give an
instruction.

## Step 2 — apply the rules that give the most benefit

These twelve rules remove most errors. The full catalog is in
[references/writing-rules.md](references/writing-rules.md).

1. **One meaning for each word.** Select one term for each thing. Do not use synonyms. Write
   `make sure`, not `verify`, `check`, `confirm`, or `ensure`. (Rules 1.1, 1.3, 1.11, 9.4)
2. **One part of speech for each word.** `test` is a noun. Write `do a test`, not `to test`.
   (Rules 1.2, 1.7, 1.13)
3. **Simple tenses only.** Use the infinitive, the imperative, the simple present, the simple
   past, the simple future, and the past participle as an adjective. Write `we received the report`,
   not `we have received the report`. (Rules 3.1, 3.2, 3.3)
4. **No complex verb constructions.** Do not stack auxiliary verbs. (Rule 3.4)
5. **No "-ing" verb forms.** An "-ing" word is permitted only as a technical noun, or as part of
   one. `The bearing is dry` is correct. `Removing the bolt takes time` is not correct. (Rule 3.5)
6. **Active voice.** Procedures must always use the active voice. Descriptions can use the passive
   voice only when the agent is unknown. (Rule 3.6)
7. **A verb for an action.** Write `Inspect the valve`, not `Do an inspection of the valve`.
   (Rule 3.7)
8. **Three nouns maximum in a multi-word noun.** Break longer clusters with `of` or `for`, or give
   the thing a short name. (Rules 2.1, 2.2)
9. **Do not remove words to shorten a sentence.** Keep the subject, the verb, and the article. Do
   not use contractions. Split the sentence instead. (Rules 4.2, 4.5)
10. **No semicolons.** Every other standard punctuation mark is permitted. Write two sentences.
    (Rule 8.1)
11. **No phrasal verbs.** Write `assemble`, not `put together`. Write `start`, not `set up`.
    (Rule 9.3)
12. **A vertical list for complex text.** A list is clearer than a long sentence with many clauses.
    (Rule 4.3)

## Core rewrite rules

STE's rules divide into two kinds, and this skill can only fully deliver one of them. **Structural
rules** are self-contained: they describe sentence shape, and you can apply them from the
description alone. **Lexical rules** are defined entirely by the official ~900-word dictionary,
which this skill deliberately does not reproduce. Without that dictionary, the lexical rules
degrade from a checkable standard into a preference for plain words.

Apply the structural rules with confidence. Apply the lexical rules as a direction of travel, and
say so in your output rather than implying dictionary compliance you cannot verify.

### Structural rules — apply these

| Rule | Do | Don't |
|---|---|---|
| Active voice | "The agent deletes the file." | "The file is deleted (by the agent)." — unless the actor is genuinely unknown or irrelevant |
| No phrasal verbs (Rule 9.3) | "Remove the panel." / "Start the job." | "Take off the panel." / "Spin up the job." — a two-word verb has meanings the parts do not predict |
| One instruction per sentence | "Open the file. Read line 3." | "Open the file and read line 3, then check if it matches." |
| Sentence length | ≤20 words for instructions/procedures, ≤25 words for descriptions | Long compound or subordinate-clause sentences |
| No semicolons (Rule 8.1) | Split into separate sentences | Any semicolon at all — STE bans the mark outright, not only as a clause join. Rule 8.1 permits every other standard punctuation mark; the em dash is *not* banned by STE, though it often signals a sentence that should be split. |
| Noun clusters | ≤3 words stacked as a noun phrase ("fuel pump valve") | 4+ word noun stacks ("high pressure fuel pump inlet valve assembly") |
| No ellipsis | Keep the subject, verb, and article explicit even if it reads longer | Drop words to save space ("Files not backed up will be lost" → ambiguous which files) |
| Keep modality | "The request **may have** failed." stays "may have" | Promote a hedge to a fact ("The request failed.") or invent a certainty the source did not state |
| Paragraph limits | One topic per paragraph, ≤6 sentences | Multi-topic paragraphs |
| Lists for sequences | Use a numbered or bulleted list for 3+ steps or conditions | Bury a sequence inside one prose sentence |

### Lexical rules — direction of travel only

| Rule | Do | Don't | Why it is weaker here |
|---|---|---|---|
| One word, one meaning | Pick one verb for one action and reuse it every time (e.g. always "check", never mix "check"/"verify"/"confirm") | Rotate synonyms for the same idea across a document | Consistency within a document is checkable. Which word is the *approved* one is not, without the dictionary. |
| One part of speech per word | "Apply oil to the valve" (oil = noun) | "Oil the valve" (oil = verb) | Whether "oil" is approved as a noun only is a dictionary fact. Prefer the noun form when both read equally well; do not claim compliance. |
| Verb, not noun (Rule 3.7) | "Analyze the log." | "Perform an analysis of the log." — a noun form of an action makes the sentence longer and hides who acts | Rule 3.7 says "use an **approved** verb to describe an action." Preferring the verb form is safe to apply anywhere; knowing which verb is the approved one needs the dictionary. |
| Domain terms | Keep necessary technical nouns/verbs, but define them once if not common English (STE allows a project-specific glossary beyond its base dictionary) | Use jargon without ever defining it | The glossary allowance is real STE, but the base dictionary it extends is absent. |

### Simple tenses — apply with one exception

STE permits infinitive, imperative, simple present, simple past, simple future, and past participle
as adjective. It excludes present perfect and other compound forms: "we received the report", not
"we have received the report".

Aircraft manuals never need present perfect, so the exclusion costs the standard nothing. Other text
is not always so lucky. "The job has completed" (and its output is available now) and "the job
completed" (at some past point) are different statements, and status text frequently needs the
first. **Where the compound form carries information the simple form cannot — current relevance, or
a hedge as in "may have failed" — keep it and flag the departure.** Elsewhere, follow the rule.

## Scan checklist

These six habits cover most of what makes machine-written English hard to parse. Each one is
mechanical: you can point at the exact word or punctuation mark that breaks the rule, with no
judgment call. Scan for all six before you rewrite anything.

1. **Synonym rotation** — the same thing gets several names in one document ("the user", "the
   customer", "the client"). The reader cannot tell whether they are one thing or three. Fix: pick
   one name, use it every time.
2. **Hedge stacking** — helper verbs and qualifiers pile up until the sentence asserts nothing
   ("it is important to note that this may potentially help to improve"). Fix: state the claim, or
   delete it.
3. **Nominalization** — an action frozen into a noun ("perform an analysis of", "provides assistance
   to"). Fix: use the verb ("analyze", "helps").
4. **Marketing adjectives** — words that claim quality instead of showing it: seamless, robust,
   powerful, cutting-edge, effortless, blazing-fast. Fix: delete, or replace with the measurement
   that earns the claim.
5. **Run-on sentences** — several ideas joined by semicolons or em dashes. Fix: one idea per
   sentence.
6. **Soft phrasal verbs** — spin up, reach out, dive into, kick off. Fix: use the single plain verb
   (start, contact, read, begin).

## Step 3 — rewrite, do not substitute word for word

A word-for-word replacement often fails. Change the construction of the sentence. (Rule 9.1)

Before, 34 words with a semicolon, a phrasal verb, and a gerund:

> Before configuring the client, you'll want to grab the API key from the dashboard; you can find it
> under Settings, which is where most of the credentials are kept.

After, three instructions, each under 20 words:

> 1. Open the Settings page of the dashboard.
> 2. Get the API key.
> 3. Configure the client with this key.

More worked examples are in [references/examples.md](references/examples.md).

**Check modality before you commit to a rewrite.** Hedges ("may", "could", "sometimes", "is likely
to") carry the author's confidence, and confidence is content. A shorter sentence that upgrades a
hedge to a fact is not a simplification — it is a different claim. This is the most common way a
well-intentioned STE rewrite goes wrong, because hedges are exactly what a length cap tempts you to
cut. When the tense rule and the modality rule conflict, modality wins.

Never add a fact the source did not state. A rewrite that reads better because it supplies a cause,
a frequency, or a mechanism has stopped being a rewrite.

## Step 4 — check the result

Run the checker on the file:

```bash
python3 scripts/ste_check.py --mode descriptive path/to/file.md
python3 scripts/ste_check.py --mode procedural --max-words 20 path/to/file.md
```

The script applies the word-count rules of Section 8. Text in parentheses counts as one word. A
hyphenated word counts as one word. In a vertical list, a colon ends a sentence. (Rules 8.4–8.7)

The script reports these problems:

- A sentence that is too long for the chosen mode
- A semicolon or a contraction
- The present perfect tense and other complex verb forms
- The passive voice
- An "-ing" form not registered as a technical noun
- A multi-word noun of more than three nouns
- A phrasal verb from a known list
- A Latin abbreviation, an ampersand, and `(s)` for a plural
- A wordy phrase and a common unapproved synonym

The script cannot check the dictionary. It has no part-of-speech analysis. Read the output as help,
not as proof of conformance.

## Step 5 — report the limits of your work

Always tell the user two things:

- Which rules you applied.
- Which rules you could not apply, and why. The dictionary is the usual reason.

## Output format

**Default: the rewritten text, and nothing else.** Most callers want a result they can paste
straight into a tool description, an error string, or a prompt. Print the simplified text on its
own. Do not add a preamble about this skill, a mode announcement, a violation count, a summary of
what changed, a rule table, or a closing offer to explain further.

The one permitted addition: if a longer phrasing was kept on purpose, add a single line after the
text, prefixed `Kept as-is:`, naming the phrase and the precision that would have been lost. Omit
the line when there is nothing to report.

**On request: the rule table.** When the user asks to see the reasoning — "show the diff", "which
rules did it break", "explain the changes", "before/after" — output this table instead:

```markdown
| Rule violated | Original | Simplified |
|---|---|---|
| Present perfect tense | "We have received your request." | "We received your request." |
| Noun cluster (4+ words) | "the agent task queue priority handler" | "the handler that sets task-queue priority" |

Mode: Strict. 7 violations found.
```

Follow the table with a one-line note on anything deliberately not simplified, and why (usually:
simplifying would lose required precision).

## Process

1. Pick the mode (Strict or STE-flavored). Say which only when the user asked for the rule table —
   see Output Format.
2. Read the input text once for meaning — do not start rewriting before you understand what it
   must still say afterward.
3. Walk it sentence by sentence. Flag every rule violation from the Core Rewrite Rules tables and
   every habit from the Scan Checklist. In STE-flavored mode, flag the lexical rules but do not
   enforce them.
4. Rewrite each flagged sentence to fix the violation while preserving the original meaning
   exactly. If a rewrite would drop necessary precision (a safety condition, a scope qualifier, a
   number), keep the longer phrasing and flag it instead of silently simplifying.
5. Output the rewritten text (see Output Format). Keep the mode choice and the rule analysis
   internal unless the user asked to see them.
6. If the input already complies, say so — do not force changes onto compliant text.

## Edge cases

**Code, identifiers, and file paths.** Do not change them. Keep them in backticks. They are
technical nouns. The word-count rules count each one as one word.

**Product names and error strings.** Do not change them, even when they break a rule. Quote the
exact string. Add an STE sentence that explains the string.

**Tables and headings.** The sentence limits are for sentences. A table cell or a heading is not a
sentence. Keep both short.

**Safety text.** Put the risk word first: `WARNING` for a risk to a person, `CAUTION` for a risk
to equipment. Then give the command or the condition. Then explain the result. (Rules 7.1, 7.2,
7.3) Place the safety instruction in front of the step it protects. Never after.

**Marketing text.** STE is not for marketing text. Tell the user this. Write the technical parts
in STE, and leave the marketing parts alone.

**Text that must stay long.** A legal sentence or a quoted standard can be too long. Keep it. Mark
it as a quotation. Do not report it as an error.

**A text with no content.** STE makes empty text short and clean. It does not make it useful. If
the source text says nothing, tell the user.

## Boundaries

**Will:**
- Rewrite ambiguous or dense English into short, single-meaning, active-voice sentences.
- Return the rewritten text alone by default, and name the rules it applied when the user asks.
- Preserve every fact, condition, and scope qualifier in the original.
- Preserve the strength of every hedge, and add no claim the source did not make.
- Suggest a one-line glossary entry for domain terms that must stay.

**Will not:**
- Reproduce ASD's official ~900-word dictionary as if it were memorized verbatim — always treat the
  official download as the source of truth for exact approved wording.
- Simplify creative, marketing, or persuasive copy where voice and nuance are the point.
- Silently drop a safety condition, exception, or scope qualifier to shorten a sentence — it will
  flag the trade-off instead.
- Convert "may have failed" into "failed", or "could be caused by X" into "X is the cause" — losing
  a hedge changes the claim.
- Guarantee an aerospace/defense-grade STE-compliant document; this is a general-purpose clarity
  tool inspired by STE, not a certified STE authoring tool.
- Make weak content true or useful. STE fixes the *form* of a text, not its substance. A hollow
  paragraph rewritten under these rules becomes a clean, short, well-punctuated hollow paragraph.
  If the text has nothing to say, no rewrite fixes that — say so instead of polishing it.
- Shorten past the point of clarity. Cutting words is not the goal; removing ambiguity is. Past a
  certain point compression starts costing the reader time rather than saving it, so stop when the
  sentence is unambiguous, not when it is shortest.

## References

- [references/writing-rules.md](references/writing-rules.md) — all 53 rules, with numbers (Issue 9,
  January 2025), plus GR-1..GR-8 grammar guidance
- [references/word-substitutions.md](references/word-substitutions.md) — unapproved word to approved
  word, including the phrasal-verb list
- [references/examples.md](references/examples.md) — before and after, for software text and
  agent-output text, with rule citations
- [scripts/ste_check.py](scripts/ste_check.py) — the checker (stdlib only, Python 3.9+)
- [NOTICE](NOTICE) and [LICENSE](LICENSE) — licensing boundary with ASD
- [examples/before-after.md](examples/before-after.md) — additional agent-output examples
  (tool description, error message, inter-agent instruction, README)
