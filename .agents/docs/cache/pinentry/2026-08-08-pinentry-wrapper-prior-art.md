---
source:
  - https://github.com/Paraphraser/set-gpg-pinentry-program
  - https://github.com/heathcliff26/pinentry-keyring
  - https://gist.github.com/io41/c4af3923c74c0da7596d2457009c6bc9
  - https://gist.github.com/BMTLab/55f3f7eba9e2fc041ee2c2f22d9e4cac
captured: 2026-08-08
freshness: stable
tags: [pinentry, gpg-agent, prior-art]
---

# Prior art — pinentry wrapper, manager, and selector

A chezmoi-managed pinentry wrapper invoked through `pinentry-program` is the
mainstream pattern, and at least one project solves the same runtime-switch
problem by mutating `gpg-agent.conf`.

Captured 2026-08-08 while designing the `~/.shell/helper/pinentry-wrapper`.

## Finding

Owning the wrapper is the well-trodden pattern. At least three independent
projects do it for unrelated reasons (1Password unlock, fingerprint unlock,
keyring-checkbox fix), and at least one project solves the same "switch
pinentry at runtime" problem by mutating `gpg-agent.conf` — the failure mode
this project rejected.

Community evidence also confirms that the system `/usr/bin/pinentry` wrapper
is unreliable on KDE/Wayland hosts, so owning the wrapper is the correct
premise, not only the comfortable one.

## Evidence

**Direct analogues (own-the-wrapper pattern).**

| Project | Purpose | Match |
|---|---|---|
| **io41/gist c4af3923** — `pinentry-1password.sh` | Fetches the passphrase from 1Password through `op read`. Installed at `~/.local/bin/pinentry-1password.sh`, configured at `~/.config/gpg-1password-pinentry/config.zsh`, pointed at by `pinentry-program` in `gpg-agent.conf`. Recovery: remove `pinentry-program` and run `gpg-connect-agent killagent /bye`. | Same shape, different backend source. Validates the pattern. |
| **BMTLab/gist 55f3f7eba9e2fc041ee2c2f22d9e4cac** — `pinentry-fingerprint.sh` v2.0.0 (2026-04-26) | Speaks Assuan natively. GETPIN → kdialog fingerprint prompt → fprintd-verify (3 retries) → kwallet-query → Assuan `D <data>` + `OK`. On failure returns `ERR 83886179` (canceled) so gpg-agent re-invokes. Optional `PINENTRY_FP_DEBUG=1` syslog logging. | Same shape, heavier: it talks Assuan directly, so the wrapper here can ignore Assuan and `exec` a real backend. |
| **heathcliff26/pinentry-keyring** | Go binary. Forces `OPTION allow-external-password-cache` and rewrites `SETKEYINFO --clear → SETKEYINFO pinenty-keyring-default-key` so the "save passphrase" checkbox appears. Install via Fedora COPR `heathcliff26/cli`. | Same install path, different transformation purpose. |
| **pinentry-kwallet** (Gentoo) | Standalone pinentry backed by KWallet. | Same pattern; distros ship it. |

**Switcher pattern (mutates `gpg-agent.conf`).** `Paraphraser/set-gpg-pinentry-program`
— `set-gpg-pinentry-program.sh`. `./set-gpg-pinentry-program curses` activates
`pinentry-program /usr/bin/pinentry-curses`. The implementation comments out
any active `pinentry-program` line, un-comments a matching `#pinentry-program`
block, or appends one if no inactive form exists, then reloads with
`gpgconf --reload gpg-agent`. macOS adds a LaunchAgent and delegate glue
layer for `pinentry-mac`. License MIT. Inspired by
drduh/YubiKey-Guide#504.

This is the closest direct analog for a runtime-switchable pinentry. It
solves the same goal by a mechanism this project rejected, because mutating
`gpg-agent.conf` is incompatible with chezmoi. It confirms the demand for a
switcher is real.

**Per-call override (`PINENTRY_USER_DATA` pattern).** a3nm on
unix.stackexchange.com/questions/236746 (2015) shows a wrapper script reading
the `PINENTRY_USER_DATA` environment variable: `gpg2` → curses,
`PINENTRY_USER_DATA=gtk gpg2` → gtk. Quoted: *"You can use the
`PINENTRY_USER_DATA` environment variable to give `gpg` information to pass to
the pinentry command. You then need to set `pinentry-program` to a custom
wrapper such as this that will run the curses or the GTK pinentry depending
on that variable. Note that this only seems to work with GPG 2.x."*

The Gentoo wiki (GnuPG, "Changing pinentry for SSH logins") uses the same
family with a different variable namespace: `export
PINENTRY_USER_DATA="USE_CURSES=1"` in `~/.bash_profile` when `SSH_CONNECTION`
is set, so pinentry-qt switches itself to curses.

This layer is an additional override channel, orthogonal to the mode file. The
wrapper can read both: the mode file first (persistent, user-set), then
`PINENTRY_USER_DATA` (per-invocation, caller-set), then auto-classification.

**Auto-classification rule.** The rule here is `SSH_CONNECTION` or
`SSH_TTY` set → curses, GNOME with `DISPLAY` → gnome3, other with `DISPLAY`
or `WAYLAND_DISPLAY` → qt, else curses. That is identical to the system
`/usr/bin/pinentry` wrapper shipped by the `gpg` package, which is why the
preexec approach should have worked in isolation. Community evidence shows
the system wrapper is bypassed on KDE/Wayland hosts:

- openSUSE forum, "ssh, gpg-agent and pinentry - no tty or curses?"
  (forums.opensuse.org/t/136910) — a user reports pinentry-qt is launched
  even when the KDE environment matches what the system wrapper should detect.
  Diagnosis: *"the wrapper script /usr/bin/pinentry does not do what it was
  supposed to do ... I wonder if the choice of pinentry-qt was compiled in
  gpg."*
- preining.info blog, "Arch Linux: Fix gcr-agent interfering with
  ssh/gpg-agent" (2024-06) — `gcr-agent` ships a wrong `SSH_AUTH_SOCK` symlink
  that overrides gpg-agent, worked around with `PINENTRY=pinentry-qt` in
  `/etc/environment.d/`. Same family as the "agent interposed by another
  process" failure seen on this host.
- bbs.archlinux.org/viewtopic.php?id=184650 — `pinentry-curses` fails when
  invoked via `ssh` even though it works for direct `gpg` use, because the
  agent's TTY view is stale. Same root cause as the
  `Match host * exec "gpg-connect-agent updatestartuptty /bye"` workaround
  already in this project's `dot_ssh/config`.
- SuperUser 520980 — the canonical "force console pinentry" answer recommends
  `pinentry-program /usr/bin/pinentry-tty` plus
  `gpg-connect-agent reloadagent /bye`. The wrapper here uses
  `gpgconf --reload gpg-agent` instead; Paraphraser and io41 both confirm
  `gpgconf --reload` is the more reliable form.

**Distro-level switchers.** Gentoo ships `eselect pinentry`, Debian and Ubuntu
ship `update-alternatives`, and Homebrew has `pinentry` and `pinentry-mac` as
separate formulae. These change a symlink or alternative, so
`~/.gnupg/gpg-agent.conf` overrides them — the same override order as the mode
file here. They are package-manager solutions, not user-script solutions.

## Why it matters

Six refinements followed from the survey:

1. Use `gpgconf --reload gpg-agent` rather than
   `gpg-connect-agent reloadagent /bye`.
2. Add `PINENTRY_USER_DATA` as a third precedence level, below the mode file,
   so a caller can override per invocation. Cheap, and it expands usability.
3. `pinentry-switch status` should `exec` the wrapper's `--query` subcommand
   rather than re-implement discovery. BMTLab's `GETINFO flavor` is the same
   pattern: expose identity through an Assuan query.
4. Log to stderr only. None of the surveyed projects ship verbose logging by
   default, and io41 logs only with `PINENTRY_FP_DEBUG=1`.
5. Write recovery instructions. io41's "remove the `pinentry-program` line
   plus `gpg-connect-agent killagent /bye`" is a good template.
6. Note the path prefix in the wrapper. It hard-codes `/usr/bin/pinentry-<mode>`
   paths, so a non-`/usr` install needs the prefix edited.

## Scope

The wrapper design in this project. Prior art is stable: the tool APIs
(`gpg-agent --pinentry-program`, the Assuan protocol, `gpgconf --reload`) have
not changed in years.

## Uncertainty

Re-verify only if gpg-agent or pinentry releases a major protocol change. The
survey did not test any of the projects; it read their sources and READMEs.

## Sources

- https://github.com/Paraphraser/set-gpg-pinentry-program (MIT, single bash script, mtime 2024+)
- https://github.com/heathcliff26/pinentry-keyring (Apache-2.0, Go binary, Fedora COPR)
- https://gist.github.com/io41/c4af3923c74c0da7596d2457009c6bc9 — pinentry-1password.sh (zsh + `op` CLI)
- https://gist.github.com/BMTLab/55f3f7eba9e2fc041ee2c2f22d9e4cac — pinentry-fingerprint.sh v2.0.0 (2026-04-26, MIT, bash + fprintd + kwallet-query)
- https://unix.stackexchange.com/questions/236746 — a3nm's PINENTRY_USER_DATA wrapper pattern (2015)
- https://wiki.gentoo.org/wiki/GnuPG — `eselect pinentry` + `PINENTRY_USER_DATA="USE_CURSES=1"` for SSH logins
- https://wiki.archlinux.org/title/GnuPG — canonical `Match host * exec "gpg-connect-agent UPDATESTARTUPTTY /bye"` workaround
- https://forums.opensuse.org/t/ssh-gpg-agent-and-pinentry-no-tty-or-curses/136910 — community report of system wrapper being bypassed
- https://www.preining.info/blog/2024/06/arch-linux-fix-gcr-agent-interfering-with-ssh-gpg-agent — gcr-agent override precedent
- https://bbs.archlinux.org/viewtopic.php?id=184650 — pinentry-curses + ssh stale-TTY issue (same root cause)
- https://iifx.dev/en/articles/460136063/gpg-gui-prompt-disappeared-a-guide-to-pinentry-setup — generic pinentry-program guide
- https://superuser.com/questions/520980/how-to-force-gpg-to-use-console-mode-pinentry — canonical console-mode answer
- https://superuser.com/questions/1457167/i-want-to-make-gpg-use-gui-locally-and-cli-on-ssh — exact problem statement
- https://www.gnupg.org/documentation/manuals/gnupg/GPG-gnupg.html — `pinentry-program` as the documented extension point

## See also

- `docs/post-mortem/2026-08-05-pinentry-switcher.md` — the switcher design
  this survey supported
