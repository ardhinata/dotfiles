# pinentry

Facts about gpg-agent's pinentry extension point and the wrapper pattern
around it.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-08-08 | [Prior art — pinentry wrapper, manager, and selector](2026-08-08-pinentry-wrapper-prior-art.md) | 4 GitHub projects, Gentoo and Arch wikis, unix.stackexchange, SuperUser | stable | Four projects own the wrapper for unrelated reasons. One solves the same runtime-switch problem by mutating `gpg-agent.conf`, which is incompatible with chezmoi. |
| 2026-11-03 | [macOS pinentry options](2026-11-03-macos-pinentry-options.md) | Homebrew formulae, GPGTools source, jorgelbg and olebedev repos | stable | Five backends. Homebrew builds no Qt or GTK pinentry on macOS. The host now runs `pinentry-mac` (see the entry). |
