# Chezmoi Documentation Map

**Version:** chezmoi v2.70.5 | **Generated:** 2026-06-07
To check staleness: compare `chezmoi --version` vs version above; if different, re-run `.help/fetch_current_docs.sh`.

Top-level under `.help/chezmoi-docs/`:

- `docs/` — all documentation content (MkDocs source)
- `snippets/` — reusable flag/config snippets for inclusion in doc pages
- `mkdocs.yml` — MkDocs site config
- `CNAME`, `.gitignore` — site infrastructure

## docs/

### Overview Pages
`index.md.tmpl`, `install.md.tmpl`, `quick-start.md`, `what-does-chezmoi-do.md`, `why-use-chezmoi.md`, `comparison-table.md`, `migrating-from-another-dotfile-manager.md`, `license.md`, `docs.go`, `hooks.py`, `logo.svg`, `chezmoi/index.html`, `voice_30-04-2025_09-20-*.ogx` (3 files)

### user-guide/ — daily usage, setup, templating, scripts
- **Root:** `setup.md`, `daily-operations.md`, `command-overview.md`, `templating.md`, `manage-machine-to-machine-differences.md`, `manage-different-types-of-file.md`, `include-files-from-elsewhere.md`, `use-scripts-to-perform-actions.md`
- **encryption/** — age, gpg, rage, transparent (5 files)
- **password-managers/** — 1Password, AWS Secrets Manager, Azure KV, Bitwarden, custom, Dashlane, Doppler, ejson, gopass, KeePassXC, Keeper, keychain, LastPass, pass, passhole, Proton Pass, Vault (17 files)
- **tools/** — diff, editor, proxy, merge (4 files)
- **machines/** — general, containers-and-vms, linux, macos, windows (5 files)
- **advanced/** — customize-source-dir, install-packages-declaratively, install-pm-on-init, migrate-away, watchman (5 files)
- **frequently-asked-questions/** — design, encryption, general, troubleshooting, usage (5 files)

### reference/ — core concepts, attributes, plugins
- **Root:** `index.md`, `concepts.md`, `application-order.md`, `source-state-attributes.md`, `target-types.md`, `plugins.md`, `release-history.md.tmpl`
- **commands/** — one `.md` per CLI command (~55 files) plus `commands.go` / `commands_test.go` for doc generation
- **command-line-flags/** — index, common, developer, global (4 files)
- **configuration-file/** — index, editor, hooks, interpreters, pinentry, textconv, umask, variables.md.tmpl, variables.md.yaml, warnings (10 files)
- **special-directories/** — chezmoidata, chezmoiexternals, chezmoiscripts, chezmoitemplates (4 files + index)
- **special-files/** — chezmoi-format-tmpl, chezmoidata-format, chezmoiexternal-format, chezmoiignore, chezmoiremove, chezmoiroot, chezmoiversion (7 files + index)
- **templates/** — index, variables, directives
  - **functions/** — 45 built-in template function docs (abortEmpty … warnf)
  - **1password-functions/** — onepassword, onepasswordDetailsFields, onepasswordDocument, onepasswordItemFields, onepasswordRead (5 + index)
  - **aws-secrets-manager-functions/** — awsSecretsManager, awsSecretsManagerRaw (2 + index)
  - **azure-key-vault-functions/** — azureKeyVault (1 file)
  - **bitwarden-functions/** — bitwarden, bitwardenAttachment, bitwardenAttachmentByRef, bitwardenFields, bitwardenSecrets, rbw, rbwFields (7 + index)
  - **dashlane-functions/** — dashlaneNote, dashlanePassword (2 + index)
  - **doppler-functions/** — doppler, dopplerProjectJson (2 + index)
  - **ejson-functions/** — ejsonDecrypt, ejsonDecryptWithKey (2 + index)
  - **github-functions/** — gitHubKeys, gitHubLatestRelease, gitHubLatestReleaseAssetURL, gitHubLatestTag, gitHubRelease, gitHubReleaseAssetURL, gitHubReleases, gitHubTags (8 + index)
  - **gopass-functions/** — gopass, gopassRaw (2 + index)
  - **keepassxc-functions/** — keepassxc, keepassxcAttachment, keepassxcAttribute (3 + index)
  - **keeper-functions/** — keeper, keeperDataFields, keeperFindPassword (3 + index)
  - **keyring-functions/** — keyring (1 file)
  - **lastpass-functions/** — lastpass, lastpassRaw (2 + index)
  - **pass-functions/** — pass, passFields, passRaw (3 + index)
  - **passhole-functions/** — passhole (1 + index)
  - **protonpass-functions/** — protonPass, protonPassJSON (2 + index)
  - **secret-functions/** — secret, secretJSON (2 + index)
  - **vault-functions/** — vault (1 file)
  - **init-functions/** — exit, promptBool, promptBoolOnce, promptChoice, promptChoiceOnce, promptInt, promptIntOnce, promptMultichoice, promptMultichoiceOnce, promptString, promptStringOnce, writeToStdout (12 + index)

### developer-guide/ — architecture, building-on-top, contributing, install-script, packaging, releases, security, testing, using-make, website (10 files + index)

### links/ — articles, dotfile-repos, podcasts, related-software, social-media, videos (6 .md/.tmpl + 3 .yaml data files)

## snippets/
- **Root:** `config-format.md`
- **common-flags/** — exclude, format, include, init, nul-path-separator, override-data-file, override-data, parent-dirs, path-style, recursive, tree (11 files)

---

## Sprig Template Functions (`.help/sprig-docs/`)

Chezmoi includes the full Sprig template function library. These docs are cloned from `Masterminds/sprig` (`master` branch) and serve as the canonical reference for all Sprig functions available in Chezmoi templates.

| File | Description |
|---|---|
| `index.md` | Sprig overview and getting started |
| `strings.md` | String manipulation (trim, upper/lower, replace, plural, quote, etc.) |
| `math.md` | Integer arithmetic (add, sub, mul, div, max, min, mod) |
| `mathf.md` | Floating-point math operations |
| `lists.md` | List/slice operations (append, prepend, first, last, reverse, sortAlpha, union, uniq, etc.) |
| `dicts.md` | Dictionary/map operations (get, set, keys, values, merge, hasKey, etc.) |
| `defaults.md` | Default value functions (default, empty, coalesce) |
| `date.md` | Date formatting and manipulation (now, dateModify, htmlDate, etc.) |
| `encoding.md` | Encoding/decoding (b64enc, b64dec, fromJson, toJson, fromYaml, toYaml) |
| `crypto.md` | Cryptographic hashing (sha256sum, sha512sum, derivePassword, etc.) |
| `conversion.md` | Type conversion (atoi, int64, float64, toString, toDecimal, etc.) |
| `flow_control.md` | Control flow helpers (ternary, coalesce, fail) |
| `os.md` | OS/environment functions (env, expandenv) |
| `paths.md` | File path manipulation (base, dir, ext, clean, isAbs) |
| `reflection.md` | Type reflection (kindOf, typeOf, typeIs, typeIsLike) |
| `semver.md` | Semantic version parsing and comparison |
| `url.md` | URL parsing and construction (urlParse, urlJoin) |
| `network.md` | Network utilities |
| `uuid.md` | UUID generation (uuidv4) |
| `integer_slice.md` | Integer slice utilities (until, untilStep) |
| `string_slice.md` | String slice utilities |
