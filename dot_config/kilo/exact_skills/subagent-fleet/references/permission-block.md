# Permission Block (snapshot 2026-08-25)

> Re-verify against `docs/subagent-fleet/2026-08-17-subagent-creative-conservative.md` §6
> when reachable. The block is shared by all 5 subagents.

## Hybrid model

An explicit allowlist of common read-only bash commands runs without
prompting; everything else bash triggers a per-call user confirmation
(`ask`). Web research tools (built-in + MCP) are allowed. Mutation
tools (`edit`, `write`) are scoped to the report-doc directory and
`/tmp/kilo`.

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
    ".tmp/docs/subagent-runs/**": allow
    ".tmp/docs/subagent-runs/**/*": allow
  write:
    "*": deny
    ".tmp/docs/subagent-runs/**": allow
    ".tmp/docs/subagent-runs/**/*": allow
  external_directory:
    "/tmp/kilo/**": allow
    "/tmp/kilo/**/*": allow
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

## Notes

- **`*` → `ask` is the catch-all** — order matters (last match wins).
  Allowlist entries come AFTER `*`, so specific patterns override `ask`
  for common read-only commands. Any other bash call (every `aws`
  verb, `docker`, `kubectl`, package managers) prompts the user.
- **`firecrawl_*` / `tavily_*` / `context7_*` are MCP catch-alls** —
  the tool id format is `<tool_id>_<tool_name>` (e.g.
  `firecrawl_firecrawl_search`), so the single-segment `*` matches
  every tool that server exposes. No `:batch` / `:exacto` / `:<tag>`
  variants exist on MCP tool ids.
- **`/tmp/kilo` depth limit** — `*` does NOT match `/` in this matcher,
  so the two patterns `/tmp/kilo/**` and `/tmp/kilo/**/*` together
  cover one and two segment depths. Three-or-more segments do not
  match — accepted limitation, documented.
- **Subagents stay read-only by default** — if the question requires
  mutation, the main agent does the mutation, not the subagents.

## Operational discipline preamble (prepend to every subagent body)

Every subagent body starts with this section so the read-only
discipline sits alongside the role-specific prompt:

```markdown
## Operational discipline (read-only by default)

You run under a hybrid permission model:

- **Allowlisted bash** (no prompt): git read-only
  (`log`/`diff`/`status`/`show`), `find`, `grep`, `ls`, `cat`, `tail`,
  `head`.
- **Catch-all bash**: every other command — including all `aws` verbs,
  `docker`, `kubectl`, package managers, anything not in the allowlist —
  triggers a per-call user confirmation (`ask`). Use these only when no
  allowlisted equivalent exists.
- **Mutation tools** (`edit`, `write`) are denied everywhere except the
  report doc location `.tmp/docs/subagent-runs/` and the scratch dir
  `/tmp/kilo`.
- **Web research tools** are allowed: `webfetch`, `websearch`,
  `firecrawl_*`, `tavily_*`, `context7_*`.
- **Delegation tools** are auto-denied: `task` (cannot spawn further
  subagents), `question` / `interactive_terminal` / `suggest` (cannot
  query the user).

Treat the `ask` fallback as a hard stop. Prefer read-only equivalents:

| Mutating (will prompt) | Read-only substitute |
|---|---|
| `git push`, `git commit` | `git log`, `git diff`, `git show` |
| `aws ec2 run-instances`, `aws iam create-access-key` | `aws ec2 describe-*`, `aws iam list-*`, `aws iam get-*` |
| `rm`, `mv`, `cp` to overwrite | read the file, then in your output write `main_agent_should_run: <cmd>` and let the main agent execute it |
| any package install / service restart | state the action in your output; do not run |

The main agent owns all mutations. You produce findings and
recommended actions in your structured output; the main agent performs
the writes.
```

## Validation checklist

After deploying, verify:

1. `kilo agent list` shows all 5 subagents loading.
2. `kilo agent list --json` (or equivalent) shows `permission.task: deny`
   on all 5 — the one-level delegation ceiling.
3. Subagent isolation — confirm parent's `edit`/`bash` allow does NOT
   leak into subagents. Parent's `deny` survives per
   `.agents/docs/cache/kilo-subagents/2026-08-17-revalidation-v7.4.22-deep.md:21-26`.
4. Per-model behaviour — run a single known question with N=4
   (`haru + natsu + aki + fuyu` in parallel). Confirm `shiki`'s
   `claims_table` has rows for each research subagent and the
   `provenance.research_ran` list names all four.
5. Cost ceiling — verify the worst case (N=4 + shiki) stays within the
   per-question budget.
