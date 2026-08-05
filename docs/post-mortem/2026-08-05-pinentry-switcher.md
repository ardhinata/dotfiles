# Pinentry switcher + dispatcher — post-mortem

**Status:** Implementation abandoned, rolled back. Repo is at `051234a` (the commit before the work began).

## Summary

A `pinentry-switch` shell helper plus an opt-in per-TTY dispatcher were
built to let the user flip between `pinentry-qt` / `pinentry-curses` /
`pinentry-tty` on demand and to handle the VSCode-tunnel SSH-signing
case where gpg-agent under `systemd --user` cannot launch pinentry on
its own. The helper rewrites `~/.gnupg/gpg-agent.conf` on every call;
the dispatcher adds a second source of truth
(`~/.cache/pinentry-mode/by-tty/${tty}.mode`).

The user surfaced a fundamental design flaw: **the helper mutates a
chezmoi-managed file**, so every `pinentry-switch` invocation makes the
deployed file diverge from the source, and the next `chezmoi apply`
silently overwrites the helper's edits. The dispatcher compounded the
problem with its own distributed state. Even after the dispatcher was
hardened (most-recent-TTY fallback, self-derived `GPG_TTY` export), the
underlying gpg-agent TTY-propagation issue in the VSCode tunnel was
not solved.

The user aborted the experiment. All five implementation commits were
reverted via `git reset --hard 051234a`.

## What was rolled back

| Commit | Subject |
|---|---|
| `18cc5ef` | pinentry-switch helper + opt-in per-TTY dispatcher |
| `2427a4e` | lift pinentry-classify, use `>!` for noclobber |
| `3091cb2` | gpg-agent.conf private (0600) |
| `2e52406` | `GPG_TTY=$(tty)` export in `10-common-export.zsh` |
| `3976cb1` | `Match host * exec "gpg-connect-agent updatestartuptty /bye"` in `~/.ssh/config` |
| `e57ec4a` | preload prezto environment module |

Files removed from the working tree:

- `dot_local/bin/executable_pinentry-switch-auto`
- `dot_shell/zsh/30-pinentry-switch.zsh`
- `dot_shell/zsh/31-pinentry-mode-hook.zsh`
- `dot_shell/zsh/completions/_pinentry-switch`
- `~/.local/bin/pinentry-switch-auto` (deployed)
- `~/.cache/pinentry-mode/` (cache + log)

System files removed (not in chezmoi):

- `/etc/sudoers.d/pinentry-env`

## Root cause

`pinentry-switch write-config + reload` is fundamentally incompatible
with a chezmoi-managed `~/.gnupg/gpg-agent.conf`. The user's model is
that the source-of-truth file in chezmoi is canonical and `apply`
enforces it; a helper that rewrites the deployed file in place makes
that model unusable. **A chezmoi-managed config file must not be
mutated outside `chezmoi apply`** — the helper wanted to do exactly
that, every time it ran.

The dispatcher tried to side-step this by reading per-TTY mode files
written by a `preexec` hook. That created a second source of truth
(cache files in `~/.cache/`) that the user could not reconcile with
chezmoi either. Even setting the chezmoi conflict aside, the
dispatcher did not solve the underlying issue: gpg-agent under
`systemd --user` does not propagate `GPG_TTY` to the pinentry child
(verified via env-trace), so any dispatcher that relies on the agent
forking pinentry with the user's TTY in its env is fighting the agent.

## What was tried during the session

1. Activated the dispatcher via `pinentry-switch auto --dispatcher`.
   `pinentry-program` was rewritten to the dispatcher binary.
2. Verified `Match exec` fires correctly:
   `debug1: Executing command: 'gpg-connect-agent updatestartuptty /bye'`.
3. Hardened the dispatcher with:
   - Most-recent-TTY mode-file fallback when `GPG_TTY` is empty.
   - Inverse sanitization (e.g. `dev-pts-5.mode` → `/dev/pts/5`).
   - Self-derived `GPG_TTY` export before exec'ing pinentry
     (because gpg-agent under systemd --user does not pass it through).
4. Verified end-to-end via env-trace (replaced `pinentry-program`
   with a wrapper that dumped its env, confirmed `GPG_TTY=` was empty).
5. End-to-end test from the user's VSCode tunnel terminal:
   `ssh -T git@github.com` returned
   `sign_and_send_pubkey: signing failed ... from agent: agent refused
   operation`. The dispatcher log showed only the 23:35:03 entry, then
   no new entries — because the user's `pinentry-switch curses` call
   had replaced the dispatcher with `/usr/bin/pinentry-curses` directly,
   and the manual switch still failed.

## Lessons learned

- **A chezmoi-managed config file must not be mutated outside
  `chezmoi apply`.** Any helper that needs to override a managed
  config must either (a) drive the override through the chezmoi source
  (e.g. a template that reads runtime state from elsewhere) or (b) own
  a sibling file that the source specifically *defers* to.
- **Don't ship a complex dispatcher on top of a helper that already
  breaks the user's model.** The helper's chezmoi conflict was visible
  the moment `pinentry-switch` ran the first time; the right move was
  to flag it then, not to keep iterating on the dispatcher's invocation
  path.
- **Don't try to "fix" the gpg-agent TTY-propagation bug (T6478) by
  bolting state on top of it.** The systemd --user agent's refusal to
  launch pinentry in a tunnel without a TTY is a known upstream bug;
  the only known workaround is the `Match exec` trick, and even that
  only works when the local terminal has a TTY that the agent can be
  told about. The dispatcher is a stronger version of the same band-aid
  and inherits the same limits.
- **Don't kill the systemd --user gpg-agent.** Doing so earlier in this
  experiment was wrong; the agent's supervision model is not the
  problem.

## What this plan does NOT solve

The underlying VSCode-tunnel gpg-agent SSH-signing problem is still
unresolved. The pre-existing `Match host * exec` + `GPG_TTY=$(tty)`
workaround may help in terminal sessions where the user has a real
local TTY, but it does not address the case where the user's tunnel
window has no visible display and the agent cannot launch any
pinentry. Reverting the implementation dropped both pieces; a future
attempt at this problem should start from the rollback point and
test the simplest possible `Match exec` + `GPG_TTY` flow first,
before introducing any helper or dispatcher.

## Pointer

The transient plan this post-mortem was promoted from is at
`.tmp/plans/2026-08-05-pinentry-switcher.md` (will be deleted when
this post-mortem is committed).
