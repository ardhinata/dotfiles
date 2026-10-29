---
source:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  - https://arxiv.org/abs/2307.03172
  - https://arxiv.org/abs/2601.03269
  - https://arxiv.org/abs/2601.10343
captured: 2026-10-26
freshness: check-2027-04
tags: [agent-instructions, token-budget, skills]
---

# Always-on instruction files cost tokens on every request

Always-loaded instructions cost 5,000 to 10,000 tokens per request, so the
global rule tree needs a measured budget rather than a remembered one.

Captured 2026-10-26 while auditing the 19 global instruction files in
`dot_agents/rules/` and `dot_agents/rules.personal.d/`.

## Finding

Vendor guidance puts the cost of always-loaded instructions at 5,000 to
10,000 tokens per request, and recommends keeping the total under 5,000
tokens. Every extra rule therefore pays for itself on every request, not once.

## Evidence

**Always-loaded instructions cost 5,000 to 10,000 tokens per request.** The
Anthropic Claude cookbook (skills introduction) states this and recommends
keeping total instruction content under 5,000 tokens for efficiency.

**Progressive disclosure is the counter-move.** Layer 1 loads skill metadata
(name and description, about 100 to 200 tokens each) for every skill. Layer 2
loads the `SKILL.md` body only on a trigger. Layer 3 loads referenced files
on demand. Anthropic's own guide states that Claude does not read every skill
in full at the start of a conversation.

**Long contexts dilute instructions.** Liu et al., "Lost in the Middle"
(arXiv 2307.03172) shows a U-shaped recall curve: models use the start and
the end of a long prompt and under-use the middle, sometimes performing below
a closed-book baseline.

**Instruction following degrades with position.** arXiv 2601.03269 ("The
Instruction Gap") reports that instruction compliance falls off for material
in the middle of long inputs, with a primacy and recency bias.

**Every added constraint can cost more than it saves.** The OpenAI developer
community thread "Prompt Anti-Patterns" records cases where stacking extra
reasonable constraints degraded output quality.

**Task solving and scaffold compliance are different skills.** OctoBench
(arXiv 2601.10343) reports a systematic gap between how well an agent solves
a task and how well it follows the scaffold rules for the same task. An agent
can pass the work while ignoring the always-on rules, so rule quality needs
its own measurement, not a proxy of "the task got done".

**Negative clauses are the weakest form.** Anthropic's "Effective context
engineering for AI agents" (2025-09-29) warns against stuffing a prompt with
a laundry list of edge cases, and recommends a small set of canonical examples
instead. It also frames just-in-time loading as a strategy for task content,
not for the behavioral constraints an agent must hold at the moment it
decides.

**The measured local case.**

- Before the trim, the 19 deployed rule files held 41,996 bytes and 6,296
  words, about 9 to 11k tokens of always-on system prompt.
- A 19-subagent audit (one per file) returned 18 TRIM or KEEP ALWAYS-ON and no
  DELETE. Nothing moved into a skill, because every rule's trigger arrives at
  the moment a skill would load too late.
- After the trim the same 19 files render to 22,446 bytes and 3,492 words,
  about 5 to 6k tokens. That is a 45% cut in words and 47% in bytes.
- `rtk gain` on this host measured 15.9% token savings over 541 commands, not
  the 60 to 90 percent the old rule claimed. Small outputs gain nothing:
  `git status --short` was 1,065 bytes raw and 1,064 bytes through rtk.

## Why it matters

Four rules came out of the audit:

- A rule that must guard an action cannot move into a skill. The skill loads
  after the trigger, and the trigger is the action.
- A router rule earns its slot with hazards, not with a trigger list. The
  harness already surfaces skill frontmatter, so a copied trigger list is paid
  for twice.
- Always-on rules that state facts need a measured number, not a remembered
  one.
- Cross-file links between two always-on files are dead weight: the target
  text is already in the same context.

## Scope

This project, 19 global rule files. The token figures come from Anthropic
documentation and local measurement of `rtk gain` on this host.

## Uncertainty

Vendor documentation on skill loading changes often. Re-verify the token
figures and the Anthropic guidance after 6 months, or after a major Claude
Code or OpenCode release. The 19 audit reports live under
`/tmp/opencode/rule-audit/` and are not tracked.

## Sources

- Anthropic, Claude cookbook, "Core Concepts and Progressive Disclosure"
  (skills introduction notebook 01).
- Anthropic, "Fundamentals — the complete guide to building Skills for
  Claude".
- Anthropic, "Effective context engineering for AI agents" (2025-09-29).
- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts",
  arXiv 2307.03172.
- arXiv 2601.03269, "The Instruction Gap: LLMs get lost in following
  instructions".
- OctoBench, "Benchmarking Scaffold-Aware Instruction Following in
  Repository-Grounded Agentic Coding", arXiv 2601.10343.
- OpenAI developer community, "Prompt Anti-Patterns — When More Instructions
  May Harm Model Performance".
- Scale AI, "A Guide to Improving Long Context Instruction Following".
- Local: `rtk gain` on 2026-10-26; the 19 audit reports under
  `/tmp/opencode/rule-audit/` (not tracked).

## See also

- `docs/plans/2026-10-25-agent-instruction-review/` — the audit this entry
  came from
- `.agents/docs/cache/agent-instructions/2026-10-28-harness-rule-discovery.md`
  — the load-path side of the same trade
