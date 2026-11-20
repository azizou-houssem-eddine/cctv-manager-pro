import unittest
import os
import shutil
import tempfile
import base64
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi

class TestEnhancements(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_enhancements.db")
        self.db = DatabaseManager(self.db_path)
        self.db.initialize_db()
        self.pdf_gen = PDFGenerator()
        self.api = JsApi(self.db, self.pdf_gen)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_client_search_by_numeric_id(self):
        # Create clients
        c1_id = self.db.add_client({
            "full_name": "Ahmed Benali",
            "doc_number": "1001",
            "city": "Alger"
        })
        c2_id = self.db.add_client({
            "full_name": "Karim Ziani",
            "doc_number": "1002",
            "city": "Oran"
        })
        c3_id = self.db.add_client({
            "full_name": "Samir Saidi",
            "doc_number": "1003",
            "city": "Constantine"
        })

        # Search specifically by exact client ID of c2
        results = self.db.get_clients(search_query=str(c2_id))
        matching_ids = [c["id"] for c in results]
        self.assertIn(c2_id, matching_ids)

        # Search by non-existent ID
        empty_results = self.db.get_clients(search_query="99999")
        self.assertEqual(len(empty_results), 0)

    def test_update_camera_model_db_and_bridge(self):
        # 1. Add model
        model_id = self.db.add_camera_model(
            model_name="CAM-100",
            equipment_designation="كاميرا مراقبة 2 ميغابكسل",
            equipment_nature="رقمية IP",
            category="01",
            sub_category="02",
            low_stock_threshold=5
        )
        self.assertIsInstance(model_id, int)

        # 2. Update via db_manager
        up_db = self.db.update_camera_model(
            model_id=model_id,
            model_name="CAM-100-PRO",
            equipment_designation="كاميرا مراقبة احترافية 4 ميغابكسل",
            equipment_nature="رقمية IP ذكية",
            category="03",
            sub_category="04",
            low_stock_threshold=10
        )
        self.assertTrue(up_db)

        # Verify updated values in db
        models = self.db.get_camera_models()
        target = next((x for x in models if x["id"] == model_id), None)
        self.assertIsNotNone(target)
        self.assertEqual(target["model_name"], "CAM-100-PRO")
        self.assertEqual(target["equipment_designation"], "كاميرا مراقبة احترافية 4 ميغابكسل")
        self.assertEqual(target["equipment_nature"], "رقمية IP ذكية")
        self.assertEqual(target["category"], "03")
        self.assertEqual(target["sub_category"], "04")
        self.assertEqual(target["low_stock_threshold"], 10)

        # 3. Update via api_bridge with dictionary payload
        up_api = self.api.update_camera_model({
            "model_id": model_id,
            "model_name": "CAM-100-ULTRA",
            "equipment_designation": "كاميرا مراقبة 8K",
            "equipment_nature": "PTZ Dome",
            "category": "05",
            "sub_category": "06",
            "low_stock_threshold": 3
        })
        self.assertTrue(up_api["success"])

        # Verify bridge update
        models_after = self.api.get_camera_models()["data"]
        target2 = next((x for x in models_after if x["id"] == model_id), None)
        self.assertEqual(target2["model_name"], "CAM-100-ULTRA")
        self.assertEqual(target2["low_stock_threshold"], 3)

        # 4. Validation errors
        err1 = self.api.update_camera_model({"model_id": None, "model_name": "X"})
        self.assertFalse(err1["success"])

        err2 = self.api.update_camera_model({"model_id": model_id, "model_name": ""})
        self.assertFalse(err2["success"])

    def test_serial_history_assignments_and_returns(self):
        # Setup model and serials
        model_id = self.db.add_camera_model("CAM-HIST", "كاميرا تاريخ", "IP", "01", "01", 5)
        self.db.save_serial_batch(model_id, ["SN-H1", "SN-H2", "SN-H3", "SN-H4"])

        client_id = self.db.add_client({"full_name": "History Client", "doc_number": "HIST001"})

        # 1. Single assignment via assign_camera_by_serial_number
        res1 = self.db.assign_camera_by_serial_number(client_id, "SN-H1")
        self.assertTrue(res1["success"])

        hist1 = self.db.get_serial_history(serial_number="SN-H1")
        self.assertEqual(len(hist1), 1)
        self.assertEqual(hist1[0]["action"], "ASSIGN")
        self.assertEqual(hist1[0]["client_id"], client_id)

        # 2. Batch assignment via assign_cameras_batch
        serials_db = self.db.get_all_serials()
        s2 = next(s for s in serials_db if s["serial_number"] == "SN-H2")
        assigned_count = self.db.assign_cameras_batch(client_id, [s2["id"]])
        self.assertEqual(assigned_count, 1)

        hist2 = self.db.get_serial_history(serial_number="SN-H2")
        self.assertEqual(len(hist2), 1)
        self.assertEqual(hist2[0]["action"], "ASSIGN")

        # 3. Direct serial number assign via assign_camera_by_serial_number
        res3 = self.db.assign_camera_by_serial_number(client_id, "SN-H3")
        self.assertTrue(res3["success"])

        hist3 = self.db.get_serial_history(serial_number="SN-H3")
        self.assertEqual(len(hist3), 1)
        self.assertEqual(hist3[0]["action"], "ASSIGN")

        # 4. Assign N cameras via assign_n_cameras_by_model
        res4 = self.db.assign_n_cameras_by_model(client_id, model_id, 1)
        self.assertTrue(res4["success"])
        self.assertEqual(res4["assigned_count"], 1)

        hist4 = self.db.get_serial_history(serial_number="SN-H4")
        self.assertEqual(len(hist4), 1)
        self.assertEqual(hist4[0]["action"], "ASSIGN")

        # 5. Return cameras batch
        ret_count = self.db.return_cameras_batch(["SN-H1", "SN-H2"])
        self.assertEqual(ret_count, 2)

        # Verify returned action logged
        hist_h1 = self.db.get_serial_history(serial_number="SN-H1")
        self.assertEqual(len(hist_h1), 2)
        actions_h1 = [h["action"] for h in hist_h1]
        self.assertEqual(actions_h1, ["RETURN", "ASSIGN"])

        # 6. Test via api bridge get_serial_history
        bridge_hist = self.api.get_serial_history(serial_number="SN-H1")
        self.assertTrue(bridge_hist["success"])
        self.assertEqual(len(bridge_hist["data"]), 2)

    def test_delete_client_unlinks_cameras_and_records_history(self):
        model_id = self.db.add_camera_model("CAM-DEL", "كاميرا حذف", "IP", "01", "01", 5)
        self.db.save_serial_batch(model_id, ["SN-DEL1", "SN-DEL2"])

        client_id = self.db.add_client({"full_name": "To Delete Client", "doc_number": "DEL001"})

        self.db.assign_camera_by_serial_number(client_id, "SN-DEL1")
        self.db.assign_camera_by_serial_number(client_id, "SN-DEL2")

        # Verify assigned
        client_res = self.api.get_client(client_id)
        self.assertEqual(len(client_res["cameras"]), 2)

        # Delete client via API bridge
        del_res = self.api.delete_client(client_id)
        self.assertTrue(del_res["success"])

        # Check client gone
        client_after = self.api.get_client(client_id)
        self.assertFalse(client_after["success"])

        # Check cameras returned to stock
        serials_after = self.db.get_all_serials()
        s1 = next(s for s in serials_after if s["serial_number"] == "SN-DEL1")
        s2 = next(s for s in serials_after if s["serial_number"] == "SN-DEL2")
        self.assertEqual(s1["is_used"], 0)
        self.assertEqual(s2["is_used"], 0)

        # Check history contains return on client deletion
        hist = self.db.get_serial_history(serial_number="SN-DEL1")
        actions = [h["action"] for h in hist]
        self.assertIn("RETURN", actions)
        self.assertIn("Client deleted", hist[0]["details"])

    def test_client_purchases_includes_assigned_at(self):
        model_id = self.db.add_camera_model("CAM-DATE", "كاميرا تاريخ", "IP", "01", "01", 5)
        self.db.save_serial_batch(model_id, ["SN-DATE1"])
        c_id = self.db.add_client({"full_name": "Date Client", "doc_number": "DATE001"})
        self.db.assign_camera_by_serial_number(c_id, "SN-DATE1")

        purchases = self.db.get_client_purchases_for_pdf(c_id)
        self.assertEqual(len(purchases["cameras"]), 1)
        self.assertIn("assigned_at", purchases["cameras"][0])
        self.assertTrue(bool(purchases["cameras"][0]["assigned_at"]))

    def test_pdf_signature_city_resolution(self):
        # 1. Configured installer profile with city via set_installer_profile
        self.pdf_gen.set_installer_profile({"city": "وهران", "company_name": "SecurTech Oran"})

        client = {"city": "الجزائر", "full_name": "Test Client"}
        sig_city = self.pdf_gen._get_signature_city(client)
        self.assertEqual(sig_city, "وهران")

        # 2. Configured profile with empty city -> falls back to client city
        self.pdf_gen.set_installer_profile({"city": "", "company_name": "SecurTech Oran"})

        sig_city_client = self.pdf_gen._get_signature_city(client)
        self.assertEqual(sig_city_client, "الجزائر")

        # 3. Both empty -> fallback to default "الجزائر"
        empty_client = {"city": "", "full_name": "Empty City Client"}
        sig_city_def = self.pdf_gen._get_signature_city(empty_client)
        self.assertEqual(sig_city_def, "الجزائر")

        # 4. Clean DB with no configured installer city must fall back to client city (e.g. البليدة)
        profile_from_db = self.db.get_installer_profile()
        self.assertEqual(profile_from_db.get("city"), "")
        self.pdf_gen.set_installer_profile(profile_from_db)
        client_blida = {"city": "البليدة", "full_name": "Blida Client"}
        self.assertEqual(self.pdf_gen._get_signature_city(client_blida), "البليدة")

    def test_delete_non_existent_client_returns_false(self):
        # Attempt to delete non-existent client ID 99999
        res = self.db.delete_client(99999)
        self.assertFalse(res)
        res_api = self.api.delete_client(99999)
        self.assertFalse(res_api["success"])

    def test_update_camera_model_zero_threshold(self):
        model_id = self.db.add_camera_model("CAM-ZERO", "كاميرا صفر", "IP", "01", "01", 5)
        # Update threshold to 0
        up_res = self.api.update_camera_model({"model_id": model_id, "model_name": "CAM-ZERO", "low_stock_threshold": 0})
        self.assertTrue(up_res["success"])
        models = self.db.get_camera_models()
        m = next(x for x in models if x["id"] == model_id)
        self.assertEqual(m["low_stock_threshold"], 0)

    def test_export_serials_with_status_filter(self):
        model_id = self.db.add_camera_model("CAM-EXP", "كاميرا تصدير", "IP", "01", "01", 5)
        self.db.save_serial_batch(model_id, ["SN-EXP-1", "SN-EXP-2"])
        c_id = self.db.add_client({"full_name": "Export Client", "doc_number": "EXP001"})
        self.db.assign_camera_by_serial_number(c_id, "SN-EXP-1")

        # Export in_stock
        res_stock = self.api.export_serials_csv(status="in_stock")
        self.assertTrue(res_stock["success"])
        csv_str_stock = res_stock["csv_data"]
        self.assertIn("SN-EXP-2", csv_str_stock)
        self.assertNotIn("SN-EXP-1", csv_str_stock)

        # Export assigned
        res_assigned = self.api.export_serials_csv(status="assigned")
        self.assertTrue(res_assigned["success"])
        csv_str_assigned = res_assigned["csv_data"]
        self.assertIn("SN-EXP-1", csv_str_assigned)
        self.assertNotIn("SN-EXP-2", csv_str_assigned)

        # Export excel with filter
        res_xlsx = self.api.export_serials_excel(status="in_stock")
        self.assertTrue(res_xlsx["success"])
        self.assertTrue(len(res_xlsx["base64"]) > 0)
        decoded_bytes = base64.b64decode(res_xlsx["base64"])
        self.assertTrue(len(decoded_bytes) > 0)

if __name__ == "__main__":
    unittest.main()
