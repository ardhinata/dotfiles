# RTK — Rust Token Killer

`rtk` is a token-optimized CLI proxy for shell commands. Prefix output-heavy
shell commands with `rtk`. The saving on this host is modest: `rtk gain`
measured 15.9% over 541 commands. Do not claim a larger number.

**Never wrap the harness's dedicated tools** — `aft_search`, `aft_outline`,
`aft_zoom`, `grep`, `glob`, `read`, and the background-process facility are
already token-aware. `rtk` is for shell-only commands with heavy stdout or
stderr. Commands with trivial output (`git add`, `mkdir`, `cd`, `touch`) gain
nothing — run them raw.

For filesystem inspection prefer the dedicated tools: `glob` for file
discovery, `grep` for content search, `read` for file contents. Do not
`rtk`-wrap `ls`, `find`, `diff`, or `wc` unless the operation is genuinely
shell-side.

## Chaining

Wrap **each output-producing sub-command** individually, never the whole chain:

```bash
git add . && git commit -m "msg" && rtk git push
rtk cargo build && rtk cargo test
```

## On demand

Run `rtk --help` or `rtk help <subcommand>` for diagnostics (`rtk gain`,
`rtk discover`, `rtk session`), summary modes (`rtk err`, `rtk smart`,
`rtk log`, `rtk json`), and flags (`-v`, `--ultra-compact`, `--skip-env`).
