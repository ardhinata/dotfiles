# Knowledge Cache

Date-tagged, reusable facts learned from web research in this project. Read
this index before external research, so a fact that is already known is not
fetched again.

## Convention

- **Path:** `.agents/docs/cache/<topic>/YYYY-MM-DD-<short-slug>.md` — one
  topic per file, ISO date prefix sorts chronologically.
- **Index:** this file links every topic; each topic's `README.md` links every
  entry with its date, source, and freshness note.
- **Scope:** only persistent, reusable, volatile facts belong here. One-off
  answers, scratchpads, and transient work go in `.tmp/`.
- **Re-verify:** CLI tool and framework APIs are volatile — re-verify if the
  entry is more than 6 months old, or if the domain has had a major release.

## Cache policy

The cache subtree is **tracked in git**. The entries are curated and small,
and tracking them means a fresh clone can answer a question without a web
fetch. Three rules keep that safe:

1. An entry earns its place only when it states a fact that is still true and
   still useful. Anything about a removed tool, a moved path, or a dismissed
   design gets pruned, not archived.
2. The cache never holds a secret. Scan the tracked set for tokens and keys
   before every commit that touches it.
3. The cache is never deployed. The repo-root `.agents/` tree is project scope
   and does not reach `$HOME`, so a tracked entry cannot leak into a target
   machine through chezmoi.

Fresh research lands in the cache and is pruned into the tracked set when it
is verified. A finding that also changes behaviour belongs in the matching
skill or rule file, with the cache entry as the evidence behind it.

## Topics

| Topic | Description | Entries |
|---|---|---|
| [agent-instructions](agent-instructions/README.md) | Cost and load-path facts about the always-on instruction files | 2 |
| [asd-ste100](asd-ste100/README.md) | The upstream ASD-STE100 checker: capabilities and install path | 1 |
| [document-conventions](document-conventions/README.md) | Which document rules are standard, and which citations were wrong | 1 |
| [opencode-harness](opencode-harness/README.md) | How the OpenCode harness and its plugins behave | 2 |
| [pinentry](pinentry/README.md) | gpg-agent's pinentry extension point and the wrapper pattern | 1 |
| [ssh](ssh/README.md) | Reusable SSH client facts for this host | 1 |

## Related

- `.help/` — legacy project knowledge cache (chezmoi + sprig docs, quirks, doc
  index). See `.help/README.md`.
- `~/.agents/rules/web-verification.md` — global web-tool selection and
  cache-use policy.
