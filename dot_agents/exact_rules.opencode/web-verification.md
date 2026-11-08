# Web Verification — OpenCode Tools

The web tools on this host, for the shared rule
`~/.agents/rules/web-verification.md`.

- `websearch` — web search. It takes no per-call parameters.
- `webfetch` — fetch a URL as text, markdown, or HTML.

## context7 MCP

`context7` is a remote MCP server. It serves the documentation of open-source
apps, services, and frameworks. The pages are always up to date, and the
server returns the version that the project uses.

The server is disabled by default in `~/.config/opencode/opencode.jsonc`,
under `mcp.servers.context7.disabled`. A disabled server adds no tool schemas
to a request, so it costs nothing.

Check it before you use `websearch` or `webfetch` for the documentation of a
framework or a service.

- The server is on. Use the `context7` tools. They give version-specific
  documentation and code examples.
- The server is off. Say in one line that it is off. The user turns it on
  when the task clearly benefits from it. The flag lives in the chezmoi
  source file `dot_config/opencode/private_opencode.jsonc`, so a change
  there needs a `chezmoi apply` to reach the target. Then use `websearch`
  or `webfetch`.
