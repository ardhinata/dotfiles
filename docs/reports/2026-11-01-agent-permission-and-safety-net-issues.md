---
status: fixed
severity: minor
captured: 2026-11-01
resolved: 2026-11-02
---

# Agent permission and safety-net issues

Findings about the harness permission rules and the cc-safety-net policy on
this host. All three are fixed. The text below keeps the original analysis,
and each finding ends with the fix that landed.

## Summary

Three findings. Each one was a configuration problem, not a code problem.

| # | Finding | Where | Status |
|---|---|---|---|
| 1 | The OpenCode shell rules deny a recursive delete of any path, so the safe-delete carve-out in `destructive-actions.md` never fires | `dot_config/opencode/private_opencode.jsonc` | fixed |
| 2 | cc-safety-net has every secret file class rule turned off, and the rule that guarded a recursive delete outside the working directory | `private_dot_cc-safety-net/private_policy.json` | fixed |
| 3 | The shellx helper is world-readable and holds the master secret in two places | `dot_shell/helper/private_executable_shellx.tmpl` | fixed by the shellx plan |

## Findings

### 1. The OpenCode shell rules deny safe deletes

**Steps to reproduce**

Run either command from any directory.

```sh
rm -rf /tmp/opencode/sb
rm -rf ./sb
```

**Expected**

Both are refused by a rule that names a dangerous path, not every path. The
personal rule `destructive-actions.md` states that a recursive delete inside
the working directory needs no approval when the agent created the file.

**Actual**

Both are denied. The permission block contains `rm -*rf /*`, `rm -*rf ~*`,
`rm -*rf ./*` and `rm -*rf ../*`. The last two cover the relative form, so
every recursive delete is refused. The carve-out in `destructive-actions.md`
never fires for `rm -rf`.

The rules are also mostly redundant. cc-safety-net already blocks `rm -rf /`
and `rm -rf ~` through its catastrophic rules, which no policy can disable.

**Fixed**

The block now holds four rules: `rm -*rf /`, `rm -*rf ~*`, `rm -*fr /` and
`rm -*fr ~*`. The root and the home directory stay blocked at the harness
level, and cc-safety-net blocks them as well.

The rest of the class moved to cc-safety-net. Its
`rm.recursive-force-outside-cwd` rule blocks a recursive delete outside the
working directory, and the temporary roots `/tmp` and `/var/tmp` count as
scratch space. The measured result after the change:

| Command | Result | Owner |
|---|---|---|
| `rm -rf ./sb` | allowed | inside the working directory |
| `rm -rf /tmp/opencode/sb` | allowed | temporary root |
| `rm -rf ../sb` | blocked | outside the working directory |
| `rm -rf /etc/foo` | blocked | outside the working directory |
| `rm -rf ~/foo` | blocked | OpenCode rule and cc-safety-net |
| `rm -rf /` | blocked | OpenCode rule and cc-safety-net |

### 2. cc-safety-net has the secret rules disabled

**Steps to reproduce**

Read `~/.cc-safety-net/policy.json`.

**Expected**

The secret protection rules cover the file classes the repo rules forbid:
`.age`, `.asc`, `.pem`, `*.key`, `.env`.

**Actual**

`secret_protection.overrides` sets `secret.ext.pem`,
`secret.ext-pattern.key`, `secret.ext.asc`, `secret.basename.env`,
`secret.pattern.env-variant` and `secret.ext.ovpn` to `off`. The repo rule
file in `.agents/rules/chezmoi-source-project.md` covers `.age`, `.asc`,
`.decrypted`, the `encrypted_` prefix, path keywords and
`.encryption_keys/`. The layer below it was therefore off for `.pem`, `*.key`
and `.env` outside those paths.

`destructive_command_protection.overrides` set
`rm.recursive-force-outside-cwd` to `off`, so a recursive force delete
outside the working directory was not guarded.
`destructive_command_protection.allow_paths` was empty, while
`secret_protection.allow_paths` listed the three SSH allowlist paths.

No user rule file existed, so `~/.cc-safety-net/rules/rule.json` was absent.
The `ssh` gap recorded in project memory had nowhere to be fixed.

**Fixed**

`secret_protection.overrides` is empty and
`rm.recursive-force-outside-cwd` is on again. The measured result:

| Command | Result |
|---|---|
| `cat ~/.local/share/shellx/master.key` | blocked |
| `cat .encryption_keys/personal_pq.secret.key` | blocked |
| `cat ~/.config/opencode/opencode.jsonc` | allowed |
| `cat README.md` | allowed |

The `ssh` gap closed itself. cc-safety-net 2.7.1 treats `ssh` as a built-in
transparent wrapper, so `ssh host rm -rf ~` is blocked without a user rule
file. An A/B test with and without `ssh` in `transparent_wrappers` gave the
same result. The quoted form `ssh host 'rm -rf ~'` stays allowed, because the
analyzer keeps a quoted argument as one token. The command runs on the remote
host, not on this machine.

`destructive_command_protection.allow_paths` stays empty. The temporary roots
`/tmp` and `/var/tmp` are allowed by the rule itself.

The `git` and `find.delete` overrides stay off. `git restore` and
`git checkout --` are normal work, and `find . -delete` inside the working
directory is blocked by the rule, so the agent would lose a cleanup path.

### 3. The shellx helper is world-readable and holds the master secret

**Steps to reproduce**

```sh
stat -c '%A' ~/.shell/helper/shellx
stat -c '%A' ~/.shell/helper/__pycache__/shellx_impl.cpython-314.pyc
```

**Expected**

The helper is not readable by other users, and the master secret is not in
a file that a scanner can read.

**Actual**

The helper was `0755`. It carried `SHELLX_NONCE_DEFAULT` and
`SHELLX_STATIC_PW_DEFAULT` as plain literals. The `.pyc` beside it was
`0644` and carried a second copy of the same literals. Any local user could
derive the store key and decrypt every blob. The `0700` store directory and
the `0600` blobs bought nothing against a local user.

**Fixed**

Step 8 of the
[shellx helper optimization plan](../plans/2026-11-01-shellx-helper-optimization.md)
landed on 2026-11-02. The helper is now `0700`. The implementation, the key
module, and the bytecode are `0600`. The master key moved to
`~/.local/share/shellx/master.key` with mode `0600`. A scan of `~/.shell`
finds no copy of the secret.

## Environment

- opencode 2.2.5, permission block in `dot_config/opencode/private_opencode.jsonc`
- cc-safety-net 2.7.1, plugin at `~/.cache/opencode/npm/cc-safety-net@latest`
- Python 3.14.9, chezmoi 2.73.3

## Related

- [Shellx helper optimization plan](../plans/2026-11-01-shellx-helper-optimization.md)
- `.agents/rules/chezmoi-source-project.md` — the repo secret handling rules
- `~/.agents/rules.personal.d/destructive-actions.md` — the carve-out that finding 1 defeated
