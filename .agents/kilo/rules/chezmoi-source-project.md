---
description: Rules for working with this Chezmoi dotfiles source project
---

# Chezmoi Source Project

This is a [Chezmoi](https://chezmoi.io) dotfiles source project. For full conventions — source-state attribute tables, template function guidelines, project-specific patterns — **load the `chezmoi` skill**.

## Sensitive File Handling

Never read or include content from files matching: `.age`, `.asc`, `.decrypted` extensions; `encrypted_` prefix; paths containing `token`, `secret`, `credential`, `password`, `key`, `cert`, `pem`; files in `.encryption_keys/`, `.encrypted_data/tokens/`, or `dot_ssh/keys/`.

## Quick Reference

| File | Purpose |
|---|---|
| `.chezmoi.yaml.tmpl` | Config template (age encryption, key discovery) |
| `.chezmoidata.yaml` | Template data: `source_structure`, `system_environment.profile` |
| `.chezmoiignore` | Templated exclusion rules |
| `.chezmoiversion` | Minimum version: `2.70.4` |

## Documentation

Validate against local docs before making assumptions about chezmoi behavior: `.help/chezmoi-docs/`, `.help/DOCS_MAP.md`, `.help/QUIRKS.md`. If `.help/chezmoi-docs/` is missing, run `bash .help/fetch_current_docs.sh`.
