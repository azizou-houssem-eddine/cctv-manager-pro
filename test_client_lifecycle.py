import unittest
import os
import shutil
import tempfile
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi

class TestClientLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_cctv.db")
        self.db = DatabaseManager(self.db_path)
        self.db.initialize_db()
        self.pdf_gen = PDFGenerator()
        self.api = JsApi(self.db, self.pdf_gen)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_client_crud_and_search(self):
        # 1. Save new client
        client_data = {
            "full_name": "Karim Benali",
            "father_name": "Ahmed",
            "mother_name": "Fatima",
            "dob": "15/04/1985",
            "pob": "Alger",
            "nationality": "جزائرية",
            "doc_number": "1122334455",
            "doc_issuer": "Daira Sidi M'Hamed",
            "doc_issue_date": "10/01/2020",
            "company_name": "SARL Algerie Surveillance",
            "phone": "0550123456",
            "email": "contact@algerie-surveillance.dz",
            "city": "Alger",
            "address": "12 Rue Didouche Mourad"
        }
        res = self.api.save_client(client_data)
        self.assertTrue(res.get("success"), f"Failed to save client: {res}")
        client_id = res["id"]

        # 2. Get client
        client_res = self.api.get_client(client_id)
        self.assertTrue(client_res.get("success"))
        client = client_res["client"]
        self.assertEqual(client["full_name"], "Karim Benali")
        self.assertEqual(client["company_name"], "SARL Algerie Surveillance")
        self.assertEqual(client["phone"], "0550123456")

        # 3. Update client
        update_data = dict(client_data)
        update_data["phone"] = "0661998877"
        update_data["company_name"] = "EURL Algerie Surveillance"
        update_res = self.api.update_client(client_id, update_data)
        self.assertTrue(update_res.get("success"))

        # Verify update
        client_res_2 = self.api.get_client(client_id)
        self.assertEqual(client_res_2["client"]["phone"], "0661998877")
        self.assertEqual(client_res_2["client"]["company_name"], "EURL Algerie Surveillance")

        # 4. Search clients
        search_res = self.api.get_clients("Surveillance")
        self.assertTrue(search_res.get("success"))
        self.assertEqual(len(search_res["data"]), 1)
        self.assertEqual(search_res["data"][0]["id"], client_id)

        # Search by phone
        search_res_phone = self.api.get_clients("066199")
        self.assertEqual(len(search_res_phone["data"]), 1)

        # Search by doc number
        search_res_doc = self.api.get_clients("1122334455")
        self.assertEqual(len(search_res_doc["data"]), 1)

    def test_client_camera_assignment_and_count(self):
        # 1. Create Model & Serials
        model_id = self.db.add_camera_model("CAM-HIK-4K", "Caméra Dôme 4K", "IR 30m", "القسم الأول", "الفرع أ")
        self.db.save_serial_batch(model_id, ["SN-CLIENT-001", "SN-CLIENT-002", "SN-CLIENT-003"])

        # 2. Create Client
        res = self.api.save_client({
            "full_name": "Mustapha Touati",
            "doc_number": "99887766",
            "company_name": "Touati Security"
        })
        client_id = res["id"]

        # 3. Check initial camera count in get_clients
        clients_res = self.api.get_clients("Touati")
        self.assertEqual(clients_res["data"][0]["camera_count"], 0)

        # 4. Assign 2 cameras using direct N
        assign_res = self.api.assign_n_cameras_by_model(client_id, model_id, 2)
        self.assertTrue(assign_res.get("success"))
        self.assertEqual(assign_res["assigned_count"], 2)

        # 5. Check updated camera count in get_clients
        clients_res_after = self.api.get_clients("Touati")
        self.assertEqual(clients_res_after["data"][0]["camera_count"], 2)

        # 6. Assign 1 more using barcode direct scan
        scan_assign_res = self.api.assign_camera_by_serial_number(client_id, "SN-CLIENT-003")
        self.assertTrue(scan_assign_res.get("success"))

        # 7. Check count is 3
        clients_res_final = self.api.get_clients("Touati")
        self.assertEqual(clients_res_final["data"][0]["camera_count"], 3)

        # 8. Return 1 camera
        ret_res = self.api.return_cameras(["SN-CLIENT-001"])
        self.assertTrue(ret_res.get("success"))
        self.assertEqual(ret_res["count"], 1)

        # Count should now be 2
        clients_res_returned = self.api.get_clients("Touati")
        self.assertEqual(clients_res_returned["data"][0]["camera_count"], 2)

if __name__ == "__main__":
    unittest.main()
