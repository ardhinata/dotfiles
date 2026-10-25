# `.encrypted_data/ejson_store/`

**ejson-encrypted JSON stores** checked into the chezmoi source tree.
`.encrypted_data/` is source-only — chezmoi never deploys it — so these
files are read only during `chezmoi apply`.

## Files

| File                | State                                  |
| ------------------- | -------------------------------------- |
| `environment.json`  | ejson-encrypted store, committed       |

One store holds every machine. Each machine gets one section, named after
`system_environment.machine_name` from the chezmoi data values.

## Structure

Field names stay plaintext, so a reviewer sees which variables exist for
which machine, but never the values. Only the values are ciphertext.

```json
{
  "_public_key": "<hex>",
  "_metadata": {},
  "shiraki-yuki": {
    "OPENROUTER_API_OPENCODE_INDEX": "EJ[1:...]"
  }
}
```

Field names inside a section are environment variable names. The template
exports every field in the machine's own section and skips fields whose name
starts with `_`.

ejson encrypts string values only. Numbers, booleans, and nulls stay in
plaintext, so store every secret as a string.

## Keys

The private key lives in [`../ejson_key/`](../ejson_key/):

| File                    | State                                  |
| ----------------------- | -------------------------------------- |
| `environment.key`       | plaintext, gitignored, never committed |
| `environment.key.age`   | age-encrypted, committed               |

A fresh machine needs both files. Pull the repo for the `.key.age`, then
decrypt it with one of the identities in `.encryption_keys/`.

One key pair protects the whole store. Every `*.key.age` in this repo is
encrypted to the same age recipients, so a machine that holds one age
identity can decrypt every other machine's ejson key as well. Separate keys
per machine would not add isolation.

## Consumers

[`dot_shell/zsh/private_20-ejson-environment-load.zsh.tmpl`](../../dot_shell/zsh/private_20-ejson-environment-load.zsh.tmpl)
decrypts the store at apply time and deploys
`~/.shell/zsh/20-ejson-environment-load.zsh` at mode `0600`, since it holds the
secret in plaintext. `dot_zshrc` sources it at shell startup.

The template uses chezmoi's native `ejsonDecryptWithKey` template function,
so no `ejson` binary is needed at apply time. chezmoi has supported it
since v2.33.0.

## Adding a secret

`ejson encrypt` rewrites a file in place and looks the private key up in
`$EJSON_KEYDIR` by public-key hex filename. Point that at a scratch
directory so the repo stays clean. A store is already encrypted, so decrypt
it before editing.

Keep the plaintext work file outside the repo, so a stray `git add` cannot
commit it:

```bash
cd ~/.local/share/chezmoi
STORE=.encrypted_data/ejson_store/environment.json
KEY=.encrypted_data/ejson_key/environment.key

WORK="$(mktemp -d)"
export EJSON_KEYDIR="$WORK/keydir"
mkdir -p "$EJSON_KEYDIR"
ln -sf "$PWD/$KEY" "$EJSON_KEYDIR/$(jq -r ._public_key "$STORE")"

ejson decrypt "$STORE" > "$WORK/work.json"

# Edit "$WORK/work.json": add the field under the machine section.
# The field name is the environment variable name. The value is plaintext
# at this point, and ejson encrypt encrypts it.

ejson encrypt "$WORK/work.json"
cp "$WORK/work.json" "$STORE"
rm -rf "$WORK"
```

`ejson encrypt` leaves values that are already encrypted untouched, so
running it on a decrypted store does not re-encrypt the existing secrets.

Commit the store. If you replaced the key, re-encrypt it and commit that too:

```bash
chezmoi encrypt --output .encrypted_data/ejson_key/environment.key.age \
	.encrypted_data/ejson_key/environment.key
```

The `ejson` binary is needed to edit a store. chezmoi has no `ejsonEncrypt`
template function, so the binary stays an authoring-time tool. It is not
chezmoi-managed; install it separately if it is missing.

## Failure behavior

The template degrades to a warning and exits `0` when the store or key is
unavailable, when no age identity can decrypt the key, or when a value in
the machine section is not a string. It never aborts the rest of
`chezmoi apply`.

One case does abort: a key that decrypts but does not match the store. That
is a real mismatch, and a silent warning would look like a configuration
problem instead.

For the age-only store, see [`../env_store/README.md`](../env_store/README.md).
