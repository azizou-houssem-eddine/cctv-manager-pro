import os
import shutil
import pytest
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi
from seed_data import seed_database

@pytest.fixture
def clean_test_env(tmp_path, monkeypatch):
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import license_manager

    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode("ascii")
    monkeypatch.setattr(license_manager, "PUBLIC_KEY_B64", pub_b64)
    monkeypatch.setattr(license_manager.verify_license, "__defaults__", (pub_b64,))

    db_file = str(tmp_path / "test_cctv.db")
    custom_dossiers = str(tmp_path / "Custom_Clients_Directory")
    db = DatabaseManager(db_file)
    db.initialize_db()
    mid = license_manager.get_machine_id()
    sig_b32 = base64.b32encode(priv.sign(f"{mid}:9999-12-31".encode("utf-8"))).decode("ascii").rstrip("=")
    db.save_license_key(f"99991231-{sig_b32}")
    pdf_gen = PDFGenerator("templates_pdf")
    api = JsApi(db, pdf_gen)
    return {
        "db": db,
        "pdf_gen": pdf_gen,
        "api": api,
        "tmp_path": tmp_path,
        "custom_dossiers": custom_dossiers
    }

def test_dossier_root_dir_persistence(clean_test_env):
    """Test getting and setting custom dossier root directory."""
    db = clean_test_env["db"]
    api = clean_test_env["api"]
    custom_dir = clean_test_env["custom_dossiers"]

    # Initial default
    default_dir = db.get_dossier_root_dir()
    assert os.path.isabs(default_dir)
    assert os.path.exists(default_dir)

    # Change through API
    res_set = api.set_dossier_root_dir(custom_dir)
    assert res_set["success"] is True
    assert res_set["path"] == os.path.abspath(custom_dir)
    assert os.path.exists(custom_dir)

    # Verify getter returns updated path
    res_get = api.get_dossier_root_dir()
    assert res_get["success"] is True
    assert res_get["path"] == os.path.abspath(custom_dir)

    # Empty path validation
    res_err = api.set_dossier_root_dir("")
    assert res_err["success"] is False
    assert "error" in res_err

def test_client_folder_structure_specification(clean_test_env):
    """
    Verify client folder structure matches user exact requirement:
    <User-Selected Root>/<Client Full Name>/1er dossier/
    <User-Selected Root>/<Client Full Name>/2eme dossier/
    """
    db = clean_test_env["db"]
    api = clean_test_env["api"]
    custom_root = clean_test_env["custom_dossiers"]
    api.set_dossier_root_dir(custom_root)

    # Add model & serials
    mid = db.add_camera_model("Hikvision DS-2CD2143G2-I", "كاميرا مراقبة خارجية", "Dome 4MP", "القسم أ", "الفرع 1", 5)
    db.save_serial_batch(mid, ["TEST-SN-1001", "TEST-SN-1002"])

    # Register client with full name
    client_name = "Ahmed Karim Mansouri"
    cid = db.add_client({
        "full_name": client_name,
        "doc_number": "ID-ALG-998877",
        "phone": "0550112233",
        "city": "الجزائر"
    })

    # Assign camera
    avail = db.get_available_serials(mid)
    db.assign_cameras_batch(cid, [avail[0]["id"]])

    # Generate dossier
    res_dossier = api.generate_client_dossier(cid)
    assert res_dossier["success"] is True

    # Check client directory structure on disk
    client_folder = os.path.join(custom_root, client_name)
    dossier_1 = os.path.join(client_folder, "1er dossier")
    dossier_2 = os.path.join(client_folder, "2eme dossier")

    assert os.path.isdir(client_folder), f"Expected client folder at {client_folder}"
    assert os.path.isdir(dossier_1), f"Expected 1er dossier at {dossier_1}"
    assert os.path.isdir(dossier_2), f"Expected 2eme dossier at {dossier_2}"

    # Verify generated PDF files inside 1er dossier
    assert os.path.isfile(os.path.join(dossier_1, "annex1.pdf"))
    assert os.path.isfile(os.path.join(dossier_1, "annex5.pdf"))
    assert os.path.isfile(os.path.join(dossier_1, "pv_reception.pdf"))

def test_seed_database_execution(clean_test_env):
    """Verify seed_database populates rich realistic data and generates dossiers."""
    db = clean_test_env["db"]
    pdf_gen = clean_test_env["pdf_gen"]
    custom_root = clean_test_env["custom_dossiers"]
    db.set_dossier_root_dir(custom_root)

    res = seed_database(db, pdf_gen)
    assert res["success"] is True
    assert len(db.get_camera_models()) >= 8
    assert len(db.get_clients()) >= 7
    assert len(db.get_all_serials()) >= 100
    assert res["assignments_made"] > 0
    assert len(res["dossiers_generated"]) >= 2

    # Check that dossiers were generated inside custom root
    for d_info in res["dossiers_generated"]:
        cname = d_info["client"]
        c_folder = os.path.join(custom_root, cname)
        assert os.path.isdir(os.path.join(c_folder, "1er dossier"))
        assert os.path.isdir(os.path.join(c_folder, "2eme dossier"))
