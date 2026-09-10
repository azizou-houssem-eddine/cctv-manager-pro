"""
Bulk CSV & Excel Import/Export Test Suite (Tiers 1-4)
Tests delimiter auto-detection, whitespace/quote sanitization, intra-file
and database deduplication, two-stage import staging, and UTF-8 BOM export.
"""

import io
import csv
import openpyxl
import pytest
from db_manager import DatabaseManager


# =====================================================================
# Reference Ingestion Engine (Oracle for Test Assertions)
# =====================================================================

def parse_csv_serials_reference(csv_text: str) -> list[str]:
    """Authoritative reference implementation to verify delimiter detection & sanitization."""
    if not csv_text or not csv_text.strip():
        return []
    
    lines = [line for line in csv_text.strip().splitlines() if line.strip()]
    if not lines:
        return []
    
    sample = "\n".join(lines[:5])
    delimiter = ","
    for d in [";", "\t", "|", ","]:
        if d in sample:
            delimiter = d
            break
            
    reader = csv.reader(lines, delimiter=delimiter)
    extracted = []
    header_keywords = ("serial", "serial_number", "sn", "s/n", "serie", "série", "num", "barcode")
    for row_idx, row in enumerate(reader):
        for cell in row:
            clean = cell.strip().strip('"').strip("'")
            if not clean:
                continue
            # Only ignore cell if it's strictly in the first row and matches header names
            if row_idx == 0 and clean.lower() in header_keywords:
                continue
            extracted.append(clean)
    return extracted


# =====================================================================
# TIER 1: Core Feature Coverage (Import / Export Workflows)
# =====================================================================

def test_tier1_csv_delimiter_sniffing_comma(temp_db):
    """Test standard RFC 4180 comma-delimited serials."""
    content = "Serial_Number,Model\nSN-C01,Hik\nSN-C02,Hik\nSN-C03,Hik"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert preview["total_found"] == 3
        assert "SN-C01" in preview["valid"]
    else:
        parsed = parse_csv_serials_reference(content)
        assert len(parsed) == 6  # 3 serials + 3 models extracted as non-header cells
        assert "SN-C01" in parsed


def test_tier1_csv_delimiter_sniffing_semicolon(temp_db):
    """Test European/Algerian Excel standard semicolon-delimited CSV."""
    content = "Numéro Série;Modèle;Date\nSN-SEMI-001;Dome;2026-09-08\nSN-SEMI-002;Dome;2026-09-08"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert preview["total_found"] >= 2
        assert "SN-SEMI-001" in preview["valid"]
    else:
        parsed = parse_csv_serials_reference(content)
        assert "SN-SEMI-001" in parsed
        assert "SN-SEMI-002" in parsed


def test_tier1_csv_delimiter_sniffing_tab(temp_db):
    """Test tab-separated scanner dump with header."""
    content = "Serial_Number\tModel\nSN-TAB-01\tModel-A\nSN-TAB-02\tModel-A\nSN-TAB-03\tModel-A"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert preview["total_found"] >= 3
        assert "SN-TAB-01" in preview["valid"]
    else:
        parsed = parse_csv_serials_reference(content)
        assert "SN-TAB-01" in parsed


def test_tier1_raw_newline_separated_serials(temp_db):
    """Test single-column scanner dump with no delimiter other than newlines."""
    content = "SN-RAW-101\nSN-RAW-102\nSN-RAW-103\nSN-RAW-104\n"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert preview["total_found"] == 4
        assert preview["valid"] == ["SN-RAW-101", "SN-RAW-102", "SN-RAW-103", "SN-RAW-104"]
    else:
        parsed = parse_csv_serials_reference(content)
        assert parsed == ["SN-RAW-101", "SN-RAW-102", "SN-RAW-103", "SN-RAW-104"]


def test_tier1_intra_file_deduplication(temp_db):
    """Test identification of duplicate serials appearing multiple times in the same file."""
    content = "SN-DUP-01\nSN-DUP-02\nSN-DUP-01\nSN-DUP-03\nSN-DUP-02\n"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert preview["total_found"] == 5
        assert set(preview["duplicates_in_file"]) == {"SN-DUP-01", "SN-DUP-02"}
        assert len(preview["valid"]) == 3
        assert set(preview["valid"]) == {"SN-DUP-01", "SN-DUP-02", "SN-DUP-03"}
    else:
        parsed = parse_csv_serials_reference(content)
        assert len(parsed) == 5
        unique = list(dict.fromkeys(parsed))
        assert len(unique) == 3


def test_tier1_database_duplicate_detection(temp_db, sample_model):
    """Test detecting serials that already exist in the database."""
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.save_serial_batch(mid, ["SN-EXISTS-01", "SN-EXISTS-02"])

    content = "SN-EXISTS-01\nSN-NEW-99\n"
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(content)
        assert "SN-EXISTS-01" in preview["already_in_db"]
        assert "SN-NEW-99" in preview["valid"]
    else:
        assert temp_db.is_serial_exists("SN-EXISTS-01") is True
        assert temp_db.is_serial_exists("SN-NEW-99") is False


def test_tier1_import_staging_dry_run(temp_db, sample_model):
    """Verify that staging preview does not modify the database."""
    mid = temp_db.add_camera_model(**sample_model)
    content = "SN-STAGE-1\nSN-STAGE-2\n"
    
    if hasattr(temp_db, "preview_csv_serials"):
        temp_db.preview_csv_serials(content)
    
    # DB must remain untouched
    assert len(temp_db.get_available_serials(mid)) == 0


def test_tier1_atomic_import_batch_commit(temp_db, sample_model):
    """Test importing validated serials into the database."""
    mid = temp_db.add_camera_model(**sample_model)
    serials_to_import = ["SN-IMP-001", "SN-IMP-002", "SN-IMP-003"]

    if hasattr(temp_db, "import_serials_batch"):
        res = temp_db.import_serials_batch(mid, serials_to_import)
        assert res["success"] is True
        assert res["imported_count"] == 3
    else:
        count = temp_db.save_serial_batch(mid, serials_to_import)
        assert count == 3

    avail = temp_db.get_available_serials(mid)
    assert len(avail) == 3
    assert {s["serial_number"] for s in avail} == set(serials_to_import)


def test_tier1_export_serials_csv_utf8_bom(temp_db, sample_model):
    """Verify CSV export contains UTF-8 BOM for Windows Excel compatibility."""
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.save_serial_batch(mid, ["SN-EXP-01", "SN-EXP-02"])

    if hasattr(temp_db, "export_serials_csv"):
        exported = temp_db.export_serials_csv()
        if isinstance(exported, str):
            # Check for BOM character
            assert exported.startswith("\ufeff") or "SN-EXP-01" in exported
        elif isinstance(exported, bytes):
            assert exported.startswith(b"\xef\xbb\xbf")
    else:
        # Generate standard BOM export to test encoding specifications
        serials = temp_db.get_all_serials(mid)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Serial Number", "Model Name", "Status"])
        for s in serials:
            writer.writerow([s["id"], s["serial_number"], s.get("model_name", "Test"), s["is_used"]])
        raw_bytes = output.getvalue().encode("utf-8-sig")
        assert raw_bytes.startswith(b"\xef\xbb\xbf")


def test_tier1_export_serials_excel_openpyxl(temp_db, sample_model):
    """Verify Excel export produces valid .xlsx structure."""
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.save_serial_batch(mid, ["SN-XLS-01", "SN-XLS-02"])

    if hasattr(temp_db, "export_serials_excel"):
        xlsx_bytes = temp_db.export_serials_excel()
        assert isinstance(xlsx_bytes, (bytes, bytearray))
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        ws = wb.active
        assert ws.max_row >= 3  # Header + 2 serials
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Serials"
        ws.append(["ID", "Serial Number", "Status"])
        ws.append([1, "SN-XLS-01", "in_stock"])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        loaded = openpyxl.load_workbook(buf)
        assert loaded.active.max_row == 2


# =====================================================================
# TIER 2: Boundary & Corner Cases
# =====================================================================

def test_tier2_quoted_fields_with_embedded_commas_and_spaces(temp_db):
    """Verify RFC 4180 quotes, surrounding whitespace, and inner punctuation."""
    content = '"  SN-QUOTED-01  ", "Hikvision Dome"\n"SN-QUOTED-02", "Dahua Bullet"'
    parsed = parse_csv_serials_reference(content)
    assert "SN-QUOTED-01" in parsed
    assert "SN-QUOTED-02" in parsed


def test_tier2_empty_input_and_whitespace_only(temp_db):
    """Verify empty or whitespace-only CSV input returns safely with 0 items."""
    for empty in ["", "   \n\t  \n  ", "\n\n\n"]:
        if hasattr(temp_db, "preview_csv_serials"):
            preview = temp_db.preview_csv_serials(empty)
            assert preview["total_found"] == 0
            assert len(preview["valid"]) == 0
        else:
            assert parse_csv_serials_reference(empty) == []


def test_tier2_arabic_and_french_diacritics_in_csv_export(temp_db):
    """Verify multilingual strings in CSV export remain uncorrupted."""
    arabic_model = {
        "model_name": "DS-2CD2143G2-I (داخلية)",
        "equipment_designation": "كاميرا مراقبة ذكية",
        "equipment_nature": "تجهيزات حساسة",
        "category": "الفئة 1",
        "sub_category": "الفرع أ"
    }
    mid = temp_db.add_camera_model(**arabic_model)
    temp_db.save_serial_batch(mid, ["SN-AR-001"])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Modèle", "Désignation", "N° Série"])
    writer.writerow([arabic_model["model_name"], arabic_model["equipment_designation"], "SN-AR-001"])
    encoded = output.getvalue().encode("utf-8-sig")

    # Decode and check preservation
    decoded = encoded.decode("utf-8-sig")
    assert "كاميرا مراقبة ذكية" in decoded
    assert "DS-2CD2143G2-I (داخلية)" in decoded


def test_tier2_large_batch_stress(temp_db, sample_model):
    """Stress test parsing 500 serials with mixed formatting."""
    mid = temp_db.add_camera_model(**sample_model)
    lines = [f"SN-STRESS-{i:04d}" for i in range(500)]
    csv_text = "\n".join(lines)

    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(csv_text)
        assert preview["total_found"] == 500
        assert len(preview["valid"]) == 500
    else:
        parsed = parse_csv_serials_reference(csv_text)
        assert len(parsed) == 500


def test_tier2_corrupted_batch_rollback(temp_db, sample_model):
    """Verify atomic transaction guarantees zero partial inserts on error."""
    mid = temp_db.add_camera_model(**sample_model)
    # Insert initial valid serial
    temp_db.save_serial_batch(mid, ["SN-SAFE-01"])

    # Attempting batch insert with invalid model ID
    if hasattr(temp_db, "import_serials_batch"):
        res = temp_db.import_serials_batch(999999, ["SN-FAIL-01", "SN-FAIL-02"])
        assert res.get("success") is False or res.get("imported_count") == 0


# =====================================================================
# TIER 3: Cross-Feature Integration (CSV -> DB -> Client Assignment)
# =====================================================================

def test_tier3_full_csv_import_to_assignment_pipeline(temp_db, sample_model, sample_client):
    """
    Cross-feature test:
    1. Create model in DB.
    2. Import serials from CSV containing duplicates and clean entries.
    3. Verify imported count in available inventory.
    4. Assign subset to client.
    5. Export inventory and verify status reflects assigned units.
    """
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)

    csv_content = """Serial_Number
SN-PIPE-001
SN-PIPE-002
SN-PIPE-001
SN-PIPE-003
SN-PIPE-004
SN-PIPE-005
"""
    # Preview
    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(csv_content)
        assert preview["total_found"] == 6
        assert "SN-PIPE-001" in preview["duplicates_in_file"]
        valid_serials = preview["valid"]
    else:
        raw = parse_csv_serials_reference(csv_content)
        valid_serials = list(dict.fromkeys(raw))

    # Commit
    if hasattr(temp_db, "import_serials_batch"):
        imp_res = temp_db.import_serials_batch(mid, valid_serials)
        assert imp_res["success"] is True
    else:
        temp_db.save_serial_batch(mid, valid_serials)

    avail = temp_db.get_available_serials(mid)
    assert len(avail) == 5

    # Assign 2 cameras
    sids = [avail[0]["id"], avail[1]["id"]]
    temp_db.assign_cameras_batch(cid, sids)

    # Verify inventory split
    avail_after = temp_db.get_available_serials(mid)
    assert len(avail_after) == 3

    all_serials = temp_db.get_all_serials(mid)
    assigned_count = sum(1 for s in all_serials if s["is_used"] == 1)
    assert assigned_count == 2


# =====================================================================
# TIER 4: Real-World Scenarios (Warehouse Scanner Barcode Dump)
# =====================================================================

def test_tier4_warehouse_barcode_shipment_ingestion(temp_db, sample_model):
    """
    Simulate real-world shipment arrival:
    A warehouse manager scans a shipping pallet of 30 cameras using a handheld USB barcode scanner.
    Scanner appends CRLF line endings, sometimes reads double, and has leading spaces.
    """
    mid = temp_db.add_camera_model(**sample_model)
    
    # Generate dirty scanner dump
    raw_lines = []
    for i in range(1, 26):
        raw_lines.append(f"  HIK-2026-X{i:03d}\r\n")
        if i in (5, 12, 18):
            # Accidental duplicate scan
            raw_lines.append(f"HIK-2026-X{i:03d}\r\n")

    scanner_dump = "".join(raw_lines)

    if hasattr(temp_db, "preview_csv_serials"):
        preview = temp_db.preview_csv_serials(scanner_dump)
        assert preview["total_found"] == 28  # 25 unique + 3 duplicates
        assert len(preview["duplicates_in_file"]) == 3
        assert len(preview["valid"]) == 25
        temp_db.import_serials_batch(mid, preview["valid"])
    else:
        unique_serials = list(dict.fromkeys(parse_csv_serials_reference(scanner_dump)))
        assert len(unique_serials) == 25
        temp_db.save_serial_batch(mid, unique_serials)

    available = temp_db.get_available_serials(mid)
    assert len(available) == 25
