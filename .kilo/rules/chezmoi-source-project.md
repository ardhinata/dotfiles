---
description: Rules for working with this Chezmoi dotfiles source project
version: 3
---

# Chezmoi Source Project

This is a [Chezmoi](https://chezmoi.io) dotfiles source project. All configuration files and scripts are managed by Chezmoi for deployment to target machines.

When working with chezmoi templates (`.tmpl`), source-state files (prefixed with `dot_`, `private_`, `encrypted_`, `executable_`, etc.), `.age`/`.asc` encryption, or chezmoi config/conventions, **load the `chezmoi` skill** for full conventions, attribute tables, and template function guidelines.

## Sensitive File Handling

When a file path or name suggests it contains sensitive information, do not read or include the full file content. Instead, include only the minimal necessary snippet or describe the file's purpose without exposing its contents.

Indicators of sensitive files:
- Files under `.encryption_keys/` or any `keys/` directory
- Files under `.encrypted_data/tokens/`
- Files with `.age` or `.asc` extension (encrypted files)
- Files with `.decrypted` extension (decrypted output, ignored by `.chezmoiignore` and `.gitignore`)
- Files containing `token`, `secret`, `credential`, `password`, `key`, `cert`, `pem` in path or name
- Files in `dot_ssh/` that appear to be private keys
- Any file with the `encrypted_` source-state prefix

## Documentation

Before questioning or making assumptions about any Chezmoi config field, template function, command behavior, or special file convention, **validate against the local docs first**. Key reference files:

- `.help/chezmoi-docs/` — full documentation matching installed `chezmoi` version
- `.help/DOCS_MAP.md` — quick index to locate docs for a given topic
- `.help/QUIRKS.md` — undocumented behaviors and edge cases (e.g., `decrypt` hard abort)
- `docs/reference/configuration-file/variables.md.yaml` — all config variables
- `docs/reference/source-state-attributes.md` — all prefixes, suffixes, and target-type combinations
- `docs/reference/templates/functions/*.md` + `.help/sprig-docs/` — template function reference

If `.help/chezmoi-docs/` is missing or empty, run: `bash .help/fetch_current_docs.sh`

## Chezmoi Configuration

- Configuration is in `.chezmoi.yaml.tmpl`, `.chezmoi.yaml`, or `.config/chezmoi/chezmoi.yaml`
- `.chezmoidata.yaml` defines template data, including `source_structure` (key paths) and `system_environment.profile`
- `.chezmoiignore` controls target exclusion (templated, supports `doublestar.Match`)
- `.chezmoiversion` specifies minimum Chezmoi version (current: `2.70.4`)
