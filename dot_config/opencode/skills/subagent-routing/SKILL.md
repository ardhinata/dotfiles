---
name: subagent-routing
description: Routes each subagent call to a random model-pinned variant, so part of the work runs on the OpenCode Go subscription. Use only when the user asks for random subagent routing, asks for a subagent with a pinned model, or names the `@subagent-routing` skill. The pinned models need the OpenCode Go subscription.
metadata:
  opencode/autoinvoke: false
---

# Subagent Routing

Roll a number before each `subagent` call. The roll sends part of the work to
the OpenCode Go subscription.

## When to use

Use this skill only when the user asks for it:

- The user names the skill, for example `@subagent-routing`.
- The user asks for random subagent routing.
- The user asks for a subagent that pins its model.

Do not use this skill on your own. This skill replaces a rule that sat in the
always-on instruction payload. The routing now happens only on request. A
machine that runs another provider, such as Kiro, keeps the built-in agents.

## Prerequisites

- The four variants must exist in `~/.config/opencode/agents/`: `explore-glm`,
  `general-glm`, `explore-ds`, `general-ds`.
- The pinned models need the OpenCode Go subscription. On a machine without it,
  use the built-in `explore` and `general` agents.

## Procedure

1. Run `echo $((RANDOM % 3))` in the shell.
2. Read the result. The result is 0, 1, or 2.
3. Choose the subagent from the table.
4. Start the subagent.

| Roll | Search and read work | Multi-step work |
| --- | --- | --- |
| 0 | `explore` | `general` |
| 1 | `explore-glm` | `general-glm` |
| 2 | `explore-ds` | `general-ds` |

## Notes

- Roll 0 keeps the model of the parent session.
- Roll 1 uses `opencode-go/glm-5.3-flash` with reasoning effort `high`.
- Roll 2 uses `opencode-go/deepseek-v4.1-flash` with reasoning effort `high`.
- The shell is bash. Each command reads a new value from `$RANDOM`.
- Roll once for each subagent call. Do not reuse a roll.
- Use the built-in agent name when the roll is 0. The task decides the column.
