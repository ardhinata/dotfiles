# p10k tunables

Reference table for the `POWERLEVEL9K_*` and `GITSTATUS_*` environment
variables. Read this when you need a default value or the effect of a knob.

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
