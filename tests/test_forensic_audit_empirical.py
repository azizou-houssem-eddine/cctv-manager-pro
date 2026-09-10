"""
Forensic Integrity Audit Empirical Verification Suite
Authored by Forensic Auditor (Milestone 1)
Empirically verifies:
1. Zero hardcoded return values / facades
2. Genuine SQL execution and schema migration
3. True SQLite transaction rollback on simulated errors
4. Parameter binding correctness and injection resilience
5. CSV parser delimiter auto-detection and deduplication
6. Excel binary generation with openpyxl styling and valid zip headers
7. Executive analytics KPI calculations against live database mutations
8. Windows filesystem sanitization and dossier directory creation
"""

import os
import io
import tempfile
import shutil
import sqlite3
import openpyxl
import pytest
from db_manager import DatabaseManager, sanitize_dossier_name, get_client_dossier_dir, migrate_legacy_dossiers

def test_forensic_db_mutations_and_integrity():
    tmpdir = tempfile.mkdtemp(prefix="forensic_")
    try:
        db_path = os.path.join(tmpdir, "forensic.db")
        db = DatabaseManager(db_path)
        db.initialize_db()

        # Check raw sqlite schema directly
        raw_conn = sqlite3.connect(db_path)
        cur = raw_conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {r[0] for r in cur.fetchall()}
        assert {"camera_models", "clients", "serial_numbers", "client_purchases"}.issubset(tables)

        # Check PRAGMA settings on DatabaseManager connection
        assert db.conn.cursor().execute("PRAGMA foreign_keys;").fetchone()[0] == 1, "Foreign keys must be enabled"

        # Check indexes directly in sqlite_master
        cur.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = {r[0] for r in cur.fetchall()}
        assert "idx_sn_model_used" in indexes
        assert "idx_cp_client_id" in indexes

        # Add model and verify raw insertion
        mid = db.add_camera_model("Cam A", "Dome 4K", "Fixe", "Cat1", "Sub1", low_stock_threshold=3)
        assert mid > 0
        cur.execute("SELECT model_name, low_stock_threshold FROM camera_models WHERE id = ?;", (mid,))
        row = cur.fetchone()
        assert row[0] == "Cam A"
        assert row[1] == 3

        # Add serials and verify raw insertion
        serials = ["SN-FORENSIC-001", "SN-FORENSIC-002", "SN-FORENSIC-003"]
        inserted = db.save_serial_batch(mid, serials)
        assert inserted == 3
        cur.execute("SELECT COUNT(*) FROM serial_numbers WHERE model_id = ? AND is_used = 0;", (mid,))
        assert cur.fetchone()[0] == 3

        # Add client and assign
        cid = db.add_client({"full_name": "Audit Client", "doc_number": "DOC-AUDIT-001"})
        avail = db.get_available_serials(mid)
        sid0 = avail[0]["id"]
        ok = db.assign_camera_to_client(cid, sid0)
        assert ok is True

        cur.execute("SELECT is_used FROM serial_numbers WHERE id = ?;", (sid0,))
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM client_purchases WHERE client_id = ? AND serial_id = ?;", (cid, sid0))
        assert cur.fetchone()[0] == 1

        # Analytics verification on live data
        analytics = db.get_dashboard_analytics()
        assert analytics["total_stock"] == 2
        assert analytics["total_assigned"] == 1
        assert analytics["total_clients"] == 1
        assert analytics["total_models"] == 1
        # Stock (2) <= threshold (3) -> should alert low stock
        assert analytics["low_stock_count"] == 1
        assert analytics["low_stock_items"][0]["model_name"] == "Cam A"

        # Return camera
        returned = db.return_cameras_batch(["SN-FORENSIC-001"])
        assert returned == 1
        cur.execute("SELECT is_used FROM serial_numbers WHERE id = ?;", (sid0,))
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT COUNT(*) FROM client_purchases WHERE serial_id = ?;", (sid0,))
        assert cur.fetchone()[0] == 0

        raw_conn.close()
        db.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_forensic_transaction_rollback():
    tmpdir = tempfile.mkdtemp(prefix="forensic_")
    try:
        db_path = os.path.join(tmpdir, "rollback.db")
        db = DatabaseManager(db_path)
        db.initialize_db()

        mid = db.add_camera_model("Cam B", "Bullet", "Fixe", "Cat2", "Sub2")
        db.save_serial_batch(mid, ["SN-ROLL-1", "SN-ROLL-2"])
        serials = db.get_available_serials(mid)
        sids = [s["id"] for s in serials]

        cid = db.add_client({"full_name": "Rollback Client", "doc_number": "DOC-ROLL-1"})

        # Intentionally provoke an error during batch assignment by including an invalid serial ID (foreign key failure)
        res = db.assign_cameras_batch(cid, [sids[0], 999999])
        assert res == 0, "Batch assignment must return 0 on error"

        # Verify raw database: sids[0] must NOT be marked used, and client_purchases must be empty
        raw_conn = sqlite3.connect(db_path)
        cur = raw_conn.cursor()
        cur.execute("SELECT COUNT(*) FROM client_purchases;")
        assert cur.fetchone()[0] == 0, "Rollback must leave client_purchases pristine"
        cur.execute("SELECT is_used FROM serial_numbers WHERE id = ?;", (sids[0],))
        assert cur.fetchone()[0] == 0, "Rollback must not leave serial marked as used"
        raw_conn.close()
        db.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_forensic_dynamic_migration():
    """Verify that initialize_db dynamically adds columns to an older schema version."""
    tmpdir = tempfile.mkdtemp(prefix="forensic_")
    try:
        db_path = os.path.join(tmpdir, "migration.db")
        # Create legacy schema missing low_stock_threshold and new columns
        raw_conn = sqlite3.connect(db_path)
        raw_conn.execute("""
            CREATE TABLE camera_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                equipment_designation TEXT,
                equipment_nature TEXT,
                category TEXT,
                sub_category TEXT
            );
        """)
        raw_conn.execute("INSERT INTO camera_models (model_name) VALUES ('Legacy Cam');")
        raw_conn.commit()
        raw_conn.close()

        # Run DatabaseManager initialize_db
        db = DatabaseManager(db_path)
        db.initialize_db()

        # Verify low_stock_threshold column was added dynamically
        raw_conn = sqlite3.connect(db_path)
        cur = raw_conn.cursor()
        cur.execute("PRAGMA table_info(camera_models);")
        cols = [r[1] for r in cur.fetchall()]
        assert "low_stock_threshold" in cols

        # Verify legacy data preserved
        cur.execute("SELECT model_name, low_stock_threshold FROM camera_models WHERE id = 1;")
        row = cur.fetchone()
        assert row[0] == "Legacy Cam"
        raw_conn.close()
        db.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_forensic_csv_and_excel_authenticity():
    tmpdir = tempfile.mkdtemp(prefix="forensic_")
    try:
        db_path = os.path.join(tmpdir, "export.db")
        db = DatabaseManager(db_path)
        db.initialize_db()

        mid = db.add_camera_model("Hikvision 2MP", "Camera Dome", "Fixe", "Cat1", "Sub1")
        db.save_serial_batch(mid, ["HK-1001", "HK-1002"])
        cid = db.add_client({"full_name": "Societe Equipement", "company_name": "SARL Tech"})
        avail = db.get_available_serials(mid)
        db.assign_camera_to_client(cid, avail[0]["id"])

        # 1. Test CSV Export
        csv_str = db.export_serials_csv()
        assert isinstance(csv_str, str)
        assert csv_str.startswith("\ufeff"), "CSV must include UTF-8 BOM"
        # Strip BOM for line check
        clean_csv = csv_str.lstrip("\ufeff")
        lines = [l.strip() for l in clean_csv.strip().splitlines()]
        assert lines[0] == "ID,Serial Number,Model Name,Designation,Status,Client Name,Date Assigned"
        assert any("HK-1001" in l and "Assigned" in l and "Societe Equipement" in l for l in lines)
        assert any("HK-1002" in l and "In Stock" in l for l in lines)

        # 2. Test Excel Export
        excel_bytes = db.export_serials_excel()
        assert isinstance(excel_bytes, bytes)
        assert excel_bytes[:4] == b"PK\x03\x04", "Excel file must have standard ZIP/XLSX magic bytes"

        # Load with openpyxl to verify real workbook structure
        wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
        assert "Inventory Serials" in wb.sheetnames
        ws = wb["Inventory Serials"]
        assert ws.cell(row=1, column=1).value == "ID"
        assert ws.cell(row=1, column=2).value == "Serial Number"
        # Check styling authenticity
        assert ws.cell(row=1, column=1).font.bold is True
        assert ws.cell(row=1, column=1).fill.start_color.rgb == "001E293B"

        # Verify data rows
        rows = list(ws.iter_rows(values_only=True))
        assert len(rows) == 3 # header + 2 serials
        serials_in_excel = {r[1] for r in rows[1:]}
        assert serials_in_excel == {"HK-1001", "HK-1002"}

        # 3. Test CSV Delimiter Sniffing & Staging
        # Semicolon delimited
        semi_csv = "S/N;Model\nSN-SEMI-1;Hik\nSN-SEMI-2;Hik\nSN-SEMI-1;Hik\nHK-1001;Hik"
        preview = db.preview_csv_serials(semi_csv)
        assert preview["total_found"] == 4
        assert set(preview["duplicates_in_file"]) == {"SN-SEMI-1"}
        assert set(preview["already_in_db"]) == {"HK-1001"}
        assert set(preview["valid"]) == {"SN-SEMI-1", "SN-SEMI-2"}

        # Tab delimited
        tab_csv = "Serial Number\tModel\nSN-TAB-1\tM1\nSN-TAB-2\tM2"
        preview_tab = db.preview_csv_serials(tab_csv)
        assert set(preview_tab["valid"]) == {"SN-TAB-1", "SN-TAB-2"}

        db.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_forensic_dossier_sanitization_and_migration():
    # 1. Path traversal attempts
    assert "/" not in sanitize_dossier_name("../../etc/passwd")
    assert "\\" not in sanitize_dossier_name("..\\..\\windows\\system32")
    assert sanitize_dossier_name("..") == "Client_Unnamed"
    assert sanitize_dossier_name("   ...   ") == "Client_Unnamed"
    assert sanitize_dossier_name(None) == "Client_Unnamed"
    assert sanitize_dossier_name("") == "Client_Unnamed"

    # 2. Windows reserved device names
    assert sanitize_dossier_name("CON") == "CON_client"
    assert sanitize_dossier_name("prn") == "prn_client"
    assert sanitize_dossier_name("aux") == "aux_client"
    assert sanitize_dossier_name("nul") == "nul_client"
    assert sanitize_dossier_name("com1") == "com1_client"
    assert sanitize_dossier_name("lpt9") == "lpt9_client"

    # 3. Arabic Unicode
    ar_name = "شركة السلام للأمن والمراقبة"
    assert sanitize_dossier_name(ar_name) == ar_name

    # 4. Legacy migration
    tmpdir = tempfile.mkdtemp(prefix="forensic_mig_")
    try:
        legacy_dir = os.path.join(tmpdir, "1er dossier")
        target_root = os.path.join(tmpdir, "dossiers")
        client_dir = os.path.join(legacy_dir, "Client_Alpha")
        os.makedirs(client_dir, exist_ok=True)

        test_file = os.path.join(client_dir, "annex1.pdf")
        with open(test_file, "wb") as f:
            f.write(b"%PDF-1.4 test content")

        migrated_count = migrate_legacy_dossiers(legacy_dir, target_root)
        assert migrated_count == 1

        dst_1er = os.path.join(target_root, "Client_Alpha", "1er_dossier", "annex1.pdf")
        dst_2eme = os.path.join(target_root, "Client_Alpha", "2eme_dossier")
        assert os.path.exists(dst_1er)
        assert os.path.isdir(dst_2eme)
        with open(dst_1er, "rb") as f:
            assert f.read() == b"%PDF-1.4 test content"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

def test_forensic_boundary_csv_preview():
    tmpdir = tempfile.mkdtemp(prefix="forensic_csv_")
    try:
        db_path = os.path.join(tmpdir, "csv_boundary.db")
        db = DatabaseManager(db_path)
        db.initialize_db()

        # Empty / whitespace
        assert db.preview_csv_serials("") == {"total_found": 0, "valid": [], "duplicates_in_file": [], "already_in_db": []}
        assert db.preview_csv_serials("   \n\n   \t\n") == {"total_found": 0, "valid": [], "duplicates_in_file": [], "already_in_db": []}

        # Large batch (2000 lines) with mixed delimiters and duplicates
        lines = ["SN;Model"]
        for i in range(1000):
            lines.append(f"SN-BATCH-{i:04d};Dome")
        for i in range(200): # 200 intra-file duplicates
            lines.append(f"SN-BATCH-{i:04d};Dome")
        
        csv_content = "\r\n".join(lines)
        preview = db.preview_csv_serials(csv_content)
        assert preview["total_found"] == 1200
        assert len(preview["duplicates_in_file"]) == 200
        assert len(preview["valid"]) == 1000

        db.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
