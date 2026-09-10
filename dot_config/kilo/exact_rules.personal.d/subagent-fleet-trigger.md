Use the subagent fleet (`haru` / `natsu` / `aki` / `fuyu` / `shiki` / `reki`) for stuck-task recovery and for load-bearing verification. The fleet design, permission block, output contracts, and invocation procedure live in `~/.config/kilo/skills/subagent-fleet/` (skill, deployed from `dot_config/kilo/exact_skills/subagent-fleet/` in this chezmoi source). Load the skill on demand when about to spawn. This rule owns the **when** and the **continuation protocol**.

## When

Trigger the fleet when **either** of these holds:

- **Stuck-task recovery.** The current step is the third or later attempt at the same hypothesis, **or** the same approach has produced two or more failed tool calls in a row (errors, empty results, validation rejections). Turn count is not a trigger — a long task that is still progressing is not stuck.
- **Load-bearing decision.** The next action affects security, correctness of a public artifact, scope/cost commitment, or a claim the user will quote in the final answer.

If only one of the two holds, default to launching **one** research subagent whose role matches the failure shape (see Pick below). When **both** hold, or when stakes are high enough that a single viewpoint is not enough, launch **two or more research subagents** plus the `shiki` verifier (mandatory at N≥2). Optionally also spawn `reki` (second verifier) when the 2-verifier mode trigger fires — see Pick below.

## Pick

Pick the research subagent whose stance fits the failure shape. The
**failure-shape → role mapping table** lives in the skill at
`~/.config/kilo/skills/subagent-fleet/SKILL.md` §"Failure-shape → role
mapping" — load it on demand when choosing a role. This rule owns the
*when*; the skill owns the *which*.

The 2-verifier mode trigger (last row of the skill table) is opt-in.
`shiki` is mandatory at N≥2; `reki` is the opt-in second witness,
family-diverse from shiki, run in parallel with shiki over the same
research YAMLs.

`shiki` is the default channel back into the main agent when two or more research subagents ran. The main agent reads `shiki`'s `recommendation` and `open_questions_for_main_agent`, **never** the raw research artefacts. In 2-verifier mode (`reki` spawned), the main agent reads **both** verifier reports and applies the disagreement-resolution rule (see skill `references/invocation-pattern.md` §"Reconciliation"). **Carve-out for continuation requests** (see "Continuation protocol" below): the parent reads the subagent's final message text for the `continuation_request:` marker; this is a control signal, not a finding, and is exempt from the noise-isolation rule.

## Process

0. Load the task-prompt budget at
   `~/.config/kilo/skills/subagent-fleet/references/task-prompt-budget.md`
   before composing the per-spawn `task` prompt. (The budget was moved
   from this `exact_rules.personal.d/` directory into the skill on
   2026-09-10 — it is only useful at the spawn moment, not every turn.)
1. Write the question, the leading candidate (if any), and the relevant context into the subagent prompt. Pass haru's output to `fuyu` when both ran in the same fan-out (see skill `references/invocation-pattern.md` §"Procedure").
2. Run research subagents in parallel.
3. Run `shiki` (verifier — see `references/model-picks.md` for the
   current model + sampling) when two or more research subagents ran.
   Read only shiki's report. Optionally also run `reki` in parallel
   with shiki when the 2-verifier mode trigger fires (Pick table last
   row). Read only the verifier pair's reports.
4. **Continuation protocol.** After every research subagent returns:
   - Parse the subagent's final message for the literal `continuation_request: <N>` line. If absent, no continuation is requested — proceed to step 5.
   - If present, check whether the parent has already honoured ≤ 2 continuations for this spawn (count per research role, per task). The 3rd request for the same role + question must **escalate to the user** via the `question` tool — do not auto-honour a 3rd continuation. Show: "Research subagent <name> requested its 3rd continuation for `<question>` (file <path>); previous continuations: <N>. Continue, accept partial, or escalate?" — let the user pick.
   - When honoured, **re-spawn the same subagent** with `task_id=<prior_sessionID>` and a short continuation prompt: "Continue from where you left off. Read the partial YAML at `<path>`. Append the remaining findings to that file, switch `status: partial` → `complete`, increment `batch:`." The runtime preserves the subagent's full message history, tool outputs, and model state across the resume.
   - When a continuation returns `status: complete`, count it against the per-spawn cap and proceed to step 5. When it returns `status: partial` again, treat it as a new continuation request (re-apply this step).
5. Act on shiki's recommendation, or escalate to the user if shiki's `open_questions_for_main_agent` lists items that block the main agent. In 2-verifier mode, reconcile shiki's and reki's verdicts per the disagreement-resolution rule (skill `references/invocation-pattern.md` §"Reconciliation") before acting. If shiki's report flags `needs-escalation` on a research subagent's `status: partial`, the parent's continuation protocol has not completed — route to the user via the `question` tool.

## Anti-patterns

- Triggering on turn count alone — long, progressing work is not stuck.
- Skipping shiki because "it's only two subagents" — shiki is mandatory at N≥2 to keep noise out of the main agent's context. `reki` is opt-in; do not skip shiki even when reki ran. `reki` alone is not a verifier pair.
- Spawning `reki` on the same model as `shiki` — decorrelation requires family diversity. See skill `references/model-picks.md` for the cohort.
- Reading raw research subagent output directly into the main agent's context — bypasses the verifier and pollutes working memory. (The carve-out for continuation requests is narrow: only the literal `continuation_request:` marker line, not the full message.)
- Launching all four research subagents by default — fan-out cost is bounded by the failure shape (Pick table); don't over-spawn.
- Using the fleet for tasks the agent can answer from already-loaded context or one tool call — the fleet is for stuck or load-bearing questions, not for free second opinions.
- Treating shiki's recommendation as final when its `deep:` column shows `unclear` on a `load_bearing: true` claim — re-run, escalate, or (in 2-verifier mode) start stage 1 of the disagreement-resolution rule.
- **Continuation anti-patterns:**
  - Honoring a 3rd continuation without escalating to the user — the cap is 2 per spawn.
  - Re-deriving the prior batch's tool calls from a `past_steps:` array — your prior tool-call history is already in the conversation via `task_id` continuation; reconstructing it is duplicate work.
  - Reading the full partial YAML into the main agent's context when only the `continuation_request:` marker is needed.
  - Spawning the continuation subagent with the same question text — the continuation prompt must point at the partial file, not restate the question.

## Boundary

- **When to call the fleet + continuation protocol** (this rule).
- **How the fleet is configured, what each role does, the permission block, output contracts, invocation patterns** → `~/.config/kilo/skills/subagent-fleet/` (skill). Load `references/invocation-pattern.md` before composing any spawn.
- **Per-model sampling, variants, cost ceilings, provider picks** → skill `references/model-picks.md`.
- **2-verifier disagreement resolution** → skill `references/invocation-pattern.md` §"Reconciliation".
- **Per-spawn task-prompt budget (≤ 15 lines, no body-duplication, no path/filename override)** → `~/.config/kilo/skills/subagent-fleet/references/task-prompt-budget.md` (load before any spawn).