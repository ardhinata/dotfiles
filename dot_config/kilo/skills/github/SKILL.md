---
name: github
description: GitHub work via the official `gh` CLI. Load for any GitHub-related action — opening/closing/listing issues and PRs, viewing repos, releases, Actions runs, code/repo/issue/PR search, clones, gists, secrets, and arbitrary GitHub REST/GraphQL calls. Always prefer `gh` over `curl`, `git`, or webfetch for github.com / GitHub Enterprise targets.
---

# GitHub CLI (`gh`)

Use `gh` for every GitHub-related action. It is authenticated, handles pagination, respects rate limits, and emits JSON when asked. Never `curl https://api.github.com` — go through `gh api` instead.

## When to Load

Any task that touches GitHub: issues, PRs, repos, releases, Actions, gists, code/issue/PR search, secrets, variables, deploy keys, repo metadata, or arbitrary REST/GraphQL. If you would otherwise reach for `curl`, `webfetch`, or `git` against `github.com`, use `gh` first.

## Auth Check

Run before any non-trivial batch of `gh` calls — fast and surfaces scope problems early:

```bash
gh auth status                                # accounts, protocol, scopes
gh auth token                                 # the active token (treat as secret)
gh api rate_limit --jq '.rate | {limit, remaining, reset}'
```

If `gh auth status` shows a failed default account (common when both `GITHUB_TOKEN` env and a stored host account compete), use `--hostname` or `GH_HOST` to disambiguate, or `gh auth switch` to choose the active one.

Token precedence: `GH_TOKEN` > `GITHUB_TOKEN` (github.com, *.ghe.com) and `GH_ENTERPRISE_TOKEN` > `GITHUB_ENTERPRISE_TOKEN` (GHES). For GitHub Enterprise set `GH_HOST=<host>` so stored creds are reused.

## Repository Context

`gh` infers the repo from the current working directory's `origin` remote. Override explicitly when needed:

```bash
gh pr list -R owner/repo                       # one-off
GH_REPO=owner/repo gh issue list               # env override
gh -R owner/repo release view v1.2.3           # global flag
```

## Output: JSON, jq, Templates

Default text output is line-based and human-shaped. For scripts, always pick JSON:

```bash
# Discover fields — run with no arg to enumerate
gh pr list --json

# Pick fields, then narrow
gh pr list --json number,title,author,state --jq '.[] | select(.state=="OPEN") | {n:.number, t:.title}'

# Go templates for terminal-friendly tables
gh issue list --json number,title,labels --template '{{range .}}{{.number}} {{.title}}{{"\n"}}{{end}}'
```

`--jq` does not require `jq` to be installed. For multi-page REST, use `--paginate` (combine with `--slurp` to get a single array):

```bash
gh api repos/owner/repo/issues --paginate --slurp \
  --jq 'map(select(.state=="open")) | length'
```

## Common Tasks

### Issues

```bash
gh issue list --state open --limit 50
gh issue view 123 --comments
gh issue create --title "..." --body "..." --label bug --assignee @me
gh issue close 123 --comment "fixed by #124"
gh issue develop 123 --branch fix/123 --base main    # create a branch linked to the issue
gh search issues "is:open is:issue label:bug repo:owner/repo"
```

### Pull Requests

```bash
gh pr list --author @me --state open
gh pr view 42 --json files,reviewDecision,statusCheckRollup
gh pr checkout 42                                    # co is an alias
gh pr create --fill --base main --reviewer @me --label ready
gh pr create --draft --title "WIP" --body "..."
gh pr merge 42 --squash --delete-branch
gh pr checks 42 --watch
gh pr diff 42
gh search prs "is:open review-requested:@me"
```

### Repos

```bash
gh repo view owner/repo --json nameWithOwner,defaultBranchRef,isPrivate,description
gh repo clone owner/repo
gh repo fork owner/repo --clone
gh repo sync                                       # mirror upstream
gh repo set-default owner/repo                      # set this checkout as default
gh browse                                          # open current repo in browser
gh browse 42                                        # open issue/PR #42
gh browse -n main path/to/file                     # print URL only
```

### Releases

```bash
gh release list --limit 10
gh release view v1.2.3
gh release create v1.2.3 ./dist/* --title "v1.2.3" --notes-file RELEASE.md
gh release download v1.2.3 -p "*.tar.gz" -D ./out
```

### Actions

```bash
gh run list --workflow ci.yml --limit 20
gh run view 12345 --log
gh run watch 12345                                 # blocks until done
gh run rerun 12345 --failed
gh workflow run ci.yml -f ref=main
gh cache list --sort size --limit 20
```

### Secrets, Variables, Deploy Keys

```bash
gh secret list
gh secret set MY_SECRET --body "$VALUE"            # or --env-file
gh variable set MY_VAR --body "value"
gh repo deploy-key add ~/.ssh/id_ed25519.pub --title "ci-key" --read-only
```

### Search across GitHub

```bash
gh search repos "language:rust stars:>1000"
gh search code "TODO owner/repo" --limit 20
gh search commits "fix race condition" --author @me
gh search prs "is:merged author:@me" --json number,title,repository --limit 50
```

### Raw REST / GraphQL via `gh api`

Use `gh api` whenever the high-level command does not cover the call (e.g. rulesets, reactions, projects v2, custom endpoints):

```bash
# REST — path templating is brace-expanded
gh api repos/{owner}/{repo}/rulesets
gh api -X POST repos/owner/repo/issues -f title='...' -f body='...'

# GraphQL — query via -f
gh api graphql -f query='{ viewer { login } }' --jq '.data.viewer.login'

# Pagination + aggregation
gh api --paginate --slurp repos/owner/repo/issues/comments \
  --jq 'map(.user.login) | group_by(.) | map({user: .[0], count: length}) | sort_by(.count) | reverse'

# Read body from a file
gh api repos/owner/repo/rulesets --input rulesets.json --method PUT
```

## Scripting Patterns

- **Always** add `--json` + `--jq` for anything downstream consumes. Default text output is for humans and can change between releases.
- **Always** pass `--limit` explicitly on `list`/`search` commands when you need a specific cap; the default is 30.
- **Prefer** `gh api` over `curl` for github.com — it inherits auth, host, and tokens correctly.
- **Prefer** `gh search` over GitHub's web UI for filtering through the agent.
- **Detect** silent pagination truncation: `gh api ... --paginate --slurp` returns one big array; without `--slurp` the default is to print only the last page.
- **Exit codes**: `0` ok, `1` failure, `2` cancelled, `4` auth required. Check `gh help exit-codes` when scripting.

## Anti-Patterns

- ❌ `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/...` — use `gh api` instead.
- ❌ `webfetch` against `api.github.com` — the GitHub API rarely returns readable markdown; use `gh api` or `gh <noun> view`.
- ❌ `git ls-remote` to discover PR/issue refs — use `gh pr/issue list`.
- ❌ Building JSON by string concatenation — pipe `--input file.json` or `-f key=value` to `gh api`.
- ❌ Echoing `gh auth token` in logs or responses — it is a credential.
- ❌ Skipping `gh auth status` when a command fails with `401`/`403`; the failure is usually a scope, not a bug.
- ❌ Writing `gh pr create` with `--title`/`--body` from `printf` heredocs that contain backticks — use `--body-file` or `--body "$VAR"` to avoid shell expansion.
- ❌ Reading encrypted secrets out of `dot_ssh/keys/`, `.encryption_keys/`, or age-encrypted files to pass to `gh secret set` — read from the live secret store instead, or ask the user to provide the value.

## Quick Decision Cheatsheet

| Goal | Command |
|---|---|
| Open repo / issue / PR in browser | `gh browse [path\|#]` |
| Read a single file from a repo | `gh repo read-file owner/repo path/to/file` (no clone) |
| List a repo's directory | `gh repo read-dir owner/repo path/to/dir` |
| Find a PR by branch | `gh pr list --head <branch> --json number,title,url` |
| Find an issue by text | `gh issue list --search "in:title <phrase>"` |
| Get the current PR's CI status | `gh pr checks --json name,conclusion,state` |
| Open an issue from a stack trace | `gh issue create --title "..." --body-file -` (stdin) |
| Cross-repo search | `gh search prs --review-requested:@me --state open` |
| Enterprise host | `GH_HOST=github.acme.com gh api ...` |

## Cross-References

- For text rendering (TUI / output formatting): use `gh issue/pr view --comments` not web scraping.
- For chezmoi templating that involves GitHub refs: combine with the `chezmoi` skill.
- For shell-side scripting helpers: load the `fnm` skill when any Node tooling is in the chain.

## Pointers

- Official manual: <https://cli.github.com/manual>
- Environment variables: `gh help environment`
- Output formatting reference: `gh help formatting`
- Exit codes: `gh help exit-codes`
- Release notes: <https://github.com/cli/cli/releases>
