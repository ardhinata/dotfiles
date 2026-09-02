# Permission Block (snapshot 2026-09-02 — globalised)

> The fleet was rebuilt 2026-09-01 with the subagents deployed globally
> (chezmoi-managed at `dot_config/kilo/exact_agent/` → deployed to
> `~/.config/kilo/agent/`). This update removes project-specific
> references from the shared permission block so the same block works
> on any project the user is in.

## Hybrid model

An explicit allowlist of common read-only bash commands runs without
prompting; everything else bash triggers a per-call user confirmation
(`ask`). Web research tools (built-in + MCP) are allowed. Mutation
tools (`edit`, `write`) are scoped to the **global subagent write
target** (`~/.local/share/kilo/subagent-runs/`) and `/tmp/kilo`.

## YAML block (paste into each subagent's frontmatter)

```yaml
permission:
  "*": deny
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit:
    "*": deny
    "~/.local/share/kilo/subagent-runs/**": allow
    "~/.local/share/kilo/subagent-runs/**/*": allow
  write:
    "*": deny
    "~/.local/share/kilo/subagent-runs/**": allow
    "~/.local/share/kilo/subagent-runs/**/*": allow
  external_directory:
    "/tmp/kilo/**": allow
    "/tmp/kilo/**/*": allow
    "~/.local/share/kilo/subagent-runs/**": allow
    "~/.local/share/kilo/subagent-runs/**/*": allow
  bash:
    "*": ask
    "git log *": allow
    "git diff *": allow
    "git status *": allow
    "git show *": allow
    "find *": allow
    "grep *": allow
    "ls *": allow
    "cat *": allow
    "tail *": allow
    "head *": allow
  webfetch: allow
  websearch: allow
  firecrawl_*: allow
  tavily_*: allow
  context7_*: allow
  # `task`, `question`, `suggest`, `interactive_terminal` are auto-denied by
  # the KiloTask pre-pend layer; do not declare them here.
```

## Global write target

Subagent YAML reports go to **`~/.local/share/kilo/subagent-runs/`**
(deployed via the `~/.local/share/kilo/` parent kilo state dir). This
replaces the older project-local `.tmp/docs/subagent-runs/`, which
required the subagent to know the project's shared-context convention
and tied the write target to the working directory.

The global target is:

- Independent of project (works in any working directory).
- Cross-project visible — `ls ~/.local/share/kilo/subagent-runs/` shows
  all subagent runs across projects (mix of runs is OK; filenames are
  timestamp-prefixed so collisions don't happen).
- Per-machine only — subagent reports are ephemeral, no cross-machine
  sync required.
- Not git-tracked — add `subagent-runs/` to the user's shell cleanup
  (`rm -rf` after a session) if desired.

If you want per-project retention or cross-worktree sync, move reports
back to `.tmp/docs/subagent-runs/` at the **parent agent** level (i.e.
have the parent agent `mv` the file from the global dir to the shared
context dir after the subagent returns). The subagents themselves stay
project-agnostic.

## Notes

- **`*` → `ask` is the catch-all** — order matters (last match wins).
  Allowlist entries come AFTER `*`, so specific patterns override
  `ask` for common read-only commands. Any other bash call (every
  `aws` verb, `docker`, `kubectl`, package managers) prompts the user.
- **`firecrawl_*` / `tavily_*` / `context7_*` are MCP catch-alls** —
  the tool id format is `<tool_id>_<tool_name>`, so the single-segment
  `*` matches every tool that server exposes.
- **`/tmp/kilo` and `~/.local/share/kilo/subagent-runs` depth limit** —
  `*` does NOT match `/` in this matcher, so the two patterns `<dir>/**`
  and `<dir>/**/*` together cover one and two segment depths.
- **Subagents stay read-only by default** — if the question requires
  mutation, the parent agent does the mutation, not the subagents.

## Sensitive-file handling

The subagent bodies no longer hardcode project-specific sensitive-file
deny rules (e.g. `.encryption_keys/`, `dot_ssh/keys/`, `.age`,
`.encrypted_data/`, etc.). Those conventions are project-specific — the
chezmoi dotfiles project has them, a generic `code` project does not.

The Kilo runtime globally guards:

- `.env`, `.env.*` reads — `read: allow` does not bypass the prompt
  (per `2026-08-15-permissions-actions-precedence.md` line 84).
- Other projects' sensitive-file patterns should be added to the
  parent's `permission.read` block, not the global subagent block.

## Operational discipline preamble

The preamble that previously lived inline in every subagent body has
been removed; each body now has a 6-line `## Operational discipline`
section that points at this file. The summary text:

```markdown
## Operational discipline

The shared permission block + operational discipline preamble lives
at `~/.config/kilo/skills/subagent-fleet/references/permission-block.md`
(deployed from
`dot_config/kilo/exact_skills/subagent-fleet/references/permission-block.md`
in this chezmoi source). Read it once at session start; do not
duplicate the rules inline here. Summary: read-only by default,
mutation allowed only under `~/.local/share/kilo/subagent-runs/` and
`/tmp/kilo/`, web research allowed, delegation denied.
```

## Validation checklist

After deploying, verify:

1. `kilo agent list` shows all 5 subagents loading.
2. Each subagent's permission block has `~/.local/share/kilo/subagent-runs/**`
   allowed on `edit`/`write`/`external_directory`.
3. `~/.local/share/kilo/subagent-runs/` exists and is writable
   (`mkdir -p` if needed; the deploy-time script could do this).
4. Subagent isolation — confirm parent's `edit`/`bash` allow does NOT
   leak into subagents. Parent's `deny` survives per
   `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md:21-26`.
5. Per-model behaviour — run a single known question with N=4
   (`haru + natsu + aki + fuyu` in parallel). Confirm `shiki`'s
   `claims_table` has rows for each research subagent and the
   `provenance.research_ran` list names all four.
6. Cost ceiling — verify the worst case (N=4 + shiki) stays within the
   per-question budget.
