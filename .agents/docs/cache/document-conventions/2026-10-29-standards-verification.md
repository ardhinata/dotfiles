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
structure:

> It certainly does not mean that you should create empty structures for
> tutorials/howto guides/reference/explanation with nothing in them. Don't do
> that. It's horrible.

## The project-layout citation table

The `project-layout` skill has its own "Standard vs house style" table. It was
verified on 2026-10-29, after the citation research had already run against
`project-context` only.

| Row | Verdict |
|---|---|
| Root `AGENTS.md` plus nested per-package files, closest wins | Correct. The agents.md FAQ section says "The closest AGENTS.md to the edited file wins" |
| `docs/` at the repo root | No published standard prescribes the path. It is a docs-as-code convention, not a spec |
| `docs/adr/` | Correct. MADR's own init creates `docs/decisions`, and its 3.0.0-beta changelog records "Directory of ADRs changed from `docs/adr` to `docs/decisions`" |
| `docs/rfcs/` | Two defects. RFC 2223 "Instructions to RFC Authors" was obsoleted by RFC 7322 in 2014. Kubernetes keeps its proposals in `keps/`, not `rfcs/`, so it backs the practice and not the directory name |
| `docs/how-to/` and `docs/reference/` | Correct about the quadrants. The compass gives tutorial, how-to, reference, explanation. It says nothing about a `docs/` prefix, and the skill already says so |
| `postmortem` spelled as one word | Correct. Verified against the American Heritage Dictionary, Dictionary.com, Cambridge and Collins. The Merriam-Webster page returns 403 to automated fetches, so the citation was changed to a dictionary that was actually read |

## Sources

All live on 2026-10-29:

- agentskills.io specification, agents.md
- MADR 4.0.0 template and ADR-0002/0008
- Rust and React RFC templates, Kubernetes KEP template
- Standard Readme spec and standard-readme-cli
- Keep a Changelog 1.1.0, Conventional Commits 1.0.0
- diataxis.fr compass, markdownlint MD025
- Google style guide headings and filenames, GitLab style guide
- Google SRE postmortem chapters, PagerDuty and Atlassian postmortem templates
- Software Engineering at Google ch.10, opensource.guide, Contributor Covenant
- IETF RFC 7322, the kubernetes/enhancements repository tree
- American Heritage Dictionary, Dictionary.com, Cambridge and Collins

Re-verify the agent-spec rows in 6 months. The agent-spec sources change
fastest. The changelog, SemVer and MADR rows change slowest.
