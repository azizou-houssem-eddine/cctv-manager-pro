import sqlite3
import os
import csv
import io
import re
import shutil
import threading
import functools

def synchronized(method):
    """
    Ensure thread-safe execution across worker threads using the instance's reentrant lock.
    If an unhandled exception escapes and a transaction remains active, performs a safety rollback.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            try:
                return method(self, *args, **kwargs)
            except Exception:
                if getattr(self, "conn", None) is not None:
                    try:
                        if self.conn.in_transaction:
                            self.conn.rollback()
                    except Exception:
                        pass
                raise
    return wrapper

def _sanitize_excel_value(val):
    """
    Sanitize text values for Excel (.xlsx) and CSV export:
    - Strips ASCII control characters (\x00-\x08, \x0b-\x0c, \x0e-\x1f) that cause openpyxl IllegalCharacterError.
    - Defuses formula injection (CWE-1236) by prepending a single quote if string begins with '=', '+', '-', or '@'.
    - Preserves numeric integers/floats, Arabic Unicode, French diacritics, and valid whitespace (\t, \n, \r).
    """
    if val is None:
        return ""
    if isinstance(val, (int, float)):
        return val
    # 1. Strip illegal control characters
    s = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', str(val))
    # 2. Defuse formula injection triggers
    if s and s[0] in ('=', '+', '-', '@'):
        s = "'" + s
    return s

def _normalize_text_input(raw_input) -> str:
    """Normalize plain text, bytes, or base64 data URIs into decoded string."""
    if isinstance(raw_input, bytes):
        for enc in ("utf-8-sig", "utf-8", "cp1256", "latin1"):
            try:
                return raw_input.decode(enc)
            except UnicodeDecodeError:
                continue
        return raw_input.decode("latin1", errors="replace")

    s = str(raw_input)
    if s.startswith("data:") and ";base64," in s:
        import base64
        b64_data = s.split(";base64,", 1)[1]
        try:
            raw_bytes = base64.b64decode(b64_data)
            return _normalize_text_input(raw_bytes)
        except Exception:
            pass
    return s

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

def get_client_dossier_dir(client_name: str, dossier_type: str = "1er dossier", base_dir: str = "dossiers") -> str:
    """
    Return modular client dossier directory path (e.g. dossiers/<Sanitized>/1er dossier/).
    Creates the directory if it does not already exist, and initializes the 2eme dossier slot.
    """
    sanitized = sanitize_dossier_name(client_name)
    target_dir = os.path.join(base_dir, sanitized, dossier_type)
    os.makedirs(target_dir, exist_ok=True)
    slot_2eme = os.path.join(base_dir, sanitized, "2eme dossier")
    os.makedirs(slot_2eme, exist_ok=True)
    return target_dir

def migrate_legacy_dossiers(legacy_dir: str = "1er dossier", target_root: str = "dossiers") -> int:
    """
    Migrate legacy client folders from '1er dossier/<Client>/' into 'dossiers/<Client>/1er_dossier/'.
    Non-destructively copies files without overwriting existing files in destination.
    Also initializes '2eme_dossier' extensible slot.
    Returns the count of migrated files.
    """
    if not os.path.exists(legacy_dir) or not os.path.isdir(legacy_dir):
        return 0

    migrated_count = 0
    try:
        entries = os.listdir(legacy_dir)
    except OSError:
        return 0

    for entry in entries:
        src_client_path = os.path.join(legacy_dir, entry)
        if not os.path.isdir(src_client_path):
            continue

        sanitized_name = sanitize_dossier_name(entry)
        dst_1er_dir = os.path.join(target_root, sanitized_name, "1er_dossier")
        dst_2eme_dir = os.path.join(target_root, sanitized_name, "2eme_dossier")
        
        os.makedirs(dst_1er_dir, exist_ok=True)
        os.makedirs(dst_2eme_dir, exist_ok=True)

        for filename in os.listdir(src_client_path):
            src_file = os.path.join(src_client_path, filename)
            if os.path.isfile(src_file):
                dst_file = os.path.join(dst_1er_dir, filename)
                if not os.path.exists(dst_file):
                    shutil.copy2(src_file, dst_file)
                    migrated_count += 1

    return migrated_count

class DatabaseManager:
    """Manages all database operations for the CCTV Manager application."""

    def __init__(self, db_path: str = "cctv_manager.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA busy_timeout = 5000;")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

    # ------------------------------------------------------------------ #
    #  Schema & Migrations
    # ------------------------------------------------------------------ #
    @synchronized
    def initialize_db(self) -> None:
        """Create all tables if they do not already exist and migrate schema."""
        cursor = self.conn.cursor()
        
        # 1. Camera Models
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                equipment_designation TEXT,
                equipment_nature TEXT,
                category TEXT,
                sub_category TEXT,
                low_stock_threshold INTEGER DEFAULT 5
            );
        """)

        # 2. Clients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT,
                father_name TEXT,
                mother_name TEXT,
                dob TEXT,
                pob TEXT,
                nationality TEXT,
                doc_number TEXT UNIQUE,
                doc_issuer TEXT,
                doc_issue_date TEXT,
                address TEXT,
                city TEXT,
                phone TEXT,
                email TEXT,
                fax TEXT,
                profession TEXT,
                activity_type TEXT,
                company_name TEXT,
                company_hq TEXT,
                position TEXT,
                accreditation_ref TEXT,
                origin_country TEXT,
                import_country TEXT,
                transport_method TEXT,
                storage_location TEXT,
                security_conditions TEXT,
                shareholders TEXT,
                passport_number TEXT,
                passport_issuer TEXT,
                passport_issue_date TEXT,
                passport_expiry_date TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Serial Numbers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS serial_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                serial_number TEXT UNIQUE,
                is_used BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES camera_models(id)
            );
        """)

        # 4. Client Purchases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                serial_id INTEGER UNIQUE,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(serial_id) REFERENCES serial_numbers(id)
            );
        """)

        # 5. App Settings (Persistent user configurations like dossier root folder)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)

        # 6. Serial Numbers History Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS serial_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_id INTEGER,
                serial_number TEXT,
                client_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY (serial_id) REFERENCES serial_numbers(id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE SET NULL
            );
        """)

        # Dynamic migrations
        # Camera models migration
        cursor.execute("PRAGMA table_info(camera_models)")
        existing_cm = [row[1] for row in cursor.fetchall()]
        cm_cols = [
            ("model_name", "TEXT"), ("equipment_designation", "TEXT"), 
            ("equipment_nature", "TEXT"), ("category", "TEXT"), ("sub_category", "TEXT"),
            ("low_stock_threshold", "INTEGER DEFAULT 5")
        ]
        for col, typ in cm_cols:
            if col not in existing_cm and existing_cm:
                cursor.execute(f"ALTER TABLE camera_models ADD COLUMN {col} {typ};")

        # Clients migration
        cursor.execute("PRAGMA table_info(clients)")
        existing_cl = [row[1] for row in cursor.fetchall()]
        cl_cols = [
            ("full_name", "TEXT"), ("father_name", "TEXT"), ("mother_name", "TEXT"),
            ("dob", "TEXT"), ("pob", "TEXT"), ("nationality", "TEXT"),
            ("doc_number", "TEXT"), ("doc_issuer", "TEXT"), ("doc_issue_date", "TEXT"),
            ("address", "TEXT"), ("city", "TEXT"), ("phone", "TEXT"),
            ("email", "TEXT"), ("fax", "TEXT"), ("profession", "TEXT"),
            ("activity_type", "TEXT"), ("company_name", "TEXT"), ("company_hq", "TEXT"),
            ("position", "TEXT"), ("accreditation_ref", "TEXT"), ("origin_country", "TEXT"),
            ("import_country", "TEXT"), ("transport_method", "TEXT"), ("storage_location", "TEXT"),
            ("security_conditions", "TEXT"), ("shareholders", "TEXT"),
            ("passport_number", "TEXT"), ("passport_issuer", "TEXT"),
            ("passport_issue_date", "TEXT"), ("passport_expiry_date", "TEXT"),
            ("created_at", "DATETIME")
        ]
        for col, typ in cl_cols:
            if col not in existing_cl and existing_cl:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col} {typ};")

        # Serial numbers migration
        cursor.execute("PRAGMA table_info(serial_numbers)")
        existing_sn = [row[1] for row in cursor.fetchall()]
        if "created_at" not in existing_sn and existing_sn:
            cursor.execute("ALTER TABLE serial_numbers ADD COLUMN created_at DATETIME;")

        # Client purchases migration
        cursor.execute("PRAGMA table_info(client_purchases)")
        existing_cp = [row[1] for row in cursor.fetchall()]
        if "assigned_at" not in existing_cp and existing_cp:
            cursor.execute("ALTER TABLE client_purchases ADD COLUMN assigned_at DATETIME;")

        # Secondary Composite Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sn_model_used ON serial_numbers(model_id, is_used);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cp_client_id ON client_purchases(client_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sn_serial ON serial_numbers(serial_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sn_used ON serial_numbers(is_used);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_name ON camera_models(model_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sh_serial_id ON serial_history(serial_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sh_serial_num ON serial_history(serial_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sh_client_id ON serial_history(client_id);")

        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Camera Models CRUD
    # ------------------------------------------------------------------ #
    @synchronized
    def get_camera_models(self) -> list[dict]:
        """Return all camera models with stock count and low stock threshold."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                cm.*,
                COALESCE(cm.low_stock_threshold, 5) as low_stock_threshold,
                COUNT(CASE WHEN sn.is_used = 0 THEN 1 END) as in_stock_count,
                COUNT(CASE WHEN sn.is_used = 1 THEN 1 END) as assigned_count,
                COUNT(sn.id) as total_count
            FROM camera_models cm
            LEFT JOIN serial_numbers sn ON cm.id = sn.model_id
            GROUP BY cm.id
            ORDER BY cm.id DESC;
        """)
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def add_camera_model(self, model_name: str, equipment_designation: str, 
                         equipment_nature: str, category: str, sub_category: str,
                         low_stock_threshold: int = 5) -> int:
        """Insert a new camera model and return its ID."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO camera_models 
                   (model_name, equipment_designation, equipment_nature, category, sub_category, low_stock_threshold) 
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (model_name, equipment_designation, equipment_nature, category, sub_category, low_stock_threshold)
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception:
            self.conn.rollback()
            return 0

    @synchronized
    def update_model_threshold(self, model_id: int, threshold: int) -> bool:
        """Update low stock alert threshold for a camera model."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "UPDATE camera_models SET low_stock_threshold = ? WHERE id = ?;",
                (threshold, model_id)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    @synchronized
    def update_camera_model(self, model_id: int, model_name: str, equipment_designation: str = "",
                            technical_nature: str = None, regulatory_section: str = None,
                            regulatory_subsection: str = None, low_stock_threshold: int = 5,
                            equipment_nature: str = None, category: str = None, sub_category: str = None, **kwargs) -> bool:
        """Update existing camera model fields."""
        nature = technical_nature if technical_nature is not None else (equipment_nature if equipment_nature is not None else "")
        cat = regulatory_section if regulatory_section is not None else (category if category is not None else "")
        subcat = regulatory_subsection if regulatory_subsection is not None else (sub_category if sub_category is not None else "")
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE camera_models
                SET model_name = ?,
                    equipment_designation = ?,
                    equipment_nature = ?,
                    category = ?,
                    sub_category = ?,
                    low_stock_threshold = ?
                WHERE id = ?;
            """, (str(model_name).strip(), str(equipment_designation).strip(), str(nature).strip(),
                  str(cat).strip(), str(subcat).strip(), int(low_stock_threshold), int(model_id)))
            self.conn.commit()
            return cursor.rowcount > 0
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    @synchronized
    def delete_camera_model(self, model_id: int) -> bool:
        """Delete a camera model if it has no assigned serial numbers."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM serial_numbers WHERE model_id = ? AND is_used = 1;", (model_id,))
            if cursor.fetchone()[0] > 0:
                return False
            cursor.execute("DELETE FROM serial_numbers WHERE model_id = ?;", (model_id,))
            cursor.execute("DELETE FROM camera_models WHERE id = ?;", (model_id,))
            self.conn.commit()
            return True
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    # ------------------------------------------------------------------ #
    #  Clients CRUD
    # ------------------------------------------------------------------ #
    @synchronized
    def get_clients(self, search_query: str = "") -> list[dict]:
        """Return all clients or filter by full_name, company_name, or doc_number."""
        cursor = self.conn.cursor()
        if search_query:
            q = f"%{search_query.strip()}%"
            cursor.execute("""
                SELECT 
                    c.*,
                    COUNT(cp.id) as camera_count
                FROM clients c
                LEFT JOIN client_purchases cp ON c.id = cp.client_id
                WHERE c.full_name LIKE ? OR c.company_name LIKE ? OR c.doc_number LIKE ? OR c.phone LIKE ? OR CAST(c.id AS TEXT) LIKE ?
                GROUP BY c.id
                ORDER BY c.id DESC;
            """, (q, q, q, q, q))
        else:
            cursor.execute("""
                SELECT 
                    c.*,
                    COUNT(cp.id) as camera_count
                FROM clients c
                LEFT JOIN client_purchases cp ON c.id = cp.client_id
                GROUP BY c.id
                ORDER BY c.id DESC;
            """)
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def get_client(self, client_id: int) -> dict:
        """Return a single client by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?;", (client_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @synchronized
    def add_client(self, client_data: dict) -> int:
        """Insert a new client into the database and return the client ID."""
        cursor = self.conn.cursor()
        fields = [
            "full_name", "father_name", "mother_name", "dob", "pob", "nationality",
            "doc_number", "doc_issuer", "doc_issue_date", "address", "city", "phone",
            "email", "fax", "profession", "activity_type", "company_name", "company_hq",
            "position", "accreditation_ref", "origin_country", "import_country",
            "transport_method", "storage_location", "security_conditions", "shareholders",
            "passport_number", "passport_issuer", "passport_issue_date", "passport_expiry_date"
        ]
        
        present_fields = [f for f in fields if f in client_data]
        placeholders = ", ".join(["?"] * len(present_fields))
        columns = ", ".join(present_fields)
        values = [client_data[f] for f in present_fields]
        
        query = f"INSERT INTO clients ({columns}) VALUES ({placeholders});"
        
        try:
            cursor.execute(query, tuple(values))
            self.conn.commit()
            return cursor.lastrowid
        except (sqlite3.IntegrityError, sqlite3.Error, Exception):
            self.conn.rollback()
            return 0

    @synchronized
    def update_client(self, client_id: int, client_data: dict) -> bool:
        """Update an existing client's info."""
        cursor = self.conn.cursor()
        fields = [
            "full_name", "father_name", "mother_name", "dob", "pob", "nationality",
            "doc_number", "doc_issuer", "doc_issue_date", "address", "city", "phone",
            "email", "fax", "profession", "activity_type", "company_name", "company_hq",
            "position", "accreditation_ref", "origin_country", "import_country",
            "transport_method", "storage_location", "security_conditions", "shareholders",
            "passport_number", "passport_issuer", "passport_issue_date", "passport_expiry_date"
        ]
        
        set_clauses = []
        values = []
        for f in fields:
            if f in client_data:
                set_clauses.append(f"{f} = ?")
                values.append(client_data[f])
        
        if not set_clauses:
            return True
            
        values.append(client_id)
        query = f"UPDATE clients SET {', '.join(set_clauses)} WHERE id = ?;"
        
        try:
            cursor.execute(query, tuple(values))
            self.conn.commit()
            return True
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    @synchronized
    def delete_client(self, client_id: int) -> bool:
        """Delete a client and return all their assigned cameras back to stock."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id FROM clients WHERE id = ?;", (client_id,))
            if not cursor.fetchone():
                return False
            cursor.execute("""
                SELECT sn.id, sn.serial_number 
                FROM serial_numbers sn 
                JOIN client_purchases cp ON sn.id = cp.serial_id 
                WHERE cp.client_id = ?;
            """, (client_id,))
            assigned_rows = cursor.fetchall()
            for r in assigned_rows:
                sid, sn = r[0], r[1]
                cursor.execute("UPDATE serial_numbers SET is_used = 0 WHERE id = ?;", (sid,))
                cursor.execute("""
                    INSERT INTO serial_history (serial_id, serial_number, client_id, action, details)
                    VALUES (?, ?, ?, 'RETURN', 'Client deleted');
                """, (sid, sn, client_id))
            cursor.execute("DELETE FROM client_purchases WHERE client_id = ?;", (client_id,))
            cursor.execute("DELETE FROM clients WHERE id = ?;", (client_id,))
            self.conn.commit()
            return True
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    # ------------------------------------------------------------------ #
    #  Inventory & Serial Numbers
    # ------------------------------------------------------------------ #
    @synchronized
    def save_serial_batch(self, model_id: int, serials: list[str]) -> int:
        """Insert a batch of serial numbers for a model. Skips duplicates."""
        cursor = self.conn.cursor()
        inserted = 0
        try:
            for sn in serials:
                clean_sn = str(sn).strip()
                if not clean_sn:
                    continue
                try:
                    cursor.execute(
                        "INSERT INTO serial_numbers (model_id, serial_number) VALUES (?, ?);",
                        (model_id, clean_sn)
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass
            self.conn.commit()
            return inserted
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return 0

    @synchronized
    def save_single_serial_direct(self, model_id: int, serial_number: str) -> dict:
        """
        Instantly saves a single scanned barcode serial to the database with strict validation.
        Returns a rich status dict for direct audio-visual feedback in UI.
        """
        if not serial_number or not str(serial_number).strip():
            return {
                "success": False,
                "error": "invalid_input",
                "message": "Numéro de série vide ou invalide."
            }

        clean_sn = str(serial_number).strip()
        cursor = self.conn.cursor()

        # Check model exists
        cursor.execute("SELECT id, model_name FROM camera_models WHERE id = ?;", (model_id,))
        model_row = cursor.fetchone()
        if not model_row:
            return {
                "success": False,
                "error": "invalid_model",
                "message": f"Modèle #{model_id} introuvable."
            }
        model_name = model_row["model_name"]

        # Check duplicate
        cursor.execute("""
            SELECT sn.id, sn.is_used, cm.model_name, c.full_name as assigned_client
            FROM serial_numbers sn
            JOIN camera_models cm ON sn.model_id = cm.id
            LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
            LEFT JOIN clients c ON cp.client_id = c.id
            WHERE sn.serial_number = ?;
        """, (clean_sn,))
        existing = cursor.fetchone()
        if existing:
            status_text = f"assigné à {existing['assigned_client']}" if existing['is_used'] else "déjà en stock"
            return {
                "success": False,
                "error": "duplicate",
                "duplicate": True,
                "serial_number": clean_sn,
                "existing_id": existing["id"],
                "existing_model": existing["model_name"],
                "message": f"Le numéro '{clean_sn}' existe déjà ({existing['model_name']} - {status_text})."
            }

        try:
            cursor.execute(
                "INSERT INTO serial_numbers (model_id, serial_number, is_used) VALUES (?, ?, 0);",
                (model_id, clean_sn)
            )
            new_id = cursor.lastrowid
            self.conn.commit()
            return {
                "success": True,
                "serial_id": new_id,
                "serial_number": clean_sn,
                "model_id": model_id,
                "model_name": model_name,
                "is_used": 0,
                "assigned_client_name": None,
                "message": f"Numéro '{clean_sn}' enregistré avec succès."
            }
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return {
                "success": False,
                "error": "duplicate",
                "duplicate": True,
                "serial_number": clean_sn,
                "message": f"Le numéro de série '{clean_sn}' existe déjà."
            }
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "error": "database_error",
                "message": str(e)
            }

    @synchronized
    def delete_serial_number(self, serial_id: int) -> dict:
        """
        Deletes an unassigned serial number from inventory.
        Prevents deletion if the camera is assigned to a client (enforces regulatory integrity).
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT sn.id, sn.serial_number, sn.is_used, c.full_name as client_name
            FROM serial_numbers sn
            LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
            LEFT JOIN clients c ON cp.client_id = c.id
            WHERE sn.id = ?;
        """, (serial_id,))
        row = cursor.fetchone()
        if not row:
            return {
                "success": False,
                "error": "not_found",
                "message": "Numéro de série introuvable."
            }

        if row["is_used"]:
            client_name = row["client_name"] or "un client"
            return {
                "success": False,
                "error": "assigned",
                "message": f"Impossible de supprimer le numéro '{row['serial_number']}': il est assigné à {client_name}. Effectuez un retour en stock avant de supprimer."
            }

        try:
            cursor.execute("DELETE FROM serial_numbers WHERE id = ?;", (serial_id,))
            self.conn.commit()
            return {
                "success": True,
                "serial_id": serial_id,
                "serial_number": row["serial_number"],
                "message": f"Numéro '{row['serial_number']}' supprimé avec succès."
            }
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "error": "database_error",
                "message": str(e)
            }

    @synchronized
    def delete_serials_batch(self, serial_ids: list[int]) -> dict:
        """
        Transactionally deletes multiple unassigned serial numbers.
        Skips any that are currently assigned to clients.
        """
        if not serial_ids:
            return {"success": True, "deleted_count": 0, "skipped_assigned": 0, "message": "Aucun élément sélectionné."}

        cursor = self.conn.cursor()
        try:
            placeholders = ",".join("?" for _ in serial_ids)
            cursor.execute(f"SELECT id, is_used FROM serial_numbers WHERE id IN ({placeholders});", tuple(serial_ids))
            rows = cursor.fetchall()

            unassigned_ids = [r["id"] for r in rows if not r["is_used"]]
            skipped_assigned = len(rows) - len(unassigned_ids)

            if unassigned_ids:
                del_placeholders = ",".join("?" for _ in unassigned_ids)
                cursor.execute(f"DELETE FROM serial_numbers WHERE id IN ({del_placeholders});", tuple(unassigned_ids))
            self.conn.commit()
            return {
                "success": True,
                "deleted_count": len(unassigned_ids),
                "skipped_assigned": skipped_assigned,
                "message": f"{len(unassigned_ids)} numéro(s) supprimé(s)." + (f" ({skipped_assigned} ignoré(s) car assigné(s))" if skipped_assigned > 0 else "")
            }
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "error": "database_error",
                "message": str(e)
            }

    @synchronized
    def get_available_serials(self, model_id: int) -> list[dict]:
        """Return unused serial numbers for a specific camera model."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, serial_number FROM serial_numbers WHERE model_id = ? AND is_used = 0 ORDER BY id ASC;",
            (model_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def get_all_serials(self, model_id: int = None) -> list[dict]:
        """Return all serial numbers with model info."""
        cursor = self.conn.cursor()
        if model_id:
            cursor.execute("""
                SELECT 
                    sn.id, sn.serial_number, sn.is_used, cm.model_name,
                    c.full_name as assigned_client_name, c.id as assigned_client_id
                FROM serial_numbers sn
                JOIN camera_models cm ON sn.model_id = cm.id
                LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
                LEFT JOIN clients c ON cp.client_id = c.id
                WHERE sn.model_id = ?
                ORDER BY sn.id DESC;
            """, (model_id,))
        else:
            cursor.execute("""
                SELECT 
                    sn.id, sn.serial_number, sn.is_used, cm.model_name,
                    c.full_name as assigned_client_name, c.id as assigned_client_id
                FROM serial_numbers sn
                JOIN camera_models cm ON sn.model_id = cm.id
                LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
                LEFT JOIN clients c ON cp.client_id = c.id
                ORDER BY sn.id DESC;
            """)
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def is_serial_exists(self, serial_number: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM serial_numbers WHERE serial_number = ? LIMIT 1;", (serial_number.strip(),))
        return cursor.fetchone() is not None

    @synchronized
    def assign_camera_to_client(self, client_id: int, serial_id: int) -> bool:
        """Assign a camera serial to a client."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO client_purchases (client_id, serial_id) VALUES (?, ?);",
                (client_id, serial_id)
            )
            cursor.execute(
                "UPDATE serial_numbers SET is_used = 1 WHERE id = ?;",
                (serial_id,)
            )
            cursor.execute("SELECT serial_number FROM serial_numbers WHERE id = ?;", (serial_id,))
            sn_row = cursor.fetchone()
            sn_val = sn_row[0] if sn_row else ""
            cursor.execute("""
                INSERT INTO serial_history (serial_id, serial_number, client_id, action)
                VALUES (?, ?, ?, 'ASSIGN');
            """, (serial_id, sn_val, client_id))
            self.conn.commit()
            return True
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    @synchronized
    def assign_cameras_batch(self, client_id: int, serial_ids: list[int]) -> int:
        """Assign multiple cameras to a client in a single transaction."""
        cursor = self.conn.cursor()
        assigned = 0
        try:
            for sid in serial_ids:
                cursor.execute(
                    "INSERT INTO client_purchases (client_id, serial_id) VALUES (?, ?);",
                    (client_id, sid)
                )
                cursor.execute(
                    "UPDATE serial_numbers SET is_used = 1 WHERE id = ?;",
                    (sid,)
                )
                cursor.execute("SELECT serial_number FROM serial_numbers WHERE id = ?;", (sid,))
                sn_row = cursor.fetchone()
                sn_val = sn_row[0] if sn_row else ""
                cursor.execute("""
                    INSERT INTO serial_history (serial_id, serial_number, client_id, action)
                    VALUES (?, ?, ?, 'ASSIGN');
                """, (sid, sn_val, client_id))
                assigned += 1
            self.conn.commit()
            return assigned
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return 0

    @synchronized
    def assign_camera_by_serial_number(self, client_id: int, serial_number: str) -> dict:
        """
        Scan-to-Client: Directly assigns an in-stock camera serial to a client by barcode.
        Automatically verifies serial exists, model info, and whether already assigned.
        """
        if not serial_number or not str(serial_number).strip():
            return {"success": False, "error": "invalid_input", "message": "Numéro de série vide ou invalide."}

        clean_sn = str(serial_number).strip().upper()
        cursor = self.conn.cursor()

        # Check client exists
        cursor.execute("SELECT id, full_name, company_name FROM clients WHERE id = ?;", (client_id,))
        client_row = cursor.fetchone()
        if not client_row:
            return {"success": False, "error": "client_not_found", "message": f"Client #{client_id} introuvable."}
        client_name = client_row["full_name"] or client_row["company_name"] or f"Client #{client_id}"

        # Find serial number
        cursor.execute("""
            SELECT sn.id, sn.serial_number, sn.is_used, cm.id as model_id, cm.model_name,
                   c.full_name as current_client_name
            FROM serial_numbers sn
            JOIN camera_models cm ON sn.model_id = cm.id
            LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
            LEFT JOIN clients c ON cp.client_id = c.id
            WHERE UPPER(sn.serial_number) = ?;
        """, (clean_sn,))
        row = cursor.fetchone()

        if not row:
            return {
                "success": False,
                "error": "not_found",
                "serial_number": clean_sn,
                "message": f"Numéro '{clean_sn}' introuvable dans le stock."
            }

        if row["is_used"]:
            curr_holder = row["current_client_name"] or "un autre client"
            return {
                "success": False,
                "error": "already_assigned",
                "serial_number": clean_sn,
                "assigned_to": curr_holder,
                "message": f"Numéro '{clean_sn}' déjà assigné à {curr_holder}."
            }

        sid = row["id"]
        try:
            cursor.execute(
                "INSERT INTO client_purchases (client_id, serial_id) VALUES (?, ?);",
                (client_id, sid)
            )
            cursor.execute("UPDATE serial_numbers SET is_used = 1 WHERE id = ?;", (sid,))
            cursor.execute("""
                INSERT INTO serial_history (serial_id, serial_number, client_id, action)
                VALUES (?, ?, ?, 'ASSIGN');
            """, (sid, row["serial_number"], client_id))
            self.conn.commit()
            return {
                "success": True,
                "client_id": client_id,
                "client_name": client_name,
                "serial_id": sid,
                "serial_number": row["serial_number"],
                "model_id": row["model_id"],
                "model_name": row["model_name"],
                "message": f"Caméra {row['model_name']} ({row['serial_number']}) assignée avec succès à {client_name}."
            }
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "error": "database_error", "message": str(e)}

    @synchronized
    def assign_n_cameras_by_model(self, client_id: int, model_id: int, count: int) -> dict:
        """
        Auto-pick allocation: Selects and assigns N available in-stock cameras of a model to a client.
        Enforces transaction atomicity and prevents over-allocation.
        """
        if count <= 0:
            return {"success": False, "error": "invalid_count", "message": "La quantité doit être supérieure à 0."}

        cursor = self.conn.cursor()

        # Check client
        cursor.execute("SELECT id, full_name, company_name FROM clients WHERE id = ?;", (client_id,))
        client_row = cursor.fetchone()
        if not client_row:
            return {"success": False, "error": "client_not_found", "message": f"Client #{client_id} introuvable."}
        client_name = client_row["full_name"] or client_row["company_name"]

        # Check model and available stock
        cursor.execute("SELECT id, model_name FROM camera_models WHERE id = ?;", (model_id,))
        model_row = cursor.fetchone()
        if not model_row:
            return {"success": False, "error": "model_not_found", "message": f"Modèle #{model_id} introuvable."}
        model_name = model_row["model_name"]

        cursor.execute(
            "SELECT id, serial_number FROM serial_numbers WHERE model_id = ? AND is_used = 0 ORDER BY id ASC LIMIT ?;",
            (model_id, count)
        )
        available_rows = cursor.fetchall()

        if len(available_rows) < count:
            return {
                "success": False,
                "error": "insufficient_stock",
                "requested_count": count,
                "available_count": len(available_rows),
                "model_name": model_name,
                "message": f"Stock insuffisant pour {model_name}: {len(available_rows)} disponible(s), {count} demandé(s)."
            }

        assigned_serials = []
        try:
            for r in available_rows:
                sid = r["id"]
                sn = r["serial_number"]
                cursor.execute(
                    "INSERT INTO client_purchases (client_id, serial_id) VALUES (?, ?);",
                    (client_id, sid)
                )
                cursor.execute("UPDATE serial_numbers SET is_used = 1 WHERE id = ?;", (sid,))
                cursor.execute("""
                    INSERT INTO serial_history (serial_id, serial_number, client_id, action)
                    VALUES (?, ?, ?, 'ASSIGN');
                """, (sid, sn, client_id))
                assigned_serials.append({"id": sid, "serial_number": sn})

            self.conn.commit()
            return {
                "success": True,
                "client_id": client_id,
                "client_name": client_name,
                "model_id": model_id,
                "model_name": model_name,
                "assigned_count": len(assigned_serials),
                "serials": assigned_serials,
                "message": f"{len(assigned_serials)} caméra(s) {model_name} assignée(s) avec succès à {client_name}."
            }
        except Exception as e:
            self.conn.rollback()
            return {"success": False, "error": "database_error", "message": str(e)}

    @synchronized
    def return_cameras_batch(self, serial_numbers: list[str]) -> int:
        """Return cameras to stock: removes assignment from client_purchases and resets is_used = 0."""
        cursor = self.conn.cursor()
        count = 0
        try:
            for sn in serial_numbers:
                cursor.execute("""
                    SELECT sn.id, cp.client_id
                    FROM serial_numbers sn
                    LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
                    WHERE sn.serial_number = ?;
                """, (sn,))
                row = cursor.fetchone()
                if row:
                    sid = row[0]
                    client_id = row[1]
                    cursor.execute("DELETE FROM client_purchases WHERE serial_id = ?;", (sid,))
                    cursor.execute("UPDATE serial_numbers SET is_used = 0 WHERE id = ?;", (sid,))
                    cursor.execute("""
                        INSERT INTO serial_history (serial_id, serial_number, client_id, action)
                        VALUES (?, ?, ?, 'RETURN');
                    """, (sid, sn, client_id))
                    count += 1
            self.conn.commit()
            return count
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return 0

    @synchronized
    def get_client_purchases_for_pdf(self, client_id: int) -> dict:
        """Fetch client details and all assigned cameras for PDF generation."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?;", (client_id,))
        client_row = cursor.fetchone()
        if not client_row:
            return {"client": None, "cameras": []}
            
        client = dict(client_row)
        cursor.execute("""
            SELECT 
                cm.model_name, cm.equipment_designation, cm.equipment_nature, cm.category, cm.sub_category, sn.serial_number, sn.id as serial_id, cp.assigned_at
            FROM client_purchases cp
            JOIN serial_numbers sn ON cp.serial_id = sn.id
            JOIN camera_models cm ON sn.model_id = cm.id
            WHERE cp.client_id = ?;
        """, (client_id,))
        
        cameras = [dict(row) for row in cursor.fetchall()]
        return {"client": client, "cameras": cameras}

    @synchronized
    def clear_database(self) -> bool:
        """Truncate all tables."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM serial_history;")
            cursor.execute("DELETE FROM client_purchases;")
            cursor.execute("DELETE FROM serial_numbers;")
            cursor.execute("DELETE FROM clients;")
            cursor.execute("DELETE FROM camera_models;")
            self.conn.commit()
            return True
        except (sqlite3.Error, Exception):
            self.conn.rollback()
            return False

    @synchronized
    def get_serial_history(self, serial_number: str = None, client_id: int = None, limit: int = 50) -> list[dict]:
        """Query serial assignment and return history."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM serial_history"
        conditions = []
        params = []
        if serial_number:
            conditions.append("serial_number = ?")
            params.append(str(serial_number).strip())
        if client_id is not None:
            conditions.append("client_id = ?")
            params.append(int(client_id))
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id DESC LIMIT ?;"
        params.append(int(limit))
        cursor.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def close(self) -> None:
        if self.conn:
            self.conn.close()

    # ------------------------------------------------------------------ #
    #  Executive Analytics & Metrics (R1)
    # ------------------------------------------------------------------ #
    @synchronized
    def get_dashboard_analytics(self) -> dict:
        """Return executive analytics and stock overview metrics."""
        cursor = self.conn.cursor()

        # Aggregate counts
        cursor.execute("SELECT COUNT(*) FROM serial_numbers WHERE is_used = 0;")
        total_stock = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM serial_numbers WHERE is_used = 1;")
        total_assigned = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clients;")
        total_clients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM camera_models;")
        total_models = cursor.fetchone()[0]

        # Low stock items: models where in_stock_count <= threshold
        cursor.execute("""
            SELECT 
                cm.id AS model_id,
                cm.model_name,
                cm.equipment_designation,
                cm.equipment_nature,
                COALESCE(cm.low_stock_threshold, 5) AS threshold,
                COUNT(CASE WHEN sn.is_used = 0 THEN 1 END) AS in_stock,
                COUNT(CASE WHEN sn.is_used = 1 THEN 1 END) AS assigned_count,
                COUNT(sn.id) AS total_count
            FROM camera_models cm
            LEFT JOIN serial_numbers sn ON cm.id = sn.model_id
            GROUP BY cm.id
            HAVING in_stock <= COALESCE(cm.low_stock_threshold, 5)
            ORDER BY in_stock ASC, cm.model_name ASC;
        """)
        low_stock_items = [dict(row) for row in cursor.fetchall()]

        # Recent clients (latest 5 registrations)
        cursor.execute("""
            SELECT 
                c.id, c.full_name, c.company_name, c.doc_number, c.phone,
                COUNT(cp.id) AS camera_count
            FROM clients c
            LEFT JOIN client_purchases cp ON c.id = cp.client_id
            GROUP BY c.id
            ORDER BY c.id DESC
            LIMIT 5;
        """)
        recent_clients = [dict(row) for row in cursor.fetchall()]

        return {
            "total_stock": total_stock,
            "total_assigned": total_assigned,
            "total_clients": total_clients,
            "total_models": total_models,
            "low_stock_count": len(low_stock_items),
            "low_stock_items": low_stock_items,
            "totals": {
                "total_clients": total_clients,
                "total_in_stock": total_stock,
                "total_assigned": total_assigned,
                "total_models": total_models
            },
            "low_stock_alerts": low_stock_items,
            "recent_clients": recent_clients
        }

    @synchronized
    def get_executive_metrics(self) -> dict:
        """Alias for get_dashboard_analytics."""
        return self.get_dashboard_analytics()

    # ------------------------------------------------------------------ #
    #  Inventory Search & Filters (R2)
    # ------------------------------------------------------------------ #
    @synchronized
    def search_serials(self, query: str = None, model_id: int = None, status: str = None) -> list[dict]:
        """
        Search serial numbers joined with camera_models and assigned client.
        Supports partial serial query, filtering by model_id, and status ('in_stock', 'assigned', 'all').
        """
        cursor = self.conn.cursor()
        sql = """
            SELECT 
                sn.id,
                sn.serial_number,
                sn.is_used,
                sn.model_id,
                cm.model_name,
                cm.equipment_designation,
                cm.equipment_nature,
                c.id AS client_id,
                c.id AS assigned_client_id,
                c.full_name AS client_name,
                c.full_name AS assigned_client_name,
                c.company_name AS client_company,
                c.phone AS client_phone,
                cp.assigned_at
            FROM serial_numbers sn
            JOIN camera_models cm ON sn.model_id = cm.id
            LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
            LEFT JOIN clients c ON cp.client_id = c.id
        """
        where_clauses = []
        params = []

        if query and str(query).strip():
            q_clean = f"%{str(query).strip()}%"
            where_clauses.append("(sn.serial_number LIKE ? OR cm.model_name LIKE ? OR c.full_name LIKE ? OR c.company_name LIKE ?)")
            params.extend([q_clean, q_clean, q_clean, q_clean])

        if model_id is not None and str(model_id).strip() not in ("", "all", "None"):
            try:
                clean_mid = int(model_id)
                where_clauses.append("sn.model_id = ?")
                params.append(clean_mid)
            except (ValueError, TypeError):
                pass

        if status:
            s_lower = str(status).strip().lower()
            if s_lower in ("in_stock", "0", "available", "instock"):
                where_clauses.append("sn.is_used = 0")
            elif s_lower in ("assigned", "1", "used"):
                where_clauses.append("sn.is_used = 1")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY sn.id DESC;"
        cursor.execute(sql, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    # ------------------------------------------------------------------ #
    #  Bulk CSV/Excel Ingestion Engine (R2)
    # ------------------------------------------------------------------ #
    @synchronized
    def preview_csv_serials(self, csv_text: str) -> dict:
        """
        Auto-detect delimiter (comma, semicolon, tab, pipe, newline).
        Trim whitespace and quotes.
        Detect intra-file duplicates and serials already present in DB.
        Returns: {
            "total_found": int,
            "valid": list[str],
            "duplicates_in_file": list[str],
            "already_in_db": list[str]
        }
        """
        text = _normalize_text_input(csv_text)
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            return {
                "total_found": 0,
                "valid": [],
                "duplicates_in_file": [],
                "already_in_db": []
            }

        sample = "\n".join(lines[:10])
        counts = {
            ";": sample.count(";"),
            ",": sample.count(","),
            "\t": sample.count("\t"),
            "|": sample.count("|")
        }
        best_delim = max(counts, key=counts.get)
        delimiter = best_delim if counts[best_delim] > 0 else None

        raw_candidates = []

        # Disqualified line-number / sequence headers (row indices, NOT serials)
        line_num_headers = {
            "num", "numero", "numéro", "n°", "no", "no.", "#", "id", "index", "idx", "line", "ligne", "row", "item"
        }

        # High-priority serial keywords (explicitly denote camera/equipment serial numbers)
        high_priority_serial_keywords = (
            "serial_number", "serial number", "serial_no", "serial no", "serial", "serials",
            "num_serie", "num serie", "num_série", "num série",
            "numéro de série", "numero de serie", "n° série", "n° serie",
            "n° de série", "n° de serie", "no de série", "no de serie", "no série", "no serie",
            "barcode", "bar code", "code barre", "code barres", "code-barre", "code-barres",
            "الرقم التسلسلي", "رقم التسلسل", "رقم تسلسلي", "سيريال"
        )

        # Standalone exact-match short abbreviations
        exact_serial_tokens = {"sn", "s/n", "s_n", "s.n.", "s.n", "serie", "série"}

        def score_header_cell(cell: str) -> int:
            raw = str(cell).strip().strip("\"'")
            if not raw:
                return -1
            lower = raw.lower()
            clean = re.sub(r'[\s_\-\./#°№:]+', ' ', lower).strip()

            # Disqualify sequence/line number headers unless qualified by serie/serial
            if lower in line_num_headers or clean in line_num_headers:
                if not any(k in clean for k in ("serial", "serie", "série")):
                    return -50

            # Check high-priority serial keywords
            # Guard: if cell contains digits (e.g. SN-98765, CODE-1001), it is DATA, not a header!
            if any(k in clean for k in high_priority_serial_keywords) or any(k in lower for k in high_priority_serial_keywords):
                if not re.search(r'\d{3,}', raw):
                    return 100

            # Check exact short serial tokens
            if lower in exact_serial_tokens or clean in exact_serial_tokens:
                return 100

            # Check low priority generic keywords ('code', 'رقم')
            if (lower in ("code", "رقم") or clean in ("code", "رقم")) and not re.search(r'\d', raw):
                return 10

            return 0

        if delimiter:
            reader = csv.reader(io.StringIO(text), delimiter=delimiter)
            rows = [r for r in reader if any(cell.strip() for cell in r)]
            if not rows:
                return {"total_found": 0, "valid": [], "duplicates_in_file": [], "already_in_db": []}

            first_row = [str(c).strip() for c in rows[0]]
            col_scores = [score_header_cell(c) for c in first_row]
            best_score = max(col_scores) if col_scores else 0

            header_found = False
            serial_col_idx = 0

            if best_score >= 50:
                header_found = True
                serial_col_idx = col_scores.index(best_score)
            elif best_score > 0 and len(first_row) > 1:
                header_found = True
                serial_col_idx = col_scores.index(best_score)
            else:
                header_found = False
                # Determine best serial column from data rows if multi-column
                best_data_col = 0
                best_data_score = -1
                for col_idx in range(len(first_row)):
                    col_vals = [r[col_idx].strip() for r in rows[:10] if len(r) > col_idx and r[col_idx].strip()]
                    score = 0
                    for v in col_vals:
                        v_low = v.lower()
                        if v.isdigit() and len(v) <= 4:
                            score -= 2  # likely sequence/line index
                        elif v_low.startswith(("sn", "s/n", "cam", "hik", "dah", "code", "num-")):
                            score += 5
                        elif len(v) >= 5 and any(c.isdigit() for c in v) and any(c.isalpha() for c in v):
                            score += 3
                    if score > best_data_score:
                        best_data_score = score
                        best_data_col = col_idx
                serial_col_idx = best_data_col

            start_row = 1 if header_found else 0
            for r in rows[start_row:]:
                if len(r) > serial_col_idx:
                    val = str(r[serial_col_idx]).strip().strip("\"'")
                    if val:
                        raw_candidates.append(val)
        else:
            # Single-column raw list
            first_val = lines[0].strip().strip("\"'").lower()
            clean_first = re.sub(r'[\s_\-\./#°№:]+', ' ', first_val).strip()
            is_h0 = (
                any(k in clean_first for k in high_priority_serial_keywords) or
                first_val in exact_serial_tokens
            ) and not re.search(r'\d{3,}', first_val)
            start_idx = 1 if is_h0 else 0
            for line in lines[start_idx:]:
                val = line.strip().strip("\"'")
                if val:
                    raw_candidates.append(val)

        seen_in_file = set()
        duplicates_in_file = []
        file_unique_serials = []

        for sn in raw_candidates:
            if sn in seen_in_file:
                duplicates_in_file.append(sn)
            else:
                seen_in_file.add(sn)
                file_unique_serials.append(sn)

        total_found = len(raw_candidates)
        already_in_db = []
        valid = []

        if file_unique_serials:
            cursor = self.conn.cursor()
            existing_db_set = set()
            chunk_size = 500
            for i in range(0, len(file_unique_serials), chunk_size):
                chunk = file_unique_serials[i:i + chunk_size]
                placeholders = ",".join(["?"] * len(chunk))
                cursor.execute(
                    f"SELECT serial_number FROM serial_numbers WHERE serial_number IN ({placeholders});",
                    tuple(chunk)
                )
                for row in cursor.fetchall():
                    existing_db_set.add(row[0])

            for sn in file_unique_serials:
                if sn in existing_db_set:
                    already_in_db.append(sn)
                else:
                    valid.append(sn)

        return {
            "total_found": total_found,
            "valid": valid,
            "duplicates_in_file": duplicates_in_file,
            "already_in_db": already_in_db
        }

    @synchronized
    def import_serials_batch(self, model_id: int, serials: list[str]) -> dict:
        """
        Atomically insert a batch of unique, non-existing serial numbers for a camera model.
        Returns: { "success": bool, "imported_count": int, "duplicates_skipped": int }
        """
        if not serials:
            return {"success": True, "imported_count": 0, "duplicates_skipped": 0}

        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM camera_models WHERE id = ?;", (int(model_id),))
            if not cursor.fetchone():
                return {
                    "success": False,
                    "imported_count": 0,
                    "duplicates_skipped": 0,
                    "error": f"Model ID {model_id} not found"
                }

            imported_count = 0
            duplicates_skipped = 0
            seen_in_batch = set()

            for sn in serials:
                clean_sn = str(sn).strip().strip("\"'")
                if not clean_sn:
                    continue
                if clean_sn in seen_in_batch:
                    duplicates_skipped += 1
                    continue
                seen_in_batch.add(clean_sn)

                cursor.execute("SELECT 1 FROM serial_numbers WHERE serial_number = ?;", (clean_sn,))
                if cursor.fetchone():
                    duplicates_skipped += 1
                else:
                    cursor.execute(
                        "INSERT INTO serial_numbers (model_id, serial_number, is_used) VALUES (?, ?, 0);",
                        (int(model_id), clean_sn)
                    )
                    imported_count += 1

            self.conn.commit()
            return {
                "success": True,
                "imported_count": imported_count,
                "duplicates_skipped": duplicates_skipped
            }
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "imported_count": 0,
                "duplicates_skipped": 0,
                "error": str(e)
            }

    # ------------------------------------------------------------------ #
    #  Bulk CSV/Excel Export Engine (R2)
    # ------------------------------------------------------------------ #
    @synchronized
    def _get_export_data(self, model_id=None, status=None) -> list[dict]:
        """Fetch joined serials data for export."""
        cursor = self.conn.cursor()
        sql = """
            SELECT 
                sn.id,
                sn.serial_number,
                cm.model_name,
                COALESCE(cm.equipment_designation, '') AS designation,
                sn.is_used,
                COALESCE(c.full_name, c.company_name, '') AS client_name,
                COALESCE(cp.assigned_at, '') AS date_assigned
            FROM serial_numbers sn
            JOIN camera_models cm ON sn.model_id = cm.id
            LEFT JOIN client_purchases cp ON sn.id = cp.serial_id
            LEFT JOIN clients c ON cp.client_id = c.id
        """
        where = []
        params = []
        if model_id is not None and str(model_id).strip() not in ("", "all", "None"):
            try:
                clean_mid = int(model_id)
                where.append("sn.model_id = ?")
                params.append(clean_mid)
            except (ValueError, TypeError):
                pass
        if status:
            s_lower = str(status).strip().lower()
            if s_lower in ("in_stock", "0", "available", "instock"):
                where.append("sn.is_used = 0")
            elif s_lower in ("assigned", "1", "used"):
                where.append("sn.is_used = 1")
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY sn.id ASC;"
        cursor.execute(sql, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    @synchronized
    def export_serials_csv(self, model_id=None, status=None) -> str:
        """Export serial numbers to RFC 4180 CSV string with UTF-8 BOM."""
        rows = self._get_export_data(model_id, status)
        output = io.StringIO()
        output.write('\ufeff')  # UTF-8 BOM
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        writer.writerow(["ID", "Serial Number", "Model Name", "Designation", "Status", "Client Name", "Date Assigned"])

        for r in rows:
            st = "In Stock" if r["is_used"] == 0 else "Assigned"
            writer.writerow([
                r["id"],
                _sanitize_excel_value(r["serial_number"]),
                _sanitize_excel_value(r["model_name"]),
                _sanitize_excel_value(r["designation"]),
                st,
                _sanitize_excel_value(r["client_name"]),
                _sanitize_excel_value(r["date_assigned"])
            ])

        return output.getvalue()

    @synchronized
    def export_serials_excel(self, model_id=None, status=None) -> bytes:
        """Export serial numbers to a styled Excel (.xlsx) workbook as bytes."""
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        rows = self._get_export_data(model_id, status)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Inventory Serials"

        # Show gridlines
        ws.views.sheetView[0].showGridLines = True

        headers = ["ID", "Serial Number", "Model Name", "Designation", "Status", "Client Name", "Date Assigned"]
        ws.append(headers)

        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        for col_num in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        ws.row_dimensions[1].height = 28

        data_font = Font(name="Segoe UI", size=10)
        data_align_left = Alignment(horizontal="left", vertical="center")
        data_align_center = Alignment(horizontal="center", vertical="center")
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        for row_idx, r in enumerate(rows, start=2):
            st = "In Stock" if r["is_used"] == 0 else "Assigned"
            row_data = [
                r["id"],
                _sanitize_excel_value(r["serial_number"]),
                _sanitize_excel_value(r["model_name"]),
                _sanitize_excel_value(r["designation"]),
                st,
                _sanitize_excel_value(r["client_name"]),
                _sanitize_excel_value(r["date_assigned"])
            ]
            ws.append(row_data)

            fill = zebra_fill if row_idx % 2 == 0 else None
            for col_idx in range(1, len(row_data) + 1):
                c = ws.cell(row=row_idx, column=col_idx)
                c.font = data_font
                c.border = thin_border
                if fill:
                    c.fill = fill
                if col_idx in (1, 5, 7):
                    c.alignment = data_align_center
                else:
                    c.alignment = data_align_left
                # Defense-in-depth: explicitly enforce string type for non-numeric cells
                if col_idx != 1 and isinstance(c.value, str):
                    c.data_type = 's'
            ws.row_dimensions[row_idx].height = 20

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                if len(val_str) > max_len:
                    max_len = len(val_str)
            # Clamp column width between 12 and 50 characters (strictly < 255 OOXML limit)
            ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 50)

        buffer = io.BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    # ------------------------------------------------------------------ #
    #  Settings & Dossier Directory Management
    # ------------------------------------------------------------------ #
    @synchronized
    def get_setting(self, key: str, default: str = None) -> str:
        """Fetch persistent application setting by key."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

    @synchronized
    def set_setting(self, key: str, value: str) -> None:
        """Store or update persistent application setting."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value;
        """, (str(key), str(value)))
        self.conn.commit()

    @synchronized
    def get_license_data(self) -> dict:
        """Returns stored license key, last execution date, and activation timestamp."""
        return {
            "license_key": self.get_setting("license_key"),
            "last_run_date": self.get_setting("license_last_run"),
            "activated_at": self.get_setting("license_activated_at")
        }

    @synchronized
    def save_license_key(self, key: str) -> None:
        """Stores active license key and records activation timestamp."""
        import datetime
        self.set_setting("license_key", str(key).strip().upper())
        self.set_setting("license_activated_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    @synchronized
    def update_last_run_date(self, date_str: str) -> None:
        """Records last active run date for clock rollback protection."""
        self.set_setting("license_last_run", str(date_str).strip()[:10])

    @synchronized
    def clear_license(self) -> None:
        """Resets stored license data (maintenance/test use)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM app_settings WHERE key IN ('license_key', 'license_last_run', 'license_activated_at')")
        self.conn.commit()

    @synchronized
    def get_onboarding_status(self) -> bool:
        """Check if initial first-launch onboarding has been completed."""
        return self.get_setting("onboarding_completed", "false").lower() == "true"

    @synchronized
    def set_onboarding_completed(self, status: bool = True) -> None:
        """Flag onboarding as completed or reset."""
        self.set_setting("onboarding_completed", "true" if status else "false")

    @synchronized
    def get_dossier_root_dir(self) -> str:
        """
        Get user-selected base directory for client dossiers.
        Defaults to 'dossiers' in application working directory.
        """
        saved = self.get_setting("dossier_root_dir")
        if saved and os.path.exists(saved):
            return os.path.abspath(saved)
        default_dir = os.path.abspath("dossiers")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir

    @synchronized
    def set_dossier_root_dir(self, path: str) -> str:
        """Set and validate user-selected base directory for client dossiers."""
        if not path or not str(path).strip():
            raise ValueError("Folder path cannot be empty")
        clean_path = os.path.abspath(str(path).strip())
        os.makedirs(clean_path, exist_ok=True)
        self.set_setting("dossier_root_dir", clean_path)
        return clean_path

    # ------------------------------------------------------------------ #
    #  Modular Dossier Helpers & Legacy Migration (R4)
    # ------------------------------------------------------------------ #
    @synchronized
    def get_client_dossier_dir(self, client_name: str, dossier_type: str = "1er dossier", base_dir: str = None) -> str:
        """Return modular client dossier directory path."""
        target_base = base_dir if base_dir is not None else self.get_dossier_root_dir()
        return get_client_dossier_dir(client_name, dossier_type, target_base)

    @synchronized
    def migrate_legacy_dossiers(self, legacy_dir: str = "1er dossier", target_root: str = "dossiers") -> int:
        """Migrate legacy folders into modular dossier structure."""
        return migrate_legacy_dossiers(legacy_dir, target_root)

    # ------------------------------------------------------------------ #
    #  Unified Intelligent Excel / CSV / TXT Import Engine
    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_raw_bytes(raw_input) -> bytes:
        """Extract binary bytes from bytes, data URIs, or base64 strings."""
        if isinstance(raw_input, bytes):
            return raw_input
        s = str(raw_input).strip()
        if s.startswith("data:") and ";base64," in s:
            import base64
            try:
                return base64.b64decode(s.split(";base64,", 1)[1])
            except Exception:
                pass
        # Try raw base64 if no delimiters or spaces present
        if len(s) >= 16 and not any(c in s for c in ("\n", "\r", "\t", ";", ",", " ")):
            import base64
            try:
                decoded = base64.b64decode(s)
                # Ensure it decodes into reasonable bytes
                if len(decoded) > 0:
                    return decoded
            except Exception:
                pass
        return s.encode("utf-8", errors="replace")

    @staticmethod
    def _parse_excel_rows(file_bytes: bytes) -> list[list[str]]:
        """Parse rows from an openpyxl-compatible Excel workbook as string lists."""
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            if not row:
                continue
            cells = [str(c).strip() if c is not None else "" for c in row]
            if any(c != "" for c in cells):
                rows.append(cells)
        return rows

    @staticmethod
    def _parse_delimited_rows(text_content: str) -> list[list[str]]:
        """Auto-detect delimiter and parse text rows."""
        lines = [line for line in text_content.splitlines() if line.strip()]
        if not lines:
            return []
        sample = "\n".join(lines[:10])
        counts = {
            ";": sample.count(";"),
            ",": sample.count(","),
            "\t": sample.count("\t"),
            "|": sample.count("|")
        }
        best_delim = max(counts, key=counts.get)
        delimiter = best_delim if counts[best_delim] > 0 else ","

        reader = csv.reader(io.StringIO(text_content), delimiter=delimiter)
        rows = []
        for r in reader:
            if any(cell.strip() for cell in r):
                rows.append([cell.strip() for cell in r])
        return rows

    @synchronized
    def parse_and_preview_import(self, raw_content, filename: str = "", destination_model_id: int = None) -> dict:
        """
        Unified multi-format file parser and pre-flight validator.
        Auto-detects:
        - Mode A: MODELS_CATALOG (Model name, designation, nature, category, threshold)
        - Mode B: COMBINED_MANIFEST (Model name + Serial number)
        - Mode C: SERIALS_ONLY (Single column of serial numbers)
        Returns structured validation preview.
        """
        fn_lower = (filename or "").lower()
        is_excel = fn_lower.endswith((".xlsx", ".xlsm", ".xltx", ".xls"))

        rows = []
        try:
            raw_bytes = self._extract_raw_bytes(raw_content)
            # Check for Excel PK zip header or excel extension
            if is_excel or (len(raw_bytes) >= 4 and raw_bytes[:4] == b"PK\x03\x04"):
                try:
                    rows = self._parse_excel_rows(raw_bytes)
                except Exception as e:
                    # If openpyxl fails, fallback to delimited text
                    text_str = _normalize_text_input(raw_bytes)
                    rows = self._parse_delimited_rows(text_str)
            else:
                text_str = _normalize_text_input(raw_bytes)
                rows = self._parse_delimited_rows(text_str)
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lecture fichier: {str(e)}",
                "mode": "UNKNOWN",
                "total_detected": 0,
                "valid_items": [],
                "duplicates_in_file": [],
                "already_in_db": [],
                "new_models_to_create": []
            }

        if not rows:
            return {
                "success": True,
                "mode": "EMPTY",
                "total_detected": 0,
                "valid_items": [],
                "duplicates_in_file": [],
                "already_in_db": [],
                "new_models_to_create": []
            }

        # Header scoring tokens
        model_tokens = ("model", "modèle", "modele", "model_name", "marque", "camera_model", "equipement", "طراز", "الموديل", "الكاميرا")
        serial_tokens = ("serial", "serial_number", "s/n", "sn", "num_serie", "num_série", "numéro de série", "numero de serie", "n° série", "code barre", "barcode", "الرقم التسلسلي", "سيريال")
        desig_tokens = ("designation", "désignation", "description", "libelle", "libellé", "بيان", "التسمية")
        nature_tokens = ("nature", "type", "spécification", "specification", "النوع")
        cat_tokens = ("section", "category", "catégorie", "categorie", "القسم")
        subcat_tokens = ("sous-section", "sub_category", "sous section", "sub section", "الفرع")
        thresh_tokens = ("threshold", "seuil", "alerte", "min_stock", "حد")

        def match_col(header_row, tokens):
            for idx, col in enumerate(header_row):
                c_clean = re.sub(r'[\s_\-\./#°№:]+', ' ', col.lower()).strip()
                if any(tok in c_clean for tok in tokens):
                    return idx
            return None

        first_row = rows[0]
        col_model = match_col(first_row, model_tokens)
        col_serial = match_col(first_row, serial_tokens)
        col_desig = match_col(first_row, desig_tokens)
        col_nature = match_col(first_row, nature_tokens)
        col_cat = match_col(first_row, cat_tokens)
        col_subcat = match_col(first_row, subcat_tokens)
        col_thresh = match_col(first_row, thresh_tokens)

        # Mode determination
        has_header = False
        mode = "SERIALS_ONLY"

        if col_model is not None and col_serial is not None and col_model != col_serial:
            has_header = True
            mode = "COMBINED_MANIFEST"
        elif col_model is not None and col_serial is None:
            has_header = True
            mode = "MODELS_CATALOG"
        elif col_serial is not None:
            has_header = True
            mode = "SERIALS_ONLY"
        else:
            # No recognized header row; check columns count and data pattern
            if len(first_row) >= 2 and any(re.search(r'\d{3,}', str(first_row[1])) for _ in [1]):
                mode = "COMBINED_MANIFEST"
                has_header = False
                col_model = 0
                col_serial = 1
            else:
                mode = "SERIALS_ONLY"
                has_header = False
                col_serial = 0

        data_rows = rows[1:] if has_header else rows

        # Pre-fetch existing models and serials from DB for validation
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, LOWER(model_name) FROM camera_models;")
        existing_models_map = {row[1]: row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT serial_number FROM serial_numbers;")
        existing_db_serials = {row[0] for row in cursor.fetchall()}

        valid_items = []
        duplicates_in_file = []
        already_in_db = []
        new_models_to_create = set()

        if mode == "MODELS_CATALOG":
            seen_models = set()
            for r in data_rows:
                if not r or len(r) <= col_model:
                    continue
                raw_mname = r[col_model].strip()
                if not raw_mname:
                    continue
                # Defuse formula injection
                clean_mname = _sanitize_excel_value(raw_mname)
                m_lower = clean_mname.lower()

                if m_lower in seen_models:
                    duplicates_in_file.append(clean_mname)
                    continue
                seen_models.add(m_lower)

                if m_lower in existing_models_map:
                    already_in_db.append(clean_mname)

                desig = _sanitize_excel_value(r[col_desig]) if col_desig is not None and len(r) > col_desig else ""
                nature = _sanitize_excel_value(r[col_nature]) if col_nature is not None and len(r) > col_nature else ""
                cat = _sanitize_excel_value(r[col_cat]) if col_cat is not None and len(r) > col_cat else ""
                subcat = _sanitize_excel_value(r[col_subcat]) if col_subcat is not None and len(r) > col_subcat else ""
                
                thresh_val = 5
                if col_thresh is not None and len(r) > col_thresh and str(r[col_thresh]).strip().isdigit():
                    thresh_val = int(str(r[col_thresh]).strip())

                item = {
                    "model_name": clean_mname,
                    "equipment_designation": desig,
                    "equipment_nature": nature,
                    "category": cat,
                    "sub_category": subcat,
                    "low_stock_threshold": thresh_val,
                    "is_already_in_db": m_lower in existing_models_map
                }
                valid_items.append(item)

            total_detected = len(valid_items) + len(duplicates_in_file)

        elif mode == "COMBINED_MANIFEST":
            seen_serials = set()
            for r in data_rows:
                if not r or len(r) <= max(col_model or 0, col_serial or 0):
                    continue
                m_name = _sanitize_excel_value(r[col_model].strip()) if col_model is not None and len(r) > col_model else ""
                s_num = _sanitize_excel_value(r[col_serial].strip()) if col_serial is not None and len(r) > col_serial else ""

                if not m_name or not s_num:
                    continue

                if s_num in seen_serials:
                    duplicates_in_file.append(s_num)
                    continue
                seen_serials.add(s_num)

                if s_num in existing_db_serials:
                    already_in_db.append(s_num)
                    continue

                if m_name.lower() not in existing_models_map:
                    new_models_to_create.add(m_name)

                desig = _sanitize_excel_value(r[col_desig]) if col_desig is not None and len(r) > col_desig else ""

                valid_items.append({
                    "model_name": m_name,
                    "serial_number": s_num,
                    "designation": desig,
                    "is_new_model": m_name.lower() not in existing_models_map
                })

            total_detected = len(valid_items) + len(duplicates_in_file) + len(already_in_db)

        else: # SERIALS_ONLY
            seen_serials = set()
            col_idx = col_serial if col_serial is not None else 0
            for r in data_rows:
                if not r or len(r) <= col_idx:
                    continue
                s_num = _sanitize_excel_value(r[col_idx].strip())
                if not s_num:
                    continue

                if s_num in seen_serials:
                    duplicates_in_file.append(s_num)
                    continue
                seen_serials.add(s_num)

                if s_num in existing_db_serials:
                    already_in_db.append(s_num)
                else:
                    valid_items.append(s_num)

            total_detected = len(valid_items) + len(duplicates_in_file) + len(already_in_db)

        return {
            "success": True,
            "mode": mode,
            "filename": filename,
            "total_detected": total_detected,
            "valid_items": valid_items,
            "duplicates_in_file": duplicates_in_file,
            "already_in_db": already_in_db,
            "new_models_to_create": sorted(list(new_models_to_create))
        }

    @synchronized
    def commit_unified_import(self, mode: str, items: list, destination_model_id: int = None) -> dict:
        """
        Atomically commit validated items from unified import into SQLite.
        """
        if not items:
            return {"success": True, "imported_count": 0, "message": "Aucun élément à importer"}

        cursor = self.conn.cursor()
        try:
            if mode == "MODELS_CATALOG":
                imported_count = 0
                updated_count = 0
                for item in items:
                    m_name = item.get("model_name", "").strip()
                    if not m_name:
                        continue
                    cursor.execute("SELECT id FROM camera_models WHERE LOWER(model_name) = LOWER(?);", (m_name,))
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute("""
                            UPDATE camera_models SET
                                equipment_designation = COALESCE(NULLIF(?, ''), equipment_designation),
                                equipment_nature = COALESCE(NULLIF(?, ''), equipment_nature),
                                category = COALESCE(NULLIF(?, ''), category),
                                sub_category = COALESCE(NULLIF(?, ''), sub_category),
                                low_stock_threshold = ?
                            WHERE id = ?;
                        """, (
                            item.get("equipment_designation", ""),
                            item.get("equipment_nature", ""),
                            item.get("category", ""),
                            item.get("sub_category", ""),
                            item.get("low_stock_threshold", 5),
                            existing[0]
                        ))
                        updated_count += 1
                    else:
                        cursor.execute("""
                            INSERT INTO camera_models (
                                model_name, equipment_designation, equipment_nature, category, sub_category, low_stock_threshold
                            ) VALUES (?, ?, ?, ?, ?, ?);
                        """, (
                            m_name,
                            item.get("equipment_designation", ""),
                            item.get("equipment_nature", ""),
                            item.get("category", ""),
                            item.get("sub_category", ""),
                            item.get("low_stock_threshold", 5)
                        ))
                        imported_count += 1
                self.conn.commit()
                return {
                    "success": True,
                    "imported_count": imported_count,
                    "updated_count": updated_count
                }

            elif mode == "COMBINED_MANIFEST":
                # Ensure all models exist
                cursor.execute("SELECT id, LOWER(model_name) FROM camera_models;")
                models_map = {row[1]: row[0] for row in cursor.fetchall()}

                created_models_count = 0
                for item in items:
                    m_name = item.get("model_name", "").strip()
                    if not m_name:
                        continue
                    m_lower = m_name.lower()
                    if m_lower not in models_map:
                        cursor.execute("""
                            INSERT INTO camera_models (
                                model_name, equipment_designation, equipment_nature, category, sub_category, low_stock_threshold
                            ) VALUES (?, ?, ?, ?, ?, ?);
                        """, (
                            m_name,
                            item.get("designation") or "كاميرا مراقبة",
                            "IP Camera",
                            "القسم أ",
                            "الفرع 1",
                            5
                        ))
                        new_id = cursor.lastrowid
                        models_map[m_lower] = new_id
                        created_models_count += 1

                imported_serials_count = 0
                for item in items:
                    s_num = item.get("serial_number", "").strip()
                    m_name = item.get("model_name", "").strip().lower()
                    m_id = models_map.get(m_name)
                    if not s_num or not m_id:
                        continue

                    cursor.execute("SELECT 1 FROM serial_numbers WHERE serial_number = ?;", (s_num,))
                    if not cursor.fetchone():
                        cursor.execute(
                            "INSERT INTO serial_numbers (model_id, serial_number, is_used) VALUES (?, ?, 0);",
                            (m_id, s_num)
                        )
                        imported_serials_count += 1

                self.conn.commit()
                return {
                    "success": True,
                    "imported_serials_count": imported_serials_count,
                    "created_models_count": created_models_count
                }

            elif mode == "SERIALS_ONLY":
                if not destination_model_id:
                    return {"success": False, "error": "Modèle de destination obligatoire pour ce type d'import"}
                return self.import_serials_batch(int(destination_model_id), items)

            else:
                return {"success": False, "error": f"Mode d'importation inconnu: {mode}"}

        except Exception as e:
            self.conn.rollback()
            return {"success": False, "error": str(e)}

    @synchronized
    def generate_import_template(self, template_type: str = "catalog") -> bytes:
        """Generate professionally styled sample .xlsx workbooks for catalog or manifest import."""
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.views.sheetView[0].showGridLines = True

        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Segoe UI", size=10)
        thin_border = Border(
            left=Side(style='thin', color="CBD5E1"),
            right=Side(style='thin', color="CBD5E1"),
            top=Side(style='thin', color="CBD5E1"),
            bottom=Side(style='thin', color="CBD5E1")
        )

        if template_type.lower() == "manifest":
            ws.title = "Manifeste Livraison"
            headers = ["Modèle de Caméra *", "Numéro de Série *", "Désignation (Optionnel)"]
            samples = [
                ["Hikvision DS-2CD2143G2-I", "HK-SN-98234101", "كاميرا مراقبة داخلية"],
                ["Hikvision DS-2CD2143G2-I", "HK-SN-98234102", "كاميرا مراقبة داخلية"],
                ["Dahua IPC-HDW1230T1", "DH-SN-44321901", "كاميرا مراقبة خارجية"],
                ["Dahua IPC-HDW1230T1", "DH-SN-44321902", "كاميرا مراقبة خارجية"]
            ]
        else:
            ws.title = "Catalogue Modèles"
            headers = ["Modèle *", "Désignation (Annexe 1)", "Nature (Annexe 1)", "Section (القسم)", "Sous-section (الفرع)", "Seuil Stock"]
            samples = [
                ["Hikvision DS-2CD2043G2-I", "كاميرا مراقبة خارجية", "IP Bullet 4MP", "القسم أ", "الفرع 1", 5],
                ["Dahua IPC-HFW2431S-S-S2", "كاميرا مراقبة بالأشعة تحت الحمراء", "IP Bullet IR", "القسم ب", "الفرع 2", 8],
                ["Uniview IPC2124LR3-PF40M", "كاميرا شبكية بدقة 4 ميغابكسل", "Network Dome", "القسم أ", "الفرع 1", 5]
            ]

        # Write Headers
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        # Write Samples
        for row_data in samples:
            ws.append(row_data)
            current_row = ws.max_row
            ws.row_dimensions[current_row].height = 20
            for col_idx in range(1, len(row_data) + 1):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.font = data_font
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 5, 16)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream.read()

    # ------------------------------------------------------------------ #
    #  Database Backup & Restore Engine
    # ------------------------------------------------------------------ #
    @synchronized
    def create_database_backup(self, destination_path: str = None) -> dict:
        """
        Create a non-blocking atomic backup of the SQLite database.
        Default location: backups/cctv_backup_YYYYMMDD_HHMMSS.db
        """
        import datetime
        try:
            now = datetime.datetime.now()
            ts_str = now.strftime("%Y%m%d_%H%M%S")
            ts_display = now.strftime("%d/%m/%Y %H:%M:%S")

            if destination_path and str(destination_path).strip():
                dest = os.path.abspath(str(destination_path).strip())
            else:
                backup_dir = os.path.abspath("backups")
                os.makedirs(backup_dir, exist_ok=True)
                dest = os.path.join(backup_dir, f"cctv_backup_{ts_str}.db")

            os.makedirs(os.path.dirname(dest), exist_ok=True)

            target_conn = sqlite3.connect(dest)
            try:
                with target_conn:
                    self.conn.backup(target_conn)
            finally:
                target_conn.close()

            file_size = os.path.getsize(dest)
            size_kb = round(file_size / 1024, 1)

            # Persist backup metadata
            self.set_setting("last_backup_timestamp", ts_display)
            self.set_setting("last_backup_file", dest)

            return {
                "success": True,
                "file_path": dest,
                "filename": os.path.basename(dest),
                "file_size_kb": size_kb,
                "timestamp": ts_display
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @synchronized
    def restore_database_from_backup(self, source_path: str) -> dict:
        """
        Restore the database from an existing backup file.
        Includes pre-flight integrity check, schema validation, and automatic safety backup.
        """
        import datetime
        if not source_path or not os.path.exists(source_path):
            return {"success": False, "error": "Fichier de sauvegarde introuvable"}

        clean_src = os.path.abspath(source_path)

        # Step 1: Pre-flight integrity check
        try:
            test_conn = sqlite3.connect(clean_src)
            try:
                cur = test_conn.cursor()
                cur.execute("PRAGMA integrity_check;")
                chk = cur.fetchone()
                if not chk or chk[0] != "ok":
                    return {"success": False, "error": f"Fichier corrompu: {chk[0] if chk else 'Échec du contrôle d\'intégrité'}"}

                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = {row[0].lower() for row in cur.fetchall()}
                required_tables = {"camera_models", "clients", "serial_numbers", "client_purchases"}
                if not required_tables.issubset(tables):
                    missing = required_tables - tables
                    return {"success": False, "error": f"Base de données incompatible (tables manquantes: {', '.join(missing)})"}
            finally:
                test_conn.close()
        except Exception as e:
            return {"success": False, "error": f"Fichier SQLite invalide ou illisible: {str(e)}"}

        # Step 2: Create pre-restore safety snapshot of active database
        now = datetime.datetime.now()
        ts_str = now.strftime("%Y%m%d_%H%M%S")
        safety_dir = os.path.abspath("backups")
        os.makedirs(safety_dir, exist_ok=True)
        safety_path = os.path.join(safety_dir, f"pre_restore_safety_{ts_str}.db")

        try:
            safety_conn = sqlite3.connect(safety_path)
            try:
                with safety_conn:
                    self.conn.backup(safety_conn)
            finally:
                safety_conn.close()
        except Exception:
            pass

        # Step 3: Perform atomic in-place restore into active connection
        try:
            source_conn = sqlite3.connect(clean_src)
            try:
                with self.conn:
                    source_conn.backup(self.conn)
            finally:
                source_conn.close()

            # Step 4: Ensure schema migrations and trigger checks run
            self.initialize_db()

            return {
                "success": True,
                "source_path": clean_src,
                "safety_backup": safety_path
            }
        except Exception as e:
            return {"success": False, "error": f"Erreur lors de la restauration: {str(e)}"}

    @synchronized
    def auto_backup_on_startup(self, max_backups: int = 7) -> dict:
        """
        Automatic rolling daily backup on application launch.
        Retains up to max_backups daily snapshots to prevent disk bloat.
        """
        import datetime
        try:
            backup_dir = os.path.abspath("backups")
            os.makedirs(backup_dir, exist_ok=True)
            today_prefix = datetime.date.today().strftime("auto_backup_%Y%m%d")

            # Check if today's auto-backup already exists
            existing_today = [f for f in os.listdir(backup_dir) if f.startswith(today_prefix) and f.endswith(".db")]
            if existing_today:
                return {"success": True, "already_created": True, "file": existing_today[0]}

            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_file = os.path.join(backup_dir, f"auto_backup_{now_str}.db")
            res = self.create_database_backup(destination_path=auto_file)

            # Prune older auto-backups
            auto_backups = sorted(
                [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith("auto_backup_") and f.endswith(".db")],
                key=os.path.getmtime,
                reverse=True
            )
            if len(auto_backups) > max_backups:
                for old_b in auto_backups[max_backups:]:
                    try:
                        os.remove(old_b)
                    except OSError:
                        pass

            return res
        except Exception as e:
            return {"success": False, "error": str(e)}

    @synchronized
    def get_backup_status(self) -> dict:
        """Return metadata about backups directory and last backup timestamp."""
        last_ts = self.get_setting("last_backup_timestamp", "Jamais")
        backup_dir = os.path.abspath("backups")
        count = 0
        total_size = 0
        if os.path.exists(backup_dir):
            for f in os.listdir(backup_dir):
                if f.endswith(".db") or f.endswith(".bak"):
                    count += 1
                    try:
                        total_size += os.path.getsize(os.path.join(backup_dir, f))
                    except OSError:
                        pass
        return {
            "last_backup_timestamp": last_ts,
            "total_backups_count": count,
            "total_size_kb": round(total_size / 1024, 1),
            "backups_dir": backup_dir
        }

    # ------------------------------------------------------------------ #
    #  Installer Profile & Seal/Signature Settings
    # ------------------------------------------------------------------ #
    @synchronized
    def get_installer_profile(self) -> dict:
        """Fetch installer company information, accreditation, agreement document, and digital seal/signature."""
        return {
            "company_name": self.get_setting("installer_company_name", ""),
            "installer_name": self.get_setting("installer_name", ""),
            "phone": self.get_setting("installer_phone", ""),
            "city": self.get_setting("installer_city", ""),
            "accreditation_ref": self.get_setting("installer_accreditation_ref", ""),
            "accreditation_date": self.get_setting("installer_accreditation_date", ""),
            "agreement_doc_b64": self.get_setting("installer_agreement_doc_b64", ""),
            "agreement_doc_name": self.get_setting("installer_agreement_doc_name", ""),
            "seal_image_b64": self.get_setting("installer_seal_b64", ""),
            "signature_image_b64": self.get_setting("installer_signature_b64", ""),
            "enabled": self.get_setting("installer_seal_enabled", "1") == "1"
        }

    @synchronized
    def save_installer_profile(self, data: dict) -> bool:
        """Save installer company information, accreditation, agreement document, and digital seal/signature."""
        try:
            if not isinstance(data, dict):
                return False
            if "company_name" in data:
                self.set_setting("installer_company_name", str(data["company_name"]).strip())
            if "installer_name" in data:
                self.set_setting("installer_name", str(data["installer_name"]).strip())
            if "phone" in data:
                self.set_setting("installer_phone", str(data["phone"]).strip())
            if "city" in data:
                self.set_setting("installer_city", str(data["city"]).strip())
            if "accreditation_ref" in data:
                self.set_setting("installer_accreditation_ref", str(data["accreditation_ref"]).strip())
            if "accreditation_date" in data:
                self.set_setting("installer_accreditation_date", str(data["accreditation_date"]).strip())
            if "agreement_doc_b64" in data:
                self.set_setting("installer_agreement_doc_b64", str(data["agreement_doc_b64"] or ""))
            if "agreement_doc_name" in data:
                self.set_setting("installer_agreement_doc_name", str(data["agreement_doc_name"] or ""))
            if "seal_image_b64" in data:
                self.set_setting("installer_seal_b64", str(data["seal_image_b64"] or ""))
            if "signature_image_b64" in data:
                self.set_setting("installer_signature_b64", str(data["signature_image_b64"] or ""))
            if "enabled" in data:
                self.set_setting("installer_seal_enabled", "1" if data["enabled"] else "0")
            return True
        except Exception:
            return False
