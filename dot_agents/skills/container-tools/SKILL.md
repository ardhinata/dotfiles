---
name: container-tools
description: Container runtime selection on machines where both docker and podman may be installed. Load before any docker/podman/nerdctl/containerd command, before writing a Dockerfile, Containerfile, compose.yaml, or podman-compose.yml, or when the user asks which container tool to use.
---

# Container Tools

Selects between `docker` and `podman` based on what is installed on this host.
Also covers Compose variant selection, image reference hygiene, and the
fallback path when no container runtime is installed at all.

## When to load

- About to run any `docker`, `podman`, `nerdctl`, or `containerd` command
- Authoring or editing a `Dockerfile`, `Containerfile`, `compose.yaml`,
  `compose.yml`, `docker-compose.yml`, or `podman-compose.yml`
- The user asks which container tool to use on this machine

## Podman vs Docker decision tree

If **both** are installed, the first question is whether `docker` is a
Podman shim. The `podman-docker` package installs `/usr/bin/docker` as a
small shell script that `exec`s `podman`. Podman Desktop's
Docker-compatibility mode installs the same shim.

Detect any one of:

```bash
# 1. version line — the strongest check. Real Docker prints "Docker version",
#    the shim prints "podman version".
docker --version 2>&1 | grep -qi podman

# 2. stderr banner — podman-docker prints this on every invocation
docker --version 2>&1 | grep -q "Emulate Docker CLI using podman"

# 3. script body — the shim is a shell script that execs podman
file "$(command -v docker)" | grep -q "shell script" && \
  grep -q "exec .*podman" "$(command -v docker)"
```

The shim ends in `exec podman "$@"`, so the exit status is Podman's. Check
the exit status, not the output. The banner goes to stderr, so a script
that merges stderr into stdout sees it in the captured text. Silence it
with an empty `/etc/containers/nodocker` file.

| Case | Action |
|---|---|
| `docker` is a Podman shim | **Use `podman` natively.** Drop the indirection. Prefer OCI image references (`quay.io`, `ghcr.io`, `registry.access.redhat.com`) over `docker.io` unless Docker Hub is explicitly required. |
| `docker` is the real Docker engine | **Ask the user** which tool to use for this containerization task. Do not guess. |

Cache the user's choice for the rest of the session on this project.
Re-ask only if the toolchain changes or the user revokes the preference.

## Compose variant cheat sheet

| Engine | Compose command |
|---|---|
| Podman | `podman compose` — a wrapper that calls an external provider |
| Docker | `docker compose` — the current CLI. The legacy `docker-compose` v1 binary is end of life. |

**`podman compose` is a thin wrapper, not an implementation.** It runs an
external provider: `docker-compose` or `podman-compose`. When `docker-compose`
is installed, it takes precedence. Choose the provider with
`compose_providers` in the `[engine]` table of `containers.conf`, or with the
`PODMAN_COMPOSE_PROVIDER` environment variable. The wrapper prints a banner
on stderr. Silence it with `compose_warning_logs = false` in the same file, or
with `PODMAN_COMPOSE_WARNING_LOGS=false`.

**Compose v1 is end of life.** Docker support for it ended in July 2023, and
it is gone from current Docker Desktop releases. The supported Compose CLI
versions are v2 and v5. Both are invoked as `docker compose`. The documented
differences from v1:

- The top-level `version:` key is ignored, and Compose warns that it is
  obsolete.
- Container names use `-` where v1 used `_`.
- `docker-compose scale` becomes `docker compose up --scale`.
- `docker-compose rm --all` has no equivalent.
- `--compatibility` restores the v1 name separator.

If `command -v docker-compose` finds the legacy binary, use `docker compose`
anyway.

## Image references

Prefer OCI references unless the project pins Docker Hub:

- `quay.io/...` — Red Hat / community container registry
- `ghcr.io/...` — GitHub Container Registry, common for CI-built images
- `registry.access.redhat.com/...` — Red Hat-supported images

Use `docker.io/...` only when the project's `Dockerfile` already
references it or when pulling an image that genuinely only exists on
Docker Hub.

## Host prerequisites

- **macOS / Windows:** the machine must run. The human table of
  `podman machine list` shows `Currently running` in the LAST UP column. For
  a script, use the JSON form and read the `Running` field:
  `podman machine list --format json`. If the machine is stopped, start it
  with `podman machine start` and ask the user before doing it.
- **Linux:** sanity-check with `command -v` on first invocation.
- **Rootless vs rootful:** Podman runs rootless by default. Docker Engine
  runs rootful by default, because the system service starts as root.
  Rootless Docker is opt-in, through `dockerd-rootless-setuptool.sh install`
  or the script at <https://get.docker.com/rootless>.
- **SELinux:** on RHEL and Fedora hosts, a bind mount that the container
  writes to needs `:z` (shared) or `:Z` (private), for example
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

- **Rootless low ports:** a rootless container cannot bind a port below
  1024 unless `net.ipv4.ip_unprivileged_port_start` is lowered. The error
  says `rootlessport cannot expose privileged port`.
- **Podman 5 networking:** pasta is the default rootless network tool. It
  copies the address of the main interface. A container therefore cannot
  reach the host by that address. Inter-container connections need an
  explicit pasta network configuration.
- **Compose provider precedence:** `podman compose` runs `docker-compose`
  when it is installed, even if `podman-compose` is also present.
- **Rootless port forwarding:** rootless bridge networks forward ports
  through a userspace proxy that does not keep the client source address.
  `rootless_port_forwarder = "pasta"` in `containers.conf` changes that, but
  the option is experimental.

## Authoritative references

- podman docs — <https://docs.podman.io/en/latest/>
- `podman compose` wrapper behaviour — <https://docs.podman.io/en/latest/markdown/podman-compose.1.html>
- podman rootless notes — <https://github.com/podman-container-tools/podman/blob/main/rootless.md>
- podman and the podman-docker shim — <https://github.com/podman-container-tools/podman>
- podman-compose — <https://github.com/containers/podman-compose>
- Docker Compose versioning and the v1 migration — <https://docs.docker.com/compose/intro/history/>
- Docker retired products, including Compose v1 — <https://docs.docker.com/retired/>
- Docker Engine rootless mode — <https://docs.docker.com/engine/security/rootless/>
