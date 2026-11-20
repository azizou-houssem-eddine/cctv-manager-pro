# -*- coding: utf-8 -*-
"""
license_manager.py - Core Hardware-Bound Licensing Verifier for CCTV Manager Pro.
Binds installation to Windows MachineGuid (or fallback MAC address).
Verifies Ed25519-signed license keys (YYYYMMDD-<103-char Base32 signature>)
using only the embedded public verification key. Private signing keys never
reside in this module or in the repository.
Implements anti-clock rollback verification.
"""

import base64
import datetime
import hashlib
import uuid
from typing import Any, Dict, Tuple, Union

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

try:
    import winreg
except ImportError:
    winreg = None

# Ed25519 public verification key (safe to distribute in public source and binaries)
PUBLIC_KEY_B64 = "D5xZwSozO1nui2lHF7U92/ooNxANwPnVJsfddwIKAb0="
LIFETIME_DATES = {"9999-12-31", "2099-12-31"}
EXPECTED_SIG_B32_LEN = 103


def get_windows_machine_guid() -> Union[str, None]:
    """Retrieve unique Windows OS Cryptography MachineGuid from registry."""
    if not winreg:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            if guid:
                return str(guid).strip()
    except Exception:
        pass
    return None


def get_mac_address() -> str:
    """Fallback hardware identity from primary network card MAC address."""
    node = uuid.getnode()
    return f"{node:012X}"


def get_machine_id() -> str:
    """
    Computes a deterministic, human-readable 16-hex Machine ID:
    Format: XXXX-XXXX-XXXX-XXXX
    """
    guid = get_windows_machine_guid()
    if not guid:
        guid = get_mac_address()
    h = hashlib.sha256(guid.encode("utf-8")).hexdigest().upper()
    return f"{h[:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def _load_public_key(public_key_b64: str) -> Ed25519PublicKey:
    raw = base64.b64decode(public_key_b64)
    return Ed25519PublicKey.from_public_bytes(raw)


def verify_license(
    key_str: Union[str, None],
    public_key_b64: str = PUBLIC_KEY_B64,
) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Validates an Ed25519-signed license key against the current hardware Machine ID and expiration.
    Expected format: YYYYMMDD-<103 uppercase Base32 chars>.
    Returns:
        (True, payload_dict) if valid.
        (False, error_message) if invalid, expired, or mismatched.
    """
    if not key_str or not isinstance(key_str, str):
        return False, "La clé de licence est absente / مفتاح الترخيص مفقود"

    clean_key = key_str.strip().upper()
    parts = clean_key.split("-")
    if len(parts) != 2:
        return False, "Format de clé invalide. Attendu: YYYYMMDD-SIGNATURE"

    exp_compact, sig_part = parts
    if len(exp_compact) != 8 or len(sig_part) != EXPECTED_SIG_B32_LEN:
        return False, "Format de clé invalide (longueur incorrecte)"

    try:
        exp_year = int(exp_compact[:4])
        exp_month = int(exp_compact[4:6])
        exp_day = int(exp_compact[6:8])
        exp_date = datetime.date(exp_year, exp_month, exp_day)
        exp_str = exp_date.strftime("%Y-%m-%d")
    except ValueError:
        return False, "Date d'expiration invalide dans la clé de licence"

    try:
        sig_bytes = base64.b32decode(sig_part + "=", casefold=False)
        if len(sig_bytes) != 64:
            return False, "Format de signature invalide"
    except Exception:
        return False, "Format de signature invalide"

    current_mid = get_machine_id()
    msg = f"{current_mid}:{exp_str}".encode("utf-8")

    try:
        pub_key = _load_public_key(public_key_b64)
        pub_key.verify(sig_bytes, msg)
    except InvalidSignature:
        return False, "Signature de licence invalide pour cette machine / الترخيص غير متطابق مع هذا الجهاز"
    except Exception:
        return False, "Erreur de vérification de la licence / خطأ في التحقق من الترخيص"

    is_lifetime = exp_str in LIFETIME_DATES or exp_year >= 2099
    today = datetime.date.today()
    if not is_lifetime and today > exp_date:
        return False, f"La licence a expiré le {exp_str} / انتهت صلاحية الترخيص في {exp_str}"

    days_left = 99999 if is_lifetime else max(0, (exp_date - today).days)
    return True, {
        "valid": True,
        "expiry": exp_str,
        "machine_id": current_mid,
        "days_left": days_left,
        "is_lifetime": is_lifetime,
        "license_key": clean_key,
    }


def check_clock_rollback(last_run_str: Union[str, None]) -> bool:
    """
    Detects system time rollbacks.
    Returns False if system clock is set before the last recorded execution date.
    """
    if not last_run_str:
        return True
    try:
        last_run = datetime.datetime.strptime(str(last_run_str)[:10], "%Y-%m-%d").date()
        today = datetime.date.today()
        return today >= last_run
    except Exception:
        return True
