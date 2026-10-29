# Standards Map

Which rules in this skill are backed by a published standard, which are close
to one, and which are house style. Also: which doc types ship a template, and
which deliberately do not.

Verified 2026-10-29 against the primary sources. Re-verify before relying on
a field limit or a command name. The agent-spec sources move fast.

## Contents

- [How to read the verdicts](#how-to-read-the-verdicts)
- [Per-doc-type verdicts](#per-doc-type-verdicts)
- [Per-template verdicts](#per-template-verdicts)
- [Citation defects and their live replacements](#citation-defects-and-their-live-replacements)
- [Types that deliberately ship no template](#types-that-deliberately-ship-no-template)
- [Sources checked](#sources-checked)

## How to read the verdicts

| Verdict | Meaning |
|---|---|
| `matches-standard` | A published source states the rule, and the skill states it the same way. |
| `close-to-standard` | A published source states the rule, and the skill states it with a tightening, a gloss, or an omission. The deviation is named below. |
| `house-style` | No published source covers the rule. It is this project's convention. Cite it as such. |
| `wrong` | The skill attributes the rule to a source, and the source does not say it. Fix the citation or the rule. |

## Per-doc-type verdicts

| Doc type | Published source | Verdict | Template | Deviation |
|---|---|---|---|---|
| Rule file | none | `house-style` | `rule.md` | no frontmatter is a house decision |
| SKILL.md | [agentskills.io](https://agentskills.io/specification) | `close-to-standard` | `skill.md` | H1 in the body is house style; the spec puts no format restriction on the body |
| Skill reference file | agentskills.io "one level deep" | `matches-standard` | none | — |
| AGENTS.md | [agents.md](https://agents.md/) | `close-to-standard` | in `project-context` | the spec mandates no fields; "forbidden" is a house rule |
| README.md | [Standard Readme](https://github.com/RichardLitt/standard-readme/blob/main/spec.md) | `close-to-standard` | `readme.md` | "≤ 120 chars" is stricter than the spec's "less than 120 characters" |
| Topic README.md | none | `house-style` | none | the cache-topic template is the worked example |
| Knowledge-cache entry | none | `house-style` | `knowledge-cache-entry.md` | — |
| Knowledge-cache topic README.md | none | `house-style` | `knowledge-cache-topic-readme.md` | — |
| Knowledge-cache root README.md | none | `house-style` | none | same shape as the topic README |
| Postmortem | [Google SRE](https://sre.google/sre-book/example-postmortem/), [PagerDuty](https://response.pagerduty.com/after/post_mortem_template/) | `close-to-standard` | `postmortem.md` | the house rule adds no blameless clause, no action-item owner, no severity trigger |
| Persistent plan | none | `house-style` | `plan.md` | — |
| Transient plan | none | `house-style` | none | a scratch file needs no template |
| ADR | [MADR](https://adr.github.io/madr/) | `close-to-standard` | `adr.md` | the house rule closes the status set and fixes the section order; MADR leaves both open |
| RFC | [Rust](https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md), [React](https://raw.githubusercontent.com/reactjs/rfcs/main/0000-template.md) | `house-style` | `rfc.md` | the section list matches neither upstream template; it is house style |
| Design doc | [Google SWE ch.10](https://abseil.io/resources/swe-book/html/ch10.html), [KEP template](https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md) | `house-style` | `design-doc.md` | — |
| CHANGELOG.md | [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) | `close-to-standard` | `changelog.md` | the fixed category order is house policy; the spec only asks for grouping |
| CONTRIBUTING.md | [opensource.guide](https://opensource.guide/starting-a-project/#writing-your-contributing-guidelines) | `house-style` | `contributing.md` | no published CONTRIBUTING.md template exists |
| `.tmp/scratch` | none | `house-style` | none | — |
| `.tmp/migration` | none | `house-style` | none | — |
| Diátaxis quadrants | [diataxis.fr](https://diataxis.fr/) | `close-to-standard` | none | Diátaxis publishes language rules, not templates, and asks for no imposed structure |
| Report | none | `house-style` | `report.md` | the section set follows the shape of a bug report |
| Reference doc | [Diátaxis](https://diataxis.fr/reference/) | `house-style` | none | the quadrant is standard, the path and the no-date filename rule are house style |
| How-to guide | [Diátaxis](https://diataxis.fr/how-to-guides/) | `house-style` | none | the quadrant is standard, the path and the no-date filename rule are house style |
| Agent-only note | none | `house-style` | none | — |

## Per-template verdicts

| Template | Standard | Verdict | Notes |
|---|---|---|---|
| `adr.md` | MADR 4.0.0 | `close-to-standard` | section order matches the MADR full template item for item; MADR marks five sections optional and ships minimal and bare variants |
| `changelog.md` | Keep a Changelog 1.1.0 | `close-to-standard` | all six categories exist, including Security; `[YANKED]` and the two header links match verbatim |
| `contributing.md` | none | `house-style` | the Conventional Commits block inside it is the only standardised part |
| `design-doc.md` | Google SWE ch.10 | `house-style` | the section set is a house cut of the Google guidance, with the KEP goals and risks structure |
| `knowledge-cache-entry.md` | none | `house-style` | — |
| `knowledge-cache-topic-readme.md` | none | `house-style` | — |
| `plan.md` | none | `house-style` | — |
| `postmortem.md` | Google SRE + PagerDuty | `close-to-standard` | the field set is the published one; the house trim keeps the action-item table |
| `readme.md` | Standard Readme | `close-to-standard` | the section order matches the spec's order exactly; the spec's "no broken links" and "lint code examples" rules were missing |
| `rfc.md` | Rust + React RFC templates | `house-style` | the section list is house; the filename convention matches Rust |
| `rule.md` | none | `house-style` | — |
| `skill.md` | agentskills.io + Claude best practices | `close-to-standard` | the frontmatter fields and limits match; Claude's no-XML-tags and no-reserved-words rules were missing |
| `split-doc-directory.md` | none | `house-style` | — |
| `report.md` | none | `house-style` | the section set follows the shape of a bug report: summary, steps to reproduce, expected, actual, environment |

## Citation defects and their live replacements

Found 2026-10-29. Each row was wrong in the shipped skill.

| Wrong claim | Reality | Live replacement |
|---|---|---|
| OWASP Secrets Management Cheat Sheet supports "no secrets in docs" | the cheat sheet covers secret storage, rotation and audit; it has no rule about documentation content | [GitLab style guide — Fake tokens](https://docs.gitlab.com/development/documentation/styleguide/#fake-tokens), [GitHub — Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) |
| markdownlint MD025 enforces "exactly one H1 per file" | MD025 is "Multiple top-level headings"; it fires only when line 1 is an H1, and its only parameters are `front_matter_title` and `level` | [Google style guide — Headings](https://developers.google.com/style/headings) ("only use a level-1 heading once on a page") |
| `npx standard-readme-preset check` lints a README | `standard-readme-preset` is a remark preset with no binary and no `check` subcommand | `npx standard-readme` — the CLI package, [standard-readme-cli](https://github.com/RichardLitt/standard-readme-cli) |
| agentskills.io requires a third-person `description` | third person is a [Claude best-practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices) rule; the agentskills.io spec says only "should describe both what the skill does and when to use it" | cite the spec for the field, Claude for the voice |
| RFC section order is "IETF-inspired" | RFC 2119 and RFC 8174 govern requirement-keyword casing only; the IETF layout has no Summary, Motivation, or Drawbacks | [Rust RFC template](https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md), [React RFC template](https://raw.githubusercontent.com/reactjs/rfcs/main/0000-template.md) |
| Kubernetes `docs/rfcs/` is a cited source | the `kubernetes/rfcs` repository returns 404 and is absent from the org listing | [Kubernetes enhancements — KEP template](https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md) |
| the design doc follows the "Design Practice Repository" (Leanpub) | that book is now titled *Design Practice Reference* and holds no design-doc template | [Software Engineering at Google, ch.10](https://abseil.io/resources/swe-book/html/ch10.html) |
| `https://research.google/pubs/pub37748/` is the Google design-doc paper | that URL resolves to an unrelated advertising-economics paper | same as above |
| Conventional Commits "required prefixes" are `feat`, `fix`, `docs`, `refactor`, `test`, `chore` | only `feat` and `fix` are MUST; the rest are MAY, and the spec's own list includes `build`, `ci`, `style`, `perf` | [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) rules 2–4 |
| a breaking change is marked by appending `!` after the type | the `!` goes immediately before the colon and may follow a scope (`feat(api)!:`); the footer token is uppercase | same URL, rules 12, 13, 16 |
| the MADR status set is exactly five values | MADR's own placeholder ends in `…`; ADR-0008 shows free-form values such as `on hold` | [MADR ADR-0008](https://adr.github.io/madr/decisions/0008-add-status-field.html) |
| Keep a Changelog fixes the category order and requires the ISO date | the spec asks for same-type grouping and calls the date format "recommended" | [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) |

## Types that deliberately ship no template

| Type | Why no template |
|---|---|
| Skill reference file | the skill template already documents the `references/` layout; a second template adds nothing |
| Topic README.md, cache root README.md | the cache-topic template is the worked example of the same shape |
| Transient plan, `.tmp/scratch`, `.tmp/migration` | scratch files are never committed and have no required sections |
| Diátaxis quadrants | diataxis.fr says to impose no structure: "Don't do that. It's horrible." |
| Reference doc, how-to guide | they are Diátaxis quadrants, and diataxis.fr asks for no imposed structure |
| Agent-only note | a canonical note is free-form house knowledge |
| AGENTS.md | the template lives in the `project-context` skill, at `assets/templates/agents.md` |

## Sources checked

All live on 2026-10-29.

- [agentskills.io specification](https://agentskills.io/specification)
- [Claude — Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Anthropic — Equipping agents for the real world with agent skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [agents.md open format](https://agents.md/)
- [MADR](https://adr.github.io/madr/), [ADR-0002](https://adr.github.io/madr/decisions/0002-do-not-use-numbers-in-headings.html), [ADR-0008](https://adr.github.io/madr/decisions/0008-add-status-field.html)
- [Rust RFC template](https://raw.githubusercontent.com/rust-lang/rfcs/master/0000-template.md), [React RFC template](https://raw.githubusercontent.com/reactjs/rfcs/main/0000-template.md)
- [Kubernetes KEP template](https://raw.githubusercontent.com/kubernetes/enhancements/master/keps/NNNN-kep-template/README.md)
- [Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md), [standard-readme-cli](https://github.com/RichardLitt/standard-readme-cli)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Diátaxis](https://diataxis.fr/), [compass](https://diataxis.fr/compass/), [reference](https://diataxis.fr/reference/)
- [markdownlint MD025](https://raw.githubusercontent.com/DavidAnson/markdownlint/main/doc/md025.md)
- [Google style guide — headings](https://developers.google.com/style/headings), [filenames](https://developers.google.com/style/filenames)
- [GitLab style guide](https://docs.gitlab.com/development/documentation/styleguide/)
- [Google SRE — Example Postmortem](https://sre.google/sre-book/example-postmortem/), [Postmortem Culture](https://sre.google/sre-book/postmortem-culture/), [Workbook ch.10](https://sre.google/workbook/postmortem-culture/)
- [PagerDuty postmortem template](https://response.pagerduty.com/after/post_mortem_template/)
- [Atlassian postmortem templates](https://www.atlassian.com/incident-management/postmortem/templates)
- [Software Engineering at Google, ch.10](https://abseil.io/resources/swe-book/html/ch10.html)
- [opensource.guide — contributing guidelines](https://opensource.guide/starting-a-project/#writing-your-contributing-guidelines)
- [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)
