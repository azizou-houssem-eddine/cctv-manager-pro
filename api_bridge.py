import os
import subprocess
import re
import base64
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator, sanitize_dossier_name

class JsApi:
    """Bridge exposed to JavaScript inside pywebview via window.pywebview.api."""

    def __init__(self, db: DatabaseManager, pdf_gen: PDFGenerator, window=None):
        self.db = db
        self.pdf_gen = pdf_gen
        self.window = window

    def set_window(self, window):
        """Bind active pywebview window for native OS dialogs."""
        self.window = window

    # --- Executive Dashboard & Analytics (R1) ---
    def get_dashboard_analytics(self):
        try:
            data = self.db.get_dashboard_analytics()
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Camera Models ---
    def get_camera_models(self):
        try:
            return {"success": True, "data": self.db.get_camera_models()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_camera_model(self, data):
        try:
            name = (data.get("model_name") or "").strip()
            if not name:
                return {"success": False, "error": "Model name is required"}
            mid = self.db.add_camera_model(
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
            ok = self.db.delete_camera_model(int(model_id))
            if not ok:
                return {"success": False, "error": "Cannot delete model with active camera assignments."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_model_threshold(self, model_id, threshold):
        try:
            ok = self.db.update_model_threshold(int(model_id), int(threshold))
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Inventory & Serials ---
    def save_scanned_serials(self, model_id, serial_list):
        try:
            if not model_id or not serial_list:
                return {"success": False, "error": "Model and serials are required"}
            inserted = self.db.save_serial_batch(int(model_id), serial_list)
            return {"success": True, "count": inserted}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_inventory_serials(self, model_id=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            data = self.db.get_all_serials(mid)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_serials(self, query=None, model_id=None, status=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            data = self.db.search_serials(query=query, model_id=mid, status=status)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def preview_csv_serials(self, raw_content):
        try:
            res = self.db.preview_csv_serials(raw_content)
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

    def import_serials_batch(self, model_id, serial_list):
        try:
            if not model_id or not serial_list:
                return {"success": False, "error": "Model and serials are required", "imported_count": 0, "duplicates_skipped": 0}
            return self.db.import_serials_batch(int(model_id), serial_list)
        except Exception as e:
            return {"success": False, "imported_count": 0, "duplicates_skipped": 0, "error": str(e)}

    def export_serials_csv(self, model_id=None, status=None):
        try:
            mid = int(model_id) if model_id and str(model_id).strip() not in ("", "all", "None") else None
            csv_str = self.db.export_serials_csv(model_id=mid, status=status)
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
            excel_bytes = self.db.export_serials_excel(model_id=mid, status=status)
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
            data = self.db.get_available_serials(int(model_id))
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def assign_cameras(self, client_id, serial_ids):
        try:
            if not client_id or not serial_ids:
                return {"success": False, "error": "Client and cameras are required"}
            count = self.db.assign_cameras_batch(int(client_id), [int(s) for s in serial_ids])
            return {"success": True, "count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def return_cameras(self, serial_numbers):
        try:
            if not serial_numbers:
                return {"success": False, "error": "No serial numbers provided"}
            count = self.db.return_cameras_batch(serial_numbers)
            return {"success": True, "count": count}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Clients ---
    def get_clients(self, search_query=""):
        try:
            data = self.db.get_clients(search_query)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_client(self, client_id):
        try:
            client = self.db.get_client(int(client_id))
            if not client:
                return {"success": False, "error": "Client not found"}
            purchases = self.db.get_client_purchases_for_pdf(int(client_id))
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
            
            cid = self.db.add_client(data)
            if not cid:
                return {"success": False, "error": "Client with this ID/Passport number already exists."}
            return {"success": True, "id": cid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_client(self, client_id, data):
        try:
            cid = int(client_id)
            ok = self.db.update_client(cid, data)
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_client(self, client_id):
        try:
            cid = int(client_id)
            ok = self.db.delete_client(cid)
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
            data = self.db.get_client_purchases_for_pdf(cid)
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
            return self.pdf_gen.get_document_preview_data(client, cameras, doc_type=doc_type)
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
            return {"success": True, "path": self.db.get_dossier_root_dir()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def set_dossier_root_dir(self, path):
        try:
            if not path or not str(path).strip():
                return {"success": False, "error": "Folder path cannot be empty"}
            clean = self.db.set_dossier_root_dir(path)
            return {"success": True, "path": clean}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def select_dossier_root_dir(self):
        try:
            if self.window:
                import webview
                result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
                if result and len(result) > 0:
                    selected = os.path.abspath(result[0])
                    self.db.set_dossier_root_dir(selected)
                    return {"success": True, "path": selected}
                return {"success": False, "cancelled": True}
            return {"success": True, "path": self.db.get_dossier_root_dir()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_dossiers_root_dir(self):
        try:
            path = self.db.get_dossier_root_dir()
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            os.startfile(path)
            return {"success": True, "path": path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- Client Dossier Generation (R4 & Phase 2) ---
    def generate_client_dossier(self, client_id):
        try:
            cid = int(client_id)
            data = self.db.get_client_purchases_for_pdf(cid)
            client = data.get("client")
            if not client:
                return {"success": False, "error": "Client not found"}
            
            cameras = data.get("cameras", [])
            root_dir = self.db.get_dossier_root_dir()
            res = self.pdf_gen.generate_client_dossier(client, cameras, base_dir=root_dir, dossier_type="1er dossier")
            return {
                "success": True,
                "folder": res.get("folder"),
                "folder_path": res.get("folder_path"),
                "annex1": res.get("annex1"),
                "annex5": res.get("annex5"),
                "pv_reception": res.get("pv_reception"),
                "files": res.get("files"),
                "client_name": client.get("full_name") or client.get("company_name")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_second_dossier(self, client_id):
        try:
            cid = int(client_id)
            data = self.db.get_client_purchases_for_pdf(cid)
            client = data.get("client")
            if not client:
                return {"success": False, "error": "Client not found"}
            
            cameras = data.get("cameras", [])
            root_dir = self.db.get_dossier_root_dir()
            res = self.pdf_gen.generate_second_dossier(client, cameras, base_dir=root_dir)
            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    def open_client_folder(self, client_id):
        try:
            client = self.db.get_client(int(client_id))
            if not client:
                return {"success": False, "error": "Client not found"}
            cname = client.get("full_name") or client.get("company_name") or f"Client_{client_id}"
            sanitized = sanitize_dossier_name(cname)
            root_dir = self.db.get_dossier_root_dir()

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
            ok = self.db.clear_database()
            return {"success": ok}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def seed_demo_data(self):
        try:
            from seed_data import seed_database
            res = seed_database(self.db, self.pdf_gen)
            return {"success": True, "data": res}
        except Exception as e:
            return {"success": False, "error": str(e)}
