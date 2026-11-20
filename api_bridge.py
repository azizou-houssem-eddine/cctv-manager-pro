import os
import subprocess
import re
import base64
import threading
import datetime
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator, sanitize_dossier_name
from license_manager import verify_license, check_clock_rollback, get_machine_id

class JsApi:
    """Bridge exposed to JavaScript inside pywebview via window.pywebview.api."""

    def __init__(self, db: DatabaseManager, pdf_gen: PDFGenerator, window=None):
        self._db = db
        self._pdf_gen = pdf_gen
        self._window = window
        try:
            self._pdf_gen.set_installer_profile(self._db.get_installer_profile())
            # Run startup auto-backup asynchronously in background after initial delay
            def _delayed_backup():
                import time
                time.sleep(5)
                try:
                    self._db.auto_backup_on_startup()
                except Exception:
                    pass
            threading.Thread(target=_delayed_backup, daemon=True).start()
        except Exception:
            pass

    def set_window(self, window):
        """Bind active pywebview window for native OS dialogs."""
        self._window = window

    # --- Licensing & System Initialization ---
    def get_license_status(self):
        """Verifies license status, days left, expiration, and hardware Machine ID."""
        try:
            lic_data = self._db.get_license_data()
            key = lic_data.get("license_key")
            last_run = lic_data.get("last_run_date")
            machine_id = get_machine_id()

            if not check_clock_rollback(last_run):
                return {
                    "success": False,
                    "valid": False,
                    "tampered": True,
                    "error": "Alerte Sécurité: Horloge système modifiée / تنبيه أمني: تم التلاعب بساعة النظام",
                    "machine_id": machine_id
                }

            valid, payload = verify_license(key)
            if not valid:
                return {
                    "success": True,
                    "valid": False,
                    "tampered": False,
                    "error": payload if isinstance(payload, str) else "Licence invalide / ترخيص غير صالح",
                    "machine_id": machine_id,
                    "license_key": key or ""
                }

            # Update last run date for clock rollback protection
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            self._db.update_last_run_date(today_str)

            return {
                "success": True,
                "valid": True,
                "tampered": False,
                "days_left": payload.get("days_left", 0),
                "expiry": payload.get("expiry", ""),
                "is_lifetime": payload.get("is_lifetime", False),
                "machine_id": machine_id,
                "license_key": key
            }
        except Exception as e:
            return {"success": False, "valid": False, "error": str(e), "machine_id": get_machine_id()}

    def activate_license(self, license_key: str):
        """Validates and saves a new license key on current machine."""
        try:
            if not license_key or not str(license_key).strip():
                return {"success": False, "error": "Le code de licence ne peut pas être vide / لا يمكن ترك مفتاح الترخيص فارغاً"}

            clean_key = str(license_key).strip().upper()
            valid, payload = verify_license(clean_key)
            if not valid:
                return {"success": False, "error": payload if isinstance(payload, str) else "Clé de licence invalide"}

            self._db.save_license_key(clean_key)
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            self._db.update_last_run_date(today_str)

            return {
                "success": True,
                "license": {
                    "valid": True,
                    "days_left": payload.get("days_left", 0),
                    "expiry": payload.get("expiry", ""),
                    "is_lifetime": payload.get("is_lifetime", False),
                    "machine_id": payload.get("machine_id", ""),
                    "license_key": clean_key
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_system_init_status(self):
        """Returns comprehensive initialization status on application launch."""
        try:
            lic = self.get_license_status()
            onboarding_done = self._db.get_onboarding_status()
            installer_profile = self._db.get_installer_profile()
            dossier_root = self._db.get_dossier_root_dir()

            return {
                "success": True,
                "license": lic,
                "onboarding_completed": onboarding_done,
                "installer_profile": installer_profile,
                "dossier_root": dossier_root
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def complete_onboarding(self, data: dict):
        """Saves initial profile and settings, flags onboarding as complete."""
        try:
            profile = data.get("installer_profile")
            if profile and isinstance(profile, dict):
                norm_profile = {
                    "company_name": profile.get("company_name") or profile.get("installer_company_name", ""),
                    "installer_name": profile.get("installer_name", ""),
                    "phone": profile.get("phone") or profile.get("installer_phone", ""),
                    "city": profile.get("city") or profile.get("installer_city", ""),
                    "accreditation_ref": profile.get("accreditation_ref") or profile.get("installer_accreditation_ref", ""),
                    "accreditation_date": profile.get("accreditation_date") or profile.get("installer_accreditation_date", ""),
                    "agreement_doc_b64": profile.get("agreement_doc_b64", ""),
                    "agreement_doc_name": profile.get("agreement_doc_name", ""),
                    "seal_image_b64": profile.get("seal_image_b64", ""),
                    "signature_image_b64": profile.get("signature_image_b64", ""),
                    "enabled": profile.get("enabled", True)
                }
                self._db.save_installer_profile(norm_profile)
                self._pdf_gen.set_installer_profile(self._db.get_installer_profile())

            dossier_root = data.get("dossier_root")
            if dossier_root and str(dossier_root).strip():
                self._db.set_dossier_root_dir(str(dossier_root).strip())

            if data.get("seed_demo"):
                try:
                    from seed_data import seed_database
                    seed_database(self._db)
                except Exception:
                    pass

            self._db.set_onboarding_completed(True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _require_valid_license(self):
        """Internal gate checking if license is active before allowing regulatory actions."""
        lic = self.get_license_status()
        if not lic.get("valid"):
            err_msg = lic.get("error") or "Licence requise ou expirée / ترخيص مطلوب أو منتهي الصلاحية"
            return False, err_msg
        return True, None

    # --- Executive Dashboard & Analytics (R1) ---
    def get_dashboard_analytics(self):
        try:
            data = self._db.get_dashboard_analytics()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Camera Models ---
    def get_camera_models(self):
        try:
            return {"success": True, "data": self._db.get_camera_models()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_camera_model(self, data):
        try:
            name = (data.get("model_name") or "").strip()
            if not name:
                return {"success": False, "error": "Model name is required"}
            mid = self._db.add_camera_model(
                name,
                data.get("equipment_designation", ""),
                data.get("equipment_nature", ""),
                data.get("category", ""),
                data.get("sub_category", "")
            )
            return {"success": mid > 0, "id": mid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_camera_model(self, model_id):
        try:
            ok = self._db.delete_camera_model(int(model_id))
            if not ok:
                return {"success": False, "error": "Cannot delete model with active camera assignments."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_model_threshold(self, model_id, threshold):
        try:
            ok = self._db.update_model_threshold(int(model_id), int(threshold))
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_camera_model(self, *args, **kwargs):
        try:
            if len(args) == 1 and isinstance(args[0], dict):
                data = args[0]
            elif kwargs:
                data = kwargs
            elif len(args) >= 2:
                keys = ["model_id", "model_name", "equipment_designation", "technical_nature", "regulatory_section", "regulatory_subsection", "low_stock_threshold"]
                data = dict(zip(keys, args))
            else:
                return {"success": False, "error": "Invalid arguments for update_camera_model"}
            
            mid = data.get("model_id") or data.get("id")
            name = (data.get("model_name") or "").strip()
            if not mid or not name:
                return {"success": False, "error": "Model ID and name are required"}
            
            ok = self._db.update_camera_model(
                model_id=int(mid),
                model_name=name,
                equipment_designation=data.get("equipment_designation", ""),
                technical_nature=data.get("technical_nature") or data.get("equipment_nature", ""),
                regulatory_section=data.get("regulatory_section") or data.get("category", ""),
                regulatory_subsection=data.get("regulatory_subsection") or data.get("sub_category", ""),
                low_stock_threshold=int(data.get("low_stock_threshold", data.get("threshold", 5)))
            )
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_serial_history(self, serial_number=None, client_id=None, limit=50):
        try:
            cid = int(client_id) if client_id is not None else None
            sn = str(serial_number).strip() if serial_number else None
            rows = self._db.get_serial_history(serial_number=sn, client_id=cid, limit=int(limit or 50))
            return {"success": True, "data": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Inventory & Serials ---
    def save_single_serial_direct(self, model_id, serial_number):
        try:
            if not model_id:
                return {"success": False, "error": "invalid_model", "message": "Modèle manquant"}
            return self._db.save_single_serial_direct(int(model_id), str(serial_number))
        except Exception as e:
            return {"success": False, "error": str(e), "message": str(e)}

    def delete_serial_number(self, serial_id):
        try:
            if not serial_id:
                return {"success": False, "error": "invalid_id", "message": "ID manquant"}
            return self._db.delete_serial_number(int(serial_id))
        except Exception as e:
            return {"success": False, "error": str(e), "message": str(e)}

    def delete_serials_batch(self, serial_ids):
        try:
            if not isinstance(serial_ids, list):
                return {"success": False, "error": "invalid_format", "message": "Liste d'identifiants requise"}
            clean_ids = [int(sid) for sid in serial_ids if str(sid).strip().isdigit()]
            return self._db.delete_serials_batch(clean_ids)
        except Exception as e:
            return {"success": False, "error": str(e), "message": str(e)}

    def save_scanned_serials(self, model_id, serial_list):
        try:
            if not model_id or not serial_list:
                return {"success": False, "error": "Model and serials are required"}
            inserted = self._db.save_serial_batch(int(model_id), serial_list)
            return {"success": True, "count": inserted}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_inventory_serials(self, model_id=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            data = self._db.get_all_serials(mid)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_serials(self, query=None, model_id=None, status=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            data = self._db.search_serials(query=query, model_id=mid, status=status)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def preview_csv_serials(self, raw_content):
        try:
            res = self._db.preview_csv_serials(raw_content)
            res["success"] = True
            return res
        except Exception as e:
            return {
                "success": False,
                "total_found": 0,
                "valid": [],
                "already_in_db": [],
                "duplicates_in_file": [],
                "error": str(e)
            }

    # --- Unified Intelligent Excel / CSV / TXT Import ---
    def preview_unified_import(self, data):
        """
        Preview and pre-flight validate multi-format files (.xlsx, .xls, .csv, .txt).
        Data dict: { 'file_data': base64/str, 'filename': str, 'destination_model_id': int|None }
        """
        try:
            if not isinstance(data, dict):
                return {"success": False, "error": "Invalid payload format"}
            file_data = data.get("file_data") or data.get("raw_content") or ""
            filename = data.get("filename") or ""
            destination_model_id = data.get("destination_model_id")
            if destination_model_id in ("", "null", "None"):
                destination_model_id = None
            elif destination_model_id is not None:
                destination_model_id = int(destination_model_id)

            res = self._db.parse_and_preview_import(
                raw_content=file_data,
                filename=filename,
                destination_model_id=destination_model_id
            )
            return res
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": "UNKNOWN",
                "total_detected": 0,
                "valid_items": [],
                "duplicates_in_file": [],
                "already_in_db": [],
                "new_models_to_create": []
            }

    def commit_unified_import(self, data):
        """
        Commit validated import items into database.
        Data dict: { 'mode': str, 'items': list, 'destination_model_id': int|None }
        """
        try:
            if not isinstance(data, dict):
                return {"success": False, "error": "Invalid payload format"}
            mode = data.get("mode") or ""
            items = data.get("items") or []
            destination_model_id = data.get("destination_model_id")
            if destination_model_id in ("", "null", "None"):
                destination_model_id = None
            elif destination_model_id is not None:
                destination_model_id = int(destination_model_id)

            return self._db.commit_unified_import(mode, items, destination_model_id=destination_model_id)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_import_template(self, template_type):
        """
        Generate and return pre-styled sample Excel workbook as Base64 data URI.
        template_type: 'catalog' | 'manifest'
        """
        try:
            t_type = str(template_type).lower()
            file_bytes = self._db.generate_import_template(t_type)
            b64_data = base64.b64encode(file_bytes).decode("ascii")
            filename = "modele_catalogue_template.xlsx" if t_type == "catalog" else "manifeste_livraison_template.xlsx"
            return {
                "success": True,
                "filename": filename,
                "base64": b64_data,
                "data_uri": f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_data}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def import_serials_batch(self, model_id, serial_list):
        try:
            if not model_id or not serial_list:
                return {"success": False, "error": "Model and serials are required", "imported_count": 0, "duplicates_skipped": 0}
            return self._db.import_serials_batch(int(model_id), serial_list)
        except Exception as e:
            return {"success": False, "imported_count": 0, "duplicates_skipped": 0, "error": str(e)}

    def export_serials_csv(self, model_id=None, status=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            csv_str = self._db.export_serials_csv(model_id=mid, status=status)
            return {
                "success": True,
                "csv_data": csv_str,
                "filename": "inventaire_serials.csv"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_serials_excel(self, model_id=None, status=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            excel_bytes = self._db.export_serials_excel(model_id=mid, status=status)
            b64_data = base64.b64encode(excel_bytes).decode("ascii")
            return {
                "success": True,
                "filename": "inventaire_serials.xlsx",
                "base64": b64_data,
                "data_uri": f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_data}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_serials(self, model_id):
        try:
            if not model_id:
                return {"success": True, "data": []}
            data = self._db.get_available_serials(int(model_id))
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assign_cameras(self, client_id, serial_ids):
        try:
            if not client_id or not serial_ids:
                return {"success": False, "error": "Client and cameras are required"}
            count = self._db.assign_cameras_batch(int(client_id), [int(s) for s in serial_ids])
            return {"success": True, "count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assign_camera_by_serial_number(self, client_id, serial_number):
        try:
            if not client_id or not serial_number:
                return {"success": False, "error": "Client et numéro de série requis"}
            return self._db.assign_camera_by_serial_number(int(client_id), str(serial_number))
        except Exception as e:
            return {"success": False, "error": str(e), "message": str(e)}

    def assign_n_cameras_by_model(self, client_id, model_id, count):
        try:
            if not client_id or not model_id or not count:
                return {"success": False, "error": "Client, modèle et quantité requis"}
            return self._db.assign_n_cameras_by_model(int(client_id), int(model_id), int(count))
        except Exception as e:
            return {"success": False, "error": str(e), "message": str(e)}

    def return_cameras(self, serial_numbers):
        try:
            if not serial_numbers:
                return {"success": False, "error": "No serial numbers provided"}
            count = self._db.return_cameras_batch(serial_numbers)
            return {"success": True, "count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Clients ---
    def get_clients(self, search_query=""):
        try:
            data = self._db.get_clients(search_query)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_client(self, client_id):
        try:
            client = self._db.get_client(int(client_id))
            if not client:
                return {"success": False, "error": "Client not found"}
            purchases = self._db.get_client_purchases_for_pdf(int(client_id))
            return {"success": True, "client": client, "cameras": purchases["cameras"]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_client(self, data):
        try:
            full_name = (data.get("full_name") or "").strip()
            doc_num = (data.get("doc_number") or "").strip()
            if not full_name and not data.get("company_name"):
                return {"success": False, "error": "Client name or Company name is required"}
            if not doc_num:
                return {"success": False, "error": "ID or Passport document number is required"}
            
            cid = self._db.add_client(data)
            if not cid:
                return {"success": False, "error": "Client with this ID/Passport number already exists."}
            return {"success": True, "id": cid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_client(self, client_id, data):
        try:
            cid = int(client_id)
            ok = self._db.update_client(cid, data)
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_client(self, client_id):
        try:
            cid = int(client_id)
            ok = self._db.delete_client(cid)
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- PDF & Folder Actions ---
    def get_document_preview(self, client_id, doc_type):
        """
        In-app high-resolution document preview endpoint.
        Renders Annex 1, Annex 5, or PV de Pose into 150 DPI Pixmap PNGs (Base64 data URIs)
        and provides Base64 PDF serialization for direct print/export.
        """
        try:
            cid = int(client_id)
            data = self._db.get_client_purchases_for_pdf(cid)
            client = data.get("client")
            if not client:
                return {
                    "success": False,
                    "error": f"Client with ID {cid} not found",
                    "doc_type": doc_type,
                    "title": "",
                    "client_name": "",
                    "page_count": 0,
                    "pages": [],
                    "pdf_base64": ""
                }
            cameras = data.get("cameras", [])
            return self._pdf_gen.get_document_preview_data(client, cameras, doc_type=doc_type)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "doc_type": doc_type,
                "title": "",
                "client_name": "",
                "page_count": 0,
                "pages": [],
                "pdf_base64": ""
            }

    # --- Dossier Directory Management ---
    def get_dossier_root_dir(self):
        try:
            return {"success": True, "path": self._db.get_dossier_root_dir()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_dossier_root_dir(self, path):
        try:
            if not path or not str(path).strip():
                return {"success": False, "error": "Folder path cannot be empty"}
            clean = self._db.set_dossier_root_dir(path)
            return {"success": True, "path": clean}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def select_dossier_root_dir(self):
        try:
            if self._window:
                import webview
                result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
                if result and len(result) > 0:
                    selected = os.path.abspath(result[0])
                    self._db.set_dossier_root_dir(selected)
                    return {"success": True, "path": selected}
                return {"success": False, "cancelled": True}
            return {"success": True, "path": self._db.get_dossier_root_dir()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_dossiers_root_dir(self):
        try:
            path = self._db.get_dossier_root_dir()
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            os.startfile(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Client Dossier Generation (R4 & Phase 2) ---
    def generate_client_dossier(self, client_id):
        try:
            is_valid, err = self._require_valid_license()
            if not is_valid:
                return {"success": False, "error": err, "license_required": True}

            cid = int(client_id)
            data = self._db.get_client_purchases_for_pdf(cid)
            client = data.get("client")
            if not client:
                return {"success": False, "error": "Client not found"}
            
            cameras = data.get("cameras", [])
            root_dir = self._db.get_dossier_root_dir()
            res = self._pdf_gen.generate_client_dossier(client, cameras, base_dir=root_dir, dossier_type="1er dossier")
            return {
                "success": True,
                "folder": res.get("folder"),
                "folder_path": res.get("folder_path"),
                "annex1": res.get("annex1"),
                "annex5": res.get("annex5"),
                "agreement": res.get("agreement"),
                "pv_reception": res.get("pv_reception"),
                "files": res.get("files"),
                "client_name": client.get("full_name") or client.get("company_name")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_second_dossier(self, client_id):
        try:
            is_valid, err = self._require_valid_license()
            if not is_valid:
                return {"success": False, "error": err, "license_required": True}

            cid = int(client_id)
            data = self._db.get_client_purchases_for_pdf(cid)
            client = data.get("client")
            if not client:
                return {"success": False, "error": "Client not found"}
            
            cameras = data.get("cameras", [])
            root_dir = self._db.get_dossier_root_dir()
            res = self._pdf_gen.generate_second_dossier(client, cameras, base_dir=root_dir)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_client_folder(self, client_id):
        try:
            client = self._db.get_client(int(client_id))
            if not client:
                return {"success": False, "error": "Client not found"}
            cname = client.get("full_name") or client.get("company_name") or f"Client_{client_id}"
            sanitized = sanitize_dossier_name(cname)
            root_dir = self._db.get_dossier_root_dir()

            # Priority 1: <root>/<Client Name>/1er dossier
            # Priority 2: <root>/<Client Name>/1er_dossier
            # Priority 3: <root>/<Client Name>
            p_space = os.path.abspath(os.path.join(root_dir, sanitized, "1er dossier"))
            p_under = os.path.abspath(os.path.join(root_dir, sanitized, "1er_dossier"))
            p_client = os.path.abspath(os.path.join(root_dir, sanitized))
            legacy_path = os.path.abspath(os.path.join("1er dossier", sanitized))

            if os.path.exists(p_space):
                folder_path = p_space
            elif os.path.exists(p_under):
                folder_path = p_under
            elif os.path.exists(p_client):
                folder_path = p_client
            elif os.path.exists(legacy_path):
                folder_path = legacy_path
            else:
                folder_path = p_space
                os.makedirs(folder_path, exist_ok=True)
                os.makedirs(os.path.join(root_dir, sanitized, "2eme dossier"), exist_ok=True)
            
            os.startfile(folder_path)
            return {"success": True, "path": folder_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_file(self, file_path):
        try:
            abs_path = os.path.abspath(file_path)
            if os.path.exists(abs_path):
                os.startfile(abs_path)
                return {"success": True}
            return {"success": False, "error": "File not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Database Maintenance & Seeding ---
    def clear_database(self):
        try:
            ok = self._db.clear_database()
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def seed_demo_data(self):
        try:
            from seed_data import seed_database
            res = seed_database(self._db, self._pdf_gen)
            return {"success": True, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Database Backup & Restore Engine ---
    def create_database_backup(self, custom_path=None):
        try:
            return self._db.create_database_backup(custom_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_database_backup(self):
        try:
            if self._window:
                import webview
                import datetime
                default_name = f"cctv_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                result = self._window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename=default_name,
                    file_types=["SQLite Database (*.db;*.sqlite;*.bak)"]
                )
                if result:
                    dest = result if isinstance(result, str) else result[0]
                    return self._db.create_database_backup(destination_path=dest)
                return {"success": False, "cancelled": True}
            return self._db.create_database_backup()
        except Exception as e:
            return {"success": False, "error": str(e)}

    def restore_database_dialog(self):
        try:
            if self._window:
                import webview
                result = self._window.create_file_dialog(
                    webview.OPEN_DIALOG,
                    file_types=["SQLite Database (*.db;*.sqlite;*.bak)"]
                )
                if result and len(result) > 0:
                    chosen_file = result[0]
                    res = self._db.restore_database_from_backup(chosen_file)
                    if res.get("success"):
                        self._pdf_gen.set_installer_profile(self._db.get_installer_profile())
                    return res
                return {"success": False, "cancelled": True}
            return {"success": False, "error": "Boîte de dialogue native non disponible"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_backup_status(self):
        try:
            return {"success": True, "data": self._db.get_backup_status()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_backups_directory(self):
        try:
            status = self._db.get_backup_status()
            bdir = status.get("backups_dir", os.path.abspath("backups"))
            if not os.path.exists(bdir):
                os.makedirs(bdir, exist_ok=True)
            os.startfile(bdir)
            return {"success": True, "path": bdir}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Installer Seal & Signature Profile ---
    def get_installer_profile(self):
        try:
            profile = self._db.get_installer_profile()
            return {"success": True, "data": profile}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_installer_profile(self, data):
        try:
            ok = self._db.save_installer_profile(data)
            if ok:
                self._pdf_gen.set_installer_profile(self._db.get_installer_profile())
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}
