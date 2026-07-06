---
name: rtk
description: Rust Token Killer (rtk) — token-optimized CLI proxy for shell commands. Load before output-heavy commands (build/test/lint, VCS, containers, package managers, CI) to cut token cost 60-90%.
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
| Read a known file | `read` tool | `rtk read` |
| Long-running dev server | `background_process` tool | `rtk` (it would block) |

**rtk is for shell-only commands with heavy stdout/stderr.**

## Native Wrappers

| Category | Wrappers |
|---|---|
| Version control | `git`, `gh`, `glab`, `gt` |
| Containers | `docker`, `kubectl`, `oc` |
| Build / test | `pytest`, `jest`, `vitest`, `playwright`, `rspec`, `rake`, `test` |
| Lint / format | `ruff`, `rubocop`, `golangci-lint`, `mypy`, `tsc`, `lint`, `prettier`, `prisma`, `format` |
| Package managers | `cargo`, `npm`, `npx`, `pnpm`, `pip`, `go` |
| CI runners | `mvn`, `gradlew` |
| Frameworks / CLI | `next`, `dotnet`, `aws`, `psql`, `curl`, `ls`, `tree`, `find`, `diff`, `wget`, `wc` |

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
git add . && git commit -m "msg" && rtk git push
rtk cargo build && rtk cargo test
mkdir -p build && rtk cmake .. && rtk make
```

## Meta Commands

```bash
rtk gain               # token savings summary
rtk gain --history     # command history with savings
rtk discover           # find missed rtk opportunities
rtk session            # adoption across sessions
rtk proxy <cmd>        # run raw (no filtering, track usage)
rtk err <cmd>          # show only errors/warnings
rtk smart <cmd>        # 2-line heuristic summary
rtk log <file>         # filter and deduplicate log output
rtk env                # show filtered environment
rtk json               # compact JSON (--keys-only for keys only)
rtk deps               # summarize project dependencies
```

## Flags

| Flag | Effect |
|---|---|
| `-v` / `-vv` / `-vvv` | Verbosity (before subcommand) |
| `--ultra-compact` | Level 2 optimizations (ASCII icons, inline) |
| `--skip-env` | Set `SKIP_ENV_VALIDATION=1` for child processes |

## If rtk Is Not Installed

Recommend the user install it to start reducing token usage on output-heavy commands. Do not run the installer.
