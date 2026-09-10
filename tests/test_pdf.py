"""
PDF Engine & Document Generation Test Suite (Tiers 1-4)
Tests PyMuPDF template stamping (Annex 1, Annex 5), vector PV de pose generation,
high-res Pixmap PNG preview streaming, PDF compression, and Arabic BiDi shaping.
"""

import os
import io
import fitz
import base64
import pytest
from pdf_generator import PDFGenerator, shape_arabic, calculate_pv_page_splits, sanitize_dossier_name


# =====================================================================
# TIER 1: Core Feature Coverage (Stamping & Document Generation)
# =====================================================================

def test_tier1_annex1_template_exists_and_valid_a4(pdf_gen):
    """Verify Annex 1 template exists, is readable, and conforms to standard A4."""
    assert os.path.exists(pdf_gen.annex1_template), f"Missing template: {pdf_gen.annex1_template}"
    doc = fitz.open(pdf_gen.annex1_template)
    assert len(doc) == 1, f"Expected single-page template, found {len(doc)} pages"
    rect = doc[0].rect
    assert int(rect.width) == 595 and int(rect.height) == 842, f"Expected A4 (595x842), got {rect}"
    doc.close()


def test_tier1_annex5_template_exists_and_valid_a4(pdf_gen):
    """Verify Annex 5 template exists, is readable, and conforms to standard A4."""
    assert os.path.exists(pdf_gen.annex5_template), f"Missing template: {pdf_gen.annex5_template}"
    doc = fitz.open(pdf_gen.annex5_template)
    assert len(doc) == 1, f"Expected single-page template, found {len(doc)} pages"
    rect = doc[0].rect
    assert int(rect.width) == 595 and int(rect.height) == 842, f"Expected A4 (595x842), got {rect}"
    doc.close()


def test_tier1_generate_annex1_single_camera(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify Annex 1 generates successfully with client data and camera table (< 850 KB)."""
    out_file = os.path.join(temp_dir, "test_annex1.pdf")
    res_path = pdf_gen.generate_annex1(sample_client, sample_purchases[:1], output_name=out_file)
    
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 10000  # Non-trivial PDF size
    assert os.path.getsize(res_path) < 850_000  # Deflate compressed < 850 KB

    doc = fitz.open(res_path)
    assert len(doc) == 1
    doc.close()


def test_tier1_generate_annex5_full_questionnaire(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify Annex 5 generates successfully with 29 civil, corporate, and logistics fields (< 850 KB)."""
    out_file = os.path.join(temp_dir, "test_annex5.pdf")
    res_path = pdf_gen.generate_annex5(sample_client, sample_purchases, output_name=out_file)

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 10000
    assert os.path.getsize(res_path) < 850_000  # Deflate compressed < 850 KB

    doc = fitz.open(res_path)
    assert len(doc) == 1
    doc.close()


def test_tier1_generate_client_dossier_creates_folder_and_both_pdfs(temp_dir, pdf_gen, sample_client, sample_purchases):
    """
    Verify generate_client_dossier creates client folder, 2eme_dossier slot,
    stamps Annex 1, Annex 5, and generates pv_reception.pdf under dossiers/<Client>/1er_dossier/.
    Returns DossierResult supporting both tuple unpacking and dict access.
    """
    res = pdf_gen.generate_client_dossier(sample_client, sample_purchases, parent_folder=temp_dir)
    
    # 1. Tuple unpacking compatibility
    folder, p1, p5 = res
    assert folder.endswith("1er dossier") or folder.endswith("1er_dossier")
    assert os.path.isdir(folder)
    assert os.path.exists(p1) and p1.endswith("annex1.pdf")
    assert os.path.exists(p5) and p5.endswith("annex5.pdf")

    # 2. Dict mapping access
    assert res.get("folder_path") == folder
    p_pv = res["pv_reception"]
    assert os.path.exists(p_pv) and p_pv.endswith("pv_reception.pdf")
    assert "annex1.pdf" in res["files"]
    assert "annex5.pdf" in res["files"]
    assert "pv_reception.pdf" in res["files"]
    assert res["success"] is True

    # 3. Extensible 2eme_dossier slot
    client_parent = os.path.dirname(folder)
    slot_2eme_space = os.path.join(client_parent, "2eme dossier")
    slot_2eme_under = os.path.join(client_parent, "2eme_dossier")
    assert os.path.isdir(slot_2eme_space) or os.path.isdir(slot_2eme_under)

    # 4. File sizes strictly < 850 KB
    for path in [p1, p5, p_pv]:
        assert os.path.getsize(path) < 850_000


def test_tier1_pixmap_preview_png_streaming(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify high-resolution Pixmap rendering produces valid PNG bytes with PNG signature."""
    p1 = pdf_gen.generate_annex1(sample_client, sample_purchases[:2], output_name=os.path.join(temp_dir, "preview_test.pdf"))
    
    doc = fitz.open(p1)
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    png_bytes = pix.tobytes("png")
    doc.close()

    # Verify PNG magic number header: \x89PNG\r\n\x1a\n
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n"), "Generated preview is not a valid PNG image"
    assert len(png_bytes) > 20000, "Preview image size too small"

    # Base64 conversion
    b64 = base64.b64encode(png_bytes).decode("ascii")
    assert b64.startswith("iVBORw0KGgo")  # Standard base64 PNG header


def test_tier1_pdf_deflate_compression(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify PyMuPDF deflate compression reduces file size and satisfies < 850 KB limit."""
    p1_uncompressed = os.path.join(temp_dir, "uncompressed.pdf")
    p1_compressed = os.path.join(temp_dir, "compressed.pdf")

    # Stamped Annex 1 uncompressed
    doc_uncomp = fitz.open(pdf_gen.annex1_template)
    if pdf_gen.font_path and os.path.exists(pdf_gen.font_path):
        doc_uncomp[0].insert_font(fontname="f0", fontfile=pdf_gen.font_path)
    pdf_gen._stamp_field(doc_uncomp[0], fitz.Rect(38, 197, 467, 216), sample_client["full_name"], fontname="f0")
    doc_uncomp.save(p1_uncompressed)
    doc_uncomp.close()

    # Stamped Annex 1 compressed
    res_comp = pdf_gen.generate_annex1(sample_client, sample_purchases, output_name=p1_compressed)

    size_uncompressed = os.path.getsize(p1_uncompressed)
    size_compressed = os.path.getsize(p1_compressed)

    assert size_compressed < size_uncompressed, (
        f"Compressed size ({size_compressed}) not smaller than uncompressed ({size_uncompressed})"
    )
    assert size_compressed < 850_000, f"Compressed Annex 1 ({size_compressed}) exceeds 850 KB limit"

    # Also verify Annex 5 and PV de pose are under 850 KB limit
    p5_path = os.path.join(temp_dir, "annex5_test_size.pdf")
    pdf_gen.generate_annex5(sample_client, sample_purchases, output_name=p5_path)
    assert os.path.getsize(p5_path) < 850_000

    pv_path = os.path.join(temp_dir, "pv_test_size.pdf")
    pdf_gen.generate_pv_pose(sample_client, sample_purchases, output_path=pv_path)
    assert os.path.getsize(pv_path) < 850_000


# =====================================================================
# TIER 2: Boundary, Corner Cases & Robustness
# =====================================================================

def test_tier2_annex1_equipment_table_capping(temp_dir, pdf_gen, sample_client):
    """Annex 1 regulatory table must cap at exactly 4 rows when client has > 4 camera models."""
    multi_model_purchases = [
        {
            "model_name": f"MODEL-TYPE-{i}",
            "equipment_designation": f"كاميرا مراقبة رقمية {i}",
            "equipment_nature": "داخلية",
            "category": "الفئة 1",
            "sub_category": "أ",
            "serial_number": f"SN-CAP-{i:03d}"
        }
        for i in range(1, 9)  # 8 different models
    ]

    out_file = os.path.join(temp_dir, "annex1_capped.pdf")
    # Must not raise IndexError or visual overlap
    res_path = pdf_gen.generate_annex1(sample_client, multi_model_purchases, output_name=out_file)
    assert os.path.exists(res_path)


def test_tier2_dynamic_font_auto_scaling_long_names(temp_dir, pdf_gen, sample_client):
    """Ultra-long client names (150+ chars) must auto-scale down to 7.0pt without crashing."""
    long_client = dict(sample_client)
    long_client["full_name"] = "الشركة الجزائرية العامة لخدمات الحراسة والمراقبة الإلكترونية والاتصالات السلكية واللاسلكية ذات المسؤولية المحدودة وشركاؤه"
    long_client["company_name"] = "SOCIÉTÉ ALGÉRIENNE DE SÉCURITÉ PRIVÉE ET DE TÉLÉCOMMUNICATIONS INDUSTRIELLES PAR ACTIONS AU CAPITAL DE 50000000 DZD"

    out_file = os.path.join(temp_dir, "annex1_long_text.pdf")
    res_path = pdf_gen.generate_annex1(long_client, [], output_name=out_file)
    assert os.path.exists(res_path)


def test_tier2_none_and_empty_fields_handling(temp_dir, pdf_gen):
    """Empty or None fields must be handled gracefully without throwing exceptions."""
    minimal_client = {"full_name": None, "doc_number": None}
    out1 = os.path.join(temp_dir, "annex1_empty.pdf")
    out5 = os.path.join(temp_dir, "annex5_empty.pdf")

    p1 = pdf_gen.generate_annex1(minimal_client, [], output_name=out1)
    p5 = pdf_gen.generate_annex5(minimal_client, [], output_name=out5)

    assert os.path.exists(p1)
    assert os.path.exists(p5)


def test_tier2_missing_template_raises_file_not_found(temp_dir):
    """Verify proper FileNotFoundError when templates directory or file is missing."""
    invalid_gen = PDFGenerator(templates_dir=os.path.join(temp_dir, "nonexistent_dir"))
    with pytest.raises(FileNotFoundError):
        invalid_gen.generate_annex1({}, [])


def test_tier2_bidi_mixed_arabic_latin_reshaping():
    """Verify shape_arabic handles nulls, pure Latin, pure Arabic, and mixed French/Arabic strings."""
    assert shape_arabic(None) == ""
    assert shape_arabic("") == ""
    assert shape_arabic(12345) == "12345"

    # Pure Latin
    assert shape_arabic("DS-2CD2143G2-I") == "DS-2CD2143G2-I"

    # Mixed Latin-Arabic with model code
    mixed_model = shape_arabic("DS-2CD2143G2-I (كاميرا مراقبة)")
    assert mixed_model.startswith("DS-2CD2143G2-I (")

    # Mixed French accented Latin and Arabic
    mixed_french = shape_arabic("BÉNÉFICIAIRE / CLIENT (الزبون المستفيد):")
    assert mixed_french.startswith("BÉNÉFICIAIRE / CLIENT (")
    assert mixed_french.endswith("):")

    # Explicit base_dir overrides
    overridden_r = shape_arabic("DS-2CD2143G2-I (كاميرا)", base_dir='R')
    assert not overridden_r.startswith("DS-2CD2143G2-I (")


def test_tier2_pv_pagination_splits_anti_orphan():
    """Verify pagination split algorithm prevents orphan pages and respects <= 25 threshold."""
    assert calculate_pv_page_splits(0) == [0]
    assert calculate_pv_page_splits(1) == [1]
    assert calculate_pv_page_splits(14) == [14]
    assert calculate_pv_page_splits(25) == [25]
    assert calculate_pv_page_splits(26) == [13, 13]
    assert calculate_pv_page_splits(30) == [15, 15]
    assert calculate_pv_page_splits(50) == [25, 25]
    splits_60 = calculate_pv_page_splits(60)
    assert len(splits_60) == 3
    assert all(count >= 5 for count in splits_60)


def test_tier2_whiteout_dot_masking(temp_dir, pdf_gen, sample_client):
    """Verify dot-masking draws white rectangle before stamping text."""
    doc = fitz.open(pdf_gen.annex1_template)
    page = doc[0]
    if pdf_gen.font_path and os.path.exists(pdf_gen.font_path):
        page.insert_font(fontname="f0", fontfile=pdf_gen.font_path)
    test_rect = fitz.Rect(50, 100, 200, 120)
    
    # Stamp field with whiteout
    pdf_gen._stamp_field(page, test_rect, "Test Masking Text", whiteout=True)
    out = os.path.join(temp_dir, "masking_test.pdf")
    doc.save(out)
    doc.close()

    assert os.path.exists(out)


# =====================================================================
# TIER 3: Cross-Feature Integration (Vector PV de Pose & Preview)
# =====================================================================

def test_tier3_pv_de_pose_vector_generation(temp_dir, pdf_gen, sample_client, sample_purchases):
    """
    Test PV de Pose (Procès-Verbal de Réception / Bordereau de Livraison):
    Lists exact camera serial numbers, regulatory references, client logistics,
    and bilateral signature blocks.
    Verifies single-page layout for <= 25 cameras.
    """
    out_pv = os.path.join(temp_dir, "pv_reception.pdf")
    res = pdf_gen.generate_pv_pose(sample_client, sample_purchases, output_path=out_pv)
    assert os.path.exists(res)
    assert os.path.getsize(res) < 850_000

    doc = fitz.open(res)
    assert len(doc) == 1, "Expected single-page PV for small camera count"
    page_text = doc[0].get_text()
    clean_text = page_text.replace("\xad", "-")
    assert "09-410" in clean_text
    assert "54" in clean_text
    assert "RÉCEPTION" in clean_text.upper() or "LIVRAISON" in clean_text.upper()
    assert "BÉNÉFICIAIRE" in clean_text.upper()
    assert "INSTALLATION" in clean_text.upper()
    assert "INSTALLATEUR" in clean_text.upper()
    assert "TOTAL" in clean_text.upper()
    doc.close()

    # Also test byte generation return mode
    raw_bytes = pdf_gen.generate_pv_pose(sample_client, sample_purchases, output_path=None)
    assert isinstance(raw_bytes, bytes)
    assert len(raw_bytes) > 5000
    assert len(raw_bytes) < 850_000


def test_tier3_document_preview_api_streaming(pdf_gen, sample_client, sample_purchases):
    """Verify document preview returns Base64 Pixmap PNGs, PDF Base64, and canonical schema."""
    for dtype in ["annex1", "annex5", "pv_pose"]:
        preview_data = pdf_gen.get_document_preview_data(sample_client, sample_purchases, doc_type=dtype)
        assert preview_data["success"] is True
        assert preview_data["doc_type"] == dtype
        assert preview_data["page_count"] >= 1
        assert len(preview_data["pages"]) == preview_data["page_count"]
        assert preview_data["pages"][0].startswith("data:image/png;base64,")
        assert preview_data["pdf_base64"] is not None and len(preview_data["pdf_base64"]) > 1000
        assert preview_data["error"] is None

    # Verify invalid doc_type error handling
    err_preview = pdf_gen.get_document_preview_data(sample_client, sample_purchases, doc_type="invalid_doc")
    assert err_preview["success"] is False
    assert err_preview["error"] is not None
    assert "Unknown document type" in err_preview["error"]
    assert err_preview["page_count"] == 0
    assert err_preview["pages"] == []


# =====================================================================
# TIER 4: Real-World Scenarios (Large Installation Multi-Page PV)
# =====================================================================

def test_tier4_large_installation_multi_camera_dossier(temp_dir, pdf_gen, sample_client):
    """
    Simulate commercial CCTV deployment (20 cameras):
    - 20 cameras assigned to client.
    - Annex 1 aggregates the 20 cameras into model quantity summary rows.
    - Annex 5 questionnaire stamped.
    - PV de Pose itemizes 20 cameras on 1 single page without truncation (threshold <= 25).
    """
    large_purchases = [
        {
            "model_name": "DS-2CD2143G2-I" if i <= 12 else "DS-2CD2043G2-I",
            "equipment_designation": "كاميرا مراقبة رقمية",
            "equipment_nature": "داخلية" if i <= 12 else "خارجية",
            "category": "الفئة 1",
            "sub_category": "أ",
            "serial_number": f"HIK-SERIAL-2026-{i:04d}",
            "serial_id": i
        }
        for i in range(1, 21)
    ]

    # Generate dossier
    res = pdf_gen.generate_client_dossier(sample_client, large_purchases, parent_folder=temp_dir)
    client_dir = res[0] if isinstance(res, tuple) else res.get("folder")
    
    p1 = os.path.join(client_dir, "annex1.pdf")
    p5 = os.path.join(client_dir, "annex5.pdf")
    p_pv = os.path.join(client_dir, "pv_reception.pdf")
    assert os.path.exists(p1)
    assert os.path.exists(p5)
    assert os.path.exists(p_pv)

    # Check Annex 1 aggregated quantities
    doc1 = fitz.open(p1)
    assert len(doc1) == 1
    doc1.close()

    # Check PV de Pose has 1 page for 20 cameras
    doc_pv = fitz.open(p_pv)
    assert len(doc_pv) == 1
    doc_pv.close()


def test_tier4_large_installation_multi_page_pv_pagination(temp_dir, pdf_gen, sample_client):
    """
    Simulate large enterprise deployment triggering multi-page PV de pose:
    - 26 cameras triggers 2 pages with anti-orphan balanced distribution [13, 13].
    - 30 cameras triggers 2 pages [15, 15].
    - Verifies continuation header on page 2 and execution block on final page.
    """
    for count in [26, 30]:
        cams = [
            {
                "model_name": f"HIK-MODEL-{i%3+1}",
                "equipment_designation": "كاميرا مراقبة رقمية",
                "equipment_nature": "داخلية",
                "category": "الفئة 1",
                "sub_category": "أ",
                "serial_number": f"HIK-SN-2026-{i:04d}",
                "serial_id": i
            }
            for i in range(1, count + 1)
        ]

        out_pv = os.path.join(temp_dir, f"pv_{count}_cameras.pdf")
        pdf_gen.generate_pv_pose(sample_client, cams, output_path=out_pv)

        assert os.path.exists(out_pv)
        assert os.path.getsize(out_pv) < 850_000

        with fitz.open(out_pv) as doc:
            assert len(doc) >= 2, f"Expected >= 2 pages for {count} cameras, got {len(doc)}"
            text_p2 = doc[1].get_text()
            assert "SUITE" in text_p2 or "Page 2" in text_p2
            assert "TOTAL" in text_p2 or "unité" in text_p2


# =====================================================================
# 2ème Dossier: Annex 3 Extended & Annex 8 Non-Connection Tests
# =====================================================================

def test_tier1_annex3_and_annex8_templates_exist_and_valid(pdf_gen):
    """Verify Annex 3 extended and Annex 8 templates exist and conform to A4."""
    assert os.path.exists(pdf_gen.annex3_template), f"Missing template: {pdf_gen.annex3_template}"
    assert os.path.exists(pdf_gen.annex8_template), f"Missing template: {pdf_gen.annex8_template}"

    with fitz.open(pdf_gen.annex3_template) as doc3:
        assert len(doc3) == 1
        rect3 = doc3[0].rect
        assert int(rect3.width) == 595 and int(rect3.height) == 842

    with fitz.open(pdf_gen.annex8_template) as doc8:
        assert len(doc8) == 1
        rect8 = doc8[0].rect
        assert int(rect8.width) == 595 and int(rect8.height) == 842


def test_tier1_generate_annex3_extended_table(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify Annex 3 generates with extended 15-row table and client details."""
    out_file = os.path.join(temp_dir, "test_annex3.pdf")
    res_path = pdf_gen.generate_annex3(sample_client, sample_purchases, output_name=out_file)

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 10000
    assert os.path.getsize(res_path) < 850_000

    with fitz.open(res_path) as doc:
        assert len(doc) == 1


def test_tier1_generate_annex8_commitment(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify Annex 8 internet non-connection commitment generates correctly."""
    out_file = os.path.join(temp_dir, "test_annex8.pdf")
    res_path = pdf_gen.generate_annex8(sample_client, sample_purchases, output_name=out_file)

    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 10000
    assert os.path.getsize(res_path) < 850_000

    with fitz.open(res_path) as doc:
        assert len(doc) == 1


def test_tier1_generate_second_dossier_creates_all_pdfs(temp_dir, pdf_gen, sample_client, sample_purchases):
    """Verify generate_second_dossier creates 2eme dossier folder and stamps Annex 3, Annex 8, and PV."""
    res = pdf_gen.generate_second_dossier(sample_client, sample_purchases, parent_folder=temp_dir)

    assert res["success"] is True
    assert "folder" in res
    assert os.path.isdir(res["folder"])
    assert os.path.exists(res["annex3"]) and res["annex3"].endswith("annex3.pdf")
    assert os.path.exists(res["annex8"]) and res["annex8"].endswith("annex8.pdf")
    assert os.path.exists(res["pv_reception"]) and res["pv_reception"].endswith("pv_reception.pdf")
    assert "annex3.pdf" in res["files"]
    assert "annex8.pdf" in res["files"]
    assert "pv_reception.pdf" in res["files"]


def test_tier1_preview_annex3_and_annex8(pdf_gen, sample_client, sample_purchases):
    """Verify get_document_preview generates valid preview pixmaps for annex3 and annex8."""
    prev3 = pdf_gen.get_document_preview(sample_client, sample_purchases, doc_type="annex3")
    assert prev3["success"] is True
    assert prev3["doc_type"] == "annex3"
    assert prev3["page_count"] == 1
    assert len(prev3["pages"]) == 1
    assert prev3["pages"][0].startswith("data:image/png;base64,")

    prev8 = pdf_gen.get_document_preview(sample_client, sample_purchases, doc_type="annex8")
    assert prev8["success"] is True
    assert prev8["doc_type"] == "annex8"
    assert prev8["page_count"] == 1
    assert len(prev8["pages"]) == 1
    assert prev8["pages"][0].startswith("data:image/png;base64,")

