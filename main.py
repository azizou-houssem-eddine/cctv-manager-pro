import os
import sys
import webview
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator, resource_path
from api_bridge import JsApi

def main():
    # 1. Initialize Database and Migrations
    db = DatabaseManager("cctv_manager.db")
    db.initialize_db()

    # 2. Initialize PDF Stamping Engine
    pdf_gen = PDFGenerator("templates_pdf")

    # 3. Create Bridge API
    api = JsApi(db, pdf_gen)

    # 4. Resolve Web Assets Path (Supports Dev and PyInstaller _MEIPASS)
    html_path = resource_path(os.path.join("web", "index.html"))
    if not os.path.exists(html_path):
        html_path = os.path.abspath(os.path.join("web", "index.html"))

    # 5. Create Native Windows 11 WebView2 Window
    window = webview.create_window(
        title="CCTV Manager Pro",
        url=html_path,
        js_api=api,
        width=1320,
        height=860,
        min_size=(1050, 720),
        background_color="#f8fafc"
    )

    # Bind active window instance to bridge for native Windows file/folder dialogs
    api.set_window(window)

    webview.start(debug=False)

if __name__ == "__main__":
    main()