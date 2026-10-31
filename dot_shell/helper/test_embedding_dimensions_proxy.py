"""Unit tests for the embedding dimensions proxy.

Run with:
    python3 dot_shell/helper/test_embedding_dimensions_proxy.py

The tests use two loopback HTTP servers: a stub upstream that records the
request it receives, and the proxy under test. They need no network access
and no test framework beyond stdlib `unittest`.
"""

import importlib.machinery
import importlib.util
import json
import os
import threading
import unittest
import unittest.mock
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar

HERE = Path(__file__).resolve().parent
CANDIDATES = ("embedding_dimensions_proxy.py", "executable_embedding_dimensions_proxy.py")


def load_module():
    for name in CANDIDATES:
        path = HERE / name
        if path.exists():
            loader = importlib.machinery.SourceFileLoader("embedding_dimensions_proxy", str(path))
            spec = importlib.util.spec_from_loader(loader.name, loader)
            module = importlib.util.module_from_spec(spec)
            loader.exec_module(module)
            return module
    raise FileNotFoundError("embedding_dimensions_proxy.py not found next to the test")


proxy = load_module()


def echo_vector(width):
    """The vector the stub answers with for a requested width."""
    return [((index + 1) / 10) for index in range(width)]


class StubUpstream(BaseHTTPRequestHandler):
    """Records the last request and answers with a vector of the asked width.

    "force_width" makes the stub answer with another width, the way a
    provider that ignores "dimensions" would.
    """

    received: ClassVar[dict] = {}
    force_width: ClassVar[int] = None

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length))
        StubUpstream.received = {
            "body": body,
            "authorization": self.headers.get("Authorization"),
            "path": self.path,
        }
        width = StubUpstream.force_width or body.get("dimensions", 2)
        payload = json.dumps(
            {
                "data": [
                    {
                        "embedding": echo_vector(width),
                        "index": 0,
                    }
                ],
                "provider": "DeepInfra",
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


class ProxyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stub = ThreadingHTTPServer(("127.0.0.1", 0), StubUpstream)
        threading.Thread(target=cls.stub.serve_forever, daemon=True).start()
        proxy.UPSTREAM = f"http://127.0.0.1:{cls.stub.server_port}/v1/embeddings"
        proxy.DIMENSIONS = 1024
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), proxy.Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/v1/embeddings"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.stub.shutdown()
        cls.stub.server_close()

    def setUp(self):
        proxy.PROVIDER = {"only": ["nebius", "deepinfra"], "allow_fallbacks": True}
        proxy.DIMENSIONS = 1024
        StubUpstream.force_width = None

    def post(self, body, headers=None, path="/v1/embeddings"):
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.server.server_port}{path}",
            data=json.dumps(body).encode(),
            method="POST",
        )
        request.add_header("Content-Type", "application/json")
        for name, value in (headers or {}).items():
            request.add_header(name, value)
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read())

    def post_error(self, body, path):
        """Post to a path that must fail and return its status and payload."""
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.post(body, path=path)
        error = caught.exception
        try:
            return error.code, json.loads(error.read())
        finally:
            error.close()

    def test_injects_dimensions(self):
        status, payload = self.post({"model": "qwen/qwen3-embedding-8b", "input": ["a"]})
        self.assertEqual(200, status)
        self.assertEqual(1024, StubUpstream.received["body"]["dimensions"])
        self.assertEqual(["a"], StubUpstream.received["body"]["input"])
        self.assertEqual([0.1, 0.2], payload["data"][0]["embedding"][:2])
        self.assertEqual(echo_vector(1024), payload["data"][0]["embedding"])

    def test_overrides_a_dimensions_value_from_the_caller(self):
        self.post({"model": "m", "input": ["a"], "dimensions": 4096})
        self.assertEqual(1024, StubUpstream.received["body"]["dimensions"])

    def test_injects_the_provider_preference(self):
        self.post({"model": "m", "input": ["a"]})
        self.assertEqual(
            {"only": ["nebius", "deepinfra"], "allow_fallbacks": True},
            StubUpstream.received["body"]["provider"],
        )

    def test_keeps_a_provider_preference_from_the_caller(self):
        self.post({"model": "m", "input": ["a"], "provider": {"only": ["nebius"]}})
        self.assertEqual(
            {"only": ["nebius"]}, StubUpstream.received["body"]["provider"]
        )

    def test_sends_no_provider_when_the_preference_is_off(self):
        proxy.PROVIDER = None
        self.post({"model": "m", "input": ["a"]})
        self.assertNotIn("provider", StubUpstream.received["body"])

    def test_relays_the_authorization_header(self):
        self.post({"model": "m", "input": ["a"]}, {"Authorization": "Bearer test-key"})
        self.assertEqual("Bearer test-key", StubUpstream.received["authorization"])

    def test_serves_only_the_embeddings_path(self):
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.server.server_port}/other", data=b"{}", method="POST"
        )
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=10)
        error.exception.close()
        self.assertEqual(404, error.exception.code)

    def test_serves_a_salted_embeddings_path(self):
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.server.server_port}/salty/v1/embeddings",
            data=json.dumps({"model": "m", "input": ["a"]}).encode(),
            method="POST",
        )
        request.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(request, timeout=10) as response:
            self.assertEqual(200, response.status)
        self.assertEqual(1024, StubUpstream.received["body"]["dimensions"])

    def test_serves_the_default_width_on_a_plain_path(self):
        status, payload = self.post({"model": "m", "input": ["a"]})
        self.assertEqual(200, status)
        self.assertEqual(1024, StubUpstream.received["body"]["dimensions"])
        self.assertEqual(1024, len(payload["data"][0]["embedding"]))

    def test_serves_the_default_width_on_a_salted_path(self):
        status, payload = self.post(
            {"model": "m", "input": ["a"]}, path="/salty/v1/embeddings"
        )
        self.assertEqual(200, status)
        self.assertEqual(1024, StubUpstream.received["body"]["dimensions"])
        self.assertEqual(1024, len(payload["data"][0]["embedding"]))

    def test_serves_the_width_from_the_path(self):
        status, payload = self.post(
            {"model": "m", "input": ["a"]}, path="/salty/384/v1/embeddings"
        )
        self.assertEqual(200, status)
        self.assertEqual(384, StubUpstream.received["body"]["dimensions"])
        self.assertEqual(384, len(payload["data"][0]["embedding"]))

    def test_serves_the_width_from_the_path_without_v1(self):
        status, payload = self.post(
            {"model": "m", "input": ["a"]}, path="/salty/384/embeddings"
        )
        self.assertEqual(200, status)
        self.assertEqual(384, StubUpstream.received["body"]["dimensions"])
        self.assertEqual(384, len(payload["data"][0]["embedding"]))

    def test_overrides_the_caller_width_on_a_width_path(self):
        self.post(
            {"model": "m", "input": ["a"], "dimensions": 4096},
            path="/salty/384/v1/embeddings",
        )
        self.assertEqual(384, StubUpstream.received["body"]["dimensions"])

    def test_refuses_a_width_that_is_not_numeric(self):
        status, payload = self.post_error(
            {"model": "m", "input": ["a"]}, "/salty/wide/v1/embeddings"
        )
        self.assertEqual(400, status)
        self.assertIn("digits", payload["error"]["message"])

    def test_refuses_a_width_outside_the_range(self):
        for path in ("/salty/0/v1/embeddings", "/salty/4097/v1/embeddings"):
            with self.subTest(path=path):
                status, payload = self.post_error(
                    {"model": "m", "input": ["a"]}, path
                )
                self.assertEqual(400, status)
                self.assertIn("1 and 4096", payload["error"]["message"])

    def test_refuses_three_path_parts(self):
        status, payload = self.post_error(
            {"model": "m", "input": ["a"]}, "/a/b/c/v1/embeddings"
        )
        self.assertEqual(400, status)
        self.assertIn("salt", payload["error"]["message"])

    def test_refuses_a_reply_of_the_wrong_width(self):
        StubUpstream.force_width = 7
        status, payload = self.post_error(
            {"model": "m", "input": ["a"]}, "/salty/384/v1/embeddings"
        )
        self.assertEqual(502, status)
        message = payload["error"]["message"]
        self.assertIn("384", message)
        self.assertIn("7", message)

    def test_relays_a_reply_of_the_expected_width(self):
        status, payload = self.post(
            {"model": "m", "input": ["a"]}, path="/salty/8/v1/embeddings"
        )
        self.assertEqual(200, status)
        self.assertEqual(8, len(payload["data"][0]["embedding"]))


class LoadProviderTest(unittest.TestCase):
    def test_default_preference_without_the_variable(self):
        self.assertEqual(
            {"only": ["nebius", "deepinfra"], "allow_fallbacks": True},
            proxy.load_provider(),
        )

    def test_empty_variable_turns_the_preference_off(self):
        with unittest.mock.patch.dict(os.environ, {"EMBEDDING_PROXY_PROVIDER": "  "}):
            self.assertIsNone(proxy.load_provider())

    def test_invalid_json_stops_the_script(self):
        with (
            unittest.mock.patch.dict(os.environ, {"EMBEDDING_PROXY_PROVIDER": "{oops"}),
            self.assertRaises(SystemExit),
        ):
            proxy.load_provider()

    def test_a_json_array_stops_the_script(self):
        with (
            unittest.mock.patch.dict(os.environ, {"EMBEDDING_PROXY_PROVIDER": "[1]"}),
            self.assertRaises(SystemExit),
        ):
            proxy.load_provider()


if __name__ == "__main__":
    unittest.main()
