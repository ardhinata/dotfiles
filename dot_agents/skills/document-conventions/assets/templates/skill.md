# SKILL.md Template

Copy to `~/.agents/skills/<slug>/SKILL.md`. **Frontmatter
required** per the [agentskills.io specification](https://agentskills.io/specification).
Validate with `skills-ref validate ./<skill-dir>` before publishing.

```markdown
---
name: <skill-slug>
description: <what the skill does>. Use when <triggers>. <key terms agents will search for>.
license: <optional, e.g. Apache-2.0>
compatibility: <optional, max 500 chars, environment requirements>
metadata: <optional, string keys to string values>
allowed-tools: <optional, space-separated, e.g. Bash(git:*) Read>
---

# <Skill Name>

<one-line summary, no heading>

## When to load

<Trigger conditions. State the user's tasks that should activate this
skill. Be specific.>

## Quick start

<Minimal worked example or the most common path.>

## Workflow

<Step-by-step procedure. Numbered list. Include decision points and
fallback paths.>

### <Sub-step 1>

<details>

### <Sub-step 2>

<details>

## Examples

<2–4 input/output pairs or before/after diffs.>

## Edge cases

<Known edge cases, error modes, and how to handle them.>

## Anti-patterns

- <thing to avoid 1>
- <thing to avoid 2>

## References

- [reference-1.md](references/reference-1.md) — load when <trigger>
- [reference-2.md](references/reference-2.md) — load when <trigger>
- <external source URL>
```

**Length:** under 500 lines. Push detail into `references/*.md` when
the body grows.

**Frontmatter requirements:**

- `name` — matches the parent dir. Lowercase letters, digits and hyphens,
  1–64 chars, no `--`, no leading or trailing hyphen
- `description` — third person, 1–1024 chars, names both *what* and
  *when*, includes the keywords agents search for
- `metadata` — a map from string keys to string values
- `allowed-tools` — a space-separated string of tool names
- No XML tags in `name` or `description`, and no reserved words
  `anthropic` or `claude` in `name` (Claude's rules, the spec is silent)

**Skill directory layout:**

```
<skill-slug>/
├── SKILL.md              # this file
├── references/           # optional, loaded on demand
│   ├── reference-1.md
│   └── reference-2.md
├── scripts/              # optional, executed not loaded
│   └── helper.py
└── assets/               # optional, static resources
    └── template.md
```

**Verification:**

```bash
skills-ref validate ./<skill-slug>
```

`skills-ref` is a Python package in the
[agentskills repository](https://github.com/agentskills/agentskills/tree/main/skills-ref).
Install it with `pip install -e .` or `uv sync` from a clone of that
repository. Its own README says it is for demonstration only, so treat a
clean run as a floor, not a proof.

Manual review against [`../checklists.md`](../checklists.md) and
[`../../references/anti-patterns.md`](../../references/anti-patterns.md).