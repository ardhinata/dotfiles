---
status: open
severity: minor
captured: 2026-11-01
---

# Agent permission and safety-net issues

Findings about the harness permission rules and the cc-safety-net policy on
this host. None of them block the current work. They are recorded here and
addressed after the shellx work finishes.

## Summary

Three findings. Each one is a configuration problem, not a code problem.

| # | Finding | Where | Status |
|---|---|---|---|
| 1 | The OpenCode shell rules deny a recursive delete of any absolute path, so the safe-delete carve-out in `destructive-actions.md` never fires | `dot_config/opencode/private_opencode.jsonc` | open |
| 2 | cc-safety-net has every secret file class rule turned off, and the rule that guarded a recursive delete outside the working directory | `~/.cc-safety-net/policy.json` | open |
| 3 | The shellx helper is world-readable and holds the master secret in two places | `dot_shell/helper/executable_shellx.tmpl` | open, tracked in the shellx plan |

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

**Proposed fix**

Drop `rm -*rf /*`, `rm -*rf ./*` and `rm -*rf ../*`. Keep `rm -*rf /` and
`rm -*rf ~*`. Let the personal rule and cc-safety-net carry the rest.

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
`.encryption_keys/`. The layer below it is therefore off for `.pem`, `*.key`
and `.env` outside those paths.

`destructive_command_protection.overrides` sets
`rm.recursive-force-outside-cwd` to `off`, so a recursive force delete
outside the working directory is no longer guarded.
`destructive_command_protection.allow_paths` is empty, while
`secret_protection.allow_paths` lists the three SSH allowlist paths.

No user rule file exists, so `~/.cc-safety-net/rules/rule.json` is absent.
The `ssh` gap recorded in project memory has nowhere to be fixed.
`ssh host 'rm -rf ~'` is allowed.

**Proposed fix**

Re-enable the secret rules that the repo rules rely on, or narrow the
overrides to the exact paths the repo already excludes. Add the scratch roots
to `destructive_command_protection.allow_paths`. Create the user rule file
and add `ssh` to `transparent_wrappers`.

### 3. The shellx helper is world-readable and holds the master secret

**Steps to reproduce**

```sh
stat -c '%A' ~/.shell/helper/shellx
stat -c '%A' ~/.shell/helper/__pycache__/shellxcpython-314.pyc
```

**Expected**

The helper is not readable by other users, and the master secret is not in
a file that a scanner can read.

**Actual**

The helper is `0755`. It carries `SHELLX_NONCE_DEFAULT` and
`SHELLX_STATIC_PW_DEFAULT` as plain literals. The `.pyc` beside it is
`0644` and carries a second copy of the same literals. Any local user can
derive the store key and decrypt every blob, so the `0700` store directory
and the `0600` blobs buy nothing against a local user.

The fix is tracked in the shellx plan, because the same work detaches the
master secret and makes the helper `0700`.

## Impact

| Finding | Who is affected | Consequence |
|---|---|---|
| 1 | Every agent session | A delete of the agent's own scratch files needs a user approval, so a cleanup step stalls the run |
| 2 | Every agent session | One less layer of defence against a secret file that the repo rules do not cover |
| 3 | Any local user, and any file scanner | The store is decryptable by whoever can read the helper |

## Workaround

For finding 1, print the exact command in the reply and let the user run it.
For finding 2, the repo rules still cover the file classes the dotfiles
source uses. For finding 3, do not rely on the store directory mode as the
protection. Treat the master secret as exposed until the shellx plan lands.

## Environment

- opencode 2.2.1, permission block in `dot_config/opencode/private_opencode.jsonc`
- cc-safety-net 2.6.19, plugin at `~/.cache/opencode/npm/cc-safety-net@latest`
- Python 3.14.9, chezmoi 2.73.3

## Related

- [Shellx helper optimization plan](../plans/2026-11-01-shellx-helper-optimization.md)
- `.agents/rules/chezmoi-source-project.md` — the repo secret handling rules
- `~/.agents/rules.personal.d/destructive-actions.md` — the carve-out that finding 1 defeats
