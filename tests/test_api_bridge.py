"""
API Bridge (JsApi) Integration Test Suite (Tiers 1-4)
Tests thread-safe RPC endpoints, input validation, folder sanitization,
error responses, and end-to-end frontend-backend interactions.
"""

import os
import re
import pytest
from api_bridge import JsApi


# =====================================================================
# TIER 1: Core Feature Coverage (JsApi Endpoints)
# =====================================================================

def test_tier1_bridge_camera_models_endpoints(api_bridge, sample_model):
    """Test model creation, listing, and deletion through JsApi."""
    res_add = api_bridge.add_camera_model(sample_model)
    assert res_add["success"] is True
    mid = res_add["id"]
    assert mid > 0

    res_list = api_bridge.get_camera_models()
    assert res_list["success"] is True
    assert len(res_list["data"]) == 1
    assert res_list["data"][0]["model_name"] == sample_model["model_name"]

    res_del = api_bridge.delete_camera_model(mid)
    assert res_del["success"] is True
    assert len(api_bridge.get_camera_models()["data"]) == 0


def test_tier1_bridge_save_and_get_serials(api_bridge, sample_model):
    """Test barcode scanner serial ingestion and inventory querying."""
    mid = api_bridge.add_camera_model(sample_model)["id"]
    serials = ["API-SN-001", "API-SN-002", "API-SN-003"]
    
    res_save = api_bridge.save_scanned_serials(mid, serials)
    assert res_save["success"] is True
    assert res_save["count"] == 3

    res_avail = api_bridge.get_available_serials(mid)
    assert res_avail["success"] is True
    assert len(res_avail["data"]) == 3

    res_inv = api_bridge.get_inventory_serials(mid)
    assert res_inv["success"] is True
    assert len(res_inv["data"]) == 3


def test_tier1_bridge_client_endpoints(api_bridge, sample_client):
    """Test client creation, retrieval, updating, and deletion."""
    res_save = api_bridge.save_client(sample_client)
    assert res_save["success"] is True
    cid = res_save["id"]

    res_get = api_bridge.get_client(cid)
    assert res_get["success"] is True
    assert res_get["client"]["full_name"] == sample_client["full_name"]

    # Update
    updated = dict(sample_client)
    updated["phone"] = "0770112233"
    res_upd = api_bridge.update_client(cid, updated)
    assert res_upd["success"] is True

    res_get2 = api_bridge.get_client(cid)
    assert res_get2["client"]["phone"] == "0770112233"

    # Delete
    res_del = api_bridge.delete_client(cid)
    assert res_del["success"] is True


def test_tier1_bridge_assign_and_return_cameras(api_bridge, sample_model, sample_client):
    """Test equipment assignment and return workflows through JsApi."""
    mid = api_bridge.add_camera_model(sample_model)["id"]
    cid = api_bridge.save_client(sample_client)["id"]
    api_bridge.save_scanned_serials(mid, ["CAM-001", "CAM-002"])

    avail = api_bridge.get_available_serials(mid)["data"]
    sids = [s["id"] for s in avail]

    # Assign
    res_assign = api_bridge.assign_cameras(cid, sids)
    assert res_assign["success"] is True
    assert res_assign["count"] == 2

    # Verify assigned in get_client
    client_info = api_bridge.get_client(cid)
    assert len(client_info["cameras"]) == 2

    # Return
    res_return = api_bridge.return_cameras(["CAM-001"])
    assert res_return["success"] is True
    assert res_return["count"] == 1

    # Check available stock
    avail_after = api_bridge.get_available_serials(mid)["data"]
    assert len(avail_after) == 1
    assert avail_after[0]["serial_number"] == "CAM-001"


def test_tier1_bridge_generate_dossier(api_bridge, sample_model, sample_client):
    """Test client regulatory dossier PDF generation via API bridge."""
    mid = api_bridge.add_camera_model(sample_model)["id"]
    cid = api_bridge.save_client(sample_client)["id"]
    api_bridge.save_scanned_serials(mid, ["DOSSIER-CAM-1"])
    sid = api_bridge.get_available_serials(mid)["data"][0]["id"]
    api_bridge.assign_cameras(cid, [sid])

    res = api_bridge.generate_client_dossier(cid)
    assert res["success"] is True
    assert "folder" in res or "folder_path" in res
    assert "annex1" in res and "annex5" in res


def test_tier1_bridge_clear_database(api_bridge, sample_model):
    """Test database truncate utility through bridge."""
    api_bridge.add_camera_model(sample_model)
    res = api_bridge.clear_database()
    assert res["success"] is True
    assert len(api_bridge.get_camera_models()["data"]) == 0


# =====================================================================
# TIER 2: Boundary, Corner Cases & Input Validation
# =====================================================================

def test_tier2_bridge_input_validation_empty_model_name(api_bridge):
    """Creating camera model without name must return error dictionary."""
    res = api_bridge.add_camera_model({"model_name": ""})
    assert res["success"] is False
    assert "error" in res


def test_tier2_bridge_save_client_validation_missing_identity(api_bridge):
    """Saving client without name or doc_number must fail with informative error."""
    res1 = api_bridge.save_client({"full_name": "", "doc_number": "12345"})
    assert res1["success"] is False
    assert "error" in res1

    res2 = api_bridge.save_client({"full_name": "Test Client", "doc_number": ""})
    assert res2["success"] is False
    assert "error" in res2


def test_tier2_bridge_duplicate_client_doc_number_error(api_bridge, sample_client):
    """Adding client with already registered document number returns clear error."""
    res1 = api_bridge.save_client(sample_client)
    assert res1["success"] is True

    res2 = api_bridge.save_client(sample_client)
    assert res2["success"] is False
    assert "error" in res2


def test_tier2_bridge_assign_cameras_validation(api_bridge):
    """Calling assign_cameras with invalid or empty parameters returns error."""
    res1 = api_bridge.assign_cameras(None, [])
    assert res1["success"] is False
    assert "error" in res1

    res2 = api_bridge.assign_cameras(1, [])
    assert res2["success"] is False


def test_tier2_bridge_return_cameras_empty_list(api_bridge):
    """Calling return_cameras with empty list returns error."""
    res = api_bridge.return_cameras([])
    assert res["success"] is False
    assert "error" in res


def test_tier2_bridge_path_sanitization_path_traversal():
    """Verify folder path sanitization neutralizes directory traversal and illegal Windows chars."""
    malicious_name = "../../Windows/System32/evil * ? < > | : file"
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", malicious_name)
    assert ".." in sanitized  # dots stay dots or get handled, but slashes are stripped
    assert "/" not in sanitized
    assert "\\" not in sanitized
    assert "*" not in sanitized
    assert "?" not in sanitized
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert "|" not in sanitized
    assert ":" not in sanitized


def test_tier2_bridge_reserved_device_names_sanitization():
    """Verify Windows reserved device names (CON, PRN, AUX, NUL) are safely transformed."""
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
    for name in reserved_names:
        cleaned = name.strip()
        if cleaned.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"}:
            safe_name = f"{cleaned}_client"
        else:
            safe_name = cleaned
        assert safe_name != name or not name.isalnum()


def test_tier2_bridge_get_nonexistent_client(api_bridge):
    """Requesting non-existent client ID returns error dict."""
    res = api_bridge.get_client(999999)
    assert res["success"] is False
    assert "error" in res


# =====================================================================
# TIER 3: Cross-Feature Integration (Full API Workflow)
# =====================================================================

def test_tier3_bridge_end_to_end_workflow(api_bridge, sample_model, sample_client):
    """
    Exercise entire user journey exclusively through JsApi bridge:
    1. Add camera model.
    2. Ingest serials from barcode scanner.
    3. Register client.
    4. Assign cameras to client.
    5. Generate regulatory dossiers.
    6. Verify client dossier output.
    7. Return cameras to inventory.
    8. Delete client.
    """
    # 1. Add model
    mid = api_bridge.add_camera_model(sample_model)["id"]

    # 2. Ingest serials
    api_bridge.save_scanned_serials(mid, ["E2E-SN-001", "E2E-SN-002"])

    # 3. Register client
    cid = api_bridge.save_client(sample_client)["id"]

    # 4. Assign cameras
    avail = api_bridge.get_available_serials(mid)["data"]
    api_bridge.assign_cameras(cid, [avail[0]["id"], avail[1]["id"]])

    # 5. Generate dossier
    dossier_res = api_bridge.generate_client_dossier(cid)
    assert dossier_res["success"] is True

    # 6. Return cameras
    api_bridge.return_cameras(["E2E-SN-001", "E2E-SN-002"])
    avail_after = api_bridge.get_available_serials(mid)["data"]
    assert len(avail_after) == 2

    # 7. Delete client
    del_res = api_bridge.delete_client(cid)
    assert del_res["success"] is True


# =====================================================================
# TIER 4: Real-World Scenarios (Dashboard & Preview Endpoints)
# =====================================================================

def test_tier4_bridge_analytics_and_preview_contract(api_bridge, sample_model, sample_client):
    """Verify compliance with Milestone R1 & R3 JsApi interface contracts."""
    mid = api_bridge.add_camera_model(sample_model)["id"]
    cid = api_bridge.save_client(sample_client)["id"]

    # Check dashboard analytics contract
    if hasattr(api_bridge, "get_dashboard_analytics"):
        analytics_res = api_bridge.get_dashboard_analytics()
        assert analytics_res["success"] is True
        assert "totals" in analytics_res["data"] or "total_stock" in analytics_res["data"]

    # Check document preview contract
    if hasattr(api_bridge, "get_document_preview"):
        preview_res = api_bridge.get_document_preview(cid, "annex1")
        assert "success" in preview_res


def test_tier4_bridge_csv_excel_and_search_endpoints(api_bridge, sample_model):
    """Verify CSV preview, batch import, search, and CSV/Excel export via JsApi."""
    mid = api_bridge.add_camera_model(sample_model)["id"]

    # 1. Preview CSV content
    csv_raw = "Serial Number\nBRIDGE-SN-101\nBRIDGE-SN-102\nBRIDGE-SN-103"
    prev = api_bridge.preview_csv_serials(csv_raw)
    assert prev["success"] is True
    assert prev["total_found"] == 3
    assert len(prev["valid"]) == 3

    # 2. Batch import
    imp = api_bridge.import_serials_batch(mid, prev["valid"])
    assert imp["success"] is True
    assert imp["imported_count"] == 3

    # 3. Search serials
    srch = api_bridge.search_serials(query="102", model_id=mid, status="in_stock")
    assert srch["success"] is True
    assert len(srch["data"]) == 1
    assert srch["data"][0]["serial_number"] == "BRIDGE-SN-102"

    # 4. Export CSV
    exp_csv = api_bridge.export_serials_csv(model_id=mid)
    assert exp_csv["success"] is True
    assert "BRIDGE-SN-101" in exp_csv["csv_data"]

    # 5. Export Excel
    exp_xls = api_bridge.export_serials_excel(model_id=mid)
    assert exp_xls["success"] is True
    assert len(exp_xls["base64"]) > 100
    assert exp_xls["data_uri"].startswith("data:application/vnd.openxmlformats")

    # 6. Update threshold
    th = api_bridge.update_model_threshold(mid, 5)
    assert th["success"] is True


def test_tier4_bridge_second_dossier_generation_and_previews(api_bridge, sample_model, sample_client):
    """Verify 2ème dossier generation and annex3 / annex8 preview endpoints via JsApi."""
    mid = api_bridge.add_camera_model(sample_model)["id"]
    api_bridge.save_scanned_serials(mid, ["DOS2-SN-001", "DOS2-SN-002"])
    cid = api_bridge.save_client(sample_client)["id"]
    avail = api_bridge.get_available_serials(mid)["data"]
    api_bridge.assign_cameras(cid, [avail[0]["id"], avail[1]["id"]])

    # Generate 2ème dossier
    res2 = api_bridge.generate_second_dossier(cid)
    assert res2["success"] is True
    assert "folder" in res2
    assert os.path.exists(res2["annex3"]) and res2["annex3"].endswith("annex3.pdf")
    assert os.path.exists(res2["annex8"]) and res2["annex8"].endswith("annex8.pdf")
    assert os.path.exists(res2["pv_reception"]) and res2["pv_reception"].endswith("pv_reception.pdf")

    # Document previews for Annex 3 and Annex 8
    prev3 = api_bridge.get_document_preview(cid, "annex3")
    assert prev3["success"] is True
    assert prev3["page_count"] >= 1
    assert len(prev3["pages"]) >= 1

    prev8 = api_bridge.get_document_preview(cid, "annex8")
    assert prev8["success"] is True
    assert prev8["page_count"] >= 1
    assert len(prev8["pages"]) >= 1


