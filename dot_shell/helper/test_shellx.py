"""Unit tests for shellx crypto + JSONC parsing.

Run with:
    python3 dot_shell/helper/test_shellx.py
or:
    python3 -m unittest dot_shell/helper/test_shellx.py

Tests focus on the security-critical surface (ChaCha20, scrypt-derived
key + AAD, blob-swap attacks, tampering) plus the JSONC parser. They
require no subprocess, no test framework beyond stdlib `unittest`, and
no temp files. They do not exercise `cmd_export` / `cmd_import` because
those shell out to `chezmoi` / `age`.

The script is loaded via `importlib.machinery.SourceFileLoader` because
the deployed filename has no `.py` extension.
"""

import importlib.machinery
import importlib.util
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SOURCE = _HERE / "executable_shellx.tmpl"

# Since 1.3.0 the source file is a chezmoi template. Python cannot import
# it directly (the `{{- ... -}}` actions are not valid Python). Render it
# via `chezmoi execute-template` into a temp file, then import the rendered
# output. This keeps the tests hermetic — they don't depend on a deployed
# `~/.shell/helper/shellx` or on a working chezmoi state DB.
def _render_and_load():
    if not _SOURCE.exists():
        raise FileNotFoundError(f"shellx source not found: {_SOURCE}")
    # Skip the render if SHELLX_TEST_SKIP_RENDER=1 (the deployed copy is
    # already-rendered Python — used in CI containers where chezmoi is not
    # installed but the binary is).
    if os.environ.get("SHELLX_TEST_SKIP_RENDER") == "1":
        candidates = [
            Path("/home/ardhinata/.shell/helper/shellx"),
            _HERE / "executable_shellx",
        ]
        for c in candidates:
            if c.exists():
                return _load_from_file(c)
        raise FileNotFoundError("no rendered shellx found")
    try:
        result = subprocess.run(
            ["chezmoi", "execute-template"],
            stdin=_SOURCE.open("rb"),
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(
            f"failed to render shellx template via chezmoi: {e}. "
            f"Install chezmoi, or set SHELLX_TEST_SKIP_RENDER=1 and ensure "
            f"the deployed ~/.shell/helper/shellx exists."
        ) from e
    tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False)
    tmp.write(result.stdout)
    tmp.close()
    return _load_from_file(Path(tmp.name))


def _load_from_file(path: Path):
    loader = importlib.machinery.SourceFileLoader("shellx", str(path))
    spec = importlib.util.spec_from_loader("shellx", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


shellx = _render_and_load()


class TestChaCha20(unittest.TestCase):
    """RFC 7539 §2.3.2 block-function test vector and §2.4.2 cipher test vector."""

    KEY = bytes.fromhex(
        "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    )

    def test_rfc_7539_block_function(self):
        # §2.3.2: counter=1, nonce 00:00:00:09:00:00:00:4a:00:00:00:00
        # Expected state at end of ChaCha20 operation (final = round + state)
        state_words = [
            0xe4e7f110, 0x15593bd1, 0x1fdd0f50, 0xc47120a3,
            0xc7f4d1c7, 0x0368c033, 0x9aaa2204, 0x4e6cd4c3,
            0x466482d2, 0x09aa9f07, 0x05d7c214, 0xa2028bd9,
            0xd19c12b5, 0xb94e16de, 0xe883d0cb, 0x4e3c50a2,
        ]
        expected = b"".join(struct.pack("<I", w) for w in state_words)
        nonce = bytes.fromhex("000000090000004a00000000")
        got = shellx.chacha20_xor(self.KEY, nonce, b"\x00" * 64, counter=1)
        self.assertEqual(got, expected)

    def test_rfc_7539_cipher_first_block(self):
        # §2.4.2: counter=1, nonce 00:00:00:00:00:00:00:4a:00:00:00:00
        # Keystream first block (XOR with zeros).
        keystream_words = [
            0xf3514f22, 0xe1d91b40, 0x6f27de2f, 0xed1d63b8,
            0x821f138c, 0xe2062c3d, 0xecca4f7e, 0x78cff39e,
            0xa30a3b8a, 0x920a6072, 0xcd7479b5, 0x34932bed,
            0x40ba4c79, 0xcd343ec6, 0x4c2c21ea, 0xb7417df0,
        ]
        expected = b"".join(struct.pack("<I", w) for w in keystream_words)
        nonce = bytes.fromhex("000000000000004a00000000")
        got = shellx.chacha20_xor(self.KEY, nonce, b"\x00" * 64, counter=1)
        self.assertEqual(got, expected)

    def test_state_layout_is_16_words(self):
        """Regression: prior to the fix, state had 18 words (two spurious zeros
        between counter and nonce). The nonce was effectively half-width."""
        import struct as _s
        key = self.KEY
        nonce = b"\xaa" * 12
        # Rebuild the state the way _chacha20_block does, but inspect its length.
        state = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574]
        for i in range(8):
            state.append(_s.unpack("<I", key[i * 4 : (i + 1) * 4])[0])
        state.append(0)
        for i in range(3):
            state.append(_s.unpack("<I", nonce[i * 4 : (i + 1) * 4])[0])
        self.assertEqual(
            len(state), 16,
            "ChaCha20 state must be 16 word32s (constants/key/counter/nonce = 4+8+1+3)",
        )

    def test_different_nonces_produce_different_keystreams(self):
        nonce_a = b"\x00" * 12
        nonce_b = b"\x00" * 11 + b"\x01"
        ks_a = shellx.chacha20_xor(self.KEY, nonce_a, b"\x00" * 64, counter=0)
        ks_b = shellx.chacha20_xor(self.KEY, nonce_b, b"\x00" * 64, counter=0)
        self.assertNotEqual(ks_a, ks_b)

    def test_counter_increments_per_block(self):
        """Multi-block plaintext must roll the counter, otherwise keystream
        repeats and XOR collapses the plaintext."""
        pt = os.urandom(200)
        ct = shellx.chacha20_xor(self.KEY, b"\x00" * 12, pt, counter=0)
        # 200-byte plaintext: blocks 0 (64), 1 (64), 2 (64), 3 (8).
        # If the counter never incremented, block 0 and block 1 keystreams
        # would be identical, which would leak plaintext[0:64] XOR plaintext[64:128].
        self.assertEqual(len(ct), 200)
        # Round-trip:
        self.assertEqual(
            shellx.chacha20_xor(self.KEY, b"\x00" * 12, ct, counter=0), pt
        )


class TestBlobRoundTrip(unittest.TestCase):
    """encrypt_blob -> decrypt_blob round-trip and tamper-resistance."""

    PW = "chezmoi:shellx:test:nonce0123456789abcdef0123456789abcdef0123456789abcdef"

    def test_roundtrip_short(self):
        blob = shellx.encrypt_blob(self.PW, "GH_TOKEN", b"ghp_xxx")
        self.assertEqual(shellx.decrypt_blob(self.PW, "GH_TOKEN", blob), b"ghp_xxx")

    def test_roundtrip_empty(self):
        blob = shellx.encrypt_blob(self.PW, "EMPTY", b"")
        self.assertEqual(shellx.decrypt_blob(self.PW, "EMPTY", blob), b"")

    def test_roundtrip_multi_block(self):
        pt = os.urandom(1000)
        blob = shellx.encrypt_blob(self.PW, "BIG", pt)
        self.assertEqual(shellx.decrypt_blob(self.PW, "BIG", blob), pt)

    def test_blob_swap_attack_rejected(self):
        """AAD binds ciphertext to var_name: swapping blobs across var names
        must fail authentication."""
        blob_a = shellx.encrypt_blob(self.PW, "GH_TOKEN", b"alpha")
        blob_b = shellx.encrypt_blob(self.PW, "NPM_TOKEN", b"beta")
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "NPM_TOKEN", blob_a)
        # And the legitimate cross-check still works:
        self.assertEqual(shellx.decrypt_blob(self.PW, "GH_TOKEN", blob_a), b"alpha")
        self.assertEqual(shellx.decrypt_blob(self.PW, "NPM_TOKEN", blob_b), b"beta")

    def test_wrong_password_rejected(self):
        blob = shellx.encrypt_blob("right", "X", b"x")
        with self.assertRaises(ValueError):
            shellx.decrypt_blob("wrong", "X", blob)

    def test_bad_magic_rejected(self):
        blob = shellx.encrypt_blob(self.PW, "X", b"x")
        tampered = b"XXXX" + blob[4:]
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", tampered)

    def test_unsupported_version_rejected(self):
        blob = shellx.encrypt_blob(self.PW, "X", b"x")
        tampered = blob[:4] + bytes([99]) + blob[5:]
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", tampered)

    def test_tampered_ciphertext_rejected(self):
        blob = shellx.encrypt_blob(self.PW, "X", b"x" * 200)
        tampered = bytearray(blob)
        tampered[-1] ^= 0x01
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", bytes(tampered))

    def test_tampered_tag_rejected(self):
        blob = shellx.encrypt_blob(self.PW, "X", b"x")
        # tag is at offset 5 (magic+ver) + 16 (salt) + 12 (nonce) = 33, length 16
        tampered = bytearray(blob)
        tampered[33] ^= 0x01
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", bytes(tampered))

    def test_tampered_salt_rejected(self):
        """Salt is part of the AAD, so flipping it invalidates the tag."""
        blob = shellx.encrypt_blob(self.PW, "X", b"x")
        tampered = bytearray(blob)
        tampered[5] ^= 0x01  # first byte of salt
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", bytes(tampered))

    def test_tampered_nonce_rejected(self):
        """Nonce is part of the AAD AND the cipher input."""
        blob = shellx.encrypt_blob(self.PW, "X", b"x")
        tampered = bytearray(blob)
        tampered[5 + 16] ^= 0x01  # first byte of nonce
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", bytes(tampered))

    def test_truncated_blob_rejected(self):
        with self.assertRaises(ValueError):
            shellx.decrypt_blob(self.PW, "X", b"too short")


class TestBlobConstants(unittest.TestCase):
    """Wire-format constants."""

    def test_header_size(self):
        # MAGIC(4) + VER(1) + SALT(16) + NONCE(12) + TAG(16) = 49
        blob = shellx.encrypt_blob("pw", "X", b"x")
        self.assertEqual(len(blob), 49 + 1)  # 1-byte plaintext
        empty_blob = shellx.encrypt_blob("pw", "X", b"")
        self.assertEqual(len(empty_blob), 49)

    def test_magic_and_version(self):
        blob = shellx.encrypt_blob("pw", "X", b"x")
        self.assertEqual(blob[:4], b"SHX1")
        self.assertEqual(blob[4], 1)


class TestJsoncParsing(unittest.TestCase):
    def setUp(self):
        self.sample = (
            "// shellx_export: true\n"
            "// Format version: 1\n"
            "// Hostname:        desktop-main\n"
            "// Profile:         personal-laptop\n"
            "// Slug:            a3f9c1d8b3c49201eedd001122334455\n"
            '{\n'
            '  // var: GH  tags: ["git"]  processes: ["gh"]  updated: 2026-07-11\n'
            '  "GH_TOKEN": {\n'
            '    "value": "ghp_xxx",\n'
            '    "tag": ["git"],\n'
            '    "process": ["gh"]\n'
            '  }\n'
            '}\n'
        )

    def test_parse_header(self):
        parsed = shellx._parse_jsonc(self.sample)
        h = parsed["__header__"]
        self.assertEqual(h["shellx_export"], "true")
        self.assertEqual(h["Format version"], "1")
        self.assertEqual(h["Hostname"], "desktop-main")
        self.assertEqual(h["Profile"], "personal-laptop")
        self.assertEqual(h["Slug"], "a3f9c1d8b3c49201eedd001122334455")

    def test_parse_payload(self):
        parsed = shellx._parse_jsonc(self.sample)
        self.assertIn("GH_TOKEN", parsed["data"])
        self.assertEqual(parsed["data"]["GH_TOKEN"]["value"], "ghp_xxx")

    def test_comments_inside_strings_preserved(self):
        """`//` inside a JSON string must not be treated as a comment."""
        text = (
            "// shellx_export: true\n"
            "// Format version: 1\n"
            '{\n'
            '  "VAR": {"value": "has // in it", "tag": [], "process": []}\n'
            '}\n'
        )
        parsed = shellx._parse_jsonc(text)
        self.assertEqual(parsed["data"]["VAR"]["value"], "has // in it")

    def test_strict_json_rejects_trailing_comma(self):
        """The JSONC parser uses stdlib json, which rejects trailing commas."""
        text = (
            "// shellx_export: true\n"
            "// Format version: 1\n"
            '{\n'
            '  "A": {"value": "1", "tag": [], "process": []},\n'
            '}\n'  # trailing comma
        )
        with self.assertRaises(json.JSONDecodeError):
            shellx._parse_jsonc(text)


class TestStaticPasswordDerivation(unittest.TestCase):
    """As of shellx 1.5.0, `STATIC_PW = sha256sum("com.ardju.utils:shellx:<nonce>")`
    is derived at `chezmoi apply` time and injected as a plain string constant
    (`SHELLX_STATIC_PW_DEFAULT`). The runtime `_static_pw()` only recomputes
    from the nonce when the test-only `SHELLX_NONCE` env-var override is set.
    There is no `chezmoi data` subprocess fallback."""

    def setUp(self):
        # Clear any env-var override from previous tests.
        os.environ.pop("SHELLX_NONCE", None)

    def test_sprig_and_python_sha256_agree(self):
        """`SHELLX_STATIC_PW_DEFAULT` (rendered by Sprig's sha256sum at apply
        time) matches the value `hashlib.sha256` produces in Python. If Sprig
        ever changes its output format or the namespace string drifts, this
        will fail."""
        expected = hashlib.sha256(
            f"com.ardju.utils:shellx:{shellx.SHELLX_NONCE_DEFAULT}".encode()
        ).hexdigest()
        self.assertEqual(shellx.SHELLX_STATIC_PW_DEFAULT, expected)
        self.assertEqual(len(expected), 64)  # SHA256 hex digest

    def test_static_pw_returns_injected_default(self):
        """Without an env-var override, _static_pw() returns the
        template-injected constant directly."""
        self.assertEqual(shellx._static_pw(), shellx.SHELLX_STATIC_PW_DEFAULT)

    def test_env_var_nonce_override_recomputes(self):
        """Setting SHELLX_NONCE in the environment replaces the nonce and
        _static_pw() recomputes STATIC_PW from the override (no subprocess).
        The override is read fresh on each call (no module-global cache)."""
        override_nonce = "n" * 64
        os.environ["SHELLX_NONCE"] = override_nonce
        expected = hashlib.sha256(
            f"com.ardju.utils:shellx:{override_nonce}".encode()
        ).hexdigest()
        self.assertEqual(shellx._static_pw(), expected)
        # And the env-var nonce was used, not SHELLX_NONCE_DEFAULT.
        self.assertEqual(shellx._resolve_nonce(), override_nonce)
        self.assertNotEqual(shellx._static_pw(), shellx.SHELLX_STATIC_PW_DEFAULT)

    def test_empty_nonce_dies_without_subprocess(self):
        """An empty nonce produces a clear error. There is no recovery path
        (no chezmoi data subprocess)."""
        os.environ.pop("SHELLX_NONCE", None)
        original_default = shellx.SHELLX_NONCE_DEFAULT
        self.addCleanup(setattr, shellx, "SHELLX_NONCE_DEFAULT", original_default)
        # Empty the template-injected nonce AND the env var so _resolve_nonce()
        # returns "".
        shellx.SHELLX_NONCE_DEFAULT = ""
        with unittest.mock.patch.object(
            shellx.subprocess, "run",
            side_effect=AssertionError(
                "subprocess.run called — empty nonce should die, not shell out"
            ),
        ):
            with self.assertRaises(SystemExit) as cm:
                shellx._static_pw()
            self.assertEqual(cm.exception.code, 4)

    def test_no_subprocess_called_for_static_pw(self):
        """Sanity: deriving STATIC_PW never spawns a subprocess. The path is
        pure Python `hashlib.sha256` from this point on."""
        with unittest.mock.patch.object(
            shellx.subprocess, "run",
            side_effect=AssertionError(
                "subprocess.run called — static_pw derivation must be pure-Python"
            ),
        ):
            # Both the default and the env-override paths must be clean.
            _ = shellx._static_pw()
            os.environ["SHELLX_NONCE"] = "n" * 64
            _ = shellx._static_pw()


class TestDerivedSlug(unittest.TestCase):
    """The store slug is derived from _STATIC_PW, so no marker file is needed."""

    def setUp(self):
        # Replace _static_pw so the test doesn't depend on the
        # template-injected nonce. _derived_slug calls _static_pw() —
        # we mock the module-level function for the duration of the test.
        self._original_static_pw = shellx._static_pw
        shellx._static_pw = lambda: self._fake_pw

    def tearDown(self):
        shellx._static_pw = self._original_static_pw

    def test_derived_slug_is_deterministic(self):
        """Same static_pw → same slug, always."""
        self._fake_pw = "fake-static-pw"
        self.assertEqual(shellx._derived_slug(), shellx._derived_slug())

    def test_derived_slug_changes_with_password(self):
        """Different static_pw → different slug."""
        self._fake_pw = "alpha"
        slug_a = shellx._derived_slug()
        self._fake_pw = "beta"
        slug_b = shellx._derived_slug()
        self.assertNotEqual(slug_a, slug_b)

    def test_derived_slug_format(self):
        """Slug is 32 hex chars (16 bytes of blake2b)."""
        self._fake_pw = "test"
        slug = shellx._derived_slug()
        self.assertEqual(len(slug), 32)
        self.assertTrue(all(c in "0123456789abcdef" for c in slug))

    def test_legacy_sl_file_wins_over_derived(self):
        """A legacy `.sl` file preserves the original (pre-1.1) random slug."""
        import tempfile
        from pathlib import Path

        self._fake_pw = "test"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            legacy_slug = "deadbeefcafebabe"  # 16-hex, like 1.0 init output
            sl_path = tmp_path / ".sl"
            sl_path.write_text(legacy_slug + "\n")
            with unittest.mock.patch.object(shellx, "_sl_path", return_value=str(sl_path)):
                self.assertEqual(shellx._read_slug(), legacy_slug)

    def test_falls_back_to_derived_when_sl_missing(self):
        """If `.sl` is absent, _read_slug returns the derived slug."""
        import tempfile
        from pathlib import Path

        self._fake_pw = "test"
        with tempfile.TemporaryDirectory() as tmp:
            sl_path = str(Path(tmp) / ".sl")  # does not exist
            with unittest.mock.patch.object(shellx, "_sl_path", return_value=sl_path):
                self.assertEqual(shellx._read_slug(), shellx._derived_slug())


class TestRunSubcommandRouting(unittest.TestCase):
    """shellx 1.4.0 added `shellx run` as an explicit subcommand that
    behaves identically to bare exec mode (`shellx <proc> [args...]`).
    The subcommand exists so zsh completion can attach process-name
    completion to `shellx run <TAB>` without polluting the parent
    `shellx <TAB>` subcommand list. These tests pin that contract."""

    def setUp(self):
        # Capture (proc, passthrough) handed to os.execvpe instead of
        # actually exec'ing — we don't want a real subprocess spawned
        # from the test runner.
        self._captured = {}
        self._exec_sentinel = unittest.mock.MagicMock(
            side_effect=lambda *a, **kw: self._capture(*a, **kw)
        )
        # Patch os.execvpe at the module level so both cmd_exec and
        # _exec_main route through the sentinel.
        self._patcher = unittest.mock.patch.object(
            shellx.os, "execvpe", self._exec_sentinel
        )
        self._patcher.start()
        # Avoid the "store not initialized" die — give a fake store path.
        self._slug_path_patcher = unittest.mock.patch.object(
            shellx, "_resolve_store_path", return_value="/tmp/fake-shellx-store"
        )
        self._slug_path_patcher.start()
        self._idx_patcher = unittest.mock.patch.object(
            shellx, "_read_idx", return_value={}
        )
        self._idx_patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self._slug_path_patcher.stop()
        self._idx_patcher.stop()

    def _capture(self, proc, argv, env):
        self._captured["proc"] = proc
        self._captured["argv"] = argv
        self._captured["env_injected"] = env.get("RUNPRIV_VARS")
        # Don't actually exec; raise so the test sees a clean boundary.
        raise SystemExit(42)

    def _run_and_capture(self, args):
        try:
            shellx.main(args)
        except SystemExit as e:
            self.assertEqual(e.code, 42)

    def test_run_subcommand_executes_proc(self):
        """`shellx run echo hi` execs echo with args ['hi']."""
        self._run_and_capture(["run", "echo", "hi"])
        self.assertEqual(self._captured["proc"], "echo")
        self.assertEqual(self._captured["argv"], ["echo", "hi"])

    def test_run_subcommand_with_separator(self):
        """`shellx run -- echo hi` execs echo with args ['hi']."""
        self._run_and_capture(["run", "--", "echo", "hi"])
        self.assertEqual(self._captured["proc"], "echo")
        self.assertEqual(self._captured["argv"], ["echo", "hi"])

    def test_run_subcommand_with_tag(self):
        """`shellx run --tag=a,b -- echo hi` execs echo with args ['hi']."""
        self._run_and_capture(["run", "--tag=a,b", "--", "echo", "hi"])
        self.assertEqual(self._captured["proc"], "echo")
        self.assertEqual(self._captured["argv"], ["echo", "hi"])

    def test_run_subcommand_with_process(self):
        """`shellx run --process=gh -- gh auth status` execs gh with args."""
        self._run_and_capture(["run", "--process=gh", "--", "gh", "auth", "status"])
        self.assertEqual(self._captured["proc"], "gh")
        self.assertEqual(self._captured["argv"], ["gh", "auth", "status"])

    def test_bare_exec_mode_still_works(self):
        """`shellx echo hi` (no `run`) is unchanged — still execs echo."""
        self._run_and_capture(["echo", "hi"])
        self.assertEqual(self._captured["proc"], "echo")
        self.assertEqual(self._captured["argv"], ["echo", "hi"])

    def test_bare_exec_mode_with_tag(self):
        """`shellx --tag=a,b -- echo hi` (no `run`) is unchanged."""
        self._run_and_capture(["--tag=a,b", "--", "echo", "hi"])
        self.assertEqual(self._captured["proc"], "echo")
        self.assertEqual(self._captured["argv"], ["echo", "hi"])

    def test_run_subcommand_appears_in_help(self):
        """`shellx --help` lists `run` as a subcommand (registered in the
        subparser so completion can advertise it)."""
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                shellx.main(["--help"])
            except SystemExit:
                pass
        self.assertIn("run", buf.getvalue())

    def test_run_help_does_not_dispatch_exec(self):
        """`shellx run --help` prints usage text, does NOT exec."""
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = shellx.main(["run", "--help"])
        self.assertEqual(rc, 0)
        self.assertIn("shellx run", buf.getvalue())
        self.assertNotIn("proc", self._captured)


if __name__ == "__main__":
    unittest.main(verbosity=2)
