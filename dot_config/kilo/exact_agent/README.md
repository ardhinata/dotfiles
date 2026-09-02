# Subagent research fleet — `~/.config/kilo/agent/`

This directory holds the **5-subagent research fleet** for Kilo. The
agents are managed by chezmoi; their canonical source is
`dot_config/kilo/exact_agent/` in the chezmoi source repo, deployed
verbatim to this directory via `chezmoi apply`.

**This fleet is globally deployed.** The agent bodies are
project-agnostic — they work the same way in any working directory.
Reports land in a global write target
(`~/.local/share/kilo/subagent-runs/`), not under the project tree.

This fleet was rebuilt 2026-09-01 from scratch (abandoning the
2026-08-17-subagent-creative-conservative plan and all prior research
docs) on the user's criterion: **minimise exit-early + thinking-doom-
loop failure modes**, with family diversity dropped as a constraint.
The benchmark that drove the shiki model pick is at
`/tmp/kilo/shiki-bench/judge-20260901_230145.yaml` (transient, delete
when done auditing) and the route probe at
`.agents/docs/cache/kilo-subagents/2026-09-01-shiki-route-probe.md` (in
your project's knowledge cache; if missing, see
`~/.config/kilo/skills/subagent-fleet/references/permission-block.md`
§"Global write target" for the canonical location pattern).

## What is this for?

When the main agent is stuck or wants a second opinion on a research
question, it spawns a small fan-out of subagents and reads **only the
verifier's synthesised report**. The four research subagents handle
adversarial review, synthesis, meta-auditing, and comparison; the
verifier arbitrates between them.

The fleet is a research discovery tool — it does not modify code or
write files outside the report directory
(`~/.local/share/kilo/subagent-runs/`) and `/tmp/kilo/`.

## The five subagents

| File | Name | Role | Model | Variant | Sampling |
|---|---|---|---|---|---|
| `haru.md` | 春 haru (spring) | Adversarial — assume the leading candidate is wrong; surface top 3 failure modes | `openrouter/xiaomi/mimo-v2.5-pro` | none (boolean toggle) | T=0.2, top_p=0.9 |
| `natsu.md` | 夏 natsu (summer) | Synthesizer — propose up to 3 coherent candidate answers | `openrouter/z-ai/glm-5.3-flash` | `low` | T=0.5, top_p=0.9 |
| `aki.md` | 秋 aki (autumn) | Assumption-auditor — list up to 3 hidden assumptions and rate `likely_wrong` | `openrouter/deepseek/deepseek-v4-flash-0731` | `high` | T=0.3, top_p=0.85 |
| `fuyu.md` | 冬 fuyu (winter) | Comparator — rank candidates on a multi-criterion rubric | `openrouter/z-ai/glm-5.3-flash` | `low` | T=1.0, top_p=0.95 |
| `shiki.md` | 四季 shiki (four seasons) | Verifier — read the research YAML reports and produce one consolidated answer. **Mandatory** when ≥2 research subagents ran. | `openrouter/deepseek/deepseek-v4-flash-0731` | `high` | T=0.4, top_p=0.95 |

Cohort spans **3 architecture families** (Xiaomi MiMo, Z.ai GLM,
DeepSeek V4). Family diversity is not a constraint — exit-early and
thinking-doom-loop resistance are. See "Cohort design" below.

Each is `mode: subagent, hidden: true` — invisible to the `@`-autocomplete
but invocable via the `task` tool.

## Cohort design

**Why these models.** The 2026-09-01 live OpenRouter `/v1/models`
snapshot and route probe drove the picks. The two failure modes the
criterion filters for are:

- **Exit-early** — model gives up before completing the YAML output
  contract. Mitigated by selecting models with high
  `supported_efforts` + `parallel_tool_calls` + `structured_outputs`
  on the routes we pin.
- **Thinking-doom-loop** — model burns reasoning budget circling
  without producing structured output. Mitigated by picking models
  where reasoning_effort is genuinely honoured (so the lever exists),
  not by upping the lever to mask bad behaviour.

Per-model rationale:

- **haru** (`xiaomi/mimo-v2.5-pro`): boolean-toggle reasoning (no
  effort lever), but it just thinks regardless and produces 24-30
  reasoning tokens on a 1-token probe. Cheap, stable, the
  adversarial-stance prompt does the real work. Variant field is
  intentionally omitted from frontmatter (would be silently dropped).
- **natsu** (`z-ai/glm-5.3-flash`, `variant: low`): reasoning_effort
  is forwarded on `parasail/fp8`, `deepinfra/fp8`, `novita/fp8` (all
  confirmed in the route probe). `low` effort is cheap; the synthesis
  lever is the prompt-conditioned role, not deep reasoning.
- **aki** (`deepseek/deepseek-v4-flash-0731`, `variant: high`):
  dated id (not the `~latest` router alias, which drifts), pinned
  to `relace/fp4` and `streamlake/fp8` (sail-research and akashml
  dropped today — 429/503 on the route probe). `high` effort for
  deep assumption-hunting.
- **fuyu** (`z-ai/glm-5.3-flash`, `variant: low`): same model as
  natsu, but `T=1.0` to range over the rubric edges. Avoids the
  qwen3.7-flash doom-loop risk that the v2 aki assumption audit
  flagged (qwen defaults to >60% reasoning tokens regardless of
  effort).
- **shiki** (`deepseek/deepseek-v4-flash-0731`, `variant: high`):
  **previously `minimax/minimax-m3`** — moved 2026-09-01 after the
  benchmark showed M3 silently drops `reasoning_effort` (5-point
  invariance probe in the route-probe cache entry confirmed
  `reasoning_tokens` is constant at 25 across `effort: high`,
  `effort: low`, no-field, `enabled: true`). The token-plan-on-M3
  advantage does not offset the loss of the verifier's effort lever.

## Naming

The four research subagents are named after the Japanese four seasons
(春/夏/秋/冬). The verifier is named **shiki** (四季, "four seasons")
because it spans all four seasonal roles. The names pair naturally
with the four prompt-conditioned roles the design depends on:

- `haru` (spring) — revival / fresh attack; **attacking** the leading
  candidate.
- `natsu` (summer) — peak / fullness; **synthesising** candidates.
- `aki` (autumn) — harvest / review; **auditing** assumptions.
- `fuyu` (winter) — cold / clear; **comparing** on a rubric.
- `shiki` (four seasons) — the cycle that contains all four.

If you prefer different mnemonics, the YAML `subagent:` field in each
file's output contract can be any short slug you choose — the field
name *content* is the only thing the verifier parses for cross-reference.

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

The main agent uses the invocation pattern in
`~/.config/kilo/skills/subagent-fleet/references/invocation-pattern.md`.
The default is **N=4** (all four research subagents in parallel), then
shiki. For high-stakes questions the main agent may run haru first,
refine the question, then run natsu/aki/fuyu with the refined
question.

### What you see in your context

The main agent **never reads raw research output directly** when ≥2
research subagents ran. Only shiki's report enters your context. To
audit, the main agent can surface shiki's full `claims_table`; the raw
research YAML files are at
`~/.local/share/kilo/subagent-runs/YYYYMMDD_HHMMss-{haru,natsu,aki,fuyu,shiki}[-<topic>].yaml`.

## Customisation

Each subagent file is plain YAML frontmatter + Markdown body. Edit them
with `chezmoi edit ~/.config/kilo/agent/<name>.md` so the change goes
back through the chezmoi source tree.

Three knobs are most useful:

1. **`model:`** — swap the underlying model. Re-verify against live
   OpenRouter `/v1/models` and re-probe the route pin in
   `~/.config/kilo/kilo.jsonc` before locking production — OpenRouter
   prices and route health drift weekly.
2. **`variant:`** — only honoured on models that expose
   `reasoning_effort` in `supported_parameters` (DeepSeek V4 Flash,
   Z.ai GLM 5.3 Flash, OpenAI, Anthropic adaptive). On boolean-toggle
   models (Xiaomi MiMo, Google Gemma), `variant:` is silently dropped —
   omit it from frontmatter to avoid the lie.
3. **`permission:`** — scope edit/write to
   `~/.local/share/kilo/subagent-runs/` and `/tmp/kilo`. Don't widen
   edit or bash without a good reason; the read-only default is
   load-bearing.

To remove a subagent, delete the file from
`dot_config/kilo/exact_agent/` in the chezmoi source and run
`chezmoi apply`.

## Operational notes

### Where reports go

`~/.local/share/kilo/subagent-runs/YYYYMMDD_HHMMss-<name>[-<topic>].yaml`

This directory is **global** — under the parent kilo state dir, not
the project tree. Reports from any project land in the same place.
The directory is created on first subagent run; if it doesn't exist
yet, the subagent's first `mkdir -p` succeeds (it has external
directory access for this path).

The directory is not git-tracked and not gitignored — it's outside
all repo working trees. If you want periodic cleanup, add a
`rm -rf ~/.local/share/kilo/subagent-runs/old-*.yaml` to your shell
cleanup, or move the reports to a per-project location from the
parent agent (the parent can `mv` files into
`<project>/.tmp/docs/subagent-runs/` for cross-worktree visibility).

### Cost ceiling

The 4 research subagents run on flash-class models
(`$0.03–$0.075/M` prompt). Aki and shiki share `deepseek-v4-flash-0731`
at `variant: high` ($0.065/M prompt + ~$0.016/M cache_read). Worst-case
4-call research + 1 shiki ≈ $0.30/M aggregate. Well within the
per-question budget.

### Variant exposure table

| Role | Model | `reasoning_effort` exposed? | Variant in frontmatter | Honoured at the API? |
|---|---|---|---|---|
| haru | xiaomi/mimo-v2.5-pro | NO (boolean toggle) | (omitted) | n/a |
| natsu | z-ai/glm-5.3-flash | YES | `low` | YES |
| aki | deepseek-v4-flash-0731 | YES | `high` | YES |
| fuyu | z-ai/glm-5.3-flash | YES | `low` | YES |
| shiki | deepseek-v4-flash-0731 | YES | `high` | YES |

### Permission block externalisation

The shared permission block + operational discipline preamble (≈50
lines × 5 files = 250 lines previously duplicated) lives at
`~/.config/kilo/skills/subagent-fleet/references/permission-block.md`
(deployed from
`dot_config/kilo/exact_skills/subagent-fleet/references/permission-block.md`).
Each agent body has a 6-line `## Operational discipline` section that
points at the shared ref; the YAML `permission:` block in each
frontmatter is identical and cannot be externalised (Kilo frontmatter
needs it inline).

### Permissions inheritance

The KiloTask pre-pend layer auto-denies `task`, `question`, `suggest`,
and `interactive_terminal` inside every subagent session — subagents
cannot spawn further subagents or query the user. Parent `permission`
concatenates; parent `deny` rules survive child permission inheritance.
The full permission precedence is in
`.agents/docs/cache/kilo-subagents/2026-08-15-permissions-actions-precedence.md`
(in this project's knowledge cache; equivalent docs live at
`~/.config/kilo/`-rooted references if your project lacks
`.agents/docs/cache/`).

## Plan history

- **2026-08-17** — initial `creative-conservative` plan authored at
  `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md`.
  Multi-week iteration with empirical passes; family diversity was the
  original invariant.
- **2026-08-25** — five-season agent bodies first deployed under
  `dot_config/kilo/exact_agent/`.
- **2026-08-30** — empirical-pass halt (kilo `task` tool does not
  surface `gen-...` IDs, blocking the steps_used measurement layer);
  user chose to wait for a kilo fix.
- **2026-09-01** — user requested a from-scratch rebuild, dropping
  the creative-conservative plan. Fleet revaluation produced 5
  research artefacts + 2 shiki consolidations + a 6-run benchmark
  (3 m3 + 3 deepseek) + a 13-route wire probe. Resulting cohort
  documented above.
- **2026-09-02** — globalised: write target moved from
  `.tmp/docs/subagent-runs/` (project-local) to
  `~/.local/share/kilo/subagent-runs/` (global). Chezmoi-specific
  sensitive-file deny rules removed (they were project conventions,
  not global).

## See also

- **Permission block reference**:
  `~/.config/kilo/skills/subagent-fleet/references/permission-block.md`
- **Invocation pattern reference**:
  `~/.config/kilo/skills/subagent-fleet/references/invocation-pattern.md`
- **Model picks reference** (this project's cache; currently stale):
  `dot_config/kilo/exact_skills/subagent-fleet/references/model-picks.md`
- **Frontmatter reference** (Kilo schema for the YAML, project cache):
  `.agents/docs/cache/kilo-subagents/2026-08-15-agent-frontmatter-reference.md`
- **Permission precedence** (project cache):
  `.agents/docs/cache/kilo-subagents/2026-08-15-permissions-actions-precedence.md`
- **Reasoning variants per provider** (project cache):
  `.agents/docs/cache/kilo-subagents/2026-08-15-reasoning-variants-by-provider.md`
- **2026-09-01 route probe** (project cache, gitignored):
  `.agents/docs/cache/kilo-subagents/2026-09-01-shiki-route-probe.md`
- **OpenRouter API skill** (for live model re-verification):
  `~/.config/kilo/skills/openrouter-api/SKILL.md` (deployed from
  any project's `.agents/kilo/skills/openrouter-api/SKILL.md` or
  from the chezmoi source at
  `dot_config/kilo/exact_skills/` if chezmoi-managed)
