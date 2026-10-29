# ssh

Reusable SSH client facts for this host.

## Entries

| Date | Entry | Source | Freshness | Notes |
|---|---|---|---|---|
| 2026-10-29 | [Public-key try order with a gpg-agent on this host](2026-10-29-ssh-identity-try-order.md) | `openssh-portable` master, `ssh_config(5)`, live `ssh -G` / `ssh -v` / `ssh-add -l` runs | check 2027-04 | A host's own `IdentityFile` is tried last when the agent holds that key. `IdentityFile none` is not a reset. The fix is a negated `Host` pattern in the shared defaults block. |
