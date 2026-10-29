# docs/how-to/

How-to guides for the parts of this setup that need an action on each
machine.

## Guides

| Guide | Covers |
|---|---|
| [Embedding dimensions proxy deployment](embedding-dimensions-proxy-deployment.md) | Install the local embeddings proxy on Linux and macOS, start it as a user service, and point Magic Context and AFT at it. |

## Related source

| Path | Holds |
|---|---|
| `dot_shell/helper/executable_embedding_dimensions_proxy.py` | The proxy script. Chezmoi deploys it as `~/.shell/helper/embedding_dimensions_proxy.py`. |
| `dot_config/systemd/user/embedding-dimensions-proxy.service` | The Linux unit file. |
| `dot_config/private_cortexkit/` | The Magic Context and AFT configs that name the proxy endpoint. |
