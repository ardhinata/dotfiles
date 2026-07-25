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

- Source files and directories follow the Chezmoi naming convention: prefix attributes are **stripped** from the name to determine the target name. `dot_shell` → `.shell`, `private_store` → `store`, `executable_runpriv` → `runpriv`.
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
- **`dot_shell/private_store/` directory:** The `private_` prefix is a chezmoi attribute, so the target directory is `~/.shell/store/` (with 700 permissions). The environment store JSON file at `dot_shell/private_store/encrypted_private_<profile>_environment_store.json.age` targets `~/.shell/store/<profile>_environment_store.json`. Helper scripts (`runpriv`, `encrypt_store.sh`) reference `$HOME/.shell/store/`, not `.../private_store/`.
- **`source_structure` data map:** `.chezmoidata.yaml` defines a `source_structure` map with key paths (`encryption_keys`, `helper`) used by templates and scripts to reference project directories without hardcoding paths.
- **Dynamic `.chezmoiignore`:** The `.chezmoiignore` file is templated. It uses `check_decrypt.sh` (in `.shell_helper/`) at apply time via the `output` function to dynamically ignore encrypted files that fail decryption on the current machine.
- **`system_environment.profile`:** `.chezmoidata.yaml` defines an empty `system_environment.profile` string. Templates condition on this field to include/exclude machine-specific configuration.
- **`.encrypted_data/tokens/`:** Profile-scoped, age-encrypted shell snippets for exporting environment variables (tokens, API keys). File naming follows `<profile>_<name>.zsh.age`. The `dot_shell/helper/executable_runpriv.tmpl` script injects decrypted environment variables on-demand at process launch, avoiding persistent token exposure in the shell environment. The launched process also receives `RUNPRIV_VARS` — a comma-separated list of the injected secret variable names. See `.encrypted_data/tokens/README.md` for conventions.
- **`.decrypted` files:** Files with a `.decrypted` extension are considered sensitive decrypted output. They are explicitly ignored by both `.chezmoiignore` (`**/*.decrypted`) and `.gitignore`.

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
