# Conclusion

The verdict, the two-tranche split, the corrected arithmetic, the model
question, and a confidence grade per recommendation.

Part of the agent instruction review. See [README.md](README.md) for the index.
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

After a 9-file cut, **seven files still breach the 150-word ceiling**, and two
of those are safety files this plan deliberately protects. State that
trade-off rather than calling the cut complete.

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

