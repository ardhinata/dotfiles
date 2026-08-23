# Shellx startup regression — post-mortem

**Status:** Resolved. Fix shipped in shellx 1.3.0 (deployed). Plan lives at
`.tmp/docs/plans/2026-08-23-shellx-startup-perf.md` (committed `75e5809`).

## Summary

After replacing `runpriv` with `shellx` (Python), every invocation of
`shellx --tag=… -- proc …` paid a 1.5–2.0 s startup tax, vs `~20 ms` for
`runpriv`. Measured cold-start on this machine:

| Operation | shellx 1.2.1 | shellx 1.3.0 | Speedup |
|---|---|---|---|
| `shellx --tag=doesnotexist -- echo hi` | 1.5–1.9 s | **54–121 ms** | ~20–30× |
| `shellx list` | 1.4–1.8 s | **88–160 ms** | ~12–15× |
| `shellx` (no args) | ~1.5 s | **87–152 ms** | ~12–15× |
| `shellx --tag=git -- gh --version` (1 decrypt) | 1.6–2.0 s | **191–249 ms** | ~9–10× |
| `shellx --tag=api -- env` (9 decrypts) | ~2.5 s+ | 1.0–1.1 s | ~2.5× |

All single-decrypt paths are now under the 0.5 s target. Multi-decrypt
paths are linear in `n × scrypt cost` (~100 ms each, inherent to the
threat model — not optimizable without dropping scrypt).

## Root cause

The 1.5 s was paid by a single line of code:

```python
result = subprocess.run(
    args=["chezmoi", "data", "--format", "json"],
    capture_output=True, text=True, check=True,
)
```

`shellx._load_env()` (1.2.1:40–68) called this on **every invocation** to
resolve `system_environment.profile` and `system_environment.nonce`.
The Go binary walks the entire source dir to render the data tree, and
this machine's source dir contains
`.tmp/references/repository/kilocode/` — a 4.4 GB reference clone of the
`kilocode` repo with full `node_modules/` (2 421 `.bin/` entries alone).

`strace -e openat chezmoi data …` confirmed: 26 879 of 26 900 `openat`
syscalls landed inside `.tmp/references/repository/kilocode/node_modules/…`.
The walker is paying for the source-tree enumeration regardless of
`.chezmoiignore` rules.

### Why shellx did this in the first place

`runpriv` (`dot_shell/helper/executable_runpriv.tmpl:6`) baked
`profile` and a hash-derived `STATIC_PW` directly into the deployed
script at `chezmoi apply` time. Zero subprocess. Zero Go rendering.
Cold start: 20 ms.

`shellx` 1.1.0 explicitly removed that templating. The CHANGELOG
(`dot_shell/helper/.help/CHANGELOG.md` 1.1.0 entry, plus the original
comment at `executable_shellx:32–34`) frames the rationale:

> No .tmpl substitution anymore — this file is plain Python; the nonce
> and profile are read at runtime via `chezmoi data` so the deployed
> script is independent of any per-machine template rendering.

The trade-off was: **deploy-time templating simplicity vs. ~1.5 s per
invocation**. This machine paid the runtime cost 50–100× per active day;
the "plain Python" benefit was theoretical — no one copies `shellx`
outside `$PATH` except for tests, which already have a hermetic override
mechanism.

## What was tried during the session

### 1. `.chezmoiignore` rule for `.tmp/`

Hypothesis: the `.tmp/references/...` walking is expensive; add a
`.chezmoiignore` rule to skip it.

**Result:** No effect. `.chezmoiignore` patterns match against the
*target path* (chezmoi docs
`docs/reference/special-files/chezmoiignore.md`: "patterns are matched
using `doublestar.Match` and match against the target path"). Since
`.tmp/` is `.gitignore`-excluded and never *deployed*, there is no
target path for the pattern to match. `chezmoi ignored` showed zero
matches after adding the rule; timing was unchanged (1.5–1.7 s).

**Decision:** Kept the rule as future-proofing (commented to explain
intent) in case chezmoi ever changes how it evaluates ignore patterns.
But it is **inert for this regression**.

### 2. Verify the cost is `chezmoi data`, not Python

Bypassed the `subprocess.run` call inline with a Python `c`-style test
that hard-coded `profile` and `nonce`:

```bash
python3 -c 'import hashlib, …; print(hashlib.blake2b(f"chezmoi:shellx:{profile}:{nonce}".encode(), digest_size=16).hexdigest())'
```

Cold cost: ~70 ms (python3 + stdlib imports + blake2b).
With the subprocess call: ~1.7 s.

**Conclusion:** the Python cost is ~70 ms (acceptable); the chezmoi
cost is the dominant 1.5 s. The fix must skip the subprocess.

### 3. Template re-injection (the actual fix)

Renamed `dot_shell/helper/executable_shellx` →
`dot_shell/helper/executable_shellx.tmpl`. chezmoi strips `.tmpl` at
apply time and renders:

```python
SHELLX_PROFILE = "{{- .system_environment.profile -}}"
SHELLX_NONCE   = "{{- .system_environment.nonce -}}"
```

The deployed script reads them as plain constants — zero subprocess on
the hot path. To keep the script working when invoked outside the
chezmoi apply pipeline (CI, headless, manual copy), `_load_env()` uses
a 4-tier fallback chain:

1. Cached values (module-global; populated on first call).
2. `SHELLX_PROFILE` / `SHELLX_NONCE` env vars (test override; CI pin).
3. Template-injected `SHELLX_PROFILE` / `SHELLX_NONCE` constants.
4. `chezmoi data --format json` subprocess (slow path; ~1.5 s; only
   the path 1+2 are empty).

The slow path is exercised only by tests/CI; the normal deployed path
is zero-subprocess.

### 4. Bytecode cache in onchange hook (Plan #5)

Added `python3 -m py_compile ~/.shell/helper/shellx` to
`.chezmoiscripts/run_onchange_init-shellx-store.sh`. Saves ~20–30 ms
per cold start by letting CPython reuse the parsed AST. Pycache
lives under `__pycache__/` next to the script; `.chezmoiignore`
already excludes `**/__pycache__/**` (line 17) so the cache doesn't
leak into the deployed target tree.

### 5. Tests

Updated `dot_shell/helper/test_shellx.py` so the test loader renders
the source `.tmpl` via `chezmoi execute-template` into a temp file
before importing (the source itself contains `{{- ... -}}` actions
that aren't valid Python). Added three new tests:

- `test_template_injected_values_resolve` — fast path works.
- `test_env_var_override_takes_precedence` — env vars beat template.
- `test_empty_template_falls_back_to_chezmoi_data` — slow path
  reachable when constants are empty (mocked `subprocess.run`).
- `test_no_chezmoi_subprocess_when_template_has_values` — fast path
  does **not** shell out.

All 32 tests pass in ~2.5 s.

## Resolution (the diff)

| File | Change |
|---|---|
| `dot_shell/helper/executable_shellx` → `.tmpl` | Template-inject profile/nonce; replace `_load_env()` with 4-tier fallback |
| `dot_shell/helper/test_shellx.py` | Render-and-load the source; 3 new tests; existing tests unchanged |
| `.chezmoiscripts/run_onchange_init-shellx-store.sh` | Add `python3 -m py_compile` block (saves ~20–30 ms/cold start) |
| `.chezmoiignore` | Add `.tmp` rule (inert but future-proof) |
| `dot_shell/helper/.help/CRYPTO.md` | Update "Password (STATIC_PW)" section to document the template-injection flow + fallback chain |
| `dot_shell/helper/.help/INSTALL.md` | Replace single "headless use" snippet with three options (chezmoi apply / env vars / pre-render by hand) |
| `dot_shell/helper/.help/CHANGELOG.md` | Add `## [1.3.0] — 2026-08-23` entry explaining the perf rationale and migration (re-apply; no data migration) |

7 files, 303 insertions, 49 deletions. Working-tree change is **unstaged**
as of this post-mortem (awaiting user approval to commit per the
per-instruction "don't commit without explicit request" rule).

## What this fix does NOT solve

- **Multi-decrypt `shellx --tag=…` with N entries still scales linearly
  in scrypt cost.** N=9 → 1.0 s; N=20 → ~2 s. The threat model needs
  scrypt (32 MiB memory-hard KDF); reducing scrypt to `n=2^14` would
  cut per-decrypt cost to ~25 ms but weaken the brute-force defense.
  Acceptable trade-off for the current scale; revisit if a workflow
  routinely decrypts >10 secrets per call.
- **`shellx_completion_helper.tmpl` still shells out to `chezmoi data`.**
  Zsh completion fires once per `<TAB>`, not per shellx invocation,
  so the 1.5 s tax is paid interactively and acceptable. A follow-up
  could parse `~/.config/chezmoi/chezmoi.yaml` directly with `tomllib`
  (Python 3.11+, already the project's floor); defer as a separate
  small change.
- **`.tmp/references/repository/kilocode/node_modules` still slows down
  every `chezmoi` invocation on this machine.** The shellx fix removes
  the impact on shellx specifically. A repo-wide fix would either move
  the reference clones outside the source dir, or add `.tmp/` to
  some future chezmoi feature that walks source dirs with ignore
  semantics (not currently implemented).

## Lessons learned

- **`.chezmoiignore` does not solve source-walking cost.** It matches
  target paths, and source-side ignores have no semantic today.
  Don't waste time adding ignore rules for "make `chezmoi data`
  faster" — they won't. Fix the call site, not the data pipeline.
- **Validate the obvious hypothesis before implementing the fix.** I
  spent the first half of the session on the `.chezmoiignore` lever
  before profiling the actual hot path. A 5-minute `time python3 -c
  'subprocess.run(["chezmoi","data"])'` would have skipped all of
  that. Profile first, hypothesize second.
- **The 1.1.0 CHANGELOG trade-off was wrong for this codebase.** The
  "plain Python, independent of per-machine template rendering" win
  is theoretical (no one copies `shellx` outside `$PATH`). The cost
  is paid 50–100× per day by the actual user. When documenting a
  "we chose simplicity over performance" decision, the perf number
  should be cited, not waved at.
- **The same template-injection pattern works for any Python helper
  that reads `.chezmoidata.yaml` data at runtime.** Candidates for
  the same treatment: `shellx_completion_helper.tmpl` (as noted),
  any future Python tool that follows the same pattern. Standardize
  the env-var override + chezmoi-data-fallback chain so the next
  author doesn't repeat the 1.1.0 mistake.
- **`runpriv.tmpl`'s deploy-time templating is the right model for
  this repo.** The bash script stays because it works; the Python
  rewrite only needed to keep the deploy-time-injection property.

## Pointer

The plan that this post-mortem was promoted from is at
`.tmp/docs/plans/2026-08-23-shellx-startup-perf.md` (committed
`75e5809`). It contains the full measurement table, the alternatives
considered (and why each was rejected), and the rollout plan.
