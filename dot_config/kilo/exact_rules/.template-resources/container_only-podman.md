# Container Tools — Podman only

`docker` is **not** installed; `podman` is available. Use Podman for all
container work in this project.

## Commands

- **Container / image ops**: `podman build`, `podman run`, `podman ps`,
  `podman images`, `podman stop`, `podman rm`, `podman pull`, `podman push`,
  `podman logs`, `podman exec`. Podman's CLI matches Docker for everyday use.
- **Compose**: `podman compose up` / `podman compose down`. If the
  `podman-compose` plugin is missing, fall back to `podman-compose` (the
  external Python project) and note it for the user.
- **Volumes, networks, port mappings**: identical syntax to Docker.

## Image references

- Dockerfile is already OCI-compatible — no rewriting required.
- Prefer **OCI references** (`quay.io/...`, `ghcr.io/...`,
  `registry.access.redhat.com/...`) over `docker.io/...` when the project does
  not specifically require Docker Hub.

## First-action sanity check

Before the first `podman` invocation in a session, confirm availability:

```
command -v podman && podman --version
```

If Podman is on macOS / Windows, also confirm the machine is running:
`podman machine list` — if `Currently running: false`, surface that and stop
instead of running a command that will silently no-op.
