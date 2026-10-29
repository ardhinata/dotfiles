---
title: Embedding dimensions proxy deployment
date: 2026-10-29
last-updated: 2026-10-29
status: active
os:
  - linux
  - darwin
---

# Embedding dimensions proxy deployment

Magic Context and AFT call an OpenAI-style embeddings API without a
`dimensions` field. The provider then returns the model default, which is
4096 floats for `qwen/qwen3-embedding-8b`. A local proxy adds the field to
every request and relays the answer unchanged. Both tools then store 512
float vectors, and the semantic index shrinks by about 38 percent.

This guide installs the proxy on a Linux or a macOS machine, starts it as a
user service, and points both tools at it.

The proxy holds no secret. It forwards the `Authorization` header of the
caller. The API key stays in the environment of the caller.

## Files

| File | Linux | macOS |
|---|---|---|
| Proxy script | `~/.shell/helper/embedding_dimensions_proxy.py` | `~/.shell/helper/embedding_dimensions_proxy.py` |
| Service definition | `~/.config/systemd/user/embedding-dimensions-proxy.service` | `~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` |
| Log | `journalctl --user -u embedding-dimensions-proxy.service` | `~/.local/state/embedding-dimensions-proxy/proxy.log` |

## Before you start

1. Install Python 3.9 or newer.
2. Make sure port 8099 is free.
3. Export `OPENROUTER_API_OPENCODE_INDEX` in the environment of the agent.
4. Copy the proxy script to `~/.shell/helper/embedding_dimensions_proxy.py`.

The script lives in this repository at
`dot_shell/helper/executable_embedding_dimensions_proxy.py`. Chezmoi drops the
`dot_` and the `executable_` prefixes, so the deployed name is
`embedding_dimensions_proxy.py`.

## Linux

### 1. Install the unit

Write `~/.config/systemd/user/embedding-dimensions-proxy.service`:

```ini
[Unit]
Description=Embedding dimensions proxy for the OpenAI-compatible embeddings API
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/.shell/helper/embedding_dimensions_proxy.py
Environment=EMBEDDING_PROXY_DIMENSIONS=512
Environment=EMBEDDING_PROXY_PORT=8099
Environment=EMBEDDING_PROXY_UPSTREAM=https://openrouter.ai/api/v1/embeddings
Environment='EMBEDDING_PROXY_PROVIDER={"order":["deepinfra","siliconflow"],"allow_fallbacks":true}'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Systemd expands `%h` to the home directory. The unit file needs no template.

### 2. Start the unit

```bash
systemctl --user daemon-reload
systemctl --user enable --now embedding-dimensions-proxy.service
systemctl --user status embedding-dimensions-proxy.service
```

### 3. Keep the unit alive after logout

A user unit stops when the last session of the user ends. Run this once:

```bash
loginctl enable-linger "$USER"
```

Some systems ask for root rights for that command. Skip it when nobody logs
out of that machine.

## macOS

### 1. Install the agent

Write `~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.embedding-dimensions-proxy</string>

    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/Users/you/.shell/helper/embedding_dimensions_proxy.py</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>EMBEDDING_PROXY_DIMENSIONS</key>
        <string>512</string>
        <key>EMBEDDING_PROXY_PORT</key>
        <string>8099</string>
        <key>EMBEDDING_PROXY_UPSTREAM</key>
        <string>https://openrouter.ai/api/v1/embeddings</string>
        <key>EMBEDDING_PROXY_PROVIDER</key>
        <string>{"order":["deepinfra","siliconflow"],"allow_fallbacks":true}</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ProcessType</key>
    <string>Background</string>

    <key>StandardOutPath</key>
    <string>/Users/you/.local/state/embedding-dimensions-proxy/proxy.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/you/.local/state/embedding-dimensions-proxy/proxy.log</string>
</dict>
</plist>
```

Launchd needs absolute paths. It does not expand `%h`. The label in the file
must match the file name. The agent needs no root rights, so it never runs
`sudo`.

### 2. Load the agent

```bash
mkdir -p ~/.local/state/embedding-dimensions-proxy
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist
launchctl print gui/$(id -u)/com.user.embedding-dimensions-proxy | grep -E "state|pid"
```

To unload the agent, run:

```bash
launchctl bootout gui/$(id -u)/com.user.embedding-dimensions-proxy
```

## Point the clients at the proxy

### Magic Context

Edit `~/.config/cortexkit/magic-context.jsonc`:

```jsonc
"embedding": {
  "provider": "openai-compatible",
  "model": "qwen/qwen3-embedding-8b",
  "endpoint": "http://127.0.0.1:8099/<salt>/v1",
  "api_key": "{env:OPENROUTER_API_OPENCODE_INDEX}",
  "max_input_tokens": 640,
}
```

### AFT

Edit `~/.config/cortexkit/aft.jsonc`:

```jsonc
"semantic": {
  "backend": "openai_compatible",
  "model": "qwen/qwen3-embedding-8b",
  "base_url": "http://127.0.0.1:8099/<salt>/v1",
  "api_key_env": "OPENROUTER_API_OPENCODE_INDEX",
  "max_input_tokens": 640,
  "max_batch_size": 32,
}
```

### The salt segment

The proxy serves any path that ends in `/embeddings`. It drops the path
before the call reaches the provider. Both tools hash the endpoint into the
identity that names their embedding rows. Change the salt to force a
re-embed of every row.
The salt must be a path segment, not a query string.

## Check the deployment

### 1. The listener

```bash
# Linux
ss -ltnp | grep 8099

# macOS
lsof -nP -iTCP:8099 -sTCP:LISTEN
```

### 2. The proxy, without a call to the provider

A wrong path returns 404. A malformed body returns 400. Both answers come
from the proxy, so neither call costs a token.

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8099/nope -d "{}"
curl -s -w "\n%{http_code}\n" -X POST http://127.0.0.1:8099/<salt>/v1/embeddings -d "not-json"
```

### 3. One real call

This call reaches the provider and costs a few tokens. Run it once after a
fresh install.

```bash
python3 - <<'PY'
import json, os, urllib.request

key = os.environ["OPENROUTER_API_OPENCODE_INDEX"]
body = {"model": "qwen/qwen3-embedding-8b", "input": ["ping"]}
request = urllib.request.Request(
    "http://127.0.0.1:8099/<salt>/v1/embeddings",
    data=json.dumps(body).encode(),
    method="POST",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
)
with urllib.request.urlopen(request, timeout=60) as response:
    payload = json.load(response)
print("dims", len(payload["data"][0]["embedding"]))
PY
```

The answer must be `dims 512`. The log then names the provider that served
the call, for example `upstream provider=DeepInfra dimensions=512`.

## Restart rules

Magic Context reads its config file on every change. The new endpoint applies
at once. The tool embeds the new rows when it needs them.

AFT defers a change of `semantic.base_url`. The log line
`config reload deferred=[semantic.base_url]` names the deferred key. The
deferred value applies at the next connect or restart of the AFT backend.
Restart the agent on that machine to apply it.

The old rows stay in the database. The tools ignore them, because the stored
width no longer matches the query width. Delete those rows to reclaim the
space.

## Notes for the multi-OS templating effort

These notes describe the target shape for the templating effort. The guide
above does not depend on them.

### Source paths in this repository

| Source path | Target path |
|---|---|
| `dot_shell/helper/executable_embedding_dimensions_proxy.py` | `~/.shell/helper/embedding_dimensions_proxy.py` |
| `dot_config/systemd/user/embedding-dimensions-proxy.service` | `~/.config/systemd/user/embedding-dimensions-proxy.service` |
| `dot_Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist.tmpl` | `~/Library/LaunchAgents/com.user.embedding-dimensions-proxy.plist` |

The script path is the same on both systems. Keep one source file for it.

### Ignore the file of the other system

`.chezmoiignore` is a template. Add the target path of the file that does
not belong to the current system:

```text
{{ if eq .chezmoi.os "darwin" }}
.config/systemd/user/embedding-dimensions-proxy.service
{{ end }}
```

### Template variables

| Variable | Use |
|---|---|
| `{{ .chezmoi.os }}` | `linux` or `darwin` |
| `{{ .chezmoi.homeDir }}` | Absolute path inside the launchd plist |
| `{{ .chezmoi.username }}` | Label of the launchd agent |

Chezmoi cannot template a file name. A launchd label must match the file
name, so the label must not contain the user name. Use a fixed label such
as `com.user.embedding-dimensions-proxy`.

### Interpreter path

The two systems use different interpreters. Linux uses `/usr/bin/python3`.
macOS uses `/opt/homebrew/bin/python3` on an Apple silicon machine. Launchd
does not read `PATH`. Use an absolute path in `ProgramArguments`, or point
`ProgramArguments` at the script and rely on the shebang line.

### Start the service after apply

Use a `run_onchange` script under `.chezmoiscripts/` that branches on the
system name. The script starts `systemctl --user enable --now` on Linux and
`launchctl bootstrap` on macOS. The script needs no root rights.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| The port is busy | Another proxy uses 8099 | Change `EMBEDDING_PROXY_PORT` and the salt. Restart the service. |
| The log shows HTTP 401 | The caller sent no `Authorization` header | Export `OPENROUTER_API_OPENCODE_INDEX` in the environment of the agent. |
| The log shows HTTP 502 | The proxy could not reach the provider | Check the network and the upstream URL. |
| The log shows HTTP 429 | The provider quota answered the burst | Keep DeepInfra first in the provider order. Lower `max_batch_size`. |
| Retrieval finds nothing, the log shows 200 | The stored rows keep the old width | Let the tools re-embed, or delete the rows under the old model id. |
| The service stops after logout | The user session ended | Run `loginctl enable-linger "$USER"` on Linux. |
