import base64
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

import license_manager
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi
from license_manager import get_machine_id


def _sign_test_key(machine_id: str, expiry_date_str: str, priv: Ed25519PrivateKey) -> str:
    msg = f"{machine_id.strip().upper()}:{expiry_date_str.strip()}".encode("utf-8")
    sig_b32 = base64.b32encode(priv.sign(msg)).decode("ascii").rstrip("=")
    return f"{expiry_date_str.replace('-', '')}-{sig_b32}"


@pytest.fixture
def clean_api(tmp_path, monkeypatch):
    priv = Ed25519PrivateKey.generate()
    pub_raw = priv.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    pub_b64 = base64.b64encode(pub_raw).decode("ascii")
    monkeypatch.setattr(license_manager, "PUBLIC_KEY_B64", pub_b64)
    # Also update default arg binding on verify_license.__defaults__
    monkeypatch.setattr(license_manager.verify_license, "__defaults__", (pub_b64,))

    db_file = str(tmp_path / "test_cctv.db")
    db = DatabaseManager(db_file)
    db.initialize_db()
    pdf_gen = PDFGenerator("templates_pdf")
    api = JsApi(db, pdf_gen)
    return api, db, priv


def test_initial_system_status(clean_api):
    api, _, _ = clean_api
    status = api.get_system_init_status()
    assert status["success"] is True
    assert status["license"]["valid"] is False
    assert status["onboarding_completed"] is False
    assert "machine_id" in status["license"]


def test_activate_license_success(clean_api):
    api, _, priv = clean_api
    mid = get_machine_id()
    exp = (datetime.date.today() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    key = _sign_test_key(mid, exp, priv)

    res = api.activate_license(key)
    assert res["success"] is True
    assert res["license"]["valid"] is True
    assert res["license"]["days_left"] >= 89

    status = api.get_system_init_status()
    assert status["license"]["valid"] is True
    assert status["license"]["license_key"] == key


def test_activate_license_invalid_key(clean_api):
    api, _, _ = clean_api
    res = api.activate_license("INVALID-KEY-1234")
    assert res["success"] is False
    assert "error" in res


def test_complete_onboarding(clean_api):
    api, db, _ = clean_api
    assert db.get_onboarding_status() is False

    res = api.complete_onboarding({
        "installer_profile": {
            "installer_company_name": "Test CCTV SARL",
            "installer_name": "Karim Installer",
            "installer_phone": "0555000000",
            "installer_city": "Alger",
            "installer_accreditation_ref": "123/2026",
            "installer_accreditation_date": "2026-01-01",
            "agreement_doc_b64": "data:application/pdf;base64,JVBERi0xLjQK",
            "agreement_doc_name": "agrement_officiel.pdf",
            "seal_image_b64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
            "signature_image_b64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg==",
        },
        "dossier_root": "test_dossiers",
        "seed_demo": False,
    })
    assert res["success"] is True
    assert db.get_onboarding_status() is True
    prof = db.get_installer_profile()
    assert prof["agreement_doc_b64"] == "data:application/pdf;base64,JVBERi0xLjQK"
    assert prof["agreement_doc_name"] == "agrement_officiel.pdf"
    assert prof["seal_image_b64"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="
    assert prof["signature_image_b64"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="


def test_unlicensed_pdf_gate_enforcement(clean_api):
    api, _, _ = clean_api
    res = api.generate_client_dossier(1)
    assert res["success"] is False
    assert res.get("license_required") is True
