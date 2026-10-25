# Research steps

The five steps of the review, with the method for each so a reader can repeat
them.

Part of the agent instruction review. See [README.md](README.md) for the index.
## Research steps

### Step 1. Measure the payload

Commands used:

- `wc -c -w` over `~/.agents/rules/*.md` and
  `~/.agents/rules.personal.d/*.md`. The deployed tree is the correct one to
  measure. The `.tmpl` sources are pre-render inputs, and
  `rtk-rules.md.tmpl` is 197 bytes against 1,780 bytes deployed.
- `wc -c -w -l` over `AGENTS.md` and
  `.agents/rules/chezmoi-source-project.md`.
- YAML parse of each `~/.agents/skills/*/SKILL.md` `description`.
- `node -e "require(...).getPonytailInstructions('full')"` to get the byte
  length of the block that is actually injected, not the size of the hook
  script.
- `opencode debug config`, `opencode --version`, `opencode models`.
- `chezmoi managed` to confirm which rule files deploy.

### Step 2. Model profile research

One research pass over public sources for MiniMax M3.1 Flash. It answered
seven questions: specs, instruction adherence, tool-calling reliability,
coding failure modes, effort trade-offs, speed, and comparison against
DeepSeek V4.1 Flash 1017 and GLM 5.3 Flash.

### Step 3. Prompt-design research

One research pass over published guidance: IFScale, Anthropic's
context-engineering and Agent Skills writeups, the OpenAI Codex and GPT-5.2
guides, the agentskills.io specification, the agents.md format, the Cursor
rules documentation, and Chroma's context-rot research.

### Step 4. Internal audit

A full read of all 18 always-on files plus the six skills the routers point
at. Output: an inventory, contradictions, redundancy, over-specification,
missing triggers, a safety inventory, and a ranked defect list.

### Step 5. Four independent cross-checks

Four reviewers with non-overlapping scope: external facts, internal
measurements, the live OpenCode technical surface, and an adversarial review
of the reasoning. Their findings are in "Cross-check results".

### What this review did not do

- No empirical test of rule adherence on this model.
- No read of the `cc-safety-net` policy source. Its block list was inferred
  from bundled output by pattern search.
- No tokenizer. The token figures use a uniform 3.6 to 3.7 bytes per token
  ratio and are approximations.
- No live test of the `policies` layer.

