import base64
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from license_manager import (
    get_machine_id,
    verify_license,
    check_clock_rollback,
)


def _ephemeral_keypair():
    priv = Ed25519PrivateKey.generate()
    pub_raw = priv.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return priv, base64.b64encode(pub_raw).decode("ascii")


def _sign_test_key(machine_id: str, expiry_date_str: str, priv: Ed25519PrivateKey) -> str:
    msg = f"{machine_id.strip().upper()}:{expiry_date_str.strip()}".encode("utf-8")
    sig_b32 = base64.b32encode(priv.sign(msg)).decode("ascii").rstrip("=")
    return f"{expiry_date_str.replace('-', '')}-{sig_b32}"


def test_machine_id_format():
    mid = get_machine_id()
    assert isinstance(mid, str)
    assert len(mid) == 19
    parts = mid.split("-")
    assert len(parts) == 4
    for part in parts:
        assert len(part) == 4
        assert part.isalnum()
        assert part == part.upper()


def test_valid_license_verification():
    priv, pub_b64 = _ephemeral_keypair()
    mid = get_machine_id()
    exp = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    key = _sign_test_key(mid, exp, priv)
    valid, info = verify_license(key, public_key_b64=pub_b64)
    assert valid is True
    assert isinstance(info, dict)
    assert info["expiry"] == exp
    assert info["machine_id"] == mid
    assert info["days_left"] >= 29
    assert info["is_lifetime"] is False


def test_wrong_signing_key_rejected():
    priv_other, _ = _ephemeral_keypair()
    _, pub_b64 = _ephemeral_keypair()
    mid = get_machine_id()
    exp = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    key = _sign_test_key(mid, exp, priv_other)
    valid, _ = verify_license(key, public_key_b64=pub_b64)
    assert valid is False


def test_mismatched_machine_id_rejected():
    priv, pub_b64 = _ephemeral_keypair()
    exp = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    fake_mid = "AAAA-BBBB-CCCC-DDDD"
    key = _sign_test_key(fake_mid, exp, priv)
    valid, err = verify_license(key, public_key_b64=pub_b64)
    assert valid is False
    assert "invalide" in str(err).lower() or "machine" in str(err).lower() or "جهاز" in str(err)


def test_expired_license_rejected():
    priv, pub_b64 = _ephemeral_keypair()
    mid = get_machine_id()
    exp = (datetime.date.today() - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    key = _sign_test_key(mid, exp, priv)
    valid, err = verify_license(key, public_key_b64=pub_b64)
    assert valid is False
    assert "expir" in str(err).lower() or "انتهت" in str(err)


def test_lifetime_license_valid():
    priv, pub_b64 = _ephemeral_keypair()
    mid = get_machine_id()
    key = _sign_test_key(mid, "9999-12-31", priv)
    valid, info = verify_license(key, public_key_b64=pub_b64)
    assert valid is True
    assert info["is_lifetime"] is True
    assert info["days_left"] > 36500


def test_malformed_keys():
    invalid_keys = [
        "",
        None,
        "INVALID-KEY",
        "202610-ABCD",
        "20261030-ABC",
        "20269999-" + ("A" * 103),
        "not-a-license-key-at-all",
    ]
    for k in invalid_keys:
        valid, _ = verify_license(k)
        assert valid is False


def test_clock_rollback_detected():
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    assert check_clock_rollback(tomorrow) is False

    today = datetime.date.today().strftime("%Y-%m-%d")
    assert check_clock_rollback(today) is True

    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    assert check_clock_rollback(yesterday) is True

    assert check_clock_rollback(None) is True
