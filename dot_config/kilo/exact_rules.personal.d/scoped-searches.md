Search and inspection commands must stay within a **bounded path**. An unbounded home-directory scan (`grep -rn foo ~`, `rg foo $HOME`, `find ~`) traverses caches, browser profiles, package databases, `.git/`, `node_modules/`, encrypted bundles, and hundreds of thousands of unrelated files — slow, noisy, and likely to trip secret-file and symlink rules.

## When

About to run `grep -r`, `rg`, `find`, `fd`, or any tool that walks a directory tree.

## Default scope — the working directory

Start here unless an explicit reason says otherwise:

- For project work: the **current working directory** (`$PWD`). One tool call is enough.
- For mixed-source projects (chezmoi-style source-vs-target trees): the **source tree** the user named.

If the answer is "almost certainly in this project", do not widen.

## Escalate to a **named** managed dir, not the whole home

When the question is genuinely about a known global location, target that directory verbatim — never the parent:

| Looking for | Target dir (do not scan parent) |
|---|---|
| Global kilo config / rules / skills / agents | `~/.config/kilo/` |
| Global chezmoi source (your dotfiles) | `~/.local/share/chezmoi/` |
| gpg-agent config / state | `~/.gnupg/` |
| SSH config (allowlisted only) | `~/.ssh/config`, `~/.ssh/config.d/` |
| Shared agent context (notes/plans) | `~/.local/share/kilo/` |
| Shell history for this project | `~/.local/share/zsh/` or specific file |

If the question might touch multiple of these, run **one bounded call per dir** rather than one giant one.

Do not recurse into encrypted/sealed trees (`~/.gnupg/private-keys-v1.d/`, `~/.password-store/`, `~/.local/share/keyring/`, age-encrypted data dirs). Even filename discovery is gated.

## Process for a "where is X?" question

1. **First call**: project dir, targeted glob/grep on the obvious filename stem.
2. **No hit?** Ask yourself: is X global dotfiles, global kilo config, or env-level? If unclear, **ask the user which scope** before widening — most "where is X" questions are local in practice.
3. **Named escalation**: re-run with the specific bounded dir from the table above.
4. **No `grep -r ... ~` / `rg ... $HOME` / `find ~` without an explicit, exact target dir.** Always pass the deepest meaningful path.
5. `glob` is workspace-scoped by design — constrain with `path:` when you know the subtree.
6. Pass `--hidden` only when you intend to read dotfiles. `rg`/`grep` exclude them by default; do not flip that flag as a "just in case" move.
7. Use ripgrep when available — it auto-skips `.git/`, `node_modules/`, and respects `.gitignore`.
8. **Still no hit?** Report "not found in <scope>" and stop. Do not continue widening.

## Anti-patterns

- `grep -rn 'foo' ~` "to be safe" — costs minutes and floods the context with every browser cookie JS file.
- Disabling `--no-ignore` / `--hidden` to "see everything" — the ignore list is a feature, not friction.
