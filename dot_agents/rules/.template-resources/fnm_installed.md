# fnm - Fast Node Manager

Node.js work requires `fnm`. The shell switches the version on `cd` when a
project has a `.node-version`, `.nvmrc`, or `package.json#engines.node`
file, because `dot_shell/zsh/10-common-export.zsh` runs `fnm env
--use-on-cd`.

In a project with one of those files, run `fnm use --install-if-missing`
before the first node/npm/npx/pnpm/yarn command. Outside such a project the
shell default applies.

Use `fnm`, never `nvm`, `n`, or `volta`. Use the project's own package
manager. Do not run the install command; recommend it to the user.

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
