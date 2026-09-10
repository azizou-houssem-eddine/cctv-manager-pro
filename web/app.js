/**
 * CCTV Manager Pro - Web Application Logic
 * Integrates with Python backend via pywebview JS bridge.
 */

// --- Translations Dictionary ---
const TRANSLATIONS = {
    fr: {
        nav_inventory: "Inventaire",
        nav_clients: "Clients",
        nav_settings: "Paramètres",
        inventory_title: "Gestion de l'Inventaire & Scannage",
        inventory_sub: "Scannez des codes-barres ou sérials et suivez le stock en temps réel.",
        scan_equipment: "Scanner Équipement",
        select_model: "Modèle de Caméra",
        select_model_placeholder: "-- Choisir un modèle --",
        serial_num: "N° de Série",
        staged_batch: "Lot en attente",
        save: "Enregistrer",
        clear: "Effacer",
        existing_db: "Stock en Base de Données",
        actions: "Actions",
        no_scanned_yet: "Aucun numéro scanné",
        model: "Modèle",
        status: "État",
        assigned_to: "Assigné à",
        in_stock: "En Stock",
        assigned: "Assigné",
        clients_sub: "Enregistrez les dossiers réglementaires (Annexes 1 et 5) et affectez les équipements.",
        register_client: "Enregistrer Nouveau Client",
        edit_client: "Modifier Client ID: ",
        clear_form: "Nouveau / Vider",
        identity: "Identité",
        full_name: "Nom Complet: *",
        father_name: "Nom du Père:",
        mother_name: "Nom de la Mère:",
        dob: "Date de Naissance:",
        pob: "Lieu de Naissance:",
        nationality: "Nationalité:",
        documents: "Documents d'Identité",
        doc_num: "N° Carte d'Identité: *",
        doc_issuer: "Délivré par:",
        doc_date: "Date de délivrance:",
        passport_num: "N° Passeport (optionnel):",
        pass_issuer: "Délivré par (Passeport):",
        pass_date: "Validité Passeport:",
        corporate: "Entreprise & Contact",
        company_name: "Nom de l'Entreprise:",
        company_hq: "Siège Social:",
        profession: "Profession:",
        activity_type: "Type d'activité:",
        phone: "Téléphone:",
        email: "Email:",
        fax: "Fax:",
        city: "Ville:",
        address: "Adresse complète:",
        shareholders: "Noms et Prénoms des Associés:",
        logistics: "Logistique (Annexe 1)",
        acc_ref: "Réf. Accréditation:",
        origin_country: "Pays d'origine:",
        import_country: "Pays d'importation:",
        trans_method: "Méthode de transport:",
        storage_loc: "Lieu de stockage:",
        security_cond: "Conditions de sécurité:",
        save_client: "Enregistrer le Client",
        update_client: "Mettre à jour le Client",
        cameras: "Caméras",
        edit: "Modifier",
        assign_camera: "Assigner Caméra",
        return_camera: "Retour Caméra",
        open_folder: "Dossier",
        first_dossier: "1er Dossier (PDF)",
        settings_sub: "Configurez les modèles de caméras et gérez la base de données.",
        add_model: "Ajouter un Modèle au Catalogue",
        int_model_name: "Marque & Modèle",
        equip_desig: "Désignation (Annexe 1)",
        equip_nature: "Nature (Annexe 1)",
        category: "Section (القسم)",
        sub_category: "Sous-section (الفرع)",
        save_model: "Enregistrer le Modèle",
        maintenance: "Maintenance du Système",
        maint_desc: "Réinitialisez ou videz toutes les données en cas de besoin de maintenance.",
        clear_db: "Vider la Base de Données",
        registered_models: "Modèles Enregistrés",
        stock: "En Stock",
        cancel: "Annuler",
        confirm_assign: "Confirmer l'Assignation",
        confirm_return: "Confirmer le Retour",
        select_all: "Tout Cocher",
        clear_all: "Tout Décocher",
        dossier_ready: "1er Dossier Généré avec Succès !",
        dossier_saved_in: "Les formulaires officiels (Annexe 1 & 5) ont été tamponnés avec succès.",
        open_dossier_folder: "Ouvrir le Dossier Client",
        view_annex1: "Voir Annexe 1",
        view_annex5: "Voir Annexe 5",
        close: "Fermer",
        client_saved: "Client enregistré avec succès.",
        client_updated: "Client mis à jour avec succès.",
        serials_saved: "numéro(s) de série enregistré(s).",
        cameras_assigned: "caméra(s) assignée(s) avec succès.",
        cameras_returned: "caméra(s) retournée(s) en stock.",
        db_cleared: "La base de données a été vidée.",
        confirm_clear_prompt: "Voulez-vous vraiment supprimer TOUTES les données ? Cette action est irréversible.",
        nav_dashboard: "Tableau de Bord",
        dashboard_title: "Tableau de Bord Exécutif",
        dashboard_sub: "Vue synthétique du stock, des affectations et alertes réglementaires.",
        kpi_in_stock: "Caméras en Stock",
        kpi_available_for_install: "Disponibles pour installation",
        kpi_assigned: "Équipements Déployés",
        kpi_assigned_clients: "Assignés aux clients",
        kpi_clients: "Clients Enregistrés",
        kpi_total_dossiers: "Dossiers créés",
        kpi_low_stock: "Alertes Stock Bas",
        kpi_models_under_threshold: "Modèles sous le seuil",
        low_stock_monitoring: "Surveillance des Seuils de Stock",
        no_stock_alerts: "Aucune alerte de stock bas",
        threshold: "Seuil Min.",
        quick_actions: "Actions Rapides & Raccourcis",
        qa_quick_scan: "Scanner Immédiat",
        qa_quick_scan_sub: "Entrée rapide code-barres",
        qa_new_client: "Nouveau Client",
        qa_new_client_sub: "Créer un dossier (1er Dossier)",
        qa_import_csv: "Importer CSV",
        qa_import_csv_sub: "Chargement par lot de sérials",
        qa_export_stock: "Exporter l'Inventaire",
        qa_export_stock_sub: "Fichier Excel (.xlsx) complet",
        sc_search: "Recherche rapide",
        sc_new: "Nouveau client",
        sc_save: "Enregistrer",
        sc_esc: "Fermer dialogue",
        sound_on: "Bip Activé",
        sound_off: "Bip Coupé",
        preview_docs: "Aperçu",
        doc_preview_title: "Aperçu du Document Réglementaire",
        rendering_preview: "Génération du rendu officiel 150 DPI...",
        preview_tampon_note: "Rendu officiel haute fidélité conforme aux modèles du Journal Officiel N°54.",
        open_pdf: "Ouvrir PDF",
        fit: "Ajuster",
        csv_import_title: "Importation Massive de Séries (CSV / TXT)",
        dropzone_prompt: "Glissez-déposez votre fichier CSV ici ou cliquez pour parcourir",
        dropzone_sub: "Détection automatique du séparateur et des en-têtes.",
        total_detected: "Total détecté:",
        valid_new: "Valides & Nouveaux:",
        dup_in_file: "Doublons dans fichier:",
        already_in_db: "Déjà en base:",
        confirm_import: "Confirmer l'Importation",
        import_csv: "Importer CSV",
        dossier_1_title: "Autorisation d'Acquisition",
        dossier_1_sub: "Annexes 1 & 5 + PV de Pose",
        dossier_2_title: "2ème Dossier (Exploitation)",
        dossier_2_sub: "Annexe 3 (Tableau Étendu) & Annexe 8",
        dossier_2_badge: "Actif",
        dossier_2_badge_active: "2ème Dossier",
        second_dossier: "2ème Dossier (PDF)",
        view_annex3: "Annexe 3 (Exploitation)",
        view_annex8: "Annexe 8 (Non-Connexion)",
        view_pv_pose: "PV de Pose",
        open_in_previewer: "Ouvrir dans l'Aperçu Intégré",
        min_stock_threshold: "Seuil Alerte Stock Bas",
        export: "Exporter",
        refresh: "Actualiser",
        dossier_folder_title: "📁 Emplacement des Dossiers Clients",
        dossier_folder_desc: "Choisissez le répertoire où seront créés automatiquement les dossiers des clients.",
        current_dossier_folder: "Répertoire Racine Sélectionné",
        browse_btn: "📂 Parcourir",
        open_folder_btn: "↗️ Ouvrir",
        tree_title: "🗂️ Structure automatique des sous-dossiers :",
        seed_data_btn: "🌱 Charger Données Démo",
        all_dossiers: "Tous les Dossiers",
        open_clients_root: "Ouvrir le répertoire racine de tous les clients",
        folder_updated: "Emplacement des dossiers mis à jour !",
        seed_success: "Données de démonstration chargées avec succès !"
    },
    ar: {
        nav_inventory: "المخزون",
        nav_clients: "العملاء",
        nav_settings: "الإعدادات",
        inventory_title: "إدارة المخزون والمسح الضوئي",
        inventory_sub: "مسح الباركود والأرقام التسلسلية ومتابعة المخزون في الوقت الفعلي.",
        scan_equipment: "مسح المعدات",
        select_model: "طراز الكاميرا",
        select_model_placeholder: "-- اختر الطراز --",
        serial_num: "الرقم التسلسلي",
        staged_batch: "الدفعة المنتظرة",
        save: "حفظ",
        clear: "مسح",
        existing_db: "المخزون في قاعدة البيانات",
        actions: "إجراءات",
        no_scanned_yet: "لا توجد أرقام ممسوحة",
        model: "الموديل",
        status: "الحالة",
        assigned_to: "مخصص لـ",
        in_stock: "متوفر",
        assigned: "مخصص",
        clients_sub: "تسجيل الملفات التنظيمية (الملحق 1 والملحق 5) وتخصيص المعدات.",
        register_client: "تسجيل عميل جديد",
        edit_client: "تعديل العميل رقم: ",
        clear_form: "جديد / مسح",
        identity: "الهوية الشخصية",
        full_name: "الاسم الكامل: *",
        father_name: "اسم الأب:",
        mother_name: "اسم الأم:",
        dob: "تاريخ الميلاد:",
        pob: "مكان الميلاد:",
        nationality: "الجنسية:",
        documents: "وثائق الهوية",
        doc_num: "رقم بطاقة التعريف: *",
        doc_issuer: "جهة الإصدار:",
        doc_date: "تاريخ الإصدار:",
        passport_num: "رقم جواز السفر (اختياري):",
        pass_issuer: "جهة الإصدار (الجواز):",
        pass_date: "صلاحية الجواز:",
        corporate: "الشركة والاتصال",
        company_name: "اسم الشركة:",
        company_hq: "المقر الاجتماعي:",
        profession: "المهنة:",
        activity_type: "نوع النشاط:",
        phone: "الهاتف:",
        email: "البريد الإلكتروني:",
        fax: "الفاكس:",
        city: "المدينة:",
        address: "العنوان الكامل:",
        shareholders: "أسماء وألقاب الشركاء:",
        logistics: "اللوجستيات (الملحق 1)",
        acc_ref: "مرجع الاعتماد:",
        origin_country: "بلد المنشأ:",
        import_country: "بلد الاستيراد:",
        trans_method: "طريقة النقل:",
        storage_loc: "مكان التخزين:",
        security_cond: "شروط الأمن:",
        save_client: "حفظ العميل",
        update_client: "تحديث العميل",
        cameras: "الكاميرات",
        edit: "تعديل",
        assign_camera: "تخصيص كاميرا",
        return_camera: "إرجاع كاميرا",
        open_folder: "المجلد",
        first_dossier: "الملف الأول (PDF)",
        settings_sub: "تهيئة موديلات الكاميرات وصيانة قاعدة البيانات.",
        add_model: "إضافة طراز إلى الكتالوج",
        int_model_name: "العلامة والنموذج",
        equip_desig: "تعيين التجهيزات (الملحق 1)",
        equip_nature: "طبيعة التجهيزات (الملحق 1)",
        category: "القسم",
        sub_category: "القسم الفرعي",
        save_model: "حفظ الطراز",
        maintenance: "صيانة النظام",
        maint_desc: "إعادة تعيين أو حذف جميع البيانات لأغراض الصيانة.",
        clear_db: "تفريغ قاعدة البيانات",
        registered_models: "الموديلات المسجلة",
        stock: "المتوفر",
        cancel: "إلغاء",
        confirm_assign: "تأكيد التخصيص",
        confirm_return: "تأكيد الإرجاع",
        select_all: "تحديد الكل",
        clear_all: "إلغاء التحديد",
        dossier_ready: "تم إنشاء الملف الأول بنجاح !",
        dossier_saved_in: "تم ختم الاستمارات الرسمية (الملحق 1 والملحق 5) بنجاح.",
        open_dossier_folder: "فتح مجلد العميل",
        view_annex1: "عرض الملحق 1",
        view_annex5: "عرض الملحق 5",
        close: "إغلاق",
        client_saved: "تم حفظ العميل بنجاح.",
        client_updated: "تم تحديث العميل بنجاح.",
        serials_saved: "رقم تسلسلي تم تسجيله.",
        cameras_assigned: "كاميرا تم تخصيصها بنجاح.",
        cameras_returned: "كاميرا تمت إعادتها إلى المخزون.",
        db_cleared: "تم تفريغ قاعدة البيانات بالكامل.",
        confirm_clear_prompt: "هل تريد حقاً مسح كافة البيانات؟ هذا الإجراء لا يمكن التراجع عنه.",
        nav_dashboard: "لوحة القيادة",
        dashboard_title: "لوحة القيادة التنفيذية",
        dashboard_sub: "نظرة شاملة على المخزون والتخصيصات والتنبيهات التنظيمية.",
        kpi_in_stock: "كاميرات في المخزن",
        kpi_available_for_install: "جاهزة للتثبيت والتركيب",
        kpi_assigned: "المعدات المركبة",
        kpi_assigned_clients: "مخصصة للزبائن",
        kpi_clients: "العملاء المسجلون",
        kpi_total_dossiers: "ملفات منشأة",
        kpi_low_stock: "تنبيهات انخفاض المخزون",
        kpi_models_under_threshold: "طرازات تحت الحد الأدنى",
        low_stock_monitoring: "مراقبة حدود المخزون",
        no_stock_alerts: "لا توجد تنبيهات انخفاض في المخزون",
        threshold: "الحد الأدنى",
        quick_actions: "إجراءات سريعة واختصارات",
        qa_quick_scan: "مسح ضوئي فوري",
        qa_quick_scan_sub: "إدخال سريع للباركود",
        qa_new_client: "عميل جديد",
        qa_new_client_sub: "إنشاء ملف (الملف الأول)",
        qa_import_csv: "استيراد CSV",
        qa_import_csv_sub: "تحميل دفعة أرقام تسلسلية",
        qa_export_stock: "تصدير المخزون",
        qa_export_stock_sub: "ملف إكسل (.xlsx) كامل",
        sc_search: "بحث سريع",
        sc_new: "عميل جديد",
        sc_save: "حفظ",
        sc_esc: "إغلاق النافذة",
        sound_on: "الصوت مفعّل",
        sound_off: "الصوت مكتوم",
        preview_docs: "معاينة",
        doc_preview_title: "معاينة الوثيقة التنظيمية",
        rendering_preview: "جارٍ توليد المعاينة الرسمية بدقة 150 DPI...",
        preview_tampon_note: "معاينة رسمية عالية الدقة مطابقة لنماذج الجريدة الرسمية رقم 54.",
        open_pdf: "فتح PDF",
        fit: "ملاءمة",
        csv_import_title: "استيراد جماعي للأرقام التسلسلية (CSV / TXT)",
        dropzone_prompt: "اسحب وأفلت ملف CSV هنا أو اضغط للاستعراض",
        dropzone_sub: "اكتشاف تلقائي للفاصل ورؤوس الأعمدة.",
        total_detected: "الإجمالي المكتشف:",
        valid_new: "صالح وجديد:",
        dup_in_file: "تكرارات في الملف:",
        already_in_db: "موجود مسبقاً في القاعدة:",
        confirm_import: "تأكيد الاستيراد",
        import_csv: "استيراد CSV",
        dossier_1_title: "رخصة الاقتناء",
        dossier_1_sub: "الملحقان 1 و 5 + محضر التثبيت",
        dossier_2_title: "الملف الثاني (الاستغلال)",
        dossier_2_sub: "الملحق 3 (الجدول الممتد) والملحق 8",
        dossier_2_badge: "مفعّل",
        dossier_2_badge_active: "الملف الثاني",
        second_dossier: "2ème Dossier (PDF)",
        view_annex3: "الملحق 3 (الاستغلال)",
        view_annex8: "الملحق 8 (تعهد الإنترنت)",
        view_pv_pose: "محضر التثبيت",
        open_in_previewer: "فتح في المعاينة المدمجة",
        min_stock_threshold: "حد تنبيه انخفاض المخزون",
        export: "تصدير",
        refresh: "تحديث",
        dossier_folder_title: "📁 مجلد ملفات الزبائن",
        dossier_folder_desc: "حدد المجلد الرئيسي الذي ستنشأ فيه تلقائياً ملفات الزبائن.",
        current_dossier_folder: "المجلد الرئيسي المحدد",
        browse_btn: "📂 استعراض",
        open_folder_btn: "↗️ فتح",
        tree_title: "🗂️ الهيكل التلقائي للمجلدات الفرعية :",
        seed_data_btn: "🌱 شحن بيانات نموذجية",
        all_dossiers: "كل الملفات",
        open_clients_root: "فتح المجلد الرئيسي لجميع الزبائن",
        folder_updated: "تم تحديث مسار مجلد الزبائن بنجاح!",
        seed_success: "تم شحن البيانات النموذجية بنجاح!"
    }
};

// --- Application State ---
let currentLang = localStorage.getItem("cctv_lang") || "fr";
let stagedSerials = [];
let cameraModels = [];
let clientsList = [];
let selectedClientId = null;
let lastGeneratedDossier = null;

// --- Helper Functions ---
function t(key) {
    return (TRANSLATIONS[currentLang] && TRANSLATIONS[currentLang][key]) || key;
}

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : '✕'}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 250);
    }, 3500);
}

function switchLanguage(lang) {
    currentLang = lang;
    localStorage.setItem("cctv_lang", lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";

    document.getElementById("btnLangFr").classList.toggle("active", lang === "fr");
    document.getElementById("btnLangAr").classList.toggle("active", lang === "ar");

    // Update all static i18n text
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        el.textContent = t(key);
    });

    // Update dynamic titles
    updateClientFormTitle();
    loadInventoryTable();
    loadClientsTable();
    loadModelsTable();
}

// --- Web Audio Feedback Engine (R2) ---
let audioCtx = null;
let soundEnabled = localStorage.getItem("cctv_sound") !== "false";

function initAudio() {
    if (!audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            audioCtx = new AudioContext();
        }
    }
    if (audioCtx && audioCtx.state === "suspended") {
        audioCtx.resume();
    }
}

function playScannerBeep(type = "success") {
    if (!soundEnabled) return;
    try {
        initAudio();
        if (!audioCtx) return;

        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        if (type === "success") {
            // Crisp two-tone harmonic chime (880Hz -> 1318.5Hz)
            osc.type = "sine";
            osc.frequency.setValueAtTime(880, now);
            osc.frequency.exponentialRampToValueAtTime(1318.5, now + 0.07);
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
            osc.start(now);
            osc.stop(now + 0.15);
        } else {
            // Low distinctive error buzzer (160Hz sawtooth wave)
            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(160, now);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
            osc.start(now);
            osc.stop(now + 0.22);
        }
    } catch (e) {
        console.warn("Audio feedback error:", e);
    }
}

function toggleScannerSound() {
    soundEnabled = !soundEnabled;
    localStorage.setItem("cctv_sound", soundEnabled);
    updateSoundButtonUI();
    if (soundEnabled) playScannerBeep("success");
}

function updateSoundButtonUI() {
    const btn = document.getElementById("btnScannerSound");
    const icon = document.getElementById("soundIcon");
    if (!btn || !icon) return;
    const labelSpan = btn.querySelector("span:last-child");
    if (soundEnabled) {
        icon.textContent = "🔊";
        if (labelSpan) labelSpan.textContent = t("sound_on");
        btn.classList.remove("btn-danger");
    } else {
        icon.textContent = "🔇";
        if (labelSpan) labelSpan.textContent = t("sound_off");
        btn.classList.add("btn-danger");
    }
}

// --- Navigation Tabs & Helpers ---
function navigateToTab(tab) {
    document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

    const navBtn = document.querySelector(`.nav-item[data-tab="${tab}"]`);
    const tabPane = document.getElementById(`tab-${tab}`);
    if (navBtn) navBtn.classList.add("active");
    if (tabPane) tabPane.classList.add("active");

    if (tab === "dashboard") loadDashboard();
    if (tab === "inventory") {
        setTimeout(() => {
            const inp = document.getElementById("scannerInput");
            if (inp) inp.focus();
        }, 100);
    }
    if (tab === "clients") loadClientsTable();
    if (tab === "settings") loadModels();
}

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
        const tab = item.getAttribute("data-tab");
        navigateToTab(tab);
    });
});

// --- Modal Utilities ---
function openModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add("active");
}

function closeModal(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove("active");
}

// --- Executive Analytics Dashboard (R1) ---
async function loadDashboard() {
    try {
        const res = await window.pywebview.api.get_dashboard_analytics();
        if (!res.success) return;
        const d = res.data;

        const stockEl = document.getElementById("kpiStockVal");
        const assignedEl = document.getElementById("kpiAssignedVal");
        const clientsEl = document.getElementById("kpiClientsVal");
        const alertEl = document.getElementById("kpiAlertVal");
        const alertCard = document.getElementById("kpiAlertCard");

        const inStock = d.total_stock ?? d.totals?.total_in_stock ?? 0;
        const assigned = d.total_assigned ?? d.totals?.total_assigned ?? 0;
        const clients = d.total_clients ?? d.totals?.total_clients ?? 0;
        const lowStockItems = d.low_stock_items || d.low_stock_alerts || [];
        const lowCount = d.low_stock_count ?? lowStockItems.length;

        if (stockEl) stockEl.textContent = inStock;
        if (assignedEl) assignedEl.textContent = assigned;
        if (clientsEl) clientsEl.textContent = clients;
        if (alertEl) alertEl.textContent = lowCount;

        if (alertCard) {
            alertCard.classList.toggle("has-alerts", lowCount > 0);
        }

        const badge = document.getElementById("lowStockBadge");
        if (badge) badge.textContent = `${lowCount} alerte(s)`;

        const tbody = document.querySelector("#lowStockTable tbody");
        if (tbody) {
            tbody.innerHTML = "";
            if (lowStockItems.length === 0) {
                tbody.innerHTML = `<tr class="empty-row"><td colspan="4">${t('no_stock_alerts')}</td></tr>`;
            } else {
                lowStockItems.forEach(item => {
                    const tr = document.createElement("tr");
                    const isZero = (item.in_stock_count || 0) === 0;
                    const stBadge = isZero 
                        ? `<span class="badge badge-danger">Rupture (0)</span>` 
                        : `<span class="badge badge-warning">Stock Bas (${item.in_stock_count})</span>`;
                    tr.innerHTML = `
                        <td style="font-weight: 600;">${item.model_name}</td>
                        <td>${item.in_stock_count || 0}</td>
                        <td>${item.stock_threshold ?? 5}</td>
                        <td>${stBadge}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

// --- Scanner & Inventory Flow ---
const scannerInput = document.getElementById("scannerInput");
scannerInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        handleScan(scannerInput.value);
    }
});

function handleScan(rawVal) {
    const val = rawVal.trim().toUpperCase();
    if (!val) return;

    const modelSelect = document.getElementById("scanModelSelect");
    if (!modelSelect.value) {
        playScannerBeep("error");
        scannerInput.classList.add("scan-input-error");
        setTimeout(() => scannerInput.classList.remove("scan-input-error"), 400);
        showToast(t("select_model_placeholder"), "error");
        return;
    }

    if (stagedSerials.includes(val)) {
        playScannerBeep("error");
        scannerInput.classList.add("scan-input-error");
        setTimeout(() => scannerInput.classList.remove("scan-input-error"), 400);
        showToast(`Serial "${val}" déjà scanné dans ce lot.`, "error");
        scannerInput.value = "";
        return;
    }

    stagedSerials.push(val);
    scannerInput.value = "";
    playScannerBeep("success");
    scannerInput.classList.add("scan-input-success");
    setTimeout(() => scannerInput.classList.remove("scan-input-success"), 300);
    renderStagedTable();
}

function renderStagedTable() {
    const tbody = document.querySelector("#stagedTable tbody");
    tbody.innerHTML = "";

    document.getElementById("stagedCountBadge").textContent = `${stagedSerials.length} scanné(s)`;

    if (stagedSerials.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="3">${t('no_scanned_yet')}</td></tr>`;
        return;
    }

    stagedSerials.forEach((sn, idx) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${idx + 1}</td>
            <td style="font-family: monospace; font-weight: 600;">${sn}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="removeStagedSerial(${idx})">✕</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function removeStagedSerial(idx) {
    stagedSerials.splice(idx, 1);
    renderStagedTable();
}

function clearStagedBatch() {
    stagedSerials = [];
    renderStagedTable();
}

async function saveStagedBatch() {
    const modelSelect = document.getElementById("scanModelSelect");
    const modelId = modelSelect.value;
    if (!modelId || stagedSerials.length === 0) {
        showToast("Veuillez sélectionner un modèle et scanner au moins un numéro.", "error");
        return;
    }

    try {
        const res = await window.pywebview.api.save_scanned_serials(modelId, stagedSerials);
        if (res.success) {
            showToast(`${res.count} ${t('serials_saved')}`, "success");
            clearStagedBatch();
            loadInventoryTable();
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur lors de l'enregistrement", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Inventory Table & Instant Search (R2) ---
let inventorySearchTimer = null;
function debounceInventorySearch() {
    clearTimeout(inventorySearchTimer);
    inventorySearchTimer = setTimeout(() => {
        loadInventoryTable();
    }, 200);
}

async function loadInventoryTable() {
    const filterModel = document.getElementById("filterModelSelect")?.value || null;
    const searchInput = document.getElementById("inventorySearchInput");
    const searchQuery = searchInput ? searchInput.value.trim() : "";

    try {
        let res;
        if (searchQuery) {
            res = await window.pywebview.api.search_serials(searchQuery, filterModel || null);
        } else {
            res = await window.pywebview.api.get_inventory_serials(filterModel || null);
        }

        const tbody = document.querySelector("#inventoryTable tbody");
        tbody.innerHTML = "";

        if (!res.success || !res.data || res.data.length === 0) {
            tbody.innerHTML = `<tr class="empty-row"><td colspan="4">Aucun enregistrement d'inventaire</td></tr>`;
            document.getElementById("totalStockBadge").textContent = "0 caméras";
            return;
        }

        document.getElementById("totalStockBadge").textContent = `${res.data.length} caméras`;

        res.data.forEach(item => {
            const tr = document.createElement("tr");
            const statusBadge = item.is_used 
                ? `<span class="badge badge-info">${t('assigned')}</span>`
                : `<span class="badge badge-success">${t('in_stock')}</span>`;
            
            const assignedClient = item.assigned_client_name 
                ? item.assigned_client_name 
                : (item.client_name ? item.client_name : "—");

            tr.innerHTML = `
                <td style="font-family: monospace; font-weight: 600;">${item.serial_number}</td>
                <td>${item.model_name}</td>
                <td>${statusBadge}</td>
                <td>${assignedClient}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

// --- Bulk CSV/Excel Export & Import (R2) ---
async function exportFilteredSerials(format = "csv") {
    const filterModel = document.getElementById("filterModelSelect")?.value || null;
    try {
        if (format === "csv") {
            const res = await window.pywebview.api.export_serials_csv(filterModel);
            if (res.success && res.csv_data) {
                const blob = new Blob([res.csv_data], { type: "text/csv;charset=utf-8;" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = res.filename || "inventaire_serials.csv";
                document.body.appendChild(a);
                a.click();
                setTimeout(() => { a.remove(); URL.revokeObjectURL(url); }, 500);
                showToast("Exportation CSV terminée !", "success");
            } else {
                showToast(res.error || "Erreur export CSV", "error");
            }
        } else {
            const res = await window.pywebview.api.export_serials_excel(filterModel);
            if (res.success && res.data_uri) {
                const a = document.createElement("a");
                a.href = res.data_uri;
                a.download = res.filename || "inventaire_serials.xlsx";
                document.body.appendChild(a);
                a.click();
                setTimeout(() => { a.remove(); }, 500);
                showToast("Exportation Excel (.xlsx) terminée !", "success");
            } else {
                showToast(res.error || "Erreur export Excel", "error");
            }
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

let stagedCsvSerials = [];
function openCsvImportModal() {
    const select = document.getElementById("csvImportModelSelect");
    select.innerHTML = `<option value="">${t('select_model_placeholder')}</option>`;
    cameraModels.forEach(m => {
        select.innerHTML += `<option value="${m.id}">${m.model_name} (${m.equipment_designation || ''})</option>`;
    });
    document.getElementById("csvFileInput").value = "";
    document.getElementById("csvAnalysisSummary").style.display = "none";
    document.getElementById("csvPreviewTableWrapper").style.display = "none";
    document.getElementById("btnConfirmCsvImport").disabled = true;
    stagedCsvSerials = [];
    setupDropzone();
    openModal("csvImportModal");
}

function handleCsvFileSelected(e) {
    const file = e.target.files[0];
    if (!file) return;
    readCsvFile(file);
}

function setupDropzone() {
    const dz = document.getElementById("csvDropzone");
    if (!dz || dz.dataset.bound === "true") return;
    dz.dataset.bound = "true";

    ["dragenter", "dragover"].forEach(eventName => {
        dz.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dz.classList.add("dragover");
        }, false);
    });
    ["dragleave", "drop"].forEach(eventName => {
        dz.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dz.classList.remove("dragover");
        }, false);
    });
    dz.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const file = dt.files[0];
        if (file) readCsvFile(file);
    }, false);
}

function readCsvFile(file) {
    const reader = new FileReader();
    reader.onload = async (event) => {
        const text = event.target.result;
        try {
            const res = await window.pywebview.api.preview_csv_serials(text);
            if (res.success) {
                document.getElementById("csvStatTotal").textContent = res.total_found;
                document.getElementById("csvStatValid").textContent = res.valid.length;
                document.getElementById("csvStatDupFile").textContent = res.duplicates_in_file.length;
                document.getElementById("csvStatInDb").textContent = res.already_in_db.length;
                document.getElementById("csvAnalysisSummary").style.display = "flex";

                stagedCsvSerials = res.valid;
                const tbody = document.querySelector("#csvPreviewTable tbody");
                tbody.innerHTML = "";
                const previewRows = res.valid.slice(0, 50);
                previewRows.forEach((sn, idx) => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${idx + 1}</td>
                        <td style="font-family: monospace; font-weight:600;">${sn}</td>
                        <td><span class="badge badge-success">Valide</span></td>
                    `;
                    tbody.appendChild(tr);
                });
                if (res.already_in_db.length > 0) {
                    res.already_in_db.slice(0, 10).forEach((sn, idx) => {
                        const tr = document.createElement("tr");
                        tr.innerHTML = `
                            <td>-</td>
                            <td style="font-family: monospace; font-weight:600; text-decoration: line-through;">${sn}</td>
                            <td><span class="badge badge-danger">Déjà en base</span></td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
                document.getElementById("csvPreviewTableWrapper").style.display = "block";
                document.getElementById("btnConfirmCsvImport").disabled = res.valid.length === 0;
            } else {
                showToast(res.error || "Erreur analyse fichier CSV", "error");
            }
        } catch (err) {
            showToast(err.toString(), "error");
        }
    };
    reader.readAsText(file);
}

async function submitCsvImport() {
    const modelId = document.getElementById("csvImportModelSelect").value;
    if (!modelId) {
        showToast(t("select_model_placeholder"), "error");
        return;
    }
    if (stagedCsvSerials.length === 0) {
        showToast("Aucun numéro de série valide à importer.", "error");
        return;
    }
    try {
        const res = await window.pywebview.api.import_serials_batch(modelId, stagedCsvSerials);
        if (res.success) {
            showToast(`${res.imported_count} numéro(s) importé(s) avec succès !`, "success");
            closeModal("csvImportModal");
            loadInventoryTable();
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur lors de l'importation", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Models & Catalog ---
async function loadModels() {
    try {
        const res = await window.pywebview.api.get_camera_models();
        if (res.success) {
            cameraModels = res.data;
            populateModelSelects();
            renderModelsTable();
        }
    } catch (err) {
        console.error(err);
    }
}

function populateModelSelects() {
    const scanSelect = document.getElementById("scanModelSelect");
    const filterSelect = document.getElementById("filterModelSelect");
    const assignSelect = document.getElementById("assignModelSelect");

    const currentScanVal = scanSelect ? scanSelect.value : "";
    const currentFilterVal = filterSelect ? filterSelect.value : "";

    if (scanSelect) scanSelect.innerHTML = `<option value="">${t('select_model_placeholder')}</option>`;
    if (filterSelect) filterSelect.innerHTML = `<option value="">Tous les modèles</option>`;
    if (assignSelect) assignSelect.innerHTML = "";

    cameraModels.forEach(m => {
        const opt = `<option value="${m.id}">${m.model_name} (${m.equipment_designation || ''})</option>`;
        if (scanSelect) scanSelect.innerHTML += opt;
        if (filterSelect) filterSelect.innerHTML += opt;
        if (assignSelect) assignSelect.innerHTML += opt;
    });

    if (currentScanVal && scanSelect) scanSelect.value = currentScanVal;
    if (currentFilterVal && filterSelect) filterSelect.value = currentFilterVal;
}

function renderModelsTable() {
    const tbody = document.querySelector("#modelsTable tbody");
    tbody.innerHTML = "";
    document.getElementById("modelsCountBadge").textContent = `${cameraModels.length} modèles`;

    if (cameraModels.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="9">Aucun modèle enregistré</td></tr>`;
        return;
    }

    cameraModels.forEach(m => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${m.id}</td>
            <td style="font-weight:600;">${m.model_name}</td>
            <td>${m.equipment_designation || '—'}</td>
            <td>${m.equipment_nature || '—'}</td>
            <td>${m.category || '—'}</td>
            <td>${m.sub_category || '—'}</td>
            <td><span class="badge badge-success">${m.in_stock_count || 0}</span> / ${m.total_count || 0}</td>
            <td>
                <input type="number" class="form-control form-control-sm" style="width: 65px;" value="${m.stock_threshold ?? 5}" min="0" max="999" onchange="updateModelThreshold(${m.id}, this.value)">
            </td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteModel(${m.id})">✕</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function updateModelThreshold(modelId, threshold) {
    try {
        await window.pywebview.api.update_model_threshold(modelId, parseInt(threshold, 10) || 5);
        showToast("Seuil de stock mis à jour", "success");
        loadDashboard();
    } catch (e) {
        showToast(e.toString(), "error");
    }
}

async function handleAddModel(e) {
    e.preventDefault();
    const thresholdInput = document.getElementById("m_threshold");
    const threshold = thresholdInput ? parseInt(thresholdInput.value, 10) || 5 : 5;

    const data = {
        model_name: document.getElementById("m_name").value,
        equipment_designation: document.getElementById("m_desig").value,
        equipment_nature: document.getElementById("m_nature").value,
        category: document.getElementById("m_cat").value,
        sub_category: document.getElementById("m_subcat").value
    };

    try {
        const res = await window.pywebview.api.add_camera_model(data);
        if (res.success) {
            if (res.id && threshold !== 5) {
                await window.pywebview.api.update_model_threshold(res.id, threshold);
            }
            showToast("Modèle ajouté avec succès !", "success");
            document.getElementById("addModelForm").reset();
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur d'ajout", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function deleteModel(id) {
    if (!confirm("Voulez-vous supprimer ce modèle ?")) return;
    try {
        const res = await window.pywebview.api.delete_camera_model(id);
        if (res.success) {
            showToast("Modèle supprimé", "success");
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Impossible de supprimer", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Clients Management ---
async function loadClientsTable() {
    const search = document.getElementById("clientSearchInput").value;
    try {
        const res = await window.pywebview.api.get_clients(search);
        const tbody = document.querySelector("#clientsTable tbody");
        tbody.innerHTML = "";

        if (!res.success || res.data.length === 0) {
            tbody.innerHTML = `<tr class="empty-row"><td colspan="5">Aucun client trouvé</td></tr>`;
            document.getElementById("clientsCountBadge").textContent = "0 clients";
            updateClientActionButtons(null);
            return;
        }

        clientsList = res.data;
        document.getElementById("clientsCountBadge").textContent = `${clientsList.length} clients`;

        clientsList.forEach(c => {
            const tr = document.createElement("tr");
            tr.id = `client-row-${c.id}`;
            if (selectedClientId === c.id) tr.classList.add("selected");

            const displayName = c.full_name || c.company_name || `Client #${c.id}`;
            tr.innerHTML = `
                <td>${c.id}</td>
                <td style="font-weight: 600;">${displayName}</td>
                <td>${c.phone || '—'}</td>
                <td style="font-family: monospace;">${c.doc_number || '—'}</td>
                <td><span class="badge ${c.camera_count > 0 ? 'badge-info' : ''}">${c.camera_count || 0}</span></td>
            `;

            tr.addEventListener("click", () => selectClient(c.id));
            tbody.appendChild(tr);
        });

        if (selectedClientId && !clientsList.find(c => c.id === selectedClientId)) {
            updateClientActionButtons(null);
        }
    } catch (err) {
        console.error(err);
    }
}

function selectClient(id) {
    selectedClientId = id;
    document.querySelectorAll("#clientsTable tbody tr").forEach(tr => tr.classList.remove("selected"));
    const selectedRow = document.getElementById(`client-row-${id}`);
    if (selectedRow) selectedRow.classList.add("selected");
    updateClientActionButtons(id);
}

function updateClientActionButtons(id) {
    const disabled = !id;
    document.getElementById("btnEditClient").disabled = disabled;
    document.getElementById("btnAssignCam").disabled = disabled;
    document.getElementById("btnReturnCam").disabled = disabled;
    document.getElementById("btnOpenFolder").disabled = disabled;
    document.getElementById("btnPreviewDossier").disabled = disabled;
    document.getElementById("btnGenerateDossier").disabled = disabled;
    const btnGen2 = document.getElementById("btnGenerateSecondDossier");
    if (btnGen2) btnGen2.disabled = disabled;
}

function updateClientFormTitle() {
    const title = document.getElementById("clientFormTitle");
    const submitBtn = document.getElementById("btnSaveClient");
    const editId = document.getElementById("clientIdInput").value;

    if (editId) {
        title.textContent = `${t('edit_client')}${editId}`;
        submitBtn.textContent = t('update_client');
    } else {
        title.textContent = t('register_client');
        submitBtn.textContent = t('save_client');
    }
}

function resetClientForm() {
    document.getElementById("clientForm").reset();
    document.getElementById("clientIdInput").value = "";
    document.getElementById("cf_nationality").value = "جزائرية";
    document.getElementById("cf_origin_country").value = "الصين";
    document.getElementById("cf_import_country").value = "الجزائر";
    document.getElementById("cf_transport_method").value = "بحري / جوي";
    document.getElementById("cf_security_conditions").value = "حراسة ونظام إنذار ومراقبة 24/24";
    updateClientFormTitle();
}

async function editSelectedClient() {
    if (!selectedClientId) return;
    try {
        const res = await window.pywebview.api.get_client(selectedClientId);
        if (!res.success) return;

        const c = res.client;
        document.getElementById("clientIdInput").value = c.id;
        document.getElementById("cf_full_name").value = c.full_name || "";
        document.getElementById("cf_father_name").value = c.father_name || "";
        document.getElementById("cf_mother_name").value = c.mother_name || "";
        document.getElementById("cf_dob").value = c.dob || "";
        document.getElementById("cf_pob").value = c.pob || "";
        document.getElementById("cf_nationality").value = c.nationality || "جزائرية";
        document.getElementById("cf_doc_number").value = c.doc_number || "";
        document.getElementById("cf_doc_issuer").value = c.doc_issuer || "";
        document.getElementById("cf_doc_issue_date").value = c.doc_issue_date || "";
        document.getElementById("cf_passport_number").value = c.passport_number || "";
        document.getElementById("cf_passport_issuer").value = c.passport_issuer || "";
        document.getElementById("cf_passport_expiry_date").value = c.passport_expiry_date || "";
        document.getElementById("cf_company_name").value = c.company_name || "";
        document.getElementById("cf_company_hq").value = c.company_hq || "";
        document.getElementById("cf_profession").value = c.profession || "";
        document.getElementById("cf_activity_type").value = c.activity_type || "";
        document.getElementById("cf_phone").value = c.phone || "";
        document.getElementById("cf_email").value = c.email || "";
        document.getElementById("cf_fax").value = c.fax || "";
        document.getElementById("cf_city").value = c.city || "";
        document.getElementById("cf_address").value = c.address || "";
        document.getElementById("cf_shareholders").value = c.shareholders || "";
        document.getElementById("cf_accreditation_ref").value = c.accreditation_ref || "";
        document.getElementById("cf_origin_country").value = c.origin_country || "الصين";
        document.getElementById("cf_import_country").value = c.import_country || "الجزائر";
        document.getElementById("cf_transport_method").value = c.transport_method || "بحري / جوي";
        document.getElementById("cf_storage_location").value = c.storage_location || "";
        document.getElementById("cf_security_conditions").value = c.security_conditions || "حراسة ونظام إنذار ومراقبة 24/24";

        updateClientFormTitle();
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleClientSubmit(e) {
    e.preventDefault();
    const editId = document.getElementById("clientIdInput").value;

    const data = {
        full_name: document.getElementById("cf_full_name").value,
        father_name: document.getElementById("cf_father_name").value,
        mother_name: document.getElementById("cf_mother_name").value,
        dob: document.getElementById("cf_dob").value,
        pob: document.getElementById("cf_pob").value,
        nationality: document.getElementById("cf_nationality").value,
        doc_number: document.getElementById("cf_doc_number").value,
        doc_issuer: document.getElementById("cf_doc_issuer").value,
        doc_issue_date: document.getElementById("cf_doc_issue_date").value,
        passport_number: document.getElementById("cf_passport_number").value,
        passport_issuer: document.getElementById("cf_passport_issuer").value,
        passport_expiry_date: document.getElementById("cf_passport_expiry_date").value,
        company_name: document.getElementById("cf_company_name").value,
        company_hq: document.getElementById("cf_company_hq").value,
        profession: document.getElementById("cf_profession").value,
        activity_type: document.getElementById("cf_activity_type").value,
        phone: document.getElementById("cf_phone").value,
        email: document.getElementById("cf_email").value,
        fax: document.getElementById("cf_fax").value,
        city: document.getElementById("cf_city").value,
        address: document.getElementById("cf_address").value,
        shareholders: document.getElementById("cf_shareholders").value,
        accreditation_ref: document.getElementById("cf_accreditation_ref").value,
        origin_country: document.getElementById("cf_origin_country").value,
        import_country: document.getElementById("cf_import_country").value,
        transport_method: document.getElementById("cf_transport_method").value,
        storage_location: document.getElementById("cf_storage_location").value,
        security_conditions: document.getElementById("cf_security_conditions").value
    };

    try {
        let res;
        if (editId) {
            res = await window.pywebview.api.update_client(editId, data);
            if (res.success) {
                showToast(t('client_updated'), "success");
                resetClientForm();
                loadClientsTable();
            } else {
                showToast(res.error || "Erreur de mise à jour", "error");
            }
        } else {
            res = await window.pywebview.api.save_client(data);
            if (res.success) {
                showToast(t('client_saved'), "success");
                resetClientForm();
                loadClientsTable();
                selectClient(res.id);
            } else {
                showToast(res.error || "Erreur d'enregistrement", "error");
            }
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Assign Cameras Modal Flow ---
async function openAssignModal() {
    if (!selectedClientId) return;
    const client = clientsList.find(c => c.id === selectedClientId);
    document.getElementById("assignClientInfo").textContent = 
        `Client: ${client.full_name || client.company_name} (ID: ${client.id})`;

    loadAvailableSerialsForAssign();
    openModal("assignModal");
}

async function loadAvailableSerialsForAssign() {
    const modelId = document.getElementById("assignModelSelect").value;
    const tbody = document.querySelector("#assignSerialsTable tbody");
    tbody.innerHTML = "";

    if (!modelId) {
        document.getElementById("availableSerialsCount").textContent = "0 disponible(s)";
        return;
    }

    try {
        const res = await window.pywebview.api.get_available_serials(modelId);
        if (!res.success || res.data.length === 0) {
            tbody.innerHTML = `<tr class="empty-row"><td colspan="2">Aucun numéro en stock pour ce modèle</td></tr>`;
            document.getElementById("availableSerialsCount").textContent = "0 disponible(s)";
            return;
        }

        document.getElementById("availableSerialsCount").textContent = `${res.data.length} disponible(s)`;

        res.data.forEach(s => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="text-align: center;">
                    <input type="checkbox" class="assign-checkbox" value="${s.id}">
                </td>
                <td style="font-family: monospace; font-weight: 600;">${s.serial_number}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

function toggleAllAssignCheckboxes(checked) {
    document.querySelectorAll(".assign-checkbox").forEach(cb => cb.checked = checked);
}

async function submitAssignCameras() {
    const checked = Array.from(document.querySelectorAll(".assign-checkbox:checked")).map(cb => cb.value);
    if (checked.length === 0) {
        showToast("Veuillez sélectionner au moins une caméra.", "error");
        return;
    }

    try {
        const res = await window.pywebview.api.assign_cameras(selectedClientId, checked);
        if (res.success) {
            showToast(`${res.count} ${t('cameras_assigned')}`, "success");
            closeModal("assignModal");
            loadClientsTable();
            loadInventoryTable();
            loadModels();
        } else {
            showToast(res.error || "Erreur d'assignation", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Return Cameras Modal Flow ---
async function openReturnModal() {
    if (!selectedClientId) return;
    const client = clientsList.find(c => c.id === selectedClientId);
    document.getElementById("returnClientInfo").textContent = 
        `Client: ${client.full_name || client.company_name} (ID: ${client.id})`;

    const tbody = document.querySelector("#returnSerialsTable tbody");
    tbody.innerHTML = "";

    try {
        const res = await window.pywebview.api.get_client(selectedClientId);
        const cameras = res.cameras || [];
        document.getElementById("assignedSerialsCount").textContent = `${cameras.length} assignée(s)`;

        if (cameras.length === 0) {
            tbody.innerHTML = `<tr class="empty-row"><td colspan="3">Aucune caméra assignée à ce client</td></tr>`;
            openModal("returnModal");
            return;
        }

        cameras.forEach(c => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="text-align: center;">
                    <input type="checkbox" class="return-checkbox" value="${c.serial_number}">
                </td>
                <td style="font-family: monospace; font-weight: 600;">${c.serial_number}</td>
                <td>${c.model_name || '—'}</td>
            `;
            tbody.appendChild(tr);
        });

        openModal("returnModal");
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

function toggleAllReturnCheckboxes(checked) {
    document.querySelectorAll(".return-checkbox").forEach(cb => cb.checked = checked);
}

async function submitReturnCameras() {
    const checked = Array.from(document.querySelectorAll(".return-checkbox:checked")).map(cb => cb.value);
    if (checked.length === 0) {
        showToast("Veuillez cocher au moins une caméra à retourner.", "error");
        return;
    }

    try {
        const res = await window.pywebview.api.return_cameras(checked);
        if (res.success) {
            showToast(`${res.count} ${t('cameras_returned')}`, "success");
            closeModal("returnModal");
            loadClientsTable();
            loadInventoryTable();
            loadModels();
        } else {
            showToast(res.error || "Erreur de retour", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Dossier & PDF Generation ---
let currentDossierMode = 1;

function selectDossierMode(mode) {
    currentDossierMode = mode;
    const pill1 = document.getElementById("pillDossier1");
    const pill2 = document.getElementById("pillDossier2");
    if (mode === 1) {
        if (pill1) pill1.classList.add("active");
        if (pill2) pill2.classList.remove("active");
    } else {
        if (pill1) pill1.classList.remove("active");
        if (pill2) pill2.classList.add("active");
    }
}

function updateDossierModalButtons(isSecond = false) {
    const titleEl = document.getElementById("dossierModalTitle");
    const subEl = document.getElementById("dossierModalSubtitle");
    const container = document.getElementById("dossierFilesButtonContainer");
    if (!container) return;

    if (isSecond) {
        if (titleEl) titleEl.textContent = currentLang === 'ar' ? "تم إنشاء الملف الثاني بنجاح !" : "2ème Dossier Généré avec Succès !";
        if (subEl) subEl.textContent = currentLang === 'ar' ? "تم استخراج الملحق 3 (الجدول الممتد) والملحق 8 ومحضر التثبيت." : "L'Annexe 3 (Tableau Étendu), l'Annexe 8 et le PV ont été générés.";
        container.innerHTML = `
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex3" onclick="openAnnex3Pdf()">
                📄 <span>${t('view_annex3')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex8" onclick="openAnnex8Pdf()">
                📄 <span>${t('view_annex8')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenPvPose" onclick="openPvPosePdf()">
                📋 <span>${t('view_pv_pose')}</span>
            </button>
        `;
    } else {
        if (titleEl) titleEl.textContent = currentLang === 'ar' ? "تم إنشاء الملف الأول بنجاح !" : "1er Dossier Généré avec Succès !";
        if (subEl) subEl.textContent = currentLang === 'ar' ? "تم استخراج الملحق 1 والملحق 5 ومحضر التثبيت." : "Les formulaires officiels (Annexes 1 & 5) ont été tamponnés avec succès.";
        container.innerHTML = `
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex1" onclick="openAnnex1Pdf()">
                📄 <span>${t('view_annex1')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex5" onclick="openAnnex5Pdf()">
                📄 <span>${t('view_annex5')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenPvPose" onclick="openPvPosePdf()">
                📋 <span>${t('view_pv_pose')}</span>
            </button>
        `;
    }
}

async function generateDossierForSelectedClient() {
    if (!selectedClientId) return;
    const btn = document.getElementById("btnGenerateDossier");
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span>⏳</span> <span>Génération...</span>`;

    try {
        const res = await window.pywebview.api.generate_client_dossier(selectedClientId);
        if (res.success) {
            lastGeneratedDossier = res;
            document.getElementById("dossierClientName").textContent = res.client_name;
            updateDossierModalButtons(false);
            openModal("dossierModal");
            showToast(currentLang === 'ar' ? "تم إنشاء الملف الأول بنجاح !" : "1er Dossier généré avec succès !", "success");
        } else {
            showToast(res.error || "Erreur de génération", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function generateSecondDossierForSelectedClient() {
    if (!selectedClientId) return;
    const btn = document.getElementById("btnGenerateSecondDossier");
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span>⏳</span> <span>Génération...</span>`;

    try {
        const res = await window.pywebview.api.generate_second_dossier(selectedClientId);
        if (res.success) {
            lastGeneratedDossier = res;
            document.getElementById("dossierClientName").textContent = res.client_name;
            updateDossierModalButtons(true);
            openModal("dossierModal");
            showToast(currentLang === 'ar' ? "تم إنشاء الملف الثاني (الملحق 3 و 8) بنجاح !" : "2ème Dossier généré avec succès !", "success");
        } else {
            showToast(res.error || "Erreur de génération", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function openSelectedClientFolder() {
    if (!selectedClientId) return;
    try {
        await window.pywebview.api.open_client_folder(selectedClientId);
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function openGeneratedFolder() {
    if (lastGeneratedDossier && lastGeneratedDossier.folder) {
        await window.pywebview.api.open_file(lastGeneratedDossier.folder);
    }
}

async function openAnnex1Pdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.annex1) {
        await window.pywebview.api.open_file(lastGeneratedDossier.annex1);
    }
}

async function openAnnex5Pdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.annex5) {
        await window.pywebview.api.open_file(lastGeneratedDossier.annex5);
    }
}

async function openAnnex3Pdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.annex3) {
        await window.pywebview.api.open_file(lastGeneratedDossier.annex3);
    }
}

async function openAnnex8Pdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.annex8) {
        await window.pywebview.api.open_file(lastGeneratedDossier.annex8);
    }
}

async function openPvPosePdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.pv_reception) {
        await window.pywebview.api.open_file(lastGeneratedDossier.pv_reception);
    }
}

// --- High-Resolution In-App PDF Previewer (R3) ---
let previewCurrentClientId = null;
let previewCurrentDocType = "annex1";
let previewCurrentPage = 1;
let previewTotalPages = 1;
let previewPagesData = [];
let previewZoomScale = 1.0;

async function openSelectedClientPreview() {
    if (!selectedClientId) return;
    previewCurrentClientId = selectedClientId;
    loadDocumentPreview(selectedClientId, previewCurrentDocType);
}

function openLastGeneratedPreview() {
    if (selectedClientId) {
        closeModal("dossierModal");
        openSelectedClientPreview();
    }
}

async function loadDocumentPreview(clientId, docType = "annex1") {
    previewCurrentClientId = clientId;
    previewCurrentDocType = docType;
    openModal("pdfPreviewModal");

    const spinner = document.getElementById("pdfLoadingSpinner");
    const img = document.getElementById("pdfPageImg");
    
    if (spinner) spinner.style.display = "flex";
    if (img) img.style.display = "none";

    document.querySelectorAll(".pdf-tab").forEach(tab => {
        tab.classList.toggle("active", tab.getAttribute("data-doctype") === docType);
    });

    try {
        const res = await window.pywebview.api.get_document_preview(clientId, docType);
        if (spinner) spinner.style.display = "none";

        if (res.success && res.pages && res.pages.length > 0) {
            previewPagesData = res.pages;
            previewTotalPages = res.page_count || res.pages.length;
            previewCurrentPage = 1;
            const titleEl = document.getElementById("pdfPreviewTitle");
            const badgeEl = document.getElementById("pdfPreviewClientBadge");
            if (titleEl) titleEl.textContent = res.title || "Aperçu Document";
            if (badgeEl) badgeEl.textContent = res.client_name || `Client #${clientId}`;
            renderPreviewPage();
            if (img) img.style.display = "inline-block";
        } else {
            showToast(res.error || "Impossible de générer l'aperçu", "error");
            closeModal("pdfPreviewModal");
        }
    } catch (err) {
        if (spinner) spinner.style.display = "none";
        showToast(err.toString(), "error");
    }
}

function renderPreviewPage() {
    if (previewPagesData.length === 0) return;
    const pageIndex = Math.max(0, Math.min(previewPagesData.length - 1, previewCurrentPage - 1));
    const img = document.getElementById("pdfPageImg");
    if (img) img.src = previewPagesData[pageIndex];

    const indicator = document.getElementById("pdfPageIndicator");
    if (indicator) indicator.textContent = `Page ${previewCurrentPage} / ${previewTotalPages}`;

    const btnPrev = document.getElementById("btnPrevPage");
    const btnNext = document.getElementById("btnNextPage");
    if (btnPrev) btnPrev.disabled = previewCurrentPage <= 1;
    if (btnNext) btnNext.disabled = previewCurrentPage >= previewTotalPages;
}

function prevPreviewPage() {
    if (previewCurrentPage > 1) {
        previewCurrentPage--;
        renderPreviewPage();
    }
}

function nextPreviewPage() {
    if (previewCurrentPage < previewTotalPages) {
        previewCurrentPage++;
        renderPreviewPage();
    }
}

function switchPreviewDocType(docType) {
    if (previewCurrentClientId) {
        loadDocumentPreview(previewCurrentClientId, docType);
    }
}

function adjustPreviewZoom(delta) {
    previewZoomScale = Math.max(0.4, Math.min(2.5, previewZoomScale + delta));
    applyZoom();
}

function resetPreviewZoom() {
    previewZoomScale = 1.0;
    applyZoom();
}

function applyZoom() {
    const canvas = document.getElementById("pdfViewerCanvas");
    if (canvas) canvas.style.transform = `scale(${previewZoomScale})`;
    const badge = document.getElementById("pdfZoomBadge");
    if (badge) badge.textContent = `${Math.round(previewZoomScale * 100)}%`;
}

async function openCurrentPreviewExternally() {
    if (lastGeneratedDossier && previewCurrentClientId === selectedClientId) {
        if (previewCurrentDocType === "annex1" && lastGeneratedDossier.annex1) {
            await window.pywebview.api.open_file(lastGeneratedDossier.annex1);
            return;
        } else if (previewCurrentDocType === "annex5" && lastGeneratedDossier.annex5) {
            await window.pywebview.api.open_file(lastGeneratedDossier.annex5);
            return;
        } else if (previewCurrentDocType === "annex3" && lastGeneratedDossier.annex3) {
            await window.pywebview.api.open_file(lastGeneratedDossier.annex3);
            return;
        } else if (previewCurrentDocType === "annex8" && lastGeneratedDossier.annex8) {
            await window.pywebview.api.open_file(lastGeneratedDossier.annex8);
            return;
        } else if (previewCurrentDocType === "pv_pose" && lastGeneratedDossier.pv_reception) {
            await window.pywebview.api.open_file(lastGeneratedDossier.pv_reception);
            return;
        }
    }
    if (previewCurrentDocType === "annex3" || previewCurrentDocType === "annex8") {
        await generateSecondDossierForSelectedClient();
    } else {
        await generateDossierForSelectedClient();
    }
}

// --- Global Keyboard Shortcuts ---
window.addEventListener("keydown", (e) => {
    // Esc: close active modal
    if (e.key === "Escape") {
        const activeModal = document.querySelector(".modal-backdrop.active");
        if (activeModal) {
            activeModal.classList.remove("active");
            e.preventDefault();
        }
    }

    // Ctrl + F: quick search
    if ((e.ctrlKey || e.metaKey) && (e.key === "f" || e.key === "F")) {
        const activeTab = document.querySelector(".tab-pane.active");
        if (activeTab && activeTab.id === "tab-clients") {
            e.preventDefault();
            const inp = document.getElementById("clientSearchInput");
            if (inp) inp.focus();
        } else if (activeTab && activeTab.id === "tab-inventory") {
            e.preventDefault();
            const inp = document.getElementById("inventorySearchInput");
            if (inp) inp.focus();
        }
    }

    // Ctrl + N: new client
    if ((e.ctrlKey || e.metaKey) && (e.key === "n" || e.key === "N")) {
        e.preventDefault();
        navigateToTab("clients");
        resetClientForm();
        setTimeout(() => {
            const inp = document.getElementById("cf_full_name");
            if (inp) inp.focus();
        }, 120);
    }

    // Ctrl + S: save staged or save client
    if ((e.ctrlKey || e.metaKey) && (e.key === "s" || e.key === "S")) {
        const activeTab = document.querySelector(".tab-pane.active");
        if (activeTab && activeTab.id === "tab-inventory" && stagedSerials.length > 0) {
            e.preventDefault();
            saveStagedBatch();
        } else if (activeTab && activeTab.id === "tab-clients") {
            e.preventDefault();
            const form = document.getElementById("clientForm");
            if (form) form.requestSubmit();
        }
    }
});

// --- Client Dossier Directory Management ---
async function loadDossierDirectory() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const res = await window.pywebview.api.get_dossier_root_dir();
        if (res && res.success && res.path) {
            const input = document.getElementById("dossierRootInput");
            if (input) input.value = res.path;
        }
    } catch (err) {
        console.warn("Failed to load dossier root dir:", err);
    }
}

async function handleSelectDossierDir() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const res = await window.pywebview.api.select_dossier_root_dir();
        if (res && res.success && res.path) {
            const input = document.getElementById("dossierRootInput");
            if (input) input.value = res.path;
            showToast(t("folder_updated"), "success");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleOpenDossiersDir() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        await window.pywebview.api.open_dossiers_root_dir();
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Seed Demo Data ---
async function handleSeedDemoData() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        showToast("Chargement des données de démonstration...", "info");
        const res = await window.pywebview.api.seed_demo_data();
        if (res && res.success) {
            showToast(t("seed_success"), "success");
            loadDashboard();
            loadModels();
            loadInventoryTable();
            loadClientsTable();
            loadDossierDirectory();
        } else {
            showToast(res.error || "Erreur de chargement des données", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Database Maintenance ---
async function confirmClearDb() {
    if (!confirm(t("confirm_clear_prompt"))) return;
    try {
        const res = await window.pywebview.api.clear_database();
        if (res.success) {
            showToast(t("db_cleared"), "success");
            loadModels();
            loadInventoryTable();
            loadClientsTable();
            loadDashboard();
            resetClientForm();
            loadDossierDirectory();
        } else {
            showToast("Erreur lors de la réinitialisation", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- App Bootstrapping ---
window.addEventListener("pywebviewready", () => {
    switchLanguage(currentLang);
    updateSoundButtonUI();
    loadDashboard();
    loadModels();
    loadInventoryTable();
    loadClientsTable();
    loadDossierDirectory();
});

// Fallback for standalone browser testing / inspection
document.addEventListener("DOMContentLoaded", () => {
    if (!window.pywebview) {
        switchLanguage(currentLang);
        updateSoundButtonUI();
    }
});
