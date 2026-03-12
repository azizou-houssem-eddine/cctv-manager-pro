import sqlite3
import os

class DatabaseManager:
    """Manages all database operations for the CCTV Manager application."""

    def __init__(self, db_path: str = "cctv_manager.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row

    # ------------------------------------------------------------------ #
    #  Schema
    # ------------------------------------------------------------------ #
    def initialize_db(self) -> None:
        """Create all tables if they do not already exist and migrate schema."""
        cursor = self.conn.cursor()
        
        # 1. Base Tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS camera_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                equipment_designation TEXT,
                equipment_nature TEXT,
                category TEXT,
                sub_category TEXT
            );
        """)

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
                security_conditions TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS serial_numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                serial_number TEXT UNIQUE,
                is_used BOOLEAN DEFAULT 0,
                FOREIGN KEY (model_id) REFERENCES camera_models(id)
            );
        """)

        # NEW TABLE: Links a client to a specific purchased camera
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                serial_id INTEGER UNIQUE,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(serial_id) REFERENCES serial_numbers(id)
            );
        """)

        # Migration section for dynamic columns
        # Camera models migration
        cursor.execute("PRAGMA table_info(camera_models)")
        existing_cm = [row[1] for row in cursor.fetchall()]
        cm_cols = [
            ("model_name", "TEXT"), ("equipment_designation", "TEXT"), 
            ("equipment_nature", "TEXT"), ("category", "TEXT"), ("sub_category", "TEXT")
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
            ("security_conditions", "TEXT")
        ]
        for col, typ in cl_cols:
            if col not in existing_cl and existing_cl:
                cursor.execute(f"ALTER TABLE clients ADD COLUMN {col} {typ};")

        self.conn.commit()

    # ------------------------------------------------------------------ #
    #  Seed Data
    # ------------------------------------------------------------------ #
    def seed_dummy_data(self) -> None:
        """Production: No dummy data seeded."""
        pass

    # ------------------------------------------------------------------ #
    #  Queries & Actions
    # ------------------------------------------------------------------ #
    def get_camera_models(self) -> list[dict]:
        """Return all camera models as a list of dicts."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM camera_models;")
        return [dict(row) for row in cursor.fetchall()]

    def add_camera_model(self, model_name: str, equipment_designation: str, equipment_nature: str, category: str, sub_category: str) -> bool:
        """Insert a new camera model into the database."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO camera_models (model_name, equipment_designation, equipment_nature, category, sub_category) VALUES (?, ?, ?, ?, ?);",
                (model_name, equipment_designation, equipment_nature, category, sub_category)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_clients(self) -> list[dict]:
        """Return all clients as a list of dicts."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients;")
        return [dict(row) for row in cursor.fetchall()]

    def add_client(self, client_data: dict) -> bool:
        """Insert a new client into the database using a dictionary of fields."""
        cursor = self.conn.cursor()
        fields = [
            "full_name", "father_name", "mother_name", "dob", "pob", "nationality",
            "doc_number", "doc_issuer", "doc_issue_date", "address", "city", "phone",
            "email", "fax", "profession", "activity_type", "company_name", "company_hq",
            "position", "accreditation_ref", "origin_country", "import_country",
            "transport_method", "storage_location", "security_conditions"
        ]
        
        # Filter data to only include valid fields that are present
        present_fields = [f for f in fields if f in client_data]
        placeholders = ", ".join(["?"] * len(present_fields))
        columns = ", ".join(present_fields)
        values = [client_data[f] for f in present_fields]
        
        query = f"INSERT INTO clients ({columns}) VALUES ({placeholders});"
        
        try:
            cursor.execute(query, tuple(values))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_client(self, client_id: int, client_data: dict) -> bool:
        """Update an existing client's info."""
        cursor = self.conn.cursor()
        fields = [
            "full_name", "father_name", "mother_name", "dob", "pob", "nationality",
            "doc_number", "doc_issuer", "doc_issue_date", "address", "city", "phone",
            "email", "fax", "profession", "activity_type", "company_name", "company_hq",
            "position", "accreditation_ref", "origin_country", "import_country",
            "transport_method", "storage_location", "security_conditions"
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
        except sqlite3.Error:
            return False

    def get_client(self, client_id: int) -> dict:
        """Return a single client by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?;", (client_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def save_serial_batch(self, model_id: int, serials: list[str]) -> int:
        """Insert a batch of serial numbers for a given model."""
        cursor = self.conn.cursor()
        inserted = 0
        for sn in serials:
            try:
                cursor.execute(
                    "INSERT INTO serial_numbers (model_id, serial_number) "
                    "VALUES (?, ?);",
                    (model_id, sn),
                )
                inserted = inserted + 1
            except sqlite3.IntegrityError:
                pass
        self.conn.commit()
        return inserted

    def get_available_serials(self, model_id: int) -> list[dict]:
        """Return unused serial numbers for a specific camera model."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, serial_number FROM serial_numbers WHERE model_id = ? AND is_used = 0;",
            (model_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all_serials(self, model_id: int) -> list[dict]:
        """Return all serial numbers (used and unused) for a specific camera model."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, serial_number, is_used FROM serial_numbers WHERE model_id = ? ORDER BY id DESC;",
            (model_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def is_serial_exists(self, serial_number: str) -> bool:
        """Check if a serial number already exists in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM serial_numbers WHERE serial_number = ? LIMIT 1;", (serial_number,))
        return cursor.fetchone() is not None

    def assign_camera_to_client(self, client_id: int, serial_id: int) -> bool:
        """Assign a camera to a client and mark the serial as used."""
        cursor = self.conn.cursor()
        try:
            # 1. Record the purchase
            cursor.execute(
                "INSERT INTO client_purchases (client_id, serial_id) VALUES (?, ?);",
                (client_id, serial_id)
            )
            # 2. Mark the serial number as used
            cursor.execute(
                "UPDATE serial_numbers SET is_used = 1 WHERE id = ?;",
                (serial_id,)
            )
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    def get_client_purchases_for_pdf(self, client_id: int) -> dict:
        """Fetch client details and all their assigned cameras for the PDF forms."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM clients WHERE id = ?;", (client_id,))
        client_row = cursor.fetchone()
        if not client_row:
            return {"client": None, "cameras": []}
            
        client = dict(client_row)
        
        cursor.execute("""
            SELECT 
                cm.model_name, cm.equipment_designation, cm.equipment_nature, cm.category, cm.sub_category, sn.serial_number
            FROM client_purchases cp
            JOIN serial_numbers sn ON cp.serial_id = sn.id
            JOIN camera_models cm ON sn.model_id = cm.id
            WHERE cp.client_id = ?;
        """, (client_id,))
        
        cameras = [dict(row) for row in cursor.fetchall()]
        
        return {
            "client": client,
            "cameras": cameras
        }

    def clear_database(self) -> bool:
        """Truncate all tables (useful for maintenance). Returns True on success."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM client_purchases;")
            cursor.execute("DELETE FROM serial_numbers;")
            cursor.execute("DELETE FROM clients;")
            cursor.execute("DELETE FROM camera_models;")
            self.conn.commit()
            return True
        except sqlite3.Error:
            self.conn.rollback()
            return False

    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  Lifecycle
    # ------------------------------------------------------------------ #
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()