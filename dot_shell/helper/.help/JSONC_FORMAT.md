# JSONC Format

The `shellx export` subcommand emits a JSONC file with a metadata
header (top-of-file `//` comments) and per-entry inline comments. This
file is designed to be readable, editable, diffable, and parseable.

## Full schema

```jsonc
// shellx_export: true                       ← required
// shellx export — DO NOT EDIT by hand. Re-export with `shellx export`.
// Format version: 1                          ← required
// Hostname:        <short hostname>          ← informational
// OS/Arch:         <uname -srm>              ← informational (optional)
// Profile:         <system_environment.profile>   ← informational
// Slug:            <16-hex slug>             ← informational, not authoritative
// Exported at:     <ISO 8601 UTC>            ← informational
// Shellx version:  <X.Y.Z>                  ← informational
// Original path:   <absolute store path>     ← informational
{
  // var: <NAME>  tags: [<csv>]  processes: [<csv>]  updated: <ISO 8601>
  "<NAME>": {
    "value":    "<plaintext secret>",
    "tag":      [<csv>],
    "process":  [<csv>]
  }
  ,
  // ... more entries ...
}
```

## Required header fields

The importer **rejects** files that are missing any of these:

| Header line | Why required |
|---|---|
| `// shellx_export: true` | Sanity check; ensures this is a shellx JSONC. |
| `// Format version: <int>` | Forward-compat. Current major version: `1`. |

## Optional header fields

All other header lines are informational and stored in the parsed
header dict but not validated.

## Entry schema

Each entry is a single top-level key in the JSON object:

| Field | Type | Required | Notes |
|---|---|---|---|
| Key (object name) | string | yes | Must match `^[A-Za-z_][A-Za-z0-9_]*$`. |
| `value` | string | yes | Plaintext secret. Empty string is allowed but discouraged. |
| `tag` | array of strings | yes | Routing tags. May be `[]`. |
| `process` | array of strings | yes | Process-name matches. May be `[]`. |

The importer does not validate `tag` or `process` values beyond
type-checks; arbitrary non-empty strings are accepted.

### Inline comment per entry

The exporter writes a single `// var: ...` line before each entry for
human readability. The importer strips `//` comments before parsing, so
the comment can be safely edited or removed.

## Parsing rules

The importer:

1. Reads the file as UTF-8 text.
2. Collects consecutive `//`-prefixed lines at the top into a header
   dict keyed by the substring before the first `:` (trimmed).
3. Strips all remaining `//` comments, taking care not to touch `//`
   sequences inside JSON strings.
4. Parses the result with the stdlib `json` module (strict; no trailing
   commas, no `NaN`, no duplicate keys — `json.loads` rejects all of
   these).
5. Asserts the parsed header has `shellx_export` and a parseable
   `Format version`.

Errors are surfaced with file:line context where possible.

## Validation

Hand-edited JSONC must:

- Use **double-quoted** strings only (no single quotes).
- Have a **trailing comma after the last entry omitted** (strict JSON).
- Encode the `value` field exactly once per entry.
- Use `//` for comments, **not** `/* … */` block comments.

If the importer rejects a hand-edited file, re-export it with
`shellx export` and re-apply your edits via a script that updates the
regenerated file.

## Example: minimal

```jsonc
// shellx_export: true
// Format version: 1
{
  "GH": { "value": "ghp_xxx", "tag": ["git"], "process": ["gh"] }
}
```

## Example: full

```jsonc
// shellx_export: true
// shellx export — DO NOT EDIT by hand. Re-export with `shellx export`.
// Format version: 1
// Hostname:        desktop-main
// OS/Arch:         Linux 6.5.0 x86_64
// Profile:         personal-laptop
// Slug:            a3f9c1d8b3c49201
// Exported at:     2026-07-12T10:41:44+07:00
// Shellx version:  1.0.0
// Original path:   /home/ardhinata/.local/share/a3f9c1d8b3c49201
{
  // var: GH  tags: ["git","api"]  processes: ["gh","glab"]  updated: 2026-07-11T22:10:03+07:00
  "GH": {
    "value": "ghp_xxxxxxxxxxxxxxxxxxxx",
    "tag": ["git", "api"],
    "process": ["gh", "glab"]
  },
  // var: NPM_TOKEN  tags: ["npm"]  processes: ["npm","npx"]  updated: 2026-07-10T09:00:11+07:00
  "NPM_TOKEN": {
    "value": "npm_xxxxxxxxxxxxxxxxxxxx",
    "tag": ["npm"],
    "process": ["npm", "npx"]
  }
}
```

## Versioning policy

- **Major version bump** (e.g., `1 → 2`): breaking change to the JSON
  schema. Importers must reject unknown major versions.
- **Minor version bump** (e.g., `1.0 → 1.1`): additive — new optional
  fields, new header lines. Importers should ignore unknown keys.

`shellx export` always writes the current major version.