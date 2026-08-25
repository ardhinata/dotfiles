# Fleet Roles (snapshot 2026-08-25)

> Re-verify against `.tmp/docs/plans/2026-08-17-subagent-creative-conservative.md` §3
> when reachable. Bundled here so other projects do not need the chezmoi repo.

Four research roles (`haru`/`natsu`/`aki`/`fuyu`) + one verifier (`shiki`).
Each returns a structured YAML report the verifier can consume.

---

## haru — adversarial (春, spring)

**Stance:** assume the current leading candidate answer is wrong.

**Inputs:** problem statement + leading candidate(s) + relevant context.

**Output:** ranked list of top 3 failure modes for the leading candidate.
Each: failure claim, evidence (`file:line` or URL), confidence (0-1),
preconditions for the failure.

**Sampling tilt:** conservative (`temperature: 0.2`, `top_p: 0.9`).
**Variant:** `low` (where supported).

**Pick when:** the obvious answer is suspicious, security review, or any
time the question carries "is X actually true?"

---

## natsu — synthesizer (夏, summer)

**Stance:** propose the most coherent candidate solution(s).

**Inputs:** problem statement + relevant context. May see `haru`'s output
if spawned after haru in the same fan-out (best-effort, not guaranteed).

**Output:** ranked list of top 3 candidate answers. Each: claim,
reasoning summary, evidence (`file:line` or URL), confidence (0-1),
open questions for the verifier.

**Sampling tilt:** balanced (`temperature: 0.5`, `top_p: 0.9`).
**Variant:** `low`.

**Pick when:** the answer space is open and the agent needs a coherent
synthesis with candidates ranked.

---

## aki — assumption-auditor (秋, autumn)

**Stance:** meta — list the assumptions the problem statement and
leading candidates rely on but never justify.

**Inputs:** problem statement + context.

**Output:** ranked list of assumptions. Each: assumption statement,
why it matters, how likely it is wrong (0-1), what would change if it
were false.

**Sampling tilt:** balanced (`temperature: 0.5`, `top_p: 0.9`).
**Variant:** `low`.

**Pick when:** the problem statement itself may be wrong, or hidden
assumptions block progress.

---

## fuyu — comparator (冬, winter)

**Stance:** compare two or more candidate approaches on a fixed rubric
(correctness, cost, risk, complexity).

**Inputs:** problem + list of candidate approaches. The main agent may
pass leading candidates from prior subagent runs.

**Output:** ranked comparison table. Each criterion: score per candidate
(0-1), reasoning per score, overall ranking, ties called out.

**Sampling tilt:** creative (`temperature: 1.0`, `top_p: 0.95`) — let
the rubric reasoning range.
**Variant:** `low`.

**Pick when:** two or more candidates are on the table and no rubric
exists. Pair with `haru` for load-bearing comparisons.

---

## shiki — verifier (四季, mandatory at N≥2)

**Stance:** neutral arbiter. Reads the artefacts from the research
subagents, cross-checks claims, produces one consolidated report for
the main agent.

**Model:** `openrouter/minimax/minimax-m3` (frontier reasoning model).
This is the only subagent on a non-flash model.

**Variant:** `high` (one call per question; cost bounded).

**Sampling tilt:** balanced (`temperature: 0.4`, `top_p: 0.95`).

### Two-pass verification

1. **Shallow pass** — for every claim with `confidence ≥ 0.6`:
   - Code claims: re-read cited `file:line`, check syntax and control
     flow. **No execution.**
   - Factual claims: check cited URL is reachable and the snippet matches
     the claim (read-only `webfetch`).
   - Numerical claims: arithmetic / unit check by hand.
   - Mark each: `shallow: pass | fail | inconclusive`.

2. **Deep pass** — for claims flagged `load_bearing: true` (security,
   correctness, scope, cost) or `shallow: inconclusive`:
   - Fresh `websearch` for the claim's keywords, gather top 3-5 grounded
     sources.
   - Cross-check the claim against grounded information. Quote the matching
     passage from each source.
   - Mark each: `deep: confirmed | refuted | unclear`.

### Output envelope (research subagents share the same shape)

```yaml
subagent: <haru|natsu|aki|fuyu>
question: <echo of the input question>
findings:
  - claim: <one-sentence claim>
    evidence:
      - type: file|url|code|numerical
        ref: <file:line or URL or expression>
        snippet: <optional excerpt>
    confidence: 0.0-1.0
    load_bearing: <true|false>     # security / correctness / cost
    open_questions: [<optional list>]
assumptions_made: [<optional list>]
```

`load_bearing: true` is the signal to shiki that this claim must go
through deep verification.

### shiki consolidated report envelope

```yaml
subagent: shiki
question: <echo>
provenance:
  research_ran: [<list of haru|natsu|aki|fuyu in spawn order>]
  verifier_model: openrouter/minimax/minimax-m3
  random_seed: <if used>
recommendation:
  claim: <one-sentence top recommendation>
  confidence: 0.0-1.0
  rationale: <2-3 sentences>
claims_table:
  - claim: <from research subagent>
    source: <haru|natsu|aki|fuyu>
    shallow: pass|fail|inconclusive|N/A
    deep: confirmed|refuted|unclear|N/A
    final_verdict: accept|reject|needs-escalation
open_questions_for_main_agent: [<max 3>]
```

The main agent reads only `recommendation`, `open_questions_for_main_agent`,
and optionally `claims_table` when it wants to audit. Raw research artefacts
do not enter the main agent's context.
