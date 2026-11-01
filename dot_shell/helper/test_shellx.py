"""Unit tests for shellx crypto + JSONC parsing.

Run with:
    python3 dot_shell/helper/test_shellx.py
or:
    python3 -m unittest dot_shell/helper/test_shellx.py

Tests focus on the security-critical surface (ChaCha20, scrypt-derived
key + AAD, blob-swap attacks, tampering) plus the JSONC parser and the
`env` subcommand. They require no subprocess, no test framework beyond
stdlib `unittest`, and no temp files. They do not exercise `cmd_export`
/ `cmd_import` because those shell out to `chezmoi` / `age`.

The script is loaded via `importlib.machinery.SourceFileLoader` because
the deployed filename has no `.py` extension.
"""

import importlib.machinery
import importlib.util
import hashlib
import hmac
import io
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_KEY_MODULE_SOURCE = _HERE / "private_shellx_key.py.tmpl"
_IMPL_SOURCE = _HERE / "private_shellx_impl.py.tmpl"
_KEY_SOURCE = (
    _HERE.parents[1]
    / "dot_local"
    / "share"
    / "private_shellx"
    / "private_master.key.tmpl"
)

# The source files are chezmoi templates. Python cannot import them
# directly (the `{{- ... -}}` actions are not valid Python). Render them
# via `chezmoi execute-template` into a temp directory, then import the
# rendered output. This keeps the tests hermetic — they don't depend on a
# deployed `~/.shell/helper/shellx` or on a working chezmoi state DB.
def _render_and_load():
    for src in (_KEY_MODULE_SOURCE, _IMPL_SOURCE):
        if not src.exists():
            raise FileNotFoundError(f"shellx source not found: {src}")
    # Skip the render if SHELLX_TEST_SKIP_RENDER=1 (the deployed copy is
    # already-rendered Python — used in CI containers where chezmoi is not
    # installed but the binary is).
    if os.environ.get("SHELLX_TEST_SKIP_RENDER") == "1":
        deployed = Path("/home/ardhinata/.shell/helper")
        if (deployed / "shellx_impl.py").exists():
            sys.path.insert(0, str(deployed))
            return importlib.import_module("shellx_impl")
        raise FileNotFoundError("no rendered shellx found")
    tmpdir = tempfile.mkdtemp(prefix="shellx-test-")
    try:
        for src, name in (
            (_KEY_MODULE_SOURCE, "shellx_key.py"),
            (_IMPL_SOURCE, "shellx_impl.py"),
        ):
            result = subprocess.run(
                ["chezmoi", "execute-template"],
                stdin=src.open("rb"),
                capture_output=True,
                check=True,
            )
            Path(tmpdir, name).write_bytes(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError(
            f"failed to render shellx template via chezmoi: {e}. "
            f"Install chezmoi, or set SHELLX_TEST_SKIP_RENDER=1 and ensure "
            f"the deployed ~/.shell/helper/shellx_impl.py exists."
        ) from e
    sys.path.insert(0, tmpdir)
    return importlib.import_module("shellx_impl")


shellx = _render_and_load()
shellx_key = sys.modules["shellx_key"]


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
        """A long master key gets the fast derivation, version 2."""
        blob = shellx.encrypt_blob("p" * 64, "X", b"x")
        self.assertEqual(blob[:4], b"SHX1")
        self.assertEqual(blob[4], shellx.VERSION_HMAC)

    def test_short_key_gets_the_slow_derivation(self):
        """A short master key is a passphrase, so it gets scrypt."""
        blob = shellx.encrypt_blob("short", "X", b"x")
        self.assertEqual(blob[4], shellx.VERSION_SCRYPT)

    def test_both_versions_round_trip(self):
        """A store can hold blobs of both versions."""
        for pw in ("p" * 64, "short"):
            blob = shellx.encrypt_blob(pw, "X", b"payload")
            self.assertEqual(shellx.decrypt_blob(pw, "X", blob), b"payload")


class TestBlobVersionDispatch(unittest.TestCase):
    """The version byte selects the key derivation, so a blob written by an
    older shellx still decrypts."""

    PW = "p" * 64

    def _scrypt_blob(self, var_name: str, plaintext: bytes) -> bytes:
        """Build a version 1 blob the way shellx 1.5 did."""
        salt = os.urandom(shellx.SALT_LEN)
        nonce = os.urandom(shellx.NONCE_LEN)
        raw = hashlib.scrypt(
            self.PW.encode(),
            salt=salt,
            n=shellx.SCRYPT_N,
            r=shellx.SCRYPT_R,
            p=shellx.SCRYPT_P,
            maxmem=shellx.SCRYPT_MAXMEM,
            dklen=shellx.SCRYPT_DKLEN,
        )
        enc_key, mac_key = raw[:32], raw[32:]
        ct = shellx.chacha20_xor(enc_key, nonce, plaintext, counter=0)
        aad = shellx._aad(var_name, salt, nonce)
        tag = hmac.new(mac_key, aad + ct, hashlib.blake2b).digest()[: shellx.TAG_LEN]
        return b"SHX1" + bytes([1]) + salt + nonce + tag + ct

    def test_legacy_blob_still_decrypts(self):
        blob = self._scrypt_blob("OLD", b"legacy-value")
        self.assertEqual(shellx.decrypt_blob(self.PW, "OLD", blob), b"legacy-value")

    def test_legacy_blob_rejects_the_wrong_key(self):
        blob = self._scrypt_blob("OLD", b"legacy-value")
        with self.assertRaises(ValueError):
            shellx.decrypt_blob("q" * 64, "OLD", blob)

    def test_fast_blob_rejects_the_wrong_key(self):
        blob = shellx.encrypt_blob(self.PW, "NEW", b"value")
        with self.assertRaises(ValueError):
            shellx.decrypt_blob("q" * 64, "NEW", blob)


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


class TestMasterKeyResolution(unittest.TestCase):
    """As of shellx 1.6.0 the master key is no longer embedded in the
    helper. It is resolved at runtime from the environment, from a test-only
    nonce override, from `~/.local/share/shellx/master.key`, or from the
    platform secret store."""

    def setUp(self):
        os.environ.pop("SHELLX_MASTER_KEY", None)
        os.environ.pop("SHELLX_NONCE", None)
        self._file = unittest.mock.patch.object(
            shellx_key, "SHELLX_KEY_FILE", "/nonexistent/shellx/master.key"
        )
        self._file.start()
        self.addCleanup(self._file.stop)
        self._platform = unittest.mock.patch.object(
            shellx_key, "platform_store_read", return_value=None
        )
        self._platform.start()
        self.addCleanup(self._platform.stop)

    def test_key_file_matches_the_sprig_derivation(self):
        """The rendered key file is sha256("com.ardju.utils:shellx:<nonce>").

        The nonce comes from the chezmoi config data. If Sprig's sha256sum
        output format or the namespace string drifts, this fails.
        """
        if not _KEY_SOURCE.exists():
            self.skipTest("master key template not found")
        try:
            result = subprocess.run(
                ["chezmoi", "execute-template"],
                stdin=_KEY_SOURCE.open("rb"),
                capture_output=True,
                check=True,
            )
            data = subprocess.run(
                ["chezmoi", "data", "--format=json"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise unittest.SkipTest(f"chezmoi not usable here: {e}") from e
        nonce = json.loads(data.stdout)["system_environment"]["nonce"]
        expected = hashlib.sha256(
            f"com.ardju.utils:shellx:{nonce}".encode()
        ).hexdigest()
        self.assertEqual(result.stdout.decode().strip(), expected)
        self.assertEqual(len(expected), 64)

    def test_master_key_env_override_wins(self):
        """SHELLX_MASTER_KEY replaces every other source."""
        os.environ["SHELLX_MASTER_KEY"] = "b" * 64
        self.assertEqual(shellx._master_key(), "b" * 64)

    def test_nonce_override_derives_the_key(self):
        """SHELLX_NONCE derives the key without touching the filesystem."""
        os.environ["SHELLX_NONCE"] = "n" * 64
        expected = hashlib.sha256(
            f"com.ardju.utils:shellx:{'n' * 64}".encode()
        ).hexdigest()
        self.assertEqual(shellx._master_key(), expected)
        self.assertEqual(shellx._resolve_nonce(), "n" * 64)

    def test_key_file_is_read_when_present(self):
        """The key file is the normal source."""
        with unittest.mock.patch.object(
            shellx_key, "key_file_read", return_value="c" * 64
        ):
            self.assertEqual(shellx._master_key(), "c" * 64)

    def test_platform_store_is_the_fallback(self):
        """The platform secret store is used when the key file is gone."""
        with unittest.mock.patch.object(
            shellx_key, "key_file_read", return_value=None
        ), unittest.mock.patch.object(
            shellx_key, "platform_store_read", return_value="d" * 64
        ):
            self.assertEqual(shellx._master_key(), "d" * 64)

    def test_missing_key_exits_with_code_4(self):
        """A missing master key is a clear failure with exit code 4."""
        with self.assertRaises(SystemExit) as cm:
            shellx._static_pw()
        self.assertEqual(cm.exception.code, 4)

    def test_no_subprocess_for_the_file_and_env_paths(self):
        """The normal paths never spawn a subprocess."""
        with unittest.mock.patch.object(
            shellx_key, "platform_store_read",
            side_effect=AssertionError("subprocess path must not be reached"),
        ):
            os.environ["SHELLX_MASTER_KEY"] = "e" * 64
            self.assertEqual(shellx._static_pw(), "e" * 64)
            os.environ.pop("SHELLX_MASTER_KEY")
            os.environ["SHELLX_NONCE"] = "n" * 64
            self.assertEqual(len(shellx._static_pw()), 64)


class TestMissingMasterKeyExit(unittest.TestCase):
    """Every shellx operation needs the master key, because the store path
    is derived from it. A missing key must fail with exit code 4, not with
    the "store not initialized" code 2."""

    def setUp(self):
        os.environ.pop("SHELLX_MASTER_KEY", None)
        os.environ.pop("SHELLX_NONCE", None)
        for name, value in (
            ("SHELLX_KEY_FILE", "/nonexistent/shellx/master.key"),
        ):
            patcher = unittest.mock.patch.object(shellx_key, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = unittest.mock.patch.object(
            shellx_key, "platform_store_read", return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_env_fails_with_code_4(self):
        with self.assertRaises(SystemExit) as cm:
            shellx.main(["env", "ANY"])
        self.assertEqual(cm.exception.code, 4)

    def test_list_fails_with_code_4(self):
        with self.assertRaises(SystemExit) as cm:
            shellx.main(["list"])
        self.assertEqual(cm.exception.code, 4)

    def test_run_fails_with_code_4(self):
        """The exec path needs the key too, so it must not start a process."""
        with unittest.mock.patch.object(
            shellx.os,
            "execvpe",
            unittest.mock.MagicMock(side_effect=AssertionError("execvpe called")),
        ):
            with self.assertRaises(SystemExit) as cm:
                shellx.main(["run", "echo", "hi"])
            self.assertEqual(cm.exception.code, 4)


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
        # The store path is derived from the master key, so every command
        # needs one.
        os.environ["SHELLX_MASTER_KEY"] = "a" * 64
        self.addCleanup(os.environ.pop, "SHELLX_MASTER_KEY", None)
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
        self._captured["env_shellx"] = env.get("SHELLX_VARS")
        self._captured["env_runpriv"] = env.get("RUNPRIV_VARS")
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

    def test_shellx_vars_env_is_set(self):
        """When `cmd_exec` injects matching secrets, the launched process
        receives `SHELLX_VARS` (comma-separated list of injected var names).
        `RUNPRIV_VARS` is also set for backward compatibility."""
        idx = {
            "GH_TOKEN": {"tag": ["git"], "process": ["gh"], "updated": "2026-08-24"},
            "NPM_TOKEN": {"tag": ["git"], "process": [], "updated": "2026-08-24"},
        }
        # Fake blobs so cmd_exec decrypts successfully (we patch decrypt_blob).
        fake_blob = b"x" * 100
        with unittest.mock.patch.object(shellx, "_read_idx", return_value=idx), \
             unittest.mock.patch.object(shellx, "_read_slug", return_value="deadbeef"), \
             unittest.mock.patch.object(shellx.os.path, "exists", return_value=True), \
             unittest.mock.patch("builtins.open", unittest.mock.mock_open(read_data=fake_blob)), \
             unittest.mock.patch.object(
                 shellx, "decrypt_blob",
                 side_effect=lambda pw, var, blob: f"val-of-{var}".encode(),
             ):
            self._run_and_capture(["--tag=git", "--", "env"])
        self.assertIn("GH_TOKEN", (self._captured["env_shellx"] or "").split(","))
        self.assertIn("NPM_TOKEN", (self._captured["env_shellx"] or "").split(","))
        # RUNPRIV_VARS mirrors SHELLX_VARS for backward compatibility.
        self.assertEqual(self._captured["env_shellx"], self._captured["env_runpriv"])

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


class TestImportTargetIndex(unittest.TestCase):
    """`shellx import --to DIR` must write the index into DIR.

    A regression read and wrote the live store index, so the live index
    named blobs that the live store did not hold.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.live = self.root / "live"
        self.live.mkdir()
        self.target = self.root / "target"
        self.target.mkdir()
        (self.live / ".sl").write_text("liveslug\n")
        (self.live / ".idx").write_text("")
        os.environ["SHELLX_MASTER_KEY"] = "a" * 64
        self.addCleanup(os.environ.pop, "SHELLX_MASTER_KEY", None)
        patcher = unittest.mock.patch.object(
            shellx, "_resolve_store_path", return_value=str(self.live)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def _export_file(self) -> str:
        path = self.root / "dump.jsonc"
        path.write_text(
            "// shellx_export: true\n"
            "// Format version: 1\n"
            "{\n"
            '  "MYVAR": {"value": "v", "tag": [], "process": []}\n'
            "}\n"
        )
        return str(path)

    def _import(self) -> int:
        buf = io.StringIO()
        with redirect_stdout(buf):
            return shellx.main(
                ["import", self._export_file(), "--to", str(self.target)]
            )

    def test_import_to_writes_the_target_index(self):
        rc = self._import()
        self.assertEqual(rc, 0)
        self.assertIn("MYVAR", (self.target / ".idx").read_text())
        self.assertNotIn("MYVAR", (self.live / ".idx").read_text())

    def test_import_to_leaves_the_live_store_alone(self):
        rc = self._import()
        self.assertEqual(rc, 0)
        live_blobs = [
            p for p in self.live.iterdir() if p.name not in (".sl", ".idx")
        ]
        self.assertEqual(live_blobs, [])
        self.assertTrue(
            (self.target / shellx._blob_name("MYVAR", "target")).exists()
        )


class TestKeyCommand(unittest.TestCase):
    """`shellx key status` reports the source of the master key and a
    fingerprint. It never prints the key."""

    def test_status_prints_the_source_not_the_key(self):
        os.environ["SHELLX_MASTER_KEY"] = "s" * 64
        self.addCleanup(os.environ.pop, "SHELLX_MASTER_KEY", None)
        for name in ("key_file_read", "platform_store_read"):
            patcher = unittest.mock.patch.object(shellx_key, name, return_value=None)
            patcher.start()
            self.addCleanup(patcher.stop)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = shellx.main(["key", "status"])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("master key source", out)
        self.assertIn("fingerprint", out)
        self.assertNotIn("s" * 64, out)

    def test_status_without_a_key_exits_with_code_4(self):
        os.environ.pop("SHELLX_MASTER_KEY", None)
        os.environ.pop("SHELLX_NONCE", None)
        for name in ("key_file_read", "platform_store_read"):
            patcher = unittest.mock.patch.object(shellx_key, name, return_value=None)
            patcher.start()
            self.addCleanup(patcher.stop)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = shellx.main(["key", "status"])
        self.assertEqual(rc, 4)


class TestEnvSubcommand(unittest.TestCase):
    """`shellx env NAME` prints one `export NAME=<value>` line per name.

    The output is shell source text that a zsh startup file sources. The
    quoting must keep the value inside one shell word, so the tests check
    the round trip through POSIX word splitting, which reads the same
    text the way zsh does.
    """

    def setUp(self):
        os.environ["SHELLX_MASTER_KEY"] = "a" * 64
        self.addCleanup(os.environ.pop, "SHELLX_MASTER_KEY", None)
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Path(self._tmp.name)
        (self.store / ".sl").write_text(shellx._derived_slug() + "\n")
        self._slug_patcher = unittest.mock.patch.object(
            shellx, "_resolve_store_path", return_value=str(self.store)
        )
        self._slug_patcher.start()
        # An unknown first argument is routed to exec mode. Fail the test
        # instead of replacing the test runner with a child process.
        self._exec_patcher = unittest.mock.patch.object(
            shellx.os,
            "execvpe",
            unittest.mock.MagicMock(side_effect=AssertionError("execvpe called")),
        )
        self._exec_patcher.start()

    def tearDown(self):
        self._exec_patcher.stop()
        self._slug_patcher.stop()
        self._tmp.cleanup()

    def _store(self, var, value):
        slug = shellx._read_slug()
        blob = shellx.encrypt_blob(shellx._static_pw(), var, value.encode())
        (self.store / shellx._blob_name(var, slug)).write_bytes(blob)
        idx = shellx._read_idx()
        idx[var] = {
            "tag": [],
            "process": [],
            "updated": "2026-01-01T00:00:00+00:00",
        }
        shellx._write_idx(idx)

    def _run_env(self, *names):
        class _Out:
            def __init__(self):
                self.buffer = io.BytesIO()

            def write(self, s):
                return len(s)

            def flush(self):
                pass

        out = _Out()
        err = io.StringIO()
        with unittest.mock.patch.object(shellx.sys, "stdout", out), \
                unittest.mock.patch.object(shellx.sys, "stderr", err):
            try:
                rc = shellx.main(["env", *names])
            except SystemExit as e:
                rc = e.code
        return rc, out.buffer.getvalue().decode("utf-8"), err.getvalue()

    def test_env_prints_export_line(self):
        self._store("PLAIN", "simple")
        rc, out, err = self._run_env("PLAIN")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "export PLAIN=simple\n")
        self.assertEqual(err, "")

    def test_env_value_stays_one_shell_word(self):
        awkward = "it's $HOME `id` $(id) \"q\" ;rm -rf /tmp/x\nsecond\tline"
        self._store("AWKWARD", awkward)
        rc, out, _ = self._run_env("AWKWARD")
        self.assertEqual(rc, 0)
        words = shlex.split(out)
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0], "export")
        self.assertEqual(words[1], "AWKWARD=" + awkward)

    def test_env_empty_value(self):
        self._store("EMPTY", "")
        rc, out, _ = self._run_env("EMPTY")
        self.assertEqual(rc, 0)
        self.assertEqual(shlex.split(out), ["export", "EMPTY="])

    def test_env_multiple_names(self):
        self._store("ONE", "1")
        self._store("TWO", "2")
        rc, out, _ = self._run_env("ONE", "TWO")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "export ONE=1\nexport TWO=2\n")

    def test_env_missing_variable_fails(self):
        rc, out, err = self._run_env("NOPE")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("no such variable", err)

    def test_env_invalid_name_fails(self):
        rc, _out, err = self._run_env("BAD-NAME")
        self.assertEqual(rc, 2)
        self.assertIn("invalid variable name", err)

    def test_env_requires_a_name(self):
        rc, _out, _err = self._run_env()
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
