# .help

AI assistance and reference materials for working with this Chezmoi dotfiles source project. Files in this directory are tooling helpers, not deployed to target machines.

## Contents

### `fetch_current_docs.sh`

Downloads the Chezmoi documentation matching the installed `chezmoi` version from the upstream repository (`twpayne/chezmoi`), and clones the Sprig template library documentation from `Masterminds/sprig` (`master` branch).

**Usage:**

```
bash fetch_current_docs.sh
```

**Behavior:**
- Detects the installed `chezmoi` version via `chezmoi --version`
- Downloads the Chezmoi release archive from GitHub, wipes and replaces `chezmoi-docs/` with the extracted `assets/chezmoi.io` contents
- Shallow-clones the sprig repository (`master` branch), wipes and replaces `sprig-docs/` with the `docs/` directory
- Requires `curl` or `wget` (for chezmoi archive) and `git` (for sprig clone)

### `DOCS_MAP.md`

A structured index mapping all files under `chezmoi-docs/` to brief descriptions. Organized by category (user guide, reference, commands, templates, developer guide, etc.). Kept **outside** `chezmoi-docs/` so it survives the fetch script's directory wipe.

### `QUIRKS.md`

Documented behaviors, edge cases, and mitigations for chezmoi template functions that are not covered by the official documentation or Sprig function reference. Covers critical failure modes like the `decrypt` function's hard abort on undecryptable input, with project-specific mitigation patterns. Always consult this file when working with template functions that perform I/O or encryption.

### `chezmoi-docs/`

Local copy of the https://chezmoi.io website documentation, organized as MkDocs source. Contains the complete user guide, CLI command reference, template function reference, configuration guide, developer guide, and community links. Populated by running `fetch_current_docs.sh`.

**Key subdirectories:**
- `docs/user-guide/` — setup, daily ops, templating, encryption, password managers, FAQ
- `docs/reference/` — commands, flags, configuration, special directories/files, template functions
- `docs/developer-guide/` — architecture, contributing, packaging, testing
- `snippets/` — reusable doc snippets (common CLI flags)

### `sprig-docs/`

Local copy of the [Sprig](https://github.com/Masterminds/sprig) template function library documentation (master branch). Chezmoi includes Sprig functions natively in templates, making this the canonical reference for all Sprig functions available in Chezmoi templates. Populated by running `fetch_current_docs.sh`.

**Key files:**
- `strings.md` — string manipulation (trim, upper/lower, replace, plural, etc.)
- `math.md` — integer math (add, sub, mul, div, max, min)
- `mathf.md` — floating-point math
- `lists.md` — list operations (append, prepend, first, last, reverse, sort, etc.)
- `dicts.md` — dictionary operations (get, set, keys, values, merge, etc.)
- `defaults.md` — default value functions
- `date.md` — date formatting
- `encoding.md` — base64, json, yaml encoding/decoding
- `crypto.md` — SHA/BCrypt hashing
- `os.md` — environment variable lookup
- `conversion.md` — type conversion (atoi, int64, toString, etc.)
- `flow_control.md` — control flow helpers (ternary, coalesce)
- `reflection.md` — type inspection (kindOf, typeOf)
- `semver.md` — semantic version comparison
- `url.md` — URL parsing and construction
- `paths.md` — file path manipulation (base, dir, ext, clean)
- `network.md` — network utilities
- `uuid.md` — UUID generation

## Usage

When an AI agent needs to reference Chezmoi features, commands, templates, or configuration:
1. Use `DOCS_MAP.md` to find the relevant `.md` file path under `chezmoi-docs/`
2. Read the targeted doc file for detailed information

For Sprig template functions:
1. Browse `sprig-docs/` for the function category (e.g., `strings.md`, `math.md`)
2. Read the relevant file for function signatures and examples

If `chezmoi-docs/` or `sprig-docs/` is missing or empty:
1. Run `bash fetch_current_docs.sh` to populate them
2. If the script fails, instruct the user to run it manually
