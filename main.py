import os
import sys

# 1. SET API BEFORE ANY QT IMPORTS
os.environ["QT_API"] = "PyQt6"

# 2. CORE IMPORTS & CONFIG
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import QApplication

# High DPI policy MUST be set before QApplication instantiation
try:
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
except AttributeError:
    pass

# 3. IMMEDIATE ENGINE STARTUP
app = QApplication(sys.argv)

# 4. DELAYED IMPORTS
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qfluentwidgets import (FluentWindow, SubtitleLabel, LineEdit, ComboBox, 
                            PrimaryPushButton, TableWidget, NavigationItemPosition,
                            MessageBox, DateEdit, SearchLineEdit, setTheme, Theme, 
                            CardWidget, PushButton, FluentIcon, InfoBar, InfoBarPosition,
                            ScrollArea, CheckBox)

from db_manager import DatabaseManager
from pdf_generator import PDFGenerator

# 5. TRANSLATIONS
TRANSLATIONS = {
    'fr': {
        'nav_inventory': 'Inventaire',
        'nav_clients': 'Clients',
        'nav_settings': 'Paramètres',
        'scan_equipment': 'Scanner Équipement',
        'select_model': 'Sélectionner Modèle',
        'scan_placeholder': 'Scanner ici (Entrée)...',
        'staged_batch': 'Lot en attente',
        'save': 'Enregistrer',
        'clear': 'Effacer',
        'existing_db': 'Existant dans la base',
        'serial_num': 'N° de Série',
        'status': 'État',
        'in_stock': 'En Stock',
        'assigned': 'Assigné',
        'register_client': 'Enregistrer Nouveau Client',
        'edit_client': 'Modifier Client ID: ',
        'identity': 'Identité',
        'full_name': 'Nom Complet: *',
        'father_name': 'Nom du Père:',
        'mother_name': 'Nom de la Mère:',
        'dob': 'Date de Naissance:',
        'pob': 'Lieu de Naissance:',
        'nationality': 'Nationalité:',
        'documents': 'Documents',
        'doc_num': 'N° ID/Passeport: *',
        'doc_issuer': 'Délivré par:',
        'doc_date': 'Date de délivrance:',
        'corporate': 'Entreprise',
        'address': 'Adresse:',
        'city': 'Ville:',
        'phone': 'Téléphone:',
        'email': 'Email:',
        'fax': 'Fax:',
        'company_name': 'Nom de l\'entreprise:',
        'company_hq': 'Siège social:',
        'position': 'Poste:',
        'profession': 'Profession:',
        'activity_type': 'Type d\'activité:',
        'logistics': 'Logistique (Annexe 1)',
        'acc_ref': 'Réf. Accréditation:',
        'origin_country': 'Pays d\'origine:',
        'import_country': 'Pays d\'importation:',
        'trans_method': 'Méthode de transport:',
        'storage_loc': 'Lieu de stockage/usage:',
        'security_cond': 'Conditions de sécurité:',
        'save_client': 'Enregistrer Client',
        'update_client': 'Mettre à jour Client',
        'search_client': 'Rechercher par Nom ou ID...',
        'id': 'ID',
        'edit': 'Modifier',
        'assign_camera': 'Assigner Caméra',
        'return_camera': 'Retour Caméra',
        'first_dossier': '1er dossier',
        'catalog_mgmt': 'Gestion du Catalogue Caméras',
        'int_model_name': 'Marque & Modèle',
        'equip_desig': 'Désignation (Annex 1 Col 1)',
        'equip_nature': 'Nature (Annex 1 Col 2)',
        'category': 'Section (Annex 1 Col 3)',
        'sub_category': 'Sous-section (Annex 1 Col 4)',
        'add_model': 'Ajouter Modèle',
        'registered_models': 'Modèles Enregistrés',
        'lang_settings': 'Paramètres de Langue',
        'select_lang': 'Choisir Langue:',
        'success': 'Succès',
        'error': 'Erreur',
        'warning': 'Attention',
        'client_saved': 'Client enregistré avec succès.',
        'client_updated': 'Client mis à jour avec succès.',
        'validation_error': 'Nom Complet et N° de Document sont requis!',
        'assignment_success': 'Caméra(s) assignée(s) avec succès.',
        'pdf_generated': 'Dossier généré avec succès.',
        'maintenance': 'Maintenance',
        'clear_db': 'Vider la Base de Données',
        'confirm_title': 'Confirmation',
        'confirm_clear_msg': 'Voulez-vous vraiment supprimer TOUTES les données ? Cette action est irréversible.',
        'db_cleared': 'Succès',
        'db_cleared_msg': 'La base de données a été vidée.',
    },
    'ar': {
        'nav_inventory': 'المخزون',
        'nav_clients': 'العملاء',
        'nav_settings': 'الإعدادات',
        'scan_equipment': 'مسح المعدات',
        'select_model': 'اختر الطراز',
        'scan_placeholder': 'امسح هنا (اضغط Enter)...',
        'staged_batch': 'الدفعة المنتظرة',
        'save': 'حفظ',
        'clear': 'مسح',
        'existing_db': 'موجود في القاعدة',
        'serial_num': 'الرقم التسلسلي',
        'status': 'الحالة',
        'in_stock': 'متوفر',
        'assigned': 'مخصص',
        'register_client': 'تسجيل عميل جديد',
        'edit_client': 'تعديل العميل رقم: ',
        'identity': 'الهوية',
        'full_name': 'الاسم الكامل: *',
        'father_name': 'اسم الأب:',
        'mother_name': 'اسم الأم:',
        'dob': 'تاريخ الميلاد:',
        'pob': 'مكان الميلاد:',
        'nationality': 'الجنسية:',
        'documents': 'الوثائق',
        'doc_num': 'رقم الهوية/الجواز: *',
        'doc_issuer': 'جهة الإصدار:',
        'doc_date': 'تاريخ الإصدار:',
        'corporate': 'الشركة',
        'address': 'العنوان:',
        'city': 'المدينة:',
        'phone': 'الهاتف:',
        'email': 'البريد الإلكتروني:',
        'fax': 'الفاكس:',
        'company_name': 'اسم الشركة:',
        'company_hq': 'مقر الشركة:',
        'position': 'المصب:',
        'profession': 'المهنة:',
        'activity_type': 'نوع النشاط:',
        'logistics': 'اللوجستيات (الملحق 1)',
        'acc_ref': 'مرجع الاعتماد:',
        'origin_country': 'بلد المنشأ:',
        'import_country': 'بلد الاستيراد:',
        'trans_method': 'طريقة النقل:',
        'storage_loc': 'مكان التخزين/الاستخدام:',
        'security_cond': 'شروط الأمن:',
        'save_client': 'حفظ العميل',
        'update_client': 'تحديث العميل',
        'search_client': 'بحث بالاسم أو الرقم...',
        'id': 'رقم',
        'edit': 'تعديل',
        'assign_camera': 'تخصيص كاميرا',
        'return_camera': 'إرجاع كاميرا',
        'first_dossier': 'الملف الأول',
        'catalog_mgmt': 'إدارة كتالوج الكاميرات',
        'int_model_name': 'العلامة والنموذج',
        'equip_desig': 'تعيين التجهيزات',
        'equip_nature': 'طبيعة التجهيزات',
        'category': 'القسم',
        'sub_category': 'القسم الفرعي',
        'add_model': 'إضافة طراز',
        'registered_models': 'الموديلات المسجلة',
        'lang_settings': 'إعدادات اللغة',
        'select_lang': 'اختر اللغة:',
        'success': 'تم بنجاح',
        'error': 'خطأ',
        'warning': 'تحذير',
        'client_saved': 'تم حفظ العميل بنجاح.',
        'client_updated': 'تم تحديث العميل بنجاح.',
        'validation_error': 'الاسم الكامل ورقم الوثيقة مطلوبان!',
        'assignment_success': 'تم تخصيص الكاميرا بنجاح.',
        'pdf_generated': 'تم إنشاء الملف بنجاح.'
    }
}

CURRENT_LANG = 'fr'

def t(key):
    return TRANSLATIONS[CURRENT_LANG].get(key, key)

class InventoryInterface(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self.setObjectName("InventoryInterface")
        self.staged_serials = []

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(24, 24, 24, 24)

        # Top Card: Scanning Input
        self.inputCard = CardWidget(self)
        self.inputLayout = QVBoxLayout(self.inputCard)
        self.inputLayout.setContentsMargins(20, 20, 20, 20)

        self.scanTitle = SubtitleLabel(t('scan_equipment'), self.inputCard)
        self.inputLayout.addWidget(self.scanTitle)

        inputParamsLayout = QHBoxLayout()
        self.modelCombo = ComboBox(self.inputCard)
        self.modelCombo.setMinimumWidth(300)
        self.modelCombo.setPlaceholderText(t('select_model'))
        self.scannerInput = LineEdit(self.inputCard)
        self.scannerInput.setPlaceholderText(t('scan_placeholder'))
        self.scannerInput.returnPressed.connect(self.handle_scan)
        
        inputParamsLayout.addWidget(self.modelCombo)
        inputParamsLayout.addWidget(self.scannerInput, 1)
        self.inputLayout.addLayout(inputParamsLayout)

        self.vBoxLayout.addWidget(self.inputCard)

        # Bottom Area: Two Tables
        self.tablesLayout = QHBoxLayout()
        
        # Staged List Card
        self.stagedCard = CardWidget(self)
        self.stagedLayout = QVBoxLayout(self.stagedCard)
        self.stagedLayout.setContentsMargins(20, 20, 20, 20)
        
        stagedHeader = QHBoxLayout()
        self.stagedLabel = SubtitleLabel(t('staged_batch'), self.stagedCard)
        stagedHeader.addWidget(self.stagedLabel)
        stagedHeader.addStretch(1)
        self.btnSaveBatch = PrimaryPushButton(t('save'), self.stagedCard)
        self.btnSaveBatch.clicked.connect(self.save_scanned_batch)
        self.btnClearBatch = PushButton(t('clear'), self.stagedCard)
        self.btnClearBatch.clicked.connect(self.clear_staged)
        stagedHeader.addWidget(self.btnSaveBatch)
        stagedHeader.addWidget(self.btnClearBatch)
        self.stagedLayout.addLayout(stagedHeader)

        self.stagedTable = TableWidget(self.stagedCard)
        self.stagedTable.setColumnCount(1)
        self.stagedTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.stagedTable.setHorizontalHeaderLabels([t('serial_num')])
        self.stagedTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.stagedLayout.addWidget(self.stagedTable)
        self.tablesLayout.addWidget(self.stagedCard, 1)

        # Existing Inventory List Card
        self.inventoryCard = CardWidget(self)
        self.inventoryLayout = QVBoxLayout(self.inventoryCard)
        self.inventoryLayout.setContentsMargins(20, 20, 20, 20)
        
        self.existingLabel = SubtitleLabel(t('existing_db'), self.inventoryCard)
        self.inventoryLayout.addWidget(self.existingLabel)
        self.inventoryTable = TableWidget(self.inventoryCard)
        self.inventoryTable.setColumnCount(2)
        self.inventoryTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.inventoryTable.setHorizontalHeaderLabels([t('serial_num'), t('status')])
        self.inventoryTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.inventoryLayout.addWidget(self.inventoryTable)
        self.tablesLayout.addWidget(self.inventoryCard, 1)

        self.vBoxLayout.addLayout(self.tablesLayout, 1)
        
        self.modelCombo.currentTextChanged.connect(self.refresh_inventory_table)
        self.refresh_scanner_models()
        self.refresh_inventory_table()

    def update_ui_texts(self):
        self.scanTitle.setText(t('scan_equipment'))
        self.modelCombo.setPlaceholderText(t('select_model'))
        self.scannerInput.setPlaceholderText(t('scan_placeholder'))
        self.stagedLabel.setText(t('staged_batch'))
        self.btnSaveBatch.setText(t('save'))
        self.btnClearBatch.setText(t('clear'))
        self.existingLabel.setText(t('existing_db'))
        self.stagedTable.setHorizontalHeaderLabels([t('serial_num')])
        self.inventoryTable.setHorizontalHeaderLabels([t('serial_num'), t('status')])
        self.refresh_inventory_table()

    def get_model_names(self):
        models = self.db.get_camera_models()
        if not models:
            return [t('warning') + ": No models"]
        return [f"{m['id']} - {m['model_name']}" for m in models]

    def refresh_scanner_models(self):
        self.modelCombo.clear()
        self.modelCombo.addItems(self.get_model_names())

    def refresh_inventory_table(self):
        self.inventoryTable.setRowCount(0)
        model_str = self.modelCombo.text()
        if not model_str or "No models" in model_str:
            return
        
        try:
            mid = int(model_str.split(" - ")[0])
            serials = self.db.get_all_serials(mid)
            for s in serials:
                row = self.inventoryTable.rowCount()
                self.inventoryTable.insertRow(row)
                self.inventoryTable.setItem(row, 0, QTableWidgetItem(s["serial_number"]))
                status_text = t('in_stock') if not s["is_used"] else t('assigned')
                self.inventoryTable.setItem(row, 1, QTableWidgetItem(status_text))
        except:
            pass

    def update_staged_list_ui(self):
        self.stagedTable.setRowCount(0)
        for serial in reversed(self.staged_serials):
            row = self.stagedTable.rowCount()
            self.stagedTable.insertRow(row)
            self.stagedTable.setItem(row, 0, QTableWidgetItem(serial))

    def handle_scan(self):
        text = self.scannerInput.text().strip()
        if not text: return
        model_str = self.modelCombo.text()
        if not model_str or "No models" in model_str:
            InfoBar.warning(t('warning'), t('select_model'), parent=self, position=InfoBarPosition.TOP)
            return
        if text in self.staged_serials:
            InfoBar.warning(t('warning'), f"Duplicate: {text}", parent=self, position=InfoBarPosition.TOP)
            self.scannerInput.clear()
            return
        if self.db.is_serial_exists(text):
            InfoBar.error(t('error'), f"Serial exists: {text}", parent=self, position=InfoBarPosition.TOP)
            self.scannerInput.clear()
            return
        self.staged_serials.append(text)
        self.scannerInput.clear()
        self.update_staged_list_ui()

    def clear_staged(self):
        self.staged_serials.clear()
        self.update_staged_list_ui()

    def save_scanned_batch(self):
        if not self.staged_serials: return
        model_str = self.modelCombo.text()
        try:
            model_id = int(model_str.split(" - ")[0])
            self.db.save_serial_batch(model_id, self.staged_serials)
            count = len(self.staged_serials)
            self.clear_staged()
            self.refresh_inventory_table()
            InfoBar.success(t('success'), f"Saved {count}!", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error(t('error'), str(e), parent=self, position=InfoBarPosition.TOP)

class AssignCameraDialog(MessageBox):
    def __init__(self, db, parent=None):
        super().__init__(t('assign_camera'), "", parent)
        self.db = db
        self.all_serials = []
        self.container = QWidget()
        self.containerLayout = QVBoxLayout(self.container)
        
        self.lblModel = SubtitleLabel(t('select_model'), self.container)
        self.containerLayout.addWidget(self.lblModel)
        self.modelCombo = ComboBox(self.container)
        self.modelCombo.setMinimumWidth(350)
        self.containerLayout.addWidget(self.modelCombo)

        self.lblSerials = SubtitleLabel(t('serial_num'), self.container)
        self.containerLayout.addWidget(self.lblSerials)
        self.searchBar = SearchLineEdit(self.container)
        self.searchBar.setPlaceholderText(t('search_client'))
        self.searchBar.textChanged.connect(self.filter_serials)
        self.containerLayout.addWidget(self.searchBar)

        self.serialTable = TableWidget(self.container)
        self.serialTable.setColumnCount(2)
        self.serialTable.setHorizontalHeaderLabels(["", t('serial_num')])
        self.serialTable.setColumnWidth(0, 50)
        self.serialTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.serialTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.serialTable.setMinimumHeight(300)
        self.containerLayout.addWidget(self.serialTable)

        ctrlLayout = QHBoxLayout()
        self.btnAll = PushButton("Select All", self.container)
        self.btnNone = PushButton("Clear All", self.container)
        self.btnAll.clicked.connect(lambda: self.set_all_checked(True))
        self.btnNone.clicked.connect(lambda: self.set_all_checked(False))
        ctrlLayout.addWidget(self.btnAll)
        ctrlLayout.addWidget(self.btnNone)
        ctrlLayout.addStretch(1)
        self.containerLayout.addLayout(ctrlLayout)

        layout = getattr(self, 'viewLayout', getattr(self, 'vBoxLayout', None))
        if layout: layout.insertWidget(min(layout.count(), 2), self.container)
        
        self.modelCombo.currentTextChanged.connect(self.refresh_serials)
        self.refresh_models()
        self.widget.setMinimumWidth(500)

    def refresh_models(self):
        models = self.db.get_camera_models()
        self.modelCombo.clear()
        if not models: self.modelCombo.addItems(["No models"])
        else: self.modelCombo.addItems([f"{m['id']} - {m['model_name']}" for m in models])

    def refresh_serials(self):
        model_str = self.modelCombo.text()
        self.all_serials = []
        if not model_str or "No" in model_str:
            self.display_serials([])
            return
        try:
            mid = int(model_str.split(" - ")[0])
            self.all_serials = self.db.get_available_serials(mid)
            self.filter_serials()
        except: self.display_serials([])

    def filter_serials(self):
        query = self.searchBar.text().lower()
        filtered = [s for s in self.all_serials if query in s["serial_number"].lower()]
        self.display_serials(filtered)

    def display_serials(self, serials):
        self.serialTable.setRowCount(0)
        for s in serials:
            row = self.serialTable.rowCount()
            self.serialTable.insertRow(row)
            cb = CheckBox(self.serialTable)
            cb.setProperty("sid", s["id"])
            cb.setFixedWidth(30)
            hlayout = QHBoxLayout()
            hlayout.addWidget(cb)
            hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hlayout.setContentsMargins(0, 0, 0, 0)
            container = QWidget()
            container.setLayout(hlayout)
            self.serialTable.setCellWidget(row, 0, container)
            self.serialTable.setItem(row, 1, QTableWidgetItem(s["serial_number"]))

    def set_all_checked(self, checked):
        for i in range(self.serialTable.rowCount()):
            c = self.serialTable.cellWidget(i,0)
            if c:
                cb = c.findChild(CheckBox)
                if cb: cb.setChecked(checked)

    def get_selected_ids(self):
        ids = []
        for i in range(self.serialTable.rowCount()):
            c = self.serialTable.cellWidget(i, 0)
            if c:
                cb = c.findChild(CheckBox)
                if cb and cb.isChecked(): ids.append(cb.property("sid"))
        return ids

class ReturnCameraDialog(MessageBox):
    def __init__(self, assigned_cameras, parent=None):
        super().__init__(t('return_camera'), "", parent)
        self.assigned_cameras = assigned_cameras
        self.container = QWidget()
        self.containerLayout = QVBoxLayout(self.container)
        
        self.lblTitle = SubtitleLabel("Select Cameras to Return", self.container)
        self.containerLayout.addWidget(self.lblTitle)

        self.serialTable = TableWidget(self.container)
        self.serialTable.setColumnCount(3)
        self.serialTable.setHorizontalHeaderLabels(["", t('serial_num'), t('int_model_name')])
        self.serialTable.setColumnWidth(0, 50)
        self.serialTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.serialTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.serialTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.serialTable.setMinimumHeight(300)
        self.containerLayout.addWidget(self.serialTable)

        ctrlLayout = QHBoxLayout()
        self.btnAll = PushButton("Select All", self.container)
        self.btnNone = PushButton("Clear All", self.container)
        self.btnAll.clicked.connect(lambda: self.set_all_checked(True))
        self.btnNone.clicked.connect(lambda: self.set_all_checked(False))
        ctrlLayout.addWidget(self.btnAll)
        ctrlLayout.addWidget(self.btnNone)
        ctrlLayout.addStretch(1)
        self.containerLayout.addLayout(ctrlLayout)

        layout = getattr(self, 'viewLayout', getattr(self, 'vBoxLayout', None))
        if layout: layout.insertWidget(min(layout.count(), 2), self.container)
        
        self.display_serials(self.assigned_cameras)
        self.widget.setMinimumWidth(600)

    def display_serials(self, serials):
        self.serialTable.setRowCount(0)
        for s in serials:
            row = self.serialTable.rowCount()
            self.serialTable.insertRow(row)
            cb = CheckBox(self.serialTable)
            # Find the serial_id. In get_client_purchases_for_pdf, we get serial_number but not serial_id directly in the dict?
            # Wait, I need serial_id for the database operations. Let me check db_manager.py get_client_purchases_for_pdf
            # It returns serial_number, but I might need the primary key.
            cb.setProperty("sn", s["serial_number"])
            cb.setFixedWidth(30)
            hlayout = QHBoxLayout()
            hlayout.addWidget(cb)
            hlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hlayout.setContentsMargins(0, 0, 0, 0)
            container = QWidget()
            container.setLayout(hlayout)
            self.serialTable.setCellWidget(row, 0, container)
            self.serialTable.setItem(row, 1, QTableWidgetItem(s["serial_number"]))
            self.serialTable.setItem(row, 2, QTableWidgetItem(s.get("model_name", "")))

    def set_all_checked(self, checked):
        for i in range(self.serialTable.rowCount()):
            c = self.serialTable.cellWidget(i, 0)
            if c:
                cb = c.findChild(CheckBox)
                if cb: cb.setChecked(checked)

    def get_selected_serials(self):
        serials = []
        for i in range(self.serialTable.rowCount()):
            c = self.serialTable.cellWidget(i, 0)
            if c:
                cb = c.findChild(CheckBox)
                if cb and cb.isChecked(): serials.append(cb.property("sn"))
        return serials

class ClientInterface(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent=parent)
        self.db = db
        self.setObjectName("ClientInterface")
        self.current_editing_client_id = None
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(24, 24, 24, 24)

        self.formScroll = ScrollArea(self)
        self.formScroll.setWidgetResizable(True)
        self.formScrollWidget = QWidget()
        self.formScroll.setWidget(self.formScrollWidget)
        self.formLayout = QVBoxLayout(self.formScrollWidget)
        self.formLayout.setContentsMargins(20, 20, 20, 20)

        headerLayout = QHBoxLayout()
        self.formTitle = SubtitleLabel(t('register_client'), self.formScrollWidget)
        self.btnClearForm = PushButton(t('clear'), self.formScrollWidget)
        self.btnClearForm.clicked.connect(self.clear_client_form)
        headerLayout.addWidget(self.formTitle); headerLayout.addStretch(1); headerLayout.addWidget(self.btnClearForm)
        self.formLayout.addLayout(headerLayout)

        self.client_entries = {}
        self.sections = []

        def create_section(title_key, fields_list):
            group = CardWidget(self.formScrollWidget)
            layout = QGridLayout(group)
            title_lbl = SubtitleLabel(t(title_key), group)
            layout.addWidget(title_lbl, 0, 0, 1, 2)
            self.sections.append((title_lbl, title_key))
            
            for i, (key, label_key) in enumerate(fields_list):
                lbl = SubtitleLabel(t(label_key), group)
                lbl.setProperty("pixelFontSize", 14)
                entry = DateEdit(group) if "dob" in key or "_date" in key else LineEdit(group)
                layout.addWidget(lbl, i+1, 0); layout.addWidget(entry, i+1, 1)
                self.client_entries[key] = (entry, lbl, label_key)
            self.formLayout.addWidget(group)

        create_section("identity", [("full_name", "full_name"), ("father_name", "father_name"), ("mother_name", "mother_name"), ("dob", "dob"), ("pob", "pob"), ("nationality", "nationality")])
        create_section("documents", [("doc_number", "doc_num"), ("doc_issuer", "doc_issuer"), ("doc_issue_date", "doc_date")])
        create_section("corporate", [("address", "address"), ("city", "city"), ("phone", "phone"), ("email", "email"), ("fax", "fax"), ("company_name", "company_name"), ("company_hq", "company_hq"), ("position", "position"), ("profession", "profession"), ("activity_type", "activity_type")])
        create_section("logistics", [("accreditation_ref", "acc_ref"), ("origin_country", "origin_country"), ("import_country", "import_country"), ("transport_method", "trans_method"), ("storage_location", "storage_loc"), ("security_conditions", "security_cond")])

        self.btnSaveClient = PrimaryPushButton(t('save_client'), self.formScrollWidget)
        self.btnSaveClient.clicked.connect(self.save_client)
        self.formLayout.addWidget(self.btnSaveClient); self.formLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.formScroll, 1)

        self.rightPane = QVBoxLayout()
        self.searchBar = SearchLineEdit(self)
        self.searchBar.setPlaceholderText(t('search_client'))
        self.searchBar.textChanged.connect(self.refresh_client_table)
        self.rightPane.addWidget(self.searchBar)

        self.clientTree = TableWidget(self)
        self.clientTree.setColumnCount(4)
        self.clientTree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.clientTree.setHorizontalHeaderLabels([t('id'), t('full_name').replace(': *',''), t('phone'), t('doc_num').replace(': *','')])
        self.clientTree.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rightPane.addWidget(self.clientTree)

        actionsLayout = QHBoxLayout()
        self.btnEdit = PushButton(t('edit'), self)
        self.btnEdit.clicked.connect(self.load_selected_client_to_form)
        self.btnAssign = PushButton(t('assign_camera'), self)
        self.btnAssign.clicked.connect(self.open_assign_dialog)
        self.btnReturn = PushButton(t('return_camera'), self)
        self.btnReturn.clicked.connect(self.open_return_dialog)
        self.btn1erDossier = PrimaryPushButton(t('first_dossier'), self)
        self.btn1erDossier.clicked.connect(self.generate_combined_pdf)

        actionsLayout.addWidget(self.btnEdit); actionsLayout.addWidget(self.btnAssign); actionsLayout.addWidget(self.btnReturn); actionsLayout.addStretch(1); actionsLayout.addWidget(self.btn1erDossier)
        self.rightPane.addLayout(actionsLayout); self.hBoxLayout.addLayout(self.rightPane, 2)
        self.refresh_client_table()

    def update_ui_texts(self):
        self.formTitle.setText(t('register_client') if not self.current_editing_client_id else t('edit_client') + str(self.current_editing_client_id))
        self.btnClearForm.setText(t('clear'))
        self.btnSaveClient.setText(t('save_client') if not self.current_editing_client_id else t('update_client'))
        self.searchBar.setPlaceholderText(t('search_client'))
        self.clientTree.setHorizontalHeaderLabels([t('id'), t('full_name').replace(': *',''), t('phone'), t('doc_num').replace(': *','')])
        self.btnEdit.setText(t('edit'))
        self.btnAssign.setText(t('assign_camera'))
        self.btnReturn.setText(t('return_camera'))
        self.btn1erDossier.setText(t('first_dossier'))
        for lbl, key in self.sections: lbl.setText(t(key))
        for key, (entry, lbl, lkey) in self.client_entries.items(): 
            lbl.setText(t(lkey))
            if isinstance(entry, LineEdit): entry.setPlaceholderText(t(lkey))
        self.refresh_client_table()

    def refresh_client_table(self):
        self.clientTree.setRowCount(0)
        query = self.searchBar.text().lower()
        clients = self.db.get_clients()
        for c in clients:
            if query and query not in str(c.get("full_name","")).lower() and query not in str(c.get("doc_number","")).lower(): continue
            row = self.clientTree.rowCount(); self.clientTree.insertRow(row)
            self.clientTree.setItem(row, 0, QTableWidgetItem(str(c["id"])))
            self.clientTree.setItem(row, 1, QTableWidgetItem(str(c.get("full_name", ""))))
            self.clientTree.setItem(row, 2, QTableWidgetItem(str(c.get("phone", ""))))
            self.clientTree.setItem(row, 3, QTableWidgetItem(str(c.get("doc_number", ""))))

    def get_selected_client_id(self):
        items = self.clientTree.selectedItems()
        if not items: InfoBar.warning(t('warning'), "Selection error", parent=self, position=InfoBarPosition.TOP); return None
        return int(self.clientTree.item(items[0].row(), 0).text())

    def clear_client_form(self):
        self.current_editing_client_id = None
        self.update_ui_texts()
        for k,(v,l,lk) in self.client_entries.items():
            if isinstance(v, LineEdit): v.clear()
            elif isinstance(v, DateEdit): v.setDate(QDate.currentDate())

    def load_selected_client_to_form(self):
        cid = self.get_selected_client_id()
        if not cid: return
        data = self.db.get_client(cid)
        if not data: return
        self.clear_client_form(); self.current_editing_client_id = cid; self.update_ui_texts()
        for k,(v,l,lk) in self.client_entries.items():
            val = data.get(k)
            if val:
                if isinstance(v, LineEdit): v.setText(str(val))
                elif isinstance(v, DateEdit): 
                    y,m,d = map(int, val.split('-')) if '-' in str(val) else (2000,1,1)
                    v.setDate(QDate(y,m,d))

    def save_client(self):
        data = {}
        for k,(v,l,lk) in self.client_entries.items():
            data[k] = v.text().strip() if isinstance(v, LineEdit) else v.date().toString("yyyy-MM-dd")
        if not data["full_name"] or not data["doc_number"]:
            InfoBar.error(t('error'), t('validation_error'), parent=self, position=InfoBarPosition.TOP); return
        if self.current_editing_client_id:
            if self.db.update_client(self.current_editing_client_id, data):
                InfoBar.success(t('success'), t('client_updated'), parent=self, position=InfoBarPosition.TOP)
                self.refresh_client_table(); self.clear_client_form()
        else:
            if self.db.add_client(data):
                InfoBar.success(t('success'), t('client_saved'), parent=self, position=InfoBarPosition.TOP)
                self.refresh_client_table(); self.clear_client_form()

    def open_assign_dialog(self):
        cid = self.get_selected_client_id()
        if not cid: return
        d = AssignCameraDialog(self.db, self.window())
        if d.exec():
            ids = d.get_selected_ids()
            if not ids: return
            count = 0
            for sid in ids:
                if self.db.assign_camera_to_client(cid, sid): count += 1
            if count: InfoBar.success(t('success'), t('assignment_success'), parent=self, position=InfoBarPosition.TOP)

    def open_return_dialog(self):
        cid = self.get_selected_client_id()
        if not cid: return
        p = self.db.get_client_purchases_for_pdf(cid)["cameras"]
        if not p:
            InfoBar.warning(t('warning'), "No cameras assigned to this client", parent=self, position=InfoBarPosition.TOP)
            return
            
        d = ReturnCameraDialog(p, self.window())
        if d.exec():
            selected_serials = d.get_selected_serials()
            if not selected_serials: return
            
            count = 0
            cur = self.db.conn.cursor()
            for sn in selected_serials:
                cur.execute("SELECT id FROM serial_numbers WHERE serial_number=?", (sn,))
                row = cur.fetchone()
                if row:
                    sid = row[0]
                    cur.execute("DELETE FROM client_purchases WHERE client_id=? AND serial_id=?", (cid, sid))
                    cur.execute("UPDATE serial_numbers SET is_used=0 WHERE id=?", (sid,))
                    count += 1
            self.db.conn.commit()
            if count:
                InfoBar.success(t('success'), f"Returned {count} camera(s)!", parent=self, position=InfoBarPosition.TOP)
                if hasattr(self.window(), 'inventoryInterface'): self.window().inventoryInterface.refresh_inventory_table()

    def generate_combined_pdf(self):
        cid = self.get_selected_client_id()
        if not cid: return
        data = self.db.get_client_purchases_for_pdf(cid)
        try:
            gen = PDFGenerator()
            gen.generate_annex1(data["client"], data["cameras"])
            gen.generate_annex5(data["client"], data["cameras"])
            InfoBar.success(t('success'), t('pdf_generated'), parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error(t('error'), str(e), parent=self, position=InfoBarPosition.TOP)

class SettingsInterface(QWidget):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent=parent)
        self.db = db; self.setObjectName("SettingsInterface")
        self.vBoxLayout = QVBoxLayout(self); self.vBoxLayout.setContentsMargins(24, 24, 24, 24)

        # Language Card
        self.langCard = CardWidget(self)
        self.langLayout = QVBoxLayout(self.langCard)
        self.langTitle = SubtitleLabel(t('lang_settings'), self.langCard)
        self.langLayout.addWidget(self.langTitle)
        h = QHBoxLayout()
        self.lblSelect = SubtitleLabel(t('select_lang'), self.langCard)
        self.langCombo = ComboBox(self.langCard)
        self.langCombo.addItems(["Français", "العربية"])
        self.langCombo.setCurrentText("Français" if CURRENT_LANG == 'fr' else "العربية")
        self.langCombo.currentTextChanged.connect(self.change_language)
        h.addWidget(self.lblSelect); h.addWidget(self.langCombo); h.addStretch(1)
        self.langLayout.addLayout(h)
        self.vBoxLayout.addWidget(self.langCard)

        # Maintenance Card
        self.maintCard = CardWidget(self)
        self.maintLayout = QVBoxLayout(self.maintCard)
        self.maintTitle = SubtitleLabel(t('maintenance'), self.maintCard)
        self.maintLayout.addWidget(self.maintTitle)
        self.btnClearDb = PrimaryPushButton(t('clear_db'), self.maintCard)
        self.btnClearDb.clicked.connect(self.confirm_clear_db)
        self.maintLayout.addWidget(self.btnClearDb)
        self.vBoxLayout.addWidget(self.maintCard)

        # Mode Card
        self.inputCard = CardWidget(self)
        self.inputLayout = QVBoxLayout(self.inputCard)
        self.mgmtTitle = SubtitleLabel(t('catalog_mgmt'), self.inputCard)
        self.inputLayout.addWidget(self.mgmtTitle)
        g = QGridLayout()
        self.catName = LineEdit(self.inputCard); self.catName.setPlaceholderText(t('int_model_name'))
        self.catDesig = LineEdit(self.inputCard); self.catDesig.setPlaceholderText(t('equip_desig'))
        self.catNature = LineEdit(self.inputCard); self.catNature.setPlaceholderText(t('equip_nature'))
        self.catCat = LineEdit(self.inputCard); self.catCat.setPlaceholderText(t('category'))
        self.catSub = LineEdit(self.inputCard); self.catSub.setPlaceholderText(t('sub_category'))
        g.addWidget(self.catDesig, 0, 0)
        g.addWidget(self.catNature, 0, 1)
        g.addWidget(self.catName, 0, 2)
        g.addWidget(self.catCat, 1, 0)
        g.addWidget(self.catSub, 1, 1)
        self.btnAddModel = PrimaryPushButton(t('add_model'), self.inputCard)
        self.btnAddModel.clicked.connect(self.add_camera_model); g.addWidget(self.btnAddModel, 1,2)
        self.inputLayout.addLayout(g); self.vBoxLayout.addWidget(self.inputCard)

        # Table Card
        self.listCard = CardWidget(self)
        self.listLayout = QVBoxLayout(self.listCard)
        self.regTitle = SubtitleLabel(t('registered_models'), self.listCard)
        self.listLayout.addWidget(self.regTitle)
        self.catTree = TableWidget(self.listCard)
        self.catTree.setColumnCount(6)
        self.catTree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.catTree.setHorizontalHeaderLabels([t('id'), t('equip_desig'), t('equip_nature'), t('int_model_name'), t('category'), t('sub_category')])
        self.catTree.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.listLayout.addWidget(self.catTree); self.vBoxLayout.addWidget(self.listCard, 1)
        self.refresh_catalog_table()

    def update_ui_texts(self):
        self.langTitle.setText(t('lang_settings'))
        self.lblSelect.setText(t('select_lang'))
        self.mgmtTitle.setText(t('catalog_mgmt'))
        self.catName.setPlaceholderText(t('int_model_name'))
        self.catDesig.setPlaceholderText(t('equip_desig'))
        self.catNature.setPlaceholderText(t('equip_nature'))
        self.catCat.setPlaceholderText(t('category'))
        self.catSub.setPlaceholderText(t('sub_category'))
        self.btnClearDb.setText(t('clear_db'))
        self.maintTitle.setText(t('maintenance'))
        self.catTree.setHorizontalHeaderLabels([t('id'), t('equip_desig'), t('equip_nature'), t('int_model_name'), t('category'), t('sub_category')])
        self.refresh_catalog_table()

    def change_language(self, text):
        global CURRENT_LANG
        CURRENT_LANG = 'ar' if text == "العربية" else 'fr'
        # Update layout direction
        direction = Qt.LayoutDirection.RightToLeft if CURRENT_LANG == 'ar' else Qt.LayoutDirection.LeftToRight
        QApplication.instance().setLayoutDirection(direction)
        # Refresh all interfaces
        self.window().update_all_ui()

    def add_camera_model(self):
        n = self.catName.text().strip()
        if n:
            self.db.add_camera_model(n, self.catDesig.text(), self.catNature.text(), self.catCat.text(), self.catSub.text())
            self.catName.clear(); self.catDesig.clear(); self.catNature.clear(); self.catCat.clear(); self.catSub.clear()
            self.refresh_catalog_table()
            if hasattr(self.window(), 'inventoryInterface'): self.window().inventoryInterface.refresh_scanner_models()

    def refresh_catalog_table(self):
        self.catTree.setRowCount(0); models = self.db.get_camera_models()
        for m in models:
            r = self.catTree.rowCount(); self.catTree.insertRow(r)
            self.catTree.setItem(r, 0, QTableWidgetItem(str(m["id"])))
            self.catTree.setItem(r, 1, QTableWidgetItem(str(m.get("equipment_designation", ""))))
            self.catTree.setItem(r, 2, QTableWidgetItem(str(m.get("equipment_nature", ""))))
            self.catTree.setItem(r, 3, QTableWidgetItem(str(m["model_name"])))
            self.catTree.setItem(r, 4, QTableWidgetItem(str(m.get("category", ""))))
            self.catTree.setItem(r, 5, QTableWidgetItem(str(m.get("sub_category", ""))))

    def confirm_clear_db(self):
        w = MessageBox(t('confirm_title'), t('confirm_clear_msg'), self.window())
        if w.exec():
            if self.db.clear_database():
                self.refresh_catalog_table()
                if hasattr(self.window(), 'inventoryInterface'): self.window().inventoryInterface.refresh_scanner_models()
                InfoBar.success(t('db_cleared'), t('db_cleared_msg'), duration=2000, parent=self.window())
            else:
                InfoBar.error("Error", "Could not clear database", duration=2000, parent=self.window())

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager(); self.db_manager.initialize_db()
        self.initWindow(); setTheme(Theme.DARK)
        self.inventoryInterface = InventoryInterface(self.db_manager, self)
        self.clientInterface = ClientInterface(self.db_manager, self)
        self.settingsInterface = SettingsInterface(self.db_manager, self)
        self.initNavigation()
        self.update_all_ui()

    def update_all_ui(self):
        self.inventoryInterface.update_ui_texts()
        self.clientInterface.update_ui_texts()
        self.settingsInterface.update_ui_texts()
        
        # Rename navigation items
        for interface in [self.inventoryInterface, self.clientInterface, self.settingsInterface]:
            item = self.navigationInterface.widget(interface.objectName())
            if item:
                key = 'nav_' + interface.objectName().replace('Interface', '').lower()
                item.setText(t(key))

    def initWindow(self):
        self.resize(1300, 800); self.setWindowTitle('CCTV Manager Pro')
        d = QApplication.primaryScreen().availableGeometry(); w, h = d.width(), d.height()
        self.move(int(w//2 - self.width()//2), int(h//2 - self.height()//2))

    def initNavigation(self):
        self.addSubInterface(self.inventoryInterface, FluentIcon.FOLDER, t('nav_inventory'))
        self.addSubInterface(self.clientInterface, FluentIcon.PEOPLE, t('nav_clients'))
        self.addSubInterface(self.settingsInterface, FluentIcon.SETTING, t('nav_settings'))
        self.navigationInterface.setCurrentItem(self.inventoryInterface.objectName())

if __name__ == '__main__':
    w = MainWindow()
    w.show()
    sys.exit(app.exec())