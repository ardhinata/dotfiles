# Personal Quirks & Misc Rules

Short, catch-all rules that don't warrant their own rule file. Add new rules here when the topic is narrow, stable, and personal rather than project-specific.

## Privilege Escalation — Always Ask

- **Never run `sudo` without explicit user confirmation.** When a task requires root, surface the exact command(s) and reason via the `question` tool first, then wait for approval.
- This applies to direct `sudo ...` invocations, passwordless escalation helpers, and any shell pattern that ends up elevating (e.g. `sudo -E`, `pkexec`, `doas`). Re-confirm per command — once is not forever.
- If a tool's output implies root was silently elevated, stop and re-ask.

## `~/.ssh/` — Read Allowlist

- The agent **may read/inspect** only:
  - `~/.ssh/config`
  - `~/.ssh/config.d/` (any file inside)
- **All other paths under `~/.ssh/` are prohibited** for both reading and writing unless the user explicitly opens them for a specific task. This includes (non-exhaustive): `authorized_keys`, `known_hosts`, `known_hosts.old`, private keys (`*.pem`, files in `~/.ssh/keys/`, `id_*`, `kilo-deploy-*`, etc.), their `.pub` siblings, and any other key material.
- Treat any key file's contents as a secret even when the filename looks innocuous. Never include key material in responses, logs, or commits.

## Agent-Created SSH Keys — Use `~/.ssh/kilo-keys/`

- When the agent generates a new SSH key on the user's behalf, place it under **`~/.ssh/kilo-keys/`** (the only `~/.ssh/` subdirectory that is both creatable and inspectable by the agent).
- Create the directory if missing: `mkdir -p ~/.ssh/kilo-keys && chmod 700 ~/.ssh/kilo-keys`.
- Permissions for new keys inside it: `chmod 700` on the directory, `chmod 600` on private keys, `chmod 644` on `.pub` siblings.
- Never overwrite an existing key without asking. Pick a descriptive filename (e.g. `github-work-2026-07`) and tell the user the absolute path and fingerprint after generation.

## Plans — See plans.md

Planning has its own workflow (locations, pre-merge scan, milestone updates, memory pointers) — see **`plans.md`** in this directory.
