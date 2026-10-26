# Scoped Searches

Search and inspection commands must stay within a **bounded path**. An unbounded
home scan (`grep -rn foo ~`, `rg foo $HOME`, `find ~`) crosses caches, browser
profiles, package databases, encrypted bundles, and secret files. It is slow,
noisy, and likely to trip secret-file rules.

## When

About to run `grep -r`, `rg`, `find`, `fd`, or any tree walk. Use the dedicated
tools first: `aft_search`, `aft_outline`, `aft_zoom`, `glob`, `grep`, `read`.
They are token-aware and already scoped to the workspace. This rule applies
when those tools cannot answer the question.

## Default scope

Search the current working directory. One call is enough. If the answer is
almost certainly in this project, do not widen.

## Named escalation

Target a known global location by its exact path, never its parent:

| Looking for | Target |
|---|---|
| Global agent config, rules, skills | `~/.config/opencode/`, `~/.agents/` |
| Global chezmoi source | `~/.local/share/chezmoi/` |
| gpg-agent config | `~/.gnupg/gpg-agent.conf`, `~/.gnupg/gpg.conf` (files, not the directory) |
| SSH config | `~/.ssh/config`, `~/.ssh/config.d/` |
| Shell history | `~/.zsh_history` |

Run one bounded call per directory. If the scope is unclear, ask which scope
instead of widening.

Never recurse into sealed trees: `~/.gnupg/private-keys-v1.d/`,
`~/.password-store/`, `~/.local/share/keyring/`, age-encrypted data dirs.

## Stop

If the search finds nothing in the named scope, report "not found in <scope>"
and stop. Do not continue widening.
