# Prezto zstyle API

Reference table for the `zstyle` keys this project reads. Read this when
you need the exact key name, its effect, or where prezto reads it.

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
