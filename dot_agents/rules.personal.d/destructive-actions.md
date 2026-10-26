# Destructive Actions

Some commands destroy data. Ask the user before you run one. Print the exact
command in your reply so the user can run it themselves.

## Commands that need approval

- `rm -rf`, `rm -fr`, or `rm -r -f` on a path outside the working directory
- `git reset --hard`, `git clean -fd`, `git push --force`, `git push -f`
- `chezmoi apply`, `chezmoi re-encrypt`, `chezmoi update`
- `chmod`, `chown`, or `mv` on a path outside the working directory
- Any privilege escalation, including `sudo`, `pkexec`, and `doas`

A project instruction to apply chezmoi changes does not override this gate.

## Working directory

A recursive delete inside the working directory needs no approval when the
command removes a file the agent created in this session. Everything else
needs approval, including a bare relative path such as `rm -rf build`.

## What approval means

Stop. Show the command. Wait for a reply that approves it. Do not run a
different command instead, and do not run the command before the reply.
