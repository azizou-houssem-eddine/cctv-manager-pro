import os
import io
import base64
import unittest
import openpyxl
from db_manager import DatabaseManager

class TestUnifiedImport(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_unified_import.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = DatabaseManager(self.test_db_path)
        self.db.initialize_db()

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_excel_models_catalog_import(self):
        """Test importing camera models catalog from an Excel (.xlsx) file."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Catalog"
        ws.append(["Modèle", "Désignation", "Nature", "Section", "Sous-section", "Seuil"])
        ws.append(["Hikvision DS-2CD2043G2-I", "كاميرا خارجية للمراقبة", "IP Bullet 4MP", "القسم أ", "الفرع 1", 5])
        ws.append(["Dahua IPC-HFW2431S-S-S2", "كاميرا مراقبة بدقة عالية", "IP Bullet IR", "القسم ب", "الفرع 2", 8])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        b64_data = base64.b64encode(stream.read()).decode("ascii")

        # 1. Preview
        preview = self.db.parse_and_preview_import(b64_data, filename="catalog.xlsx")
        self.assertTrue(preview.get("success"), f"Preview failed: {preview.get('error')}")
        self.assertEqual(preview.get("mode"), "MODELS_CATALOG")
        self.assertEqual(preview.get("total_detected"), 2)
        self.assertEqual(len(preview.get("valid_items")), 2)

        # 2. Commit
        res = self.db.commit_unified_import("MODELS_CATALOG", preview.get("valid_items"))
        self.assertTrue(res.get("success"), f"Commit failed: {res.get('error')}")
        self.assertEqual(res.get("imported_count"), 2)

        models = self.db.get_camera_models()
        self.assertEqual(len(models), 2)
        names = {m["model_name"] for m in models}
        self.assertIn("Hikvision DS-2CD2043G2-I", names)
        self.assertIn("Dahua IPC-HFW2431S-S-S2", names)

    def test_excel_combined_manifest_import(self):
        """Test importing a combined delivery manifest (Model Name + Serial Number)."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Livraison"
        ws.append(["Modèle de Caméra", "Numéro de Série"])
        ws.append(["Hikvision DS-2CD2143G2-I", "HK-SN-00101"])
        ws.append(["Hikvision DS-2CD2143G2-I", "HK-SN-00102"])
        ws.append(["Dahua IPC-HDW1230T1", "DH-SN-00201"])
        ws.append(["Hikvision DS-2CD2143G2-I", "HK-SN-00101"])  # Duplicate in file

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        b64_data = base64.b64encode(stream.read()).decode("ascii")

        # Preview
        preview = self.db.parse_and_preview_import(b64_data, filename="livraison.xlsx")
        self.assertTrue(preview.get("success"), f"Preview failed: {preview.get('error')}")
        self.assertEqual(preview.get("mode"), "COMBINED_MANIFEST")
        self.assertEqual(preview.get("total_detected"), 4)
        self.assertEqual(len(preview.get("valid_items")), 3)
        self.assertEqual(len(preview.get("duplicates_in_file")), 1)
        self.assertEqual(len(preview.get("new_models_to_create")), 2)

        # Commit
        res = self.db.commit_unified_import("COMBINED_MANIFEST", preview.get("valid_items"))
        self.assertTrue(res.get("success"), f"Commit failed: {res.get('error')}")
        self.assertEqual(res.get("imported_serials_count"), 3)
        self.assertEqual(res.get("created_models_count"), 2)

        # Verify stock
        serials = self.db.get_all_serials()
        self.assertEqual(len(serials), 3)

    def test_csv_delimiters_and_headers(self):
        """Test CSV parsing with semicolon delimiter and French headers."""
        csv_content = (
            "Modèle;Numéro de Série\n"
            "Hikvision DS-2CD1023G0E;HIK-888999\n"
            "Hikvision DS-2CD1023G0E;HIK-888998\n"
        )
        preview = self.db.parse_and_preview_import(csv_content, filename="delivery.csv")
        self.assertTrue(preview.get("success"))
        self.assertEqual(preview.get("mode"), "COMBINED_MANIFEST")
        self.assertEqual(preview.get("total_detected"), 2)
        self.assertEqual(len(preview.get("valid_items")), 2)

    def test_database_duplicate_detection(self):
        """Test that serial numbers already in SQLite are flagged as already_in_db."""
        mid = self.db.add_camera_model("Test Model", "كاميرا", "IP", "Section 1", "Sub 1")
        self.db.save_serial_batch(mid, ["SN-EXISTING-1", "SN-EXISTING-2"])

        csv_content = (
            "Serial Number\n"
            "SN-EXISTING-1\n"
            "SN-NEW-3\n"
            "SN-NEW-4\n"
        )
        preview = self.db.parse_and_preview_import(csv_content, filename="serials.txt", destination_model_id=mid)
        self.assertTrue(preview.get("success"))
        self.assertEqual(preview.get("mode"), "SERIALS_ONLY")
        self.assertEqual(preview.get("total_detected"), 3)
        self.assertEqual(len(preview.get("valid_items")), 2)
        self.assertEqual(len(preview.get("already_in_db")), 1)
        self.assertEqual(preview.get("already_in_db")[0], "SN-EXISTING-1")

    def test_excel_template_generation(self):
        """Test generating pre-styled Excel templates."""
        catalog_bytes = self.db.generate_import_template("catalog")
        self.assertTrue(isinstance(catalog_bytes, bytes) and len(catalog_bytes) > 0)
        wb_cat = openpyxl.load_workbook(io.BytesIO(catalog_bytes))
        ws_cat = wb_cat.active
        headers_cat = [cell.value for cell in ws_cat[1]]
        self.assertTrue(any("Modèle" in str(h) for h in headers_cat))

        manifest_bytes = self.db.generate_import_template("manifest")
        self.assertTrue(isinstance(manifest_bytes, bytes) and len(manifest_bytes) > 0)
        wb_man = openpyxl.load_workbook(io.BytesIO(manifest_bytes))
        ws_man = wb_man.active
        headers_man = [cell.value for cell in ws_man[1]]
        self.assertTrue(any("Modèle" in str(h) for h in headers_man))
        self.assertTrue(any("Série" in str(h) or "Serial" in str(h) for h in headers_man))

    def test_api_bridge_endpoints(self):
        """Test the bridge methods exposed to pywebview."""
        from api_bridge import JsApi
        from pdf_generator import PDFGenerator
        bridge = JsApi(self.db, PDFGenerator())

        # Template test
        tpl = bridge.get_import_template("catalog")
        self.assertTrue(tpl.get("success"))
        self.assertIn("data:application", tpl.get("data_uri"))

        # Preview test
        csv_content = "Modèle;Numéro de Série\nModelX;SN-TEST-1\n"
        prev = bridge.preview_unified_import({
            "raw_content": csv_content,
            "filename": "test.csv"
        })
        self.assertTrue(prev.get("success"))
        self.assertEqual(prev.get("mode"), "COMBINED_MANIFEST")

        # Commit test
        commit_res = bridge.commit_unified_import({
            "mode": "COMBINED_MANIFEST",
            "items": prev.get("valid_items")
        })
        self.assertTrue(commit_res.get("success"))
        self.assertEqual(commit_res.get("imported_serials_count"), 1)

    def test_end_to_end_manifest_to_pdf_readiness(self):
        """
        Verify complete integration:
        Import supplier delivery manifest -> Auto-create camera models -> Verify stock availability ->
        Assign to client -> Verify client purchases data for PDF generation.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Supplier Delivery"
        ws.append(["Modèle de Caméra", "Numéro de Série", "Désignation"])
        ws.append(["Hikvision DS-2CD2386G2-ISU/SL", "HK-E2E-99001", "كاميرا ذكية للمراقبة"])
        ws.append(["Hikvision DS-2CD2386G2-ISU/SL", "HK-E2E-99002", "كاميرا ذكية للمراقبة"])
        ws.append(["Dahua IPC-HDBW3841R-ZAS", "DH-E2E-88001", "كاميرا دوم 8 ميغابكسل"])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        b64_data = base64.b64encode(stream.read()).decode("ascii")

        # 1. Preview
        prev = self.db.parse_and_preview_import(b64_data, filename="facture_fournisseur.xlsx")
        self.assertTrue(prev["success"])
        self.assertEqual(prev["mode"], "COMBINED_MANIFEST")
        self.assertEqual(len(prev["new_models_to_create"]), 2)
        self.assertEqual(len(prev["valid_items"]), 3)

        # 2. Commit
        res = self.db.commit_unified_import("COMBINED_MANIFEST", prev["valid_items"])
        self.assertTrue(res["success"])
        self.assertEqual(res["imported_serials_count"], 3)
        self.assertEqual(res["created_models_count"], 2)

        # 3. Create a test client
        cid = self.db.add_client({
            "full_name": "SARL ALGERIA SURVEILLANCE",
            "doc_number": "16-998877",
            "phone": "0550123456"
        })
        self.assertTrue(cid > 0)

        # 4. Fetch serials for assignment
        serials = self.db.get_all_serials()
        assigned_serial_ids = [s["id"] for s in serials if s["serial_number"] in ("HK-E2E-99001", "DH-E2E-88001")]
        self.assertEqual(len(assigned_serial_ids), 2)

        assigned_count = self.db.assign_cameras_batch(cid, assigned_serial_ids)
        self.assertEqual(assigned_count, 2)

        # 5. Verify PDF data aggregation
        pdf_data = self.db.get_client_purchases_for_pdf(cid)
        self.assertIsNotNone(pdf_data["client"])
        self.assertEqual(len(pdf_data["cameras"]), 2)

if __name__ == "__main__":
    unittest.main()
