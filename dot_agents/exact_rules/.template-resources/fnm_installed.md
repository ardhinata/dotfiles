Node.js work requires `fnm`. Use `fnm`, never `nvm`, `n`, or `volta`.

The user's interactive shell switches the Node version on `cd`, because
`dot_shell/zsh/10-common-export.zsh` runs `fnm env --use-on-cd`. The agent's
tool shell does not: it runs a fresh non-interactive bash. In a project with a
`.node-version`, `.nvmrc`, or `package.json#engines.node` file, run
`fnm use --install-if-missing` before the first `node`, `npm`, `npx`, `pnpm`,
or `yarn` command. Outside such a project the shell default applies.

Use the project's own package manager. Do not run `fnm install` yourself.
Offer the command to the user.

```bash
fnm install --lts          # install latest LTS
fnm install <version>      # e.g. 22, 20.5, lts/iron
fnm use <version>          # switch to an installed version
fnm current                # print the active version
fnm list                   # list installed versions
fnm exec --using=<v> <cmd> # one-off command with a specific version
```

For a `corepack` project, install with `fnm install <version>
--corepack-enabled`.
