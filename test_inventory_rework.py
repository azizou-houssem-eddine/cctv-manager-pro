import os
import unittest
import uuid
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi

class TestInventoryRework(unittest.TestCase):
    def setUp(self):
        self.test_id = uuid.uuid4().hex[:8]
        self.test_db_path = f"test_inventory_{self.test_id}.db"
        self.db = DatabaseManager(self.test_db_path)
        self.db.initialize_db()
        self.pdf_gen = PDFGenerator()
        self.api = JsApi(self.db, self.pdf_gen)
        self.model_id = self.db.add_camera_model(
            "Hikvision DS-2CD2143G2-I",
            "كاميرا مراقبة خارجية",
            "IP Dome 4MP",
            "القسم أ",
            "الفرع 1"
        )

    def tearDown(self):
        self.db.close()
        for path in [self.test_db_path, f"{self.test_db_path}-wal", f"{self.test_db_path}-shm"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def test_save_single_serial_direct_success(self):
        """Test instant single barcode scan directly saving to database."""
        res = self.db.save_single_serial_direct(self.model_id, "SN-DIRECT-001")
        self.assertTrue(res.get("success"), f"Direct scan failed: {res}")
        self.assertEqual(res.get("serial_number"), "SN-DIRECT-001")
        self.assertEqual(res.get("model_id"), self.model_id)
        self.assertEqual(res.get("is_used"), 0)

        # Check database persistence
        serials = self.db.get_available_serials(self.model_id)
        self.assertEqual(len(serials), 1)
        self.assertEqual(serials[0]["serial_number"], "SN-DIRECT-001")

    def test_save_single_serial_direct_duplicate(self):
        """Test scanning an already existing serial returns duplicate error."""
        res1 = self.db.save_single_serial_direct(self.model_id, "SN-DUP-001")
        self.assertTrue(res1.get("success"))

        res2 = self.db.save_single_serial_direct(self.model_id, "SN-DUP-001")
        self.assertFalse(res2.get("success"))
        self.assertEqual(res2.get("error"), "duplicate")
        self.assertTrue(res2.get("duplicate"))

    def test_save_single_serial_direct_invalid_input(self):
        """Test empty or whitespace serials are rejected."""
        res_empty = self.db.save_single_serial_direct(self.model_id, "   ")
        self.assertFalse(res_empty.get("success"))
        self.assertEqual(res_empty.get("error"), "invalid_input")

    def test_save_single_serial_direct_invalid_model(self):
        """Test non-existent model ID is rejected."""
        res_bad_model = self.db.save_single_serial_direct(999999, "SN-VALID-001")
        self.assertFalse(res_bad_model.get("success"))
        self.assertEqual(res_bad_model.get("error"), "invalid_model")

    def test_delete_serial_number_success(self):
        """Test deleting an unassigned serial number."""
        res_add = self.db.save_single_serial_direct(self.model_id, "SN-DEL-001")
        sid = res_add["serial_id"]

        res_del = self.db.delete_serial_number(sid)
        self.assertTrue(res_del.get("success"), f"Delete failed: {res_del}")
        self.assertEqual(res_del.get("serial_id"), sid)

        # Check it is removed
        serials = self.db.get_available_serials(self.model_id)
        self.assertEqual(len(serials), 0)

    def test_delete_serial_number_assigned_blocked(self):
        """Test that an assigned serial number cannot be deleted."""
        res_add = self.db.save_single_serial_direct(self.model_id, "SN-ASSIGNED-001")
        sid = res_add["serial_id"]

        cid = self.db.add_client({"full_name": "TEST CLIENT", "doc_number": "DOC-999"})
        self.db.assign_cameras_batch(cid, [sid])

        res_del = self.db.delete_serial_number(sid)
        self.assertFalse(res_del.get("success"))
        self.assertEqual(res_del.get("error"), "assigned")

        # Verify still in DB
        all_serials = self.db.get_all_serials(self.model_id)
        self.assertEqual(len(all_serials), 1)
        self.assertEqual(all_serials[0]["is_used"], 1)

    def test_delete_serial_number_not_found(self):
        """Test deleting non-existent serial ID."""
        res_del = self.db.delete_serial_number(999999)
        self.assertFalse(res_del.get("success"))
        self.assertEqual(res_del.get("error"), "not_found")

    def test_delete_serials_batch(self):
        """Test batch deletion of unused serials while preserving assigned ones."""
        s1 = self.db.save_single_serial_direct(self.model_id, "SN-BATCH-1")["serial_id"]
        s2 = self.db.save_single_serial_direct(self.model_id, "SN-BATCH-2")["serial_id"]
        s3 = self.db.save_single_serial_direct(self.model_id, "SN-BATCH-3")["serial_id"]
        s_assigned = self.db.save_single_serial_direct(self.model_id, "SN-BATCH-ASSIGNED")["serial_id"]

        cid = self.db.add_client({"full_name": "CLIENT BATCH", "doc_number": "DOC-888"})
        self.db.assign_cameras_batch(cid, [s_assigned])

        res = self.db.delete_serials_batch([s1, s2, s3, s_assigned])
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("deleted_count"), 3)
        self.assertEqual(res.get("skipped_assigned"), 1)

        # Only s_assigned should remain
        remaining = self.db.get_all_serials(self.model_id)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], s_assigned)

    def test_api_bridge_integration(self):
        """Test JsApi bridge exposes the new inventory operations correctly."""
        # 1. Direct scan via bridge
        res_scan = self.api.save_single_serial_direct(self.model_id, "SN-BRIDGE-001")
        self.assertTrue(res_scan.get("success"))
        sid = res_scan.get("serial_id")

        # 2. Bridge duplicate check
        res_dup = self.api.save_single_serial_direct(self.model_id, "SN-BRIDGE-001")
        self.assertFalse(res_dup.get("success"))
        self.assertTrue(res_dup.get("duplicate"))

        # 3. Bridge single deletion
        res_del = self.api.delete_serial_number(sid)
        self.assertTrue(res_del.get("success"))

        # 4. Bridge batch deletion
        s_a = self.api.save_single_serial_direct(self.model_id, "SN-BA")["serial_id"]
        s_b = self.api.save_single_serial_direct(self.model_id, "SN-BB")["serial_id"]
        res_batch_del = self.api.delete_serials_batch([s_a, s_b])
        self.assertTrue(res_batch_del.get("success"))
        self.assertEqual(res_batch_del.get("deleted_count"), 2)

    def test_assign_camera_by_serial_number_success(self):
        """Test scanning a camera barcode to assign it directly to a client."""
        cid = self.db.add_client({"full_name": "SARL DIRECT SCANNER", "doc_number": "DOC-SCAN-1"})
        self.db.save_single_serial_direct(self.model_id, "SN-SCAN-ASSIGN-1")

        res = self.db.assign_camera_by_serial_number(cid, "SN-SCAN-ASSIGN-1")
        self.assertTrue(res.get("success"), f"Assignment failed: {res}")
        self.assertEqual(res.get("serial_number"), "SN-SCAN-ASSIGN-1")
        self.assertEqual(res.get("client_id"), cid)

        # Check DB reflects assignment
        client_data = self.db.get_client_purchases_for_pdf(cid)
        self.assertEqual(len(client_data["cameras"]), 1)
        self.assertEqual(client_data["cameras"][0]["serial_number"], "SN-SCAN-ASSIGN-1")

    def test_assign_camera_by_serial_number_already_assigned(self):
        """Test assigning a serial that is already assigned to someone else fails."""
        c1 = self.db.add_client({"full_name": "CLIENT 1", "doc_number": "DOC-1"})
        c2 = self.db.add_client({"full_name": "CLIENT 2", "doc_number": "DOC-2"})
        self.db.save_single_serial_direct(self.model_id, "SN-SCAN-ASSIGN-2")

        res1 = self.db.assign_camera_by_serial_number(c1, "SN-SCAN-ASSIGN-2")
        self.assertTrue(res1.get("success"))

        res2 = self.db.assign_camera_by_serial_number(c2, "SN-SCAN-ASSIGN-2")
        self.assertFalse(res2.get("success"))
        self.assertEqual(res2.get("error"), "already_assigned")

    def test_assign_camera_by_serial_number_not_found(self):
        """Test assigning a serial that does not exist in stock fails."""
        c = self.db.add_client({"full_name": "CLIENT NONEXISTENT", "doc_number": "DOC-3"})
        res = self.db.assign_camera_by_serial_number(c, "SN-DOES-NOT-EXIST")
        self.assertFalse(res.get("success"))
        self.assertEqual(res.get("error"), "not_found")

    def test_assign_n_cameras_by_model(self):
        """Test auto-picking and allocating N units of a model to a client."""
        cid = self.db.add_client({"full_name": "SARL BATCH ALLOC", "doc_number": "DOC-ALLOC-1"})
        for i in range(5):
            self.db.save_single_serial_direct(self.model_id, f"SN-ALLOC-{i+1}")

        res = self.db.assign_n_cameras_by_model(cid, self.model_id, 3)
        self.assertTrue(res.get("success"), f"Alloc failed: {res}")
        self.assertEqual(res.get("assigned_count"), 3)
        self.assertEqual(len(res.get("serials")), 3)

        # 2 units should remain in stock, 3 assigned
        available = self.db.get_available_serials(self.model_id)
        self.assertEqual(len(available), 2)

    def test_assign_n_cameras_by_model_insufficient(self):
        """Test allocating more units than available returns insufficient error."""
        cid = self.db.add_client({"full_name": "SARL SHORT", "doc_number": "DOC-SHORT-1"})
        self.db.save_single_serial_direct(self.model_id, "SN-ONLY-ONE")

        res = self.db.assign_n_cameras_by_model(cid, self.model_id, 5)
        self.assertFalse(res.get("success"))
        self.assertEqual(res.get("error"), "insufficient_stock")
        self.assertEqual(res.get("available_count"), 1)

if __name__ == "__main__":
    unittest.main()
