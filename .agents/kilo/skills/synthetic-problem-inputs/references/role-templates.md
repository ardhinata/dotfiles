# Role Templates (Synthetic Inputs, v2 — 2026-08-30T05:01Z)

The 4×5 = 20 input seeds, paraphrased from 2026 software-engineering
decision scenarios (distributed-monolith anti-pattern, REST/GraphQL/gRPC
decision framework, monolith→microservices migration strategy, vibe-coding
pushback on requirements ambiguity). Stable across revaluation runs;
only refresh when the role's responsibility shifts or the vocabulary
becomes stale.

> v1 (2026-08-30T04:33Z) is superseded by v2 (this file). v1 is kept at
> `.tmp/docs/plans/2026-08-30-fleet-speed-benchmark-inputs.md` §"Comparison
> vs v1" for the diff.

## Haru (adversarial — failure modes of a candidate)

For each, "candidate" is a 2026 distributed-systems / API-architecture
position; haru is asked to assume it's wrong and surface the top 3
failure modes.

| # | Question template |
|---|---|
| 1 | The leading candidate is: "Adopt a microservices-first architecture from day one to give every team independent deployability, even at <10 engineers." Produce 3 ranked failure modes for this candidate. |
| 2 | The leading candidate is: "Cover the codebase with end-to-end integration tests instead of unit tests, because they give the highest confidence per test written." Produce 3 ranked failure modes for this candidate. |
| 3 | The leading candidate is: "Adopt eventual consistency as the default for every cross-service write, on the grounds that it maximizes availability and simplifies retries." Produce 3 ranked failure modes for this candidate. |
| 4 | The leading candidate is: "Use a single shared database across all future services, with one schema per service, to defer the cost of database decomposition." Produce 3 ranked failure modes for this candidate. |
| 5 | The leading candidate is: "Adopt gRPC for every internal call AND every public API, because it is 4-10× faster than REST/JSON." Produce 3 ranked failure modes for this candidate. |

## Natsu (synthesizer — coherent candidate solutions)

Each natsu problem maps to a 2026 forward-path dilemma: migration
strategy, observability foundation, consistency model, or operational
discipline. natsu picks the top 3 candidates.

| # | Question template |
|---|---|
| 1 | Synthesize 3 ranked candidate solutions for: "We have committed to breaking apart the monolith into microservices over 18 months. Pick a migration strategy that keeps feature delivery alive." |
| 2 | Synthesize 3 ranked candidate solutions for: "We are adding 5 new microservices this quarter and have no observability stack. Pick a forward path." |
| 3 | Synthesize 3 ranked candidate solutions for: "A regulated workflow requires strict consistency across two services that must stay independently deployable. Pick a forward path." |
| 4 | Synthesize 3 ranked candidate solutions for: "Our public API serves both a mobile app and a partner integration with very different data needs. Pick a forward path." |
| 5 | Synthesize 3 ranked candidate solutions for: "Background job processing is using a single worker process, and jobs are lost on crash. Pick a forward path." |

## Aki (assumption-auditor — hidden assumptions)

Each aki problem is a 2026-flavored "this is a sensible-sounding
requirement" that conceals 3 hidden assumptions.

| # | Question template |
|---|---|
| 1 | The problem statement is: "Pick a database for a new event-sourcing system that will scale to 1M events/day." List 3 hidden assumptions. |
| 2 | The problem statement is: "Use vibe coding (LLM-assisted generation) for the next sprint to ship features faster." List 3 hidden assumptions. |
| 3 | The problem statement is: "Refactor a legacy monolith into microservices to give teams autonomy and independent deploys." List 3 hidden assumptions. |
| 4 | The problem statement is: "Add a GraphQL gateway in front of every existing REST service to give clients a unified data shape." List 3 hidden assumptions. |
| 5 | The problem statement is: "Move from Jenkins to GitHub Actions to reduce maintenance burden and align with the rest of the org." List 3 hidden assumptions. |

## Fuyu (comparator — two candidates on a fixed rubric)

For each, rubric is `{correctness, cost, risk, complexity}`. The two
candidates are A and B as defined per row.

| # | Candidate A | Candidate B |
|---|---|---|
| 1 | "Strangler-fig migration: route traffic through a façade that gradually replaces the monolith" | "Branch-by-abstraction migration: introduce an abstraction layer in the monolith and replace implementations one by one" |
| 2 | "Database-per-service with eventual consistency via outbox + event bus" | "Shared database with schema-per-service boundaries and synchronous 2PC for cross-service writes" |
| 3 | "Schema-first REST with OpenAPI 3.1, codegen, and strict request/response validation" | "Code-first REST with hand-written controllers and Postman collections for QA" |
| 4 | "Public API on REST/JSON, internal service-to-service on gRPC with Protobuf contracts" | "Public API on REST/JSON, internal service-to-service on REST/JSON with a service mesh" |
| 5 | "AI-assisted observability platform with anomaly prediction and auto-remediation suggestions" | "Traditional centralized logging + dashboards + on-call runbooks, manually tuned" |

## Shiki

**Skipped** (user decision 2026-08-30T04:38Z; reaffirmed
2026-08-30T05:01Z): shiki is pinned at `openrouter/minimax/minimax-m3`,
performance is already known. Re-add shiki inputs here only if a
reevaluation moves shiki off the current model.

## Output envelope reminders (appended by the harness)

The harness appends one of these per role. The model is given the role
body via kilo's `subagent_type: <role>` dispatch, so it already knows
the envelope; the reminder is for the model's final-answer sampler.

- **haru**: `Output must follow the haru YAML envelope (3 findings, each with claim/evidence/confidence/load_bearing/open_questions).`
- **natsu**: `Output must follow the natsu YAML envelope (3 findings, each with claim/reasoning_summary/evidence/confidence/load_bearing/open_questions).`
- **aki**: `Output must follow the aki YAML envelope (3 findings, each with claim/why_it_matters/evidence/likely_wrong/what_changes_if_false/load_bearing/open_questions).`
- **fuyu**: `Output must follow the fuyu comparison-table YAML envelope (4 criteria, 2 candidates A and B, ranked with ties surfaced).`

## Provenance (2026-08-30T05:01Z)

Inputs are paraphrased from these general-audience references (web
searches performed for v2 vocabulary calibration; no direct quotes
pulled into the inputs):

**Distributed systems & microservices anti-patterns:**

- Distributed Monolith: The Anti-Pattern Every C# Developer Should Recognize (DevLeader, 2026-07-12).
- Architectural Anti-Patterns in Student-Developed Microservice Architectures (arXiv 2602.07147v2, 2026-02-10).
- Scalable Microservices Architecture: Design, Pitfalls, & Patterns (Developers.dev, 2026-08-12).
- Distributed Systems Patterns and Anti-Patterns (World Journal of Advanced Engineering Technology and Sciences, 2025-01-09).

**Monolith→microservices migration strategy:**

- Monolithic to Microservices Migration: Complete Strategy Guide (DrCodes, 2026-08-25).
- From Monolith To Microservices: A Step-By-Step Migration Strategy (iTechOps, 2026-07-07).
- Monolith to Microservices: Migration Strategies (StackPractices, 2026-06-12).
- Monolith to Microservices Migration Guide (EmizenTech, 2026-01-13).
- Monolith to Microservices: The 2026 Enterprise Migration Guide (AdaptNXT, 2026-08-15).

**REST / GraphQL / gRPC decision framework (2026):**

- REST API vs GraphQL vs gRPC in 2026: The Complete Decision Guide (Bioquro, 2026-05-07).
- GraphQL vs. REST vs. gRPC: The 2026 API Architecture Decision (JavaCodeGeeks, 2026-02-09).
- 15 API Trends for 2026: REST, GraphQL, gRPC Changes (Alphonso Labs, 2026-06-26).
- REST vs GraphQL vs gRPC APIs 2026 (APIScout, 2026-03-29).
- gRPC vs REST vs GraphQL APIs 2026 (APIScout, 2026-04-13).
- GraphQL vs REST vs gRPC in 2026: Choosing the Right API for Your Use Case (DevStarSJ, 2026-03-17).

**Requirements engineering / vibe coding pushback:**

- Incomplete and Hidden Requirements (EmergentMind, 2026-04-05).
- Software Requirements Gathering: A Guide for SMBs (2026) (Gaazzeebo, 2026-06-12).
- Requirements Gathering Methods: A Strategic Guide for 2026 (Business Model Analyst, 2026-05-27).
- Software Requirements Gathering 2026 - AI Tools, Techniques (Eidosoft, 2026-02-08).
- How to Avoid Ambiguous Requirements in Software Engineering (Jama Software, 2026-07-02).

## v1 → v2 diff (for audit)

| Theme | v1 (2026-08-30T04:33Z) | v2 (2026-08-30T05:01Z) |
|---|---|---|
| haru | Generic microservices/E2E/eventual/NoSQL/K8s positions | Distributed monolith, E2E-over-unit, eventual consistency, shared DB, gRPC-everywhere |
| natsu | Generic DB-throughput/API-timeout/CI-feedback/auth-SPOF/worker | Migration strategy, observability foundation, regulated consistency, multi-client API, worker resilience |
| aki | Generic event-sourcing/OpenTelemetry/monolith-refactor/caching/Jenkins→GHA | Event-sourcing DB, vibe coding, monolith refactor, GraphQL gateway, Jenkins→GHA |
| fuyu | Generic single-tenant DB, polling-vs-SSE, sidecar mTLS, RDS-vs-self-host, blue/green-vs-canary | Strangler-fig-vs-branch-by-abstraction, DB-per-service-vs-shared-DB, schema-first-vs-code-first REST, gRPC-internal+REST-external-vs-REST-everywhere, AI-observability-vs-traditional |

**Stable across v1 and v2:** role shape (haru/natsu/aki/fuyu), rubric
for fuyu, envelope reminders, harness contract. **Refreshed in v2:**
the candidate/problem statements, to keep the model's training-pattern
recall honest across revaluation runs.