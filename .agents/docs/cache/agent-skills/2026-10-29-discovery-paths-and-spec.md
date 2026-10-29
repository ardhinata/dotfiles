# Agent Skills — Discovery Paths and the Specification

Verified 2026-10-29 against the vendor docs and the specification site. Every
row links to the page it came from.

## Where each harness looks for skills

| Harness | Project paths | User paths | `.agents/skills/` native? |
|---|---|---|---|
| OpenCode | `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | Yes, both levels |
| Codex CLI | `.agents/skills` from CWD to repo root | `$HOME/.agents/skills` | Yes, both levels |
| Cursor | `.agents/skills/`, `.cursor/skills/`, `.claude/skills/`, `.codex/skills/` | the same four under `~` | Yes, both levels |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` | Yes, the `.agents` alias wins |
| Zed | `<worktree>/.agents/skills/` | `~/.agents/skills/` | Yes, trusted worktrees only |
| goose | `.agents/skills/` | `~/.agents/skills/` | Yes, both levels |
| Amp | `.agents/skills/` and parent dirs | `~/.agents/skills/` | Yes, unless `amp.skills.disableGlobalAgentsSkills` |
| Warp | `.agents/skills/` (recommended) and nine vendor dirs | `~/.agents/skills/` (recommended) and nine vendor dirs | Yes, both levels |
| GitHub Copilot | `.github/skills`, `.claude/skills`, `.agents/skills` | `~/.copilot/skills`, `~/.agents/skills` | CLI, app and cloud agent only. Not the VS Code harness |
| Factory Droid | `~/.factory/skills/` native, `.agents/skills/**` compatibility | same | Compatibility path, not native |
| Claude Code | `.claude/skills/` only | `~/.claude/skills/` only | No |
| Aider | — | — | No official documentation. Do not claim it |

Sources: [OpenCode](https://opencode.ai/docs/skills/), [Codex](https://developers.openai.com/codex/skills.md),
[Cursor](https://cursor.com/help/customization/skills), [Gemini CLI](https://geminicli.com/docs/cli/skills/),
[Zed](https://zed.dev/docs/ai/skills), [goose](https://goose-docs.ai/docs/guides/context-engineering/using-skills),
[Amp](https://ampcode.com/docs/customize/skills), [Warp](https://docs.warp.dev/agents/capabilities/skills/),
[GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills),
[VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills),
[Factory Droid](https://docs.factory.ai/harness/skills), [Claude Code](https://code.claude.com/docs/en/skills).

## The convention is not a spec requirement

The [client-implementation guide](https://raw.githubusercontent.com/agentskills/agentskills/main/docs/client-implementation/adding-skills-support.mdx)
says it plainly: "the Agent Skills specification does not mandate where skill
directories live". `.agents/skills/` is a cross-client convention that the
spec blesses by describing it.

## Claude Code needs a symlink per skill folder

Claude Code documents a symlinked **skill folder**: a `<skill-name>` entry in
`.claude/skills/` may be a symlink to a directory elsewhere. A symlink of the
whole `.claude/skills` directory is **not** documented. Prefer one symlink per
skill. A skill folder can also become a plugin by adding
`.claude-plugin/plugin.json`.

## The specification

Canonical spec: <https://agentskills.io/specification>. Canonical repository:
<https://github.com/agentskills/agentskills> (Apache-2.0). The spec defines
exactly six frontmatter fields.

| Field | Required | Constraint |
|---|---|---|
| `name` | Yes | 1–64 chars. Lowercase letters, digits and hyphens. Must match the parent directory name. No leading or trailing hyphen. No `--` |
| `description` | Yes | 1–1024 chars. Non-empty. Describes what the skill does and when to use it |
| `license` | No | License name or a reference to a bundled file |
| `compatibility` | No | 1–500 chars |
| `metadata` | No | Map from string keys to string values |
| `allowed-tools` | No | Space-separated string. Experimental |

OpenCode enforces the name with the regex `^[a-z0-9]+(-[a-z0-9]+)*$`.

Progressive disclosure, verbatim from the spec:

1. **Metadata** (~100 tokens) — the `name` and `description` fields, loaded at startup for all skills.
2. **Instructions** (< 5000 tokens recommended) — the full `SKILL.md` body, loaded when the skill activates.
3. **Resources** (as needed) — files in `scripts/`, `references/` or `assets/`, loaded only when required.

The spec also says: "Keep your main `SKILL.md` under 500 lines."

## `skills-ref`

The validator lives in the spec repository at `skills-ref/`. It is a Python
package, not a preinstalled binary and not an `npx` package. Install it with
`pip install -e .` or `uv sync` from a clone of the repository. Commands:
`skills-ref validate <dir>`, `skills-ref read-properties <dir>`,
`skills-ref to-prompt <dir-a> <dir-b>`.

Its README says it "is intended for demonstration purposes only. It is not
meant to be used in production." Treat a clean run as a floor.

## Claude-only rules are not spec rules

Third-person `description`, no XML tags in `name` or `description`, and no
reserved words `anthropic` or `claude` in `name` come from the
[Claude best-practices page](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices),
not from the specification. Cite them as Claude rules.

## OpenCode does not expand `@file` in AGENTS.md

Verified in the [OpenCode rules docs](https://opencode.ai/docs/rules/): "While
opencode does not automatically parse file references in `AGENTS.md`". The
documented workarounds are the `instructions` array in `opencode.json`, and
teaching the agent in `AGENTS.md` to read the referenced file on demand. The
`instructions` field takes a path or a glob. `~` expansion works in practice
but is not documented.

## Freshness

The specification moved fast in 2026: the agentskills.io site, the Claude
best-practices page and the harness docs all changed within months. Re-verify
any field limit or scan path before relying on it.
