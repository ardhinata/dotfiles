# Verification

What was changed on 2026-11-10, how it was installed, and what the host
measured afterwards. Part of the plan to correct the dotfiles for the macOS
work laptop. See [README.md](README.md) for the index.

## The source changes

| File | Change |
|---|---|
| `.chezmoitemplates/hosts.yaml` | The host table with the `IKM202300278` profile and the `_default` profile |
| `.chezmoitemplates/host.yaml.tmpl` | The resolver, with a warning and the fallback |
| `dot_zshenv` | Sources the unmanaged token file after `path.sh` |
| `dot_bashrc` | Sources the unmanaged `~/.shell/bashrc.local` after `path.sh` |
| `dot_zprofile` | Sources `path.sh` a second time, because `/etc/zprofile` runs before it |
| `dot_shell/env/path.sh` | The `_path_front` loop, the Homebrew block, the helper at the front |
| `dot_config/opencode/private_cli.json.tmpl` | The renamed file with the five extra keys behind the router |
| `.chezmoiignore` | Ignores `.config/environment.d` when `.chezmoi.os` is `darwin` |

## The host files

| File | Change |
|---|---|
| `~/.shell/bashrc.local` | New. Holds the Kiro CLI PATH line and the FastPath block |
| `~/.shell/env/path.sh` | New. The managed PATH file |
| `~/.zshenv` | A regular file now. It was a symlink to `~/.shell/.zshenv` |

`~/.shell/.zshenv` still holds the tokens. It is unmanaged, and the
dispatcher sources it.

## The install

The install ran without `chezmoi apply`. The backup is at
`~/.local/state/chezmoi-backup-2026-11-10-macos-router`, and it holds the
token file as well, because the token file is not a chezmoi target.

Each target was written from `chezmoi cat` into a temporary file in the
same directory, and the temporary file was renamed over the target. The
rename replaces the `~/.zshenv` symlink instead of following it, so the
token file was never truncated.

## The measurements

### The end state of chezmoi

```text
$ chezmoi diff | wc -l
0
$ chezmoi status
 R .chezmoiscripts/start-embeddings-proxy.sh
```

The one row left is the pre-existing drift of the embeddings proxy
script. It is not a diff.

### The secrets and the helper in a clean environment

```text
$ env -i HOME="$HOME" /bin/zsh -c 'echo "JIRA=${JIRA_API_TOKEN:+SET} BB=${BITBUCKET_API_TOKEN:+SET} JIRA_URL=${JIRA_URL:+SET}"'
JIRA=SET BB=SET JIRA_URL=SET
$ env -i HOME="$HOME" /bin/zsh -c 'command -v shellx && shellx list >/dev/null && echo "shellx OK"'
/Users/muhamad.ardhinata/.shell/helper/shellx
shellx OK
```

### The PATH in the four shell types

The first three PATH entries, and the resolved `python3`:

| Shell | PATH head | `python3` |
|---|---|---|
| `zsh -c` | `~/.cargo/bin`, `~/.shell/helper`, `/opt/homebrew/bin` | 3.15.2 |
| `zsh -lc` | `~/.shell/helper`, `/opt/homebrew/bin`, `/opt/homebrew/sbin` | 3.15.2 |
| `zsh -ic` | fnm directory, `/opt/homebrew/bin`, `/opt/homebrew/sbin` | 3.15.2 |
| `zsh -lic` | fnm directory, `/opt/homebrew/bin`, `/opt/homebrew/sbin` | 3.15.2 |

The helper sits at position 1 in the login shell and position 2 in the
non-interactive shell, behind the cargo directory that the token file
adds. In the interactive shells it sits at position 4 or 5, behind the
directories that the interactive startup prepends. In every case it is
ahead of `/usr/bin` and of `~/.local/bin`, which is what the helper
needs.

A non-interactive bash has no helper on PATH and resolves `python3` to
`/usr/bin/python3`. That is the state before the change as well: macOS
has no systemd, so the `BASH_ENV` line of `environment.d` never runs
here. An interactive bash has the helper and resolves `python3` to 3.15.2.

### The OpenCode config

```text
$ opencode debug config
warming   = {"duration": "960000 millis"}
context7 = {"type": "remote", "url": "https://mcp.context7.com/mcp", "disabled": true}
plugins  = [..., "opencode-orchestrator@latest", ...]
```

The context7 plugin is gone from the plugin list, and the remote MCP
server takes its place.

### The router

```text
$ chezmoi --source <tmp> execute-template '{{ $host := fromYaml (includeTemplate "host.yaml.tmpl" .) }}{{ $host.label }}'
work-laptop
```

An unknown hostname prints `unknown host "not-this-host": using the
default profile` and returns the `_default` profile. Both renders of the
`cli.json` template parse with `python3 -m json.tool`. The true branch is
byte for byte the live file. The `.chezmoitemplates` directory is not
deployed.

### The compiled bytecode

The new `~/.zshenv` is dated 2026-11-10, and `~/.zshenv.zwc` is dated
2026-11-03. The non-interactive shell resolves the PATH from the new
source, so the bytecode does not shadow it.

## Not checked

- The full Zed render with the new font families. The font files are
  present, but Zed was not restarted.
- The prompt and the zgenom plugins in a real terminal.
- The Linux branch of the templates. No Linux host was available.
