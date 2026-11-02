# Subagent Routing

Roll a number before each `subagent` call. The roll sends part of the work to
the OpenCode Go subscription.

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
