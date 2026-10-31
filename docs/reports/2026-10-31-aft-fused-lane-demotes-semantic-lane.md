---
status: open
severity: minor
---

# The AFT fused search lane demotes the semantic lane for natural-language queries

## Summary

AFT fuses its trigram lane and its semantic lane with weighted reciprocal
rank. For a natural-language query, the fused order places the answer that
the semantic lane ranked first behind a file that the lexical lane ranked
first. The fused lane returns the correct answer first in 17 of 50 queries.
The semantic lane on its own returns the correct answer first in 26 of 50.

The lane weights that cause this sit in a plan table that the AFT binary
pins at compile time. No configuration key reaches them. A project that
accepts the lexical lane must accept this order.

## Steps to reproduce

The harness for this measurement lives at
`.agents/docs/cache/aft-embedding/aft_width_ab.py`. It drives the real `aft`
binary over its NDJSON protocol.

1. Copy `packages/core`, `packages/ai`, `packages/schema`, and `packages/sdk`
   from the opencode source into a scratch git repository. The corpus for
   this report holds 1323 files.
2. Start one proxy for each width. The proxy is
   `dot_shell/helper/executable_embedding_dimensions_proxy.py`. Set
   `EMBEDDING_PROXY_DIMENSIONS` and `EMBEDDING_PROXY_PORT` for each.
3. Build the index for each arm:

```bash
python3 aft_width_ab.py index --root <corpus> --arm m512 --width 512 --port 8099
```

4. Run the query set twice for each arm. The first run fuses the lanes. The
   second run turns the trigram lane off:

```bash
python3 aft_width_ab.py query --root <corpus> --arm m512 --width 512 --port 8099 \
  --queries queries-main.json --label results-fused.json
python3 aft_width_ab.py query --root <corpus> --arm m512 --width 512 --port 8099 \
  --queries queries-main.json --no-trigram --label results-sem.json
```

5. Score both result files. Recall at 1 over the 50 positive queries:

```text
fused       R@1 = 17/50
semantic    R@1 = 26/50
```

## Expected

A natural-language query describes the behaviour of a file in words. The
semantic lane matches that description. The lexical lane matches the words
that the query shares with the source, which for a prose query is often
nothing. The lane that understands the question should place the answer
first.

## Actual

The fused order places the answer at rank 1 in 17 of 50 positive queries.
The semantic lane alone places it at rank 1 in 26 of the same 50.

The candidate set is not the cause. Sort the same fused candidate set by its
`semantic_score` column alone and recall at 1 becomes 24, against the fused
order's 17. The candidates match. Only the order differs.

Only 38 of 1240 returned rows carry the semantic lane. The other 1191
carry the lexical lane, and 11 carry the exact lane. The top row carries
the lexical lane for 48 of the 50 positive queries.

## Environment

| Item | Value |
|---|---|
| AFT binary | 0.62.0, from `@cortexkit/aft-opencode` |
| opencode CLI | 2.2.0 |
| Python | 3.14.8 |
| Corpus | opencode v2.1.0 source, `packages/core`, `packages/ai`, `packages/schema`, `packages/sdk`, 1323 files |
| Index shape | 10,427 chunks, 480-token cap |
| Provider | OpenRouter, `qwen/qwen3-embedding-8b`, 512 dimensions through the local proxy |
| Date | 2026-10-31 |

## Impact

An agent that asks a question in prose receives a weaker answer than the
semantic lane alone would give it. The cost is 9 queries out of 50 at
recall at 1.

Only natural-language queries show this loss. AFT classifies a query shape
before it scores, and the plan table gives the lexical lane the weight for
the other shapes. An identifier query gets lexical 0.8 against semantic 0.2.
A path query gets lexical 0.9 against semantic 0.1. Only the
natural-language shape gives the semantic lane the larger weight, and only
that shape shows the loss.

## Workaround

Turn the trigram lane off for a project whose queries are prose. The
`indexes.trigram` config key controls this. The cost is the loss of the
lexical lane. That lane serves identifier and code-literal queries best.
The trade is worth it only for a project that asks prose questions.

There is no workaround that keeps both lanes and corrects the order.

## Suspected cause

The cause is confirmed in the source. `freeze_non_exact_scores` in
`crates/aft/src/commands/semantic_search/scoring.rs` computes a weighted
reciprocal rank fusion:

```text
fusion_score = sum over lanes of weight / (rrf_constant + position + 1)
```

The weights come from `PlanTable::running_table` in
`crates/aft/src/commands/semantic_search/plan_table.rs`. For the
natural-language shape it gives lexical 0.4 and semantic 0.6, both with
`rrf_constant` 60.

Two effects follow, and both are visible in the measurement:

- A file that both lanes return sums both contributions. The fused top row
  was also in the semantic lane's top 20 for 58 of 62 queries. In 13 queries
  the semantic lane alone placed the answer first and the fused lane did
  not. In all 13, the fused top row was a file that the semantic lane also
  returned.
- A file that only the semantic lane returns receives one contribution. The
  semantic lane's best row loses to a file that the lexical lane ranks
  first.

The plan table is not configurable. `PINNED_PLAN_TABLE_JSON` embeds it in the
binary, and `verify_pinned_plan_table_at_startup` asserts that the running
table matches the pinned one at startup. `PlanTable::from_file` exists, but
no configuration key calls it. Correcting the lane balance needs a change
in AFT.

## Related

- [Embedding width A/B through the AFT semantic lane](../../.agents/docs/cache/aft-embedding/2026-10-31-embedding-width-ab.md)
- [Embedding build tuning](../../.agents/docs/cache/aft-embedding/2026-10-31-embedding-build-tuning.md)
- This report reads the AFT source at `/tmp/opencode/aftsrc`. The path is
  not permanent.
