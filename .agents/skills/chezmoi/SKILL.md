---
name: chezmoi
description: Full Chezmoi conventions, source-state attributes, template function guidelines, and project-specific patterns for this dotfiles project
---

# Chezmoi Skill

Load this skill when working with chezmoi templates, source-state files, encryption, or chezmoi configuration in this dotfiles project.

## When to Load

- Editing any `.tmpl` file
- User mentions `chezmoi apply`, `chezmoi diff`, `chezmoi add`, or template functions
- Working with source-state prefixed files (`dot_`, `private_`, `encrypted_`, `executable_`, `run_`, etc.)
- Working with `.age`/`.asc` encrypted files
- Editing `.chezmoiignore`, `.chezmoidata.yaml`, `.chezmoi.yaml.tmpl`
- User asks about source-state attributes, template syntax, or chezmoi conventions

## Source Naming

- Source files and directories follow the Chezmoi naming convention: prefix attributes are **stripped** from the name to determine the target name. `dot_shell` → `.shell`, `private_store` → `store`, `executable_embedding_dimensions_proxy.py` → `embedding_dimensions_proxy.py`.
- **Applies to both files and directory path components.** All prefix attributes on every directory component in a source path are stripped. Templates and scripts that reference target paths must use the stripped name, never the source-state name.

## Source-State Attributes

### Prefixes

| Prefix | Effect |
|---|---|
| `after_` | Run script after updating the destination |
| `before_` | Run script before updating the destination |
| `create_` | Ensure the file exists, create with contents if absent |
| `dot_` | Rename to use a leading dot (e.g., `dot_foo` → `.foo`) |
| `empty_` | Ensure the file exists even if empty (default: empty files removed) |
| `encrypted_` | Encrypt the file in the source state |
| `exact_` | Remove anything not managed by chezmoi |
| `executable_` | Add executable permissions to the target file |
| `external_` | Ignore attributes in child entries |
| `literal_` | Stop parsing prefix attributes |
| `modify_` | Treat contents as a script that modifies an existing file |
| `once_` | Only run script if contents have not run successfully before |
| `onchange_` | Only run script if contents changed since last successful run |
| `private_` | Remove all group and world permissions from the target file or directory |
| `readonly_` | Remove all write permissions from the target file or directory |
| `remove_` | Remove the file/symlink if it exists or the directory if it is empty |
| `run_` | Treat contents as a script to run |
| `symlink_` | Create a symlink instead of a regular file |

### Suffixes

| Suffix | Effect |
|---|---|
| `.literal` | Stop parsing suffix attributes |
| `.tmpl` | Treat the source file contents as a template |
| `.age` | Age-encryption suffix (stripped at apply time; configurable via `age.suffix`) |
| `.asc` | GnuPG-encryption suffix (stripped at apply time; configurable via `gpg.suffix`) |

## Project-Specific Conventions

- **`private_` + `encrypted_` combination:** SSH keys use both prefixes (e.g., `encrypted_private_codeforge.key.age` in `dot_ssh/keys/`). This ensures keys are both encrypted-at-rest and deployed with restricted permissions.
- **`dot_shell/private_store/` directory (legacy store):** The `private_` prefix is a chezmoi attribute, so the target directory is `~/.shell/store/` (with 700 permissions). The environment store JSON file at `dot_shell/private_store/encrypted_private_<profile>_environment_store.json.age` targets `~/.shell/store/<profile>_environment_store.json`. The `runpriv` and `encrypt_store.sh` helpers that read this store were retired on 2026-11-03. `shellx` replaced them and keeps its own store under `~/.local/share/<slug>/`.
- **`dot_shell/helper/` shellx sources:** The helper is split into three source files, all with the `private_` attribute so the deployed target carries mode 0600. `private_executable_shellx.tmpl` is the launcher (target mode 0700), `private_shellx_impl.py.tmpl` holds the subcommands, and `private_shellx_key.py.tmpl` resolves the master key. The launcher and the key module carry the `.tmpl` suffix, so chezmoi renders them.
- **Master key file:** `dot_local/share/private_shellx/private_master.key.tmpl` renders to `~/.local/share/shellx/master.key` with mode 0600. No deployed file holds the master secret in plaintext. `shellx` reads the key from the `SHELLX_MASTER_KEY` override, then the `SHELLX_NONCE` override, then the key file, then the platform secret store.
- **Blob versions:** A shellx blob starts with a version byte. Version 1 derives the per-blob keys with scrypt. Version 2 derives them with HMAC-SHA512 over the per-blob salt. The tag stays HMAC-BLAKE2b in both versions, so one store can hold blobs of both versions.
- **`source_structure` data map:** `.chezmoidata.yaml` defines a `source_structure` map with key paths (`encryption_keys`, `helper`) used by templates and scripts to reference project directories without hardcoding paths.
- **Dynamic `.chezmoiignore`:** The `.chezmoiignore` file is templated. It uses `check_decrypt.sh` (in `.shell_helper/`) at apply time via the `output` function to dynamically ignore encrypted files that fail decryption on the current machine.
- **`system_environment.profile`:** `.chezmoidata.yaml` defines an empty `system_environment.profile` string. The section helper uses it as the broad `p_<profile>` tier. Set it to a group name, not the hostname.
- **`.encrypted_data/env_store/`:** Source-only, because it is a dot-directory at the source root. Two file shapes live here. Manual profile snippets follow `<profile>_<name>.zsh.age` and hold `export VAR="value"` lines. `shellx export` writes `encrypted_<host>_<slug>_<utc>.jsonc.age` instead. The slug comes from the master key, so an export for an old slug cannot be imported into the current store. `shellx` (Python, replaces `runpriv`) injects secrets on demand at process launch, so no token rests in the shell environment. The launched process receives `SHELLX_VARS` (and the legacy `RUNPRIV_VARS` alias, same value), a comma-separated list of the injected names. See `.encrypted_data/env_store/README.md` for the full convention. (Renamed from `tokens/` in `shellx 1.2.0`.)
- **`.decrypted` files:** Files with a `.decrypted` extension are considered sensitive decrypted output. They are explicitly ignored by both `.chezmoiignore` (`**/*.decrypted`) and `.gitignore`.

## Identity Section Includes

A template that needs machine-specific content calls the common helper
`.chezmoitemplates/section.tmpl`. Do not add a new `if eq .chezmoi.os` block.

```gotemplate
{{ template "section.tmpl" (dict "root" . "file" "dot_zshrc.tmpl" "section" "prezto-platform") }}
```

The helper reads a sibling dot directory:

```
<dir of file>/.<base of file without .tmpl>.resources/
```

It tries these names in order and uses the first that exists:

1. `<section>.h_<hostname>`
2. `<section>.p_<profile>`
3. `<section>.os_<os>`
4. `<section>._default`

The identifier values are lowercased and sanitized to `[a-z0-9-]`.

Rules:

- Give every section a `_default`, even an empty one.
- A block section uses `template`. Put the leading blank line in the resource.
  Do not end a block resource with a newline. The template supplies the final
  newline.
- A fragment inside a line uses `trim (includeTemplate ...)`, so the resource's
  trailing newline cannot break the line.
- The helper logs the chosen candidate with `debugf`. Run
  `chezmoi -v cat <target>` to see it.
- A resource is a Go template. Escape a literal `{{`.
- `.chezmoiignore` keeps its inline OS conditions. It is a special file, not a
  target template.
- `lookPath` conditions stay inline. The helper selects on identity only.

## Exclusion and Versioning

- `.chezmoiignore` controls which files are excluded from the target state (supports `.tmpl` templating, patterns matched via `doublestar.Match` against target paths)
- `.chezmoiversion` specifies the minimum Chezmoi version (current project: `2.70.4`)

## Template Function Quirks

`.help/QUIRKS.md` documents observed behaviors, edge cases, and mitigations for chezmoi template functions not covered by official docs:

- **`decrypt` hard abort:** The `decrypt` function aborts the entire template on undecryptable input (undocumented). The project uses a guarded `output "bash" "-c"` pattern with `age --decrypt || echo __DECRYPT_FAILED__` to handle this gracefully.

Always consult `QUIRKS.md` when working with template functions that perform I/O or encryption — the official docs may omit critical failure modes.

## When Documentation Is Missing

If `.help/chezmoi-docs/` is missing or empty, run: `bash .help/fetch_current_docs.sh`
This script detects the `chezmoi` version, downloads the matching release from `twpayne/chezmoi`, and extracts `assets/chezmoi.io` into `.help/chezmoi-docs/`. Requires `curl` or `wget`.

## Template Function Guidelines

Template functions that perform I/O or recursive operations must follow strict resource-conservation rules.

### `glob` — Path Pattern Matching

- `glob` runs relative to the **destination directory** (`$HOME`) by default and uses `doublestar.Glob`. An unqualified `**` scans the entire home tree, causing hard errors on inaccessible directories.
- **Always scope to the smallest known directory.** Prefer explicit paths:
  ```
  printf "%s/dir/pattern" .chezmoi.sourceDir   # correct
  printf "**/pattern"                          # wrong — scans entire $HOME
  ```
- **Never use `**` without justification.** If required, document why in a template comment.
- **Prefer `.chezmoi.sourceDir` over `.chezmoi.destDir`** for scanning chezmoi-managed files.

### `include` / `decrypt` — File Inclusion

- `include` reads the referenced file in its entirety every time. Avoid including the same file repeatedly in loops or conditionals.
- When decrypting multiple `.age`/`.asc` files, batch them in a single loop with a narrow, scoped glob.
- `decrypt` on a missing or undecryptable file aborts the entire template. Always guard with `if`/`range` checks or use the dynamic `.chezmoiignore` pattern.

### `stat` — Filesystem Metadata

- `stat` runs `os.Stat` (a syscall per invocation). Do not call it inside loops over large file lists. Cache results in variables.
- `stat` is not hermetic: its return value depends on filesystem state at template execution time.

### `range` — Iteration

- `range` is a Go `text/template` built-in action. It iterates over a map, slice, or channel in memory.
- Prefer `range` with a hardcoded `list` over `glob **/*` when the file set is known at template-authoring time:
  ```
  {{ range $file := list "file1.tmpl" "file2.tmpl" }}
    {{ include $file }}
  {{ end }}
  ```
- `list` (Sprig) creates an in-memory list from arguments; it does **not** enumerate a directory's contents.

### `output` — Subprocess Execution

- `output "bash" "script.sh" arg1 arg2` executes a script and captures its stdout.
- `output` is not hermetic and counts as I/O. Cache its result in a variable if reused.

### General Principles

- **Idempotency:** Templates must produce the same output given the same data and source state.
- **Graceful degradation:** When data keys are missing or empty, use `warnf` to emit a diagnostic and either skip affected sections or produce a safe default.
- **Error awareness:** `glob` on an inaccessible directory is a hard error. `decrypt` on a missing file aborts the entire template. `stat` raises an error on any syscall failure other than `ENOENT`. Always guard with `if`/`range` checks.
- **Minimal I/O:** Every template function call has a cost during `chezmoi apply` and `chezmoi diff`. Use the fewest calls necessary.
