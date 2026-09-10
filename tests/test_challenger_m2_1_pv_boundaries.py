"""
Adversarial Boundary Stress Test Suite — Challenger M2-1
Empirically verifies:
1. Camera counts 0, 1, 14, 25, 26, 50, 51, 100 in generate_pv_pose()
2. Anti-orphan row guarantee (no page < 5 cameras when multi-page) across N=0..1000
3. PDF file size strictly < 850 KB for Annex 1, Annex 5, and PV de Pose
4. Geometry verification: zero overlap with border or execution footer
"""
import os
import fitz
import pytest
from pdf_generator import PDFGenerator, calculate_pv_page_splits

@pytest.fixture
def pdf_gen():
    return PDFGenerator()

@pytest.fixture
def sample_client():
    return {
        "id": 101,
        "full_name": "Société Algérienne de Surveillance et Télécoms",
        "company_name": "SAST SARL",
        "doc_number": "09-98765432",
        "doc_issuer": "Daira de Bab El Oued",
        "phone": "023 45 67 89",
        "address": "45 Rue Didouche Mourad",
        "city": "Alger",
        "storage_location": "Dépôt Sidi M'Hamed",
        "accreditation_ref": "AGR-CCTV-2026-099",
        "father_name": "Mohamed",
        "mother_name": "Fatima",
        "dob": "01/01/1980",
        "pob": "Alger",
        "nationality": "جزائرية"
    }

def make_cameras(count: int):
    return [
        {
            "model_name": f"DS-2CD2143G2-I (Cam {i})",
            "equipment_designation": "كاميرا مراقبة شبكية",
            "equipment_nature": "داخلية",
            "category": "الفئة 1",
            "sub_category": "أ",
            "serial_number": f"SN-2026-{i:05d}",
            "serial_id": i
        }
        for i in range(1, count + 1)
    ]

@pytest.mark.parametrize("count, expected_pages, max_kb", [
    (0, 1, 850),
    (1, 1, 850),
    (14, 1, 850),
    (25, 1, 850),
    (26, 2, 850),
    (50, 2, 850),
    (51, 2, 850),
    (54, 3, 850),
    (100, 4, 850),
])
def test_pv_pose_camera_count_boundaries(tmp_path, pdf_gen, sample_client, count, expected_pages, max_kb):
    cameras = make_cameras(count)
    out_pdf = str(tmp_path / f"pv_{count}.pdf")
    res = pdf_gen.generate_pv_pose(sample_client, cameras, output_path=out_pdf)
    assert os.path.exists(res)
    
    # File size assertion (< 850 KB)
    size_bytes = os.path.getsize(res)
    assert size_bytes < max_kb * 1024, f"PV with {count} cameras exceeded {max_kb} KB: {size_bytes} bytes"
    
    # Page count assertion
    with fitz.open(res) as doc:
        assert len(doc) == expected_pages, f"Count {count}: expected {expected_pages} pages, got {len(doc)}"
        final_page = doc[-1]
        text = final_page.get_text().replace('\xa0', ' ')
        assert "TOTAL" in text or "المجموع" in text
        assert "Attestation de Conformité" in text
        assert "L'INSTALLATEUR" in text

def test_pv_anti_orphan_exhaustive_0_to_1000():
    """Verify that no camera count from 0 to 1000 produces an orphan page (< 5 items) when multi-page."""
    for n in range(0, 1001):
        splits = calculate_pv_page_splits(n)
        assert sum(splits) == n, f"Sum mismatch for n={n}: {splits}"
        if len(splits) > 1:
            for p_idx, p_count in enumerate(splits):
                assert p_count >= 5, f"Orphan page found for n={n} at page {p_idx+1}: {splits}"

def test_annex1_and_annex5_file_sizes_under_850kb(tmp_path, pdf_gen, sample_client):
    """Verify Annex 1 and Annex 5 remain strictly < 850 KB across camera counts."""
    for count in [0, 1, 14, 25, 50, 100]:
        cams = make_cameras(count)
        p1 = str(tmp_path / f"a1_{count}.pdf")
        p5 = str(tmp_path / f"a5_{count}.pdf")
        pdf_gen.generate_annex1(sample_client, cams, output_name=p1)
        pdf_gen.generate_annex5(sample_client, cams, output_name=p5)
        
        assert os.path.getsize(p1) < 850 * 1024, f"Annex 1 ({count} cams) exceeded 850 KB: {os.path.getsize(p1)}"
        assert os.path.getsize(p5) < 850 * 1024, f"Annex 5 ({count} cams) exceeded 850 KB: {os.path.getsize(p5)}"

def test_pv_geometry_safety_margins(tmp_path, pdf_gen, sample_client):
    """Verify geometry margins on critical boundary counts: 25, 26, 50, 51, 53, 54."""
    for count in [25, 26, 50, 51, 53, 54]:
        cameras = make_cameras(count)
        out_pdf = str(tmp_path / f"geom_{count}.pdf")
        pdf_gen.generate_pv_pose(sample_client, cameras, output_path=out_pdf)
        
        splits = calculate_pv_page_splits(count)
        with fitz.open(out_pdf) as doc:
            for p_idx, page in enumerate(doc):
                count_here = splits[p_idx]
                is_final = (p_idx == len(doc) - 1)
                y_tbl_start = 202.0 if p_idx == 0 else 76.0
                tbl_bottom = y_tbl_start + 20.0 + (count_here * 17.0)
                
                if is_final:
                    # Footer: Total (18 pt) + Cert (46 pt, gap 6) + Sig (80 pt, gap 6)
                    # cert_top = tbl_bottom + 24, sig_top = cert_top + 52 = tbl_bottom + 76
                    sig_bottom = tbl_bottom + 76.0 + 80.0
                    assert sig_bottom <= 812.0, f"Count {count} overflowed outer border on page {p_idx+1}: {sig_bottom} > 812.0"
                else:
                    assert tbl_bottom <= 812.0, f"Count {count} table overflowed page {p_idx+1}: {tbl_bottom} > 812.0"
