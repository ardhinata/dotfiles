---
name: zsh-stack
description: zsh configuration stack used in this dotfiles project — zgenom (plugin manager), prezto (zsh config framework + modules), powerlevel10k (prompt). Load before any task that touches dot_zshrc, dot_shell/zsh/, dot_p10k.zsh, the prezto gpg module, zsh startup performance, prompt rendering, completion, or history. Captures the tunables, pitfalls, and project-specific quirks that the agent would otherwise rediscover (or repeat).
---

# zsh-stack Skill

Load when about to edit or reason about anything in the zsh init chain.

## When to Load

- Editing `dot_zshrc`, `dot_shell/zsh/*`, `dot_zprofile`, `dot_zshenv`, or `dot_p10k.zsh`.
- User mentions `zgenom`, `prezto`, `powerlevel10k`, `p10k`, `pmodload`, `compinit`, `zcompdump`, `.zwc`, `instant prompt`, `prompt_substring_search`, `UPDATESTARTUPTTY`, `gpg-agent` in a zsh context.
- Debugging slow zsh startup, broken completions, missing prompt segments, stale `.zwc` bytecode, or pinentry opening on the wrong tty.
- Adding/removing a prezto module, changing a module's `zstyle`, or reordering the prezto module list.

## Architecture

Three layers, loaded in this order:

```
┌────────────────────────────────────────────────────────────────────────┐
│ .zshrc preamble (dot_zshrc:1-7)                                         │
│   └─ source p10k instant-prompt cache (per-user, per-TX snapshot)      │
├────────────────────────────────────────────────────────────────────────┤
│ .zshrc body (dot_zshrc:9-73)                                            │
│   ├─ source 00-before-zgenom.zsh  (fpath + gpg-module zstyle)           │
│   ├─ source zgenom.zsh            (plugin manager)                     │
│   ├─ ! zgenom saved → regenerate init.zsh + compile .zshrc             │
│   │   └─ pmodload <module list>     (prezto bootstrap)                  │
│   │       └─ prompt → prompt_powerlevel10k_setup → _p9k_setup          │
│   └─ source 10/12/15  (exports, GPG_TTY, helpers)                       │
├────────────────────────────────────────────────────────────────────────┤
│ .zshrc tail (dot_zshrc:80)                                              │
│   └─ source ~/.p10k.zsh   (user prompt config, chezmoi-managed)         │
└────────────────────────────────────────────────────────────────────────┘
```

Authoritative evidence: `.tmp/notes/2026-08-08-zsh-stack-research-{zgenom,prezto,p10k}.md` (cloned source at `/tmp/kilo/zsh-stack-research/`).

---

## zgenom (plugin manager)

Repo: `jandamm/zgenom` (commit `d99d5dc` cloned 2026-08-08).

### Project-current config (where set)

| Knob | Value | Where | Purpose |
|---|---|---|---|
| `ZGENOM_DIR` | `${HOME}/.shell/zgenom` | `dot_zshrc:11` | zgenom checkout root |
| `ZGEN_PREZTO_LOAD_DEFAULT` | `0` | `dot_zshrc:16` | opt out of prezto's default module set |
| `zgenom autoupdate` | default 7 days | `dot_zshrc:24` | background self+plugin pull |
| `zgenom compile` targets | `.zshrc .zprofile .zshenv` (selective) | `dot_zshrc:70-72` | compile only top-level, **not** `$SHELL_TOOL_DIR` recursive |
| Prezto option calls | 9 lines (color, history, prompt, utility, pwd-length) | `dot_zshrc:33-42` | set module zstyles |
| Prezto module list | 12 modules, explicit order | `dot_zshrc:49-60` | env→archive→…→prompt |

### Public API (autoloaded from `functions/`)

- `zgenom load <repo|path> [loc] [branch] [--completion] [--pin=<hash>]` — clone + source + fpath
- `zgenom loadall` — bulk loader
- `zgenom prezto [module] [option value …]` — load prezto / module / set `zstyle`
- `zgenom pmodule <repo> <branch>` — load repo as a prezto module
- `zgenom bin <repo>` — stage plugin `./bin` into `$ZGENOM_SOURCE_BIN`
- `zgenom save [--no-compile]` — write static `$ZGEN_INIT`, compile sources+dumps
- `zgenom saved` — source `init.zsh` if present (the `! zgenom saved || …` guard in `dot_zshrc:27`)
- `zgenom apply` — compinit + compdef-apply + path-prepend (no-saved-script path)
- `zgenom reset` — rm `init.zsh` + `$ZGEN_CUSTOM_COMPDUMP` + bin dir
- `zgenom clean` — rm repos not in the current session's load set
- `zgenom update [--no-reset]` — `git pull --ff-only` + submodule update, then reset
- `zgenom selfupdate` — update zgenom itself
- `zgenom compile <file|dir>` — `zcompile` target(s); file → selective, dir → recursive
- `zgenom list [--bin|--init]`, `zgenom help`, `zgenom api`

### Pitfalls (cite as needed)

- **`.zwc` shadows fresh source.** zgenom auto-compiles sources + `.zshrc*.zwc` (`zgenom-save:128-147`); if `.zwc` is newer than the `.zsh`, zsh sources stale bytecode. Recompile is conditional (`__zgenom_compile:4`), so editing a file whose `.zwc` is older triggers it; otherwise the stale `.zwc` wins. **This is why the project refuses to recursively compile `$SHELL_TOOL_DIR`** (`dot_zshrc:65-72`).
- **`zgenom reset` does not clear plugins** — only `init.zsh`, `$ZGEN_CUSTOM_COMPDUMP`, bin dir (`zgenom-reset:6-18`). Use `zgenom clean` for physical removal.
- **`zgenom compile <file>` is selective.** A dir arg compiles `"$file/**/*"` recursively (`zgenom-compile:24`); a file arg compiles just that file (`zgenom-compile:20-21`).
- **Saved-cache ≠ recompile.** `zgenom saved` only sources generated `init.zsh`; editing the module list requires `zgenom reset` so the `! zgenom saved` branch runs.
- **`autoupdate` × non-interactive regen** — autoupdate spawns `_ZGENOM_JUST_INIT=1 zsh -c '<source .zshrc>'` (`zgenom-autoupdate:80-89`); if a plugin assumes an interactive shell, pass `--no-background`.
- **`autoupdate` self-silences ohmyzsh** unless `--keep-ohmyzsh` (`zgenom-autoupdate:35-37`).
- **`autoupdate` skips if `$USER` ≠ owner of `$ZGEN_DIR`** (`__zgenom_autoupdate:45`) — protects against root-owned leftovers.
- **`compdef` only exists after compinit** — use `zgenom compdef` shim for plugins that call it too early.
- **`__zgenom-*`** functions are private; treat `zgenom api` as the supported surface.

### Project quirks

- **`ZGEN_PREZTO_LOAD_DEFAULT=0`** (`dot_zshrc:16`): prezto's defaults (including `environment`, `terminal`, `editor`, `spectrum`) are **not** auto-loaded; the project lists every module explicitly. The reason `environment` *must* be listed is in `dot_zshrc:44-48` (it sets `setopt INTERACTIVE_COMMENTS`, which makes `#` work at the prompt).
- **`zgenom_refresh_cache`** (`dot_shell/zsh/15-zgenom-helper-func.zsh:1-11`): guarded on `${+functions[zgenom]}`, deletes top-level `*.zwc` in `$SHELL_TOOL_DIR`, `~/.z*.zwc`, `${XDG_CACHE_HOME:-$HOME/.cache}/prezto/zcompdump`, then `zgenom reset`. Run this when completions or `.zwc` look stale; the next fresh shell rebuilds from `! zgenom saved`.
- **`zgenom prezto '*' color "yes"`** (`dot_zshrc:41`): module `'*'` expands to `:prezto:module:*` (`__zgenom_prezto_option:10-19`); forces color on globally and is what **un-gates the syntax-highlighting module** (`syntax-highlighting/init.zsh:9-11`).

---

## prezto (zsh config framework)

Repo: `sorin-ionescu/prezto` (commit `cff2d018` cloned 2026-08-08).

### Bootstrap (`init.zsh:74-158`)

`pmodload` iterates `$pmodules` (init.zsh:96) in the order passed; **load order = `zgenom prezto <m1> <m2> …` call order in `dot_zshrc:49-60`**. Each module:

1. Locates its dir via `$^pmodule_dirs/$pmodule(-/FN)` (init.zsh:100)
2. Prepends `$module/functions` to `$fpath` (init.zsh:115)
3. Autoloads `^([_.]*|prompt_*_setup|README*|*~)(-.N:t)` (init.zsh:80, 124-126) — note `prompt_*_setup` is **excluded**; prompt themes are autoloaded on demand by `promptinit`
4. Sources `init.zsh` or `$name.plugin.zsh` (init.zsh:129-133)
5. Marks `:prezto:module:<name> loaded yes|no` (init.zsh:136/154)

### The `loaded` zstyle — disable mechanism

```zsh
# init.zsh:97 — pmodload skips modules whose `loaded` zstyle is "yes"
if zstyle -t ":prezto:module:$pmodule" loaded 'yes' 'no'; then continue
```

`00-before-zgenom.zsh:17` uses this exact gate to skip the gpg module:
```zsh
zstyle ':prezto:module:gpg' loaded 'yes'
```

### zstyle API

Format: `zstyle ':prezto:module:<name>[:<subkey>]' <key> <value>`. Under zgenom: `zgenom prezto <name>[:<subkey>] <key> <value>`. A literal `'*'` module maps to `:prezto:*` (global).

Common keys:

| Key | Effect | Where read |
|---|---|---|
| `loaded <yes\|no>` | pmodload gate; set by `pmodload`, can be pre-set by user | init.zsh:97 |
| `color <yes\|no>` | global color gate; forced `no` under dumb `TERM`; gates `environment` termcap + **gates syntax-highlighting entirely** | init.zsh:9 (syntax-highlighting) |
| `theme` | which `prompt_*_setup` runs (here `powerlevel10k`) | prompt/init.zsh:12 |
| `pwd-length <short\|long\|full>` | prompt path abbreviation | prompt-pwd |
| `managed <yes\|no>` | tells `editor-info` the theme is prezto-compatible | prompt README |
| `histsize` | sets `HISTSIZE` and `SAVEHIST` (history/init.zsh:29-34) | history/init.zsh:31 |
| `histfile` | history file path | history/init.zsh:30 |
| `savehist` | `SAVEHIST` | history/init.zsh:33 |
| `correct <yes\|no>` | gates `setopt CORRECT` | utility/init.zsh:14-16 |
| `safe-ops <yes\|no>` | `-i` on `cp/ln/mv/rm` | utility/init.zsh:71-76 |
| `utility:download helper` | `get` backend (`wget`/`curl`/`aria2c`/…) | utility/init.zsh:169-181 |
| `directory:alias skip`, `git:alias skip`, `history:alias skip` | skip module alias sets | directory/init.zsh:28; git/alias.zsh:28; history/init.zsh:40 |
| `case-sensitive` | completion matcher case-sensitivity | completion/init.zsh:136 |
| `highlighters`, `styles`, `pattern` | syntax-highlight mapping | syntax-highlighting/init.zsh:17-36 |

### Per-module notes (only what this project loads)

- **environment** — sets `INTERACTIVE_COMMENTS`, `COMBINING_CHARS`, `RC_QUOTES`; `unsetopt MAIL_WARNING`; `stty -ixon`; jobs opts; termcap colors when `environment:termcap color`. **Source of `setopt INTERACTIVE_COMMENTS` (`environment/init.zsh:35`)** — the load-bearing reason `dot_zshrc:49` re-loads it explicitly when `ZGEN_PREZTO_LOAD_DEFAULT=0`.
- **archive** — no `init.zsh`; only autoloaded `archive/lsarchive/unarchive` functions.
- **directory** — `AUTO_CD AUTOPUSHD PUSHD_*`, `CDABLE_VARS MULTIOS EXTENDED_GLOB`. Alias set skipped here (`dot_zshrc:33`).
- **git** — loads `helper`, autoloads `run-help-git`, sources `alias.zsh`. Alias set skipped here (`dot_zshrc:34`); `git:log:*` and `git:status:*` format zstyles still apply.
- **history** — `BANG_HIST EXTENDED_HISTORY SHARE_HISTORY HIST_*`. `histsize 1048576` here (`dot_zshrc:36`) → both `HISTSIZE` and `SAVEHIST`=1048576. Alias `history-stat` skipped (`dot_zshrc:35`).
- **pacman** — guarded by `commands[pacman]`; no-op on non-Arch hosts. Aliases + `aurget`.
- **rsync** — guarded by `commands[rsync]`; aliases `rsync-copy/-move/-update/-synchronize`.
- **utility** — `pmodload helper spectrum`; `correct`, `safe-ops`, ls/grep color, `o`/`pbcopy` platform; **`utility:download helper aria2c`** (`dot_zshrc:37`); `safe-ops "no"` (`dot_zshrc:38`).
- **completion** — `$TERM != dumb` guard; prepends `external/src` (zsh-completions) + brew curl to fpath; runs `compinit -i` fresh or `compinit -C` when cache <20h, writing `${XDG_CACHE_HOME:-$HOME/.cache}/prezto/zcompdump`. **This compdump is what `zgenom_refresh_cache` deletes** (`15-zgenom-helper-func.zsh:9`).
- **syntax-highlighting** — **returns early unless `:prezto:module:syntax-highlighting color` is true** (`syntax-highlighting/init.zsh:9-11`); global `'*' color yes` (`dot_zshrc:41`) un-gates it.
- **history-substring-search** — `pmodload editor`; binds Up/Down + Ctrl-P/N (emacs+viins) and vi `k/j` to its widgets.
- **prompt** — `promptinit`, reads `:prezto:module:prompt theme` into `prompt_argv`; if no theme / dumb/linux/bsd → `prompt off`. The actual `prompt_powerlevel10k_setup` is a **symlink** into prezto's `external/powerlevel10k/powerlevel10k.zsh-theme` (per `.gitmodules`) — works only when the prezto submodule is initialized (zgenom clones `--recursive`).

### Pitfalls

- **gpg module GPG_TTY race** — `modules/gpg/init.zsh:30` runs `export GPG_TTY=$TTY` at **pmodload time**, but `$TTY`/`$(tty)` during `.zshrc` source is the *previous* alacritty tab's pts. The stale value then leaks into `systemd --user import-environment` and points pinentry at the wrong tty on the next SSH sign. The module also auto-starts `gpg-agent --daemon` (gpg/init.zsh:21-27), installs the `UPDATESTARTUPTTY` preexec hook (43-47), `pmodload 'ssh'` on `enable-ssh-support` (33-41), and sets `PINENTRY_USER_DATA=USE_CURSES=1` when `$SSH_CONNECTION` (54-56). All **disabled here** via the `loaded` zstyle (`00-before-zgenom.zsh:17`) + reimplemented in `dot_shell/zsh/12-gpg.zsh` with a just-in-time preexec hook.
- **`ZGEN_PREZTO_LOAD_DEFAULT=0` drops `INTERACTIVE_COMMENTS`** — must explicitly load `environment` first (`dot_zshrc:49`).
- **syntax-highlighting → history-substring-search order** — syntax-highlighting must be sourced **before** HSS so HSS's key binds land on top of the wrapping (`dot_zshrc:58-59`). Also: syntax-highlighting is gated by `:prezto:* color yes`; HSS is not.
- **completion compinit ordering vs fpath additions** — compinit snapshots `$fpath` at module-load (`completion/init.zsh:56-68`); user completions added after won't register until the 20h cache expires. **`00-before-zgenom.zsh:11` prepends `$SHELL_TOOL_DIR/zsh/completions` before zgenom/prezto init** precisely for this reason (`_runpriv` is the load-bearing completion there).
- **`prompt_powerlevel10k_setup` is a submodule symlink** — verify `git submodule status` inside `$ZGEN_DIR/sources/prezto/` if p10k is broken.

### Project quirks (line-by-line)

| `dot_zshrc` line | Prezto concept |
|---|---|
| 16 | `ZGEN_PREZTO_LOAD_DEFAULT=0` (zgenom knob, not prezto) |
| 31 | `zgenom prezto` — load prezto `init.zsh` |
| 33-35 | `:alias skip` for directory/git/history |
| 36 | `history histsize 1048576` |
| 37 | `utility:download helper aria2c` |
| 38 | `utility safe-ops no` |
| 39 | `prompt theme powerlevel10k` |
| 40 | `prompt managed yes` |
| 41 | `'*' color yes` (global; enables syntax-highlighting) |
| 42 | `prompt pwd-length short` |
| 49 | `environment` (explicit, restore `INTERACTIVE_COMMENTS`) |
| 50-60 | explicit `pmodload` list (this is the load order) |
| `00-before-zgenom.zsh:11` | fpath prepend so compinit sees user completions |
| `00-before-zgenom.zsh:17` | `:prezto:module:gpg loaded yes` — disable gpg |
| `12-gpg.zsh` | reimplements GPG_TTY/UPDATESTARTUPTTY |

---

## powerlevel10k (prompt)

Repo: `romkatv/powerlevel10k` (commit `9253fb1` cloned 2026-08-08).

### Three layers

1. **Instant prompt** — `p10k-instant-prompt-${(%):-%n}.zsh` at `${XDG_CACHE_HOME:-$HOME/.cache}/`. Written by `_p9k_dump_instant_prompt` (`internal/p10k.zsh:6180`), guards on interactive+TTY+zle and bails if `ZSH_VERSION`/`ZSH_PATCHLEVEL`/`install.info` header changed (6210-6247). The `${(%):-%n}` is the **per-user, prompt-percent-expanded** trick.
2. **gitstatus daemon** (`gitstatusd`) — attached during `_p9k_preinit`, started at first prompt if no instant prompt (`_p9k_init_vcs` at `internal/p10k.zsh:8831`). Cached at `${XDG_CACHE_HOME:-$HOME/.cache}/gitstatus`.
3. **Prompt proper** — `precmd → _p9k_set_prompt → per-segment prompt_*` functions, with `_p9k_setup` hooking preexec/precmd (`internal/p10k.zsh:9135-9148`).

### Activation in this project

`dot_zshrc:39` `zgenom prezto prompt theme "powerlevel10k"` + `:40` `managed yes` → prezto's `prompt` module calls `prompt powerlevel10k` → `promptinit` autoloads `prompt_powerlevel10k_setup` (symlinked from the prezto submodule) → `_p9k_setup` → instant-prompt + gitstatus preinit + prompt renderer. `dot_zshrc:80` then sources `~/.p10k.zsh` (chezmoi-managed as `dot_p10k.zsh`) which overrides defaults.

### Tunables

| Knob | Default | Notes |
|---|---|---|
| `POWERLEVEL9K_INSTANT_PROMPT` | `verbose` | `verbose` warns on console output during init; `quiet` silences; `off` disables. Requires Zsh ≥5.4. |
| `POWERLEVEL9K_DISABLE_INSTANT_PROMPT` | `false` | Hard off; also used internally when gitstatus fails to attach. |
| `POWERLEVEL9K_LEFT_PROMPT_ELEMENTS` | `context dir vcs` | Left segments. |
| `POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS` | `status root_indicator background_jobs history time` | Empty → no `RPROMPT`. |
| `POWERLEVEL9K_MODE` | unset (auto) | `compatible`/`nerdfont-complete`/`awesome-patched`/… |
| `POWERLEVEL9K_COLORTERM_OVERRIDE` | unset | Force `COLORTERM` for truecolor detection. |
| `POWERLEVEL9K_OS_ICON` | derived from OS + `*_ICON` map | OS/distro icon segment. |
| `POWERLEVEL9K_PROMPT_ADD_NEWLINE` | `false` | Blank line above prompt (also in instant-prompt snapshot). |
| `POWERLEVEL9K_PROMPT_ADD_NEWLINE_COUNT` | `1` | Blank-line count. |
| `POWERLEVEL9K_TRANSPARENT_BACKGROUND` | unset | No `%k` block fill. |
| `POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD` | unset | Wizard auto-launches on first load unless `true`. |
| `POWERLEVEL9K_NEW_TTY_MAX_AGE_SECONDS` | `5` | TTL for "new terminal" snapshot capture. |
| `POWERLEVEL9K_GITSTATUS_DIR` | `${__p9k_root_dir}/gitstatus` | Override gitstatus path. |
| `POWERLEVEL9K_GITSTATUS_INIT_TIMEOUT_SEC` | `10` | Wait for gitstatus daemon. |
| `POWERLEVEL9K_DISABLE_GITSTATUS` | `false` | Skip daemon (slow). |
| `GITSTATUS_AUTO_INSTALL` | `1` | Auto-build gitstatusd on first run. |
| `GITSTATUS_CACHE_DIR` | `${XDG_CACHE_HOME:-$HOME/.cache}/gitstatus` | Where gitstatusd binaries/logs live. |
| `GITSTATUS_NUM_THREADS`, `GITSTATUS_LOG_LEVEL`, `GITSTATUS_ENABLE_LOGGING` | auto / INFO / off | Daemon tuning. |

### Pitfalls

- **Instant-prompt silent corruption** — anything requiring console input (keyring password, `[y/n]`) sourced **after** the instant-prompt block (`dot_zshrc:1-7`) hangs or silently eats input because stdin is `/dev/null`. Move such lines **above** the block (README.md:1055-1078). The `12-gpg.zsh` `preexec` hook is instant-prompt-safe because it only fires on a real command (post-preamble).
- **Console output mixing** — any stdout during init is captured and replayed uncolored; p10k prints `Console output during zsh initialization detected.` Fixes: move above, suppress output, or `POWERLEVEL9K_INSTANT_PROMPT=quiet` / `=off`.
- **"must be loaded before the first prompt"** — if p10k's init runs after the first prompt was already drawn (e.g. a slow `compinit` in between), the cached snapshot is erased (`internal/p10k.zsh:9047, 6660-6664`).
- **`prompt_cr` clash** — if `setopt prompt_cr` is re-enabled after p10k unsets it, p10k prints the warning and recommends `p10k finalize` at the end of `.zshrc` (internal/p10k.zsh:6785-6807).
- **`p10k configure` overwrites `~/.p10k.zsh`** — the wizard writes `${POWERLEVEL9K_CONFIG_FILE:-${ZDOTDIR:-~}/.p10k.zsh}` (`configure.zsh:16`). **In this project that file is `dot_p10k.zsh` (~87 KB, chezmoi-managed) — DO NOT run `p10k configure`** or it desyncs from source state. To regenerate: re-run the wizard in a temp file, then patch `dot_p10k.zsh` via chezmoi.
- **Wizard auto-runs** on first load unless `POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true` (`wizard.zsh:268, 2065`).
- **gitstatus build on first run** — missing C toolchain or read-only cache dir disables instant prompt (`internal/p10k.zsh:8850`).
- **Cache path collision** — only the username folds into the path; p10k guards per-file via embedded `ZSH_VERSION`/`ZSH_PATCHLEVEL`, `TERM`/screen/tmux, `VTE_VERSION`, gitstatus `install.info`, terminfo colors (6210-6247).

### Project quirks

- `dot_zshrc:1-7` instant-prompt block is the canonical README verbatim; the `[[ -r ... ]]` guard skips sourcing when the cache is absent (harmless before first run).
- The instant-prompt preamble **must stay at the top** — anything before it that prints to stdout will be lost; anything after it that needs stdin must be guarded.
- `~/.p10k.zsh` is `dot_p10k.zsh` (chezmoi); sourced dead-last (`dot_zshrc:80`) **after** everything else, including `12-gpg.zsh`, so `GPG_TTY` exports inside it are seen by the prompt renderer.
- See `pinentry.vscode_tunnel_no_gui` constraint (project memory) — p10k segments referencing remote/gpg info degrade gracefully but the project's gpg lifecycle is owned by `12-gpg.zsh`, not by p10k.

---

## Cross-Cutting Pitfalls

1. **`.zwc` bytecode is the single biggest zsh footgun.** If a `.zsh` file is edited but its `.zwc` is newer, zsh sources the stale compiled bytecode. Fixes: `zgenom_refresh_cache` (project helper), or `rm ~/.z*.zwc ${SHELL_TOOL_DIR}/*.zwc` manually. Recursive `zgenom compile <dir>` makes this worse — that is why `dot_zshrc:70-72` is selective.
2. **Two completion dumps coexist:** prezto's `${XDG_CACHE_HOME:-$HOME/.cache}/prezto/zcompdump` and zgenom's default `$ZGEN_DIR/zcompdump_$ZSH_VERSION`. They serve different consumers; clearing only one half-fixes.
3. **Compinit snapshots `$fpath`** at module load — user completions must be in `$fpath` before `completion` module loads (`00-before-zgenom.zsh:11`).
4. **`pmodload` order matters.** `environment` first (for `INTERACTIVE_COMMENTS`), then core utilities, then `completion` (so compinit sees all completions), then `syntax-highlighting` (must be sourced before HSS), then `history-substring-search`, then `prompt` last (so all setup is done before the theme installs). The order in `dot_zshrc:49-60` is intentional — do not "tidy" it.
5. **The `loaded` zstyle gate** is the *only* prezto-blessed way to disable a module. Don't just drop gpg from the module list; the project's `00-before-zgenom.zsh:17` zstyle is what actually disables it.
6. **Anything that needs `tty`/`$TTY`/`systemctl --user import-environment` must be re-run just-in-time** in a preexec hook, not at `.zshrc` source time — the controlling-tty value at source time is stale on alacritty (see `dot_shell/zsh/12-gpg.zsh` and project memory `gpg_agent.ssh_tty_propagation_fix`).
7. **p10k's `~/.p10k.zsh` is chezmoi-managed.** Edit via `chezmoi edit ~/dot_p10k.zsh` (after `chezmoi add`) — never `p10k configure`.
8. **Tunables are set at three different layers** with three different mechanisms:
   - zgenom: env vars `ZGEN_*` set before sourcing `zgenom.zsh`, or function calls after.
   - prezto: `zstyle ':prezto:module:<m>' <key> <value>` (or `zgenom prezto <m> <key> <value>` in this project).
   - p10k: `typeset -g POWERLEVEL9K_*` (set in `~/.p10k.zsh`).

   Confusing these is the #1 cause of "I set the option but it didn't take" debug sessions.

---

## Cross-References

| Project file | Layer | Notes |
|---|---|---|
| `dot_zshrc` | all three | The orchestration. Lines 1-7 = p10k preamble, 9-13 = env+fpath, 16 = zgenom knob, 18 = zgenom source, 24 = autoupdate, 27-73 = saved-cache guard + prezto setup, 75-77 = sourced helpers, 80 = `~/.p10k.zsh`. |
| `dot_shell/zsh/00-before-zgenom.zsh` | zgenom/prezto | `fpath` prepend for `compinit`; zstyle-disable prezto `gpg` module. Must run **before** zgenom init. |
| `dot_shell/zsh/10-common-export.zsh` | post-zgenom | Exports + `fnm env --use-on-cd` + `runpriv` PATH. Top comment says it runs after completions are active. |
| `dot_shell/zsh/12-gpg.zsh` | post-zgenom | Owns GPG_TTY lifecycle. Replaces prezto's disabled gpg module's `export GPG_TTY=$TTY` + UPDATESTARTUPTTY. Has a preexec hook for just-in-time tty refresh (alacritty reassigns controlling tty mid-startup). |
| `dot_shell/zsh/15-zgenom-helper-func.zsh` | helper | `zgenom_refresh_cache`: clears `.zwc` + prezto `zcompdump` + `zgenom reset`. |
| `dot_p10k.zsh` | p10k | User prompt config (~87 KB). Sourced last (`dot_zshrc:80`). **Never run `p10k configure`** — it overwrites. |
| `dot_shell/zsh/completions/` | completion | Custom `#compdef` functions (e.g. `_runpriv`). fpath-prepended by `00-before-zgenom.zsh`. |

## Memory pointers

- `gpg_agent.ssh_tty_propagation_fix` — root cause of the gpg/Tty/alacritty dance.
- `pinentry.switcher.locked_flags` — pinentry backend is owned by `~/.shell/helper/pinentry-wrapper`, not prezto's gpg module.
- `pinentry.testing_interactive_only` — TTY-related behavior must be tested in a real interactive terminal; non-interactive bash cannot reproduce it.

## Validation

Quick smoke tests for any edit in this stack (run in a fresh interactive shell):

```sh
# 1. Compinit/saved-cache state
ls -la "$HOME/.shell/zgenom/sources/init.zsh"
ls -la "${XDG_CACHE_HOME:-$HOME/.cache}/prezto/zcompdump"
ls -la "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"

# 2. Module load order (must match dot_zshrc:49-60)
grep -E '^pmodload ' "$HOME/.shell/zgenom/sources/init.zsh"

# 3. Module disable via zstyle (must be present before zgenom source)
zstyle -t ':prezto:module:gpg' loaded 'yes' 'no' && echo "gpg: disabled"

# 4. Interactive-comments opt (depends on environment module)
setopt | grep INTERACTIVE_COMMENTS

# 5. p10k config is chezmoi-managed (do not edit outside chezmoi)
chezmoi diff --no-tty ~/.p10k.zsh   # empty = in sync
```

If any smoke test fails, the most common fix is `zgenom_refresh_cache` followed by restarting the shell.