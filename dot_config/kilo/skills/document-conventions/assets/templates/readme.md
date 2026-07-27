# README.md Template

Copy to `README.md` at repo root. Sections follow the
[Standard Readme spec](https://github.com/RichardLitt/standard-readme/blob/main/spec.md).
Plain Markdown only — no frontmatter.

```markdown
# <Project name> (<package-name>)

<Short description: one line, ≤ 120 chars, no `>`, no leading/trailing
punctuation, matches the package manager's `description` field and
the GitHub repo description.>

<long description — motivation, problem the project solves, audience.
Move to docs/ if it grows past a few paragraphs.>

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [API](#api)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

<Why this project exists. What problem it solves. Inspiration, prior
art, dependencies.>

## Install

```sh
<install command>
```

### Dependencies

<Unusual dependencies that must be installed manually.>

## Usage

```sh
<minimal usage example>
```

### CLI

```sh
<CLI usage, if applicable>
```

## API

<Exported functions and objects. If you have a separate API.md or use
an auto-generator, point to it here.>

## Maintainers

- [@github-handle](https://github.com/handle) — <role>

## Contributing

PRs accepted. Where to ask questions: <link>. Code of Conduct:
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Small note: if editing the README, please conform to the
[standard-readme](https://github.com/RichardLitt/standard-readme)
spec.

## License

<SPDX-License-Identifier> © [Year] [Owner]
```

**Length:** < 200 lines target; 500 hard ceiling. Move detail to
`docs/`.

**Hard rules:**

- File must be `README.md` (uppercase, exactly)
- Short description ≤ 120 chars
- Sections in the order specified by Standard Readme
- License last
- English README must be `README.md`; translations use
  `README.<lang>.md` (BCP 47)

**Verification:**

```sh
npx standard-readme-preset check
```

Or manual review against [`../checklists.md`](../checklists.md).