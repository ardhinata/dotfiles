# docs/reports/

Findings to hand to the team. Each report describes a problem that still
needs attention. A report has no owner and no tracking issue. A postmortem
in `../post-mortem/` covers an incident that is already closed.

## Reports

| File | Covers |
|---|---|
| [2026-10-31-aft-fused-lane-demotes-semantic-lane.md](2026-10-31-aft-fused-lane-demotes-semantic-lane.md) | The AFT fused search lane ranks the lexical lane above the semantic lane for natural-language queries. The lane weights sit in a plan table that the AFT binary pins, so no config key corrects them. |

## Related source

| Path | Holds |
|---|---|
| `.agents/docs/cache/aft-embedding/` | The measurements behind the AFT reports, with the harness and the query sets. |
| `dot_config/private_cortexkit/aft.jsonc` | The live AFT config. Its comments carry the measurements behind each value. |
