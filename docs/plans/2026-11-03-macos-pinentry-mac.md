---
status: completed
goal: Point gpg-agent at pinentry-mac on macOS only, without touching the Linux path.
owner: agent
last-updated: 2026-11-03
---

# Give macOS a GUI pinentry prompt

## Goal

On macOS, `gpg-agent` currently runs the compiled-in default pinentry, which is
`pinentry-curses`. Any gpg prompt from a process without a TTY fails. This plan
sets `pinentry-program` to `pinentry-mac` on macOS, and leaves the Linux
behaviour byte for byte unchanged.

## Scope

In:

- `private_dot_gnupg/private_gpg-agent.conf.tmpl`
- `.agents/docs/macos-host-handoff.md` (one troubleshooting row)
- `.agents/docs/cache/pinentry/2026-11-03-macos-pinentry-options.md` (the
  "Consequences for this repo" paragraph)
- The memory entry about the macOS pinentry state

Out:

- Linux. The wrapper, the switcher, the ignore block and the `pinentry-program`
  line for Linux stay exactly as they are.
- `.chezmoiignore`. No path enters or leaves the target state.
- `pinentry-touchid`, `pinentry-mac-keychain`, smartcards.
- The macOS keychain preferences (`org.gpgtools.common`). They are host
  preferences, not repo state.
- `docs/reports/2026-11-03-macos-host-portability.md`. It is a dated report and
  records what was true that day.

## Existing constraints

- The live `~/.gnupg/gpg-agent.conf` matches the render today:
  `chezmoi diff ~/.gnupg/gpg-agent.conf` exits 0 with no output.
- Homebrew builds `gnupg` with
  `--with-pinentry-pgm=#{opt_bin("pinentry")}/pinentry`, and that `pinentry` is
  a symlink to `pinentry-curses`. A missing `pinentry-program` line therefore
  means a terminal-only prompt, not a GUI one.
- The Homebrew prefix differs by architecture (`/opt/homebrew` on Apple
  Silicon, `/usr/local` on Intel), so a hardcoded path is wrong.
- `lookPath` is already used in `dot_agents/exact_rules/runtime-tools.md.tmpl`.
  `chezmoi execute-template` on this host resolves `lookPath "pinentry-mac"`
  to `/opt/homebrew/bin/pinentry-mac`.
- The 2026-08-05 post-mortem rejected a helper that *rewrites*
  `gpg-agent.conf` at runtime. A static line in a chezmoi-managed file is a
  different thing and is allowed.
- `chezmoi apply` needs the user's approval, per the destructive-actions rule.

## Refined approach

One conditional line in the template's non-Linux branch, guarded by
`eq .chezmoi.os "darwin"` and `lookPath "pinentry-mac"`. The guard keeps three
properties:

1. Linux output does not change.
2. A macOS host without `pinentry-mac` keeps today's curses default, so an
   apply never points the agent at a missing binary.
3. No path is hardcoded, so an Intel Mac works too.

The whole change is one file. No script, no wrapper, no runtime state.

## Implementation steps

1. Replace the `{{ else }}` comment branch in
   `private_dot_gnupg/private_gpg-agent.conf.tmpl` with the macOS branch, and
   add the guarded `pinentry-program` line. The target content:

   ```gotmpl
   # ~/.gnupg/gpg-agent.conf
   #
   {{ if eq .chezmoi.os "linux" }}# The pinentry wrapper is the pinentry-program of gpg-agent.
   # The switcher in ~/.shell/helper manages that line. Chezmoi rewrites this
   # file on every apply, so run the switcher again after an apply.
   {{ else if and (eq .chezmoi.os "darwin") (lookPath "pinentry-mac") }}# pinentry-mac gives gpg-agent a GUI dialog that works without a TTY and can
   # save the passphrase in the login keychain. For a terminal prompt instead,
   # export PINENTRY_USER_DATA=USE_CURSES=1 in that shell. The line is omitted
   # when the binary is missing, so the agent keeps its built-in default.
   {{ else }}# No pinentry-program line on purpose. gpg-agent uses its built-in default
   # pinentry. The pinentry-switch helper and the pinentry wrapper are not
   # deployed, so this file is the only owner of the agent settings and
   # chezmoi rewrites them on every apply.
   {{ end }}{{ if eq .chezmoi.os "linux" }}pinentry-program {{ .chezmoi.homeDir }}/.shell/helper/pinentry-wrapper
   {{ else if and (eq .chezmoi.os "darwin") (lookPath "pinentry-mac") }}pinentry-program {{ lookPath "pinentry-mac" }}
   {{ end }}enable-ssh-support
   ```

   This exact shape was rendered with `chezmoi execute-template` and produces
   no blank lines and no stray whitespace.

2. Prove the render, without writing anything:

   ```sh
   chezmoi cat ~/.gnupg/gpg-agent.conf
   chezmoi diff
   ```

   Expected: the cat shows `pinentry-program /opt/homebrew/bin/pinentry-mac`;
   the diff lists only `~/.gnupg/gpg-agent.conf`.

3. Ask for approval, then run `chezmoi apply --dry-run` and
   `chezmoi apply ~/.gnupg/gpg-agent.conf`.

4. Reload and test:

   ```sh
   gpg-connect-agent reloadagent /bye
   echo test | gpg --clearsign > /dev/null
   ```

   Expected: the pinentry-mac dialog, and `pgrep -fl pinentry-mac` shows the
   process.

5. Update the docs: the `gpg reports a missing pinentry` row in
   `.agents/docs/macos-host-handoff.md`, the consequence paragraph in the
   cache entry, and the memory entry that says macOS renders no line.

6. Commit the working tree.

## Risks and mitigations

- Risk: `lookPath` returns empty when chezmoi runs with a minimal PATH (GUI or
  launchd launch), so the line silently disappears. Mitigation: the agent then
  falls back to curses, which is today's behaviour. No failure. Step 2 catches
  it on any host.
- Risk: `pinentry-mac` cannot reach the window server when the agent was
  started from an SSH-only session, so the prompt hangs. Mitigation:
  `PINENTRY_USER_DATA=USE_CURSES=1` in that shell, stated in the template
  comment. Not set globally, because it would disable the GUI prompt
  everywhere.
- Risk: the keychain caches the passphrase, and "Save in Keychain" is
  pre-checked (`UseKeychain` defaults to YES). Mitigation: a user decision, not
  a repo change. `defaults write org.gpgtools.common DisableKeychain -bool yes`
  turns the checkbox off.
- Risk: `enable-ssh-support` stays on, so SSH authentication through gpg-agent
  now shows the GUI dialog too. Accepted: that is the point of the change.

## Open questions

None. Both resolved on 2026-11-03 (see Decisions).

## Decisions

- 2026-11-03: guard the line with `eq .chezmoi.os "darwin"` and `lookPath`
  rather than a hardcoded Homebrew path, because the prefix differs by
  architecture and the binary may be absent.
- 2026-11-03: leave `.chezmoiignore` alone. Nothing is newly deployed or
  removed.
- 2026-11-03: disable the keychain save on this host
  (`defaults write org.gpgtools.common DisableKeychain -bool yes`), so the
  passphrase lives only in the agent cache.
- 2026-11-03: put the `PINENTRY_USER_DATA=USE_CURSES=1` export in
  `dot_shell/zsh/12-gpg.zsh`, conditional on `$SSH_CONNECTION` and darwin, so
  the GUI prompt survives everywhere else.

## Current status

Done on 2026-11-03. The two targets were applied, `chezmoi diff` on them is
empty, and `gpg --clearsign` launched
`/opt/homebrew/Cellar/pinentry-mac/1.3.1.1/.../pinentry-mac` and signed with
exit 0. The keychain default is written, so the dialog carries no save
checkbox.
