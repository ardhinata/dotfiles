---
description: BENCHMARK judge — consume 6 shiki verifier outputs (3 m3 + 3 deepseek) and produce the comparison YAML. TEMPORARY. DELETE after benchmark.
mode: subagent
model: openrouter/~deepseek/deepseek-v4-flash-latest
variant: high
steps: 40
maxTokens: 16000
temperature: 0.3
top_p: 0.9
hidden: true
permission:
  "*": ask
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit:
    "*": deny
    "/tmp/kilo/shiki-bench/**": allow
    "/tmp/kilo/shiki-bench/**/*": allow
  write:
    "*": deny
    "/tmp/kilo/shiki-bench/**": allow
    "/tmp/kilo/shiki-bench/**/*": allow
  external_directory:
    "/tmp/kilo/shiki-bench/**": allow
    "/tmp/kilo/shiki-bench/**/*": allow
  bash:
    "*": ask
    "ls *": allow
    "cat *": allow
    "head *": allow
    "tail *": allow
    "find *": allow
    "grep *": allow
    "wc *": allow
    "date *": allow
  webfetch: allow
  websearch: allow
  firecrawl_*: allow
  tavily_*: allow
  context7_*: allow
---

# BENCHMARK judge — shiki model pick comparison

**Temporary judge agent for the shiki model-pick benchmark.** Consumes
6 verifier outputs (3 from `shiki-bench-m3` on minimax-m3, 3 from
`shiki-bench-deepseek` on deepseek-v4-flash-0731) and produces the
side-by-side comparison. The user's decision: pick minimax-m3
(token plan, no per-token cost) or deepseek-v4-flash-0731
(reasoning_effort-honoured, better benchmarks, cheaper per call).

**DELETE this file after the benchmark.**

## Inputs

Read these 6 files (whichever exist) from `/tmp/kilo/shiki-bench/`:

- `output-m3-run1-*.yaml`
- `output-m3-run2-*.yaml`
- `output-m3-run3-*.yaml`
- `output-deepseek-run1-*.yaml`
- `output-deepseek-run2-*.yaml`
- `output-deepseek-run3-*.yaml`

Some may be missing if a run errored (e.g. M3 429 rate-limit shared
pool). Note absent runs as `status: rate-limited-or-error` in the
comparison; do not invent content.

## Comparison rubric

For each of the 3 m3 runs and 3 deepseek runs, score on these axes:

1. **`claims_table` completeness** — count of `final_verdict:` lines
   (target: 10-15 entries). Each entry that has all 5 fields (claim,
   source, confidence, shallow, deep, final_verdict) is well-formed.

2. **Recommendation presence** — `recommendation.claim` and
   `recommendation.rationale` are non-empty and substantive
   (recommendation.claim ≥ 1 sentence, rationale ≥ 2 sentences).

3. **Evidence grounding** — spot-check 2-3 `claims_table` entries per
   run: do the cited files (e.g. `dot_config/kilo/exact_agent/shiki.md`)
   actually exist and contain the claimed line numbers? Flag any
   `final_verdict: accept` claim whose evidence doesn't resolve.

4. **`shallow` pass rate** — percentage of claims marked
   `shallow: pass`. Higher is better (fewer unresolved claims).

5. **Variance** — are the 3 m3 runs similar to each other? Same for
   the 3 deepseek runs? Compute a coarse similarity by counting how
   many `recommendation.claim` sentences overlap word-for-word across
   the 3 runs.

6. **`open_questions_for_main_agent` quality** — count and substantive
   value (are the open questions actually blocking, or are they
   trivial?). Lower count with higher blocking-value is better.

7. **Reasoning depth** — note the `reasoning_tokens` count from the
   run's final-message summary (the benchmark subagents are
   instructed to surface it). DeepSeek V4 Flash at `variant: high`
   should produce substantially more reasoning tokens than M3 at
   default effort.

## Output

Write the comparison to
`/tmp/kilo/shiki-bench/judge-<timestamp>.yaml`. Format:

```yaml
benchmark: shiki-model-pick
date: <YYYY-MM-DD>
judge_model: openrouter/~deepseek/deepseek-v4-flash-latest
runs:
  m3:
    - file: <path>
      status: <ok|rate-limited|error>
      claims_table_count: <int>
      shallow_pass_rate: <0.0-1.0>
      recommendation_claim: <echo>
      recommendation_confidence: <0.0-1.0>
      reasoning_tokens: <int|unknown>
  deepseek:
    - file: <path>
      status: <ok|rate-limited|error>
      claims_table_count: <int>
      shallow_pass_rate: <0.0-1.0>
      recommendation_claim: <echo>
      recommendation_confidence: <0.0-1.0>
      reasoning_tokens: <int|unknown>
comparison:
  m3_avg_claims_table_count: <float>
  deepseek_avg_claims_table_count: <float>
  m3_avg_shallow_pass_rate: <float>
  deepseek_avg_shallow_pass_rate: <float>
  m3_avg_reasoning_tokens: <float|unknown>
  deepseek_avg_reasoning_tokens: <float|unknown>
  variance:
    m3_inter_run_similarity: <low|medium|high>
    deepseek_inter_run_similarity: <low|medium|high>
  evidence_grounding:
    m3_unresolved_evidence: [<list of claims with non-resolving evidence>]
    deepseek_unresolved_evidence: [<list of claims with non-resolving evidence>]
recommendation:
  preferred_model: <m3|deepseek|inconclusive>
  confidence: 0.0-1.0
  rationale: <3-5 sentences citing the comparison numbers>
open_questions_for_main_agent:
  - <only-the-decision-blocking-questions, max 3>
```

## Anti-patterns

- Don't read raw research YAMLs from the main session — only the
  6 verifier output files in `/tmp/kilo/shiki-bench/`.
- Don't fabricate missing runs. If `output-m3-runN-*.yaml` doesn't
  exist, mark the run as `status: missing` and continue.
- Don't propose a different cohort or fleet change. The benchmark is
  to compare M3 vs DeepSeek on shiki's verifier role, in production
  shape, period.
- Don't write outside `/tmp/kilo/shiki-bench/`.
