---
name: synthetic-problem-inputs
description: >
  Author, version, and dispatch synthetic inputs for fleet speed/cost benchmarks
  of the kilo subagent fleet (haru/natsu/aki/fuyu/shiki). Use when running the
  fleet speed-benchmark plan (`.tmp/docs/plans/2026-08-30-inference-speed-benchmark.md`),
  when a model revaluation needs comparable probes across the 5 roles, or when
  any future fleet probe wants a templated, role-shaped question that exercises
  the YAML envelope without engaging real reasoning. Inputs are paraphrased
  from common software-engineering decision scenarios so the prompt is non-
  trivial but the model produces the envelope from its own training, not from
  a live investigation. Key terms: synthetic input, fleet benchmark, haru
  failure mode, natsu synthesis, aki assumption, fuyu comparison, shiki
  verifier, role-shaped envelope, /generation lookup, latency p50/p95,
  cost ceiling.
---

# Synthetic Problem Inputs (Fleet Benchmark)

Author and dispatch 5-distinct synthetic inputs per research subagent role
so a fleet speed / cost / latency probe is reproducible across revaluation
runs. Inputs exercise each role's YAML envelope without engaging real
reasoning, keeping the model side of the latency budget comparable.

## When to load

- Running the fleet speed-benchmark plan
  (`.tmp/docs/plans/2026-08-30-inference-speed-benchmark.md`).
- Re-running a comparable probe after a model revaluation
  (`.agents/kilo/command/subagent-fleet-reevaluate-models.md`).
- Any future probe that needs role-shaped inputs the model can answer
  from training alone — no live web research, no real codebase.
- NOT for: production subagent runs (use the role bodies directly);
  empirical-pass probes that intentionally hit the cap (use
  `.agents/kilo/command/subagent-fleet-empirical-pass.md`).

## What this skill owns

- The 5 input templates per role (one of the four role families — see
  `references/role-templates.md`).
- The harness contract: how to inline the question + envelope reminder
  in a `task`-tool dispatch and how to extract the `gen-...` id from the
  subagent's response for the post-call `/generation` lookup.
- The provenance record: where the inputs were paraphrased from, so a
  future revaluation can refresh vocabulary without re-deriving topics.

## What this skill does NOT own

- Model picks (lives in `dot_config/kilo/exact_agent/*.md` + the
  revaluation workflow).
- Cap-plan policy (`steps` / `maxTokens` floors) — the cap plan is
  the gate that lets the benchmark run bounded; if no cap is in
  place, stop and surface the missing cap (benchmark plan anti-pattern).
- `/generation` endpoint shape (lives in the `openrouter-api` skill).
- Per-role output envelope shape (lives in each role body — read the
  relevant agent file before authoring the reminder suffix).

## Quick start

1. Read `references/role-templates.md` for the 4×5 = 20 input seeds
   (v2, 2026-08-30T05:01Z; replaces v1 drafted 2026-08-30T04:33Z).
2. For a revaluation, the inputs are **stable** — do not regenerate
   unless the role's responsibility has shifted or the vocabulary
   becomes stale. If you must regenerate, write a new "Generated:
   YYYY-MM-DD" section to
   `.tmp/docs/plans/YYYY-MM-DD-fleet-speed-benchmark-inputs.md` and
   reference both old and new in the report's `Uncertainty` section.
3. Read `references/harness-contract.md` for the dispatch shape,
   maxTokens policy, and the `/generation` lookup sequence.
4. After the run, append the latency / cost / finish_reason table to
   the new inputs plan and commit it via `kilo-shared save`.

## Anti-patterns

- **Re-authoring the 20 inputs from scratch each run** — that breaks
  cross-run comparability. The seeds are deliberately stable; refresh
  only when the role's responsibility shifts.
- **Pulling real-world problems from the user's own repo** — that
  crosses the "model answers from training" line and engages real
  reasoning, which the benchmark explicitly tries to avoid (it
  inflates latency variance with research overhead, not model
  inference overhead).
- **Omitting the output-shape reminder in the dispatch** — without
  the reminder, the model may emit prose instead of YAML, which
  breaks the post-call audit and the per-call CSV row.
- **Skipping the `/generation` lookup** — the latency in
  `/generation.latency` is the model-side number, distinct from
  end-to-end subagent wall-clock. Both are needed for the
  latency table.
- **Reusing one input across roles** — the prompts are
  role-shaped; one input cannot exercise all four envelopes.

## Boundary

- **Authoring synthetic inputs + harness contract** (this skill).
- **Why measure + the per-call schema + the cap-plan linkage** →
  `.tmp/docs/plans/2026-08-30-inference-speed-benchmark.md`.
- **Per-call OpenRouter endpoint + auth** → `openrouter-api` skill
  (load when querying `/generation`).
- **Per-role output envelope** → read the relevant
  `dot_config/kilo/exact_agent/<role>.md` file directly.
- **Run the benchmark end-to-end** →
  `.agents/kilo/command/subagent-fleet-reevaluate-models.md` (the
  benchmark is one optional Step in that workflow).
