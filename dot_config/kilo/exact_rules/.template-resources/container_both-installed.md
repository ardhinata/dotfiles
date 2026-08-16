# Container Tools — both installed

Both `docker` and `podman` are available on this machine. Before picking one,
**check whether `docker` is a Podman shim** (the `podman-docker` package, or
Podman Desktop's Docker-compatibility mode, installs `/usr/bin/docker` as a
small shell script that `exec`s `podman`).

## Detect a Podman shim

Use any one of these — they are all reliable on a `podman-docker`-style shim:

```bash
# 1. stderr banner — podman-docker prints this on every invocation
docker --version 2>&1 | grep -q "Emulate Docker CLI using podman"

# 2. script body — the shim contains the literal word "podman"
grep -q "podman" "$(command -v docker)"

# 3. wrapper size — the upstream podman-docker shim is a tiny ~10-line shell script
[ "$(wc -l < "$(command -v docker)")" -lt 20 ] && \
  grep -q "exec .*podman" "$(command -v docker)"
```

A positive match means `docker` is a thin wrapper around `podman`.

## Decision

| Case | Action |
|---|---|
| `docker` is a Podman shim | **Use `podman` natively** — drop the indirection. Prefer OCI image references (`quay.io`, `ghcr.io`, `registry.access.redhat.com`) over `docker.io` unless Docker Hub is explicitly required. |
| `docker` is the real Docker engine | **Ask the user** with the `question` tool whether to use `podman` or `docker` for this containerization task. Do not guess. |

## If the user picks Podman (real Docker present)

- Commands: `podman ...`
- Compose: `podman compose` (or `podman-compose`)
- Prefer OCI references when the project does not pin Docker Hub.
- On macOS / Windows, confirm `podman machine list` shows `Currently running: true`.

## If the user picks Docker (real Docker present)

- Commands: `docker ...`
- Compose: `docker compose` (v2 plugin, not `docker-compose` v1)
- Standard `docker.io/...` references are fine.

## Caching the choice

After the user answers, prefer the chosen tool for the rest of the session on
this project. Re-ask only if the toolchain changes or the user revokes the
preference.
