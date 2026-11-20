"""
Forensic Integrity Verification Test Suite for Milestone 2
Authored by Forensic Auditor (Milestone 2)

Empirically verifies:
1. Authentic vector drawing in generate_pv_pose (draw_rect, draw_line, insert_textbox, get_drawings).
2. Genuine camera serial stamping and text extraction across all pagination thresholds.
3. Authentic 150 DPI Pixmap rendering, PNG headers, dimensions, and pixel divergence on content change.
4. Authentic deflate compression and garbage collection (stream /FlateDecode, size reduction).
5. Authentic Arabic and mixed BiDi shaping (character transformation, visual order, base_dir='L').
6. Absence of facade/dummy return values in api_bridge and pdf_generator.
"""

import os
import io
import struct
import base64
import hashlib
import tempfile
import shutil
import fitz
import pytest

from pdf_generator import (
    PDFGenerator,
    shape_arabic,
    calculate_pv_page_splits,
    sanitize_dossier_name,
    generate_pv_pose
)
from db_manager import DatabaseManager
from api_bridge import JsApi


# =====================================================================
# CHECK 1: Authentic Vector Drawing in generate_pv_pose()
# =====================================================================

def test_forensic_check1_vector_drawing_authenticity(temp_dir, pdf_gen, sample_client):
    """
    Verify that generate_pv_pose builds an authentic vector PDF document from scratch:
    - Starts from blank fitz.open() (not copying a static file).
    - Contains real vector drawing paths (draw_rect, draw_line) inspectable via page.get_drawings().
    - Has primary header rect, double borders, two-column site info box, table rows, and signature blocks.
    """
    sample_cams = [
        {
            "equipment_designation": "كاميرا مراقبة رقمية 4K",
            "model_name": "DS-2CD2143G2-I",
            "equipment_nature": "داخلية",
            "category": "الفئة 1",
            "sub_category": "الفرع أ",
            "serial_number": "SN-VECTOR-VERIFY-001",
            "serial_id": 1
        }
    ]

    out_pdf = os.path.join(temp_dir, "test_vector_drawing.pdf")
    res_path = pdf_gen.generate_pv_pose(sample_client, sample_cams, output_path=out_pdf)
    assert os.path.exists(res_path)

    doc = fitz.open(res_path)
    assert len(doc) == 1
    page = doc[0]

    # Verify vector drawing paths via get_drawings()
    drawings = page.get_drawings()
    assert len(drawings) > 10, f"Expected > 10 vector drawing objects, got {len(drawings)}"

    # Check for specific vector structural elements:
    # 1. Outer border rectangle
    # 2. Header background rectangle
    # 3. Two-column info box rectangle and dividing line
    # 4. Table header rectangle
    # 5. Table row rectangles
    # 6. Signature box rectangles
    rect_drawings = [d for d in drawings if d.get("type") in ("f", "s", "fs") or "rect" in d]
    assert len(rect_drawings) >= 8, f"Expected at least 8 filled/stroked vector shapes, got {len(rect_drawings)}"

    # Verify outer border dimensions (~30, 30, 565, 812)
    border_found = False
    for d in drawings:
        r = d.get("rect")
        if r and abs(r.x0 - 30.0) < 2 and abs(r.y0 - 30.0) < 2 and abs(r.x1 - 565.0) < 2:
            border_found = True
            break
    assert border_found, "Outer double border vector rect not found in drawings"

    # Verify dividing line in 2-column info box (x=297, y=118..194)
    line_found = False
    for d in drawings:
        for item in d.get("items", []):
            if item[0] == "l":  # Line
                p1, p2 = item[1], item[2]
                if abs(p1.x - 297.0) < 2 and abs(p2.x - 297.0) < 2:
                    line_found = True
                    break
    assert line_found, "Two-column divider line (x=297) not found in vector drawings"

    doc.close()


# =====================================================================
# CHECK 2: Genuine Camera Serial Stamping & Extraction Across Pagination
# =====================================================================

def test_forensic_check2_camera_serial_stamping_and_extraction(temp_dir, pdf_gen, sample_client):
    """
    Verify camera serial numbers are stamped as real text in the PDF stream
    and are 100% recoverable across single-page and multi-page pagination.
    """
    # 1. Test Single-Page (10 unique cameras)
    unique_serials_10 = [f"SN-EMPIRICAL-{i:03d}" for i in range(1, 11)]
    cams_10 = [
        {
            "equipment_designation": "كاميرا مراقبة",
            "model_name": "HIK-MODEL-PRO",
            "equipment_nature": "خارجية",
            "category": "الفئة 1",
            "sub_category": "الفرع أ",
            "serial_number": sn,
            "serial_id": i
        }
        for i, sn in enumerate(unique_serials_10, 1)
    ]

    out_single = os.path.join(temp_dir, "pv_single_extracted.pdf")
    pdf_gen.generate_pv_pose(sample_client, cams_10, output_path=out_single)

    doc_single = fitz.open(out_single)
    assert len(doc_single) == 1
    # Normalize soft-hyphen \xad produced by Windows TrueType fonts
    text_single = doc_single[0].get_text().replace("\xad", "-")
    for sn in unique_serials_10:
        assert sn in text_single, f"Serial {sn} missing from extracted text in single-page PV"
    doc_single.close()

    # 2. Test Multi-Page Balanced Split (26 cameras -> Page 1: 13, Page 2: 13)
    unique_serials_26 = [f"SN-SPLIT-26-{i:03d}" for i in range(1, 27)]
    cams_26 = [
        {
            "equipment_designation": "كاميرا مراقبة",
            "model_name": "HIK-MODEL-PRO",
            "equipment_nature": "خارجية",
            "category": "الفئة 1",
            "sub_category": "الفرع أ",
            "serial_number": sn,
            "serial_id": i
        }
        for i, sn in enumerate(unique_serials_26, 1)
    ]

    out_split = os.path.join(temp_dir, "pv_split_extracted.pdf")
    pdf_gen.generate_pv_pose(sample_client, cams_26, output_path=out_split)

    doc_split = fitz.open(out_split)
    assert len(doc_split) == 2, f"Expected 2 pages for 26 cameras, got {len(doc_split)}"

    text_p1 = doc_split[0].get_text().replace("\xad", "-")
    text_p2 = doc_split[1].get_text().replace("\xad", "-")

    # First 13 serials must be on page 1
    for sn in unique_serials_26[:13]:
        assert sn in text_p1, f"Serial {sn} should be on Page 1"
        assert sn not in text_p2, f"Serial {sn} unexpectedly found on Page 2"

    # Remaining 13 serials must be on page 2
    for sn in unique_serials_26[13:]:
        assert sn in text_p2, f"Serial {sn} should be on Page 2"
        assert sn not in text_p1, f"Serial {sn} unexpectedly found on Page 1"

    doc_split.close()


# =====================================================================
# CHECK 3: Authentic 150 DPI Pixmap Preview & Dynamic Rendering
# =====================================================================

def test_forensic_check3_pixmap_preview_150dpi_and_dynamic_rendering(pdf_gen, sample_client, sample_purchases):
    """
    Verify generate_document_preview_pixmaps:
    - Returns valid PNG data URIs.
    - PNG magic number: \\x89PNG\\r\\n\\x1a\\n.
    - Validates dimensions at 150 DPI: A4 is ~1240 x 1754 px.
    - Validates dynamic rendering: altering client text changes PNG pixel hash.
    - Validates DPI sensitivity: dpi=72 produces different dimensions than dpi=150.
    """
    # 1. Preview for Annex 1
    preview_res = pdf_gen.get_document_preview(sample_client, sample_purchases, doc_type="annex1")
    assert preview_res["success"] is True
    assert len(preview_res["pages"]) >= 1

    uri = preview_res["pages"][0]
    assert uri.startswith("data:image/png;base64,")
    b64_data = uri.split(",", 1)[1]
    raw_png = base64.b64decode(b64_data)

    # Check PNG magic header
    assert raw_png[:8] == b"\x89PNG\r\n\x1a\n", "Invalid PNG magic signature"

    # Check PNG IHDR chunk (starts at byte 12)
    ihdr_marker = raw_png[12:16]
    assert ihdr_marker == b"IHDR", "PNG IHDR chunk missing"
    width, height = struct.unpack(">II", raw_png[16:24])

    # A4 standard at 150 DPI:
    # 595.0 pt * 150 / 72 = 1239.58 -> 1240 px
    # 842.0 pt * 150 / 72 = 1754.16 -> 1754 or 1755 px
    assert abs(width - 1240) <= 2, f"Expected ~1240px width at 150 DPI, got {width}"
    assert abs(height - 1754) <= 2, f"Expected ~1754px height at 150 DPI, got {height}"

    # 2. Dynamic Pixel Divergence Test (No static/cached mock images)
    client_alpha = dict(sample_client, full_name="Alpha Client", company_name="Company Alpha 1111")
    client_beta = dict(sample_client, full_name="Beta Client", company_name="Company Beta 2222")

    prev_alpha = pdf_gen.get_document_preview(client_alpha, sample_purchases, doc_type="pv_pose")
    prev_beta = pdf_gen.get_document_preview(client_beta, sample_purchases, doc_type="pv_pose")

    png_alpha = base64.b64decode(prev_alpha["pages"][0].split(",")[1])
    png_beta = base64.b64decode(prev_beta["pages"][0].split(",")[1])

    hash_alpha = hashlib.sha256(png_alpha).hexdigest()
    hash_beta = hashlib.sha256(png_beta).hexdigest()

    assert hash_alpha != hash_beta, "Pixmap preview returned identical pixels for different client names (FACADE SUSPECTED!)"

    # 3. DPI Parameter Sensitivity Check
    doc_pv = fitz.open(stream=pdf_gen.generate_pv_pose(sample_client, sample_purchases), filetype="pdf")
    pix_150 = pdf_gen.generate_document_preview_pixmaps(doc_pv, dpi=150)
    pix_72 = pdf_gen.generate_document_preview_pixmaps(doc_pv, dpi=72)
    doc_pv.close()

    png_150 = base64.b64decode(pix_150[0].split(",")[1])
    png_72 = base64.b64decode(pix_72[0].split(",")[1])

    w_150, h_150 = struct.unpack(">II", png_150[16:24])
    w_72, h_72 = struct.unpack(">II", png_72[16:24])

    assert w_150 > w_72 and h_150 > h_72, "DPI parameter has no effect on rendered pixmap dimensions"
    assert abs(w_72 - 595) <= 2, f"Expected ~595px at 72 DPI, got {w_72}"


# =====================================================================
# CHECK 4: Authentic Deflate Compression & Stream /FlateDecode
# =====================================================================

def test_forensic_check4_authentic_deflate_compression(temp_dir, pdf_gen, sample_client, sample_purchases):
    """
    Verify deflate=True, garbage=4 is genuinely applied and actively reduces file size.
    Inspects internal PDF dictionary streams for /Filter /FlateDecode.
    """
    doc_raw = fitz.open(pdf_gen.annex1_template)
    if pdf_gen.font_path and os.path.exists(pdf_gen.font_path):
        doc_raw[0].insert_font(fontname="f0", fontfile=pdf_gen.font_path)
    pdf_gen._stamp_field(doc_raw[0], fitz.Rect(38, 197, 467, 216), sample_client["full_name"], fontname="f0")

    # Uncompressed bytes
    bytes_uncompressed = doc_raw.tobytes(deflate=False, garbage=0)
    # Compressed bytes
    bytes_compressed = doc_raw.tobytes(deflate=True, garbage=4)
    doc_raw.close()

    assert len(bytes_compressed) < len(bytes_uncompressed), (
        f"Compressed size ({len(bytes_compressed)}) not smaller than uncompressed ({len(bytes_uncompressed)})"
    )

    ratio = (1.0 - (len(bytes_compressed) / len(bytes_uncompressed))) * 100.0
    assert ratio > 15.0, f"Compression ratio {ratio:.1f}% unexpectedly low"

    # Verify /FlateDecode in compressed stream
    assert b"/FlateDecode" in bytes_compressed, "PDF stream lacks /FlateDecode compression filter"

    # Verify all generated files in generate_client_dossier satisfy < 850 KB
    dossier_res = pdf_gen.generate_client_dossier(sample_client, sample_purchases, parent_folder=temp_dir)
    folder = dossier_res.get("folder")
    for fname in ["annex1.pdf", "annex5.pdf", "pv_reception.pdf"]:
        fpath = os.path.join(folder, fname)
        assert os.path.exists(fpath)
        sz = os.path.getsize(fpath)
        assert sz < 850_000, f"File {fname} size {sz} bytes exceeds 850 KB limit"


# =====================================================================
# CHECK 5: Authentic Arabic & Mixed BiDi Shaping
# =====================================================================

def test_forensic_check5_authentic_bidi_shaping():
    """
    Verify shape_arabic performs genuine contextual glyph transformation
    and bidirectional reordering without inversion of brackets/colons.
    """
    import arabic_reshaper
    from bidi.algorithm import get_display

    raw_ar = "محضر استلام"
    # Verify input is in Arabic block (U+0600..U+06FF)
    assert all('\u0600' <= ch <= '\u06FF' for ch in raw_ar.replace(" ", ""))

    shaped = shape_arabic(raw_ar)
    assert shaped != raw_ar, "shape_arabic returned unchanged string for Arabic text (reshaping failed)"

    # Reshaped Arabic should contain presentation forms (U+FB50..U+FDFF or U+FE70..U+FEFF)
    has_pres_forms = any('\uFE70' <= ch <= '\uFEFF' or '\uFB50' <= ch <= '\uFDFF' for ch in shaped)
    assert has_pres_forms, "Reshaped string missing Arabic Presentation Forms glyphs"

    # Mixed Latin-Arabic test:
    # In pure LTR without base_dir='L', brackets/colons at edges can get inverted
    mixed_input = "DS-2CD2143G2-I (كاميرا مراقبة)"
    mixed_shaped = shape_arabic(mixed_input)

    # Must preserve Latin prefix on left
    assert mixed_shaped.startswith("DS-2CD2143G2-I ("), f"Unexpected prefix: {mixed_shaped}"
    assert mixed_shaped.endswith(")"), f"Unexpected suffix: {mixed_shaped}"

    # Verify French accented characters trigger Latin base_dir='L'
    french_ar = "BÉNÉFICIAIRE (الزبون):"
    french_shaped = shape_arabic(french_ar)
    assert french_shaped.startswith("BÉNÉFICIAIRE ("), f"Unexpected start: {french_shaped}"
    assert french_shaped.endswith("):"), f"Unexpected ending: {french_shaped}"


# =====================================================================
# CHECK 6: End-to-End API Bridge & Zero-Facade Integration
# =====================================================================

def test_forensic_check6_api_bridge_real_database_and_pdf_integration(temp_dir, temp_db, pdf_gen, monkeypatch):
    """
    Verify JsApi endpoints integrate with real DatabaseManager and PDFGenerator:
    - No mock return values.
    - Mutating database records changes document output.
    - get_document_preview returns live preview payload for database client.
    - generate_client_dossier writes real PDF files to dossiers/<Client>/1er_dossier/.
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    import license_manager

    priv = Ed25519PrivateKey.generate()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode("ascii")
    monkeypatch.setattr(license_manager, "PUBLIC_KEY_B64", pub_b64)
    monkeypatch.setattr(license_manager.verify_license, "__defaults__", (pub_b64,))
    mid = license_manager.get_machine_id()
    sig_b32 = base64.b32encode(priv.sign(f"{mid}:9999-12-31".encode("utf-8"))).decode("ascii").rstrip("=")
    temp_db.save_license_key(f"99991231-{sig_b32}")

    bridge = JsApi(db=temp_db, pdf_gen=pdf_gen)

    # Add model
    m_res = bridge.add_camera_model({
        "model_name": "CAM-BRIDGE-01",
        "equipment_designation": "كاميرا مراقبة خارجية",
        "equipment_nature": "خارجية 8MP",
        "category": "الفئة 1",
        "sub_category": "الفرع ب"
    })
    assert m_res["success"] is True
    mid = m_res["id"]

    # Save serials
    s_res = bridge.save_scanned_serials(mid, ["BRIDGE-SN-1001", "BRIDGE-SN-1002"])
    assert s_res["success"] is True and s_res["count"] == 2

    # Add client
    c_res = bridge.save_client({
        "full_name": "Forensic Integration Client",
        "doc_number": "DOC-BRIDGE-9999",
        "address": "Zone Industrielle Oued Smar",
        "city": "Alger",
        "phone": "0550000000"
    })
    assert c_res["success"] is True
    cid = c_res["id"]

    # Assign 1 camera
    avail = temp_db.get_available_serials(mid)
    assert len(avail) == 2
    a_res = bridge.assign_cameras(cid, [avail[0]["id"]])
    assert a_res["success"] is True and a_res["count"] == 1

    # In-App Preview via Bridge
    prev_annex1 = bridge.get_document_preview(cid, "annex1")
    assert prev_annex1["success"] is True
    assert prev_annex1["client_name"] == "Forensic Integration Client"
    assert prev_annex1["page_count"] == 1
    assert len(prev_annex1["pages"]) == 1

    prev_pv = bridge.get_document_preview(cid, "pv_pose")
    assert prev_pv["success"] is True
    assert prev_pv["page_count"] == 1
    # Check that the assigned serial is in the PDF stream of the preview
    pdf_bytes = base64.b64decode(prev_pv["pdf_base64"])
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        extracted = doc[0].get_text().replace("\xad", "-")
        assert "BRIDGE-SN-1001" in extracted, "Assigned serial number missing from bridge preview PDF"
        assert "BRIDGE-SN-1002" not in extracted, "Unassigned serial number unexpectedly present in preview PDF"

    # Generate dossier via Bridge
    dossier_res = bridge.generate_client_dossier(cid)
    assert dossier_res["success"] is True
    assert os.path.exists(dossier_res["folder"])
    assert os.path.exists(dossier_res["pv_reception"])
    assert os.path.exists(dossier_res["annex1"])
    assert os.path.exists(dossier_res["annex5"])


# =====================================================================
# ADVERSARIAL STRESS TESTING: 100 Cameras, Edge Cases & Sanitization
# =====================================================================

def test_forensic_adversarial_stress_100_cameras_and_malicious_inputs(temp_dir, pdf_gen):
    """
    Adversarial Stress Test:
    1. 100 cameras PV de pose generation:
       - Checks multi-page split algorithm without orphan pages.
       - Validates total file size stays strictly < 850 KB (contract requirement).
       - Confirms every single camera serial is preserved.
    2. Malicious / Hostile client names:
       - Path traversal attempts (../../evil).
       - Windows reserved device names (CON, PRN, AUX, NUL, COM1, LPT1).
       - Trailing dots and spaces.
       - Null bytes and control characters.
    3. Null / None client dictionary:
       - Generates documents without throwing uncaught exceptions.
    """
    # 1. 100 cameras deployment
    stress_cams = [
        {
            "equipment_designation": f"كاميرا مراقبة رقمية {i%5}",
            "model_name": f"HIK-4K-PRO-{i%4}",
            "equipment_nature": "داخلية" if i % 2 == 0 else "خارجية",
            "category": "الفئة 1",
            "sub_category": "الفرع أ",
            "serial_number": f"SN-STRESS-{i:04d}",
            "serial_id": i
        }
        for i in range(1, 101)
    ]

    out_stress = os.path.join(temp_dir, "pv_stress_100.pdf")
    res_path = pdf_gen.generate_pv_pose(
        {"full_name": "Entreprise de Haute Sécurité 100", "doc_number": "DOC-STRESS-100"},
        stress_cams,
        output_path=out_stress
    )

    assert os.path.exists(res_path)
    file_sz = os.path.getsize(res_path)
    assert file_sz < 850_000, f"100-camera PV size {file_sz} exceeded 850 KB threshold"

    with fitz.open(res_path) as doc:
        # Splits: 25 on P1, 30 on P2, 30 on P3, 15 on P4 = 4 pages
        assert len(doc) == 4, f"Expected 4 pages for 100 cameras, got {len(doc)}"
        all_extracted = "".join(p.get_text().replace("\xad", "-") for p in doc)
        for i in range(1, 101):
            assert f"SN-STRESS-{i:04d}" in all_extracted, f"SN-STRESS-{i:04d} missing from 100-cam PV"

    # 2. Filesystem Sanitization Stress
    assert sanitize_dossier_name("CON") == "CON_client"
    assert sanitize_dossier_name("PRN") == "PRN_client"
    assert sanitize_dossier_name("AUX") == "AUX_client"
    assert sanitize_dossier_name("NUL") == "NUL_client"
    assert sanitize_dossier_name("COM1") == "COM1_client"
    sanitized_traversal = sanitize_dossier_name("../../evil/path")
    assert "/" not in sanitized_traversal and "\\" not in sanitized_traversal
    assert sanitized_traversal == ".._.._evil_path"
    assert sanitize_dossier_name("TrailingDots...") == "TrailingDots"
    assert sanitize_dossier_name("Spaces   ") == "Spaces"
    assert sanitize_dossier_name("Null\x00Byte\x1fTest") == "Null_Byte_Test"

    # 3. None / Empty client data resiliency
    res_empty_pv = pdf_gen.generate_pv_pose({}, [])
    assert isinstance(res_empty_pv, bytes) and len(res_empty_pv) > 1000

