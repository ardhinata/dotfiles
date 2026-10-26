# Conclusion

The verdict, the two-tranche split, the corrected arithmetic, the model
question, and a confidence grade per recommendation.

Part of the agent instruction review. See [README.md](README.md) for the index.

## Status

**Tranche 1 is applied.** Tranche 2 is not. The work landed in five commits
between `d00aed8` and `5f84870`.

| Change | Commit |
|---|---|
| Contradiction and path fixes, six always-on rules | `d00aed8` |
| Three new rules: destructive-action, verification, no-progress | `25724dd` |
| Destructive-command gate in the OpenCode permission layer | `d00a2b2` |
| Skill catalog trim, dead skills removed, duplication removed | `5f84870` |
| Skill catalog corrections and the reasoning-effort pin | `70d16db` |

Two findings changed the plan while it was being applied. Both came from
testing the permission layer on the live host, and both are recorded in the
commit messages.

1. **The action token is `shell`, not `bash`.** A `bash` rule validates
   against the schema and blocks nothing. This was already in the plan. It
   was re-confirmed live before the change went in.
2. **The permission patterns must be path-anchored.** The shell scanner pulls
   words out of quoted strings, so a `*rm -*rf*` pattern also denies any
   command whose text merely mentions the flag. That blocked a commit
   message documenting the rule itself. The applied patterns require an
   absolute path, `~/`, `./`, or `../` after the flag.
3. **cc-safety-net already owns the git commands.** A live test with all
   OpenCode shell rules removed showed that `git reset --hard`,
   `git clean -fd`, `git push --force`, and `git push -f` are already blocked
   by the plugin. The OpenCode layer now carries `rm` only, so one guard
   owns each command class.

## Conclusion

**Verdict.** Do not apply as written. Apply in two tranches.

### Tranche 1: safe today

Independent of every contested inference. Ship this.

1. Phase 2, items 1 to 8. The contradiction and path fixes.
2. A destructive-action gate with repaired patterns.
3. A loop stop-condition rule of one sentence.
4. The `git commit` question left alone until Phase 2 item 1 lands.

### Tranche 2: contested

Gate this behind a decision.

1. The byte cut. The target is no longer 20,000 bytes. See below.
2. The two new rules, which no longer rest on a design law.
3. The effort change, which is the weakest evidence in the document.

### The corrected arithmetic

The Phase 1 table's word targets sum to 3,715 words down to 1,510. Those nine
files hold about 24,700 bytes. Applying the same bytes-per-word ratio to the
survivor counts saves about 14,700 bytes, leaving about 24,300. The two new
rules add about 1,700 bytes. **Landed total is about 26,000 bytes, a 33% cut.**

That is a real cut. It is not 49%. Reaching 20,000 would need another ~950
words from files Phase 1 never lists: `local-first` 388, `sudo-ask` 413,
`project-context` 316, `ambiguity-resolution` 262, `ssh-read-allowlist` 264,
`zsh-stack` 257, `long-running-tools` 170.

After a 9-file cut, **no rule file breaches the length ceiling**, because
none breached it before the cut either. The budget is 150 lines; the longest
rule file is 77. State that plainly rather than claiming the cut was needed
to meet a standard it never violated.

### The model question

The plan's own numbers say DeepSeek V4.1 Flash 1017 is better on every
code-execution metric: Terminal-Bench 33.8 against 25.8, LiveBench Coding 96.0
against 83.9, Long Agentic 50.9 against 34.7. The first draft put the model
choice out of scope without comparing anything.

The honest position is a trigger, not silence. If code-execution quality on
hard tasks matters more than the latency and price difference, the swap beats
this plan's instruction work. Holding the model fixed is defensible for a
single-variable test. It is not defensible as a permanent default.

### What the plan does not deliver

It does not make the model better, and it does not deliver a measured
effectiveness gain. It delivers a smaller rule set, a real destructive-command
gate, and a loop stop-condition.

### Confidence per recommendation

| # | Recommendation | Confidence | Basis |
|---|---|---|---|
| 1 | Fix the contradictions and path defects | HIGH | Quote-level. All confirmed by measurement |
| 2 | Add a destructive-action gate | HIGH | The gap is certain. The permission mechanism was proven live |
| 3 | Add a loop stop-condition | MEDIUM | The base rate is shared with two other models. The counter is cheap |
| 4 | Cut the nine worst-value files | MEDIUM | Per-file word counts confirmed. The 33% total is arithmetic, not measurement |
| 5 | Add a verify-before-claiming rule | LOW | The motivating experiment is withdrawn. Keep only the unlaunderable parts |
| 6 | Change the default effort | LOW | Two blog curves on different tasks. The plan's own Phase 6 cannot test it |

