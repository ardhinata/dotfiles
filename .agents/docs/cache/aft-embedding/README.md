# aft-embedding

Facts about the AFT semantic lane and the local embedding-dimensions proxy:
how the lane is measured, what makes a measurement wrong, and the measured
effect of the vector width.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-10-31 | [Embedding width A/B through the AFT semantic lane](2026-10-31-embedding-width-ab.md) | AFT 0.62.0 source, local embedding-dimensions proxy, opencode source corpus | check 2027-04 | Harness plus query sets live next to this file. Four traps make a run silently wrong: a `configure` payload without `cortexkit_user_config_path` falls back to the fastembed default and returns lexical results only; a query issued while `semantic_status` is not `ready` measures the lexical lane; `semantic.query_timeout_ms` expiring drops the lane and reads as a miss; and `results` is a top-level field. Measured result: 384 versus 512 dimensions is a tie at 50 queries (all p above 0.5), so the live setup stays at 512. |
