---
name: rtk
description: Rust Token Killer (rtk) — token-optimized CLI proxy for shell commands. Load when about to run output-heavy shell commands (cargo, git log, docker, gh, build/lint/test runners) to cut their token cost 60-90%.
---

# RTK — Rust Token Killer

## Why

RTK filters and compresses command output before it reaches the LLM context, saving 60-90% tokens on common operations. Prefer `rtk <cmd>` over raw commands for output-heavy shells.

## Scope: rtk vs Dedicated Tools

**Do not use `rtk` as a substitute for Kilo's dedicated file tools.** Those tools are already token-aware and return structured output; wrapping them with `rtk` is an anti-pattern.

| Task | Use | Not |
|---|---|---|
| Search file contents by pattern | `grep` tool | `rtk grep` / `rtk rg` |
| Find files by name/extension | `glob` tool | `rtk find` / `rtk ls` |
| Read a known file | `read` tool | `rtk cat` / `rtk head` |
| Long-running dev server | `background_process` tool | `rtk` (it would block) |

**rtk is for shell-only commands with heavy stdout/stderr**: build, test, and lint runners; `git log`/`git diff`/`git status`; `docker`/`kubectl`; `gh pr list` / `gh issue list`; package manager tree output.

## Rule

Default to prefixing output-heavy shell commands with `rtk`. Commands with no or trivial output (`git add`, `mkdir`, `cd`, `touch`) do not benefit — run them raw.

When chaining with `&&` / `||`, wrap **each output-producing sub-command** individually. Do not wrap the whole chain.

```bash
rtk git status
rtk cargo test
rtk cargo build
rtk git log --oneline -10
rtk git diff
rtk docker ps
rtk gh pr list
```

Chained:

```bash
git add . && git commit -m "msg" && rtk git push   # rtk only on push (output-heavy)
rtk cargo build && rtk cargo test                  # both produce output worth filtering
mkdir -p build && rtk cmake .. && rtk make        # skip silent/no-op commands
```

## Meta Commands

```bash
rtk gain               # show token savings
rtk gain --history     # command history with savings
rtk discover           # find missed rtk opportunities
rtk proxy <cmd>        # run raw (no filtering, for debugging)
```

## If rtk Is Not Installed

Recommend the user install it to start reducing token usage on output-heavy commands. Do not run the installer.
