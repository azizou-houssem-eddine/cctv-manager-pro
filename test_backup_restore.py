import os
import unittest
import sqlite3
from db_manager import DatabaseManager

class TestBackupRestore(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_backup_master.db"
        self.backup_dir = "test_backups_dir"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.backup_dir):
            import shutil
            shutil.rmtree(self.backup_dir, ignore_errors=True)
        os.makedirs(self.backup_dir, exist_ok=True)

        self.db = DatabaseManager(self.test_db_path)
        self.db.initialize_db()

    def tearDown(self):
        self.db.close()
        for path in [self.test_db_path, f"{self.test_db_path}-wal", f"{self.test_db_path}-shm"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        if os.path.exists(self.backup_dir):
            import shutil
            shutil.rmtree(self.backup_dir, ignore_errors=True)

    def test_backup_and_restore_fidelity(self):
        """Test creating an atomic backup and restoring it with complete data fidelity."""
        # 1. Seed initial data
        mid = self.db.add_camera_model("Hikvision DS-2CD2043G2-I", "كاميرا خارجية", "IP Bullet", "القسم أ", "الفرع 1")
        self.db.save_serial_batch(mid, ["SN-BK-001", "SN-BK-002", "SN-BK-003"])
        cid = self.db.add_client({"full_name": "SARL TESTING BACKUP", "doc_number": "DOC-12345"})
        serials = self.db.get_all_serials(mid)
        target_serial = serials[0]["serial_number"]
        self.db.assign_cameras_batch(cid, [serials[0]["id"]])

        # 2. Create backup
        backup_file = os.path.join(self.backup_dir, "test_snapshot.db")
        b_res = self.db.create_database_backup(destination_path=backup_file)
        self.assertTrue(b_res.get("success"), f"Backup failed: {b_res.get('error')}")
        self.assertTrue(os.path.exists(backup_file))
        self.assertGreater(os.path.getsize(backup_file), 0)

        # 3. Modify active DB (delete client, delete models)
        self.db.conn.execute("DELETE FROM client_purchases;")
        self.db.conn.execute("DELETE FROM serial_numbers;")
        self.db.conn.execute("DELETE FROM camera_models;")
        self.db.conn.execute("DELETE FROM clients;")
        self.db.conn.commit()

        self.assertEqual(len(self.db.get_camera_models()), 0)
        self.assertEqual(len(self.db.get_clients()), 0)

        # 4. Restore from backup
        r_res = self.db.restore_database_from_backup(backup_file)
        self.assertTrue(r_res.get("success"), f"Restore failed: {r_res.get('error')}")

        # 5. Verify restored data
        models = self.db.get_camera_models()
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]["model_name"], "Hikvision DS-2CD2043G2-I")

        clients = self.db.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]["full_name"], "SARL TESTING BACKUP")

        purchases = self.db.get_client_purchases_for_pdf(cid)
        self.assertEqual(len(purchases["cameras"]), 1)
        self.assertEqual(purchases["cameras"][0]["serial_number"], target_serial)

    def test_restore_rejects_corrupted_or_invalid_db(self):
        """Test that restore refuses to apply corrupt or non-CCTV database files."""
        # Create non-cctv sqlite file
        invalid_db_path = os.path.join(self.backup_dir, "invalid.db")
        conn = sqlite3.connect(invalid_db_path)
        conn.execute("CREATE TABLE some_random_table (id INT);")
        conn.close()

        res = self.db.restore_database_from_backup(invalid_db_path)
        self.assertFalse(res.get("success"))
        self.assertIn("incompatible", res.get("error").lower())

        # Test corrupt file
        corrupt_path = os.path.join(self.backup_dir, "corrupt.db")
        with open(corrupt_path, "wb") as f:
            f.write(b"NOT A SQLITE FILE HEADER")

        res_corrupt = self.db.restore_database_from_backup(corrupt_path)
        self.assertFalse(res_corrupt.get("success"))

if __name__ == "__main__":
    unittest.main()
