# Subagent research fleet — `~/.config/kilo/agent/`

This directory holds the **5-subagent research fleet** for Kilo. The agents
are managed by chezmoi; their canonical source is
`dot_config/kilo/exact_agent/` in the chezmoi source repo, deployed
verbatim to this directory via `chezmoi apply`.

The design is documented in `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`
("subagent fleet for research + verification"). This README is the human
quick-start; the plan is the source of truth.

## What is this for?

When the main agent is stuck or wants a second opinion on a research
question, it spawns a small fan-out of subagents and reads **only the
verifier's synthesised report**. The four research subagents handle
adversarial review, synthesis, meta-auditing, and comparison; the
verifier arbitrates between them.

If you have not seen this in action yet: the design is a research
discovery tool — it does not modify code or write files outside the
report directory.

## The five subagents

| File | Name | Role | Model | Sample tilt |
|---|---|---|---|---|
| `haru.md` | 春 haru (spring) | Adversarial — assume the leading candidate is wrong; surface top 3 failure modes | `openrouter/google/gemini-2.5-flash-lite` | T=0.2, top_p=0.9 |
| `natsu.md` | 夏 natsu (summer) | Synthesizer — propose up to 3 coherent candidate answers | `openrouter/xiaomi/mimo-v2.5` | T=0.5, top_p=0.9 |
| `aki.md` | 秋 aki (autumn) | Assumption-auditor — list up to 3 hidden assumptions and rate `likely_wrong` | `openrouter/deepseek/deepseek-v4-flash-0731` | T=0.5, top_p=0.9 |
| `fuyu.md` | 冬 fuyu (winter) | Comparator — rank candidates on a multi-criterion rubric | `openrouter/z-ai/glm-4.7-flash` | T=1.0, top_p=0.95 |
| `shiki.md` | 四季 shiki (four seasons) | Verifier — read the research YAML reports and produce one consolidated answer. **Mandatory** when ≥2 research subagents ran. | `openrouter/minimax/minimax-m3` | T=0.4, top_p=0.95 |

All four research subagents run at `variant: low` (cheap, fast). The
verifier runs at `variant: high` (frontier quality for the final answer).
Each is `mode: subagent, hidden: true` — invisible to the `@`-autocomplete
but invocable via the `task` tool.

## Naming

The four research subagents are named after the Japanese four seasons
(春/夏/秋/冬). The verifier is named **shiki** (四季, "four seasons")
because it spans all four seasonal roles. The names pair naturally with
the four prompt-conditioned roles the design depends on:

- `haru` (spring) — revival / fresh attack; **attacking** the leading
  candidate.
- `natsu` (summer) — peak / fullness; **synthesising** candidates.
- `aki` (autumn) — harvest / review; **auditing** assumptions.
- `fuyu` (winter) — cold / clear; **comparing** on a rubric.
- `shiki` (four seasons) — the cycle that contains all four.

If you prefer different mnemonics, the YAML `subagent:` field in each
file's output contract can be any short slug you choose — the field name
*content* is the only thing the verifier parses for cross-reference.
See "Customisation" below.

## How to invoke them

### Manually (via `task`)

```text
task(haru, "Find failure modes for: <leading candidate>")
task(natsu, "Propose candidates for: <question>")
task(aki, "List hidden assumptions in: <framing>")
task(fuyu, "Compare approaches A and B on correctness/cost/risk/complexity")
task(shiki, "Verify the research-*.yaml reports for: <question>")
```

### Programmatically (main-agent fan-out)

The main agent uses the invocation pattern in plan §5. The default is
**N=4** (all four research subagents in parallel), then shiki. For
high-stakes questions the main agent may run haru first, refine the
question, then run natsu/aki/fuyu with the refined question (plan §5.2).

### What you see in your context

The main agent **never reads raw research output directly** when ≥2
research subagents ran. Only shiki's report enters your context. To
audit, the main agent can surface shiki's full `claims_table`; the raw
research YAML files are at
`.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-{haru,natsu,aki,fuyu}[-<topic>].yaml`.

## Customisation

Each subagent file is plain YAML frontmatter + Markdown body. Edit them
with `chezmoi edit ~/.config/kilo/agent/<name>.md` so the change goes
back through the chezmoi source tree.

Three knobs are most useful:

1. **`model:`** — swap the underlying model. The four are different
   families (Google / Xiaomi / DeepSeek / Z.ai) for inductive-bias
   diversity. Keeping this constraint is the whole point of the design.
   **Note (2026-08-25):** haru's pick is `google/gemini-2.5-flash-lite`,
   not `google/gemma-4-31b-it` — Google has both a Gemma family and a
   Gemini family. The cohort still spans 4 distinct architectures
   (Gemini / MiMo / DeepSeek-V4 / GLM); the "4 distinct families"
   constraint is **4 distinct architecture families**, not 4 distinct
   parent companies.
2. **`temperature:` / `top_p:`** — sampling tilt. Per plan §2, on
   reasoning models this only affects the final-answer sampler, not the
   reasoning trace. Useful for fine control; the structural diversity
   comes from the prompt-conditioned roles themselves.
3. **`permission:`** — scope edit/write to `.tmp/docs/subagent-runs/`
   and external directories. Don't widen edit or bash without a good
   reason; the read-only default is load-bearing.

To remove a subagent, delete the file from
`dot_config/kilo/exact_agent/` in the chezmoi source and run
`chezmoi apply`.

## Operational notes

### Where reports go

`.tmp/docs/subagent-runs/YYYYMMDD_HHMMss-<name>[-<topic>].yaml` — this directory is in
the shared-context git repo but added to its `.gitignore` so the
per-run YAML files do not pollute shared-context commit history
(commit `5d6fd6f`).

### Cost ceiling

Worst case = 4× cheap flash + 1× frontier = roughly 2-3× a single
frontier call. The four research subagents run on flash-class models
(~$0.035–$0.40 per million input tokens) so the per-question budget
is small. The 2026-08-25 pinentry-simulation live run cost **$0.08**
for 4 research subagents (shiki ran BYOK) — well under the ceiling.
haru's `google/gemini-2.5-flash-lite` pin starts with
`google-ai-studio/flex` at $0.05/M in / $0.005/M cache_read, the
cheapest live route in the cohort.

### `variant: low` coverage gap

Per plan §4.2, `variant: low` is silently dropped on `natsu` and
`fuyu` because those models fall into OpenRouter's boolean-toggle
branch (instant/thinking only). `aki` honours it via the `[low,
medium, high, max]` effort set. `haru` (Gemini 2.5 Flash Lite) does
not advertise `reasoning_effort` in its `supported_parameters`; the
OpenRouter `reasoning.effort` envelope likely applies — verify per
session with `kilo provider list --json`. Acceptable for synthesis
(long-context coherence matters more than effort tuning) and
comparison (the `temperature: 1.0` / `top_p: 0.95` sampling is the
intended lever).

### Permissions inheritance

The KiloTask pre-pend layer auto-denies `task`, `question`, `suggest`,
and `interactive_terminal` inside every subagent session — subagents
cannot spawn further subagents or query the user. Parent `permission`
concatenates; parent `deny` rules survive child permission inheritance.
The full permission precedence is in
`.agents/docs/cache/kilo-subagents/2026-08-15-permissions-actions-precedence.md`.

## Plan history

This README and the 5 subagent files were authored in three turns on
2026-08-25:

1. Authored with English role names
   (`research-adversarial.md` etc.) at `.agents/kilo/agent/`.
2. Moved to chezmoi-managed global at
   `dot_config/kilo/exact_agent/`.
3. Renamed to the four-seasons scheme (this version).

The design rationale (RCAF vs tilted-sampling tradeoff, family-diversity
constraint, `variant: low` gap, two-pass verification flow, etc.) is
in the plan at
`docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`.

The per-model provider/benchmark snapshot at
`.agents/docs/cache/kilo-subagents/2026-08-25-survivor-provider-benchmark-snapshot.md`
captures the OpenRouter pricing + uptime + supported_parameters for
the 4 survivor models; re-verify before locking production (OpenRouter
prices drift weekly).

## See also

- **Plan**: `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` —
  full design, role descriptions, sampling rationale, validation
  checklist.
- **Provider benchmark snapshot**:
  `.agents/docs/cache/kilo-subagents/2026-08-25-survivor-provider-benchmark-snapshot.md`
- **Frontmatter reference** (Kilo schema for the YAML):
  `.agents/docs/cache/kilo-subagents/2026-08-15-agent-frontmatter-reference.md`
- **Permission precedence**:
  `.agents/docs/cache/kilo-subagents/2026-08-15-permissions-actions-precedence.md`
- **Reasoning variants per provider**:
  `.agents/docs/cache/kilo-subagents/2026-08-15-reasoning-variants-by-provider.md`
- **OpenRouter skill** (for re-verifying model availability):
  `.agents/kilo/skills/openrouter-api/SKILL.md`
