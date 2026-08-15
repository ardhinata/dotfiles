When the agent generates a new SSH key on the user's behalf, place it under `~/.ssh/kilo-keys/` — the only `~/.ssh/` subdirectory the agent is allowed to create and inspect.

## When

About to create a new SSH keypair (deploy key, work-specific identity, one-off alias, etc.).

## Process

1. Confirm the user wants a new key, and that no existing key fits the purpose.
2. Create the directory if missing:
   ```bash
   mkdir -p ~/.ssh/kilo-keys && chmod 700 ~/.ssh/kilo-keys
   ```
3. Generate the keypair into that directory (e.g. `ssh-keygen -t ed25519 -f ~/.ssh/kilo-keys/<descriptive-name> -C "<comment>"`).
4. Set permissions:
   - `chmod 700` on the directory (already done in step 2).
   - `chmod 600` on private keys.
   - `chmod 644` on `.pub` siblings.
5. Tell the user the **absolute path** of the new key and its **fingerprint** (`ssh-keygen -lf <path>`).

## Naming

Pick a descriptive filename that includes:

- The platform or service (e.g. `github-work`, `gitlab-prod-deploy`).
- A short year-month tag (e.g. `-2026-07`) so concurrent keys don't collide.

Example: `github-work-2026-07`.

## Anti-patterns

- Overwriting an existing key silently — always ask first, even when the user says "make me a key".
- Putting keys directly under `~/.ssh/` (e.g. `~/.ssh/id_ed25519`) — those collide with the user's identity keys.
- Reading existing key contents to "see what we already have" before generating — see `ssh-read-allowlist.md`.
- Returning a key fingerprint to the user without telling them the path (or vice versa).

## References

- `~/.config/kilo/rules.personal.d/ssh-read-allowlist.md` — read constraints that motivate this location.
