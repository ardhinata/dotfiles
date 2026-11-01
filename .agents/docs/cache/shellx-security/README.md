# shellx-security

Facts about the shellx secret store: how the master secret is held, what
protects it, and what the options cost.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-11-01 | [Protecting the shellx master secret](2026-11-01-master-secret-protection-options.md) | Kernel docs, man7 keyrings(7), Cloudflare key retention blog, LWN libsecret, ArchWiki gnome-keyring, local tests | stable | Five options, measured on this host. The kernel keyring and libsecret both work here. systemd-creds does not, because its host key is root-only. |

## Related

- `docs/plans/2026-11-01-shellx-helper-optimization.md` — the plan that acts on these facts.
- `docs/reports/2026-11-01-agent-permission-and-safety-net-issues.md` — the file mode finding for the helper.
