# Destructive Actions

Some commands destroy data. Ask the user before you run one. Print the exact
command in your reply so the user can run it themselves.

## Commands that need approval

- `rm -rf`, `rm -fr`, or `rm -r -f` on a path outside the working directory
- `git reset --hard`, `git clean -fd`, `git push --force`, `git push -f`
- `chezmoi apply`, `chezmoi re-encrypt`, `chezmoi update`
- `chmod`, `chown`, or `mv` on a path outside the working directory

## Working directory

A path inside the working directory needs no approval when the command removes
a file the agent created in this session.

## What approval means

Stop. Show the command. Wait for a reply that approves it. Do not run a
different command instead, and do not run the command before the reply.

`sudo` is not listed here. The `sudo-ask.md` rule owns it.
