Use the subagent fleet (`haru` / `natsu` / `aki` / `fuyu` / `shiki` / `reki`) for stuck-task recovery and for load-bearing verification. The fleet design, permission block, output contracts, and invocation procedure live in `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` (canonical plan). This rule owns the **when** and the **continuation protocol**.

## When

Trigger the fleet when **either** of these holds:

- **Stuck-task recovery.** The current step is the third or later attempt at the same hypothesis, **or** the same approach has produced two or more failed tool calls in a row (errors, empty results, validation rejections). Turn count is not a trigger — a long task that is still progressing is not stuck.
- **Load-bearing decision.** The next action affects security, correctness of a public artifact, scope/cost commitment, or a claim the user will quote in the final answer.

If only one of the two holds, default to launching **one** research subagent whose role matches the failure shape (see Pick below). When **both** hold, or when stakes are high enough that a single viewpoint is not enough, launch **two or more research subagents** plus the **shiki** verifier (the plan §5 mandatory-verifier rule).

## Pick

Pick the research subagent whose stance fits the failure shape:

| Failure shape | First pick | Optional second pick |
|---|---|---|
| Leading answer may be wrong | `haru` (adversarial) | `shiki` verifier on haru's output |
| Need a coherent answer / candidate synthesis | `natsu` (synthesizer) | `aki` (assumption-auditor) |
| Multiple candidates on the table, no rubric | `fuyu` (comparator) | `shiki` verifier |
| Problem statement itself may be wrong | `aki` (assumption-auditor) | `natsu` or `fuyu` |
| A single load-bearing claim needs verification | `haru` (find failure modes) + `shiki` verifier | — |

`shiki` is the default channel back into the main agent when two or more research subagents ran (plan §5). The main agent reads shiki's `recommendation` and `open_questions_for_main_agent`, **never** the raw research artefacts. **Carve-out for continuation requests** (see "Continuation protocol" below): the parent reads the subagent's final message text for the `continuation_request:` marker; this is a control signal, not a finding, and is exempt from the noise-isolation rule.

## Process

0. Load the budget enforcer (`subagent-fleet-task-prompt-budget.md`) before composing the per-spawn `task` prompt.
1. Write the question, the leading candidate (if any), and the relevant context into the subagent prompt. Pass haru's output to `fuyu` when both ran in the same fan-out (plan §5).
2. Run research subagents in parallel.
3. Run `shiki` (verifier — see `references/model-picks.md` for the
   current model + sampling) when two or more research subagents ran.
   Read only shiki's report.
4. **Continuation protocol.** After every research subagent returns:
   - Parse the subagent's final message for the literal `continuation_request: <N>` line. If absent, no continuation is requested — proceed to step 5.
   - If present, check whether the parent has already honoured ≤ 2 continuations for this spawn (count per research role, per task). The 3rd request for the same role + question must **escalate to the user** via the `question` tool — do not auto-honour a 3rd continuation. Show: "Research subagent <name> requested its 3rd continuation for `<question>` (file <path>); previous continuations: <N>. Continue, accept partial, or escalate?" — let the user pick.
   - When honoured, **re-spawn the same subagent** with `task_id=<prior_sessionID>` and a short continuation prompt: "Continue from where you left off. Read the partial YAML at `<path>`. Append the remaining findings to that file, switch `status: partial` → `complete`, increment `batch:`." The runtime preserves the subagent's full message history, tool outputs, and model state across the resume — see `.agents/docs/cache/kilo-subagents/2026-09-10-subagent-continuation-primitive.md` for the runtime proof (parent-only guard at `tool/task.ts:166-173`, permission re-merge at `tool/task.ts:213-220`).
   - When a continuation returns `status: complete`, count it against the per-spawn cap and proceed to step 5. When it returns `status: partial` again, treat it as a new continuation request (re-apply this step).
5. Act on shiki's recommendation, or escalate to the user if shiki's `open_questions_for_main_agent` lists items that block the main agent. If shiki's report flags `needs-escalation` on a research subagent's `status: partial`, the parent's continuation protocol has not completed — route to the user via the `question` tool.

## Anti-patterns

- Triggering on turn count alone — long, progressing work is not stuck.
- Skipping shiki because "it's only two subagents" — the plan makes shiki mandatory at N≥2 to keep noise out of the main agent's context.
- Reading raw research subagent output directly into the main agent's context — bypasses the verifier and pollutes working memory. (The carve-out for continuation requests is narrow: only the literal `continuation_request:` marker line, not the full message.)
- Launching all four research subagents by default — the plan picks N uniformly at random (or by question shape); fan-out cost is bounded by the random draw.
- Using the fleet for tasks the agent can answer from already-loaded context or one tool call — the fleet is for stuck or load-bearing questions, not for free second opinions.
- Treating shiki's recommendation as final when its `deep:` column shows `unclear` on a `load_bearing: true` claim — re-run or escalate.
- **Continuation anti-patterns:**
  - Honoring a 3rd continuation without escalating to the user — the cap is 2 per spawn.
  - Re-deriving the prior batch's tool calls from a `past_steps:` array — your prior tool-call history is already in the conversation via `task_id` continuation; reconstructing it is duplicate work.
  - Reading the full partial YAML into the main agent's context when only the `continuation_request:` marker is needed.
  - Spawning the continuation subagent with the same question text — the continuation prompt must point at the partial file, not restate the question.

## Boundary

- **When to call the fleet + continuation protocol** (this rule).
- **How the fleet is configured, what each role does, the permission block, output contracts, invocation patterns** → `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` (canonical plan).
- **Per-model sampling, variants, cost ceilings, provider picks** → the same plan §4.
- **Per-spawn task-prompt budget (≤ 15 lines, no body-duplication, no path/filename override)** → `dot_config/kilo/exact_rules.personal.d/subagent-fleet-task-prompt-budget.md`.