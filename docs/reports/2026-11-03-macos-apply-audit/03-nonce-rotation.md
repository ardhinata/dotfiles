# Rotate the work-laptop shellx nonce

The 2026-11-03 apply audit recorded, in this directory and in
[.agents/docs/macos-apply-blockers.md](../../../.agents/docs/macos-apply-blockers.md),
the `chezmoi init` nonce for this host, the master key derived from it,
and the store slug. The repo is public at
`https://github.com/ardhinata/dotfiles`, so the master key is public. The
2026-11-05 secret-exposure audit removed the values from the HEAD files,
but a redaction does not retire a key: git history keeps the old text
(commit `27e7261`), and a clone made before the redaction keeps a copy.
The nonce must rotate.

Rotation changes: a new nonce derives a new master key, the new master
key derives a new store slug, and the new store starts empty. The old
store blobs are protected by a key the whole internet can read, so the
runbook deletes them.

**Status: runbook for the owner. Not yet run.**

Run every command on the work laptop, in an interactive zsh.

## Before the rotation

List the names in the shellx store, so you know what the new store needs.
`--no-encrypt` writes plaintext to /tmp. Read the JSONC entries once,
then remove the directory right away:

```bash
~/.shell/helper/shellx export --no-encrypt --to /tmp/shellx-audit
less /tmp/shellx-audit/*.jsonc
rm -r /tmp/shellx-audit
```

The store held one entry on 2026-11-03, `OPENROUTER_API_OPENCODE_INDEX`,
and a copy of that value is still in `~/.shell/.zshrc` (chezmoi does not
manage that file). The inventory step is optional when the store holds
values you can recover from a file.

## 1. Draw a fresh nonce

The live config is rendered from `.chezmoi.yaml.tmpl`. The template takes
the nonce from the config and draws a fresh one when the value is missing
or not 64 characters:

```bash
chezmoi edit-config
```

In the `data.system_environment:` block, delete the `nonce:` line and
save. `edit-config` re-renders the template on save, so the file regains
a `nonce:` with a new random value. Confirm, in your own shell, that the
new value differs from the leaked one, and record it nowhere:

```bash
grep nonce ~/.config/chezmoi/chezmoi.yaml
```

## 2. Re-render the master key

```bash
chezmoi apply ~/.local/share/shellx/master.key
cat ~/.local/share/shellx/master.key
```

The rendered value is 64 hex characters and must differ from the leaked
value. A plain `chezmoi apply` gives the same result. The
[report index](README.md) counts the 54 diff entries a full apply makes;

## 3. Create the store and re-store the values

A new master key derives a new slug, so `init` opens a fresh state:

```bash
~/.shell/helper/shellx init
```

Send each value to `store` on stdin. For the known entry, using the copy
in `~/.shell/.zshrc`:

```python
python3 - <<'EOF' | ~/.shell/helper/shellx store OPENROUTER_API_OPENCODE_INDEX
import re, pathlib, sys
t = pathlib.Path.home().joinpath('.shell/.zshrc').read_text()
v = re.search(r'^export OPENROUTER_API_OPENCODE_INDEX=(.*)$', t, re.M).group(1)
sys.stdout.write(v.strip().strip('"').strip("'"))
EOF
```

Repeat the pattern for every other name in the inventory.

## 4. Remove the old store

The old blobs sit on disk under a public master key, so they are not
protected. The old directory holds the old slug; find it by its mode
0700 and its 2026-11-03 date, then delete it:

```bash
ls -ld ~/.local/share/*/
rm -rf ~/.local/share/<old-slug>
```

Keep `~/.local/share/shellx/` — it holds `master.key`.

## 5. Verify

In your terminal, `shellx env OPENROUTER_API_OPENCODE_INDEX` prints the
value with no stderr warning, and a fresh login shell loads it. In the
source tree, `chezmoi status` stays clean and `git status --short` shows
no new export file (this runbook produces no repo export).

## Optional

`shellx key move` copies the master key into the macOS login Keychain
and removes `~/.local/share/shellx/master.key`. The
[protection-options note](../../../.agents/docs/cache/shellx-security/2026-11-01-master-secret-protection-options.md)
records that option and its cost.

## What this does not fix

Git history keeps the old values until the rotation makes them useless. A
history rewrite, for example `git filter-repo` over the two affected
paths, plus a force push, removes the text; it needs a decision from the
owner because already-cloned copies keep it anyway.

Back to the [report index](README.md).
