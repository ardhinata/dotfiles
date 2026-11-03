---
title: Prezto modules per operating system
date: 2026-11-03
last-updated: 2026-11-03
status: active
os:
  - linux
  - darwin
---

# Prezto modules per operating system

The prezto module list lives in `dot_zshrc.tmpl`. The template loads the
common modules on both systems, then adds the modules that only one of
them uses.

## Why the list needs a split

`zgenom prezto <module>` does not load a module. It appends the module to
a list, and `zgenom save` writes that list into
`~/.shell/zgenom/sources/init.zsh` as one `pmodload` line. The shell
loads the modules from that file.

Two consequences shape the setup:

- The module list in the generated file, not in `~/.zshrc`. A change to
  the recipe needs a regeneration before it reaches the shell.
- `ZGEN_PREZTO_LOAD_DEFAULT=0` skips the prezto default modules. Every
  module the shell needs must appear in the explicit list.

## The common modules

These load on Linux and on macOS.

| Module | Why |
|---|---|
| `environment` | Sets `INTERACTIVE_COMMENTS`, so `#` starts a comment at the prompt. The default modules carry it, and `ZGEN_PREZTO_LOAD_DEFAULT=0` skips them. |
| `terminal` | Sets the window and tab titles. It is also the module that knows about Apple Terminal. |
| `archive` | The `archive`, `unarchive` and `lsarchive` functions. It has no `init.zsh`, only autoloaded functions. |
| `directory` | `AUTO_CD`, `AUTOPUSHD` and the directory aliases. |
| `git` | The git aliases and the repository status for the prompt. |
| `history` | The history options and the 1 MiB history size. |
| `rsync` | The rsync aliases. The module adds `--crtimes --fileflags` on macOS. |
| `utility` | The general aliases. It reads the `ls` implementation and sets `alias ls='ls -G'` on BSD and `alias ls='ls --color=auto'` on GNU. |
| `editor` | The `edit` and `ev` key bindings. |
| `completion` | The completion system. It snapshots `fpath` when it loads, so it must come after the modules that add to `fpath`. |
| `syntax-highlighting` | The highlighting. It needs the global `color` style, which the template sets. |
| `history-substring-search` | The search widget. It must come after `syntax-highlighting`, so its key binds land on top of the highlighting wrapper. |
| `prompt` | The prompt. It loads the powerlevel10k theme. |

## The macOS modules

These load on macOS only.

| Module | Why |
|---|---|
| `osx` | The macOS helpers: `pfd` and `pfs` for the Finder, `ql` for Quick Look, `trash` for the trash, `tab` for a new terminal tab, `mand` and `manp` for the man pages. The module returns early on a non-macOS host. |
| `command-not-found` | Suggests a package for a command that is not on the PATH. On macOS the module loads the Homebrew handler from `$(brew --repository)/Library/Homebrew/command-not-found/handler.sh`. |

Two of the `osx` helpers need software that this machine does not have.
`mand` opens Dash.app, and `tab` opens Terminal.app. The terminal in use
is Ghostty, installed under `~/Applications`. Both helpers fail only when
they are called.

## The Linux modules

These load on Linux only.

| Module | Why |
|---|---|
| `pacman` | The Arch package manager aliases and the `aurget` function. The module returns early when the `pacman` command is missing, so it is safe on a host that is not Arch. |

A host on Fedora, Debian or Alpine needs a different package manager
module. The split uses `.chezmoi.os`, which names the operating system
but not the distribution. Adding a distribution key needs a change to
`.chezmoidata.yaml`.

## The modules this repository does not load

| Module | Why not |
|---|---|
| `pacman` on macOS | The Arch package manager. It belongs to the Linux list. |
| `homebrew` | `brew shellenv` runs in `dot_shell/zsh/00-before-zgenom.zsh` and already exports the `HOMEBREW_` variables. The module adds the `brewc`, `brewi`, `brewl` and `brewo` aliases on top of that, and the old host configuration skipped those aliases too. |
| `gnu-utility` | The module defines a function for every GNU coreutils command it finds, so it replaces the BSD tools on macOS. The `utility` module reads the `ls` implementation when it loads, and the load order decides which branch it takes. With `gnu-utility` first, `utility` sets `alias ls='ls --color=auto'`. With `utility` first, it sets `alias ls='ls -G'`, and GNU `ls` reads `-G` as `--no-group`, so the listing loses its colors. |
| `macports` | The module needs the `port` command. This machine uses Homebrew. |
| `gpg` | Disabled on purpose. The module exports `GPG_TTY` when it loads, which points pinentry at the wrong tty. `dot_shell/zsh/12-gpg.zsh` does the same work with a just-in-time hook. |
| `ssh` | The module only starts an `ssh-agent`. The gpg module loads it, and the gpg module is disabled. |

## How a change reaches the shell

The template regenerates the init script when the `.zshrc` is newer than
the generated file. The regeneration writes the new module list, and the
next shell loads it. A change takes two shell starts.

To force a regeneration by hand, remove the compiled file:

```zsh
rm "${HOME}/.zshrc.zwc"
```

## Verify the loaded modules

The loaded modules are prezto zstyles. Print them from a login shell:

```zsh
zstyle -L ':prezto:module:*' loaded
```

A module that the template does not load must not appear. The `gpg` line
shows `loaded yes` in every case. That is the disable style, and it means
the module is skipped.

Check that the `ls` implementation is the one the platform ships:

```zsh
ls --version
```

BSD `ls` answers `unrecognized option`. GNU `ls` prints its version.
