---
description: Rules for working with this Chezmoi dotfiles source project
version: 2
---

# Chezmoi Source Project

This is a [Chezmoi](https://chezmoi.io) dotfiles source project. All configuration files and scripts are managed by Chezmoi for deployment to target machines.

## Sensitive File Handling

When a file path or name suggests it contains sensitive information (e.g., keys, credentials, tokens, encrypted files, secrets), do not read or include the full file content. Instead, include only the minimal necessary snippet or describe the file's purpose without exposing its contents.

Indicators of sensitive files include:
- Files under `.encryption_keys/` or any `keys/` directory
- Files under `.encrypted_data/tokens/` (profile-scoped encrypted token snippets)
- Files with `.age` extension (age-encrypted files)
- Files with `.asc` extension (GnuPG-encrypted files, or ASCII-armored age keys)
- Files with `.decrypted` extension (project convention: decrypted output protected by `.chezmoiignore` and `.gitignore`)
- Files containing `token`, `secret`, `credential`, `password`, `key`, `cert`, `pem` in the path or name
- Files in `dot_ssh/` that appear to be private keys
- Any file with the `encrypted_` source-state prefix

## Documentation

The current Chezmoi documentation is stored locally in `.help/chezmoi-docs/`. This directory is the source for the https://chezmoi.io website. When needing to reference Chezmoi features, commands, templates, or configuration, consult this directory first.

The documentation was fetched using `.help/fetch_current_docs.sh`, which downloads the docs matching the installed `chezmoi` version from the upstream repository.

A docs index mapping file exists at `.help/DOCS_MAP.md` (kept **outside** `.help/chezmoi-docs/` because the fetch script wipes that directory). Use it to quickly locate the relevant doc file for a given topic.

### Template Function Quirks

`.help/QUIRKS.md` documents observed behaviors, edge cases, and mitigations for chezmoi template functions that are not covered by the official documentation. Key entries include:

- **`decrypt` hard abort:** The `decrypt` function aborts the entire template on undecryptable input (undocumented in the official function reference). The project uses a guarded `output "bash" "-c"` pattern with `age --decrypt || echo __DECRYPT_FAILED__` to handle this gracefully.

Always consult `QUIRKS.md` when working with template functions that perform I/O or encryption — the official docs may omit critical failure modes.

### Documentation-First Rule

Before questioning or making assumptions about any Chezmoi config field, template function, command behavior, or special file convention, **always validate against the local docs first**. Key reference files:

- Config fields: `docs/reference/configuration-file/variables.md.yaml` (lists every valid config variable with types and defaults)
- Commands: `docs/reference/commands/*.md`
- Template functions: `docs/reference/templates/functions/*.md` plus Sprig functions at `.help/sprig-docs/` (see `DOCS_MAP.md` for file index)
- Special files/directories: `docs/reference/special-files/*.md` and `docs/reference/special-directories/*.md`
- Config template behavior: `docs/reference/special-files/chezmoi-format-tmpl.md` (documents what data is available during `init` vs. `apply`)
- Source state attributes: `docs/reference/source-state-attributes.md` (complete table of all prefixes, suffixes, and target-type combinations)

### When Documentation Is Missing

If the `.help/chezmoi-docs/` directory does not exist or is empty, attempt to run `.help/fetch_current_docs.sh` to download the documentation. This script:
- Detects the current `chezmoi` version from `chezmoi --version`
- Downloads the matching release archive from GitHub (`twpayne/chezmoi`)
- Extracts `assets/chezmoi.io` into `.help/chezmoi-docs/`
- Requires `curl` or `wget` to be available

If the script fails or is not runnable, instruct the user to manually run:
```bash
bash .help/fetch_current_docs.sh
```

## Chezmoi Conventions

### Source Naming

- Source files and directories follow the Chezmoi naming convention: prefix attributes are **stripped** from the name to determine the target name. For example, `dot_shell` becomes `.shell`, `private_store` becomes `store`, `executable_runpriv.sh` becomes `runpriv.sh`.
- **This applies to both files and directory path components.** When constructing target paths, ALL prefix attributes on every directory component in the source path are stripped. Templates and scripts that reference target paths must use the stripped name, never the source-state name.
- Configuration is in `.chezmoi.yaml.tmpl`, `.chezmoi.yaml`, or the `.config/chezmoi/chezmoi.yaml` layout

### Source-State Attributes (Prefixes)

Full set of documented prefixes (see `docs/reference/source-state-attributes.md` for per-target-type permissions):

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

### Source-State Attributes (Suffixes)

| Suffix | Effect |
|---|---|
| `.literal` | Stop parsing suffix attributes |
| `.tmpl` | Treat the source file contents as a template |
| `.age` | Age-encryption suffix (stripped at apply time; configurable via `age.suffix`) |
| `.asc` | GnuPG-encryption suffix (stripped at apply time; configurable via `gpg.suffix`) |

### Project-Specific Conventions

This project uses the following patterns beyond standard Chezmoi:

- **`private_` + `encrypted_` combination:** SSH keys use both prefixes (e.g., `encrypted_private_codeforge.key.age` in `dot_ssh/keys/`). This ensures keys are both encrypted-at-rest and deployed with restricted permissions.
- **`dot_shell/private_store/` directory:** The `private_` prefix is a chezmoi attribute, so the target directory is `~/.shell/store/` (with 700 permissions). The environment store JSON file at `dot_shell/private_store/encrypted_private_<profile>_environment_store.json.age` targets `~/.shell/store/<profile>_environment_store.json`. Helper scripts (`runpriv.sh`, `encrypt_store.sh`) reference `$HOME/.shell/store/`, not `.../private_store/`.
- **`source_structure` data map:** `.chezmoidata.yaml` defines a `source_structure` map with key paths (`encryption_keys`, `helper`) used by templates and scripts to reference project directories without hardcoding paths.
- **Dynamic `.chezmoiignore`:** The `.chezmoiignore` file is templated. It uses `check_decrypt.sh` (in `.shell_helper/`) at apply time via the `output` function to dynamically ignore encrypted files that fail decryption on the current machine.
- **`system_environment.profile`:** `.chezmoidata.yaml` defines an empty `system_environment.profile` string. Templates condition on this field to include/exclude machine-specific configuration.
- **`.encrypted_data/tokens/`:** Profile-scoped, age-encrypted shell snippets for exporting environment variables (tokens, API keys). File naming follows `<profile>_<name>.zsh.age`. The `dot_shell/helper/executable_runpriv.sh.tmpl` script injects decrypted environment variables on-demand at process launch, avoiding persistent token exposure in the shell environment. See `.encrypted_data/tokens/README.md` for conventions.
- **`.decrypted` files:** Files with a `.decrypted` extension are considered sensitive decrypted output. They are explicitly ignored by both `.chezmoiignore` (`**/*.decrypted`) and `.gitignore`.

### Exclusion and Versioning

- `.chezmoiignore` controls which files are excluded from the target state (supports `.tmpl` templating, patterns matched via `doublestar.Match` against target paths)
- `.chezmoiversion` specifies the minimum Chezmoi version (current project: `2.70.4`)

## Template Function Guidelines

Template functions that perform I/O or recursive operations must follow strict resource-conservation rules. Reckless patterns can cause permission errors, excessive I/O, or silent failures at apply time.

### `glob` — Path Pattern Matching

`glob` runs relative to the **destination directory** (`$HOME`) by default and uses `doublestar.Glob`. An unqualified `**` scans the entire home tree, which includes large, restricted directories (container storage, caches, mount points). This causes hard errors when inaccessible directories are encountered.

- **Always scope to the smallest known directory.** Prefer explicit paths:
  ```
  printf "%s/dir/pattern" .chezmoi.sourceDir   # correct — bounded scope
  printf "**/pattern"                          # wrong — scans entire $HOME
  ```
- **Never use `**` without justification.** If a `**` is required because files are nested at unknown depths, document why in a template comment.
- **Prefer `.chezmoi.sourceDir` over `.chezmoi.destDir`** for scanning chezmoi-managed files, unless the intent is genuinely to inspect the live destination state.

### `include` / `decrypt` — File Inclusion

- `include` reads the referenced file in its entirety every time the template is evaluated. Avoid including the same file repeatedly inside loops or conditionals.
- When decrypting multiple `.age`/`.asc` files, batch them in a single loop with a narrow, scoped glob (see `glob` rules above).
- `decrypt` on a missing or undecryptable file aborts the entire template. Always guard usage with `if`/`range` checks or use the dynamic `.chezmoiignore` pattern from this project.

### `stat` — Filesystem Metadata

- `stat` runs `os.Stat` (a syscall per invocation). Do not call it inside loops over large file lists. Cache results in variables when checking the same path multiple times.
- `stat` is not hermetic: its return value depends on filesystem state at template execution time. Exercise caution.

### `range` — Iteration

- `range` is a Go `text/template` built-in action, not a chezmoi-specific function. It iterates over a map, slice, or channel in memory.
- Prefer `range` over a hardcoded list of known paths over `glob **/*` when the file set is known at template-authoring time:
  ```
  {{ range $file := list "file1.tmpl" "file2.tmpl" }}
    {{ include $file }}
  {{ end }}
  ```
  This avoids filesystem scans entirely and is both fast and deterministic.
- `list` (Sprig) creates an in-memory list from its arguments; it does **not** enumerate a directory's contents. To enumerate files in a directory at apply time, use a scoped `glob` instead.

### `output` — Subprocess Execution

- `output "bash" "script.sh" arg1 arg2` executes a script and captures its stdout. This project uses it in `.chezmoiignore` to run `check_decrypt.sh` and produce dynamic ignore lines.
- `output` is not hermetic and counts as I/O. Cache its result in a variable if the same output is needed in multiple places.

### General Principles

- **Idempotency:** Templates must produce the same output given the same data and source state. Do not depend on external mutable state (e.g., `exec`, network calls, environment variables not set via `chezmoi data`).
- **Graceful degradation:** When data keys are missing or empty (e.g., `system_environment.profile`), use `warnf` to emit a diagnostic message and either skip affected sections or produce a safe default. Do not fail silently or call functions with empty patterns.
- **Error awareness:** Understand the failure mode of each function you invoke. `glob` on an inaccessible directory is a hard error, not a silent skip. `decrypt` on a missing file aborts the entire template. `stat` raises an error on any syscall failure other than `ENOENT`. Always guard with `if`/`range` checks.
- **Minimal I/O:** Every template function call has a cost during `chezmoi apply` and `chezmoi diff`. Use the fewest calls necessary to achieve the desired output.
