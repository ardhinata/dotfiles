---
source:
  - https://formulae.brew.sh/formula/pinentry-mac
  - https://github.com/Homebrew/homebrew-core/blob/master/Formula/g/gnupg.rb
  - https://github.com/Homebrew/homebrew-core/blob/master/Formula/p/pinentry.rb
  - https://github.com/GPGTools/pinentry/tree/master/macosx
  - https://github.com/jorgelbg/pinentry-touchid
  - https://github.com/olebedev/pinentry-mac-keychain
  - https://jpmens.net/2025/04/04/overriding-gnupg-s-pin-entry/
captured: 2026-11-03
freshness: stable
tags: [pinentry, gpg-agent, macos, keychain, touch-id]
---

# macOS pinentry options

Five backends exist for a Mac. One is the terminal default, one is the
standard GUI dialog, two add Touch ID, one is a low-adoption smartcard tool.
There is no Qt or GTK pinentry on macOS through Homebrew.

## Current state on this host (2026-11-03)

- `gpg` 2.5.24, `pinentry` 1.3.3 and `pinentry-mac` 1.3.1.1 from Homebrew.
  `pinentry-touchid` is not installed.
- `~/.gnupg/gpg-agent.conf` carries no `pinentry-program` line on purpose.
- The effective backend is `pinentry-curses`. Homebrew builds `gnupg` with
  `--with-pinentry-pgm=#{opt_bin("pinentry")}/pinentry`, and that `pinentry` is a
  symlink to `pinentry-curses`.
- A terminal backend cannot prompt without a TTY. Proof:
  `printf 'GETPIN\n' | pinentry` returns
  `ERR 83918950 Inappropriate ioctl for device <Pinentry>`.

## The options

| Backend | Source | State | Needs | Notes |
|---|---|---|---|---|
| `pinentry-curses` (current) | Homebrew `pinentry` 1.3.3 | maintained | a TTY | zero config. Fails for GUI-launched gpg and over cron. |
| `pinentry-tty` | same formula | maintained | a TTY | cruder curses. same limits. |
| `pinentry-mac` | Homebrew `pinentry-mac` 1.3.1.1, GPGTools repo pushed 2025-04 | maintained | GUI session | native dialog. Optional login-keychain save. `PINENTRY_USER_DATA=USE_CURSES=1` falls back to curses for SSH. |
| `pinentry-touchid` | `brew tap jorgelbg/tap`, v0.0.3 (2022-08), repo pushed 2023-10 | dormant | pinentry-mac, Touch ID sensor | wraps pinentry-mac, keychain items guarded by `LAContext`. No Apple Watch fallback. README paths are `/usr/local`. |
| `pinentry-mac-keychain` | olebedev, Go, 5 stars, pushed 2026-03 | early | pinentry-mac | stores smartcard PINs in the keychain. too small to rely on. |
| no pinentry | — | — | — | `allow-preset-passphrase` + `gpg-preset-passphrase`, or move git signing to SSH keys. Removes the prompt instead of restyling it. |

`pinentry-qt`, `-gtk2`, `-gnome3`, `-fltk` are disabled in the Homebrew formula
(`--disable-pinentry-*`), so they do not exist here unless built by hand.

## pinentry-mac details

- Preferences live in the `org.gpgtools.common` defaults suite
  (`macosx/AppDelegate.m:37`). Keys: `UseKeychain` (default YES),
  `DisableKeychain`, `KeychainPath` (`macosx/KeychainSupport.m:33`).
  `org.gpgtools.pinentry-mac`, used by several posts, is not the domain the
  program reads.
- `PINENTRY_USER_DATA=USE_CURSES=1` makes it run the curses UI
  (`macosx/main.m:76-94`). Useful over SSH or when the GUI dialog would hang.
- Touch ID comes from the keychain access prompt, not from the program. The
  item is created with an ACL, so macOS offers Touch ID or Apple Watch when the
  item is read. That "Always allow" grant is the security trade-off: any process
  the user approves can read it afterwards.
- Setting the file once is static config. A runtime switcher that rewrites
  `gpg-agent.conf` is what the 2026-08-05 post-mortem rejected.

## Consequences for this repo

`private_dot_gnupg/private_gpg-agent.conf.tmpl` renders
`pinentry-program <lookPath pinentry-mac>` on macOS, and omits the line when the
binary is absent so the agent keeps its terminal default. The path comes from
`lookPath`, because the Homebrew prefix is `/opt/homebrew` on Apple Silicon and
`/usr/local` on Intel. `dot_shell/zsh/12-gpg.zsh` exports
`PINENTRY_USER_DATA=USE_CURSES=1` when the shell is an SSH login on darwin. The
keychain save is a host preference:
`defaults write org.gpgtools.common DisableKeychain -bool yes`. Reload the agent
after a change: `gpg-connect-agent reloadagent /bye`.
