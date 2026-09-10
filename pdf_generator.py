import os
import sys
import re
import math
import base64
from datetime import date
import fitz
import arabic_reshaper
from bidi.algorithm import get_display

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def sanitize_dossier_name(name: str) -> str:
    """
    Sanitize client names for Windows 11 filesystem compatibility:
    - Strips invalid characters (/ \\ : * ? \" < > | and ASCII control characters)
    - Strips trailing dots and spaces (Windows Explorer restriction)
    - Handles reserved device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
    - Clamps to max 100 characters
    - Preserves Arabic Unicode characters
    """
    if not name or not str(name).strip():
        return "Client_Unnamed"
    cleaned = re.sub(r'[\\/*?:"<>|\x00-\x1f]', '_', str(name).strip())
    cleaned = re.sub(r'_+', '_', cleaned).rstrip('. ')
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
    if cleaned.upper() in reserved:
        cleaned = f"{cleaned}_client"
    return cleaned[:100] if cleaned else "Client_Unnamed"

def shape_arabic(text: str, base_dir: str = None) -> str:
    """
    Smart shaping and bidirectional reordering helper for Arabic & mixed Arabic/Latin text.
    Uses base_dir='L' for mixed text strings to prevent bracket, punctuation, and colon inversion.
    Includes French accented characters (\u00C0-\u024F) in Latin detection.
    """
    if text is None:
        return ""
    text_str = str(text).strip()
    if not text_str:
        return ""

    has_arabic = any(
        '\u0600' <= ch <= '\u06FF' or 
        '\u0750' <= ch <= '\u077F' or 
        '\u08A0' <= ch <= '\u08FF' or
        '\uFB50' <= ch <= '\uFDFF' or
        '\uFE70' <= ch <= '\uFEFF'
        for ch in text_str
    )
    if not has_arabic:
        return text_str

    try:
        reshaped = arabic_reshaper.reshape(text_str)
        has_latin = any(
            ('A' <= ch <= 'Z' or 'a' <= ch <= 'z' or '\u00C0' <= ch <= '\u024F')
            for ch in text_str
        )
        if base_dir:
            return get_display(reshaped, base_dir=base_dir)
        elif has_latin:
            return get_display(reshaped, base_dir='L')
        return get_display(reshaped)
    except Exception:
        return text_str

def calculate_pv_page_splits(n_cams: int) -> list[int]:
    """
    Computes camera item distribution per page for PV de pose:
    - n_cams <= 25: exactly 1 page (fits table + execution footer block).
    - 26 <= n_cams <= 50: 2 pages with balanced split (no page < 5 cameras).
    - n_cams > 50: multi-page (Page 1 up to 25, continuation pages up to 30, final page >= 5 + footer).
    Guarantees no orphan pages with < 5 items.
    """
    if n_cams <= 25:
        return [n_cams]
    if n_cams <= 50:
        p1 = math.ceil(n_cams / 2)
        return [p1, n_cams - p1]

    pages = []
    p1 = 25
    pages.append(p1)
    rem = n_cams - p1
    while rem > 0:
        if rem <= 28:
            if rem < 5 and len(pages) > 0:
                borrow = 5 - rem
                pages[-1] -= borrow
                rem += borrow
            pages.append(rem)
            break
        else:
            chunk = 30
            if rem - chunk < 5:
                chunk = rem - 5
            pages.append(chunk)
            rem -= chunk
    return pages

class DossierResult(tuple):
    """
    Hybrid return container for generate_client_dossier:
    Acts as a 3-element tuple (folder, annex1, annex5) for legacy callers,
    while offering complete dictionary / mapping access for modern multi-dossier consumers.
    """
    def __new__(cls, folder, annex1, annex5, pv_reception=None, files=None):
        return super().__new__(cls, (folder, annex1, annex5))

    def __init__(self, folder, annex1, annex5, pv_reception=None, files=None):
        self._dict = {
            "success": True,
            "folder": folder,
            "folder_path": folder,
            "annex1": annex1,
            "annex5": annex5,
            "pv_reception": pv_reception or os.path.join(folder, "pv_reception.pdf"),
            "files": files or ["annex1.pdf", "annex5.pdf", "pv_reception.pdf"]
        }

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in self._dict:
                return self._dict[key]
            raise KeyError(key)
        return super().__getitem__(key)

    def __contains__(self, key):
        if isinstance(key, str):
            return key in self._dict
        return super().__contains__(key)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def to_dict(self):
        return dict(self._dict)

    def __repr__(self):
        return f"<DossierResult {self._dict}>"

class PDFGenerator:
    def __init__(self, templates_dir="templates_pdf"):
        self.templates_dir = resource_path(templates_dir)
        self.annex1_template = os.path.join(self.templates_dir, "annex1_template.pdf")
        self.annex5_template = os.path.join(self.templates_dir, "annex5_template.pdf")
        self.annex3_template = os.path.join(self.templates_dir, "annex3_extended_template.pdf")
        self.annex8_template = os.path.join(self.templates_dir, "annex8_internet_commitment_template.pdf")
        
        # Locate system Arabic TrueType font
        possible_fonts = [
            r"C:\Windows\Fonts\times.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahoma.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
        ]
        self.font_path = None
        for p in possible_fonts:
            if os.path.exists(p):
                self.font_path = p
                break
        if not self.font_path:
            self.font_path = "helv"
        
        try:
            self.font = fitz.Font(fontfile=self.font_path) if os.path.exists(self.font_path) else None
        except Exception:
            self.font = None

    def shape_arabic(self, text: str, base_dir: str = None) -> str:
        """Instance method shortcut for shape_arabic."""
        return shape_arabic(text, base_dir=base_dir)

    def _stamp_field(self, page, rect, text, fontname="f0", max_size=10.5, min_size=6.0, 
                     align=fitz.TEXT_ALIGN_RIGHT, whiteout=False):
        """Stamps text into exact rectangle with Arabic reshaping and dynamic font auto-scaling."""
        if text is None:
            return
        text_str = str(text).strip()
        if not text_str:
            return

        reshaped = shape_arabic(text_str)

        if whiteout:
            # Mask the preprinted dots cleanly only if explicitly requested
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        size = max_size
        if self.font:
            while size >= min_size:
                try:
                    w = self.font.text_length(reshaped, fontsize=size)
                    if w <= rect.width - 2:
                        break
                except Exception:
                    break
                size -= 0.5

        # Vertical centering adjustment
        rc = page.insert_textbox(rect, reshaped, fontname=fontname, fontsize=size, align=align)
        while rc < 0 and size > 4.5:
            size -= 0.5
            rc = page.insert_textbox(rect, reshaped, fontname=fontname, fontsize=size, align=align)

    @staticmethod
    def _insert_box_text(page, rect, text, fontname, max_size=8.5, min_size=5.5, color=(0.10, 0.10, 0.10), align=fitz.TEXT_ALIGN_LEFT):
        """Helper to insert text in PV boxes with auto font downsizing to prevent clipping or dropping."""
        if not text:
            return
        size = max_size
        while size >= min_size:
            rc = page.insert_textbox(rect, text, fontname=fontname, fontsize=size, color=color, align=align)
            if rc >= 0:
                return
            size -= 0.5
        page.insert_textbox(rect, text, fontname=fontname, fontsize=min_size, color=color, align=align)

    def _prepare_client_data(self, client):
        data = dict(client) if client else {}
        display_name = data.get("full_name") or data.get("company_name") or ""
        data["display_name"] = display_name
        return data

    def generate_annex1(self, client_data: dict, purchases: list[dict], output_name="annex1.pdf") -> str | bytes:
        """Stamp client info and aggregated equipment quantities onto Page 18 (Annex 1)."""
        if not os.path.exists(self.annex1_template):
            raise FileNotFoundError(f"Template not found: {self.annex1_template}")

        doc = fitz.open(self.annex1_template)
        page = doc[0]
        fontname = "helv"
        if self.font_path and os.path.exists(self.font_path):
            try:
                page.insert_font(fontname="f0", fontfile=self.font_path)
                fontname = "f0"
            except Exception:
                fontname = "helv"

        client = self._prepare_client_data(client_data)
        today = date.today().strftime("%d/%m/%Y")

        # 1. Identity Fields (floating on top of preprinted points)
        self._stamp_field(page, fitz.Rect(38, 194, 442, 210), client.get("display_name", ""), fontname=fontname)
        
        dob = client.get("dob", "")
        pob = client.get("pob", "")
        dob_pob = f"{dob} بـ {pob}".strip(" بـ ") if dob or pob else ""
        self._stamp_field(page, fitz.Rect(38, 218, 465, 234), dob_pob, fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 242, 465, 258), client.get("nationality", "جزائرية"), fontname=fontname)
        
        addr = client.get("address", "")
        city = client.get("city", "")
        full_addr = f"{addr}، {city}".strip("، ") if addr or city else ""
        self._stamp_field(page, fitz.Rect(38, 266, 465, 282), full_addr, fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 290, 475, 306), client.get("profession", ""), fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 314, 438, 330), client.get("activity_type", ""), fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 338, 440, 354), client.get("accreditation_ref", ""), fontname=fontname)

        # 2. Group Equipment by (model_name, designation, nature, category, sub_category)
        purchases_list = list(purchases) if purchases else []
        grouped = {}
        for c in purchases_list:
            k = (
                c.get("equipment_designation") or "كاميرا مراقبة",
                c.get("equipment_nature") or c.get("model_name") or "",
                c.get("model_name") or "",
                c.get("category") or "",
                c.get("sub_category") or ""
            )
            grouped[k] = grouped.get(k, 0) + 1

        y_start = 441.0
        row_height = 20.0
        for i, (k, qty) in enumerate(grouped.items()):
            if i >= 3:
                break
            y = y_start + (i * row_height)
            desig = k[0]
            nature = f"{k[1]} ({k[2]})" if k[2] and k[2] != k[1] else k[1]
            cat = k[3]
            sub_cat = k[4]

            # Columns precisely mapped to template borders:
            # Col 1: تعيين التجهيزات (442 - 530)
            self._stamp_field(page, fitz.Rect(442, y, 530, y + row_height - 2), desig, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.0, min_size=6.0)
            # Col 2: طبيعة التجهيزات (312 - 439)
            self._stamp_field(page, fitz.Rect(312, y, 439, y + row_height - 2), nature, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.5, min_size=6.0)
            # Col 3: القسم (212 - 309)
            self._stamp_field(page, fitz.Rect(212, y, 309, y + row_height - 2), cat, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=7.0)
            # Col 4: القسم الفرعي (120 - 209)
            self._stamp_field(page, fitz.Rect(120, y, 209, y + row_height - 2), sub_cat, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=7.0)
            # Col 5: الكمية (35 - 117)
            self._stamp_field(page, fitz.Rect(35, y, 117, y + row_height - 2), str(qty), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=8.0)

        # 3. Date & City (City after حرر بـ, Date after في)
        sig_city = client.get("city") or "الجزائر"
        self._stamp_field(page, fitz.Rect(130, 506, 158, 522), sig_city, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
        self._stamp_field(page, fitz.Rect(57, 506, 112, 522), today, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)

        # 4. Logistics Lines (floating on top of points)
        self._stamp_field(page, fitz.Rect(38, 557, 430, 573), client.get("origin_country", "الصين"), fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 576, 428, 592), client.get("import_country", "الجزائر"), fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 595, 415, 611), client.get("transport_method", "بري / جوي"), fontname=fontname)
        
        storage = client.get("storage_location") or client.get("company_hq") or full_addr
        self._stamp_field(page, fitz.Rect(38, 614, 333, 630), storage, fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 633, 375, 649), client.get("security_conditions", "حراسة ونظام إنذار ومراقبة 24/24"), fontname=fontname)

        if output_name is None:
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            return pdf_bytes

        out_path = os.path.abspath(output_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        doc.save(out_path, deflate=True, garbage=4)
        doc.close()
        return out_path

    def generate_annex5(self, client_data: dict, purchases: list[dict] = None, output_name="annex5.pdf") -> str | bytes:
        """Stamp detailed civil and corporate identity onto Page 21 (Annex 5)."""
        if not os.path.exists(self.annex5_template):
            raise FileNotFoundError(f"Template not found: {self.annex5_template}")

        doc = fitz.open(self.annex5_template)
        page = doc[0]
        fontname = "helv"
        if self.font_path and os.path.exists(self.font_path):
            try:
                page.insert_font(fontname="f0", fontfile=self.font_path)
                fontname = "f0"
            except Exception:
                fontname = "helv"

        client = self._prepare_client_data(client_data)
        today = date.today().strftime("%d/%m/%Y")

        # Identity (floating on top of preprinted points)
        self._stamp_field(page, fitz.Rect(38, 252, 430, 268), client.get("display_name", ""), fontname=fontname)
        self._stamp_field(page, fitz.Rect(318, 274, 485, 290), client.get("father_name", ""), fontname=fontname)
        self._stamp_field(page, fitz.Rect(38, 274, 300, 290), client.get("mother_name", ""), fontname=fontname)
        
        dob = client.get("dob", "")
        pob = client.get("pob", "")
        dob_pob = f"{dob} بـ {pob}".strip(" بـ ") if dob or pob else ""
        self._stamp_field(page, fitz.Rect(38, 296, 445, 312), dob_pob, fontname=fontname)

        addr = client.get("address", "")
        city = client.get("city", "")
        full_addr = f"{addr}، {city}".strip("، ") if addr or city else ""
        self._stamp_field(page, fitz.Rect(38, 318, 450, 334), full_addr, fontname=fontname)

        # ID Document (exact calibrated dots)
        self._stamp_field(page, fitz.Rect(307, 340, 382, 356), client.get("doc_number", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(175, 340, 252, 356), client.get("doc_issuer", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=6.0)
        self._stamp_field(page, fitz.Rect(39, 340, 138, 356), client.get("doc_issue_date", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=6.0)

        # Passport
        self._stamp_field(page, fitz.Rect(308, 362, 443, 378), client.get("passport_number", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(38, 362, 250, 378), client.get("passport_issuer", ""), fontname=fontname, align=fitz.TEXT_ALIGN_RIGHT, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(310, 384, 445, 400), client.get("passport_issue_date", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(38, 384, 188, 400), client.get("passport_expiry_date", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=6.0)

        # Nationality
        self._stamp_field(page, fitz.Rect(38, 406, 465, 422), client.get("nationality", "جزائرية"), fontname=fontname)

        # Corporate
        self._stamp_field(page, fitz.Rect(309, 428, 398, 444), client.get("company_name", ""), fontname=fontname, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(40, 428, 264, 444), client.get("company_hq", ""), fontname=fontname, max_size=10.0, min_size=6.0)

        # Contact
        self._stamp_field(page, fitz.Rect(341, 450, 467, 466), client.get("phone", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(207, 450, 303, 466), client.get("fax", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=6.0)
        self._stamp_field(page, fitz.Rect(36, 450, 141, 466), client.get("email", ""), fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.5, min_size=6.0)

        # Shareholders
        self._stamp_field(page, fitz.Rect(38, 472, 412, 488), client.get("shareholders", ""), fontname=fontname, max_size=10.0, min_size=6.0)

        # Signature city & date (Date after حرر في, City after بـ)
        sig_city = client.get("city") or "الجزائر"
        self._stamp_field(page, fitz.Rect(135, 599, 185, 615), today, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=7.0)
        self._stamp_field(page, fitz.Rect(58, 599, 133, 615), sig_city, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=10.0, min_size=7.0)

        if output_name is None:
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            return pdf_bytes

        out_path = os.path.abspath(output_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        doc.save(out_path, deflate=True, garbage=4)
        doc.close()
        return out_path

    def generate_annex3(self, client_data: dict, purchases: list[dict] = None, output_name="annex3.pdf") -> str | bytes:
        """
        Stamp client info and individual serialized equipment onto the extended Annex 3 template.
        Supports up to 15 camera rows with:
        - Equipment designation (تعيين التجهيزات)
        - Nature & Model (طبيعة التجهيزات)
        - Quantity (الكمية)
        - Serial number / registration (الرقم التسلسلي)
        - Origin country (منشأ التجهيزات)
        - Usage purpose (الغرض من استعمال التجهيزات - شخصي أو مهني)
        - Installation location (مكان الاستعمال)
        """
        if not os.path.exists(self.annex3_template):
            raise FileNotFoundError(f"Template not found: {self.annex3_template}")

        doc = fitz.open(self.annex3_template)
        page = doc[0]
        fontname = "helv"
        if self.font_path and os.path.exists(self.font_path):
            try:
                page.insert_font(fontname="f0", fontfile=self.font_path)
                fontname = "f0"
            except Exception:
                fontname = "helv"

        client = self._prepare_client_data(client_data)
        today = date.today().strftime("%d/%m/%Y")

        # 1. Identity Fields (floating on top of points)
        self._stamp_field(page, fitz.Rect(38, 154, 405, 170), client.get("display_name", ""), fontname=fontname)
        
        addr = client.get("address", "")
        city = client.get("city", "")
        full_addr = f"{addr}، {city}".strip("، ") if addr or city else ""
        self._stamp_field(page, fitz.Rect(38, 176, 420, 192), full_addr, fontname=fontname)
        
        prof = client.get("profession") or client.get("activity_type") or ""
        self._stamp_field(page, fitz.Rect(38, 198, 365, 214), prof, fontname=fontname)

        # 2. Equipment Rows on Extended Table (up to 15 rows)
        purchases_list = list(purchases) if purchases else []
        y_start = 321.61
        row_height = 20.0

        for i, cam in enumerate(purchases_list):
            if i >= 15:
                break
            y = y_start + (i * row_height)
            
            desig = cam.get("equipment_designation") or "كاميرا مراقبة"
            model_part = cam.get("model_name", "") or ""
            nature_part = cam.get("equipment_nature", "") or ""
            nature = f"{model_part} ({nature_part})".strip(" ()") if nature_part else model_part
            qty = "1"
            sn = cam.get("serial_number", "") or ""
            origin = cam.get("origin_country") or client.get("origin_country") or "الصين"
            purpose = client.get("usage_purpose") or "مهني"
            site_addr = client.get("address") or full_addr or "مقر النشاط"

            # Col 0 (472.63 - 530.0): تعيين التجهيزات
            self._stamp_field(page, fitz.Rect(473, y + 1, 529, y + 19), desig, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.0, min_size=5.5, whiteout=False)
            # Col 1 (384.47 - 472.63): طبيعة التجهيزات
            self._stamp_field(page, fitz.Rect(385, y + 1, 472, y + 19), nature, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.0, min_size=5.0, whiteout=False)
            # Col 2 (327.50 - 384.47): كمية التجهيزات
            self._stamp_field(page, fitz.Rect(328, y + 1, 384, y + 19), qty, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=7.0, whiteout=False)
            # Col 3 (247.56 - 327.50): الرقم التسلسلي
            self._stamp_field(page, fitz.Rect(248, y + 1, 327, y + 19), sn, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.5, min_size=5.5, whiteout=False)
            # Col 4 (188.60 - 247.56): منشأ التجهيزات
            self._stamp_field(page, fitz.Rect(189, y + 1, 247, y + 19), origin, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.0, min_size=6.0, whiteout=False)
            # Col 5 (93.64 - 188.60): الغرض من استعمال التجهيزات
            self._stamp_field(page, fitz.Rect(94, y + 1, 188, y + 19), purpose, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.0, min_size=6.0, whiteout=False)
            # Col 6 (29.0 - 93.64): مكان الاستعمال
            self._stamp_field(page, fitz.Rect(30, y + 1, 93, y + 19), site_addr, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=8.0, min_size=5.5, whiteout=False)

        # 3. Date & City (City after حرر بـ, Date after في)
        sig_city = client.get("city") or "الجزائر"
        self._stamp_field(page, fitz.Rect(160, 640, 188, 654), sig_city, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=6.0, whiteout=False)
        self._stamp_field(page, fitz.Rect(98, 640, 148, 654), today, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER, max_size=9.5, min_size=6.0, whiteout=False)

        if output_name is None:
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            return pdf_bytes

        out_path = os.path.abspath(output_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        doc.save(out_path, deflate=True, garbage=4)
        doc.close()
        return out_path

    def generate_annex8(self, client_data: dict, purchases: list[dict] = None, output_name="annex8.pdf") -> str | bytes:
        """
        Stamp client identity and installation site location onto Annex 8:
        Official Internet Non-Connection Commitment Form (Décret exécutif n° 16-61, Page 14).
        """
        if not os.path.exists(self.annex8_template):
            raise FileNotFoundError(f"Template not found: {self.annex8_template}")

        doc = fitz.open(self.annex8_template)
        page = doc[0]
        fontname = "helv"
        if self.font_path and os.path.exists(self.font_path):
            try:
                page.insert_font(fontname="f0", fontfile=self.font_path)
                fontname = "f0"
            except Exception:
                fontname = "helv"

        client = self._prepare_client_data(client_data)
        today = date.today().strftime("%d/%m/%Y")

        # 1. Signatory Name (أنا الممضي أسفله السيد (ة) - floating on top of points)
        c_name = client.get("display_name", "")
        self._stamp_field(page, fitz.Rect(35, 306, 380, 322), c_name, fontname=fontname, align=fitz.TEXT_ALIGN_RIGHT)

        # 2. Installation Location (عنوان مكان استغلال نظام كاميرات المراقبة)
        addr = client.get("address", "")
        city = client.get("city", "")
        full_addr = f"{addr}، {city}".strip("، ") if addr or city else ""
        site_loc = client.get("storage_location") or client.get("company_hq") or full_addr
        self._stamp_field(page, fitz.Rect(35, 328, 310, 344), site_loc, fontname=fontname, align=fitz.TEXT_ALIGN_RIGHT)

        # 3. Date & City (City after حرر بـ, Date after في)
        sig_city = client.get("city") or "الجزائر"
        self._stamp_field(page, fitz.Rect(116, 461, 153, 477), sig_city, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
        self._stamp_field(page, fitz.Rect(31, 461, 95, 477), today, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)

        if output_name is None:
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            return pdf_bytes

        out_path = os.path.abspath(output_name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        doc.save(out_path, deflate=True, garbage=4)
        doc.close()
        return out_path

    def generate_pv_pose(
        self,
        client: dict,
        cameras: list[dict] = None,
        output_path: str = None,
        output_name: str = None,
        return_bytes: bool = False
    ) -> str | bytes:
        """
        Pure PyMuPDF vector generation of Procès-Verbal de Réception & de Livraison (PV de Pose).
        - Algerian regulatory compliance: Décret exécutif n° 09-410 & Arrêté 23 août 2017 (J.O. n° 54).
        - 2-column Client & Installation Logistics Card.
        - 5-column Itemized Serial Number Table.
        - Deterministic anti-orphan pagination (<= 25 cameras: single-page; 26+ cameras: balanced multi-page).
        - Attestation of technical conformity and bilateral signature/stamp blocks.
        - Compression: deflate=True, garbage=4 (< 850 KB).
        """
        target_path = output_path or output_name
        cameras_list = list(cameras) if cameras else []
        client_data = self._prepare_client_data(client)

        doc = fitz.open()

        page_splits = calculate_pv_page_splits(len(cameras_list))
        total_pages = len(page_splits)

        cid = client_data.get("id") or 1
        try:
            cid_int = int(cid)
        except Exception:
            cid_int = 1
        today_str = date.today().strftime("%d/%m/%Y")
        pv_ref = f"PV-{cid_int:04d}-{date.today().strftime('%Y%m%d')}"

        col_x = [35.0, 60.0, 190.0, 310.0, 440.0, 560.0]
        headers = [
            "N°",
            "Désignation (التعيين)",
            "Modèle / Nature (النموذج)",
            "Section (القسم)",
            "N° Série / Barcode (الرقم التسلسلي)"
        ]

        cam_cursor = 0

        for page_idx, count_on_page in enumerate(page_splits):
            p = doc.new_page(width=595.0, height=842.0)
            fname = "helv"
            if self.font_path and os.path.exists(self.font_path):
                try:
                    p.insert_font(fontname="f0", fontfile=self.font_path)
                    fname = "f0"
                except Exception:
                    fname = "helv"

            # 1. Outer Double Border
            p.draw_rect(fitz.Rect(30.0, 30.0, 565.0, 812.0), color=(0.18, 0.28, 0.48), width=1.2)
            p.draw_rect(fitz.Rect(32.0, 32.0, 563.0, 810.0), color=(0.75, 0.80, 0.88), width=0.5)

            if page_idx == 0:
                # Full Primary Header
                p.draw_rect(fitz.Rect(33.0, 33.0, 562.0, 90.0), color=None, fill=(0.94, 0.96, 0.99))
                p.insert_textbox(fitz.Rect(40.0, 38.0, 555.0, 58.0), "PROCÈS-VERBAL DE RÉCEPTION & DE LIVRAISON",
                                 fontname=fname, fontsize=11.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.12, 0.22, 0.42))
                p.insert_textbox(fitz.Rect(40.0, 56.0, 555.0, 74.0), shape_arabic("محضر استلام وتسليم وتثبيت معدات المراقبة بالكاميرات"),
                                 fontname=fname, fontsize=11.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.12, 0.22, 0.42))
                p.insert_textbox(fitz.Rect(40.0, 74.0, 555.0, 88.0), f"Réf: {pv_ref}  |  Date: {today_str}",
                                 fontname=fname, fontsize=8.5, align=fitz.TEXT_ALIGN_CENTER, color=(0.35, 0.40, 0.48))

                # Legal Citations Box
                legal_text = "Établi en application du Décret exécutif n° 09-410 et de l'Arrêté interministériel du 23 août 2017 (J.O. n° 54) régissant les équipements sensibles de vidéosurveillance."
                p.draw_rect(fitz.Rect(33.0, 94.0, 562.0, 114.0), color=None, fill=(0.98, 0.98, 0.99))
                p.insert_textbox(fitz.Rect(36.0, 96.0, 559.0, 112.0), legal_text,
                                 fontname=fname, fontsize=7.2, align=fitz.TEXT_ALIGN_CENTER, color=(0.30, 0.35, 0.40))

                # Client & Site Info Box (2 Columns)
                y_info = 118.0
                h_info = 76.0
                p.draw_rect(fitz.Rect(35.0, y_info, 560.0, y_info + h_info), color=(0.78, 0.82, 0.88), width=0.8, fill=(0.97, 0.98, 1.0))
                p.draw_line(fitz.Point(297.0, y_info), fitz.Point(297.0, y_info + h_info), color=(0.78, 0.82, 0.88), width=0.8)

                # Left: Beneficiary / Client
                c_name = client_data.get("company_name") or client_data.get("full_name") or client_data.get("display_name") or "Non spécifié"
                doc_num = client_data.get("doc_number", "") or ""
                doc_iss = client_data.get("doc_issuer", "") or ""
                doc_id = f"{doc_num} ({doc_iss})".strip(" ()") if doc_num or doc_iss else "Non renseigné"
                phone = client_data.get("phone", "") or "Non renseigné"

                p.insert_textbox(fitz.Rect(40.0, y_info + 4.0, 292.0, y_info + 18.0),
                                 shape_arabic("BÉNÉFICIAIRE / CLIENT (الزبون المستفيد):", base_dir='L'),
                                 fontname=fname, fontsize=8.0, color=(0.15, 0.25, 0.45))
                self._insert_box_text(p, fitz.Rect(40.0, y_info + 20.0, 292.0, y_info + 35.0),
                                      shape_arabic(f"Nom/Entreprise: {c_name}", base_dir='L'), fname, max_size=8.5)
                self._insert_box_text(p, fitz.Rect(40.0, y_info + 36.0, 292.0, y_info + 51.0),
                                      shape_arabic(f"Pièce ID / RC: {doc_id}", base_dir='L'), fname, max_size=8.0)
                self._insert_box_text(p, fitz.Rect(40.0, y_info + 52.0, 292.0, y_info + 68.0),
                                      shape_arabic(f"Téléphone / Contact: {phone}", base_dir='L'), fname, max_size=8.0)

                # Right: Installation Site
                addr = client_data.get("address", "") or ""
                city = client_data.get("city", "") or ""
                site_addr = f"{addr}، {city}".strip("، ") if addr or city else "Non renseigné"
                storage = client_data.get("storage_location") or client_data.get("company_hq") or site_addr
                acc_ref = client_data.get("accreditation_ref") or "Non renseigné"

                p.insert_textbox(fitz.Rect(302.0, y_info + 4.0, 555.0, y_info + 18.0),
                                 shape_arabic("SITE D'INSTALLATION (موقع التثبيت):", base_dir='L'),
                                 fontname=fname, fontsize=8.0, color=(0.15, 0.25, 0.45))
                self._insert_box_text(p, fitz.Rect(302.0, y_info + 20.0, 555.0, y_info + 35.0),
                                      shape_arabic(f"Adresse Site: {site_addr}", base_dir='L'), fname, max_size=8.5)
                self._insert_box_text(p, fitz.Rect(302.0, y_info + 36.0, 555.0, y_info + 51.0),
                                      shape_arabic(f"Lieu de Stockage: {storage}", base_dir='L'), fname, max_size=8.0)
                self._insert_box_text(p, fitz.Rect(302.0, y_info + 52.0, 555.0, y_info + 68.0),
                                      shape_arabic(f"Réf. Autorisation: {acc_ref}", base_dir='L'), fname, max_size=8.0)

                y_tbl_start = 202.0
            else:
                # Compact Continuation Header
                p.draw_rect(fitz.Rect(33.0, 33.0, 562.0, 70.0), color=None, fill=(0.94, 0.96, 0.99))
                p.insert_textbox(fitz.Rect(40.0, 38.0, 555.0, 54.0), "PROCÈS-VERBAL DE RÉCEPTION & DE LIVRAISON (SUITE)",
                                 fontname=fname, fontsize=10.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.12, 0.22, 0.42))
                p.insert_textbox(fitz.Rect(40.0, 53.0, 555.0, 67.0), f"Réf: {pv_ref}  |  Page {page_idx + 1} / {total_pages}",
                                 fontname=fname, fontsize=8.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.35, 0.40, 0.48))
                y_tbl_start = 76.0

            # Table Column Headers
            p.draw_rect(fitz.Rect(35.0, y_tbl_start, 560.0, y_tbl_start + 20.0), color=(0.18, 0.28, 0.48), fill=(0.18, 0.28, 0.48))
            for idx_h, h_text in enumerate(headers):
                p.insert_textbox(fitz.Rect(col_x[idx_h], y_tbl_start + 3.0, col_x[idx_h + 1], y_tbl_start + 18.0),
                                 shape_arabic(h_text), fontname=fname, fontsize=7.5,
                                 align=fitz.TEXT_ALIGN_CENTER, color=(1.0, 1.0, 1.0))

            # Table Rows for this page
            curr_y = y_tbl_start + 20.0
            row_h = 17.0

            batch_cams = cameras_list[cam_cursor : cam_cursor + count_on_page]
            for sub_i, cam in enumerate(batch_cams):
                global_idx = cam_cursor + sub_i
                bg = (0.98, 0.98, 0.99) if global_idx % 2 == 0 else (1.0, 1.0, 1.0)
                p.draw_rect(fitz.Rect(35.0, curr_y, 560.0, curr_y + row_h), color=(0.82, 0.85, 0.90), fill=bg, width=0.5)

                c_desig = cam.get("equipment_designation") or "كاميرا مراقبة"
                model_part = cam.get("model_name", "") or ""
                nature_part = cam.get("equipment_nature", "") or ""
                c_mod = f"{model_part} ({nature_part})".strip(" ()") if nature_part else model_part
                c_sec = f"{cam.get('category', '') or ''} / {cam.get('sub_category', '') or ''}".strip(" /")
                c_sn = cam.get("serial_number", "") or ""

                p.insert_textbox(fitz.Rect(col_x[0], curr_y + 2.0, col_x[1], curr_y + row_h),
                                 str(global_idx + 1), fontname=fname, fontsize=8.0, align=fitz.TEXT_ALIGN_CENTER)
                p.insert_textbox(fitz.Rect(col_x[1] + 2.0, curr_y + 2.0, col_x[2] - 2.0, curr_y + row_h),
                                 shape_arabic(c_desig), fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_CENTER)
                p.insert_textbox(fitz.Rect(col_x[2] + 2.0, curr_y + 2.0, col_x[3] - 2.0, curr_y + row_h),
                                 shape_arabic(c_mod, base_dir='L'), fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_CENTER)
                p.insert_textbox(fitz.Rect(col_x[3] + 2.0, curr_y + 2.0, col_x[4] - 2.0, curr_y + row_h),
                                 shape_arabic(c_sec), fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_CENTER)
                p.insert_textbox(fitz.Rect(col_x[4] + 2.0, curr_y + 2.0, col_x[5] - 2.0, curr_y + row_h),
                                 shape_arabic(c_sn), fontname=fname, fontsize=8.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.10, 0.20, 0.50))

                curr_y += row_h

            cam_cursor += count_on_page

            # Execution Block on the Final Page
            if page_idx == total_pages - 1:
                # 1. Total Count Row
                p.draw_rect(fitz.Rect(35.0, curr_y, 560.0, curr_y + 18.0), color=(0.70, 0.75, 0.85), fill=(0.92, 0.94, 0.98), width=0.8)
                p.insert_textbox(fitz.Rect(40.0, curr_y + 2.0, 350.0, curr_y + 16.0),
                                 f"TOTAL ÉQUIPEMENTS INSTALLÉS : {len(cameras_list)} unité(s)",
                                 fontname=fname, fontsize=8.5, color=(0.15, 0.25, 0.45))
                p.insert_textbox(fitz.Rect(360.0, curr_y + 2.0, 555.0, curr_y + 16.0),
                                 shape_arabic(f"المجموع الكلي للمعدات: {len(cameras_list)} كاميرا"),
                                 fontname=fname, fontsize=8.5, align=fitz.TEXT_ALIGN_RIGHT, color=(0.15, 0.25, 0.45))

                # 2. Technical Conformity Attestation
                y_cert = curr_y + 24.0
                p.draw_rect(fitz.Rect(35.0, y_cert, 560.0, y_cert + 46.0), color=(0.80, 0.85, 0.90), fill=(0.97, 0.98, 1.0), width=0.5)
                cert_fr = "Attestation de Conformité : L'installateur certifie la conformité technique de la pose et du fonctionnement des équipements listés ci-dessus. Le client accuse réception des caméras et reconnaît avoir été informé de ses devoirs réglementaires d'exploitation."
                p.insert_textbox(fitz.Rect(40.0, y_cert + 3.0, 555.0, y_cert + 24.0), cert_fr,
                                 fontname=fname, fontsize=7.2, color=(0.25, 0.30, 0.35))
                cert_ar = "يشهد القائم بالتركيب بمطابقة التثبيت والتشغيل التقني للمعدات المذكورة أعلاه طبقاً للمعايير القانونية السارية. ويقر الزبون باستلام الأجهزة بحالة ممتازة."
                p.insert_textbox(fitz.Rect(40.0, y_cert + 25.0, 555.0, y_cert + 42.0), shape_arabic(cert_ar),
                                 fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_RIGHT, color=(0.25, 0.30, 0.35))

                # 3. Dual Signatures & Stamps
                y_sig = y_cert + 52.0
                sig_h = 80.0

                # Left: Installer
                p.draw_rect(fitz.Rect(35.0, y_sig, 290.0, y_sig + sig_h), color=(0.75, 0.80, 0.88), width=0.8)
                p.insert_textbox(fitz.Rect(40.0, y_sig + 4.0, 285.0, y_sig + 18.0), "L'INSTALLATEUR / PRESTATAIRE AGRÉÉ",
                                 fontname=fname, fontsize=8.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.15, 0.25, 0.45))
                p.insert_textbox(fitz.Rect(40.0, y_sig + 19.0, 285.0, y_sig + 32.0), shape_arabic("القائم بالتركيب والاعتماد"),
                                 fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_CENTER, color=(0.30, 0.30, 0.30))
                p.insert_textbox(fitz.Rect(40.0, y_sig + 60.0, 285.0, y_sig + 74.0), "Cachet et Signature:",
                                 fontname=fname, fontsize=7.5, color=(0.40, 0.40, 0.40))

                # Right: Client
                p.draw_rect(fitz.Rect(305.0, y_sig, 560.0, y_sig + sig_h), color=(0.75, 0.80, 0.88), width=0.8)
                p.insert_textbox(fitz.Rect(310.0, y_sig + 4.0, 555.0, y_sig + 18.0), "LE CLIENT / RÉCEPTIONNAIRE",
                                 fontname=fname, fontsize=8.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.15, 0.25, 0.45))
                p.insert_textbox(fitz.Rect(310.0, y_sig + 19.0, 555.0, y_sig + 32.0), shape_arabic("الزبون المستلم"),
                                 fontname=fname, fontsize=7.5, align=fitz.TEXT_ALIGN_CENTER, color=(0.30, 0.30, 0.30))
                p.insert_textbox(fitz.Rect(310.0, y_sig + 33.0, 555.0, y_sig + 46.0), "(Mention \"Bon pour réception et conformité\")",
                                 fontname=fname, fontsize=7.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.40, 0.40, 0.40))
                p.insert_textbox(fitz.Rect(310.0, y_sig + 60.0, 555.0, y_sig + 74.0), "Date et Signature:",
                                 fontname=fname, fontsize=7.5, color=(0.40, 0.40, 0.40))

            # Page Numbering Footer (all pages)
            p.insert_textbox(fitz.Rect(35.0, 814.0, 560.0, 828.0), f"Page {page_idx + 1} / {total_pages}",
                             fontname=fname, fontsize=7.0, align=fitz.TEXT_ALIGN_CENTER, color=(0.45, 0.50, 0.58))

        if target_path:
            out_path = os.path.abspath(target_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            doc.save(out_path, deflate=True, garbage=4)
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            if return_bytes:
                return pdf_bytes
            return out_path
        else:
            pdf_bytes = doc.tobytes(deflate=True, garbage=4)
            doc.close()
            return pdf_bytes

    @staticmethod
    def generate_document_preview_pixmaps(doc_bytes, dpi: int = 150) -> list[str]:
        """
        Render document pages to high-resolution PNG pixmaps.
        Accepts PDF bytes, bytearray, file path, or fitz.Document.
        Returns a list of Base64 Data URI strings: ['data:image/png;base64,...'].
        """
        if isinstance(doc_bytes, fitz.Document):
            doc = doc_bytes
            should_close = False
        elif isinstance(doc_bytes, (bytes, bytearray)):
            doc = fitz.open(stream=doc_bytes, filetype="pdf")
            should_close = True
        elif isinstance(doc_bytes, (str, os.PathLike)):
            doc = fitz.open(str(doc_bytes))
            should_close = True
        else:
            raise TypeError(f"Unsupported doc_bytes type: {type(doc_bytes)}")

        pages_b64 = []
        try:
            for page in doc:
                pix = page.get_pixmap(dpi=dpi)
                png_bytes = pix.tobytes("png")
                b64_str = base64.b64encode(png_bytes).decode("ascii")
                pages_b64.append(f"data:image/png;base64,{b64_str}")
        finally:
            if should_close:
                doc.close()

        return pages_b64

    def get_document_preview(self, client_data: dict, cameras: list[dict] = None, doc_type: str = "annex1") -> dict:
        """
        Generate in-memory document, render Pixmap PNGs, and return preview payload.
        doc_type: 'annex1', 'annex5', or 'pv_pose' / 'pv_reception'.
        Returns: { 'success': True, 'doc_type': ..., 'title': ..., 'client_name': ..., 'pages': [...], 'pdf_base64': ..., 'page_count': int, 'error': None }
        """
        try:
            cameras_list = list(cameras) if cameras else []
            dtype = str(doc_type).lower().strip()
            
            if "1" in dtype or "annex1" in dtype or "annexe1" in dtype:
                title = "Annexe 1 - Déclaration d'Équipements"
                doc_bytes = self.generate_annex1(client_data, cameras_list, output_name=None)
            elif "3" in dtype or "annex3" in dtype or "annexe3" in dtype:
                title = "Annexe 3 - Demande d'Autorisation d'Exploitation (Tableau Étendu)"
                doc_bytes = self.generate_annex3(client_data, cameras_list, output_name=None)
            elif "5" in dtype or "annex5" in dtype or "annexe5" in dtype:
                title = "Annexe 5 - Fiche de Renseignements"
                doc_bytes = self.generate_annex5(client_data, cameras_list, output_name=None)
            elif "8" in dtype or "annex8" in dtype or "annexe8" in dtype:
                title = "Annexe 8 - Engagement de Non-Connexion à Internet"
                doc_bytes = self.generate_annex8(client_data, cameras_list, output_name=None)
            elif "pv" in dtype or "pose" in dtype or "reception" in dtype:
                title = "Procès-Verbal de Réception / Bordereau de Livraison"
                doc_bytes = self.generate_pv_pose(client_data, cameras_list, output_path=None)
            else:
                return {
                    "success": False,
                    "doc_type": doc_type,
                    "title": "",
                    "client_name": "",
                    "page_count": 0,
                    "pages": [],
                    "pdf_base64": "",
                    "error": f"Unknown document type: '{doc_type}'. Expected 'annex1', 'annex3', 'annex5', 'annex8', or 'pv_pose'."
                }

            pages = self.generate_document_preview_pixmaps(doc_bytes, dpi=150)
            pdf_b64 = base64.b64encode(doc_bytes).decode("ascii")
            
            client = self._prepare_client_data(client_data)
            display_name = client.get("display_name", "")

            return {
                "success": True,
                "doc_type": doc_type,
                "title": title,
                "client_name": display_name,
                "page_count": len(pages),
                "pages": pages,
                "pdf_base64": pdf_b64,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "doc_type": doc_type,
                "title": "",
                "client_name": "",
                "page_count": 0,
                "pages": [],
                "pdf_base64": "",
                "error": str(e)
            }

    # Contract alias for test suite compatibility
    get_document_preview_data = get_document_preview

    def generate_client_dossier(
        self,
        client_data: dict,
        purchases: list[dict] = None,
        base_dir: str = "dossiers",
        parent_folder: str = None,
        dossier_type: str = "1er dossier",
        **kwargs
    ) -> DossierResult:
        """
        Generate all three regulatory documents into the modular client dossier folder:
        - annex1.pdf: Equipment declaration (Official Gazette #54 Page 18)
        - annex5.pdf: Security clearance questionnaire (Official Gazette #54 Page 21)
        - pv_reception.pdf: Delivery & installation receipt with exact camera serials
        Outputs to: <selected_root>/<Client_Name>/1er dossier/
        Initializes empty extensible slot: <selected_root>/<Client_Name>/2eme dossier/
        """
        purchases_list = list(purchases) if purchases else []
        client = self._prepare_client_data(client_data)
        client_name = client.get("full_name") or client.get("company_name") or f"Client_{client.get('id', 'new')}"
        sanitized_name = sanitize_dossier_name(client_name)

        # Support both base_dir and parent_folder
        root_dir = parent_folder if parent_folder is not None else base_dir
        client_dir = os.path.join(root_dir, sanitized_name, dossier_type)
        os.makedirs(client_dir, exist_ok=True)

        # Initialize extensible slot 2eme dossier
        slot_2eme = os.path.join(root_dir, sanitized_name, "2eme dossier")
        os.makedirs(slot_2eme, exist_ok=True)

        p1 = os.path.join(client_dir, "annex1.pdf")
        p5 = os.path.join(client_dir, "annex5.pdf")
        p_pv = os.path.join(client_dir, "pv_reception.pdf")

        self.generate_annex1(client, purchases_list, output_name=p1)
        self.generate_annex5(client, purchases_list, output_name=p5)
        self.generate_pv_pose(client, purchases_list, output_path=p_pv)

        return DossierResult(client_dir, p1, p5, pv_reception=p_pv)

    def generate_second_dossier(
        self,
        client_data: dict,
        purchases: list[dict] = None,
        base_dir: str = "dossiers",
        parent_folder: str = None,
        **kwargs
    ) -> dict:
        """
        Generate 2ème Dossier (Exploitation phase) documents into <root>/<Client_Name>/2eme dossier/:
        - annex3.pdf: Extended Table sensitive equipment exploitation license request (Official Gazette #63)
        - annex8.pdf: Official internet non-connection commitment (Décret exécutif n° 16-61)
        - pv_reception.pdf: Technical delivery and installation receipt (PV de pose)
        """
        purchases_list = list(purchases) if purchases else []
        client = self._prepare_client_data(client_data)
        client_name = client.get("full_name") or client.get("company_name") or f"Client_{client.get('id', 'new')}"
        sanitized_name = sanitize_dossier_name(client_name)

        root_dir = parent_folder if parent_folder is not None else base_dir
        client_dir = os.path.join(root_dir, sanitized_name, "2eme dossier")
        os.makedirs(client_dir, exist_ok=True)

        p3 = os.path.join(client_dir, "annex3.pdf")
        p8 = os.path.join(client_dir, "annex8.pdf")
        p_pv = os.path.join(client_dir, "pv_reception.pdf")

        self.generate_annex3(client, purchases_list, output_name=p3)
        self.generate_annex8(client, purchases_list, output_name=p8)
        self.generate_pv_pose(client, purchases_list, output_path=p_pv)

        return {
            "success": True,
            "dossier_type": "2eme_dossier",
            "folder": client_dir,
            "folder_path": client_dir,
            "annex3": p3,
            "annex8": p8,
            "pv_reception": p_pv,
            "files": ["annex3.pdf", "annex8.pdf", "pv_reception.pdf"],
            "client_name": client.get("full_name") or client.get("company_name")
        }

# Module-level convenience functions
generate_document_preview_pixmaps = PDFGenerator.generate_document_preview_pixmaps

def generate_pv_pose(client: dict, cameras: list[dict] = None, output_path: str = None, **kwargs):
    """Module-level generator for PV de pose."""
    gen = PDFGenerator()
    return gen.generate_pv_pose(client, cameras, output_path=output_path, **kwargs)
