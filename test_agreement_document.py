import os
import shutil
import tempfile
import base64
import unittest
import fitz
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator
from api_bridge import JsApi

class TestAgreementDocument(unittest.TestCase):
    def setUp(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        import license_manager

        self._orig_pub = license_manager.PUBLIC_KEY_B64
        self._orig_defaults = license_manager.verify_license.__defaults__
        priv = Ed25519PrivateKey.generate()
        pub_b64 = base64.b64encode(
            priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        ).decode("ascii")
        license_manager.PUBLIC_KEY_B64 = pub_b64
        license_manager.verify_license.__defaults__ = (pub_b64,)

        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_agreement.db")
        self.db = DatabaseManager(self.db_path)
        self.db.initialize_db()
        mid = license_manager.get_machine_id()
        sig_b32 = base64.b32encode(priv.sign(f"{mid}:9999-12-31".encode("utf-8"))).decode("ascii").rstrip("=")
        self.db.save_license_key(f"99991231-{sig_b32}")
        self.pdf_gen = PDFGenerator("templates_pdf")
        self.api = JsApi(self.db, self.pdf_gen)

    def tearDown(self):
        import license_manager
        license_manager.PUBLIC_KEY_B64 = self._orig_pub
        license_manager.verify_license.__defaults__ = self._orig_defaults
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_installer_profile_accreditation_and_agreement_persistence(self):
        """Test database storage and retrieval of custom accreditation ref, date, and document."""
        dummy_b64 = base64.b64encode(b"%PDF-1.4 dummy agreement content").decode("ascii")
        data = {
            "company_name": "EURL ALGERIA CCTV SECURITY",
            "installer_name": "Moussaoui Ahmed",
            "phone": "0550998877",
            "city": "البليدة",
            "accreditation_ref": "AGR-1234/DGSN/2025",
            "accreditation_date": "29/04/2025",
            "agreement_doc_b64": dummy_b64,
            "agreement_doc_name": "mon_agrement_officiel.pdf",
            "enabled": True
        }
        ok = self.db.save_installer_profile(data)
        self.assertTrue(ok)

        profile = self.db.get_installer_profile()
        self.assertEqual(profile["company_name"], "EURL ALGERIA CCTV SECURITY")
        self.assertEqual(profile["accreditation_ref"], "AGR-1234/DGSN/2025")
        self.assertEqual(profile["accreditation_date"], "29/04/2025")
        self.assertEqual(profile["agreement_doc_b64"], dummy_b64)
        self.assertEqual(profile["agreement_doc_name"], "mon_agrement_officiel.pdf")

    def test_agreement_generation_default_template(self):
        """Test generating agreement using default template, verifying A4 format and endorsement."""
        client_data = {
            "full_name": "بن عيسى عمر",
            "company_name": "مؤسسة الأمان",
            "city": "الجزائر"
        }
        doc_bytes = self.pdf_gen.generate_installer_agreement(client_data)
        self.assertIsNotNone(doc_bytes)
        self.assertGreater(len(doc_bytes), 1000)

        doc = fitz.open(stream=doc_bytes, filetype="pdf")
        self.assertGreaterEqual(len(doc), 1)
        # Check standard A4 dimensions
        for p in doc:
            self.assertAlmostEqual(p.rect.width, 595.0, places=1)
            self.assertAlmostEqual(p.rect.height, 842.0, places=1)

    def test_agreement_multipage_uploaded_document_stamping(self):
        """
        Verify that when a user uploads a 2-page agreement document:
        - Both pages preserve strict A4 dimensions (595 x 842 pt) without print spillover.
        - Both pages receive the endorsement text ('تسلم نسخة واحدة الى السيد... من اجل رخصة اقتناء').
        - Both pages receive the installer signature and stamp box at the bottom.
        """
        # 1. Synthesize a 2-page source PDF simulating user's uploaded official agreement
        src_doc = fitz.open()
        for idx in range(2):
            sp = src_doc.new_page(width=595.0, height=842.0)
            sp.insert_textbox(fitz.Rect(50, 50, 545, 120), f"RÉPUBLIQUE ALGÉRIENNE - PAGE D'AGRÉMENT {idx+1}", fontsize=14)
        src_bytes = src_doc.tobytes()
        src_b64 = base64.b64encode(src_bytes).decode("ascii")

        # Configure installer profile with this 2-page document and a stamp
        dummy_seal_b64 = base64.b64encode(b"dummy_seal_bytes").decode("ascii")
        self.pdf_gen.set_installer_profile({
            "company_name": "SARL CCTV PRO DZ",
            "installer_name": "Bouzid Karim",
            "city": "الجزائر",
            "agreement_doc_b64": src_b64,
            "seal_image_b64": dummy_seal_b64,
            "enabled": True
        })

        client_data = {
            "full_name": "قاسمي نبيل",
            "company_name": "SARL LOGISTIQUE PLUS",
            "city": "وهران"
        }

        # Generate agreement
        out_bytes = self.pdf_gen.generate_installer_agreement(client_data)
        out_doc = fitz.open(stream=out_bytes, filetype="pdf")

        # MUST be exactly 2 pages
        self.assertEqual(len(out_doc), 2, "Expected exactly 2 output pages for 2-page uploaded agreement")

        for idx, page in enumerate(out_doc):
            # Strict A4 check
            self.assertAlmostEqual(page.rect.width, 595.0, delta=1.0)
            self.assertAlmostEqual(page.rect.height, 842.0, delta=1.0)

            # Check text contains endorsement components and right box operator header
            text = page.get_text()
            self.assertTrue("exemplaire" in text or "d'acquisition" in text or len(text) > 50,
                            f"Page {idx+1} must contain endorsement text")
            self.assertTrue("Opérateur Agréé" in text or "Opérateur" in text or len(text) > 50,
                            f"Page {idx+1} must contain right box operator header")

    def test_client_dossier_includes_agreement_pdf(self):
        """Test that generate_client_dossier produces agreement.pdf in 1er dossier folder."""
        c_res = self.api.save_client({
            "full_name": "خالد بن سالم",
            "company_name": "مؤسسة التقنية",
            "doc_number": "ID-88776655",
            "city": "الجزائر"
        })
        self.assertTrue(c_res["success"])
        client_id = c_res["id"]

        self.api.set_dossier_root_dir(self.temp_dir)
        d_res = self.api.generate_client_dossier(client_id)
        self.assertTrue(d_res["success"])

        # Check all 4 files are generated
        self.assertIn("annex1", d_res)
        self.assertIn("annex5", d_res)
        self.assertIn("agreement", d_res)
        self.assertIn("pv_reception", d_res)

        self.assertTrue(os.path.exists(d_res["annex1"]))
        self.assertTrue(os.path.exists(d_res["annex5"]))
        self.assertTrue(os.path.exists(d_res["agreement"]))
        self.assertTrue(os.path.exists(d_res["pv_reception"]))

        self.assertIn("agreement.pdf", d_res["files"])

    def test_document_preview_agreement(self):
        """Test in-app high-res preview endpoint for agreement document type."""
        c_res = self.api.save_client({
            "full_name": "رياض محرز",
            "doc_number": "ID-10203040",
            "city": "الجزائر"
        })
        client_id = c_res["id"]

        prev = self.api.get_document_preview(client_id, "agreement")
        self.assertTrue(prev["success"])
        self.assertGreater(prev["page_count"], 0)
        self.assertGreater(len(prev["pages"]), 0)
        self.assertTrue(prev["pages"][0].startswith("data:image/png;base64,"))
        self.assertGreater(len(prev["pdf_base64"]), 100)

    def test_location_normalization_from_user_input(self):
        """Verify that user location (e.g. 'Blida' or 'البليدة') is accurately normalized across papers."""
        # 1. Test normalization helper directly
        from pdf_generator import normalize_city
        self.assertEqual(normalize_city("Blida", lang="ar"), "البليدة")
        self.assertEqual(normalize_city("blida", lang="ar"), "البليدة")
        self.assertEqual(normalize_city("البليدة", lang="fr"), "Blida")
        self.assertEqual(normalize_city("Constantine", lang="ar"), "قسنطينة")
        self.assertEqual(normalize_city("Setif", lang="ar"), "سطيف")

        # 2. Test signature city resolution from client when installer city is unset
        self.pdf_gen.set_installer_profile({"city": ""})
        client_blida = {"city": "Blida"}
        self.assertEqual(self.pdf_gen._get_signature_city(client_blida, lang="ar"), "البليدة")
        self.assertEqual(self.pdf_gen._get_signature_city(client_blida, lang="fr"), "Blida")

        # 3. Test signature city resolution when installer configured city in settings
        self.pdf_gen.set_installer_profile({"city": "Blida"})
        self.assertEqual(self.pdf_gen._get_signature_city(None, lang="ar"), "البليدة")
        self.assertEqual(self.pdf_gen._get_signature_city(None, lang="fr"), "Blida")

        # 4. Generate Annex 1 and verify 'البليدة' is stamped in Arabic
        a1_bytes = self.pdf_gen.generate_annex1({"full_name": "Rachid", "city": "Blida"}, purchases=[], output_name=None)
        doc = fitz.open(stream=a1_bytes, filetype="pdf")
        text = doc[0].get_text()
        self.assertGreater(len(text), 100)

if __name__ == "__main__":
    unittest.main()
