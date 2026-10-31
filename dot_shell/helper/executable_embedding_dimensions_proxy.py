#!/usr/bin/env python3
"""Local embeddings proxy that sets a per-caller vector width and a provider.

AFT and Magic Context both send an OpenAI-style /v1/embeddings request
without a "dimensions" field. The server then returns the model default,
which is 4096 floats for qwen3-embedding-8b. This proxy adds "dimensions"
to every request body and relays the response unchanged.

The request path picks the width. Take the path, drop the query string and
trailing slashes, then strip the final "/embeddings". If the rest ends with
"/v1", strip that too. Split the rest on "/" and drop empty parts. The count
of parts decides the width:

  /v1/embeddings            no salt, no width: the env default
  /<salt>/v1/embeddings     one salt: the env default
  /<salt>/<width>/v1/embeddings  a salt and a width: that width
  /<a>/<b>/<c>/...          400: one salt and one width at most

The width must be decimal digits only, between 1 and 4096.

The salt never reaches the provider. It changes the endpoint string that the
caller hashes into its embedding identity, so a new salt forces a re-embed.

A provider can ignore the "dimensions" field and answer with the model
default. A caller would then store rows that never match its query vectors,
and the failure would be silent. So a 200 reply that holds a "data" list of
objects with an "embedding" list must match the width the proxy asked for.
Any other reply shape passes through untouched.

The proxy also names the providers the request may use. The list holds
Nebius and DeepInfra, which cost the same per token. The list has no order,
so OpenRouter picks the provider for each request by price, throughput,
latency, and reliability, and shifts traffic away from a pool that answers
with HTTP 429. SiliconFlow is not in the list. A caller that sends its own
"provider" field keeps that choice.

The upstream API key stays with the caller. The caller sends its own
Authorization header and the proxy forwards that header as it is.

Environment:
  EMBEDDING_PROXY_UPSTREAM    upstream URL, default OpenRouter
  EMBEDDING_PROXY_DIMENSIONS  default vector width, used when the path
                              carries no width segment, default 1024
  EMBEDDING_PROXY_PROVIDER    provider preference as JSON, empty for none
  EMBEDDING_PROXY_PORT        listen port, default 8099
  EMBEDDING_PROXY_TIMEOUT     upstream timeout in seconds, default 180
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

UPSTREAM = os.environ.get(
    "EMBEDDING_PROXY_UPSTREAM", "https://openrouter.ai/api/v1/embeddings"
)
DIMENSIONS = int(os.environ.get("EMBEDDING_PROXY_DIMENSIONS", "1024"))
PORT = int(os.environ.get("EMBEDDING_PROXY_PORT", "8099"))
TIMEOUT = float(os.environ.get("EMBEDDING_PROXY_TIMEOUT", "180"))
PROVIDER_FIELD = re.compile(rb'"provider"\s*:\s*"([^"]+)"')
DEFAULT_PROVIDER = {"only": ["nebius", "deepinfra"], "allow_fallbacks": True}
WIDTH_MIN = 1
WIDTH_MAX = 4096


def load_provider():
    raw = os.environ.get("EMBEDDING_PROXY_PROVIDER")
    if raw is None:
        return DEFAULT_PROVIDER
    if not raw.strip():
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SystemExit(f"EMBEDDING_PROXY_PROVIDER is not valid JSON: {error}")
    if not isinstance(value, dict):
        raise SystemExit("EMBEDDING_PROXY_PROVIDER must hold a JSON object")
    return value


PROVIDER = load_provider()


def path_width(path):
    """Return the vector width that a trimmed request path asks for.

    The path ends with "/embeddings", and an optional "/v1" sits before it.
    No part before that keeps the default width. One part is a salt and also
    keeps the default. Two parts are a salt and a width. Three or more parts
    are refused. Raise ValueError with a short message when the path cannot
    name a width.
    """
    rest = path[: -len("/embeddings")]
    if rest.endswith("/v1"):
        rest = rest[: -len("/v1")]
    parts = [part for part in rest.split("/") if part]
    if len(parts) < 2:
        return DIMENSIONS
    if len(parts) > 2:
        raise ValueError(
            "a path may hold at most one salt and one width segment"
        )
    raw = parts[1]
    if not re.fullmatch(r"[0-9]+", raw):
        raise ValueError("the width segment must hold decimal digits only")
    width = int(raw)
    if not WIDTH_MIN <= width <= WIDTH_MAX:
        raise ValueError(
            f"the width must be between {WIDTH_MIN} and {WIDTH_MAX}"
        )
    return width


def wrong_width(data, width):
    """Return a message when a reply holds vectors of another width.

    Return None when the body is not a "data" list of objects with an
    "embedding" list. Such a body is relayed as it is.
    """
    try:
        payload = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    items = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    for item in items:
        embedding = item.get("embedding") if isinstance(item, dict) else None
        if not isinstance(embedding, list):
            return None
        if len(embedding) != width:
            return (
                f"upstream returned {len(embedding)} dimensions, "
                f"expected {width}"
            )
    return None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "embedding-dimensions-proxy/1"

    def do_POST(self):
        # Any path that ends with /embeddings is served. The parts in front of
        # it hold an optional salt and an optional width. See path_width.
        path = self.path.split("?", 1)[0].rstrip("/")
        if not path.endswith("/embeddings"):
            self.reply(404, b'{"error":{"message":"only an /embeddings path is served"}}')
            return
        try:
            width = path_width(path)
        except ValueError as error:
            self.reply(400, json.dumps({"error": {"message": str(error)}}).encode())
            return

        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as error:
            self.reply(400, json.dumps({"error": {"message": str(error)}}).encode())
            return
        if not isinstance(body, dict):
            self.reply(400, b'{"error":{"message":"body must be a JSON object"}}')
            return

        body["dimensions"] = width
        if PROVIDER is not None and "provider" not in body:
            body["provider"] = PROVIDER

        request = urllib.request.Request(
            UPSTREAM, data=json.dumps(body).encode(), method="POST"
        )
        request.add_header("Content-Type", "application/json")
        authorization = self.headers.get("Authorization")
        if authorization:
            request.add_header("Authorization", authorization)

        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                data = response.read()
                status = response.status
        except urllib.error.HTTPError as error:
            data = error.read()
            status = error.code
        except (OSError, ValueError) as error:
            message = json.dumps(
                {"error": {"message": f"upstream request failed: {error}"}}
            ).encode()
            self.reply(502, message)
            return

        self.note_provider(data, width)
        problem = wrong_width(data, width) if status == 200 else None
        if problem is not None:
            self.reply(502, json.dumps({"error": {"message": problem}}).encode())
            return
        self.reply(status, data)

    def note_provider(self, data, width):
        match = PROVIDER_FIELD.search(data)
        provider = match.group(1).decode() if match else "unknown"
        print(
            f"[embedding-dimensions-proxy] upstream provider={provider} "
            f"dimensions={width}",
            file=sys.stderr,
            flush=True,
        )

    def reply(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print(f"[embedding-dimensions-proxy] {fmt % args}", file=sys.stderr, flush=True)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(
        f"[embedding-dimensions-proxy] listening on 127.0.0.1:{PORT} "
        f"dimensions={DIMENSIONS} provider={json.dumps(PROVIDER)} upstream={UPSTREAM}",
        file=sys.stderr,
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
