# Cross-check results

What each of the four independent reviewers found, what it changed, and what
survived all four.

Part of the agent instruction review. See [README.md](README.md) for the index.
## Cross-check results

Four reviewers, non-overlapping scope, all four found material errors.

| Reviewer | Scope | Verdict | Material errors |
|---|---|---|---|
| Adversarial logic | Does each recommendation follow from its evidence | Rework | F-1 is p about 0.33 and confounded. The plan optimises bytes while its own F-3 names constraints. `git commit` ask deadlocks the Phase 2 commit rule. `git push --force*` blocks the safe `--force-with-lease` form. Loops get no rule. Phase 6 is underpowered. |
| External facts | 26 claims against primary sources | Major corrections | The 92.8% figure is misused by a factor of 2.3. The pivotal test is underpowered and confounded. 48 times is an outlier. "512,000 on some providers" is wrong. NeQA is overstated. The family scores 82.9% on IFBench, which undercuts the premise. |
| Internal measurement | 8 payload figures, 9 word counts, 18 defect claims | Minor corrections | "9 of 16 above the ceiling" is really 16 of 16. The ponytail injection is 2,861 bytes, not 5,565. 3,301 words is 0.57 times the rule set, not 2.9 times. All 18 defect line references were confirmed. |
| OpenCode technical | Live v2.1.4 binary and schema | **The block is inert** | `action: "bash"` does nothing; v2 uses `"shell"`. Ordering is documented: last match wins. Patterns are whole-value anchored. A deny-list is the wrong shape. `agents.variant` is invalid. |

### What each reviewer changed

| Correction | Effect on the plan |
|---|---|
| `bash` to `shell` | Phase 4 rewritten. Proven by a live A/B test: a `bash` deny let the command run, a `shell` deny blocked it |
| Deny-list to default-ask plus allowlist | Phase 4 rewritten. The docs warn against recognising every dangerous command by pattern |
| "9 of 16" to "16 of 16" | Recommendation 1 downgraded from HIGH to MEDIUM. The byte target no longer follows from the ceiling |
| 49% to 33% | The 20,000-byte target is withdrawn. Recomputed below |
| ponytail 5,565 to 2,861 | The payload total drops to ~52,600 bytes |
| 2.9 times to 0.57 times | The `asd-ste100` argument weakens. It is still the largest single on-demand load |
| F-1 withdrawn | "Structural, not prose" is no longer a design law. The two new rules lose their justification as a class |
| IFBench 82.9% for the family | The premise that a fast model needs a smaller set is unsupported |
| `git commit` ask dropped | Conflicts with Phase 2. Phase 2 gets fixed first |
| `agents.variant` moved inside `model` | Phase 5 snippet corrected |

### What survived all four reviews

D-1, D-2, D-3, D-7, D-12, and D-18. These are quote-level defects with no
theory attached. They ship in tranche 1 regardless of what happens to the
rest. The choice of the four worst-value files to cut also survived:
`zsh-emulate-fallback`, the GnuPG block, the `stdbuf` caveats, and the
`rtk-rules` command categories.

