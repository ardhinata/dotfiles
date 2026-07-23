# Container Tools (Docker / Podman)

Neither `docker` nor `podman` is installed on this machine.

If a project contains a `Dockerfile` or a Docker Compose file (`docker-compose.yml`,
`docker-compose.yaml`, `compose.yml`, `compose.yaml`), surface a recommendation to
install one of:

- **Podman** — daemonless, rootless by default, drop-in Docker-CLI compatible.
- **Docker** — Docker Desktop (macOS / Windows) or Docker Engine (Linux).

Do **not** run the installer. Ask the user which one they prefer and stop there.

If the project has no container artifacts, this rule is a no-op.
