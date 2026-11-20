import os
import io
import base64
import unittest
import fitz
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator

def create_dummy_png_b64(color=(255, 0, 0)):
    """Create a minimal valid PNG image in Base64 for testing."""
    pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 50, 50), 1)
    pix.clear_with(255)
    # Draw simple rect
    bytes_data = pix.tobytes("png")
    return base64.b64encode(bytes_data).decode("ascii")

class TestInstallerSeal(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_seal.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = DatabaseManager(self.test_db_path)
        self.db.initialize_db()
        self.pdf_gen = PDFGenerator()

    def tearDown(self):
        self.db.close()
        for path in [self.test_db_path, f"{self.test_db_path}-wal", f"{self.test_db_path}-shm"]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def test_installer_profile_persistence(self):
        """Test storing and retrieving installer branding in DatabaseManager."""
        profile_data = {
            "company_name": "SARL CCTV PRO ALGERIE",
            "installer_name": "Amine Benali",
            "phone": "0550112233",
            "city": "البليدة",
            "seal_image_b64": create_dummy_png_b64(),
            "signature_image_b64": create_dummy_png_b64(),
            "enabled": True
        }
        ok = self.db.save_installer_profile(profile_data)
        self.assertTrue(ok)

        retrieved = self.db.get_installer_profile()
        self.assertEqual(retrieved["company_name"], "SARL CCTV PRO ALGERIE")
        self.assertEqual(retrieved["installer_name"], "Amine Benali")
        self.assertEqual(retrieved["city"], "البليدة")
        self.assertTrue(retrieved["enabled"])
        self.assertTrue(len(retrieved["seal_image_b64"]) > 0)

    def test_pdf_stamping_with_seal_and_signature(self):
        """Test that PV de pose and Annex 1 stamp images when enabled."""
        seal_b64 = create_dummy_png_b64()
        sig_b64 = create_dummy_png_b64()

        self.pdf_gen.set_installer_profile({
            "company_name": "SARL CCTV PRO",
            "seal_image_b64": seal_b64,
            "signature_image_b64": sig_b64,
            "enabled": True
        })

        client = {"full_name": "Client Test Seal", "doc_number": "12345", "city": "الجزائر"}
        cameras = [{"model_name": "Cam A", "serial_number": "SN-001"}]

        # PV de Pose test
        pv_bytes = self.pdf_gen.generate_pv_pose(client, cameras, return_bytes=True)
        doc = fitz.open(stream=pv_bytes, filetype="pdf")
        images = doc[0].get_images()
        self.assertGreaterEqual(len(images), 1, "Expected installer seal/signature images on PV de Pose")
        doc.close()

        # Disable test
        self.pdf_gen.set_installer_profile({
            "company_name": "SARL CCTV PRO",
            "seal_image_b64": seal_b64,
            "signature_image_b64": sig_b64,
            "enabled": False
        })
        pv_disabled_bytes = self.pdf_gen.generate_pv_pose(client, cameras, return_bytes=True)
        doc_dis = fitz.open(stream=pv_disabled_bytes, filetype="pdf")
        images_dis = doc_dis[0].get_images()
        self.assertEqual(len(images_dis), 0, "Expected NO images when installer seal is disabled")
        doc_dis.close()

if __name__ == "__main__":
    unittest.main()
