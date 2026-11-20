import base64
import os
import sys
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

import license_manager
from license_manager import get_machine_id, verify_license


def test_ed25519_key_format_and_verification(monkeypatch):
    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode("ascii")

    mid = get_machine_id()
    test_cases = [
        (mid, "2027-10-30", True),
        ("1234-5678-9ABC-DEF0", "2026-12-31", False),
        (mid, "9999-12-31", True),
        ("9F8E-7D6C-5B4A-3210", "2028-05-15", False),
    ]

    for machine_id, expiry, expect_valid in test_cases:
        msg = f"{machine_id}:{expiry}".encode("utf-8")
        sig_b32 = base64.b32encode(priv.sign(msg)).decode("ascii").rstrip("=")
        key = f"{expiry.replace('-', '')}-{sig_b32}"
        assert len(key) == 112
        parts = key.split("-")
        assert len(parts[0]) == 8
        assert len(parts[1]) == 103

        valid, _ = verify_license(key, public_key_b64=pub_b64)
        assert valid is expect_valid


def test_cli_license_generator_if_present(monkeypatch, capsys):
    gen_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "license_generator.py"))
    priv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "private", "license_private.pem"))
    if not (os.path.exists(gen_path) and os.path.exists(priv_path)):
        pytest.skip("Private license generator or private key not present in public environment")

    from tools.license_generator import main as cli_main

    mid = get_machine_id()
    monkeypatch.setattr(sys, "argv", ["license_generator.py", "--machine-id", mid, "--expiry", "2027-10-30"])
    cli_main()
    captured = capsys.readouterr()
    assert "LICENSE KEY: 20271030-" in captured.out
    for line in captured.out.splitlines():
        if "LICENSE KEY:" in line:
            generated_key = line.split("LICENSE KEY:", 1)[1].strip()
            valid, info = verify_license(generated_key)
            assert valid is True
            assert info["expiry"] == "2027-10-30"
