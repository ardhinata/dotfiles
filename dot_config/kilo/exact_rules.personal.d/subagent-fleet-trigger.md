Use the subagent fleet (`haru` / `natsu` / `aki` / `fuyu` / `shiki`) for stuck-task recovery and for load-bearing verification. The fleet design, permission block, output contracts, and invocation procedure live in `.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md` (canonical plan). This rule owns the **when**.

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

`shiki` is the only channel back into the main agent when two or more research subagents ran (plan §5). The main agent reads shiki's `recommendation` and `open_questions_for_main_agent`, **never** the raw research artefacts.

## Process

1. Write the question, the leading candidate (if any), and the relevant context into the subagent prompt. Pass haru's output to `fuyu` when both ran in the same fan-out (plan §5).
2. Run research subagents in parallel.
3. Run `shiki` (verifier, `openrouter/minimax/minimax-m3`, `variant: high`) when two or more research subagents ran. Read only shiki's report.
4. Act on shiki's recommendation, or escalate to the user if shiki's `open_questions_for_main_agent` lists items that block the main agent.

## Anti-patterns

- Triggering on turn count alone — long, progressing work is not stuck.
- Skipping shiki because "it's only two subagents" — the plan makes shiki mandatory at N≥2 to keep noise out of the main agent's context.
- Reading raw research subagent output directly into the main agent's context — bypasses the verifier and pollutes working memory.
- Launching all four research subagents by default — the plan picks N uniformly at random (or by question shape); fan-out cost is bounded by the random draw.
- Using the fleet for tasks the agent can answer from already-loaded context or one tool call — the fleet is for stuck or load-bearing questions, not for free second opinions.
- Treating shiki's recommendation as final when its `deep:` column shows `unclear` on a `load_bearing: true` claim — re-run or escalate.

## Boundary

- **When to call the fleet** (this rule).
- **How the fleet is configured, what each role does, the permission block, output contracts, invocation patterns** → `.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md` (canonical plan).
- **Per-model sampling, variants, cost ceilings, provider picks** → the same plan §4.