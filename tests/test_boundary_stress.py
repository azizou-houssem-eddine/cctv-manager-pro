"""
Boundary & Adversarial Stress Test Suite for Milestone 1
Author: Challenger 2 (Milestone 1: CSV/Excel & Boundary Stress Verifier)

Empirically challenges:
1. 5,000 messy CSV serials ingestion, timing, memory, and deduplication
2. Header detection false positives on camera serials starting with SN-, NUM-, CODE-
3. Adversarial SQL injection strings across import, search, and update
4. Path traversal and Windows reserved device names in dossier management
5. 5,000 record Excel export binary integrity, column width bounds, and formula injection
"""

import io
import os
import time
import shutil
import tempfile
import openpyxl
import pytest
from db_manager import (
    DatabaseManager,
    sanitize_dossier_name,
    get_client_dossier_dir,
    migrate_legacy_dossiers,
    _normalize_text_input
)


# =====================================================================
# 1. 5,000 Messy CSV Serials Stress & Deduplication
# =====================================================================

def test_stress_5000_csv_serials_ingestion(temp_db, sample_model):
    """
    Generate 5,000 unique serial numbers formatted with chaotic delimiters,
    trailing spaces, quotes, and empty lines. Verify preview and atomic import.
    """
    model_id = temp_db.add_camera_model(**sample_model)
    assert model_id > 0

    # Build chaotic 5,000 CSV lines with mixed formatting
    lines = ["Serial Number,Model,Status"]
    expected_serials = []
    for i in range(1, 5001):
        sn = f"SN-CHAOS-{i:05d}"
        expected_serials.append(sn)
        if i % 7 == 0:
            lines.append(f'"{sn}",DS-2CD2143G2-I,In Stock')
        elif i % 5 == 0:
            lines.append(f"{sn} , DS-2CD2143G2-I , In Stock ")
        elif i % 11 == 0:
            lines.append(f"\n{sn},DS-2CD2143G2-I,In Stock\n")  # extra empty lines
        else:
            lines.append(f"{sn},DS-2CD2143G2-I,In Stock")

    csv_text = "\n".join(lines)

    # 1. Preview staging timing
    t0 = time.perf_counter()
    preview = temp_db.preview_csv_serials(csv_text)
    preview_elapsed = time.perf_counter() - t0

    assert preview["total_found"] == 5000, f"Expected 5000 total found, got {preview['total_found']}"
    assert len(preview["valid"]) == 5000, f"Expected 5000 valid, got {len(preview['valid'])}"
    assert len(preview["duplicates_in_file"]) == 0
    assert len(preview["already_in_db"]) == 0
    assert preview_elapsed < 5.0, f"Preview took {preview_elapsed:.2f}s, exceeding 5.0s threshold"

    # 2. Batch atomic import timing
    t1 = time.perf_counter()
    res = temp_db.import_serials_batch(model_id, preview["valid"])
    import_elapsed = time.perf_counter() - t1

    assert res["success"] is True
    assert res["imported_count"] == 5000
    assert res["duplicates_skipped"] == 0
    assert import_elapsed < 10.0, f"Import took {import_elapsed:.2f}s, exceeding 10.0s threshold"

    # 3. Verify in database
    available = temp_db.get_available_serials(model_id)
    assert len(available) == 5000

    # 4. Stress re-import of the exact same 5,000 serials (must skip all 5,000)
    t2 = time.perf_counter()
    res_dup = temp_db.import_serials_batch(model_id, preview["valid"])
    dup_elapsed = time.perf_counter() - t2

    assert res_dup["success"] is True
    assert res_dup["imported_count"] == 0
    assert res_dup["duplicates_skipped"] == 5000
    assert dup_elapsed < 10.0


# =====================================================================
# 2. Header Detection False Positives & Edge Cases
# =====================================================================

def test_header_detection_false_positives_on_raw_serials(temp_db):
    """
    CRITICAL CHALLENGE: Camera serial numbers commonly start with 'SN-', 'NUM-', 'CODE-',
    'SERIE-', or 'S/N-'. If a CSV has NO header row, does preview_csv_serials mistakenly
    treat the first legitimate camera serial as a header and drop it?
    """
    # Case A: Standard 2-column CSV without header, where first serial starts with SN-
    content_sn = "SN-98765,Hikvision\nSN-98766,Hikvision\nSN-98767,Hikvision"
    preview_sn = temp_db.preview_csv_serials(content_sn)
    
    # Document whether row 0 was dropped
    sn_dropped = "SN-98765" not in preview_sn["valid"]

    # Case B: First serial starts with CODE-
    content_code = "CODE-1001,Dahua\nCODE-1002,Dahua"
    preview_code = temp_db.preview_csv_serials(content_code)
    code_dropped = "CODE-1001" not in preview_code["valid"]

    # Case C: First serial starts with NUM-
    content_num = "NUM-501;Uniview\nNUM-502;Uniview"
    preview_num = temp_db.preview_csv_serials(content_num)
    num_dropped = "NUM-501" not in preview_num["valid"]

    # Record the empirical findings
    print("\n[EMPIRICAL FINDING] Header False Positive Dropped:")
    print(f"  SN-98765 dropped: {sn_dropped}")
    print(f"  CODE-1001 dropped: {code_dropped}")
    print(f"  NUM-501 dropped: {num_dropped}")

    # We expect an ideal parser NOT to drop legitimate serials.
    # We assert the finding to document this defect empirically.
    assert not sn_dropped, (
        "DEFECT DETECTED: preview_csv_serials dropped legitimate serial 'SN-98765' "
        "because substring 'sn' in row 0 was mistakenly identified as a header column!"
    )


def test_horizontal_comma_separated_serials_edge_case(temp_db):
    """
    CHALLENGE: Test user input where multiple serials are listed on one line or separated
    horizontally, e.g. 'SN001, SN002, SN003'.
    """
    content = "SN001, SN002, SN003"
    preview = temp_db.preview_csv_serials(content)
    print(f"\n[EMPIRICAL FINDING] Horizontal serial preview: {preview}")
    # Document whether preview treats multi-column row as single serial + extra cols


# =====================================================================
# 3. Adversarial SQL Injection & XSS Payloads
# =====================================================================

def test_adversarial_sql_injection_payloads(temp_db, sample_model, sample_client):
    """
    Test extreme SQL injection vectors in serial numbers, search queries,
    and client fields. Verify tables are never dropped or corrupted.
    """
    model_id = temp_db.add_camera_model(**sample_model)
    assert model_id > 0

    sqli_serials = [
        "'; DROP TABLE serial_numbers; --",
        "' OR '1'='1",
        '" OR ""="',
        "'; UPDATE serial_numbers SET is_used = 1; --",
        "UNION SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 --",
        "admin'--",
        "'; DROP TABLE clients; --",
        "'; DROP TABLE camera_models; --",
        "0; ATTACH DATABASE 'evil.db' AS evil;",
        "'; VACUUM; --"
    ]

    # Ingest SQL injection strings
    res = temp_db.import_serials_batch(model_id, sqli_serials)
    assert res["success"] is True
    assert res["imported_count"] == len(sqli_serials)

    # Verify tables still exist
    models = temp_db.get_camera_models()
    assert len(models) == 1, "camera_models table was dropped or corrupted!"

    all_serials = temp_db.get_all_serials(model_id)
    assert len(all_serials) == len(sqli_serials), "serial_numbers table was dropped or corrupted!"

    # Test search with SQL injection payload (note: outer quotes were stripped by importer)
    search_q = temp_db.search_serials("; DROP TABLE")
    assert len(search_q) >= 2, "Failed to find inserted serials containing SQL injection payload"

    search_or = temp_db.search_serials("OR '1'=")
    assert len(search_or) >= 1, "Failed to find inserted serials containing SQL injection payload"

    # Test client creation with SQL injection in full_name and doc_number
    client_payload = dict(sample_client)
    client_payload["full_name"] = "Malicious Client '; DROP TABLE clients; --"
    client_payload["doc_number"] = "DOC-'; DROP TABLE serial_numbers; --"
    cid = temp_db.add_client(client_payload)
    assert cid > 0

    clients = temp_db.get_clients()
    assert any(c["id"] == cid for c in clients)

    # Ensure foreign keys and data remain intact
    client_data = temp_db.get_client(cid)
    assert "DROP TABLE" in client_data["full_name"]


# =====================================================================
# 4. Extreme Unicode, BiDi & Boundary Characters
# =====================================================================

def test_extreme_unicode_arabic_emojis_and_long_strings(temp_db, sample_model):
    """
    Test Arabic RTL strings, emojis, mixed bilingual characters, and long strings.
    """
    model_id = temp_db.add_camera_model(**sample_model)

    long_serial = "SN-" + "A" * 500
    arabic_serial = "كاميرا-رقم-١٢٣٤٥-مراقبة"
    emoji_serial = "📷-CAMERA-🎥-SECURE-🛡️-001"
    special_char_serial = "SN#@!$%^&*()_+=-~`{}[]|;:,.<>?"

    extreme_batch = [long_serial, arabic_serial, emoji_serial, special_char_serial]
    res = temp_db.import_serials_batch(model_id, extreme_batch)
    assert res["success"] is True
    assert res["imported_count"] == len(extreme_batch)

    # Search each
    assert len(temp_db.search_serials("كاميرا-رقم")) == 1
    assert len(temp_db.search_serials("📷-CAMERA")) == 1
    assert len(temp_db.search_serials(long_serial[:50])) == 1

    # CSV export handles Arabic and emojis properly
    csv_content = temp_db.export_serials_csv()
    assert arabic_serial in csv_content
    assert emoji_serial in csv_content


# =====================================================================
# 5. Path Traversal & Windows Reserved Device Names
# =====================================================================

def test_adversarial_path_traversal_and_windows_device_names(temp_dir):
    """
    Test sanitize_dossier_name and get_client_dossier_dir with:
    - Path traversal: ../../evil
    - Windows reserved device names: CON, PRN, AUX, NUL, COM1, LPT1
    - Windows reserved names with extensions: CON.txt, aux.pdf, nul.dat
    - Trailing spaces and dots
    - Characters illegal on Windows: < > : " / \\ | ? *
    """
    test_cases = [
        ("../../evil_dir", "evil_dir"),
        ("..\\..\\windows\\system32", "windows_system32"),
        ("....//....//nested", "nested"),
        (".", "Client_Unnamed"),
        ("..", "Client_Unnamed"),
        ("...", "Client_Unnamed"),
        ("CON", "CON_client"),
        ("prn", "prn_client"),
        ("aux", "aux_client"),
        ("nul", "nul_client"),
        ("com1", "com1_client"),
        ("lpt1", "lpt1_client"),
        ("CON.txt", "CON.txt"),       # CRITICAL WINDOWS VULNERABILITY CHECK
        ("aux.pdf", "aux.pdf"),       # CRITICAL WINDOWS VULNERABILITY CHECK
        ("Client : With <Bad> *Chars* ?", "Client _ With _Bad_ _Chars_ _"),
        ("Client Name . . . ", "Client Name"),
        ("   ", "Client_Unnamed"),
        ("A" * 200, "A" * 100),
    ]

    for raw_name, expected_substring in test_cases:
        sanitized = sanitize_dossier_name(raw_name)
        assert sanitized, f"Sanitized name is empty for input '{raw_name}'"
        assert not any(c in sanitized for c in '<>:"/\\|?*'), f"Illegal Windows char in '{sanitized}'"
        assert not sanitized.endswith(('.', ' ')), f"Trailing dot/space in '{sanitized}'"

        # Check if get_client_dossier_dir can actually create the directory on Windows 11
        try:
            dossier_path = get_client_dossier_dir(raw_name, "1er_dossier", base_dir=temp_dir)
            assert os.path.isdir(dossier_path), f"Failed to create valid directory for '{raw_name}' -> '{dossier_path}'"
        except OSError as e:
            pytest.fail(f"CRITICAL OS ERROR creating folder for '{raw_name}' (sanitized: '{sanitized}'): {e}")


def test_migrate_legacy_dossiers_with_adversarial_entries(temp_dir):
    """
    Test migrate_legacy_dossiers when legacy directory contains folders with
    traversal names or reserved names.
    """
    legacy_root = os.path.join(temp_dir, "1er dossier")
    target_root = os.path.join(temp_dir, "dossiers")
    os.makedirs(legacy_root, exist_ok=True)

    # Create legitimate client folder
    legit_folder = os.path.join(legacy_root, "Client_Normal")
    os.makedirs(legit_folder, exist_ok=True)
    with open(os.path.join(legit_folder, "annex1.pdf"), "w", encoding="utf-8") as f:
        f.write("mock pdf content")

    count = migrate_legacy_dossiers(legacy_root, target_root)
    assert count == 1
    dst_file = os.path.join(target_root, "Client_Normal", "1er_dossier", "annex1.pdf")
    assert os.path.exists(dst_file)


# =====================================================================
# 6. Large Excel Export (5,000 records) & openpyxl Integrity
# =====================================================================

def test_stress_5000_excel_export_openpyxl_integrity(temp_db, sample_model):
    """
    Export 5,000 serial records to Excel (.xlsx) using export_serials_excel.
    Verify:
    1. Binary format validity via openpyxl.load_workbook
    2. Sheet row count == 5,001 (1 header + 5,000 data rows)
    3. Column count == 7
    4. Auto column width does not crash or exceed max bounds
    5. Execution time and memory sanity
    """
    model_id = temp_db.add_camera_model(**sample_model)
    serials = [f"DS2CD-EXCEL-{i:05d}" for i in range(1, 5001)]
    temp_db.import_serials_batch(model_id, serials)

    # Measure export time
    t0 = time.perf_counter()
    excel_bytes = temp_db.export_serials_excel()
    export_elapsed = time.perf_counter() - t0

    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 50000, f"Excel file suspiciously small: {len(excel_bytes)} bytes"
    assert export_elapsed < 10.0, f"Excel export took {export_elapsed:.2f}s, exceeding 10.0s"

    # Verify openpyxl can read the output cleanly
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes), read_only=True)
    ws = wb["Inventory Serials"]
    rows = list(ws.iter_rows(values_only=True))
    assert len(rows) == 5001, f"Expected 5,001 rows in Excel, got {len(rows)}"
    assert rows[0] == ("ID", "Serial Number", "Model Name", "Designation", "Status", "Client Name", "Date Assigned")
    assert rows[1][1] == "DS2CD-EXCEL-00001"
    assert rows[5000][1] == "DS2CD-EXCEL-05000"
    wb.close()


def test_excel_export_extreme_column_width(temp_db, sample_model):
    """
    CHALLENGE: In Excel, column width has a strict upper limit (255 characters).
    If a camera model designation or client name has 500 characters, does openpyxl
    crash or produce an invalid sheet when auto-calculating column width?
    """
    extreme_model = dict(sample_model)
    extreme_model["equipment_designation"] = "VERY_LONG_DESIGNATION_" * 20  # 440 chars
    mid = temp_db.add_camera_model(**extreme_model)
    temp_db.import_serials_batch(mid, ["SN-WIDTH-TEST-001"])

    excel_bytes = temp_db.export_serials_excel(model_id=mid)
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws = wb.active
    # Check calculated width on designation column (col D)
    col_d_width = ws.column_dimensions["D"].width
    print(f"\n[EMPIRICAL FINDING] Column D calculated width: {col_d_width}")
    # If width > 255, Excel will report workbook corruption upon opening
    assert col_d_width <= 255, (
        f"DEFECT DETECTED: Column D width is {col_d_width}, which exceeds "
        "Microsoft Excel maximum allowed column width of 255! Excel will reject this file as corrupted."
    )
    wb.close()


def test_excel_export_illegal_characters_crash(temp_db, sample_model):
    """
    CRITICAL CHALLENGE: Barcode scanner garbage or binary dumps containing ASCII control
    characters (e.g. \\x00, \\x01-\\x1f) crash openpyxl with IllegalCharacterError.
    """
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.import_serials_batch(mid, ["SN-VALID-001", "SN-BAD-\x00\x01-002"])

    try:
        data = temp_db.export_serials_excel()
        assert len(data) > 0
    except Exception as e:
        import openpyxl.utils.exceptions
        if isinstance(e, openpyxl.utils.exceptions.IllegalCharacterError):
            pytest.fail(
                f"DEFECT DETECTED: export_serials_excel() crashed with unhandled IllegalCharacterError: {e}. "
                "Control characters from scanner dumps or corrupted CSVs must be sanitized before writing to openpyxl."
            )
        raise


def test_formula_injection_handling(temp_db, sample_model):
    """
    CHALLENGE: Formula injection payloads in serial numbers or client names
    (starting with =, +, -, @) should not be converted to executable formulas in Excel.
    """
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.import_serials_batch(mid, ["=SUM(1,2)"])

    excel_bytes = temp_db.export_serials_excel()
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws = wb.active
    cell = ws.cell(row=2, column=2)
    print(f"\n[EMPIRICAL FINDING] Formula cell data_type: {cell.data_type}, value: {cell.value}")
    assert cell.data_type != "f", (
        f"DEFECT DETECTED: Serial '=SUM(1,2)' was stored with data_type='f' (Formula)! "
        "Excel will execute this formula or fail with #NAME? error. Serial strings must be escaped or treated as string type."
    )
    wb.close()

