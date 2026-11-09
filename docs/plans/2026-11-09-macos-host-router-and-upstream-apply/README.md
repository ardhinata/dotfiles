---
status: draft
goal: Make the macOS work laptop use the upstream dotfiles with the host-local secrets and the PATH order intact
owner: ardhinata
last-updated: 2026-11-09
---

# Correct dotfiles for the macOS work laptop

The upstream `origin/main` branch changes the shell startup chain and the
OpenCode config. This plan makes the macOS work laptop take those changes
without losing the host-local API tokens. The `shellx` helper must keep
working. The host-local shell preferences must survive.

The plan also adds a hostname router. A future host difference then has one
place to go, instead of a new `if` in every template.

## Index

| File | Contents |
|---|---|
| [01-findings.md](01-findings.md) | The six defects in the upstream tree, each with the measurement that proves it |
| [02-design.md](02-design.md) | The three layers: presence-based dispatch, the hostname router, and the OS axis. The corrected `path.sh` |
| [03-implementation.md](03-implementation.md) | The four phases, the risks, the verification list, the open questions and the decisions |

## Scope

- In: the four upstream commits, the `~/.zshenv` and `~/.bashrc` targets,
  the PATH order on macOS, the OpenCode `cli.json` keys, and the
  systemd-only `environment.d` directory.
- Out: the nonce rotation, the shellx store format, the encryption keys,
  and the Linux host.

## Existing constraints

- The owner banned `chezmoi apply` after the 2026-11-09 incident. Every
  change goes in through `chezmoi diff` and `chezmoi cat`.
- The repo is public. A secret value must not go into a tracked file.
- `~/.shell/.zshenv` holds the only copy of the Jira and Bitbucket tokens.
  The live `~/.zshenv` is a relative symlink to that file.
- The work laptop hostname is `IKM202300278`. `chezmoi` reports the name up
  to the first dot.

## What the upstream change does

| Commit | Change |
|---|---|
| `58573f4` | Add `dot_zshenv`, `dot_shell/env/path.sh`, `dot_config/environment.d/10-shell-env.conf` and `dot_bashrc`. Move the PATH out of `dot_shell/zsh/10-common-export.zsh` |
| `c2dd534` | Replace the `@upstash/context7-opencode` plugin with a disabled `context7` remote MCP server. Add `opencode-orchestrator@latest` |
| `0101746`, `5cdb0f0` | Add three reports. Rename the Zed font families |

## Executive summary

The upstream tree breaks this host in four ways. The `~/.zshenv` symlink
becomes a regular file, so the API tokens stop loading. The helper
directory lands behind `/usr/bin`, so the `shellx` helper runs on Python 3.9
and crashes. The `environment.d` file is a systemd mechanism that macOS
ignores. The `~/.bashrc` and the OpenCode `cli.json` lose host-local
content.

Two upstream config changes are safe. The `context7` remote MCP server is
schema valid, and the Zed font families are installed.

The design uses three layers. A repo file sources a host-local file when
that file exists. A hostname router renders the content that the repo must
render itself. The OS axis covers the platform facts.

## Current status

The agent measured the findings. The sandbox home
`/private/var/folders/sb/yh9r4cqx0jdcc7ml6lwccp2m0000gn/T/opencode/om-sim`
holds the upstream tree and the candidate `path.sh`. The upstream worktree
sits at `/private/var/folders/sb/yh9r4cqx0jdcc7ml6lwccp2m0000gn/T/opencode/om-main`.
