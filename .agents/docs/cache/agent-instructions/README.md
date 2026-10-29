# agent-instructions

Cost and load-path facts about the always-on instruction files that every
agent request carries.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-10-26 | [Always-on instruction files cost tokens on every request](2026-10-26-always-on-instruction-files.md) | Anthropic docs, arXiv 2307.03172, 2601.03269, 2601.10343, Scale AI | check 2027-04 | 19 global rule files measured at 41,996 B before the trim and 22,446 B after. Vendor guidance puts the cost at 5,000–10,000 tokens per request. |
| 2026-10-28 | [How each harness discovers agent rule files](2026-10-28-harness-rule-discovery.md) | Official docs for 10 harnesses | check 2027-01 | No harness discovers `~/.agents/rules/` natively. Only OpenCode and Copilot CLI can load a directory of rule files. |
