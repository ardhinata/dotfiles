# `.encrypted_data/ejson_store/`

**ejson-encrypted JSON stores** checked into the chezmoi source tree, one per
machine. `.encrypted_data/` is source-only — chezmoi never deploys it — so
these files are read only during `chezmoi apply`.

## Files

Naming: `<machine_name>.json`, for example `shiraki-yuki.json`. The name
comes from the `system_environment.machine_name` chezmoi data value.

Each store holds a `_public_key` field, an empty `_metadata` object, and one
field per secret, for example `opencode_index_key`. Secret values hold ejson
ciphertext. Field names stay plaintext.

## Keys

Its private key lives in [`../ejson_key/`](../ejson_key/):

| File                     | State                                  |
| ------------------------ | -------------------------------------- |
| `<machine_name>.key`     | plaintext, gitignored, never committed |
| `<machine_name>.key.age` | age-encrypted, committed               |

A fresh machine needs both files. Pull the repo for the `.key.age`, then
decrypt it with one of the identities in `.encryption_keys/`.

## Consumers

[`dot_shell/zsh/private_20-ejson-environment-load.zsh.tmpl`](../../dot_shell/zsh/private_20-ejson-environment-load.zsh.tmpl)
decrypts the store at apply time and deploys
`~/.shell/zsh/20-ejson-environment-load.zsh` at mode `0600`, since it holds the
secret in plaintext. `dot_zshrc` sources it at shell startup.

## Adding a secret

`ejson encrypt` rewrites a file in place and looks the private key up in
`$EJSON_KEYDIR` by public-key hex filename. Point that at a scratch directory
so the repo stays clean. A store is already encrypted, so decrypt it before
editing:

```bash
cd ~/.local/share/chezmoi
STORE=.encrypted_data/ejson_store/shiraki-yuki.json
KEY=.encrypted_data/ejson_key/shiraki-yuki.key

export EJSON_KEYDIR="$(mktemp -d)"
ln -sf "$PWD/$KEY" "$EJSON_KEYDIR/$(jq -r ._public_key "$STORE")"

ejson decrypt "$STORE" > work.json
# edit work.json: add "new_secret": "value"  (plaintext, delete it afterwards)
ejson encrypt work.json
mv work.json "$STORE"
rm -rf "$EJSON_KEYDIR"
```

Commit the store. If you replaced the key, re-encrypt it and commit that too:

```bash
chezmoi encrypt --output .encrypted_data/ejson_key/shiraki-yuki.key.age \
	.encrypted_data/ejson_key/shiraki-yuki.key
```

## Failure behavior

The template degrades to a warning and exits `0` when the store or key is
unavailable. The same holds when the age identity is absent or when the key
does not match the store. It never aborts the rest of `chezmoi apply`.

For the age-only store, see [`../env_store/README.md`](../env_store/README.md).
