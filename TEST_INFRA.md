# CCTV Manager Pro — Test Infrastructure & Architecture Guide

## 1. Overview & Testing Philosophy

The CCTV Manager Pro test suite is designed as an **independent, opaque-box testing harness** providing automated verification of all core system capabilities across four rigorous evaluation tiers.

The testing architecture guarantees:
- **Total Isolation**: Tests execute against ephemeral SQLite databases and isolated temporary directories (`tempfile.mkdtemp`), guaranteeing zero contamination or alteration of production data in `cctv_manager.db` or `dossiers/`.
- **Zero Facades**: Every test asserts observable system state, database side-effects, PyMuPDF vector/pixmap signatures, or RFC-compliant serialized formats.
- **Multilingual & Regulatory Fidelity**: Verifies Arabic Unicode persistence, Right-to-Left (RTL) text shaping, calibrated dot-masking, and official Algerian gazette compliance (Decree 09-410 & Gazette #54).
- **Windows 11 Native Execution**: Full compatibility with PowerShell (`pwsh`), Windows backslash path semantics, and CRLF / UTF-8 BOM file encoding.

---

## 2. Directory Layout

```text
d:\programation\cctv\
├── tests/
│   ├── __init__.py            # Test package root
│   ├── conftest.py            # Shared fixtures: temp_db, temp_dir, pdf_gen, sample entities
│   ├── test_db.py             # Database schema, WAL mode, composite indexes, rollback, metrics
│   ├── test_csv_import.py     # Delimiter auto-detect, deduplication, staging, UTF-8 BOM export
│   ├── test_pdf.py            # PyMuPDF stamping, vector PV de pose, Pixmap PNG preview, BiDi
│   ├── test_api_bridge.py     # JsApi RPC endpoints, validation, error responses, path sanitization
│   └── run_e2e_tests.py       # Custom standalone test runner with Tier breakdown & reporting
├── TEST_INFRA.md              # Test infrastructure documentation (this document)
└── TEST_READY.md              # Test readiness and test suite publication notice
```

---

## 3. Four-Tier Test Architecture

The test harness enforces progressive verification organized into four tiers:

### Tier 1: Feature Coverage (Core Functionality)
Covers baseline happy paths across all modules (minimum 5 tests per core feature):
- **Database (`test_db.py`)**:
  - `test_tier1_db_init_creates_required_tables`: Verifies `camera_models`, `clients`, `serial_numbers`, and `client_purchases` exist.
  - `test_tier1_camera_models_crud`: Verifies CRUD for camera models with regulatory fields.
  - `test_tier1_clients_crud_full_29_fields`: Full-fidelity persistence and retrieval of all 29 civil, identity, corporate, and logistics attributes.
  - `test_tier1_client_update`: In-place updates of existing client records.
  - `test_tier1_serial_numbers_batch_save_and_available`: Batch ingestion and stock filtering.
  - `test_tier1_single_camera_assignment` & `test_tier1_batch_camera_assignment`: Transactional assignment of cameras to clients.
  - `test_tier1_return_cameras_batch`: Disassociation of serials and resetting `is_used = 0`.
  - `test_tier1_get_client_purchases_for_pdf`: Multi-table relational join for regulatory stamping.
  - `test_tier1_clear_database`: Truncation utility.
- **CSV & Export (`test_csv_import.py`)**:
  - `test_tier1_csv_delimiter_sniffing_comma`, `test_tier1_csv_delimiter_sniffing_semicolon`, `test_tier1_csv_delimiter_sniffing_tab`: Delimiter auto-detection.
  - `test_tier1_raw_newline_separated_serials`: Headerless line-by-line scanner dumps.
  - `test_tier1_intra_file_deduplication`: Detection of duplicate serials within the source file.
  - `test_tier1_database_duplicate_detection`: Cross-reference with database inventory.
  - `test_tier1_import_staging_dry_run`: Read-only staging verification.
  - `test_tier1_atomic_import_batch_commit`: Transactional insertion.
  - `test_tier1_export_serials_csv_utf8_bom`: Byte-order mark (`\xef\xbb\xbf`) RFC 4180 export.
  - `test_tier1_export_serials_excel_openpyxl`: Excel `.xlsx` workbook generation.
- **PDF Engine (`test_pdf.py`)**:
  - `test_tier1_annex1_template_exists_and_valid_a4` & `test_tier1_annex5_template_exists_and_valid_a4`: Template validation.
  - `test_tier1_generate_annex1_single_camera` & `test_tier1_generate_annex5_full_questionnaire`: Document stamping.
  - `test_tier1_generate_client_dossier_creates_folder_and_both_pdfs`: Atomic client dossier creation.
  - `test_tier1_pixmap_preview_png_streaming`: High-resolution Pixmap rendering to PNG byte streams.
  - `test_tier1_pdf_deflate_compression`: Stream compression validation (`deflate=True, garbage=4`).
- **API Bridge (`test_api_bridge.py`)**:
  - `test_tier1_bridge_camera_models_endpoints`, `test_tier1_bridge_save_and_get_serials`, `test_tier1_bridge_client_endpoints`, `test_tier1_bridge_assign_and_return_cameras`, `test_tier1_bridge_generate_dossier`, `test_tier1_bridge_clear_database`: Remote Procedure Call (RPC) bridge methods exposed to JavaScript.

### Tier 2: Boundary & Corner Cases (Adversarial Robustness)
Stress tests edge conditions, invalid inputs, and security boundaries:
- Unique constraints on client `doc_number` and camera `serial_number`.
- Foreign key enforcement preventing assignment to non-existent clients.
- Deletion cascade protection: blocking deletion of models with active camera assignments.
- Client deletion safety: automatically resetting assigned serials back to available stock.
- **Transaction Rollback Bug Verification**: Ensures `assign_cameras_batch` returns `0` upon rollback and leaks zero state.
- Arabic Unicode preservation: full UTF-8 persistence of complex Arabic strings and diacritics.
- Empty/whitespace-only input handling across serials, CSVs, and API endpoints.
- Path traversal sanitization: neutralizes `../../` and illegal Windows characters (`\ / : * ? " < > |`).
- Windows reserved device names: handles `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`.
- Annex 1 table capping: strictly caps at 4 rows when client purchases exceed 4 distinct camera models.
- Dynamic font auto-scaling: scales down from 10.5pt to 7.0pt for corporate titles exceeding 150 characters without overflow.
- Calibrated dot-masking: verifies solid whiteout masking before drawing dynamic text.

### Tier 3: Cross-Feature Integration
Tests interactions across multiple system components:
- `test_tier3_executive_analytics_kpi_calculations`: Validates live calculation of `total_stock`, `total_assigned`, `total_clients`, `low_stock_items`, and low stock alert triggers.
- `test_tier3_inventory_search_and_filters`: Complex queries filtering by query text, model ID, and stock status.
- `test_tier3_full_csv_import_to_assignment_pipeline`: Pipeline starting from CSV ingestion -> duplicate filtering -> database commit -> client assignment -> inventory export.
- `test_tier3_pv_de_pose_vector_generation`: Pure vector generation of installation delivery receipts with exact serials and signature blocks.
- `test_tier3_document_preview_api_streaming`: Base64 Pixmap preview generation for in-app viewing.
- `test_tier3_bridge_end_to_end_workflow`: Entire application lifecycle executed through `JsApi`.

### Tier 4: Real-World Application Scenarios
Simulates authentic operational workflows encountered by Algerian security installers:
- `test_tier4_complete_installer_lifecycle_multi_model`: Multi-model deployment (Dome, Bullet, PTZ), corporate bank client & hypermarket, RMA defect return, hardware swap, and stock reconciliation.
- `test_tier4_warehouse_barcode_shipment_ingestion`: Handheld scanner export dump with CRLF line breaks, duplicate scans, and whitespace noise.
- `test_tier4_large_installation_multi_camera_dossier`: Large commercial facility with 20 camera units verifying aggregated Annex 1 and detailed PV receipt.
- `test_tier4_bridge_analytics_and_preview_contract`: Verification of analytics and preview contracts.

---

## 4. How to Run the Tests

### Option A: Standard Pytest Runner
```powershell
python -m pytest tests/ -v
```

### Option B: Automated E2E Runner with Tier Breakdown
```powershell
python tests/run_e2e_tests.py
```

---

## 5. Test Suite Verification Results

Execution verified on Windows 11 / Python 3.14.5:

```text
======================================================================
  CCTV MANAGER PRO — AUTOMATED E2E TEST SUITE RUNNER
======================================================================
  [Tier 1 (Feature Coverage)     ]  PASSED: 33 | FAILED:  0 | SKIPPED:  0 (Total: 33)
  [Tier 2 (Boundary & Corner)    ]  PASSED: 30 | FAILED:  0 | SKIPPED:  0 (Total: 30)
  [Tier 3 (Cross-Feature)        ]  PASSED:  6 | FAILED:  0 | SKIPPED:  0 (Total:  6)
  [Tier 4 (Real-World Scenarios) ]  PASSED:  4 | FAILED:  0 | SKIPPED:  0 (Total:  4)
----------------------------------------------------------------------
  TOTAL EXECUTED: 73
  TOTAL PASSED:   73
  TOTAL FAILED:   0
  TOTAL SKIPPED:  0
  TOTAL DURATION: 5.75 seconds
======================================================================
```
