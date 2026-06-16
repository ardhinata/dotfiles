# Chezmoi Template Function Quirks

Documented behaviors, edge cases, and mitigations not covered by the official chezmoi documentation or the Sprig function reference.

## `decrypt` — Hard Abort on Undecryptable Input

**Official docs:** `docs/reference/templates/functions/decrypt.md` states only:

> `decrypt` decrypts *ciphertext* using chezmoi's configured encryption method.

No failure mode is documented. The `merge` command docs (`docs/reference/commands/merge.md`) acknowledge that "an encrypted file that cannot be decrypted" prevents target state computation, but the template-level behavior is not specified.

### Observed behavior

When `decrypt` encounters ciphertext that age cannot decrypt (wrong identity, corrupt file, `age` not installed), it **aborts the entire template with a fatal error**:

```
age: error: no identity matched any of the recipients
chezmoi: <target>: template: <source>: executing "<source>" at <decrypt>: error calling decrypt: exit status 1
```

Template execution stops immediately. No output is produced for the target file (or a two-way merge is performed if using `chezmoi merge`). This differs from functions like `stat` (which returns a structured value with error info) and `exec` (which returns `false` on command failure without aborting).

### Impact

Any template that iterates over encrypted files with `include | decrypt` without a guard will fail entirely if a single file is undecryptable. This includes:

- New machines that don't yet have all secret keys
- Files encrypted with a key that was rotated or removed
- Files encrypted for a different profile/machine

### Project mitigation

This project uses a **guarded `output "bash" "-c"` pattern** instead of `decrypt` in templates that need graceful degradation. The pattern:

1. Use `output "bash" "-c"` to call `age --decrypt` directly with the same identity keys chezmoi configures
2. The shell command uses `|| echo __DECRYPT_FAILED__` so the command always exits 0
3. Check the captured output against the failure marker
4. Emit a diagnostic comment on failure instead of aborting

Reference implementation: `dot_shell/helper/encrypt_store.sh.tmpl` (Chacha20-based encrypt/decrypt via openssl for the runtime environment store).

```
{{- $keys := glob (printf "%s/.encryption_keys/*.secret.key" .chezmoi.sourceDir) -}}
{{- range $file := glob $pattern -}}
{{-   $cmd := "age --decrypt" -}}
{{-   range $k := $keys -}}
{{-     $cmd = printf "%s -i %s" $cmd $k -}}
{{-   end -}}
{{-   $cmd = printf "%s %s 2>/dev/null || echo __DECRYPT_FAILED__" $cmd $file -}}
{{-   $result := output "bash" "-c" $cmd -}}
{{-   if eq (trim $result) "__DECRYPT_FAILED__" -}}
# TOKENS: failed to decrypt {{ base $file }}
{{-   else -}}
{{ $result -}}
{{-   end -}}
{{- end -}}
```

An alternative approach in `.chezmoiignore` uses an external script (`check_decrypt.sh`) to test decryption and dynamically produce ignore patterns for undecryptable files, avoiding template-level `decrypt` entirely.

### When to apply this mitigation

Use the guarded pattern when:

- The template iterates over encrypted files from a glob or directory listing
- Individual files may be undecryptable on some machines (profile-scoped keys)
- You want a diagnostic comment rather than a template crash

Do **not** need this pattern when:

- The encrypted file is referenced directly by name (not via glob) — use `if (stat …).IsEncrypted` to check first
- The template uses `encrypted_` source-state attributes (chezmoi's core engine handles those, not the template `decrypt` function)
- A template crash is the desired behavior (fail-closed security stance)

### Tested against

| chezmoi version | Status |
|---|---|
| v2.70.5 | Confirmed — `decrypt` aborts template on undecryptable ciphertext |
