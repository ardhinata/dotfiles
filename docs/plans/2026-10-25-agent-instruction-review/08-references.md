# References

Sources for the model profile, the prompt-design evidence, and the harness
claims.

Part of the agent instruction review. See [README.md](README.md) for the index.
## References

### Model

- MiniMax M3.1 Flash announcement — https://www.minimax.io/blog/minimax-m31f
- MiniMax Codex guide (effort ladder, 512K client window) —
  https://platform.minimax.io/docs/m-plan/codex.md
- MiniMax tool-use guide (`reasoning_content`, interleaved thinking) —
  https://platform.minimax.io/docs/guides/text-m3-function-call
- MiniMax text-generation guide —
  https://platform.minimax.io/docs/guides/text-generation
- Artificial Analysis model page —
  https://artificialanalysis.ai/models/minimax-m3-1-flash
- AA-Omniscience definition —
  https://artificialanalysis.ai/evaluations/omniscience
- Artificial Analysis launch thread —
  https://x.com/ArtificialAnlys/status/2112211865128608002
- AI/ML API hands-on review (the controlled admit-uncertainty test, the effort
  ladder, the effect-ladder comparison) —
  https://aimlapi.com/blog/minimax-m3-1-flash-review
- Atomic Agent test (low against max on one task, loop detector) —
  https://atomicagent.io/blog/minimax-m3-1-flash/
- BenchLeader model page (Terminal-Bench, LiveBench, IFBench gap) —
  https://www.benchleader.com/models/minimax-m3-1-flash
- BenchLeader IFBench leaderboard (MiniMax M3 at 82.9%, rank 2) —
  https://www.benchleader.com/benchmarks/aa_ifbench
- OpenCode public usage data —
  https://opencode.ai/data/minimax/minimax-m3-1-flash

### Prompt design

- IFScale — https://arxiv.org/abs/2507.11538
- OctoBench, scaffold-aware instruction following in repository-grounded
  agentic coding — https://arxiv.org/abs/2601.10343
- Anthropic, effective context engineering —
  https://www.anthropic.com/research/effective-context-engineering-for-ai-agents
- Anthropic, Agent Skills —
  https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic, writing effective tools —
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, Claude Code best practices —
  https://www.anthropic.com/research/claude-code-best-practices
- OpenAI, Codex prompting guide —
  https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- OpenAI, GPT-5.2 prompting guide —
  https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- agentskills.io specification — https://agentskills.io/specification
- agents.md — https://agents.md
- Cursor rules — https://cursor.com/docs/rules
- Chroma, context rot — https://research.trychroma.com/context-rot

### Harness

- OpenCode config schema — https://opencode.ai/config.json
- OpenCode permissions (v2 action names `shell` and `subagent`, last match
  wins) — https://opencode.ai/docs/permissions
- OpenCode policies — https://opencode.ai/docs/policies
- OpenCode models and variants — https://opencode.ai/v2/docs/models
- OpenCode instructions — https://opencode.ai/v2/docs/instructions
- OpenCode skills (metadata lives in the `skill` tool description, and `deny`
  hides a skill) — https://opencode.ai/docs/skills

### Skills design

Used by the skills analysis. Each is graded HIGH (primary spec, paper with
direct measurement, or official vendor doc), MEDIUM (vendor guidance without
measurement, or a technical blog with measurement), or LOW (aggregator, or
inference).

- agentskills.io specification (frontmatter constraints, 500-line and 5,000
  token recommendation) — https://agentskills.io/specification — HIGH
- agentskills.io implementor guide (50 to 100 tokens per skill in the
  catalog) — https://agentskills.io/client-implementation/adding-skills-support.md — HIGH
- agentskills.io, optimizing descriptions (trigger-first framing, imperative
  phrasing, the labelled-query trigger eval) —
  https://agentskills.io/skill-creation/optimizing-descriptions — HIGH
- agentskills.io, best practices (conditional reference loads, the
  "overly comprehensive skills can hurt" warning) —
  https://agentskills.io/skill-creation/best-practices — HIGH
- Anthropic, equipping agents with Agent Skills (100+ skills as a working
  scale, and test skills against every model you will use) —
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices — HIGH
- Anthropic, Claude Code skills (1,536-character listing truncation,
  `disable-model-invocation`, `paths:` scoping) —
  https://code.claude.com/docs/en/skills — HIGH
- Anthropic, writing effective tools (namespacing effects vary by model) —
  https://www.anthropic.com/research/writing-tools-for-agents — HIGH
- Anthropic, advanced tool use (tool search, 49% to 74% with a large library) —
  https://www.anthropic.com/research/advanced-tool-use — HIGH
- OpenAI, Codex skills (2% catalog budget, description shortening, front-load
  the trigger) — https://developers.openai.com/codex/build-skills — HIGH
- OpenAI, skills in the Responses API (skill instructions are user-prompt
  priority, not system-prompt priority) —
  https://developers.openai.com/api/docs/guides/tools-skills — HIGH
- Cursor rules (four activation modes) — https://cursor.com/docs/context/rules — HIGH
- OctoBench, scaffold-aware instruction following in repository-grounded
  agentic coding (the per-channel ISR table: 82.98 for Claude.md against
  12.33 for Skill.md on the same model) —
  https://arxiv.org/abs/2601.10343 — HIGH
- SRA-Bench (26,262-skill corpus, no monotonic size trend in skill-loading
  rationality, and the "enumerate skills in context fails to scale" finding) —
  https://arxiv.org/abs/2604.24594 — HIGH
- Progressive disclosure for agentic long-document reasoning (a hierarchical
  pack never beat a flat pack and collapsed on a weak-navigator harness) —
  https://arxiv.org/abs/2607.17598 — HIGH
- Skill activation as precision and recall (measured description-edit
  interference, 46.3% to 67.3% micro-recall) —
  https://www.agentic-patterns.com/patterns/skill-activation-as-precision-recall — MEDIUM
- Tool selection at scale (over-presentation costs choice accuracy) —
  https://arxiv.org/abs/2605.24660 — HIGH

### Internal

- `.agents/skills/document-conventions/references/structure-and-length.md` —
  the 30-80 line target and 150-line ceiling
- `dot_agents/rules/.template-resources/` — six host-rendered snippets, not
  deployed (`chezmoi managed` count is 0)
- `dot_config/opencode/private_opencode.jsonc` — the effective config
- `dot_agents/skills/` — the 11 skills analysed, 304,451 bytes total

