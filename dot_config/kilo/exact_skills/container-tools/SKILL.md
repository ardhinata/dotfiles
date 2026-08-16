---
name: container-tools
description: Container runtime selection on machines where both docker and podman may be installed. Load before any docker/podman/nerdctl/containerd command, before writing a Dockerfile, Containerfile, compose.yaml, or podman-compose.yml, or when the user asks which container tool to use.
---

# Container Tools

Selects between `docker` and `podman` based on what's installed on this host.
Also covers Compose variant selection, image reference hygiene, and the
fallback path when no container runtime is installed at all.

## When to load

- About to run any `docker`, `podman`, `nerdctl`, or `containerd` command
- Authoring or editing a `Dockerfile`, `Containerfile`, `compose.yaml`,
  `compose.yml`, `docker-compose.yml`, or `podman-compose.yml`
- The user asks which container tool to use on this machine

## Podman vs Docker decision tree

If **both** are installed, the first question is whether `docker` is a
Podman shim — the `podman-docker` package (or Podman Desktop's
Docker-compatibility mode) installs `/usr/bin/docker` as a small shell
script that `exec`s `podman`.

Detect any one of:

```bash
# 1. stderr banner — podman-docker prints this on every invocation
docker --version 2>&1 | grep -q "Emulate Docker CLI using podman"

# 2. script body — the shim contains the literal word "podman"
grep -q "podman" "$(command -v docker)"

# 3. wrapper size — the upstream shim is a tiny ~10-line shell script
[ "$(wc -l < "$(command -v docker)")" -lt 20 ] && \
  grep -q "exec .*podman" "$(command -v docker)"
```

| Case | Action |
|---|---|
| `docker` is a Podman shim | **Use `podman` natively.** Drop the indirection. Prefer OCI image references (`quay.io`, `ghcr.io`, `registry.access.redhat.com`) over `docker.io` unless Docker Hub is explicitly required. |
| `docker` is the real Docker engine | **Ask the user** with the `question` tool whether to use `podman` or `docker` for this containerization task. Do not guess. |

Cache the user's choice for the rest of the session on this project.
Re-ask only if the toolchain changes or the user revokes the preference.

## Compose variant cheat sheet

| Engine | Compose command |
|---|---|
| Podman | `podman compose` (built-in, ships with `podman` >= 4.x) or `podman-compose` (standalone Python tool) |
| Docker | `docker compose` — **v2 plugin only**, never the legacy `docker-compose` v1 binary |

Confirm with `command -v docker-compose` — if it exists, prefer
`docker compose` (v2 plugin) anyway; v1 is unmaintained and lacks
several v2 features (`--profile`, `--env-file` precedence, build
secrets).

## Image references

Prefer OCI references unless the project pins Docker Hub:

- `quay.io/...` — Red Hat / community container registry
- `ghcr.io/...` — GitHub Container Registry, common for CI-built images
- `registry.access.redhat.com/...` — Red Hat-supported images

Use `docker.io/...` only when the project's `Dockerfile` already
references it or when pulling an image that genuinely only exists on
Docker Hub.

## Host prerequisites

- **macOS / Windows:** `podman machine list` must show
  `Currently running: true`. If `Currently running: false`, start with
  `podman machine start` and ask the user before doing it.
- **Linux:** sanity-check with `command -v` on first invocation.
- **Rootless vs rootful:** both engines default to rootless; SELinux
  hosts need `:z` (shared) or `:Z` (private) on bind mounts, e.g.
  `podman run -v ./src:/src:Z ...`.

## When no container runtime is installed

If `command -v docker` and `command -v podman` both fail, and the
project contains a `Dockerfile` or any compose file
(`compose.{yaml,yml}`, `docker-compose.{yaml,yml}`, `podman-compose.{yaml,yml}`),
recommend one of:

- **Podman** — daemonless, rootless by default, drop-in Docker-CLI compatible.
- **Docker** — Docker Desktop (macOS / Windows) or Docker Engine (Linux).

Ask the user which one they prefer. **Do not run the installer.**
Surface the install command only after the user confirms.

If the project has no container artifacts, this section is a no-op —
do not surface install recommendations for unrelated work.

## Known gotchas

- **Compose v1 vs v2:** v1 (`docker-compose`) is deprecated; v2
  (`docker compose` subcommand) ships with the Docker Engine CLI
  plugin. Several v1 flags (`--x-networking`) are silently dropped.
- **Rootless vs rootful:** rootless containers cannot bind to
  privileged ports (< 1024) without `sysctl` adjustments; for
  long-running daemons, rootful may be the right choice. Confirm with
  the user before flipping modes.
- **SELinux relabeling:** on RHEL/Fedora hosts, missing `:z`/`:Z`
  produces `Permission denied` inside the container. Add it on every
  bind mount that the container writes to.
- **Podman shim quiet failure:** the `podman-docker` shim
  occasionally returns success but with empty stdout when the
  underlying `podman` daemon is down. Always check exit status, not
  just output.

## Authoritative references

- podman docs — <https://docs.podman.io/en/latest/>
- podman-compose — <https://github.com/containers/podman-compose>
- containers/common (podman-docker shim source) — <https://github.com/containers/common>
- Docker Compose v2 plugin — <https://docs.docker.com/compose/compose-v2/>
- Docker Engine rootless mode — <https://docs.docker.com/engine/security/rootless/>