---
topic: aft-embedding
date: 2026-10-31
source: AFT 0.62.0 source at /tmp/opencode/aftsrc, local embedding-dimensions proxy, opencode source corpus
freshness: check 2027-04 (AFT semantic lane is volatile; the proxy dimensions parameter is local code)
---

# Embedding width A/B through the AFT semantic lane

## Question

Can the AFT semantic index run at 384 dimensions instead of 512 while the
chunk cap stays at 480 max input tokens, and still rank as well?

## Why it matters

The vector width sets the size of the semantic index. A narrower vector
saves disk, and it costs quality if the ranking loses signal.

## How the measurement is done

The harness drives the real `aft` binary over its NDJSON stdin protocol.
Nothing is reimplemented: the same chunker, the same embed-text caps, the
same query instruction, the same ranking, and the same fused
trigram-plus-semantic lane that the agent sees in production.

Each arm gets:

- its own `AFT_STORAGE_DIR` (the semantic artifact key hashes the full
  `base_url`, so two widths cannot share one storage dir)
- its own `base_url` salt (`http://127.0.0.1:<port>/<salt>/v1`)
- its own proxy instance, started with a different
  `EMBEDDING_PROXY_DIMENSIONS` and `EMBEDDING_PROXY_PORT`

The proxy serves any path that ends in `/embeddings`, drops the path before
the call reaches the provider, and honours a `dimensions` request parameter.
Both Nebius and DeepInfra honour the requested width, so a 384-dim arm needs
no provider change.

Corpus: the opencode source tree (`packages/core`, `packages/ai`,
`packages/schema`, `packages/sdk`), copied into a scratch git repo so the
trigram index sees a normal project.

## Four traps that produce a false result

1. **`configure` needs `cortexkit_user_config_path`.** The `configure`
   payload takes an absolute path to the user-tier `aft.jsonc`. Without it
   AFT reads no user tier, so the semantic backend falls back to the
   fastembed default (`all-MiniLM-L6-v2`). The query vector then does not
   match the index vectors, and every query returns lexical results only.
   The symptom is a fast, silent, plausible-looking result set.
2. **A query during a build measures the wrong lane.** While
   `semantic_status` is `loading` or `building`, AFT answers with lexical
   fallback only. Poll until `semantic_status == "ready"`.
3. **`results` is a top-level response field**, not under `data`.
4. **The query timeout silently removes the lane.** See the section below.

## Files

- `aft_width_ab.py` — the harness. Subcommands: `index`, `query`, `report`.
- `queries-pilot.json` — 28 positive and 6 negative queries over a 41-file
  corpus. Used to prove the pipeline before spending on a real run.
- `queries-main.json` — 50 positive and 12 negative queries over the
  1323-file corpus. Every `expect` path was checked against the corpus
  before the run.

## Method note: how to judge the arms

The pilot corpus was too small to separate the arms. At 41 files the top
result is usually right for both widths, so the difference fell inside the
noise of a handful of queries.

The main corpus is 1323 files, so many near-duplicate candidates compete
for each query. That is what makes the ranking sensitive to width.

Score with recall@1, recall@5, recall@10, and MRR@10 over the positive
queries. The negative queries have no ground truth; their useful signal is
the top score the lane still returns. A width that keeps the positive top
score well above the negative top score separates signal from noise.

## A third trap: the query timeout

`semantic.query_timeout_ms` defaults to 3000 ms. A remote query embed takes
1-3 s, so under load the semantic lane times out and AFT answers with
lexical results only. The result set looks like a ranking failure, but it is
a timeout. `lanes.semantic.status` reports `unavailable` for that query.

The harness asserts `lanes.semantic.status == "ready"` on every query and
aborts otherwise. Without that assertion the earlier run scored R@1 = 7/50
for 512 dimensions, which was the timeout, not the width.

The live `dot_config/private_cortexkit/aft.jsonc` already sets 8000 ms. A
harness that runs two builds at once needs about 30000 ms.

## Result

Both arms indexed the same corpus to the same shape: 1323 files, 10,427
chunks. The 512 build took 651 s, the 384 build 1197 s (the 384 build shared
the provider quota with a concurrent 512 query run, so the two times are not
comparable).

Index size proves the arms really differ in width:

| arm | semantic.bin | delta |
|---|---|---|
| 512 | 28,463,349 B | |
| 384 | 23,124,725 B | -5,338,624 B |

5,338,624 = 10,427 chunks x 128 dimensions x 4 bytes, exactly. The 384 arm
stored genuinely narrower vectors.

### Semantic-only lane (trigram off)

| metric | 512 | 384 |
|---|---|---|
| R@1 | 26/50 | 27/50 |
| R@5 | 38/50 | 37/50 |
| R@10 | 42/50 | 43/50 |
| R@20 | 46/50 | 47/50 |
| MRR | 0.631 | 0.640 |

### Fused lane (trigram on, what the agent sees)

| metric | 512 | 384 |
|---|---|---|
| R@1 | 17/50 | 17/50 |
| R@5 | 32/50 | 32/50 |
| R@10 | 37/50 | 39/50 |
| R@20 | 42/50 | 42/50 |
| MRR | 0.462 | 0.467 |

### Significance

Exact McNemar on the paired per-query hit indicators, and an exact sign test
on the paired MRR differences:

| lane | comparison | discordant | p |
|---|---|---|---|
| semantic | R@1 | 512-only 1, 384-only 2 | 1.000 |
| semantic | R@5 | 512-only 1, 384-only 0 | 1.000 |
| semantic | MRR | 384 better 9, 512 better 7 | 0.804 |
| fused | R@1 | 512-only 0, 384-only 0 | 1.000 |
| fused | R@10 | 512-only 0, 384-only 2 | 0.500 |
| fused | MRR | 384 better 7, 512 better 4 | 0.549 |

The 95 percent CI on the paired MRR difference (384 minus 512) is
[-0.028, +0.047] for the semantic lane and [-0.004, +0.014] for the fused
lane. Both intervals straddle zero.

## Conclusion

**No measurable difference at 50 queries.** 384 is not worse, and it is not
better. The point estimates lean slightly to 384 (paired rank 7 wins vs 4
losses fused, 9 vs 7 semantic-only) but that is noise at this sample size.

At n = 50 with the measured paired spread, this design can only detect a
true MRR gap of about 0.054 (8.5 percent relative) in the semantic lane. A
real difference smaller than that is invisible here.

### How this sits next to the 2026-10-28 A/B

The earlier A/B (468 files, 16,252 chunks, 40 needle plus 10 fixture
queries) paired every width against a 1024-dim arm and found 384 at 2
better and 6 worse. That arm set was 1024, 768, 512, and 384. This run
pairs 384 against 512.

The two agree once the pairing is accounted for: the earlier run had 512
level with 1024, and this run has 384 level with 512. So 384 sits close to
512, and the earlier 384-versus-1024 loss was the 1024 side of that same
gap. Neither run isolates a 384-specific defect.

The earlier run also found the fused lane's recall@1 at 0.86 for every
width. This run finds the fused lane at 17/50 (0.34) while the semantic
lane alone reaches 26/50 (0.52). The two are not in conflict, because they
measured different corpora and different query sets. They agree on the
point that matters for a width decision: the fused lane is the same at
every width.

### What this does not change

The live setup stays at 512 dimensions. Two reasons:

1. The width is inside the AFT index fingerprint
   (`SemanticIndexFingerprint::from_config` takes `dimension`). Moving to
   384 forces a full re-embed of every root.
2. The width is *not* inside the Magic Context identity for stored rows.
   The memories and git-commit rows are keyed by `providerIdentity` alone,
   which holds the endpoint but not the vector width. A width change
   therefore leaves the old rows in place, and the new narrower queries
   match nothing, because the cosine of a length mismatch is 0. The
   memory semantic lane stops retrieving until those rows are re-embedded
   by hand. A width change is not self-applying on the Magic Context
   side.

Switching to 384 would save 18.8 percent of the semantic index, about 16 MB
on a 10,427-chunk index. That is a disk saving, not a speed or quality win.

### The fused lane is mostly lexical, and that is the bigger finding

In the fused lane only 38 of 1240 returned rows came from the semantic lane
against 1191 lexical. Fused R@1 (17/50) is worse than semantic-only R@1
(26/50) on the same queries.

This is not a candidate-set effect. Re-ranking the *same* fused candidate
set by its `semantic_score` column alone gives R@1 24 against the fused
order's 17. The candidates are the same; only the ordering differs.

The cause is in AFT's scoring. `freeze_non_exact_scores` computes a weighted
reciprocal rank fusion: `weight / (rrf_constant + position + 1)`. The weights
come from `PlanTable::running_table`, which for a natural-language query
gives lexical 0.4 and semantic 0.6, both with `rrf_constant` 60.

Two consequences:

- A file found by *both* lanes sums both contributions. The fused top-1 row
  was also in the semantic lane's top 20 for 58 of 62 queries, and in all
  13 queries where the semantic lane alone put the wanted file first but
  fusion did not, the fused top-1 was a file the semantic lane also
  returned. The lexical lane promotes files the semantic lane agrees with.
- A file found *only* by the semantic lane gets one contribution. The
  semantic lane's best hit loses to a file the lexical lane ranks first.

The top-1 row source is `lexical` for 48 of 50 positive queries in both
arms.

**This is not configurable.** The plan table is pinned into the binary as
`PINNED_PLAN_TABLE_JSON` and `verify_pinned_plan_table_at_startup` asserts
the running table matches it. `PlanTable::from_file` exists but no config
key reaches it. Changing the lane balance is an upstream AFT change.

What is configurable is the lane mix itself: `indexes.trigram` is a config
key. The semantic-only arm is what a project with `"trigram": false` sees.
On this corpus that is worth 9 hits at R@1 (26 against 17). It costs the
lexical lane, which is the fast path for identifier and code-literal
queries, where the plan table gives lexical 0.8 to 0.9 and semantic 0.1 to
0.2. The measured queries here are natural-language sentences, which is the
one shape where the semantic lane is meant to win.

### If someone repeats this

- Run the two arms sequentially, not concurrently, so both get the provider
  quota and the timings are comparable.
- Assert the lane state per query. A timeout silently reads as a miss.
- Score the semantic-only lane and the fused lane separately. The fused
  numbers hide the semantic lane's quality.
- Use a query set with several acceptable target files per question where
  sibling implementations exist (`migration.ts` and `migration.gen.ts`).
  One strict target per question punishes both arms for the same reason.

## See also

- [Embedding build tuning: token cap, batch size, and provider routing](2026-10-31-embedding-build-tuning.md)
- [The AFT fused search lane demotes the semantic lane for natural-language queries](../../../../docs/reports/2026-10-31-aft-fused-lane-demotes-semantic-lane.md)
  — the fusion finding written up as a report to hand to the team
