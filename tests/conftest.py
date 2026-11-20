"""
Shared fixtures and test configuration for CCTV Manager Pro test suite.
"""

import os
import sys
import tempfile
import shutil
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi


@pytest.fixture
def temp_dir():
    """Provides a clean temporary directory for filesystem operations."""
    td = tempfile.mkdtemp(prefix="cctv_test_")
    yield td
    try:
        shutil.rmtree(td, ignore_errors=True)
    except Exception:
        pass


@pytest.fixture
def temp_db(temp_dir):
    """Provides an isolated DatabaseManager instance backed by a temporary file."""
    db_path = os.path.join(temp_dir, "test_cctv.db")
    db = DatabaseManager(db_path)
    db.initialize_db()
    yield db
    try:
        db.close()
    except Exception:
        pass


@pytest.fixture
def pdf_gen():
    """Provides a PDFGenerator instance pointing to project templates."""
    templates_dir = os.path.join(PROJECT_ROOT, "templates_pdf")
    return PDFGenerator(templates_dir=templates_dir)


@pytest.fixture
def api_bridge(temp_db, pdf_gen, monkeypatch):
    """Provides an initialized JsApi instance backed by isolated temp db with valid ephemeral Ed25519 test license."""
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import license_manager
    from license_manager import get_machine_id

    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode("ascii")
    monkeypatch.setattr(license_manager, "PUBLIC_KEY_B64", pub_b64)
    monkeypatch.setattr(license_manager.verify_license, "__defaults__", (pub_b64,))

    mid = get_machine_id()
    msg = f"{mid}:9999-12-31".encode("utf-8")
    sig_b32 = base64.b32encode(priv.sign(msg)).decode("ascii").rstrip("=")
    temp_db.save_license_key(f"99991231-{sig_b32}")
    return JsApi(db=temp_db, pdf_gen=pdf_gen)


@pytest.fixture
def sample_model():
    """Standard camera model metadata adhering to Algerian regulatory classification."""
    return {
        "model_name": "DS-2CD2143G2-I",
        "equipment_designation": "كاميرا مراقبة بصرية رقمية ثابتة",
        "equipment_nature": "كاميرا مراقبة داخلية / خارجية بدقة 4 ميغابكسل",
        "category": "الفئة الأولى",
        "sub_category": "الفرع أ"
    }


@pytest.fixture
def sample_client():
    """Full 29-field realistic Algerian client entity (Bilingual French/Arabic)."""
    return {
        "full_name": "محمد أمين بن علي",
        "father_name": "علي",
        "mother_name": "فاطمة الزهراء بوحيرد",
        "dob": "15/04/1985",
        "pob": "الجزائر الوسطى",
        "nationality": "جزائرية",
        "doc_number": "1198516020145236",
        "doc_issuer": "دائرة سيدي امحمد - ولاية الجزائر",
        "doc_issue_date": "10/05/2021",
        "address": "حي 500 مسكن، عمارة ج رقم 14",
        "city": "الجزائر",
        "phone": "0550123456",
        "email": "amine.benali@algerie-telecom.dz",
        "fax": "021654321",
        "profession": "مدير عام",
        "activity_type": "تجارة تجهيزات الأمن والحماية",
        "company_name": "SARL ATLAS SÉCURITÉ INDUSTRIELLE",
        "company_hq": "المنطقة الصناعية الرغاية، الجزائر",
        "position": "المسير الرئيسي",
        "accreditation_ref": "W16/AGR/2023/048",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري",
        "storage_location": "مستودع المنطقة اللوجستية رغاية",
        "security_conditions": "حراسة 24/24 مع نظام إنذار ضد السرقة والحريق",
        "shareholders": "محمد أمين بن علي (60%)، كريم بلقاسم (40%)",
        "passport_number": "219876543",
        "passport_issuer": "ولاية الجزائر",
        "passport_issue_date": "01/02/2022",
        "passport_expiry_date": "01/02/2032"
    }


@pytest.fixture
def sample_purchases(sample_model):
    """List of purchases for PDF generation."""
    return [
        {
            "model_name": sample_model["model_name"],
            "equipment_designation": sample_model["equipment_designation"],
            "equipment_nature": sample_model["equipment_nature"],
            "category": sample_model["category"],
            "sub_category": sample_model["sub_category"],
            "serial_number": f"DS2CD2143-2026-{i:04d}",
            "serial_id": i
        }
        for i in range(1, 6)
    ]
