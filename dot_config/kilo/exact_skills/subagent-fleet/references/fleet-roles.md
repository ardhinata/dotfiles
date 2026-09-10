# Fleet Roles

Four research roles (`haru`/`natsu`/`aki`/`fuyu`) + two verifiers
(`shiki` mandatory, `reki` opt-in 2-verifier mode). Each returns a
structured YAML report the verifier pair can consume.

For current model assignments, sampling tilts, route pins, and cost
ceilings, see `references/model-picks.md`. For the shared permission
block + tool-deny list + global write target, see
`references/permission-block.md`.

---

## haru — adversarial (春, spring)

**Stance:** assume the current leading candidate answer is wrong.

**Inputs:** problem statement + leading candidate(s) + relevant context.

**Output:** ranked list of top 3 failure modes for the leading candidate.
Each: failure claim, evidence (`file:line` or URL), confidence (0-1),
preconditions for the failure.

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

**Pick when:** two or more candidates are on the table and no rubric
exists. Pair with `haru` for load-bearing comparisons.

---

## shiki — verifier 1 (四季, mandatory at N≥2)

**Stance:** neutral arbiter. Reads the artefacts from the research
subagents, cross-checks claims, produces one consolidated report for
the main agent.

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
status: complete | partial              # partial = continuation batch; main agent resumes on the same context via task_id
batch: <integer, 1+>                    # batch index; 1 for first batch
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
continuation_request:                  # only present on status: partial
  remaining_findings: <integer>
  next_actions: [<short list>]
```

`load_bearing: true` is the signal to shiki (and reki) that this claim
must go through deep verification. `status: partial` is the signal to
shiki/reki that the report is incomplete and the verifier must refuse
with escalation (see "Refusal on partial input" in each verifier body).
The continuation subagent is the same session as the prior batch —
the runtime preserves message history and tool outputs via `task_id`
(`.agents/docs/cache/kilo-subagents/2026-09-10-subagent-continuation-primitive.md`),
so the subagent continues from where it left off without re-deriving
prior tool calls.

### Verifier behaviour on partial research input

Both `shiki` and `reki` apply the same rule: if **any** research
subagent YAML has `status: partial`, the verifier refuses with
escalation on every claim from that YAML. The default is refuse —
the user can opt-in per-spawn via a `verifier: accept_partial` flag
in the parent's task prompt to switch to partial-recommendation mode
with explicit uncertainty markers. The continuation path is owned by
the main agent (it tracks per-spawn continuation counts and re-spawns
the research subagent with `task_id=<prior_sessionID>`).

### shiki consolidated report envelope (single-verifier mode)

```yaml
subagent: shiki
question: <echo>
provenance:
  research_ran: [<list of haru|natsu|aki|fuyu in spawn order>]
  verifier_model: <populated by KiloTask.resolveModel>
  variant: <populated by KiloTask.resolveModel>
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

### shiki consolidated report envelope (2-verifier mode)

```yaml
subagent: shiki
question: <echo>
provenance:
  research_ran: [<list of haru|natsu|aki|fuyu in spawn order>]
  verifier_model: <populated by KiloTask.resolveModel>
  variant: <populated by KiloTask.resolveModel>
  random_seed: <if used>
  verifier_pair: [shiki, reki]
recommendation:
  claim: <one-sentence top recommendation>
  confidence: 0.0-1.0
  rationale: <2-3 sentences>
  disagreements_with_reki: <int — count of load_bearing claims where shiki.verdict ≠ reki.verdict>
claims_table:
  - claim: <from research subagent>
    source: <haru|natsu|aki|fuyu>
    confidence: <from research subagent>
    shallow: pass|fail|inconclusive|N/A
    deep: confirmed|refuted|unclear|N/A
    shiki_verdict: accept|reject|needs-escalation
    reki_verdict: <accept|reject|needs-escalation|N/A>
    shiki_reki_match: true|false|N/A
    final_verdict: accept|reject|needs-escalation       # per-claim resolution by shiki's reading
open_questions_for_main_agent: [<max 3>]
```

In 2-verifier mode, the main agent also reads reki's report for the
disagreement-resolution merge step (see
`kilo-subagents/2026-09-09-verifier-disagreement-resolution.md`).

---

## reki — verifier 2 (暦, opt-in 2-verifier mode)

**Stance:** second witness. Independent verdict over the **same** research
YAMLs, family-diverse from shiki. If you agree with shiki on every claim,
you are not adding value — the disagreement-detection signal is the
purpose.

**Stance rules** (see `reki.md` for full body):

1. **Independent verdict first** — complete your own two-pass
   verification before reading shiki's report.
2. **Sample aggressively** — use the creative sampling tilt to consider
   alternative framings on `shallow: inconclusive` claims.
3. **Disagree loudly, but justified** — surface disagreements clearly;
   don't downweight family-diverse evidence.
4. **Cross-family evidence is your edge** — when your model family
   identifies a failure mode that a same-family verifier would typically
   miss, that's the signal the main agent is paying you for.
5. **Don't blindly agree** — if you and shiki agree on every claim,
   re-check at least one claim by reading the original source directly.

**Trigger** (main agent decides):

- N≥3 research subagents ran, **OR**
- ≥3 `load_bearing: true` claims expected, **OR**
- The answer lands in a public artifact (commit, PR, doc) or commits
  cost/scope.

**Pick when:** the verifier pair adds value (high-stakes decisions,
public artifacts) and the user has opted into the 2-verifier cost.

### reki report envelope

Same as shiki's 2-verifier mode envelope, with `subagent: reki` and
`disagreements_with_shiki` in `recommendation`. See
`~/.config/kilo/agent/reki.md` for the canonical body.