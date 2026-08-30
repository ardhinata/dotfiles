---
description: Personal tmux configuration — what each option does, the rationale, and the deferred ideas that can be enabled later
---

# tmux Configuration

This directory holds the personal `tmux.conf`. It is chezmoi-managed from
`dot_config/tmux/tmux.conf` and rendered to `~/.config/tmux/tmux.conf`,
which tmux 3.2+ loads automatically (ahead of `~/.tmux.conf`).

Reload after any edit with `prefix r` (the `bind r` line at the bottom
of the file).

The file is heavily commented — every non-trivial option or binding has a
short comment explaining what it does and why. This README is the
companion narrative: it groups the configuration by purpose, lists every
key binding in one place, and records the ideas that were considered but
deferred, so future-you can revisit them with full context.

---

## 1. Conventions

- **Prefix**: `C-a` is the primary prefix. `C-b` is bound as
  `prefix2` (tmux 3.0+) so muscle memory from default tmux and GNU
  Screen both work. Both prefixes accept the same follow-up keys.
- **Send-prefix**: `C-a a` sends a literal `C-a` to the application
  inside the focused pane (useful when an editor or TUI expects `C-a`
  as a binding).
- **Reload**: `prefix r` reloads the config in-place from
  `#{config_files}`.
- **Install plugins**: First launch on a fresh chezmoi-managed machine
  installs TPM plugins automatically (see §6). After that, `prefix I`
  (capital I) installs new ones and `prefix U` upgrades them.

---

## 2. Prefix & Terminal Capabilities

| Setting | Value | Effect |
|---|---|---|
| `prefix` / `prefix2` | `C-a` / `C-b` | Two usable prefixes |
| `set-clipboard` | `on` (3.2+) | Pass OSC 52 through tmux; remote yanks reach the local clipboard |
| `mouse` | `on` | Click-to-focus panes, drag-to-resize, wheel scroll |
| `focus-events` | `on` | Forward focus gained/lost for Neovim `FocusGained/FocusLost` |
| `extended-keys` | `on` (3.4+) | Pass Shift+Arrow / Ctrl+Arrow / CSI-u |
| `escape-time` | `0` | No ESC delay → instant Neovim mode switch |
| `default-terminal` | `tmux-256color` | Modern terminfo inside tmux |
| `terminal-features` | `,xterm*:RGB,Tc` | Truecolor + synchronized output (CSI 2026) |
| `history-limit` | `50000` | Deep scrollback for long compile / `git log` runs |
| `base-index` / `pane-base-index` | `1` | 1-indexed windows and panes |
| `renumber-windows` | `on` | Surviving windows renumber after a kill |
| `aggressive-resize` | `on` | Layout follows the active client |
| `allow-rename` | `off` | Programs no longer overwrite window titles |
| `monitor-activity` / `visual-activity` | `on` / `off` | Silent activity dot per window |
| `repeat-time` | `300` | Tighter repeat window for `-r` bindings |

---

## 3. Pane Splitting

Two sets of bindings, both inherit the focused pane's working directory
(`-c "#{pane_current_path}"`).

| Keys | Action |
|---|---|
| `prefix \|` | Split left \| right (primary mnemonic) |
| `prefix -` | Split top / bottom (primary mnemonic) |
| `prefix %` | Split left \| right (default tmux binding, retained) |
| `prefix "` | Split top / bottom (default tmux binding, retained) |

Rationale: `|` and `-` look like the divider they create and need no
Shift, so they are faster. `%` and `"` stay bound for muscle memory
from old habits and shared screen recordings.

## 4. Pane Navigation & Manipulation

| Keys | Action |
|---|---|
| `prefix h` / `j` / `k` / `l` | Move focus left / down / up / right |
| `M-Left` / `M-Right` / `M-Up` / `M-Down` | Same, without prefix (root-table) |
| `prefix H` / `J` / `K` / `L` | **Swap** the pane in that direction (repeatable) |

Mnemonic: lowercase navigates, uppercase manipulates. The `-r` flag on
the swap bindings makes them repeatable — hold the prefix once and tap
the direction key repeatedly to push a pane several positions.

## 5. Window Management

| Keys | Action |
|---|---|
| `prefix C-h` / `prefix C-l` | Previous / next window (repeatable) |
| `prefix <` / `prefix >` | Swap current window left / right in the list (repeatable) |
| `prefix r` | Reload the config |

## 6. Copy Mode, Clipboard, and Paste

| Setting / Binding | Effect |
|---|---|
| `mode-keys` | `vi` — vi-style navigation in copy mode |
| `prefix [` | Enter copy mode (default tmux binding) |
| `v` in copy mode | Begin selection (vi visual mode) |
| `V` in copy mode | Line selection (vi capital-V) |
| `C-v` in copy mode | Rectangular / block selection toggle |
| `y` in copy mode | Yank selection, exit copy mode, pipe to `wl-copy` |
| Mouse drag end in copy mode | Same: pipe to `wl-copy` |
| `prefix P` | Paste last buffer (no copy mode) |

Clipboards:

- **OSC 52 path**: `set-clipboard on` lets Neovim 0.10+ (`vim.g.clipboard='osc52'`),
  kitty, and Alacritty reach the local clipboard through tmux without
  any external tool. Works over SSH.
- **`wl-copy` path**: The manual bindings above cover non-OSC-52 apps
  and shell output on Wayland. On X11, swap `wl-copy` for
  `xclip -selection clipboard`.

## 7. Status Bar

| Setting | Value | Effect |
|---|---|---|
| `status-interval` | `5` | Clock refreshes every 5 s |
| `status-justify` | `left` | Window list grows rightward |
| `status-left` | `#[fg=green] #S ` | Session name in green |
| `status-right` | `#[fg=white] %Y-%m-%d %H:%M ` | ISO date + 24 h clock |
| `status-position` | `top` | Bar at the top (more vertical room for panes) |
| `pane-border-style` | `fg=#30363d` | Dim grey borders on inactive panes |
| `pane-active-border-style` | `fg=#00e68a` | Green border on the focused pane |
| `pane-scrollbars` | `on` (3.6+) | Per-pane scrollbar on the right edge |

The scrollbar costs ~1 cell of pane width. If it feels cramped on
small layouts, comment both `pane-scrollbars` lines out — mouse scroll
still works without them.

## 8. Plugin Manager (TPM)

TPM is installed via chezmoi externals (`.chezmoiexternals/tpm.yaml`)
and bootstraps the plugin list below on the first `tmux` launch thanks
to the `if "test ! -d ~/.tmux/plugins/tmux-resurrect"` guard just
before the `run` line.

| Plugin | Role |
|---|---|
| `tmux-plugins/tpm` | Plugin manager itself |
| `tmux-plugins/tmux-sensible` | Curated sane defaults (loaded automatically) |
| `tmux-plugins/tmux-resurrect` | Manual save / restore: `prefix Ctrl-s` to save, `prefix Ctrl-r` to restore |
| `tmux-plugins/tmux-continuum` | Auto-save every 15 min, auto-restore on start (`@continuum-restore on`) |
| `tmux-plugins/tmux-prefix-highlight` | Status-bar color flips while the prefix is held |
| `tmux-plugins/tmux-battery` | Battery % in the status bar (auto-disabled on hosts without a battery) |

---

## 9. References

- `man tmux` — the source of truth for every option and binding.
- [tmux 3.2 changelog](https://github.com/tmux/tmux/blob/3.2/CHANGES) —
  `set-clipboard` introduced here.
- [tmux 3.6 changelog](https://github.com/tmux/tmux/blob/3.6/CHANGES) —
  per-pane scrollbars introduced here.
- [christoomey/vim-tmux-navigator](https://github.com/christoomey/vim-tmux-navigator)
  — the canonical pattern for unified `C-h/j/k/l` between Neovim and
  tmux panes (deferred — see §10).
- [tmux-plugins/tpm](https://github.com/tmux-plugins/tpm) — the
  plugin manager used here.
- [tmux-plugins/tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect) —
  session persistence plugin.
- [tmux-plugins/tmux-continuum](https://github.com/tmux-plugins/tmux-continuum) —
  auto-save companion to resurrect.
- OSC 52 clipboard spec — covered by tmux's `set-clipboard on`,
  Neovim's `vim.g.clipboard='osc52'`, and Alacritty's built-in
  handler.

---

## 10. Deferred Ideas (skipped during the 2026-08-30 review)

Each entry below was evaluated during the review but deferred. They
are recorded here so that they can be re-enabled later without
rediscovering the rationale.

### 10.1 vim-tmux-navigator (deferred — no Neovim plugin installed)

`Ctrl-h/j/k/l` unifies Neovim-split navigation and tmux-pane
navigation into a single chord. Highest single-leverage productivity
plugin for Neovim users per every surveyed guide.

**To enable**:
1. Install the Neovim plugin in your editor config
   (`christoomey/vim-tmux-navigator`).
2. Add the next four lines to `tmux.conf` (matches the plugin's
   recommended upstream pattern):
   ```tmux
   is_vim="ps -o state= -o comm= -t '#{pane_tty}' \
           | grep -iqE '^[^TXZ ]+ +(\\S+\\/)?g?(view|n?vim?x?)(diff)?$'"
   bind-key -n 'C-h' if-shell "$is_vim" 'send-keys C-h'  'select-pane -L'
   bind-key -n 'C-j' if-shell "$is_vim" 'send-keys C-j'  'select-pane -D'
   bind-key -n 'C-k' if-shell "$is_vim" 'send-keys C-k'  'select-pane -U'
   bind-key -n 'C-l' if-shell "$is_vim" 'send-keys C-l'  'select-pane -R'
   ```
3. **Conflict**: `prefix C-h` / `prefix C-l` for previous / next
   window use the same chord (without prefix), which clashes with
   `C-h` / `C-l` from vim-tmux-navigator. Drop the window-nav bindings
   (the `bind -r C-h previous-window` and `bind -r C-l next-window`
   lines) when you turn the navigator on.

### 10.2 One-key multi-pane layouts (deferred — personal taste)

`M-q` → four-pane quad, `M-1` → 2-pane horizontal, `M-2` → 2-pane
vertical, used heavily in "AI coding" workflows for running parallel
agents.

**To enable**, add a block like:
```tmux
bind -n M-q send-keys tmux new-session -d \; split-window -h \; \
    split-window -v -t 0 \; split-window -v -t 2 \; select-pane -t 0
bind -n M-1 send-keys tmux new-session -d \; split-window -h \; select-pane -t 0
bind -n M-2 send-keys tmux new-session -d \; split-window -v \; select-pane -t 0
```

Note: each binding opens a **new** session rather than reusing the
current window. Adapt if a layout-spawn-in-current-window variant is
preferred.

### 10.3 Nested-tmux prefix discipline (deferred — not yet needed)

When SSH-ing into a remote that also runs tmux, having two prefixes
collides. The standard remedy is to leave the local prefix at `C-a`
and set the remote tmux's prefix to `C-b` (or vice versa), then use
`prefix prefix` to send the key to the inner session.

This is already partly handled by `prefix2 C-b`: pressing `C-a C-b`
on the outer tmux drops a literal `C-b` into the remote session's
prefix slot, which works as a prefix there. Adopt a per-host config
only if nested sessions become a daily workflow.

### 10.4 Layout-spawn script (deferred — same family as 10.2)

If the one-key layouts in 10.2 grow to more patterns, move them into
a shell script (e.g. `~/.local/bin/tmux-layout-quad`) and bind to
`run-shell "tmux-layout-quad"` instead of inlining the commands.

---

## 11. Change Log

- **2026-08-30** — Added `prefix2 C-b`, `set-clipboard on`,
  mnemonic `|` / `-` splits (with `%` / `"` retained), uppercase
  `H/J/K/L` pane swap, copy-mode `V` / `C-v`, `P` paste, `C-h` / `C-l`
  window nav, `<` / `>` window swap, `aggressive-resize`,
  `allow-rename off`, activity monitor, `repeat-time 300`,
  `status-position top`, pane-border-style, `pane-scrollbars`,
  `tmux-resurrect`, `tmux-continuum`, `tmux-prefix-highlight`,
  `tmux-battery`, and the auto-install plugin guard.
- **2026-08-30 (earlier)** — Initial `prefix C-a` and TPM setup.
