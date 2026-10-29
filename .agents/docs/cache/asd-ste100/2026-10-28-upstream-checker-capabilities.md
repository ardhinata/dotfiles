---
source:
  - https://github.com/sourdough-bread/asd-ste100-checker
captured: 2026-10-28
freshness: check-2027-04
tags: [asd-ste100, tooling, ste100]
---

# The upstream ASD-STE100 checker: capabilities and install path

The upstream checker is worth adding as a second pass for the dictionary and
the part-of-speech rules, but it must not replace the local script.

Captured 2026-10-28 while deciding whether the home-made `asd-ste100` skill
should use the local checker script or
[github.com/sourdough-bread/asd-ste100-checker](https://github.com/sourdough-bread/asd-ste100-checker).

## Finding

The upstream project is a Python package with a CLI, an MCP server and an LSP
server. It has no Markdown support and it does not implement six rule
families the local script covers.

## Evidence

**The package is not on PyPI.** `https://pypi.org/pypi/asd-ste100-checker/json`
and `https://pypi.org/pypi/ste100/json` both return HTTP 404. Upstream's own
README command, `uvx --from asd-ste100-checker ste100 setup`, therefore fails.
There are no release tags, so a commit sha is the only pinnable reference.

```bash
uv tool install "asd-ste100-checker @ git+https://github.com/sourdough-bread/asd-ste100-checker@e193ecdd66b09ce81b7c611f1c841efd8ba84cc7"
```

**`ste100 setup` fails too.** It runs `python -m spacy download`, and spaCy's
downloader calls `uv pip` without an active virtual environment:
`error: No virtual environment found`. Install the model wheel into the tool
environment instead:

```bash
uv pip install --python ~/.local/share/uv/tools/asd-ste100-checker/bin/python \
  "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"
```

The model comes from a GitHub release, not from PyPI. After this,
`ste100 doctor` reports `spacy_model_load: ok`.

**The model is mandatory for `check`.** `analyze()` calls `get_nlp()` at
`ste100/core/analyzer.py:152` with no try/except, so a missing model makes
`ste100 check` exit 2 with `error: analysis failed`. Only `lookup` and
`explain` work without it.

**The CLI shape.** `ste100 check [FILE] [--text-type auto|procedure|description]
[--output json|sarif] [--glossary PATH] [--spacy-model NAME] [--quiet]`. Exit
0 compliant, 1 not compliant, 2 error. Also `lookup`, `explain`,
`check-changed`, `doctor`, `setup`, `serve`, `lsp`.

Two traps:

- The FILE argument rejects `-`, because it is a `click.Path(exists=True)`.
  Pipe the text in with **no** file argument: `... | ste100 check`.
- `--text-type` takes `description`, not `descriptive`.

**Rule coverage against the local script.** Upstream registers 12 rule ids:
`STE-VOCAB-UNAPPROVED`, `STE-VOCAB-FORBIDDEN`, `STE-SENTENCE-LENGTH`,
`STE-ONE-INSTRUCTION`, `STE-UNITS-FORMAT`, `STE-PASSIVE`, `STE-IMPERATIVE`,
`STE-VERB-FORM`, `STE-NOUN-CLUSTER`, `STE-PRONOUN-AMBIG`, `STE-TOPIC-SENTENCE`,
`STE-POS-MISMATCH`.

Upstream has no rule for semicolons (8.1), contractions (4.2), phrasal verbs
(9.3), Latin abbreviations (GR-6), ampersands or `(s)` plurals (GESG), or wordy
phrases (9.1). The local script covers all of them, and it strips frontmatter,
code fences, tables and headings before it checks anything.

Upstream has what the local script cannot do: a dictionary of 2,152 Issue-9
headwords (851 approved, 1,301 unapproved) in
`ste100/dictionary/data/dictionary.json` (1.07 MB), 61 rule records in
`rules.json`, and part-of-speech analysis.

**Reading the output.** Measured on one 40-line rule file: 164 findings, of
which **123 had the status `not_in_dictionary`** — the word is simply absent
from the STE list, which is not a rule violation — and 28 had the status
`unapproved`, which is a real finding. The remaining 13 were grammar findings
(pronoun ambiguity, part of speech mismatch, verb form, sentence length).
Filter on the status.

The two checkers count words differently, so their sentence-length findings
disagree. The local script implements the STE word-count rules 8.5 to 8.7 and
owns that check.

**Upstream's own skill is not a drop-in.** `skill/SKILL.md` in the upstream
repo is 6,983 B against 19,968 B for the local one, and it is an MCP-only
playbook: it names 8 MCP tools that are not CLI commands.

## Why it matters

The upstream checker covers the two rule families the local script cannot
check, so it is a second pass and not a replacement. The install path has two
traps that cost an afternoon each if rediscovered.

## Scope

The upstream repo at commit `e193ecdd`. The `ste100` CLI at that commit.

## Uncertainty

Upstream has no release tags, so the commit sha is the only pin. The rule ids
and the dictionary size will change with upstream commits.

## Sources

- github.com/sourdough-bread/asd-ste100-checker at `e193ecdd`.
- PyPI JSON API for `asd-ste100-checker` and `ste100` (both HTTP 404).
- Live `ste100 doctor` and `ste100 check` runs on this host, 2026-10-28.

## See also

- `dot_agents/skills/asd-ste100/SKILL.md` — the skill that carries both passes
- `docs/plans/2026-10-28-agent-instruction-scope-and-ste-checker.md` — the
  plan this entry came from
