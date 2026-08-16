# Container Tools — Docker only

`docker` is installed; `podman` is **not** available. Use Docker for all
container work in this project.

## Commands

- **Container / image ops**: standard `docker build`, `docker run`, `docker ps`,
  `docker images`, `docker stop`, `docker rm`, `docker pull`, `docker push`,
  `docker logs`, `docker exec`.
- **Compose**: `docker compose` (the **v2 CLI plugin**, not the legacy
  `docker-compose` v1 binary).
- **Image references**: `docker.io/...` is the implicit default; OCI
  registries (`ghcr.io/...`, `quay.io/...`) work without changes.

No Docker-vs-Podman decision needed — use Docker directly.
