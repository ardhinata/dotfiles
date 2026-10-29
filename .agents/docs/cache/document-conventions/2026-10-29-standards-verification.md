# The document-conventions skill: which rules are standard, and which citations were wrong

Captured 2026-10-29 while verifying every reference and template in
`dot_agents/skills/document-conventions` against its cited source.

## Finding

The skill is broadly accurate but carried **11 wrong or unsupported
citations**. The verdicts and the full defect list are now in the skill
itself, at `references/standards-map.md`. This entry records only the facts
that will go stale fastest, plus what the research concluded about template
coverage.

## The wrong citations, and what replaced them

| Was cited | Reality | Replacement |
|---|---|---|
| OWASP Secrets Management Cheat Sheet | covers secret storage and rotation, not documentation content | GitLab style guide "Fake tokens"; GitHub "Removing sensitive data from a repository" |
| markdownlint MD025 | "Multiple top-level headings"; fires only when line 1 is an H1; parameters are `front_matter_title` and `level` only | Google style guide, headings ("only use a level-1 heading once on a page") |
| `npx standard-readme-preset check` | `standard-readme-preset` is a remark preset with no binary and no `check` subcommand | `npx standard-readme` (package `standard-readme`, repo standard-readme-cli) |
| agentskills.io for a third-person description | third person is a Claude best-practices rule; the spec says only "should describe both what the skill does and when to use it" | cite the spec for the field, Claude for the voice |
| "IETF-inspired" RFC layout | RFC 2119 and 8174 govern requirement-keyword casing only | Rust RFC template and React RFC template |
| `kubernetes/rfcs` | the repository returns 404 and is absent from the org listing | kubernetes/enhancements KEP template |
| "Design Practice Repository" (Leanpub) | now titled "Design Practice Reference", and it holds no design-doc template | Software Engineering at Google, ch.10 |
| `research.google/pubs/pub37748/` | resolves to an unrelated advertising-economics paper | abseil.io/resources/swe-book/html/ch10.html |
| Conventional Commits "required prefixes" | only `feat` and `fix` are MUST; the rest are MAY, and the spec's list includes `build`, `ci`, `style`, `perf` | Conventional Commits 1.0.0, rules 2–4 |
| breaking-change marker | `!` goes immediately before the colon and may follow a scope; the footer token is uppercase | Conventional Commits 1.0.0, rules 12, 13, 16 |
| MADR's closed status set | MADR's placeholder ends in `…`; ADR-0008 shows free-form values | MADR ADR-0008 |

## Template coverage

Twenty doc types, thirteen templates. The research recommended shipping two
more — `postmortem.md` and `design-doc.md` — and keeping the other seven
types template-free on purpose. Both new templates shipped.

Do **not** ship Diátaxis quadrant templates. diataxis.fr says to impose no
structure: "It certainly does not mean that you should create empty
structures for tutorials/howto guides/reference/explanation with nothing in
them. Don't do that. It's horrible."

## Sources

All live on 2026-10-29: agentskills.io specification, agents.md, MADR 4.0.0
template and ADR-0002/0008, Rust and React RFC templates, Kubernetes KEP
template, Standard Readme spec and standard-readme-cli, Keep a Changelog
1.1.0, Conventional Commits 1.0.0, diataxis.fr, markdownlint MD025, Google
style guide headings and filenames, GitLab style guide, Google SRE postmortem
chapters, PagerDuty and Atlassian postmortem templates, Software Engineering
at Google ch.10, opensource.guide, Contributor Covenant.

Re-verify the agent-spec rows in 6 months. The agent-spec sources change
fastest; the changelog, SemVer and MADR rows change slowest.
