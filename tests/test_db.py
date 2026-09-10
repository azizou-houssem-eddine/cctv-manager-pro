"""
Comprehensive Database Test Suite (Tiers 1-4)
Tests SQLite schema, CRUD operations, concurrency/WAL mode, composite indexes,
transaction rollback integrity, and executive analytics queries.
"""

import sqlite3
import threading
import pytest
from db_manager import DatabaseManager


# =====================================================================
# TIER 1: Core Feature Coverage (CRUD & Standard Workflows)
# =====================================================================

def test_tier1_db_init_creates_required_tables(temp_db):
    """Verify that all core regulatory tables are properly initialized."""
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    expected = {"camera_models", "clients", "serial_numbers", "client_purchases"}
    assert expected.issubset(tables), f"Missing tables: {expected - tables}"


def test_tier1_camera_models_crud(temp_db, sample_model):
    """Test creation, retrieval, and deletion of regulatory camera models."""
    model_id = temp_db.add_camera_model(
        model_name=sample_model["model_name"],
        equipment_designation=sample_model["equipment_designation"],
        equipment_nature=sample_model["equipment_nature"],
        category=sample_model["category"],
        sub_category=sample_model["sub_category"]
    )
    assert model_id > 0, "Model insertion failed to return valid ID"

    models = temp_db.get_camera_models()
    assert len(models) == 1
    m = models[0]
    assert m["model_name"] == sample_model["model_name"]
    assert m["equipment_designation"] == sample_model["equipment_designation"]
    assert m["equipment_nature"] == sample_model["equipment_nature"]
    assert m["category"] == sample_model["category"]
    assert m["sub_category"] == sample_model["sub_category"]

    # Delete model without assigned serials
    deleted = temp_db.delete_camera_model(model_id)
    assert deleted is True
    assert len(temp_db.get_camera_models()) == 0


def test_tier1_clients_crud_full_29_fields(temp_db, sample_client):
    """Test insertion and full-fidelity retrieval of 29 client fields."""
    client_id = temp_db.add_client(sample_client)
    assert client_id > 0, "Client creation failed"

    client = temp_db.get_client(client_id)
    assert client is not None
    for field, expected_val in sample_client.items():
        assert client[field] == expected_val, f"Mismatch in field '{field}': {client[field]} != {expected_val}"

    # Verify clients list retrieval
    clients_list = temp_db.get_clients()
    assert len(clients_list) == 1
    assert clients_list[0]["id"] == client_id


def test_tier1_client_update(temp_db, sample_client):
    """Test updating existing client fields."""
    client_id = temp_db.add_client(sample_client)
    updated_data = dict(sample_client)
    updated_data["phone"] = "0661998877"
    updated_data["city"] = "وهران"

    ok = temp_db.update_client(client_id, updated_data)
    assert ok is True

    fresh = temp_db.get_client(client_id)
    assert fresh["phone"] == "0661998877"
    assert fresh["city"] == "وهران"


def test_tier1_serial_numbers_batch_save_and_available(temp_db, sample_model):
    """Test batch insertion of serial numbers and stock availability queries."""
    mid = temp_db.add_camera_model(**sample_model)
    serials = ["SN-HIK-001", "SN-HIK-002", "SN-HIK-003", "SN-HIK-004"]
    
    count = temp_db.save_serial_batch(mid, serials)
    assert count == 4

    available = temp_db.get_available_serials(mid)
    assert len(available) == 4
    assert {s["serial_number"] for s in available} == set(serials)

    all_serials = temp_db.get_all_serials(mid)
    assert len(all_serials) == 4
    for s in all_serials:
        assert s["is_used"] == 0


def test_tier1_single_camera_assignment(temp_db, sample_model, sample_client):
    """Test assigning an individual camera to a client."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-ASSIGN-1"])
    
    available = temp_db.get_available_serials(mid)
    sid = available[0]["id"]

    success = temp_db.assign_camera_to_client(cid, sid)
    assert success is True

    # Check that serial is now marked as used
    avail_after = temp_db.get_available_serials(mid)
    assert len(avail_after) == 0

    purchases = temp_db.get_client_purchases_for_pdf(cid)
    assert len(purchases["cameras"]) == 1
    assert purchases["cameras"][0]["serial_number"] == "SN-ASSIGN-1"


def test_tier1_batch_camera_assignment(temp_db, sample_model, sample_client):
    """Test assigning multiple camera serials to a client in batch."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    serials = [f"SN-BATCH-{i:03d}" for i in range(1, 6)]
    temp_db.save_serial_batch(mid, serials)

    available = temp_db.get_available_serials(mid)
    sids = [s["id"] for s in available]

    assigned_count = temp_db.assign_cameras_batch(cid, sids)
    assert assigned_count == 5

    # All should be used
    avail_after = temp_db.get_available_serials(mid)
    assert len(avail_after) == 0

    purchases = temp_db.get_client_purchases_for_pdf(cid)
    assert len(purchases["cameras"]) == 5


def test_tier1_return_cameras_batch(temp_db, sample_model, sample_client):
    """Test returning assigned cameras back into available inventory."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    serials = ["SN-RET-01", "SN-RET-02", "SN-RET-03"]
    temp_db.save_serial_batch(mid, serials)
    
    sids = [s["id"] for s in temp_db.get_available_serials(mid)]
    temp_db.assign_cameras_batch(cid, sids)

    # Return 2 cameras
    returned = temp_db.return_cameras_batch(["SN-RET-01", "SN-RET-02"])
    assert returned == 2

    # Verify inventory counts
    avail_now = temp_db.get_available_serials(mid)
    assert len(avail_now) == 2
    assert {s["serial_number"] for s in avail_now} == {"SN-RET-01", "SN-RET-02"}

    purchases = temp_db.get_client_purchases_for_pdf(cid)
    assert len(purchases["cameras"]) == 1
    assert purchases["cameras"][0]["serial_number"] == "SN-RET-03"


def test_tier1_get_client_purchases_for_pdf(temp_db, sample_model, sample_client):
    """Test joined client purchase records for PDF document stamping."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-PDF-001"])
    sid = temp_db.get_available_serials(mid)[0]["id"]
    temp_db.assign_camera_to_client(cid, sid)

    pdf_data = temp_db.get_client_purchases_for_pdf(cid)
    assert "client" in pdf_data and "cameras" in pdf_data
    assert pdf_data["client"]["full_name"] == sample_client["full_name"]
    assert len(pdf_data["cameras"]) == 1
    cam = pdf_data["cameras"][0]
    assert cam["model_name"] == sample_model["model_name"]
    assert cam["equipment_designation"] == sample_model["equipment_designation"]
    assert cam["serial_number"] == "SN-PDF-001"


def test_tier1_clear_database(temp_db, sample_model, sample_client):
    """Test full database clearing utility."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-CLR-1"])
    
    ok = temp_db.clear_database()
    assert ok is True
    assert len(temp_db.get_camera_models()) == 0
    assert len(temp_db.get_clients()) == 0
    assert len(temp_db.get_all_serials()) == 0


# =====================================================================
# TIER 2: Boundary, Corner Cases & Robustness
# =====================================================================

def test_tier2_client_doc_number_unique_constraint(temp_db, sample_client):
    """Verify that duplicate National ID / Passport numbers are rejected."""
    id1 = temp_db.add_client(sample_client)
    assert id1 > 0

    # Attempt inserting identical doc_number
    id2 = temp_db.add_client(sample_client)
    assert id2 == 0 or id2 is False or id2 is None, "Duplicate doc_number was unexpectedly accepted"
    assert len(temp_db.get_clients()) == 1


def test_tier2_serial_number_unique_constraint(temp_db, sample_model):
    """Verify that duplicate camera serial numbers are not stored twice."""
    mid = temp_db.add_camera_model(**sample_model)
    inserted1 = temp_db.save_serial_batch(mid, ["SN-UNIQUE-99", "SN-UNIQUE-99"])
    assert inserted1 == 1, f"Expected 1 inserted, got {inserted1}"

    # Insert again in subsequent call
    inserted2 = temp_db.save_serial_batch(mid, ["SN-UNIQUE-99"])
    assert inserted2 == 0, f"Expected 0 inserted for duplicate, got {inserted2}"


def test_tier2_delete_model_blocked_by_assigned_cameras(temp_db, sample_model, sample_client):
    """Ensure camera model cannot be deleted if any serial numbers are assigned."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-BLOCK-DEL"])
    sid = temp_db.get_available_serials(mid)[0]["id"]
    temp_db.assign_camera_to_client(cid, sid)

    deleted = temp_db.delete_camera_model(mid)
    assert deleted is False, "Model with assigned cameras was deleted!"
    assert len(temp_db.get_camera_models()) == 1


def test_tier2_delete_client_resets_serials_to_in_stock(temp_db, sample_model, sample_client):
    """Deleting a client must return all assigned cameras back to in_stock (is_used=0)."""
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-RESET-01", "SN-RESET-02"])
    sids = [s["id"] for s in temp_db.get_available_serials(mid)]
    temp_db.assign_cameras_batch(cid, sids)

    # Delete client
    ok = temp_db.delete_client(cid)
    assert ok is True

    # Serials must now be available in stock
    available = temp_db.get_available_serials(mid)
    assert len(available) == 2
    for s in available:
        assert s["serial_number"] in ["SN-RESET-01", "SN-RESET-02"]


def test_tier2_arabic_unicode_preservation(temp_db):
    """Ensure Arabic characters, quotes, and punctuation are stored and queried faithfully."""
    arabic_model = {
        "model_name": "كاميرا-المراقبة-فائقة-الدقة-4K",
        "equipment_designation": "كاميرا مراقبة بصرية رقمية ثابتة (داخلية/خارجية)",
        "equipment_nature": "تجهيزات حساسة خاضعة للمرسوم التنفيذي 09-410",
        "category": "القسم الأول",
        "sub_category": "الفرع الثاني"
    }
    mid = temp_db.add_camera_model(**arabic_model)
    models = temp_db.get_camera_models()
    assert len(models) == 1
    m = models[0]
    assert m["model_name"] == arabic_model["model_name"]
    assert m["equipment_designation"] == arabic_model["equipment_designation"]

    # Search with Arabic query
    client_ar = {
        "full_name": "عبد الرحمن بن محمد البشير",
        "doc_number": "DZ-998877665544",
        "city": "قسنطينة",
        "company_name": "مؤسسة النور لأنظمة المراقبة والحماية"
    }
    cid = temp_db.add_client(client_ar)
    assert cid > 0
    c = temp_db.get_client(cid)
    assert c["full_name"] == "عبد الرحمن بن محمد البشير"
    assert c["company_name"] == "مؤسسة النور لأنظمة المراقبة والحماية"


def test_tier2_empty_and_whitespace_serials_handled(temp_db, sample_model):
    """Verify empty strings or whitespace-only serials are not accepted."""
    mid = temp_db.add_camera_model(**sample_model)
    count = temp_db.save_serial_batch(mid, ["", "   ", "\t\n", "SN-VALID-01"])
    # Only the valid non-empty serial should be inserted
    assert count == 1
    available = temp_db.get_available_serials(mid)
    assert len(available) == 1
    assert available[0]["serial_number"] == "SN-VALID-01"


def test_tier2_foreign_key_enforcement_on_invalid_assignment(temp_db, sample_model):
    """Verify SQLite foreign key enforcement prevents phantom assignments."""
    mid = temp_db.add_camera_model(**sample_model)
    temp_db.save_serial_batch(mid, ["SN-FK-01"])
    sid = temp_db.get_available_serials(mid)[0]["id"]

    # Non-existent client ID 999999
    success = temp_db.assign_camera_to_client(999999, sid)
    assert success is False, "Assignment to non-existent client succeeded despite FK constraints"

    # Serial must remain unused
    avail = temp_db.get_available_serials(mid)
    assert len(avail) == 1


def test_tier2_transaction_rollback_returns_zero_on_error(temp_db, sample_model, sample_client):
    """
    CRITICAL BUG TEST:
    Verify that if assign_cameras_batch encounters an error mid-batch,
    the transaction is rolled back and returns 0 (NOT the partial count).
    """
    mid = temp_db.add_camera_model(**sample_model)
    cid = temp_db.add_client(sample_client)
    temp_db.save_serial_batch(mid, ["SN-ROLL-1", "SN-ROLL-2"])
    available = temp_db.get_available_serials(mid)
    valid_sid = available[0]["id"]
    invalid_sid = 99999999  # Does not exist, will trigger FK violation

    assigned = temp_db.assign_cameras_batch(cid, [valid_sid, invalid_sid])
    
    # Must return 0 because transaction was rolled back
    assert assigned == 0, (
        f"Rollback bug detected: assign_cameras_batch returned {assigned} instead of 0 upon rollback"
    )

    # Verify no serial was marked as used in DB
    avail_after = temp_db.get_available_serials(mid)
    assert len(avail_after) == 2, "Partial state leaked into database despite rollback!"


def test_tier2_wal_mode_and_concurrency(temp_db):
    """Verify SQLite connection thread safety and WAL journal mode."""
    cursor = temp_db.conn.cursor()
    cursor.execute("PRAGMA journal_mode;")
    mode = cursor.fetchone()[0].lower()
    # In M1, WAL mode is enforced; memory mode is also acceptable in testing
    assert mode in ("wal", "memory"), f"Unexpected journal_mode: {mode}"

    # Verify cross-thread execution does not raise ProgrammingError
    errors = []

    def thread_query():
        try:
            c = temp_db.conn.cursor()
            c.execute("SELECT COUNT(*) FROM camera_models;")
            c.fetchone()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=thread_query) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Thread safety errors detected: {errors}"


def test_tier2_composite_indexes_exist(temp_db):
    """Verify secondary performance indexes are created on serial_numbers and client_purchases."""
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = {row[0] for row in cursor.fetchall()}
    
    # Milestone 1 performance indexes
    expected_indexes = {"idx_sn_model_used", "idx_cp_client_id"}
    missing = expected_indexes - indexes
    assert not missing, f"Missing performance indexes: {missing}"


def test_tier2_low_stock_threshold_migration(temp_db, sample_model):
    """Verify low_stock_threshold column exists with default value 5."""
    cursor = temp_db.conn.cursor()
    cursor.execute("PRAGMA table_info(camera_models);")
    cols = {row[1]: row for row in cursor.fetchall()}
    assert "low_stock_threshold" in cols, "Column 'low_stock_threshold' missing from camera_models"

    mid = temp_db.add_camera_model(**sample_model)
    cursor.execute("SELECT low_stock_threshold FROM camera_models WHERE id = ?;", (mid,))
    val = cursor.fetchone()[0]
    assert val == 5, f"Expected default threshold 5, got {val}"


# =====================================================================
# TIER 3: Cross-Feature Integration (Analytics, Filters, Metrics)
# =====================================================================

def test_tier3_executive_analytics_kpi_calculations(temp_db, sample_model, sample_client):
    """Verify executive dashboard KPIs: stock counts, assigned counts, low stock warnings."""
    # Model 1: Dome (threshold 5, stock 3 -> LOW STOCK)
    m1 = temp_db.add_camera_model(
        model_name="HIK-DOME", equipment_designation="Dome", equipment_nature="Int", category="Cat 1", sub_category="A"
    )
    temp_db.save_serial_batch(m1, ["SN-D1", "SN-D2", "SN-D3"])

    # Model 2: Bullet (threshold 5, stock 8 -> OK)
    m2 = temp_db.add_camera_model(
        model_name="HIK-BULLET", equipment_designation="Bullet", equipment_nature="Ext", category="Cat 1", sub_category="A"
    )
    temp_db.save_serial_batch(m2, [f"SN-B{i}" for i in range(1, 9)])

    # Client 1 with 2 assigned cameras from Model 2
    cid = temp_db.add_client(sample_client)
    bullet_serials = temp_db.get_available_serials(m2)
    temp_db.assign_cameras_batch(cid, [bullet_serials[0]["id"], bullet_serials[1]["id"]])

    # Query analytics
    assert hasattr(temp_db, "get_dashboard_analytics"), "get_dashboard_analytics method not implemented"
    analytics = temp_db.get_dashboard_analytics()

    assert analytics["total_stock"] == 9   # 3 domes + 6 bullets
    assert analytics["total_assigned"] == 2 # 2 bullets
    assert analytics["total_clients"] == 1
    assert analytics["low_stock_count"] >= 1
    low_models = [item["model_name"] for item in analytics["low_stock_items"]]
    assert "HIK-DOME" in low_models


def test_tier3_inventory_search_and_filters(temp_db, sample_model, sample_client):
    """Verify search_serials filtering by query, model_id, and status."""
    m1 = temp_db.add_camera_model(model_name="MODEL-ALPHA", equipment_designation="Alpha", equipment_nature="A", category="C", sub_category="S")
    m2 = temp_db.add_camera_model(model_name="MODEL-BETA", equipment_designation="Beta", equipment_nature="B", category="C", sub_category="S")
    cid = temp_db.add_client(sample_client)

    temp_db.save_serial_batch(m1, ["SN-AAA-001", "SN-AAA-002"])
    temp_db.save_serial_batch(m2, ["SN-BBB-001", "SN-BBB-002"])

    # Assign one from Alpha
    s_alpha = temp_db.get_available_serials(m1)[0]["id"]
    temp_db.assign_camera_to_client(cid, s_alpha)

    assert hasattr(temp_db, "search_serials"), "search_serials method not implemented"

    # Search by serial substring
    res_search = temp_db.search_serials(query="BBB")
    assert len(res_search) == 2

    # Filter by model_id
    res_m1 = temp_db.search_serials(model_id=m1)
    assert len(res_m1) == 2

    # Filter by status: in_stock
    res_in_stock = temp_db.search_serials(status="in_stock")
    assert len(res_in_stock) == 3  # 1 Alpha + 2 Beta

    # Filter by status: assigned
    res_assigned = temp_db.search_serials(status="assigned")
    assert len(res_assigned) == 1
    assert res_assigned[0]["serial_number"] == "SN-AAA-001"


# =====================================================================
# TIER 4: Real-World Scenario (Full Multi-Model Lifecycle)
# =====================================================================

def test_tier4_complete_installer_lifecycle_multi_model(temp_db):
    """
    Simulate full operational cycle of an Algerian security installation contractor:
    - 3 camera models (Dome, Bullet, Speed Dome PTZ).
    - Ingestion of 25 serialized units.
    - 2 clients (Banque Nationale d'Algérie Agency & Hypermarché UNO).
    - Batch assignments across multiple models.
    - Hardware defect replacement (return 1 camera, re-assign replacement).
    - Inventory reconciliation and metrics check.
    """
    # 1. Setup Models
    m_dome = temp_db.add_camera_model(
        model_name="DS-2CD2143G2-I", equipment_designation="كاميرا قبة داخلية",
        equipment_nature="4MP Dome IP", category="الفئة 1", sub_category="أ"
    )
    m_bullet = temp_db.add_camera_model(
        model_name="DS-2CD2043G2-I", equipment_designation="كاميرا أنبوبية خارجية",
        equipment_nature="4MP Bullet IP", category="الفئة 1", sub_category="أ"
    )
    m_ptz = temp_db.add_camera_model(
        model_name="DS-2DE4425IW-DE", equipment_designation="كاميرا متحركة عالية الدقة",
        equipment_nature="4MP 25x PTZ IP", category="الفئة 1", sub_category="ب"
    )

    # 2. Ingest Stock
    dome_serials = [f"DOME-{i:03d}" for i in range(1, 11)]    # 10 units
    bullet_serials = [f"BULL-{i:03d}" for i in range(1, 11)]  # 10 units
    ptz_serials = [f"PTZ-{i:03d}" for i in range(1, 6)]       # 5 units
    temp_db.save_serial_batch(m_dome, dome_serials)
    temp_db.save_serial_batch(m_bullet, bullet_serials)
    temp_db.save_serial_batch(m_ptz, ptz_serials)

    # 3. Create Clients
    bna_client = {
        "full_name": "البنك الوطني الجزائري - وكالة الأبيار",
        "doc_number": "RC-16/00-0123456B18",
        "city": "الجزائر",
        "company_name": "BANQUE NATIONALE D'ALGERIE"
    }
    uno_client = {
        "full_name": "مجمع سيفيتال - هايبرماركت أونو",
        "doc_number": "RC-16/00-9876543A19",
        "city": "باب الزوار، الجزائر",
        "company_name": "HYPERMARCHÉ UNO"
    }
    c_bna = temp_db.add_client(bna_client)
    c_uno = temp_db.add_client(uno_client)

    # 4. Assign cameras to BNA: 4 Domes + 2 Bullets + 1 PTZ
    avail_domes = temp_db.get_available_serials(m_dome)
    avail_bullets = temp_db.get_available_serials(m_bullet)
    avail_ptz = temp_db.get_available_serials(m_ptz)

    bna_sids = [avail_domes[0]["id"], avail_domes[1]["id"], avail_domes[2]["id"], avail_domes[3]["id"],
                avail_bullets[0]["id"], avail_bullets[1]["id"], avail_ptz[0]["id"]]
    assigned_bna = temp_db.assign_cameras_batch(c_bna, bna_sids)
    assert assigned_bna == 7

    # 5. Assign cameras to UNO: 5 Bullets + 2 PTZ
    avail_bullets = temp_db.get_available_serials(m_bullet)
    avail_ptz = temp_db.get_available_serials(m_ptz)
    uno_sids = [avail_bullets[0]["id"], avail_bullets[1]["id"], avail_bullets[2]["id"],
                avail_bullets[3]["id"], avail_bullets[4]["id"], avail_ptz[0]["id"], avail_ptz[1]["id"]]
    assigned_uno = temp_db.assign_cameras_batch(c_uno, uno_sids)
    assert assigned_uno == 7

    # 6. RMA / Defect Return: BNA reports DOME-001 defective, returned to stock
    returned = temp_db.return_cameras_batch(["DOME-001"])
    assert returned == 1

    # Re-assign replacement DOME-005 to BNA
    avail_domes = temp_db.get_available_serials(m_dome)
    replacement = [s["id"] for s in avail_domes if s["serial_number"] == "DOME-005"][0]
    temp_db.assign_camera_to_client(c_bna, replacement)

    # 7. Final Verification
    bna_purchases = temp_db.get_client_purchases_for_pdf(c_bna)
    assert len(bna_purchases["cameras"]) == 7
    bna_serials = {c["serial_number"] for c in bna_purchases["cameras"]}
    assert "DOME-001" not in bna_serials
    assert "DOME-005" in bna_serials

    # Total in stock should be: 25 - (7 BNA + 7 UNO) + 1 (DOME-001 is back in stock) - 1 (DOME-005 reassigned) = 11
    all_avail = (
        len(temp_db.get_available_serials(m_dome)) +
        len(temp_db.get_available_serials(m_bullet)) +
        len(temp_db.get_available_serials(m_ptz))
    )
    assert all_avail == 11
