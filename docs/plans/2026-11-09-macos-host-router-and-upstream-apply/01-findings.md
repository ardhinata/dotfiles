# Findings

Six defects in the upstream `origin/main` tree, measured on the macOS work
laptop `IKM202300278`. Part of the plan to correct the dotfiles for that
host. See [README.md](README.md) for the index.

Every measurement below ran in a sandbox home with a controlled PATH. The
first attempt used the agent's inherited PATH, which put the helper at
position 13 for the wrong reason. The numbers here come from
`env -i` with PATH set to `/usr/bin:/bin:/usr/sbin:/sbin`.

## F1. The `~/.zshenv` symlink becomes a regular file

`chezmoi --source <worktree> diff` shows the deletion of the symlink and
then the creation of a regular file, with the mode change from `120755` to
`100644`. The token file survives the apply, but nothing sources it any
more. `JIRA_API_TOKEN` and `BITBUCKET_API_TOKEN` go empty in every new
shell.

## F2. The `shellx` helper is on PATH and broken

The helper runs `#!/usr/bin/env python3`. The first `python3` on PATH wins.
On this host `/usr/bin/python3` is 3.9.6 and `/opt/homebrew/bin/python3` is
3.15.2. The helper needs 3.10 or newer.

The upstream design puts the helper on PATH from `~/.zshenv`. macOS runs
`/etc/zprofile` after `~/.zshenv`, and `path_helper` rewrites PATH with the
system list first. The upstream `path.sh` leaves an entry alone when it
finds it in PATH, so the helper stays where `path_helper` put it.

The measured result, with the upstream tree in a sandbox home:

```text
$ zsh -c 'command -v python3'
/usr/bin/python3
$ shellx list
  File ".../shellx_key.py", line 124, in <module>
    def platform_store_read() -> str | None:
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

An interactive login shell fails the same way. `brew shellenv` moves
`/opt/homebrew/bin` to the front but leaves the helper behind `/usr/bin`, at
position 14.

This failure is new. Today the helper is not on PATH in a non-interactive
shell at all, so the helper is absent instead of broken. The upstream
change turns an absent helper into a broken one.

## F3. `environment.d` is a systemd mechanism

The upstream file header says that `systemd-environment-d-generator` reads
the file. macOS has no systemd, so the file does nothing there. The
`BASH_ENV` line has no other source on this host.

## F4. The `~/.bashrc` loses the host-local lines

The live `~/.bashrc` holds a Kiro CLI PATH line and a FastPath block. The
upstream `dot_bashrc` holds neither. `~/.fastpath/env` does not exist on
this host, so the FastPath block does nothing today. The Kiro CLI line
matters.

The live `~/.profile` holds the same line, and the repo's `dot_zprofile`
sources `~/.profile`. So the line survives in a login zsh and disappears in
an interactive bash.

## F5. The OpenCode `cli.json` loses five keys

The live file is a strict superset of the repo file. The live file holds
`session.image_preview`, `session.sidebar`, `session.markdown`,
`session.permissions` and `diffs.wrap`. The repo file holds none of them.

## F6. Two upstream config changes are safe

- The `context7` remote MCP server is schema valid, the endpoint answers
  `initialize` with HTTP 200 and no key, and `disabled` is a valid field.
- The Zed font families `FiraMono Nerd Font` and `Terminess Nerd Font` are
  both installed.
- The `warming.duration` value `16 minutes` passes the validation, because
  the default ping interval of 4 minutes is shorter than the window.
