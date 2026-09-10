# Invocation Pattern (snapshot 2026-09-10)

> **Supersedes the 2026-08-25 snapshot.** Re-verify against
> `dot_config/kilo/exact_agent/README.md` when reachable.
>
> **2026-09-09 changes:**
> - Added opt-in 2-verifier mode (shiki + reki).
> - Added two-stage disagreement-resolution rule for verifier pair.
>
> **2026-09-10 changes:**
> - Cohort cap harmonised to `steps: 30, maxTokens: 6144` for all four
>   research subagents. Paired with the new continuation protocol in
>   the subagent bodies and the verifier refusal-on-partial rule in
>   shiki/reki. Plan:
>   `.tmp/docs/plans/2026-09-10-subagent-30step-6k-continuation.md`.

## Procedure

1. **Decide N** — number of research subagents to launch. The
   `subagent-fleet-trigger` rule's "Pick" table maps failure shapes to
   first/second picks:
   - One trigger (stuck or load-bearing) fires → default N=1 with the
     role matching the failure shape.
   - Both triggers fire, or stakes are high → N=2-4.
   - For comparison tasks with no rubric → N=1 with `fuyu`, plus `haru`
     when the leading candidate is load-bearing.

2. **Pick which roles** — if N<4, sub-sample from `{haru, natsu, aki,
   fuyu}` weighted toward the failure shape.

3. **Spawn in parallel** — same prompt for each. Pass `haru`'s output
   to `fuyu` when both run in the same fan-out.

4. **Continuation protocol (after every research subagent returns)** —
   parse the subagent's final message for the literal
   `continuation_request: <N>` line. If present:
   - Track per-spawn continuations (≤ 2; the 3rd escalates to user via
     the `question` tool).
   - On honour, re-spawn with `task_id=<prior_sessionID>` and a short
     continuation prompt: "Continue from where you left off. Read the
     partial YAML at `<path>`. Append the remaining findings to that
     file, switch `status: partial` → `complete`, increment `batch:`."
     The runtime preserves the subagent's full message history and
     tool outputs via `task_id` —
     `.agents/docs/cache/kilo-subagents/2026-09-10-subagent-continuation-primitive.md`
     has the runtime proof (parent-only guard at
     `packages/opencode/src/tool/task.ts:166-173`, permission re-merge
     at `tool/task.ts:213-220`). The subagent does **not** re-derive
     its prior tool calls — they are in the resumed session.

5. **Mandatory `shiki` when N≥2.** When N=1, spawn `shiki` only when
   the agent flags the single research subagent's output as load-bearing
   (cited in the final answer).

6. **Opt-in `reki` (2-verifier mode)** — spawn reki in parallel with
   shiki when **any** of:
   - N≥3 research subagents ran, **OR**
   - ≥3 `load_bearing: true` claims expected, **OR**
   - The answer lands in a public artifact (commit, PR, doc) or commits
     cost/scope.

7. **Refusal on partial input (both verifiers)** — if any research
   subagent YAML has `status: partial`, the verifier refuses with
   escalation on every claim from that YAML. The default is refuse;
   the user can opt-in per-spawn via a `verifier: accept_partial` flag.

8. **Reconciliation (2-verifier mode only)** — the main agent reads both
   verifier reports and applies the two-stage disagreement-resolution
   rule (see
   `kilo-subagents/2026-09-09-verifier-disagreement-resolution.md`):
   - Stage 1: main agent resolves with ≤ 3 tool calls (webfetch /
     websearch / firecrawl_scrape / tavily_extract) for shaping-artefact
     and evidence-asymmetry disagreements.
   - Stage 2: targeted 4-season fan-out (aki + fuyu interpretive roles
     only) for interpretation-asymmetry disagreements.

9. **Read only the verifier pair's `recommendation` +
   `open_questions_for_main_agent` blocks** (and optionally
   `claims_table` for audit). Decide whether to escalate to the user
   or accept.

## Hard rules

- **Never read raw research subagent output when N≥2.** The verifier
  pair (shiki, optionally + reki) is the only channel into the main
  agent's context. This keeps noise out of working memory.
- **Carve-out for continuation requests** — the parent parses the
  subagent's final message for the literal `continuation_request:`
  marker line. This is a control signal, not a finding, and is exempt
  from the noise-isolation rule. The continuation subagent does not
  trigger the noise-isolation rule for its partial file input (it
  *must* read the partial file to append findings).
- **Pass `haru`'s output to `fuyu`** when both spawn in the same
  fan-out (best-effort, not guaranteed by Kilo's parallel scheduler).
- **Cap on continuations per spawn (≤ 2).** The 3rd continuation
  request for the same role + question must escalate to the user.
- **Cap on verifier escalation.** When both verifiers return `deep:
  unclear` on a `load_bearing: true` claim, escalate to the user; do
  not loop another verifier call indefinitely.
- **In 2-verifier mode, do not read reki's YAML before reki's own
  two-pass verification completes** (reki-side anti-pattern). On
  shiki's side, do not read reki's YAML before completing shiki's
  own two-pass verification (shiki-side anti-pattern).

## Sequential chain (optional, not default)

For high-stakes questions:

1. Round 1: spawn `haru` alone. Use its output to refine the question.
2. Round 2: spawn `natsu`, `aki`, `fuyu` with the refined question.
   Run `shiki` (mandatory). Optionally run `reki` (2-verifier mode).

Cost: ~3 research calls + 1 verifier (single) or 2 verifiers (pair).
Higher quality on questions where the adversarial pass reveals the
original framing was wrong. Default off; on for security/correctness
stakes.

## Reports go to `~/.local/share/kilo/subagent-runs/`

Each subagent writes its report to
`~/.local/share/kilo/subagent-runs/YYYYMMDD_HHMMss-<role>[-<topic>].yaml`
(e.g. `20260826_113348-haru.yaml` or
`20260826_113348-natsu-sdd-synthesis.yaml`). The `YYYYMMDD_HHMMss`
segment is computed at write time with `date +%Y%m%d_%H%M%S` (local
clock; do not use `date +%s`). The optional `<topic>` slug is a short
disambiguator derived from the question — omit when the role alone is
clear. `shiki` and `reki` never take a topic slug. The directory is
**global** (under the parent kilo state dir, not the project tree)
and is gitignored at the parent kilo state level — reports from any
project land in the same place.

Continuation batches use a **single file per spawn**: batch 2+ reads
the partial file (same path as batch 1), appends findings via `edit`
against a known YAML anchor, switches `status: partial` → `complete`,
increments `batch:`. Do not split continuation batches across files —
the verifier pair expects one YAML per research role per spawn.

## Anti-patterns

- Skipping `shiki` because "it's only two subagents" — shiki is
  mandatory at N≥2 to keep noise out of the main agent's context.
  (`reki` is opt-in; do not skip shiki even if reki ran.)
- Reading raw research subagent output into the main agent's context.
- Launching all four research subagents by default for trivial questions
  — cost ceiling is bounded by the failure shape.
- Treating `shiki`'s recommendation as final when `deep: unclear` on a
  `load_bearing: true` claim — re-run, escalate, or (in 2-verifier
  mode) start stage 1 of the disagreement-resolution rule.
- **Continuation anti-patterns:**
  - Auto-honouring a 3rd continuation (cap is ≤ 2 per spawn).
  - Re-spawning without `task_id` — the subagent loses its full
    conversation and must re-derive every prior tool call. The runtime
    primitive is `task_id=<prior_sessionID>`; use it.
  - Splitting a continuation across multiple YAML files — the
    verifier expects one file per spawn.
  - Spawning the continuation subagent with the same question text
    instead of pointing it at the partial file.
- **2-verifier anti-patterns:**
  - Spawning reki for every question (default is single-shiki; the
    trigger is opt-in).
  - Reading reki's YAML in the main agent *before* reading shiki's
    YAML (or vice-versa) — the disagreement-detection signal
    benefits from reading both first and reconciling once.
  - Spawning reki on the same model as shiki (decorrelation requires
    family diversity).
  - Spawning reki in series (waiting for shiki, then spawning reki
    with shiki's output as context) — destroys the disagreement-
    detection signal via anchoring.
