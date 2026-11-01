---
status: draft
last-updated: 2026-11-01
---

# Optimize the shellx helper

## Goal

Make `shellx env NAME` cheap enough to run in a shell startup, close the open
correctness bugs, and move the master secret out of the world-readable
helper.

The order is fixed: correctness first, performance second, security third. A
bug that corrupts the store or loses a secret outranks any speed gain.

## Scope

In scope:

- `dot_shell/helper/executable_shellx.tmpl`
- `dot_shell/helper/test_shellx.py`
- `dot_shell/helper/.help/` and the shellx CHANGELOG
- `dot_shell/zsh/20-secret-env-load.zsh`
- `.chezmoiscripts/run_onchange_init-shellx-store.sh`
- The secret store migration and the age-encrypted export

Out of scope:

- The OpenCode permission block and the cc-safety-net policy. They are in
  [the report](../reports/2026-11-01-agent-permission-and-safety-net-issues.md).
- The legacy `runpriv` triple in `dot_shell/helper/`.
- The age export file format.

## Baseline

Measured on 2026-11-01 with `shellx env NAME` against the real store.

| Part | Cost |
|---|---|
| scrypt derivation | 72.7 ms |
| Import of 15 stdlib modules | 21.7 ms |
| Compile of the 33 KB source, no cached `.pyc` | 7.2 ms |
| Interpreter start and spawn | 11.3 ms |
| argparse parser build | 1.1 ms |
| Module body execution | under 0.1 ms |
| **Total** | **140.0 ms** |

The store holds 16 blobs. Each blob carries its own random salt, so the KDF
runs once per secret. Sixteen secrets in one call cost 1254.9 ms.

## Steps

### Step 1 — Deploy the committed change

Correctness.

The runtime decrypt loader is committed but not applied. Until the apply
runs, a new shell prints one missing-file line and the variable stays unset.

Run `chezmoi apply`. The apply also removes the old plaintext loader, through
`dot_shell/zsh/remove_20-ejson-environment-load.zsh`.

Verify: a new interactive shell has the variable set, and
`~/.shell/zsh/20-ejson-environment-load.zsh` no longer exists.

### Step 2 — Fix the store corruption in `shellx import --to`

Correctness. This is a data-loss bug.

`cmd_import` reads the index from the live store and writes it back to the
live store, even when `--to` names another directory. The source lines are
617 and 643 of `dot_shell/helper/executable_shellx.tmpl`.

The blobs land in the target directory. The index lands in the live store.
The live index then names blobs that do not exist there, so `shellx env` on
the live store fails with `missing blob`.

Fix: resolve the index path from `target_dir`, not from `_idx_path()`.

Verify: import into a scratch directory, then compare the live index before
and after. It must not change.

### Step 3 — Close the temp-file window

Correctness.

`_write_idx` and `cmd_import` open the temp file with the default mode and
call `chmod 0600` afterwards. A crash between the two calls leaves a
world-readable index or blob on disk.

Fix: create the temp file with `os.open(path, os.O_WRONLY | os.O_CREAT |
os.O_TRUNC, 0o600)`.

Verify: add a test that checks the mode of the temp file during the write.

### Step 4 — Remove the no-op bytecode step

Correctness.

`.chezmoiscripts/run_onchange_init-shellx-store.sh` runs
`python3 -m py_compile` on the deployed helper. Python never reads a `.pyc`
for a script that runs as `__main__`, so the step changes no timing. Its
only effect is a second world-readable copy of the master secret.

Fix: delete the step.

Verify: `chezmoi apply` writes no `.pyc` file.

### Step 5 — Cover the paths that were never tested

Correctness.

The `RESTRICTED` mode, a login shell, and the `shellx run` exec path were
never tested. The exec path decrypts every matching secret, so it pays the
same per-secret KDF cost.

Fix: add a test for each path, or record the manual check in the helper
CHANGELOG.

Verify: the test suite covers the three paths.

### Step 6 — Take the interpreter savings

Performance. Worth about 21 ms of the 140 ms.

1. Move the cold-path imports into the functions that need them. Drop
   `getpass`, `socket`, `subprocess`, `secrets` and `datetime` from module
   level. `Any` is unused, and `NoReturn` appears in one annotation.
   Measured effect: 140.0 to 128.9 ms.
2. Use `python3 -S` in the shebang. Measured effect: 121.2 to 119.2 ms in the
   prototype.
3. Split the helper into a thin launcher and an importable module, so the
   `.pyc` is used. Measured effect: 128.9 to 121.2 ms.

Do part 3 after step 8. The split puts the master secret into a second file
and a second `.pyc`, so it must follow the detachment.

Verify: run the timing script before and after.

### Step 7 — Change the key derivation function

Performance. Worth about 94 ms of the 140 ms.

The password is not a passphrase. `STATIC_PW` is the sha256 of the 64
character nonce in `~/.config/chezmoi/chezmoi.yaml`, and that nonce comes
from `randAlphaNum 64`. It holds at least 341 bits of entropy. scrypt
N=2^15 is key stretching, and key stretching protects a low entropy
password. It protects nothing here.

Design:

- Blob version 1 stays scrypt, so old blobs still decrypt.
- Blob version 2 uses HMAC-SHA512 over the per-blob salt.
- The encrypt path picks the version. Use the fast path only when the nonce
  is at least 32 characters. Otherwise keep scrypt, so a hand-typed nonce
  still gets stretched.

Migration. The store has 16 blobs. Run `shellx export` to write an
age-encrypted JSONC file, then `shellx import --force` to write the store
again with version 2 blobs.

The export lands in `.encrypted_data/env_store/` as an age file. The user
reads it and commits it. The plaintext never reaches the disk, because the
export pipes it into `chezmoi encrypt`.

The slug depends on `STATIC_PW`, and `STATIC_PW` does not change, so the
store path stays the same.

Verify: all 16 values round-trip byte-exactly, a version 1 blob still
decrypts, and the export file contains no plaintext.

Risk: this is the highest-risk step, because it rewrites every blob. Take a
copy of the store directory first.

Alternative: keep scrypt and derive one master key per store from a fixed
salt file. That costs one scrypt per process instead of one per secret. It
keeps the slow KDF and needs the same format change.

### Step 8 — Detach the master secret

Security.

The helper is `0755` and carries the nonce and `STATIC_PW` as plain
literals. The `.pyc` beside it is `0644` and carries a second copy. Any
local user derives the store key from the helper, so the `0700` store
directory and the `0600` blobs do not protect anything against a local user.

The options and their measured costs are in
[the cache entry](../../.agents/docs/cache/shellx-security/2026-11-01-master-secret-protection-options.md).

Recommended:

1. Give the helper the `private_executable_` source attribute. The target
   mode is then `0700`. The combination is not in the chezmoi attribute
   table, but it works. Verified in a scratch HOME.
2. Move the master secret out of the source file into a `0600` file. The
   helper reads it at runtime.
3. Push the secret into the kernel user keyring at startup, and read it from
   there. The keyring holds the payload in RAM only. A file scanner never
   sees the secret. Read cost: 2.5 ms.

Also fix the zeroing. `val = b"\x00" * len(val)` rebinds the name, and the
original bytes stay alive until the collector frees them. Either zero the
buffer in place with a `bytearray`, or drop the claim from
`dot_shell/helper/.help/LIMITATIONS.md`.

Verify: the helper and the key file are `0700` and `0600`, the secret does
not appear in any file under `~/.shell/`, and the store still decrypts.

### Step 9 — Retire the legacy runpriv triple

Separate. Optional.

`dot_shell/helper/executable_runpriv.tmpl`,
`dot_shell/helper/executable_encrypt_store.sh.tmpl`, and the store file
`~/.shell/store/personal-laptop_environment_store.json` are still deployed.
The store holds one entry. Nothing in the repo reads them any more.

Fix: remove the three files and the store file, after a last check that no
secret is lost.

## Status

| Step | Priority | State | Blocked by |
|---|---|---|---|
| 1. Deploy the committed change | correctness | pending | needs the user's apply |
| 2. Fix `shellx import --to` | correctness | pending | |
| 3. Close the temp-file window | correctness | pending | |
| 4. Remove the no-op bytecode step | correctness | pending | |
| 5. Cover the untested paths | correctness | pending | |
| 6. Take the interpreter savings | performance | pending | part 3 waits for step 8 |
| 7. Change the KDF | performance | pending | step 2, because the migration uses `import` |
| 8. Detach the master secret | security | pending | |
| 9. Retire the runpriv triple | security | pending | needs the user's approval |

## Decisions

1. Correctness, then performance, then security. The order comes from the
   owner.
2. The KDF change needs a blob version dispatch and a migration, so it lands
   after the correctness fixes.
3. The launcher split waits for the secret detachment, so the secret never
   lands in two files at once.
4. The store format keeps the version byte. A reader must handle both
   versions until every blob is migrated.

## Risks

| Risk | Effect | Answer |
|---|---|---|
| The migration rewrites all 16 blobs | A lost secret | Take a copy of the store directory first. The export is the recovery path |
| The fast KDF weakens a weak nonce | A guessable store | Refuse the fast path below 32 nonce characters |
| The detached key is missing | The shell has no secret | Decide the failure mode in step 8. See the open questions |
| The keyring holds the secret in RAM | A reboot loses it | The age-encrypted export is the recovery path |
| A lower KDF cost draws attention | None | The nonce entropy is the reason, and it is recorded |

## Open questions

1. When the master secret is missing, should the shell startup fail closed
   or print a warning and continue?
2. Is the kernel keyring layer worth it? A process with the same user id can
   read both the `0600` file and the keyring.
3. Should the KDF change happen at all, given that the master secret will
   move to a `0600` file or the keyring either way?

## Related

- [Agent permission and safety-net issues](../reports/2026-11-01-agent-permission-and-safety-net-issues.md)
- `.agents/docs/cache/shellx-security/2026-11-01-master-secret-protection-options.md`
- `dot_shell/helper/.help/LIMITATIONS.md` — the claims that step 8 has to fix
