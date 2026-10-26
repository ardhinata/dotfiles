#!/usr/bin/env python3
"""Local embeddings proxy that sets a fixed vector width.

AFT and Magic Context both send an OpenAI-style /v1/embeddings request
without a "dimensions" field. The server then returns the model default,
which is 4096 floats for qwen3-embedding-8b. This proxy adds "dimensions"
to every request body and relays the response unchanged.

The upstream API key stays with the caller. The caller sends its own
Authorization header and the proxy forwards that header as it is.

Environment:
  EMBEDDING_PROXY_UPSTREAM    upstream URL, default OpenRouter
  EMBEDDING_PROXY_DIMENSIONS  vector width to request, default 1024
  EMBEDDING_PROXY_PORT        listen port, default 8099
  EMBEDDING_PROXY_TIMEOUT     upstream timeout in seconds, default 180
"""

import json
import os
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


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "embedding-dimensions-proxy/1"

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/embeddings":
            self.reply(404, b'{"error":{"message":"only /v1/embeddings is served"}}')
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

        body["dimensions"] = DIMENSIONS
        request = urllib.request.Request(
            UPSTREAM, data=json.dumps(body).encode(), method="POST"
        )
        request.add_header("Content-Type", "application/json")
        authorization = self.headers.get("Authorization")
        if authorization:
            request.add_header("Authorization", authorization)

        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                self.reply(response.status, response.read())
        except urllib.error.HTTPError as error:
            self.reply(error.code, error.read())
        except (OSError, ValueError) as error:
            message = json.dumps(
                {"error": {"message": f"upstream request failed: {error}"}}
            ).encode()
            self.reply(502, message)

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
        f"dimensions={DIMENSIONS} upstream={UPSTREAM}",
        file=sys.stderr,
        flush=True,
    )
    server.serve_forever()


if __name__ == "__main__":
    main()
