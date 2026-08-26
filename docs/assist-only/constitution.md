# Project constitution — assist-only mode

**Status:** drafting (seed template — fill, then lock)
**Last reviewed:** <YYYY-MM-DD>

This constitution is the source of truth that every spec-kit phase transitions against. The agent must re-read it at every phase transition; the user owns the edits.

## How to use this file

1. Read every numbered principle.
2. Replace each placeholder with a concrete commitment.
3. Add or remove principles as the project requires; aim for 5–8.
4. The **Testing bar** and **Stack allow/deny** sections are non-negotiable — every spec and plan inherits from them.
5. Once you stop editing, mark `**Status:** locked` so the agent treats it as authoritative.

## Principles

### 1. <principle name>

> <one sentence: the rule>

**Applies to:** <which surfaces — code, docs, infra, process>

### 2. <principle name>

> <one sentence>

**Applies to:** <surfaces>

### 3. <principle name>

> <one sentence>

**Applies to:** <surfaces>

## Testing bar

- **Unit tests:** <required / recommended / spec-driven>
- **Integration tests:** <scope and requirement>
- **Smoke tests:** <who runs them, when>
- **Coverage target:** <number, with reasoning — do not pull a number from the air>

## Stack allow / deny

| Category | Allowed | Forbidden | Reason |
|---|---|---|---|
| Language | <e.g. Python 3.12+> | <e.g. Python 2> | <one sentence> |
| Runtime | <e.g. CPython 3.12.x> | <e.g. PyPy> | <one sentence> |
| Test framework | <e.g. pytest> | <e.g. unittest> | <one sentence> |
| Package manager | <e.g. uv> | <e.g. pip-tools> | <one sentence> |
| Database | <e.g. Postgres 16> | <e.g. MySQL> | <one sentence> |
| CI / CD | <e.g. GitHub Actions> | <e.g. Travis> | <one sentence> |

## Locking

When this file's `**Status:**` flips from `drafting` to `locked`:

- All subsequent spec and plan artifacts must cite a principle number or a stack row when they make a non-obvious choice.
- The agent may still challenge locked principles, but any change requires a written acknowledgement with a migration plan.
- A locked constitution is the gate at every `clarify → plan` transition.

## See also

- [spec-kit skill](../../dot_config/kilo/exact_skills/spec-kit/SKILL.md) — phase order and gate questions.
- assist-only mode file — production-boundary rule and anti-assumption protocol.
- Specs index — `docs/assist-only/specs/README.md`.
