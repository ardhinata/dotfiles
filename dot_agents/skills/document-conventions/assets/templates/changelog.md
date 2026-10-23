# CHANGELOG.md Template

Per [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).
Plain Markdown. Sections in fixed order; latest version first.

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- <new feature>.

### Changed

- <change in existing functionality>.

### Deprecated

- <soon-to-be-removed feature>.

### Removed

- <now-removed feature>.

### Fixed

- <bug fix>.

### Security

- <vulnerability fix>.

## [1.0.0] - YYYY-MM-DD

### Added

- <initial feature>.

[Unreleased]: https://github.com/<owner>/<repo>/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/<owner>/<repo>/releases/tag/v1.0.0
```

**Length:** unbounded. Trim old versions on a release cadence if the
file grows huge.

**Section order within a version:** Added → Changed → Deprecated →
Removed → Fixed → Security. Always.

**ISO date format:** `## [X.Y.Z] - YYYY-MM-DD`. Yanked releases add
`[YANKED]`: `## [0.0.5] - 2014-12-13 [YANKED]`.

**Verification:** manual review against [`../checklists.md`](../checklists.md).
Check date format and section order.