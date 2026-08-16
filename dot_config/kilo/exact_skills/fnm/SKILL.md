---
name: fnm
description: Node.js version management with fnm. Load before any node/npm/pnpm/yarn/npx command to ensure the correct Node version is active.
---

# Fast Node Manager (`fnm`)

Use `fnm` for all Node.js version management. Run `fnm use --install-if-missing` before any Node command in a project.

## Setup

If `$FNM_DIR` is empty, bootstrap first:

```bash
eval "$(fnm env --shell zsh)"
```

## Version Detection

fnm reads version from these files (priority order): `.node-version` > `.nvmrc` > `package.json#engines.node`. When a project has any of these, this skill applies.

## Commands

```bash
fnm use --install-if-missing          # run before any node/npm/npx/pnpm/yarn
fnm install --lts                     # install latest LTS
fnm install --latest                  # install latest release
fnm install <version>                 # e.g. 22, 20.5, lts/iron
fnm use <version>                     # switch to installed version
fnm exec --using=<version> <cmd>      # one-off command with specific version
fnm current                           # print active version
fnm list                              # list installed versions
fnm list-remote                       # list available versions
fnm default <version>                 # set global default
```

If `fnm use --install-if-missing` fails (no version dotfile), fall back:

```bash
fnm install && fnm use
```

## Rules

- Never use `nvm`, `n`, or `volta` — only `fnm`
- Always run `fnm use --install-if-missing` before any Node command in a project with a version dotfile
- Use the project's existing package manager (`npm`, `pnpm`, `yarn`); do not switch
- For `corepack` projects: `fnm install <version> --corepack-enabled`

## If fnm Is Not Installed

Check `.node-version`, `.nvmrc`, or `package.json#engines.node` for the required Node version. Recommend the user install `fnm`:

```bash
curl -fsSL https://fnm.vercel.app/install | bash
```

Do NOT run the install command — only recommend it.
