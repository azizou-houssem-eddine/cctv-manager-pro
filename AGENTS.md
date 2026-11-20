# AGENTS.md - CCTV Manager Pro

Comprehensive developer and agent reference for the **CCTV Manager Pro** repository.

---

## 1. Project Overview

**CCTV Manager Pro** is a Windows 11 desktop application designed for CCTV security equipment installers and vendors operating under Algerian regulatory compliance.

### Core Capabilities
- **Inventory & Serial Tracking:** Barcode scanner-compatible batch entry of camera serial numbers linked to specific catalog models. Tracks stock lifecycle (`in_stock` vs. `assigned`).
- **Client Lifecycle Management:** Detailed client directory storing civil identity, identity documents (national ID/passport), corporate credentials, and installation logistics.
- **Equipment Assignment & Return:** Assign available serialized cameras to clients; supports batch assignment and multi-camera return workflows.
- **Regulatory Scanned PDF Stamping:**
  - **1er Dossier (Acquisition Phase):**
    - **Annex 1 (Official Gazette #54, 2017 Page 18):** Equipment declaration form stamped with client identity, logistics, and aggregated camera models.
    - **Annex 5 (Official Gazette #54, 2017 Page 21):** Security clearance questionnaire stamped with 29 civil, corporate, and document fields.
    - **Agrément de l'Installateur (اعتماد القائم بالتركيب):** Authentic installer license stamped on each page with regulatory endorsement (`تسلم نسخة واحدة الى السيد... من اجل رخصة اقتناء`) and seal/signature.
    - **PV de Réception / Bordereau de Pose:** Vector installation receipt detailing all exact serial numbers.
  - **2ème Dossier (Exploitation Phase):**
    - **Annex 3 Extended (Official Gazette #63, 2011):** Sensitive equipment exploitation license request with an extended 15-row regulatory table.
    - **Annex 8 (Official Gazette #09, 2016 - Décret exécutif 16-61):** Official commitment of non-connection of sensitive equipment to the global internet network.
    - **PV de Réception:** Companion installation receipt.
  - Generates modular dossier folders (`dossiers/<Client_Name>/1er_dossier/` and `dossiers/<Client_Name>/2eme_dossier/`).
- **Bilingual Interface:** Real-time toggling between French (`fr`) and Arabic (`ar`) with dynamic RTL (Right-To-Left) and LTR layout switching.

---

## 2. Tech Stack & Environment

- **Language:** Python 3.10+ (Verified on Python 3.14.5 Windows 11)
- **GUI Engine:** `pywebview` (v6.x) utilizing native Microsoft Edge WebView2 runtime on Windows 10/11
- **Frontend:** Modern HTML5, CSS3 (Windows 11 Fluent dark theme, responsive grid), Vanilla JS
- **Database Engine:** SQLite3 (Local file: `cctv_manager.db`, foreign keys enabled)
- **Document Engine:** `PyMuPDF` (`fitz` v1.27+) with `arabic_reshaper` & `python-bidi`
- **Official Scanned Templates:**
  - `templates_pdf/annex1_template.pdf` (Gazette #54 Page 18)
  - `templates_pdf/annex5_template.pdf` (Gazette #54 Page 21)
  - `templates_pdf/annex3_extended_template.pdf` (Gazette #63 Extended 15-row table)
  - `templates_pdf/annex8_internet_commitment_template.pdf` (Gazette #09 Décret 16-61)
- **Executable Bundler:** PyInstaller (`build.py`)

---

## 3. Repository File Structure

```text
d:\programation\cctv\
├── AGENTS.md                  # Agent instruction file (this document)
├── README.md                  # Human-facing overview and setup
├── main.py                    # pywebview application entry point & window lifecycle
├── api_bridge.py              # JsApi Python bridge exposed to JavaScript (window.pywebview.api)
├── db_manager.py              # SQLite database manager, schemas, queries, and migrations
├── pdf_generator.py           # PyMuPDF coordinate stamping engine with Arabic BiDi shaping
├── build.py                   # PyInstaller single-file build automation script
├── cctv_manager.db            # SQLite database file (generated at runtime)
├── templates_pdf/             # Official scanned PDF templates
│   ├── annex1_template.pdf    # Official Gazette Page 18 (Annex 1)
│   ├── annex5_template.pdf    # Official Gazette Page 21 (Annex 5)
│   ├── annex3_extended_template.pdf # Gazette #63 Extended 15-row Table (Annex 3)
│   └── annex8_internet_commitment_template.pdf # Gazette #09 Décret 16-61 (Annex 8)
├── web/                       # Modern Fluent UI web frontend
│   ├── index.html             # Application shell, dual dossier switcher & modals
│   ├── style.css              # Windows 11 dark theme Fluent styling with RTL support
│   └── app.js                 # State, barcode listener, API bridge calls, translations
├── dossiers/                  # Root directory for generated client dossiers
│   └── <Client_Name>/
│       ├── 1er_dossier/       # annex1.pdf, annex5.pdf, agreement.pdf, pv_reception.pdf
│       └── 2eme_dossier/      # annex3.pdf, annex8.pdf, pv_reception.pdf
└── dist/                      # PyInstaller output directory (contains CCTV_Manager_Pro.exe)
```

---

## 4. Setup & Execution Commands

### Prerequisites
Ensure Python 3.10+ is installed on Windows 11.

### Dependency Installation
```powershell
pip install pywebview PyMuPDF arabic-reshaper python-bidi pyinstaller
```

### Running the Application (Development)
```powershell
python main.py
```

### Building the Standalone Executable
```powershell
python build.py
```
*Note: The executable will be generated in `dist/CCTV_Manager_Pro.exe` with `web/` and `templates_pdf/` bundled via `--add-data`.*

---

## 5. Database Architecture (`db_manager.py`)

The application uses an embedded SQLite database (`cctv_manager.db`) with `PRAGMA foreign_keys = ON;`.

### Tables & Relationships
- `camera_models`: Stores internal model name, official designation, nature, section (القسم), subsection (الفرع).
- `clients`: Complete civil identity, national ID / passport data, company credentials, shareholders, and logistics.
- `serial_numbers`: Serial strings linked to a `model_id`, with `is_used` boolean flag.
- `client_purchases`: Relational link between `client_id` and assigned `serial_id` (enforces unique `serial_id`).

### Key Workflow Methods
- `save_serial_batch(model_id, serials)`: Batch ingestion from barcode scans.
- `assign_cameras_batch(client_id, serial_ids)`: Transactional assignment.
- `return_cameras_batch(serial_numbers)`: Removes from `client_purchases` and sets `is_used = 0`.
- `get_client_purchases_for_pdf(client_id)`: Aggregates client and camera details for document generation.

---

## 6. PDF Stamping Engine (`pdf_generator.py`)

Instead of synthesizing HTML from scratch, the system stamps client data and equipment tables directly onto the authentic Algerian Gazette templates.

### Engineering Controls
1. **Dynamic Font Auto-Scaling:** Uses `fitz.Font.text_length` to measure rendered width against the bounding box. Shrinks text size (from 10.5pt down to 7.0pt) for long client names or corporate titles.
2. **Arabic Shaping & BiDi:** All Arabic text is shaped using `arabic_reshaper.reshape()` and converted to visual RTL order via `bidi.algorithm.get_display()`.
3. **Calibrated Dot Masking:** Preprinted dotted lines (`................`) are cleanly whited out before stamping to avoid visual collision.
4. **Equipment Grouping:** Groups individual cameras by model and designation, calculating row totals for the 5-column regulatory table on Annex 1.

---

## 7. Developer & Agent Guidelines

1. **Frontend-Backend Bridge:** All backend functionality must be exposed as methods on `JsApi` in `api_bridge.py`. JavaScript calls them asynchronously via `await window.pywebview.api.<method>()`.
2. **Path Sanitization:** Always sanitize client folder names before filesystem operations using `re.sub(r'[\\/*?:"<>|]', "_", client_name)`.
3. **Packaging Assets:** Any new assets (templates, icons, styles) must be placed inside `web/` or `templates_pdf/` and registered in `build.py` with `--add-data`.
4. **Translations (`ui-translator`):** Whenever adding new UI controls or messages, update both `fr` and `ar` in the `TRANSLATIONS` dictionary in `web/app.js`.
