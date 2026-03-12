import os
import sys
import webbrowser
from jinja2 import Environment, FileSystemLoader
import subprocess
from datetime import date

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class PDFGenerator:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = resource_path(templates_dir)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))

    def _clean_data(self, client_data):
        # We replace None or empty string with dots
        cleaned = {}
        for k, v in client_data.items():
            if v is None or str(v).strip() == "":
                cleaned[k] = "........................................"
            else:
                cleaned[k] = str(v)
        
        # Display logic for Annex 1 identity
        if cleaned.get("full_name", "").startswith("....") and not cleaned.get("company_name", "").startswith("...."):
            cleaned["display_name"] = cleaned["company_name"]
        elif not cleaned.get("full_name", "").startswith("...."):
            cleaned["display_name"] = cleaned["full_name"]
        else:
            cleaned["display_name"] = "........................................"

        if cleaned.get("storage_location", "").startswith("....") and not cleaned.get("company_hq", "").startswith("...."):
            cleaned["display_storage"] = cleaned["company_hq"]
        elif not cleaned.get("storage_location", "").startswith("...."):
            cleaned["display_storage"] = cleaned["storage_location"]
        else:
            cleaned["display_storage"] = "........................................"

        return cleaned

    def _generate_pdf(self, html_content, output_name):
        html_path = os.path.abspath(output_name.replace(".pdf", ".html"))
        pdf_path = os.path.abspath(output_name)
        
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        path_found = None
        for p in edge_paths:
            if os.path.exists(p):
                path_found = p
                break
                
        if path_found:
            cmd = [
                path_found,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--print-to-pdf=" + pdf_path,
                "file:///" + html_path.replace("\\", "/")
            ]
            subprocess.run(cmd, check=True)
            if os.path.exists(html_path):
                try:
                    os.remove(html_path)
                except:
                    pass
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
                return pdf_path
        
        # Fallback to HTML
        webbrowser.open(f"file://{html_path}")
        return html_path

    def generate_annex5(self, client_data: dict, purchases: list[dict], output_name="annex5.pdf"):
        template = self.env.get_template("annex5.html")
        cleaned_client = self._clean_data(client_data)
        html_content = template.render(client=cleaned_client, purchases=purchases, today_date=date.today().strftime('%d/%m/%Y'))
        return self._generate_pdf(html_content, output_name)

    def generate_annex1(self, client_data: dict, purchases: list[dict], output_name="annex1.pdf"):
        grouped = {}
        for c in purchases:
            k = (c.get("model_name", ""), c.get("equipment_designation", ""), 
                 c.get("equipment_nature", ""), c.get("category", ""), c.get("sub_category", ""))
            grouped[k] = grouped.get(k, 0) + 1
            
        grouped_purchases = []
        for k, v in grouped.items():
            grouped_purchases.append({
                "model_name": k[0] or "....................",
                "equipment_designation": k[1] or "....................",
                "equipment_nature": k[2] or "....................",
                "category": k[3] or "....................",
                "sub_category": k[4] or "....................",
                "quantity": v
            })
            
        template = self.env.get_template("annex1.html")
        cleaned_client = self._clean_data(client_data)
        html_content = template.render(client=cleaned_client, purchases=grouped_purchases, today_date=date.today().strftime('%d/%m/%Y'))
        return self._generate_pdf(html_content, output_name)
