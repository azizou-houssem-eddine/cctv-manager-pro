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
        qa_import_csv: "Importer Excel / CSV",
        qa_import_csv_sub: "Chargement de modèles et sérials",
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
        btn_import_unified: "Importer Excel / CSV",
        btn_import_catalog: "Importer Catalogue (Excel)",
        unified_import_title: "Importation Intelligente (Excel / CSV)",
        templates_hint: "Modèles types à télécharger :",
        tpl_catalog: "Modèle Catalogue (.xlsx)",
        tpl_manifest: "Modèle Manifeste (.xlsx)",
        unified_dropzone_prompt: "Glissez-déposez votre fichier Excel ou CSV ici",
        unified_dropzone_sub: "Détection automatique : Catalogue Modèles, Manifeste de Livraison (Modèle + N° Série) ou Numéros de Série.",
        new_models_found: "Nouveaux modèles:",
        mode_catalog_title: "Catalogue de Modèles",
        mode_manifest_title: "Manifeste de Livraison (Modèles + Séries)",
        mode_serials_title: "Numéros de Série Unitaires",
        backup_restore_title: "Sauvegarde & Restauration",
        backup_restore_desc: "Créez des instantanés fiables de la base de données SQLite, exportez vers un support externe ou restaurez un fichier.",
        btn_create_backup: "Créer Sauvegarde",
        btn_export_backup: "Exporter vers...",
        btn_restore_backup: "Restaurer...",
        btn_open_backups: "Dossier",
        installer_seal_title: "Cachet & Signature de l'Installateur",
        enable_seal_stamping: "Tampon Automatique",
        installer_seal_desc: "Apposez automatiquement le cachet officiel et la signature de votre entreprise sur tous les documents PDF générés.",
        installer_company_name: "Nom de l'Entreprise d'Installation",
        installer_seal_image: "Cachet Officiel (PNG/JPG)",
        installer_signature_image: "Signature Numérique (PNG/JPG)",
        btn_choose: "Choisir",
        btn_save_installer: "Enregistrer le Profil Installateur",
        backup_created: "Sauvegarde créée avec succès !",
        backup_restored: "Base de données restaurée avec succès !",
        installer_saved: "Profil et cachet enregistrés !",
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
        seed_success: "Données de démonstration chargées avec succès !",
        scan_mode_direct: "Direct (Auto-Save)",
        scan_mode_batch: "Par Lot (Staging)",
        session_scanned: "Session",
        validate_btn: "Valider",
        filter_all: "Tous",
        filter_in_stock: "En Stock",
        filter_assigned: "Assignés",
        delete_selected: "Supprimer",
        delete_serial_confirm: "Voulez-vous vraiment supprimer ce numéro de série de l'inventaire ?",
        delete_batch_confirm: "Voulez-vous supprimer les {count} numéros de série sélectionnés ?",
        serial_deleted: "Numéro de série supprimé.",
        serials_deleted_batch: "{count} numéro(s) de série supprimé(s).",
        cannot_delete_assigned: "Ce numéro est assigné à un client et ne peut pas être supprimé.",
        scan_direct_saved: "Série '{sn}' enregistrée en stock !",
        scan_direct_duplicate: "Numéro '{sn}' déjà existant !",
        add_model_quick_btn: "Ajouter un Modèle",
        new_model_btn: "Nouveau",
        add_model_quick_title: "➕ Ajouter un Modèle au Catalogue",
        scan_to_assign_label: "Scanner Directement une Caméra (Lecteur Code-barres) :",
        assign_btn: "Assigner",
        or_model_selection: "Ou sélection / tirage par modèle",
        quick_qty_label: "Prendre au hasard :",
        units_label: "unités",
        btn_auto_pick: "Cocher N",
        btn_auto_assign: "Assigner N Direct",
        auto_assigned_success: "{count} caméra(s) {model} assignée(s) avec succès !",
        tab_identity: "Identité",
        tab_documents: "Documents",
        tab_corporate: "Entreprise",
        tab_logistics: "Logistique",
        step_next: "Suivant",
        step_prev: "Précédent",
        btn_new_client: "Nouveau Client",
        no_client_selected_hint: "Sélectionnez un client dans la liste pour activer les actions.",
        action_group_equipment: "Équipements",
        action_group_dossiers: "Dossiers Réglementaires",
        action_group_management: "Fichiers & Modif",
        kpi_models: "Modèles de Caméras",
        kpi_catalog_references: "Références au catalogue",
        recent_clients_title: "Derniers Clients Enregistrés",
        recent_activity_badge: "Activité Récente",
        no_recent_clients: "Aucune activité récente",
        view_all_clients: "Voir Tous les Clients →",
        client_equipment_title: "Équipements Assignés",
        no_equipment_assigned: "Aucun équipement assigné à ce client.",
        assignment_date: "Date d'Affectation",
        dossier_completeness_title: "Conformité Dossier Réglementaire (Annexe 5)",
        delete_client: "Supprimer",
        confirm_delete_client: "Voulez-vous vraiment supprimer ce client ? Toutes ses caméras assignées seront remises en stock.",
        client_deleted_success: "Client supprimé avec succès.",
        scan_to_return_label: "Scanner une Caméra à Retourner :",
        btn_check: "Cocher",
        edit_model_title: "Modifier le Modèle de Caméra",
        model_updated_success: "Modèle mis à jour avec succès !",
        installer_city: "Ville / Wilaya de Signature",
        installer_name: "Nom du Responsable / Installateur",
        installer_phone: "Téléphone de Contact",
        model_name: "Nom Commercial / Référence: *",
        model_designation: "Désignation Réglementaire (Arabe):",
        model_nature: "Nature Technique:",
        model_category: "Section Réglementaire (القسم):",
        model_subcategory: "Sous-Section (الفرع):",
        stock_threshold_label: "Seuil Minimal d'Alerte Stock:",
        save_changes: "Enregistrer les Modifications",
        client_name: "Client / Société",
        doc_number: "N° Pièce / RC",
        equipment_count: "Caméras",
        action: "Action",
        doc_agreement: "Agrément",
        installer_accreditation_ref: "Réf. / N° d'Agrément",
        installer_accreditation_date: "Date de l'Agrément",
        installer_agreement_doc: "Document Officiel d'Agrément (PDF ou Image, 1 ou 2 pages)",
        agreement_doc_badge_custom: "Agrément personnalisé chargé",
        agreement_doc_badge_none: "Aucun document chargé",
        installer_agreement_hint: "Chaque installateur doit charger son propre document officiel d'agrément (1 ou 2 pages). La mention réglementaire « تسلم نسخة واحدة إلى السيد... » et le cachet de l'opérateur agréé seront apposés au bas de chaque page au format A4.",
        view_agreement: "Afficher l'Agrément",
        inv_tab_serials: "Numéros de Série & Scannage",
        inv_tab_serials_desc: "Lecteur code-barres & stock matériel",
        inv_tab_models: "Modèles & Catalogue",
        inv_tab_models_desc: "Catalogue des références & seuils",
        stat_total_models: "Modèles au Catalogue",
        stat_total_stock: "Total Caméras en Stock",
        stat_alert_models: "Modèles sous le Seuil",
        scan_this_model: "Scanner des caméras pour ce modèle",
        catalog_moved_title: "Gestion du Catalogue & Modèles de Caméras",
        catalog_moved_desc: "Les modèles de caméras, leurs désignations réglementaires et leurs seuils d'alerte sont désormais centralisés dans l'onglet Inventaire.",
        go_to_models_btn: "Accéder aux Modèles →",
        search_models_placeholder: "🔍 Filtrer les modèles, désignations...",
        // Licensing, Onboarding & Interactive Tour
        license_active: "Licence Pro",
        license_expired: "Licence Expirée",
        license_unactivated: "Non Activée",
        license_tampered: "Alerte Horloge",
        settings_license_title: "Licence Logicielle",
        settings_license_desc: "Informations sur l'activation et la validité de la licence sur ce poste de travail.",
        lic_modal_title: "Activation de la Licence Logicielle",
        lic_machine_id: "Identifiant Unique Machine",
        lic_expiry_label: "Date d'expiration",
        lic_days_left_label: "Jours Restants",
        lic_key_input_label: "Clé de Licence",
        lic_key_hint: "Format : YYYYMMDD-<SIGNATURE> (clé signée fournie par l'éditeur)",
        lic_lifetime: "Licence Permanente (À Vie)",
        lic_days_count: "{days} jours restants",
        btn_renew_license: "Renouveler / Changer la Clé",
        btn_activate: "Activer la Licence",
        btn_copy: "Copier",
        copied: "Copié !",
        onboarding_title: "Bienvenue sur CCTV Manager Pro",
        onboarding_sub: "Configuration initiale & mise en conformité réglementaire",
        reg_conform_badge: "Conforme Décret Exécutif 16-61 & JORADP",
        welcome_hero_title: "Gestion Intégrale de vos Équipements & Dossiers Réglementaires",
        welcome_hero_desc: "CCTV Manager Pro automatise la traçabilité des caméras par code-barres et édite instantanément les documents officiels conformes à la réglementation algérienne.",
        feat_dossier1_title: "1er Dossier - Acquisition",
        feat_dossier1_desc: "Annexes 1 et 5 (J.O #54), Agrément installateur tamponné et PV d'installation officiel.",
        feat_dossier2_title: "2ème Dossier - Exploitation",
        feat_dossier2_desc: "Annexe 3 étendue (15 lignes) et Annexe 8 (Engagement de non-connexion Internet Décret 16-61).",
        feat_scanner_title: "Inventaire & Code-Barres",
        feat_scanner_desc: "Numérisation ultra-rapide des numéros de série par douchette code-barres et gestion des stocks.",
        feat_seal_title: "Tamponnage Numérique",
        feat_seal_desc: "Incrustation vectorielle haute précision de votre cachet officiel et signature sur chaque page.",
        step2_title: "Activation de la Licence du Poste",
        step2_desc: "Ce logiciel est protégé par une signature matérielle liée à votre machine. Veuillez activer votre licence pour continuer.",
        lic_req_title: "Licence Requise",
        lic_req_desc: "Transmettez votre identifiant machine à votre fournisseur pour obtenir votre clé d'activation.",
        lic_success_title: "Licence Validée !",
        step3_title: "Profil de l'Entreprise d'Installation",
        step3_desc: "Ces informations légales seront apposées sur les annexes réglementaires et PV d'installation.",
        step4_title: "Emplacement des Dossiers & Démarrage",
        step4_desc: "Dernière étape ! Définissez l'emplacement racine où seront générés automatiquement les dossiers des clients.",
        seed_demo_label: "Charger des données de démonstration (Recommandé)",
        seed_demo_desc: "Injecte des modèles de caméras courants (Hikvision, Dahua), des numéros de série et un client exemple pour explorer immédiatement l'application.",
        btn_choose_seal: "Choisir Cachet (Image)",
        onb_dossier_hint: "Sous-dossiers automatiques créés pour chaque client : <Client>/1er dossier/ et <Client>/2eme dossier/.",
        btn_prev: "Précédent",
        btn_next: "Suivant"
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
        qa_import_csv: "استيراد Excel / CSV",
        qa_import_csv_sub: "تحميل الموديلات والأرقام التسلسلية",
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
        btn_import_unified: "استيراد Excel / CSV",
        btn_import_catalog: "استيراد الكتالوج (Excel)",
        unified_import_title: "الاستيراد الذكي (Excel / CSV)",
        templates_hint: "نماذج جاهزة للتحميل :",
        tpl_catalog: "نموذج الكتالوج (.xlsx)",
        tpl_manifest: "نموذج بيان التسليم (.xlsx)",
        unified_dropzone_prompt: "اسحب وأفلت ملف Excel أو CSV هنا",
        unified_dropzone_sub: "كشف تلقائي: كتالوج الموديلات، بيان التسليم (الموديل + الرقم التسلسلي) أو الأرقام التسلسلية.",
        new_models_found: "موديلات جديدة:",
        mode_catalog_title: "كتالوج الموديلات",
        mode_manifest_title: "بيان تسليم (موديلات + أرقام تسلسلية)",
        mode_serials_title: "أرقام تسلسلية أحادية",
        backup_restore_title: "النسخ الاحتياطي والاستعادة",
        backup_restore_desc: "إنشاء نسخ احتياطية آمنة لقاعدة البيانات، التصدير إلى قرص خارجي أو استعادة ملف موجود.",
        btn_create_backup: "إنشاء نسخة احتياطية",
        btn_export_backup: "تصدير إلى...",
        btn_restore_backup: "استعادة...",
        btn_open_backups: "المجلد",
        installer_seal_title: "ختم وتوقيع القائم بالتركيب",
        enable_seal_stamping: "الختم التلقائي",
        installer_seal_desc: "ختم وتوقيع المستندات الرسمية بصيغة PDF تلقائياً باسم وبيانات شركتكم.",
        installer_company_name: "اسم شركة التثبيت والتركيب",
        installer_seal_image: "الختم الرسمي (PNG/JPG)",
        installer_signature_image: "التوقيع الرقمي (PNG/JPG)",
        btn_choose: "اختيار",
        btn_save_installer: "حفظ الملف التعريفي للقائم بالتركيب",
        backup_created: "تم إنشاء النسخة الاحتياطية لقاعدة البيانات بنجاح !",
        backup_restored: "تمت استعادة قاعدة البيانات بنجاح !",
        installer_saved: "تم حفظ بيانات وختم القائم بالتركيب بنجاح !",
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
        seed_success: "تم شحن البيانات النموذجية بنجاح!",
        scan_mode_direct: "المسح المباشر (حفظ فوري)",
        scan_mode_batch: "مسح بالدفعات (تجميع)",
        session_scanned: "الجلسة",
        validate_btn: "تأكيد",
        filter_all: "الكل",
        filter_in_stock: "في المخزن",
        filter_assigned: "مركب / مخصص",
        delete_selected: "حذف",
        delete_serial_confirm: "هل أنت متأكد من حذف هذا الرقم التسلسلي من المخزون؟",
        delete_batch_confirm: "هل أنت متأكد من حذف {count} رقماً تسلسلياً محدداً؟",
        serial_deleted: "تم حذف الرقم التسلسلي بنجاح.",
        serials_deleted_batch: "تم حذف {count} رقماً تسلسلياً.",
        cannot_delete_assigned: "هذا الرقم التسلسلي مخصص لعميل ولا يمكن حذفه.",
        scan_direct_saved: "تم حفظ الرقم '{sn}' مباشرة في المخزن !",
        scan_direct_duplicate: "الرقم '{sn}' موجود مسبقاً !",
        add_model_quick_btn: "إضافة طراز جديد",
        new_model_btn: "طراز جديد",
        add_model_quick_title: "➕ إضافة طراز إلى الكتالوج",
        scan_to_assign_label: "مسح الكاميرا مباشرة للعميل (قارئ الباركود) :",
        assign_btn: "تخصيص",
        or_model_selection: "أو اختيار / سحب حسب الطراز",
        quick_qty_label: "سحب عشوائي :",
        units_label: "كاميرات",
        btn_auto_pick: "تحديد N",
        btn_auto_assign: "تخصيص N مباشرة",
        auto_assigned_success: "تم تخصيص {count} كاميرا {model} بنجاح !",
        tab_identity: "الهوية",
        tab_documents: "وثائق الهوية",
        tab_corporate: "الشركة",
        tab_logistics: "اللوجستيات",
        step_next: "التالي",
        step_prev: "السابق",
        btn_new_client: "عميل جديد",
        no_client_selected_hint: "حدد عميلاً من القائمة لتفعيل الإجراءات ومتابعة الملف.",
        action_group_equipment: "المعدات",
        action_group_dossiers: "الملفات الرسمية",
        action_group_management: "الملفات والتعديل",
        kpi_models: "طرازات الكاميرات",
        kpi_catalog_references: "المراجع المسجلة في الدليل",
        recent_clients_title: "آخر الزبائن المسجلين",
        recent_activity_badge: "نشاط حديث",
        no_recent_clients: "لا يوجد نشاط حديث",
        view_all_clients: "عرض جميع الزبائن ←",
        client_equipment_title: "المعدات المعينة",
        no_equipment_assigned: "لا توجد معدات معينة لهذا الزبون.",
        assignment_date: "تاريخ التعيين",
        dossier_completeness_title: "مطابقة الملف التنظيمي (الملحق 5)",
        delete_client: "حذف",
        confirm_delete_client: "هل أنت متأكد من حذف هذا الزبون؟ ستتم إعادة جميع الكاميرات المعينة له إلى المخزن.",
        client_deleted_success: "تم حذف الزبون بنجاح.",
        scan_to_return_label: "مسح كاميرا لإعادتها إلى المخزن :",
        btn_check: "تحديد",
        edit_model_title: "تعديل طراز الكاميرا",
        model_updated_success: "تم تحديث الطراز بنجاح !",
        installer_city: "مدينة / ولاية التوقيع",
        installer_name: "اسم المسؤول / القائم بالتركيب",
        installer_phone: "هاتف الاتصال",
        model_name: "الاسم التجاري / المرجع: *",
        model_designation: "التسمية التنظيمية (عربي):",
        model_nature: "الطبيعة التقنية:",
        model_category: "القسم التنظيمي (القسم):",
        model_subcategory: "الفرع التنظيمي (الفرع):",
        stock_threshold_label: "الحد الأدنى لتنبيه المخزون:",
        save_changes: "حفظ التعديلات",
        client_name: "الزبون / الشركة",
        doc_number: "رقم الوثيقة / السجل التجاري",
        equipment_count: "الكاميرات",
        action: "الإجراء",
        doc_agreement: "رخصة الاعتماد",
        installer_accreditation_ref: "مرجع / رقم الاعتماد",
        installer_accreditation_date: "تاريخ الاعتماد",
        installer_agreement_doc: "الوثيقة الرسمية للاعتماد (PDF أو صورة، صفحة واحدة أو صفحتين)",
        agreement_doc_badge_custom: "تم تحميل وثيقة الاعتماد الخاصة",
        agreement_doc_badge_none: "لم يتم تحميل وثيقة الاعتماد",
        installer_agreement_hint: "يجب على كل مركب تحميل رخصة الاعتماد الخاصة به (صفحة واحدة أو صفحتين). ستتم كتابة العبارة التنظيمية «تسلم نسخة واحدة إلى السيد...» مع ختم وتوقيع المتعامل المعتمد أسفل كل صفحة مع الحفاظ على مقاس A4.",
        view_agreement: "عرض رخصة الاعتماد",
        inv_tab_serials: "الأرقام التسلسلية والمسح",
        inv_tab_serials_desc: "قارئ الباركود ومخزون الأجهزة",
        inv_tab_models: "نماذج الكاميرات والدليل",
        inv_tab_models_desc: "دليل الطرازات وحدود التنبيه",
        stat_total_models: "الموديلات في الدليل",
        stat_total_stock: "إجمالي الكاميرات في المخزن",
        stat_alert_models: "موديلات تحت الحد الأدنى",
        scan_this_model: "مسح كاميرات لهذا الطراز",
        catalog_moved_title: "إدارة دليل نماذج الكاميرات",
        catalog_moved_desc: "أصبحت موديلات الكاميرات والتسميات التنظيمية وحدود التنبيه مجمعة في شاشة المخزون.",
        go_to_models_btn: "الانتقال إلى الموديلات ←",
        search_models_placeholder: "🔍 تصفية الموديلات والتسميات...",
        // Licensing, Onboarding & Interactive Tour
        license_active: "ترخيص مفعل",
        license_expired: "الترخيص منتهي",
        license_unactivated: "غير مفعل",
        license_tampered: "تنبيه في الساعة",
        settings_license_title: "ترخيص البرنامج",
        settings_license_desc: "معلومات تفعيل وصلاحية الترخيص على محطة العمل الحالية.",
        lic_modal_title: "تفعيل ترخيص البرنامج",
        lic_machine_id: "المعرّف الفريد للجهاز",
        lic_expiry_label: "تاريخ انتهاء الصلاحية",
        lic_days_left_label: "الأيام المتبقية",
        lic_key_input_label: "مفتاح الترخيص",
        lic_key_hint: "الصيغة: YYYYMMDD-<التوقيع> (مفتاح موقّع من المورّد)",
        lic_lifetime: "ترخيص دائم (مدى الحياة)",
        lic_days_count: "{days} يوماً متبقياً",
        btn_renew_license: "تجديد / تغيير المفتاح",
        btn_activate: "تفعيل الترخيص",
        btn_copy: "نسخ",
        copied: "تم النسخ !",
        onboarding_title: "مرحبًا بك في CCTV Manager Pro",
        onboarding_sub: "الإعداد الأولي والمطابقة التنظيمية الجزائرية",
        reg_conform_badge: "مطابق للمرسوم التنفيذي 16-61 والجريدة الرسمية",
        welcome_hero_title: "إدارة شاملة لمعدات وتراخيص كاميرات المراقبة الحساسة",
        welcome_hero_desc: "نظام احترافي يتيح التتبع الفوري للأرقام التسلسلية بالباركود وطباعة الملفات والوثائق التنظيمية المعتمدة رسمياً.",
        feat_dossier1_title: "الملف الأول - رخصة الاقتناء",
        feat_dossier1_desc: "الملحقان 1 و5 (ج.ر 54)، رخصة الاعتماد مختومة ومحضر استلام الأشغال الرسمي.",
        feat_dossier2_title: "الملف الثاني - رخصة الاستغلال",
        feat_dossier2_desc: "الملحق 3 الموسع (15 سطراً) والملحق 8 (تعهد بعدم ربط التجهيزات الحساسة بالإنترنت).",
        feat_scanner_title: "المخزون وقارئ الباركود",
        feat_scanner_desc: "مسح فائق السرعة للأرقام التسلسلية عبر قارئ الباركود ومتابعة آنية للمخزون.",
        feat_seal_title: "الختم والتوقيع الرقمي",
        feat_seal_desc: "دمج عالي الدقة لختم وتوقيع المؤسسة المعتمدة على كافة صفحات الوثائق الرسمية.",
        step2_title: "تفعيل ترخيص محطة العمل",
        step2_desc: "هذا النظام محمي بتوقيع رقمي مرتبط بجهازك. يرجى تفعيل الترخيص للمتابعة.",
        lic_req_title: "الترخيص مطلوب",
        lic_req_desc: "يرجى تزويد المطور أو المورد بمعرّف جهازك للحصول على مفتاح التفعيل.",
        lic_success_title: "تم التحقق من الترخيص بنجاح !",
        step3_title: "بيانات مؤسسة التركيب والاعتماد",
        step3_desc: "ستُطبع هذه البيانات القانونية تلقائياً على كافة الملاحق التنظيمية ومحاضر التركيب.",
        step4_title: "مجلد الحفظ وبدء التشغيل",
        step4_desc: "المرحلة الأخيرة ! حدد المجلد الرئيسي لإنشاء ملفات العملاء تلقائياً.",
        seed_demo_label: "تحميل بيانات تجريبية (مستحسن)",
        seed_demo_desc: "إدراج نماذج كاميرات شائعة (Hikvision, Dahua) وأرقام تسلسلية وعميل تجريبي لاستكشاف البرنامج فوراً.",
        btn_choose_seal: "اختيار الختم (صورة)",
        onb_dossier_hint: "يتم إنشاء مجلدات فرعية لكل عميل تلقائياً: <العميل>/1er dossier/ و <العميل>/2eme dossier/.",
        btn_prev: "السابق",
        btn_next: "التالي"
    }
};

// --- Application State ---
let currentLang = localStorage.getItem("cctv_lang") || "fr";
let currentInventorySubtab = "serials"; // "serials" or "models"
let scanMode = localStorage.getItem("cctv_scan_mode") || "direct"; // "direct" or "batch"
let sessionScanCount = 0;
let inventoryStatusFilter = "all"; // "all", "in_stock", "assigned"
let selectedSerialIds = new Set();
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

function switchLanguage(lang, reloadData = true) {
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

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        el.placeholder = t(key);
    });

    // Update dynamic titles
    updateClientFormTitle();
    updateDossierCompleteness();
    setScanMode(scanMode);
    handleScanModelChange();

    // Refresh onboarding text if active
    const onbModal = document.getElementById("onboardingModal");
    if (onbModal && onbModal.classList.contains("active") && typeof goToOnbStep === "function") {
        goToOnbStep(currentOnbStep);
    }

    if (reloadData) {
        loadInventoryTable();
        loadClientsTable();
        loadDashboard();
        if (typeof renderModelsTable === "function") {
            renderModelsTable();
        }
    }
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
        loadInventoryTable();
        loadModels();
        if (currentInventorySubtab === "serials") {
            setTimeout(() => {
                const inp = document.getElementById("scannerInput");
                if (inp) inp.focus();
            }, 100);
        } else {
            setTimeout(() => {
                const searchInp = document.getElementById("modelFilterSearchInput");
                if (searchInp) searchInp.focus();
            }, 100);
        }
    }
    if (tab === "clients") loadClientsTable();
    if (tab === "settings") loadInstallerProfile();
}

function switchInventorySubtab(subtab = "serials") {
    currentInventorySubtab = subtab;
    const btnSerials = document.getElementById("invSubtabBtn_serials");
    const btnModels = document.getElementById("invSubtabBtn_models");
    const paneSerials = document.getElementById("invPane_serials");
    const paneModels = document.getElementById("invPane_models");

    if (btnSerials) btnSerials.classList.toggle("active", subtab === "serials");
    if (btnModels) btnModels.classList.toggle("active", subtab === "models");
    if (paneSerials) paneSerials.classList.toggle("active", subtab === "serials");
    if (paneModels) paneModels.classList.toggle("active", subtab === "models");

    if (subtab === "serials") {
        loadInventoryTable();
        setTimeout(() => {
            const inp = document.getElementById("scannerInput");
            if (inp) inp.focus();
        }, 100);
    } else if (subtab === "models") {
        loadModels();
        setTimeout(() => {
            const searchInp = document.getElementById("modelFilterSearchInput");
            if (searchInp) searchInp.focus();
        }, 100);
    }
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
        const modelsEl = document.getElementById("kpiModelsVal");
        const alertCard = document.getElementById("kpiAlertCard");

        const inStock = d.total_stock ?? d.totals?.total_in_stock ?? 0;
        const assigned = d.total_assigned ?? d.totals?.total_assigned ?? 0;
        const clients = d.total_clients ?? d.totals?.total_clients ?? 0;
        const totalModels = d.total_models ?? d.totals?.total_models ?? 0;
        const lowStockItems = d.low_stock_items || d.low_stock_alerts || [];
        const lowCount = d.low_stock_count ?? lowStockItems.length;

        if (stockEl) stockEl.textContent = inStock;
        if (assignedEl) assignedEl.textContent = assigned;
        if (clientsEl) clientsEl.textContent = clients;
        if (alertEl) alertEl.textContent = lowCount;
        if (modelsEl) modelsEl.textContent = totalModels;

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
                    const inStockVal = item.in_stock ?? item.in_stock_count ?? 0;
                    const thresholdVal = item.threshold ?? item.stock_threshold ?? 5;
                    const isZero = inStockVal === 0;
                    const stBadge = isZero 
                        ? `<span class="badge badge-danger">${currentLang === 'ar' ? 'نفاد (0)' : 'Rupture (0)'}</span>` 
                        : `<span class="badge badge-warning">${currentLang === 'ar' ? `مخزون منخفض (${inStockVal})` : `Stock Bas (${inStockVal})`}</span>`;
                    tr.innerHTML = `
                        <td style="font-weight: 600;">${item.model_name}</td>
                        <td>${inStockVal}</td>
                        <td>${thresholdVal}</td>
                        <td>${stBadge}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }

        const rcTbody = document.querySelector("#recentClientsTable tbody");
        if (rcTbody) {
            rcTbody.innerHTML = "";
            const recent = d.recent_clients || [];
            if (recent.length === 0) {
                rcTbody.innerHTML = `<tr class="empty-row"><td colspan="5">${t('no_recent_clients')}</td></tr>`;
            } else {
                recent.forEach(c => {
                    const tr = document.createElement("tr");
                    const name = c.full_name || c.company_name || `Client #${c.id}`;
                    const camCount = c.camera_count || 0;
                    tr.innerHTML = `
                        <td style="font-weight: 600;">${name}</td>
                        <td style="font-family: var(--font-mono); font-size: 12px;">${c.doc_number || '—'}</td>
                        <td>${c.phone || '—'}</td>
                        <td><span class="badge ${camCount > 0 ? 'badge-success' : ''}">📷 ${camCount}</span></td>
                        <td>
                            <button class="btn btn-secondary btn-sm" onclick="navigateToTab('clients'); selectClient(${c.id});" title="Voir client">
                                👁️ <span style="font-size: 11px;">${t('edit')}</span>
                            </button>
                        </td>
                    `;
                    rcTbody.appendChild(tr);
                });
            }
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

// --- Scanner & Inventory Flow ---
function setScanMode(mode) {
    scanMode = mode;
    localStorage.setItem("cctv_scan_mode", mode);
    const btnDirect = document.getElementById("btnModeDirect");
    const btnBatch = document.getElementById("btnModeBatch");
    const drawer = document.getElementById("stagedBatchDrawer");
    if (btnDirect) btnDirect.classList.toggle("active", mode === "direct");
    if (btnBatch) btnBatch.classList.toggle("active", mode === "batch");
    if (drawer) drawer.style.display = (mode === "batch") ? "block" : "none";

    const scannerInput = document.getElementById("scannerInput");
    if (scannerInput) {
        scannerInput.placeholder = (mode === "direct") 
            ? (currentLang === 'ar' ? "⚡ جاهز للمسح المباشر والحفظ التلقائي... امسح واضغط إدخال" : "⚡ Prêt pour le lecteur code-barres... Scanner ou taper et Entrée")
            : (currentLang === 'ar' ? "📋 وضع الدفعات... امسح لتجميع الأرقام ثم احفظ اللوت" : "📋 Mode lot... Scanner pour accumuler puis enregistrer");
        scannerInput.focus();
    }
}

function handleScanModelChange() {
    const scanSelect = document.getElementById("scanModelSelect");
    const pill = document.getElementById("modelStockPill");
    if (!scanSelect || !pill) return;
    const mid = parseInt(scanSelect.value, 10);
    const model = cameraModels.find(m => m.id === mid);
    if (model) {
        const inStock = model.in_stock_count || 0;
        pill.textContent = currentLang === 'ar' ? `${inStock} في المخزن` : `${inStock} en stock`;
        pill.style.display = "inline-flex";
        pill.className = `badge ${inStock > 0 ? 'badge-success' : 'badge-danger'}`;
    } else {
        pill.style.display = "none";
    }
}

const scannerInput = document.getElementById("scannerInput");
if (scannerInput) {
    scannerInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleScan(scannerInput.value);
        }
    });
}

function handleManualScanSubmit() {
    const inp = document.getElementById("scannerInput");
    if (inp) handleScan(inp.value);
}

async function handleScan(rawVal) {
    const val = rawVal.trim().toUpperCase();
    if (!val) return;

    const modelSelect = document.getElementById("scanModelSelect");
    if (!modelSelect || !modelSelect.value) {
        playScannerBeep("error");
        scannerInput.classList.add("scan-input-error");
        setTimeout(() => scannerInput.classList.remove("scan-input-error"), 400);
        showToast(t("select_model_placeholder"), "error");
        return;
    }
    const modelId = parseInt(modelSelect.value, 10);

    if (scanMode === "direct") {
        try {
            const res = await window.pywebview.api.save_single_serial_direct(modelId, val);
            if (res.success) {
                playScannerBeep("success");
                scannerInput.classList.add("scan-input-success");
                setTimeout(() => scannerInput.classList.remove("scan-input-success"), 300);
                scannerInput.value = "";

                sessionScanCount++;
                const sessionEl = document.getElementById("sessionScanCount");
                if (sessionEl) sessionEl.textContent = sessionScanCount;

                showToast(t("scan_direct_saved").replace("{sn}", val), "success");

                // Immediately reload and highlight the new row at the top
                await loadInventoryTable(res.serial_id);
                await loadModels();
                handleScanModelChange();
                loadDashboard();
            } else {
                playScannerBeep("error");
                scannerInput.classList.add("scan-input-error");
                setTimeout(() => scannerInput.classList.remove("scan-input-error"), 400);
                showToast(res.message || t("scan_direct_duplicate").replace("{sn}", val), "error");
                scannerInput.select();
            }
        } catch (err) {
            playScannerBeep("error");
            showToast(err.toString(), "error");
        }
    } else {
        // Mode Batch
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
}

function renderStagedTable() {
    const container = document.getElementById("stagedTagsContainer");
    const badge = document.getElementById("stagedCountBadge");
    if (!container) return;

    if (badge) badge.textContent = `${stagedSerials.length} scanné(s)`;

    if (stagedSerials.length === 0) {
        container.innerHTML = `<span class="empty-staged-hint">${t('no_scanned_yet')}</span>`;
        return;
    }

    container.innerHTML = "";
    stagedSerials.forEach((sn, idx) => {
        const chip = document.createElement("div");
        chip.className = "staged-chip";
        chip.innerHTML = `
            <span>${sn}</span>
            <button type="button" class="staged-chip-remove" onclick="removeStagedSerial(${idx})" title="Supprimer">✕</button>
        `;
        container.appendChild(chip);
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
    const modelId = modelSelect ? modelSelect.value : null;
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
            handleScanModelChange();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur lors de l'enregistrement", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Status Filtering & Inventory Table ---
function setInventoryStatusFilter(status) {
    inventoryStatusFilter = status;
    const pillAll = document.getElementById("pillFilterAll");
    const pillInStock = document.getElementById("pillFilterInStock");
    const pillAssigned = document.getElementById("pillFilterAssigned");

    if (pillAll) pillAll.classList.toggle("active", status === "all");
    if (pillInStock) pillInStock.classList.toggle("active", status === "in_stock");
    if (pillAssigned) pillAssigned.classList.toggle("active", status === "assigned");

    loadInventoryTable();
}

let inventorySearchTimer = null;
function debounceInventorySearch() {
    clearTimeout(inventorySearchTimer);
    inventorySearchTimer = setTimeout(() => {
        loadInventoryTable();
    }, 200);
}

async function loadInventoryTable(highlightSerialId = null) {
    const filterModel = document.getElementById("filterModelSelect")?.value || null;
    const searchInput = document.getElementById("inventorySearchInput");
    const searchQuery = searchInput ? searchInput.value.trim() : "";

    try {
        // Fetch serials using search_serials with status filter
        const res = await window.pywebview.api.search_serials(
            searchQuery || null,
            filterModel || null,
            inventoryStatusFilter === "all" ? null : inventoryStatusFilter
        );

        // Also fetch total counts across all categories to update filter badges
        const countsRes = await window.pywebview.api.search_serials(searchQuery || null, filterModel || null, null);
        if (countsRes.success && countsRes.data) {
            const allItems = countsRes.data;
            const totalCount = allItems.length;
            const inStockCount = allItems.filter(item => !item.is_used).length;
            const assignedCount = allItems.filter(item => item.is_used).length;

            const badgeTotal = document.getElementById("totalStockBadge");
            const badgeCountAll = document.getElementById("countFilterAll");
            const badgeCountInStock = document.getElementById("countFilterInStock");
            const badgeCountAssigned = document.getElementById("countFilterAssigned");
            const badgeInvSerials = document.getElementById("invSerialsCountBadge");

            if (badgeTotal) badgeTotal.textContent = `${totalCount} ${totalCount > 1 ? 'caméras' : 'caméra'}`;
            if (badgeCountAll) badgeCountAll.textContent = totalCount;
            if (badgeCountInStock) badgeCountInStock.textContent = inStockCount;
            if (badgeCountAssigned) badgeCountAssigned.textContent = assignedCount;
            if (badgeInvSerials) badgeInvSerials.textContent = totalCount;
        }

        const tbody = document.querySelector("#inventoryTable tbody");
        if (!tbody) return;
        tbody.innerHTML = "";

        if (!res.success || !res.data || res.data.length === 0) {
            tbody.innerHTML = `<tr class="empty-row"><td colspan="6">${currentLang === 'ar' ? 'لا توجد معدات في المخزون' : 'Aucun enregistrement d\'inventaire'}</td></tr>`;
            updateBatchActionUI();
            return;
        }

        res.data.forEach(item => {
            const tr = document.createElement("tr");
            tr.id = `serial-row-${item.id}`;
            if (highlightSerialId && item.id === highlightSerialId) {
                tr.classList.add("row-newly-added");
            }

            const isChecked = selectedSerialIds.has(item.id);
            if (isChecked) tr.classList.add("selected");

            const statusBadge = item.is_used 
                ? `<span class="badge badge-info"><span class="status-dot assigned-dot"></span> ${t('assigned')}</span>`
                : `<span class="badge badge-success"><span class="status-dot in-stock-dot"></span> ${t('in_stock')}</span>`;
            
            const assignedClient = item.assigned_client_name 
                ? item.assigned_client_name 
                : (item.client_name ? item.client_name : "—");

            const actionBtn = item.is_used
                ? `<span class="btn-row-action btn-row-locked" title="${t('cannot_delete_assigned')}">🔒</span>`
                : `<button type="button" class="btn-row-action btn-row-delete" onclick="handleDeleteSingleSerial(${item.id}, '${item.serial_number}')" title="${t('delete_selected')}">🗑️</button>`;

            tr.innerHTML = `
                <td style="text-align: center;" onclick="event.stopPropagation()">
                    <input type="checkbox" class="serial-checkbox" data-id="${item.id}" ${isChecked ? 'checked' : ''} onchange="handleSelectSerialRow(this, ${item.id})">
                </td>
                <td style="font-family: monospace; font-weight: 700; color: #0f172a; font-size: 13.5px;">${item.serial_number}</td>
                <td>${item.model_name}</td>
                <td>${statusBadge}</td>
                <td style="font-weight: 500;">${assignedClient}</td>
                <td style="text-align: center;" onclick="event.stopPropagation()">${actionBtn}</td>
            `;

            tbody.appendChild(tr);
        });

        updateBatchActionUI();

        // If a newly added serial was highlighted, scroll smoothly to it
        if (highlightSerialId) {
            const highlightedRow = document.getElementById(`serial-row-${highlightSerialId}`);
            if (highlightedRow) {
                highlightedRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        }
    } catch (err) {
        console.error("loadInventoryTable error:", err);
    }
}

// --- Serial Deletion Handlers ---
async function handleDeleteSingleSerial(serialId, serialNumber) {
    if (!confirm(`${t('delete_serial_confirm')}\n\nSerial : ${serialNumber}`)) return;

    try {
        const res = await window.pywebview.api.delete_serial_number(serialId);
        if (res.success) {
            showToast(t("serial_deleted"), "success");
            selectedSerialIds.delete(serialId);
            await loadInventoryTable();
            await loadModels();
            handleScanModelChange();
            loadDashboard();
        } else {
            showToast(res.message || res.error || "Erreur de suppression", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

function handleSelectSerialRow(checkbox, serialId) {
    if (checkbox.checked) {
        selectedSerialIds.add(serialId);
    } else {
        selectedSerialIds.delete(serialId);
    }
    const row = document.getElementById(`serial-row-${serialId}`);
    if (row) row.classList.toggle("selected", checkbox.checked);
    updateBatchActionUI();
}

function handleToggleSelectAllSerials(masterCheckbox) {
    const isChecked = masterCheckbox.checked;
    const checkboxes = document.querySelectorAll(".serial-checkbox");
    checkboxes.forEach(cb => {
        cb.checked = isChecked;
        const sid = parseInt(cb.getAttribute("data-id"), 10);
        if (isChecked) {
            selectedSerialIds.add(sid);
        } else {
            selectedSerialIds.delete(sid);
        }
        const row = document.getElementById(`serial-row-${sid}`);
        if (row) row.classList.toggle("selected", isChecked);
    });
    updateBatchActionUI();
}

function updateBatchActionUI() {
    const count = selectedSerialIds.size;
    const btn = document.getElementById("btnBatchDelete");
    const countSpan = document.getElementById("batchDeleteCount");
    const masterCheckbox = document.getElementById("selectAllSerialsCheckbox");

    if (countSpan) countSpan.textContent = count;
    if (btn) btn.style.display = count > 0 ? "inline-flex" : "none";

    // Update master checkbox state
    const allCheckboxes = document.querySelectorAll(".serial-checkbox");
    if (masterCheckbox && allCheckboxes.length > 0) {
        const checkedCount = document.querySelectorAll(".serial-checkbox:checked").length;
        masterCheckbox.checked = (checkedCount === allCheckboxes.length);
        masterCheckbox.indeterminate = (checkedCount > 0 && checkedCount < allCheckboxes.length);
    } else if (masterCheckbox) {
        masterCheckbox.checked = false;
        masterCheckbox.indeterminate = false;
    }
}

async function handleBatchDeleteSerials() {
    const count = selectedSerialIds.size;
    if (count === 0) return;

    if (!confirm(t("delete_batch_confirm").replace("{count}", count))) return;

    try {
        const ids = Array.from(selectedSerialIds);
        const res = await window.pywebview.api.delete_serials_batch(ids);
        if (res.success) {
            const msg = t("serials_deleted_batch").replace("{count}", res.deleted_count) + 
                (res.skipped_assigned > 0 ? ` (${res.skipped_assigned} ignorés car assignés)` : "");
            showToast(msg, "success");
            selectedSerialIds.clear();
            await loadInventoryTable();
            await loadModels();
            handleScanModelChange();
            loadDashboard();
        } else {
            showToast(res.message || res.error || "Erreur lors de la suppression groupée", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Bulk CSV/Excel Export & Import (R2) ---
async function exportFilteredSerials(format = "csv") {
    const filterModel = document.getElementById("filterModelSelect")?.value || null;
    const status = (inventoryStatusFilter === "all" || !inventoryStatusFilter) ? null : inventoryStatusFilter;
    try {
        if (format === "csv") {
            const res = await window.pywebview.api.export_serials_csv(filterModel, status);
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
            const res = await window.pywebview.api.export_serials_excel(filterModel, status);
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

// --- Unified Intelligent Excel / CSV / TXT Import Engine ---
let currentUnifiedImportResult = null;

function openUnifiedImportModal(defaultType = null) {
    const select = document.getElementById("unifiedImportModelSelect");
    if (select) {
        select.innerHTML = `<option value="">${t('select_model_placeholder')}</option>`;
        cameraModels.forEach(m => {
            select.innerHTML += `<option value="${m.id}">${m.model_name} (${m.equipment_designation || ''})</option>`;
        });
    }

    const fileInp = document.getElementById("unifiedFileInput");
    if (fileInp) fileInp.value = "";

    const banner = document.getElementById("importModeBanner");
    if (banner) banner.style.display = "none";

    const destGroup = document.getElementById("importDestinationModelGroup");
    if (destGroup) destGroup.style.display = "block";

    const summary = document.getElementById("unifiedAnalysisSummary");
    if (summary) summary.style.display = "none";

    const tableWrap = document.getElementById("unifiedPreviewTableWrapper");
    if (tableWrap) tableWrap.style.display = "none";

    const confirmBtn = document.getElementById("btnConfirmUnifiedImport");
    if (confirmBtn) confirmBtn.disabled = true;

    currentUnifiedImportResult = null;
    setupUnifiedDropzone();
    openModal("unifiedImportModal");
}

// Backwards compatibility alias
function openCsvImportModal() {
    openUnifiedImportModal();
}

function setupUnifiedDropzone() {
    const dz = document.getElementById("unifiedDropzone");
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
        if (file) handleUnifiedFile(file);
    }, false);
}

function handleUnifiedFileSelected(e) {
    const file = e.target.files[0];
    if (!file) return;
    handleUnifiedFile(file);
}

function handleUnifiedFile(file) {
    const modelSelect = document.getElementById("unifiedImportModelSelect");
    const destModelId = modelSelect ? modelSelect.value : null;

    showToast("Analyse du fichier en cours...", "info");
    const reader = new FileReader();

    reader.onload = async (event) => {
        const dataUri = event.target.result;
        try {
            const res = await window.pywebview.api.preview_unified_import({
                file_data: dataUri,
                filename: file.name,
                destination_model_id: destModelId
            });

            if (res.success) {
                currentUnifiedImportResult = res;
                renderUnifiedPreview(res);
            } else {
                showToast(res.error || "Erreur lors de l'analyse du fichier", "error");
            }
        } catch (err) {
            showToast(err.toString(), "error");
        }
    };

    // Use readAsDataURL uniformly to preserve binary Excel workbooks and text encoding
    reader.readAsDataURL(file);
}

function renderUnifiedPreview(res) {
    const mode = res.mode || "SERIALS_ONLY";
    const banner = document.getElementById("importModeBanner");
    const modeText = document.getElementById("importModeText");
    const modeIcon = document.getElementById("importModeIcon");
    const modeSub = document.getElementById("importModeSubBadge");
    const destGroup = document.getElementById("importDestinationModelGroup");

    banner.className = "import-mode-banner";
    if (mode === "MODELS_CATALOG") {
        banner.classList.add("mode-banner-catalog");
        modeIcon.textContent = "📑";
        modeText.textContent = t("mode_catalog_title");
        modeSub.textContent = `${res.valid_items.length} modèle(s)`;
        if (destGroup) destGroup.style.display = "none";
    } else if (mode === "COMBINED_MANIFEST") {
        banner.classList.add("mode-banner-manifest");
        modeIcon.textContent = "📦";
        modeText.textContent = t("mode_manifest_title");
        modeSub.textContent = `${res.valid_items.length} caméra(s)`;
        if (destGroup) destGroup.style.display = "none";
    } else {
        banner.classList.add("mode-banner-serials");
        modeIcon.textContent = "⚡";
        modeText.textContent = t("mode_serials_title");
        modeSub.textContent = `${res.valid_items.length} sérial(s)`;
        if (destGroup) destGroup.style.display = "block";
    }
    banner.style.display = "flex";

    // Summary counts
    document.getElementById("importStatTotal").textContent = res.total_detected || 0;
    document.getElementById("importStatValid").textContent = res.valid_items ? res.valid_items.length : 0;
    document.getElementById("importStatDupFile").textContent = res.duplicates_in_file ? res.duplicates_in_file.length : 0;
    document.getElementById("importStatInDb").textContent = res.already_in_db ? res.already_in_db.length : 0;

    const newModelsGroup = document.getElementById("importStatNewModelsGroup");
    const newModelsStat = document.getElementById("importStatNewModels");
    if (res.new_models_to_create && res.new_models_to_create.length > 0) {
        newModelsStat.textContent = res.new_models_to_create.length;
        newModelsGroup.style.display = "block";
    } else {
        newModelsGroup.style.display = "none";
    }

    document.getElementById("unifiedAnalysisSummary").style.display = "flex";

    // Table Header & Rows
    const thead = document.getElementById("unifiedPreviewTableHead");
    const tbody = document.querySelector("#unifiedPreviewTable tbody");
    thead.innerHTML = "";
    tbody.innerHTML = "";

    if (mode === "MODELS_CATALOG") {
        thead.innerHTML = `
            <tr>
                <th style="width: 45px;">#</th>
                <th>${t('model')}</th>
                <th>${t('equip_desig')}</th>
                <th>${t('equip_nature')}</th>
                <th>${t('category')}</th>
                <th style="width: 70px;">${t('threshold')}</th>
                <th style="width: 110px;">${t('status')}</th>
            </tr>
        `;
        const previewRows = res.valid_items.slice(0, 50);
        previewRows.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td style="font-weight: 700;">${item.model_name}</td>
                <td>${item.equipment_designation || '—'}</td>
                <td>${item.equipment_nature || '—'}</td>
                <td>${item.category || '—'}</td>
                <td>${item.low_stock_threshold}</td>
                <td><span class="badge ${item.is_already_in_db ? 'badge-info' : 'badge-success'}">${item.is_already_in_db ? 'Mise à jour' : 'Nouveau'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } else if (mode === "COMBINED_MANIFEST") {
        thead.innerHTML = `
            <tr>
                <th style="width: 45px;">#</th>
                <th>${t('model')}</th>
                <th>${t('serial_num')}</th>
                <th>${t('equip_desig')}</th>
                <th style="width: 140px;">${t('status')}</th>
            </tr>
        `;
        const previewRows = res.valid_items.slice(0, 50);
        previewRows.forEach((item, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td style="font-weight: 700;">${item.model_name}</td>
                <td style="font-family: monospace; font-weight: 600;">${item.serial_number}</td>
                <td>${item.designation || '—'}</td>
                <td><span class="badge ${item.is_new_model ? 'badge-new-model' : 'badge-success'}">${item.is_new_model ? '✨ Nouveau Modèle' : 'Valide'}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } else { // SERIALS_ONLY
        thead.innerHTML = `
            <tr>
                <th style="width: 45px;">#</th>
                <th>${t('serial_num')}</th>
                <th style="width: 120px;">${t('status')}</th>
            </tr>
        `;
        const previewRows = res.valid_items.slice(0, 50);
        previewRows.forEach((sn, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td style="font-family: monospace; font-weight: 600;">${sn}</td>
                <td><span class="badge badge-success">Valide</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Already in DB items display
    if (res.already_in_db && res.already_in_db.length > 0) {
        res.already_in_db.slice(0, 10).forEach(item => {
            const tr = document.createElement("tr");
            const valStr = typeof item === 'object' ? (item.serial_number || item.model_name) : item;
            tr.innerHTML = `
                <td>-</td>
                <td colspan="${mode === 'SERIALS_ONLY' ? 1 : (mode === 'COMBINED_MANIFEST' ? 3 : 5)}" style="font-family: monospace; font-weight: 600; text-decoration: line-through; color: #94a3b8;">${valStr}</td>
                <td><span class="badge badge-danger">Déjà en base</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    document.getElementById("unifiedPreviewTableWrapper").style.display = "block";
    const confirmBtn = document.getElementById("btnConfirmUnifiedImport");
    if (confirmBtn) {
        confirmBtn.disabled = !res.valid_items || res.valid_items.length === 0;
    }
}

async function submitUnifiedImport() {
    if (!currentUnifiedImportResult || !currentUnifiedImportResult.valid_items || currentUnifiedImportResult.valid_items.length === 0) {
        showToast("Aucun élément valide à importer.", "error");
        return;
    }

    const mode = currentUnifiedImportResult.mode;
    const destModelSelect = document.getElementById("unifiedImportModelSelect");
    const destModelId = destModelSelect ? destModelSelect.value : null;

    if (mode === "SERIALS_ONLY" && !destModelId) {
        showToast(t("select_model_placeholder"), "error");
        return;
    }

    const btn = document.getElementById("btnConfirmUnifiedImport");
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span>⏳</span> <span>Importation...</span>`;

    try {
        const res = await window.pywebview.api.commit_unified_import({
            mode: mode,
            items: currentUnifiedImportResult.valid_items,
            destination_model_id: destModelId
        });

        if (res.success) {
            let msg = "Importation réussie !";
            if (mode === "MODELS_CATALOG") {
                msg = currentLang === 'ar' 
                    ? `تم استيراد ${res.imported_count || 0} طراز جديد وتحديث ${res.updated_count || 0} بنجاح !`
                    : `${res.imported_count || 0} nouveau(x) modèle(s) importé(s) et ${res.updated_count || 0} mis à jour !`;
            } else if (mode === "COMBINED_MANIFEST") {
                msg = currentLang === 'ar'
                    ? `تم استيراد ${res.imported_serials_count || 0} كاميرا وإنشاء ${res.created_models_count || 0} طراز بنجاح !`
                    : `${res.imported_serials_count || 0} caméra(s) importée(s) et ${res.created_models_count || 0} modèle(s) créé(s) !`;
            } else {
                msg = `${res.imported_count || 0} numéro(s) de série importé(s) avec succès !`;
            }

            showToast(msg, "success");
            closeModal("unifiedImportModal");
            loadInventoryTable();
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur lors de l'importation", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

async function downloadImportTemplate(type) {
    try {
        const res = await window.pywebview.api.get_import_template(type);
        if (res.success && res.data_uri) {
            const a = document.createElement("a");
            a.href = res.data_uri;
            a.download = res.filename || "template.xlsx";
            document.body.appendChild(a);
            a.click();
            setTimeout(() => { a.remove(); }, 500);
            showToast(currentLang === 'ar' ? "تم تحميل النموذج بنجاح !" : "Modèle téléchargé avec succès !", "success");
        } else {
            showToast(res.error || "Erreur génération modèle", "error");
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
        const inStockText = (m.in_stock_count || 0) > 0 ? `[${m.in_stock_count} en stock]` : `[0 en stock]`;
        const scanOpt = `<option value="${m.id}">${m.model_name} ${inStockText}</option>`;
        const filterOpt = `<option value="${m.id}">${m.model_name}</option>`;
        const assignOpt = `<option value="${m.id}">${m.model_name} (${m.equipment_designation || ''})</option>`;
        if (scanSelect) scanSelect.innerHTML += scanOpt;
        if (filterSelect) filterSelect.innerHTML += filterOpt;
        if (assignSelect) assignSelect.innerHTML += assignOpt;
    });

    if (currentScanVal && scanSelect) scanSelect.value = currentScanVal;
    if (currentFilterVal && filterSelect) filterSelect.value = currentFilterVal;
    handleScanModelChange();
}

function filterModelsTable() {
    renderModelsTable();
}

function renderModelsTable() {
    const tbody = document.querySelector("#modelsTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    // Calculate aggregated metrics
    const totalModels = cameraModels.length;
    const totalStock = cameraModels.reduce((sum, m) => sum + (m.in_stock_count || 0), 0);
    const alertCount = cameraModels.filter(m => (m.in_stock_count || 0) <= (m.stock_threshold ?? 5)).length;

    // Update mini-KPIs and subtab badges
    const mCountBadge = document.getElementById("modelsCountBadge");
    const invModelsBadge = document.getElementById("invModelsCountBadge");
    const statTotModels = document.getElementById("modelStatTotalModels");
    const statTotStock = document.getElementById("modelStatTotalStock");
    const statAlerts = document.getElementById("modelStatAlertModels");

    if (invModelsBadge) invModelsBadge.textContent = totalModels;
    if (statTotModels) statTotModels.textContent = totalModels;
    if (statTotStock) statTotStock.textContent = totalStock;
    if (statAlerts) statAlerts.textContent = alertCount;

    // Filter models by search query if any
    const searchInput = document.getElementById("modelFilterSearchInput");
    const q = searchInput ? searchInput.value.trim().toLowerCase() : "";
    const filtered = q ? cameraModels.filter(m => 
        (m.model_name || "").toLowerCase().includes(q) ||
        (m.equipment_designation || "").toLowerCase().includes(q) ||
        (m.equipment_nature || "").toLowerCase().includes(q) ||
        (m.category || "").toLowerCase().includes(q) ||
        (m.sub_category || "").toLowerCase().includes(q) ||
        String(m.id).includes(q)
    ) : cameraModels;

    if (mCountBadge) {
        mCountBadge.textContent = currentLang === 'ar' 
            ? `${filtered.length} طراز` 
            : `${filtered.length} ${filtered.length > 1 ? 'modèles' : 'modèle'}`;
    }

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="9">${currentLang === 'ar' ? 'لا يوجد طراز مطابق' : 'Aucun modèle enregistré'}</td></tr>`;
        return;
    }

    filtered.forEach(m => {
        const inStockCount = m.in_stock_count || 0;
        const totalCount = m.total_count || 0;
        const thresh = m.stock_threshold ?? 5;
        const isZero = inStockCount === 0;
        const isLow = inStockCount <= thresh;
        const badgeClass = isZero ? 'badge-danger' : (isLow ? 'badge-warning' : 'badge-success');

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-text-secondary);">${m.id}</td>
            <td style="font-weight: 700; color: var(--color-text-primary); font-size: 13.5px;">${m.model_name}</td>
            <td>${m.equipment_designation || '—'}</td>
            <td>${m.equipment_nature || '—'}</td>
            <td><span class="badge" style="background:#f1f5f9; color:#475569;">${m.category || '—'}</span></td>
            <td><span class="badge" style="background:#f1f5f9; color:#475569;">${m.sub_category || '—'}</span></td>
            <td style="text-align: center;">
                <span class="badge ${badgeClass}">${inStockCount}</span>
                <span style="color: var(--color-text-muted); font-size: 11.5px; font-weight: 600;">/ ${totalCount}</span>
            </td>
            <td style="text-align: center;">
                <input type="number" class="form-control form-control-sm" style="width: 65px; text-align: center; font-weight: 700; font-family: var(--font-mono);" value="${thresh}" min="0" max="999" onchange="updateModelThreshold(${m.id}, this.value)">
            </td>
            <td style="text-align: center;">
                <div style="display: flex; gap: 4px; justify-content: center;">
                    <button type="button" class="btn btn-sm btn-scan-model-fast" onclick="startScanningForModel(${m.id})" title="${t('scan_this_model')}">⚡</button>
                    <button type="button" class="btn btn-secondary btn-sm" onclick="openEditModelModal(${m.id})" title="${t('edit')}">✏️</button>
                    <button type="button" class="btn btn-danger btn-sm" onclick="deleteModel(${m.id})" title="Supprimer">✕</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function startScanningForModel(modelId) {
    switchInventorySubtab('serials');
    const scanSelect = document.getElementById("scanModelSelect");
    if (scanSelect) {
        scanSelect.value = modelId;
        handleScanModelChange();
    }
    setTimeout(() => {
        const inp = document.getElementById("scannerInput");
        if (inp) {
            inp.focus();
            inp.classList.add("scan-input-success");
            setTimeout(() => inp.classList.remove("scan-input-success"), 500);
        }
    }, 120);
}

function toggleAddModelDrawer(forceOpen = null) {
    const body = document.getElementById("addModelBody");
    const chev = document.getElementById("addModelChevron");
    if (!body) return;
    const isHidden = body.style.display === "none";
    const shouldOpen = forceOpen !== null ? forceOpen : isHidden;
    body.style.display = shouldOpen ? "block" : "none";
    if (chev) chev.textContent = shouldOpen ? "▲" : "▼";
    if (shouldOpen) {
        setTimeout(() => {
            const nameInp = document.getElementById("m_name");
            if (nameInp) nameInp.focus();
        }, 100);
    }
}

function resetAddModelForm() {
    const form = document.getElementById("addModelForm");
    if (form) form.reset();
    const cat = document.getElementById("m_cat");
    const subcat = document.getElementById("m_subcat");
    const thresh = document.getElementById("m_threshold");
    if (cat) cat.value = "القسم أ";
    if (subcat) subcat.value = "الفرع 1";
    if (thresh) thresh.value = 5;
}

function openEditModelModal(modelId) {
    const model = cameraModels.find(m => m.id === modelId);
    if (!model) return;
    document.getElementById("em_id").value = model.id;
    document.getElementById("em_name").value = model.model_name || "";
    document.getElementById("em_desig").value = model.equipment_designation || "";
    document.getElementById("em_nature").value = model.equipment_nature || "";
    document.getElementById("em_cat").value = model.category || "";
    document.getElementById("em_subcat").value = model.sub_category || "";
    document.getElementById("em_threshold").value = model.low_stock_threshold ?? model.stock_threshold ?? 5;
    openModal("editModelModal");
}

async function handleEditModelSubmit(e) {
    e.preventDefault();
    const modelId = parseInt(document.getElementById("em_id").value, 10);
    const rawThresh = parseInt(document.getElementById("em_threshold").value, 10);
    const data = {
        id: modelId,
        model_id: modelId,
        model_name: document.getElementById("em_name").value,
        equipment_designation: document.getElementById("em_desig").value,
        technical_nature: document.getElementById("em_nature").value,
        equipment_nature: document.getElementById("em_nature").value,
        regulatory_section: document.getElementById("em_cat").value,
        category: document.getElementById("em_cat").value,
        regulatory_subsection: document.getElementById("em_subcat").value,
        sub_category: document.getElementById("em_subcat").value,
        low_stock_threshold: isNaN(rawThresh) ? 5 : rawThresh
    };

    try {
        const res = await window.pywebview.api.update_camera_model(data);
        if (res.success) {
            showToast(t("model_updated_success"), "success");
            closeModal("editModelModal");
            await loadModels();
            loadInventoryTable();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur de modification", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function updateModelThreshold(modelId, threshold) {
    try {
        const val = parseInt(threshold, 10);
        await window.pywebview.api.update_model_threshold(modelId, isNaN(val) ? 5 : val);
        showToast("Seuil de stock mis à jour", "success");
        loadDashboard();
    } catch (e) {
        showToast(e.toString(), "error");
    }
}

async function handleAddModel(e) {
    e.preventDefault();
    const thresholdInput = document.getElementById("m_threshold");
    const parsedThresh = thresholdInput ? parseInt(thresholdInput.value, 10) : 5;
    const threshold = isNaN(parsedThresh) ? 5 : parsedThresh;

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
            showToast(currentLang === 'ar' ? "تمت إضافة الطراز بنجاح !" : "Modèle ajouté avec succès !", "success");
            resetAddModelForm();
            await loadModels();
            loadInventoryTable();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur d'ajout", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

function openQuickAddModelModal() {
    const form = document.getElementById("quickAddModelForm");
    if (form) form.reset();
    openModal("quickAddModelModal");
    setTimeout(() => {
        const inp = document.getElementById("qm_name");
        if (inp) inp.focus();
    }, 150);
}

async function handleQuickAddModelSubmit(e) {
    e.preventDefault();
    const thresholdInput = document.getElementById("qm_threshold");
    const parsedThresh = thresholdInput ? parseInt(thresholdInput.value, 10) : 5;
    const threshold = isNaN(parsedThresh) ? 5 : parsedThresh;

    const data = {
        model_name: document.getElementById("qm_name").value,
        equipment_designation: document.getElementById("qm_desig").value,
        equipment_nature: document.getElementById("qm_nature").value,
        category: document.getElementById("qm_cat").value,
        sub_category: document.getElementById("qm_subcat").value
    };

    try {
        const res = await window.pywebview.api.add_camera_model(data);
        if (res.success && res.id) {
            if (threshold !== 5) {
                await window.pywebview.api.update_model_threshold(res.id, threshold);
            }
            closeModal("quickAddModelModal");
            await loadModels();
            
            // Auto-select this newly created model in the scanner dropdown
            const scanSelect = document.getElementById("scanModelSelect");
            if (scanSelect) {
                scanSelect.value = res.id;
                handleScanModelChange();
            }
            loadDashboard();
            showToast(currentLang === 'ar' ? "تمت إضافة الطراز بنجاح وهو محدد الآن للمسح !" : "Modèle ajouté avec succès et prêt pour le scan !", "success");
            
            const scanInput = document.getElementById("scannerInput");
            if (scanInput) scanInput.focus();
        } else {
            showToast(res.error || "Erreur d'enregistrement du modèle", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function deleteModel(id) {
    const promptMsg = currentLang === 'ar' 
        ? "هل أنت متأكد من حذف هذا الطراز من الكتالوج؟"
        : "Voulez-vous vraiment supprimer ce modèle du catalogue ?";
    if (!confirm(promptMsg)) return;
    try {
        const res = await window.pywebview.api.delete_camera_model(id);
        if (res.success) {
            showToast(currentLang === 'ar' ? "تم حذف الطراز بنجاح." : "Modèle supprimé avec succès.", "success");
            await loadModels();
            loadInventoryTable();
            loadDashboard();
        } else {
            showToast(res.error || (currentLang === 'ar' ? "تعذر حذف الطراز" : "Impossible de supprimer ce modèle"), "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Clients Management & Ergonomic Sub-Tabs ---
let currentClientFormTab = "identity";

function setClientFormTab(tabName) {
    currentClientFormTab = tabName;
    const tabs = ["identity", "documents", "corporate", "logistics"];
    tabs.forEach(t => {
        const btn = document.getElementById(`subtabBtn_${t}`);
        const pane = document.getElementById(`subtabPane_${t}`);
        if (btn) btn.classList.toggle("active", t === tabName);
        if (pane) pane.classList.toggle("active", t === tabName);
    });
}

function startNewClientRegistration() {
    resetClientForm();
    setClientFormTab("identity");
    const nameInput = document.getElementById("cf_full_name");
    if (nameInput) {
        nameInput.focus();
        nameInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

async function loadClientsTable() {
    const search = document.getElementById("clientSearchInput")?.value || "";
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
            const secondaryName = (c.company_name && c.full_name && c.company_name !== c.full_name) 
                ? `<div style="font-size: 11px; color: var(--color-text-muted); font-weight: 500;">🏢 ${c.company_name}</div>` 
                : '';
            const camCount = c.camera_count || 0;

            tr.innerHTML = `
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-text-secondary);">${c.id}</td>
                <td>
                    <div style="font-weight: 700; color: var(--color-text-primary);">${displayName}</div>
                    ${secondaryName}
                </td>
                <td>${c.phone ? `<span style="font-family: var(--font-mono); font-size: 12.5px;">${c.phone}</span>` : '—'}</td>
                <td style="font-family: var(--font-mono); font-weight: 600; font-size: 12px;">${c.doc_number || '—'}</td>
                <td style="text-align: center;"><span class="badge ${camCount > 0 ? 'badge-success' : ''}">${camCount}</span></td>
            `;

            tr.title = currentLang === 'ar' ? 'انقر مرتين لتعديل بيانات العميل' : 'Double-cliquez pour modifier le client';
            tr.addEventListener("click", () => selectClient(c.id));
            tr.addEventListener("dblclick", () => editSelectedClient());
            tbody.appendChild(tr);
        });

        if (selectedClientId) {
            const clientStillExists = clientsList.find(c => c.id === selectedClientId);
            if (clientStillExists) {
                selectClient(selectedClientId);
            } else {
                updateClientActionButtons(null);
            }
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

    const client = clientsList.find(c => c.id === id);
    const strip = document.getElementById("selectedClientStrip");
    if (strip && client) {
        strip.className = "selected-client-strip active";
        const displayName = client.full_name || client.company_name || `Client #${client.id}`;
        const companyMeta = (client.company_name && client.company_name !== client.full_name) 
            ? `<span>🏢 ${client.company_name}</span>` 
            : '';
        const docMeta = client.doc_number ? `<span>🪪 ${client.doc_number}</span>` : '';
        const phoneMeta = client.phone ? `<span>📞 ${client.phone}</span>` : '';
        const camCount = client.camera_count || 0;
        const camBadgeClass = camCount > 0 ? "badge-success" : "";
        const camLabel = currentLang === 'ar' ? `${camCount} كاميرات` : `${camCount} caméra(s)`;

        strip.innerHTML = `
            <div class="strip-icon">👤</div>
            <div class="strip-details">
                <div class="strip-name">${displayName}</div>
                <div class="strip-meta">
                    ${docMeta}
                    ${phoneMeta}
                    ${companyMeta}
                    <span class="badge ${camBadgeClass}">📷 ${camLabel}</span>
                </div>
            </div>
        `;
    }

    loadClientEquipment(id);
}

function updateClientActionButtons(id) {
    const disabled = !id;
    const btnEdit = document.getElementById("btnEditClient");
    const btnAssign = document.getElementById("btnAssignCam");
    const btnReturn = document.getElementById("btnReturnCam");
    const btnFolder = document.getElementById("btnOpenFolder");
    const btnPreview = document.getElementById("btnPreviewDossier");
    const btnGen1 = document.getElementById("btnGenerateDossier");
    const btnGen2 = document.getElementById("btnGenerateSecondDossier");
    const btnDelete = document.getElementById("btnDeleteClient");

    if (btnEdit) btnEdit.disabled = disabled;
    if (btnAssign) btnAssign.disabled = disabled;
    if (btnReturn) btnReturn.disabled = disabled;
    if (btnFolder) btnFolder.disabled = disabled;
    if (btnPreview) btnPreview.disabled = disabled;
    if (btnGen1) btnGen1.disabled = disabled;
    if (btnGen2) btnGen2.disabled = disabled;
    if (btnDelete) btnDelete.disabled = disabled;

    if (!id) {
        hideClientEquipmentTray();
        const strip = document.getElementById("selectedClientStrip");
        if (strip) {
            strip.className = "selected-client-strip empty";
            strip.innerHTML = `
                <div class="strip-icon">👤</div>
                <div class="strip-details">
                    <span id="selectedClientStripText">${t('no_client_selected_hint')}</span>
                </div>
            `;
        }
    }
}

async function handleDeleteSelectedClient() {
    if (!selectedClientId) return;
    const client = clientsList.find(c => c.id === selectedClientId);
    const name = client ? (client.full_name || client.company_name || `#${client.id}`) : `#${selectedClientId}`;
    const confirmed = confirm(`${t('confirm_delete_client')}\n(${name})`);
    if (!confirmed) return;

    try {
        const res = await window.pywebview.api.delete_client(selectedClientId);
        if (res && res.success) {
            showToast(t('client_deleted_success'), "success");
            selectedClientId = null;
            resetClientForm();
            updateClientActionButtons(null);
            hideClientEquipmentTray();
            await loadClientsTable();
            loadInventoryTable();
            loadModels();
            loadDashboard();
        } else {
            showToast(res.error || "Erreur de suppression du client", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

let isEquipmentTrayExpanded = false;

function toggleClientEquipmentTray() {
    const body = document.getElementById("clientEquipmentBody");
    const chevron = document.getElementById("clientEquipmentChevron");
    if (!body) return;
    isEquipmentTrayExpanded = !isEquipmentTrayExpanded;
    body.style.display = isEquipmentTrayExpanded ? "block" : "none";
    if (chevron) {
        chevron.style.transform = isEquipmentTrayExpanded ? "rotate(180deg)" : "rotate(0deg)";
    }
}

function hideClientEquipmentTray() {
    const tray = document.getElementById("clientEquipmentTray");
    const body = document.getElementById("clientEquipmentBody");
    const chevron = document.getElementById("clientEquipmentChevron");
    if (tray) tray.style.display = "none";
    if (body) body.style.display = "none";
    if (chevron) chevron.style.transform = "rotate(0deg)";
    isEquipmentTrayExpanded = false;
}

async function loadClientEquipment(clientId) {
    const tray = document.getElementById("clientEquipmentTray");
    const tbody = document.querySelector("#clientEquipmentTable tbody");
    const badge = document.getElementById("clientEquipmentCountBadge");
    if (!tray || !tbody) return;

    if (!clientId) {
        hideClientEquipmentTray();
        return;
    }

    tray.style.display = "block";
    tbody.innerHTML = `<tr class="empty-row"><td colspan="3">Chargement...</td></tr>`;

    try {
        const res = await window.pywebview.api.get_client(clientId);
        if (res && res.success) {
            if (badge) {
                badge.textContent = cameras.length;
                badge.className = "badge " + (cameras.length > 0 ? "badge-success" : "");
            }
            if (cameras.length === 0) {
                tbody.innerHTML = `<tr class="empty-row"><td colspan="3">${t('no_equipment_assigned')}</td></tr>`;
            } else {
                tbody.innerHTML = "";
                cameras.forEach(cam => {
                    const tr = document.createElement("tr");
                    const dateStr = cam.assigned_at ? cam.assigned_at.split(" ")[0] : "—";
                    tr.innerHTML = `
                        <td style="font-family: var(--font-mono); font-weight: 700; color: var(--color-accent-primary);">${cam.serial_number}</td>
                        <td style="font-weight: 600;">${cam.model_name || '—'}</td>
                        <td style="font-family: var(--font-mono); font-size: 12px; color: var(--color-text-secondary);">${dateStr}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }
    } catch (e) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="3">${e.toString()}</td></tr>`;
    }
}

const REQUIRED_ANNEX5_FIELDS = [
    "cf_full_name",
    "cf_father_name",
    "cf_mother_name",
    "cf_dob",
    "cf_pob",
    "cf_nationality",
    "cf_address",
    "cf_city",
    "cf_phone",
    "cf_doc_number",
    "cf_doc_issuer",
    "cf_doc_issue_date"
];

function updateDossierCompleteness() {
    const badge = document.getElementById("dossierCompletenessBadge");
    const bar = document.getElementById("dossierCompletenessBar");
    const hint = document.getElementById("dossierCompletenessHint");
    if (!badge || !bar) return;

    let filled = 0;
    const total = REQUIRED_ANNEX5_FIELDS.length;

    REQUIRED_ANNEX5_FIELDS.forEach(fId => {
        const el = document.getElementById(fId);
        if (el && el.value && el.value.trim().length > 0) {
            filled++;
        }
    });

    const percent = Math.round((filled / total) * 100);
    badge.textContent = `${percent}%`;

    badge.className = "badge " + (percent >= 80 ? "badge-success" : (percent >= 50 ? "badge-warning" : "badge-danger"));
    bar.style.width = `${percent}%`;
    bar.style.backgroundColor = percent >= 80 ? "#10b981" : (percent >= 50 ? "#f59e0b" : "#ef4444");

    if (hint) {
        hint.textContent = currentLang === 'ar' 
            ? `${filled}/${total} حقول مطلوبة مكتملة` 
            : `${filled}/${total} champs requis remplis`;
    }
}

function updateClientFormTitle() {
    const title = document.getElementById("clientFormTitle");
    const submitBtn = document.getElementById("btnSaveClient");
    const editId = document.getElementById("clientIdInput")?.value;

    if (editId) {
        title.textContent = `${t('edit_client')}${editId}`;
        submitBtn.innerHTML = `💾 <span>${t('update_client')}</span>`;
    } else {
        title.textContent = t('register_client');
        submitBtn.innerHTML = `💾 <span>${t('save_client')}</span>`;
    }
}

function resetClientForm() {
    const form = document.getElementById("clientForm");
    if (form) form.reset();
    document.getElementById("clientIdInput").value = "";
    document.getElementById("cf_nationality").value = "جزائرية";
    document.getElementById("cf_origin_country").value = "الصين";
    document.getElementById("cf_import_country").value = "الجزائر";
    document.getElementById("cf_transport_method").value = "بحري / جوي";
    document.getElementById("cf_security_conditions").value = "حراسة ونظام إنذار ومراقبة 24/24";
    setClientFormTab("identity");
    updateClientFormTitle();
    updateDossierCompleteness();
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

        setClientFormTab("identity");
        updateClientFormTitle();
        updateDossierCompleteness();
        showToast(currentLang === 'ar' ? `تم تحميل بيانات العميل #${c.id} للتعديل` : `Client #${c.id} chargé pour modification`, "info");
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleClientSubmit(e) {
    e.preventDefault();
    const editId = document.getElementById("clientIdInput")?.value;

    const fullName = document.getElementById("cf_full_name")?.value.trim();
    if (!fullName) {
        setClientFormTab("identity");
        const el = document.getElementById("cf_full_name");
        if (el) {
            el.focus();
            el.classList.add("scan-input-error");
            setTimeout(() => el.classList.remove("scan-input-error"), 500);
        }
        showToast(currentLang === 'ar' ? "يرجى إدخال الاسم الكامل للعميل" : "Le nom complet est obligatoire.", "error");
        return;
    }

    const docNumber = document.getElementById("cf_doc_number")?.value.trim();
    if (!docNumber) {
        setClientFormTab("documents");
        const el = document.getElementById("cf_doc_number");
        if (el) {
            el.focus();
            el.classList.add("scan-input-error");
            setTimeout(() => el.classList.remove("scan-input-error"), 500);
        }
        showToast(currentLang === 'ar' ? "يرجى إدخال رقم بطاقة التعريف أو الوثيقة" : "Le numéro de document est obligatoire.", "error");
        return;
    }

    const data = {
        full_name: fullName,
        father_name: document.getElementById("cf_father_name")?.value.trim() || "",
        mother_name: document.getElementById("cf_mother_name")?.value.trim() || "",
        dob: document.getElementById("cf_dob")?.value.trim() || "",
        pob: document.getElementById("cf_pob")?.value.trim() || "",
        nationality: document.getElementById("cf_nationality")?.value.trim() || "جزائرية",
        doc_number: docNumber,
        doc_issuer: document.getElementById("cf_doc_issuer")?.value.trim() || "",
        doc_issue_date: document.getElementById("cf_doc_issue_date")?.value.trim() || "",
        passport_number: document.getElementById("cf_passport_number")?.value.trim() || "",
        passport_issuer: document.getElementById("cf_passport_issuer")?.value.trim() || "",
        passport_expiry_date: document.getElementById("cf_passport_expiry_date")?.value.trim() || "",
        company_name: document.getElementById("cf_company_name")?.value.trim() || "",
        company_hq: document.getElementById("cf_company_hq")?.value.trim() || "",
        profession: document.getElementById("cf_profession")?.value.trim() || "",
        activity_type: document.getElementById("cf_activity_type")?.value.trim() || "",
        phone: document.getElementById("cf_phone")?.value.trim() || "",
        email: document.getElementById("cf_email")?.value.trim() || "",
        fax: document.getElementById("cf_fax")?.value.trim() || "",
        city: document.getElementById("cf_city")?.value.trim() || "",
        address: document.getElementById("cf_address")?.value.trim() || "",
        shareholders: document.getElementById("cf_shareholders")?.value.trim() || "",
        accreditation_ref: document.getElementById("cf_accreditation_ref")?.value.trim() || "",
        origin_country: document.getElementById("cf_origin_country")?.value.trim() || "الصين",
        import_country: document.getElementById("cf_import_country")?.value.trim() || "الجزائر",
        transport_method: document.getElementById("cf_transport_method")?.value.trim() || "بحري / جوي",
        storage_location: document.getElementById("cf_storage_location")?.value.trim() || "",
        security_conditions: document.getElementById("cf_security_conditions")?.value.trim() || "حراسة ونظام إنذار ومراقبة 24/24"
    };

    const saveBtn = document.getElementById("btnSaveClient");
    if (saveBtn) saveBtn.disabled = true;

    try {
        let res;
        if (editId) {
            res = await window.pywebview.api.update_client(editId, data);
            if (res.success) {
                showToast(t('client_updated'), "success");
                resetClientForm();
                await loadClientsTable();
                loadDashboard();
                selectClient(parseInt(editId, 10));
            } else {
                showToast(res.error || "Erreur de mise à jour", "error");
            }
        } else {
            res = await window.pywebview.api.save_client(data);
            if (res.success) {
                showToast(t('client_saved'), "success");
                resetClientForm();
                await loadClientsTable();
                loadDashboard();
                selectClient(res.id);
            } else {
                showToast(res.error || "Erreur d'enregistrement", "error");
            }
        }
    } catch (err) {
        showToast(err.toString(), "error");
    } finally {
        if (saveBtn) saveBtn.disabled = false;
    }
}

// --- Assign Cameras Modal Flow ---
async function openAssignModal() {
    if (!selectedClientId) return;
    const client = clientsList.find(c => c.id === selectedClientId);
    const clientName = client.full_name || client.company_name || `Client #${client.id}`;
    document.getElementById("assignClientInfo").textContent = 
        `Client: ${clientName} (ID: ${client.id})`;

    const feedback = document.getElementById("assignScanFeedback");
    if (feedback) feedback.style.display = "none";

    const scanInp = document.getElementById("assignBarcodeScannerInput");
    if (scanInp) scanInp.value = "";

    loadAvailableSerialsForAssign();
    openModal("assignModal");

    setTimeout(() => {
        if (scanInp) scanInp.focus();
    }, 180);
}

function handleScanToClientSubmit() {
    const inp = document.getElementById("assignBarcodeScannerInput");
    if (!inp) return;
    const val = inp.value.trim().toUpperCase();
    if (!val) return;
    handleScanToClient(val);
}

async function handleScanToClient(barcode) {
    const inp = document.getElementById("assignBarcodeScannerInput");
    const feedback = document.getElementById("assignScanFeedback");
    if (!selectedClientId) return;

    try {
        const res = await window.pywebview.api.assign_camera_by_serial_number(selectedClientId, barcode);
        if (res.success) {
            playScannerBeep("success");
            if (inp) {
                inp.value = "";
                inp.classList.add("scan-input-success");
                setTimeout(() => inp.classList.remove("scan-input-success"), 300);
            }
            if (feedback) {
                feedback.style.display = "block";
                feedback.style.backgroundColor = "var(--color-success-bg)";
                feedback.style.color = "var(--color-success)";
                feedback.style.border = "1.5px solid var(--color-success-border)";
                feedback.textContent = `✓ ${res.message || 'Caméra assignée avec succès !'}`;
            }
            showToast(res.message || "Caméra assignée avec succès !", "success");
            loadAvailableSerialsForAssign();
            loadClientsTable();
            loadInventoryTable();
            loadModels();
            loadDashboard();
            if (selectedClientId) {
                loadClientEquipment(selectedClientId);
            }
        } else {
            playScannerBeep("error");
            if (inp) {
                inp.classList.add("scan-input-error");
                setTimeout(() => inp.classList.remove("scan-input-error"), 400);
                inp.select();
            }
            if (feedback) {
                feedback.style.display = "block";
                feedback.style.backgroundColor = "var(--color-danger-bg)";
                feedback.style.color = "var(--color-danger)";
                feedback.style.border = "1.5px solid var(--color-danger-border)";
                feedback.textContent = `✕ ${res.message || res.error || 'Erreur d\'assignation'}`;
            }
            showToast(res.message || res.error || "Erreur d'assignation", "error");
        }
    } catch (err) {
        playScannerBeep("error");
        showToast(err.toString(), "error");
    }
}

function handleAutoPickCheckboxes() {
    const qtyInput = document.getElementById("assignQtyInput");
    const qty = parseInt(qtyInput ? qtyInput.value : 1, 10) || 1;
    const checkboxes = Array.from(document.querySelectorAll(".assign-checkbox"));

    if (checkboxes.length === 0) {
        showToast(currentLang === 'ar' ? "لا توجد كاميرات في المخزن لهذا الطراز" : "Aucune caméra en stock pour ce modèle", "error");
        return;
    }

    checkboxes.forEach((cb, idx) => {
        cb.checked = (idx < qty);
    });

    const checkedCount = Math.min(qty, checkboxes.length);
    showToast(
        currentLang === 'ar' 
            ? `تم تحديد ${checkedCount} كاميرا عشوائياً` 
            : `${checkedCount} caméra(s) sélectionnée(s) au hasard. Cliquez sur 'Confirmer' pour valider.`, 
        "info"
    );
}

async function handleDirectAssignNByModel() {
    if (!selectedClientId) return;
    const modelSelect = document.getElementById("assignModelSelect");
    const modelId = modelSelect ? parseInt(modelSelect.value, 10) : null;
    const qtyInput = document.getElementById("assignQtyInput");
    const qty = parseInt(qtyInput ? qtyInput.value : 1, 10) || 1;

    if (!modelId) {
        showToast(t("select_model_placeholder"), "error");
        return;
    }

    try {
        const res = await window.pywebview.api.assign_n_cameras_by_model(selectedClientId, modelId, qty);
        if (res.success) {
            playScannerBeep("success");
            showToast(res.message || t("auto_assigned_success").replace("{count}", res.assigned_count).replace("{model}", res.model_name), "success");
            loadAvailableSerialsForAssign();
            loadClientsTable();
            loadInventoryTable();
            loadModels();
            loadDashboard();
            if (selectedClientId) {
                loadClientEquipment(selectedClientId);
            }
        } else {
            playScannerBeep("error");
            showToast(res.message || res.error || "Stock insuffisant", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
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
            loadDashboard();
            if (selectedClientId) {
                loadClientEquipment(selectedClientId);
            }
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

    const returnScanInput = document.getElementById("returnBarcodeScannerInput");
    if (returnScanInput) returnScanInput.value = "";
    const returnFilter = document.getElementById("returnFilterInput");
    if (returnFilter) returnFilter.value = "";
    const feedback = document.getElementById("returnScanFeedback");
    if (feedback) {
        feedback.style.display = "none";
        feedback.textContent = "";
    }

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
        setTimeout(() => {
            if (returnScanInput) returnScanInput.focus();
        }, 150);
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

function handleScanToReturnSubmit() {
    const input = document.getElementById("returnBarcodeScannerInput");
    const feedback = document.getElementById("returnScanFeedback");
    if (!input) return;
    const val = input.value.trim();
    if (!val) return;

    const checkboxes = Array.from(document.querySelectorAll("#returnSerialsTable .return-checkbox"));
    const targetCb = checkboxes.find(cb => cb.value.toLowerCase() === val.toLowerCase());

    if (targetCb) {
        targetCb.checked = true;
        const row = targetCb.closest("tr");
        if (row) {
            row.style.display = "";
            row.style.backgroundColor = "#e0f2fe";
            row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            setTimeout(() => {
                row.style.backgroundColor = "";
            }, 1500);
        }
        if (feedback) {
            feedback.style.display = "block";
            feedback.style.background = "#dcfce7";
            feedback.style.color = "#166534";
            feedback.style.border = "1px solid #86efac";
            feedback.textContent = currentLang === 'ar' ? `✓ تم تحديد الكاميرا ${val}` : `✓ Caméra ${val} cochée pour retour.`;
        }
        playScannerBeep("success");
        input.value = "";
        input.focus();
    } else {
        if (feedback) {
            feedback.style.display = "block";
            feedback.style.background = "#fee2e2";
            feedback.style.color = "#991b1b";
            feedback.style.border = "1px solid #fca5a5";
            feedback.textContent = currentLang === 'ar' ? `✗ الرقم ${val} غير موجود في كاميرات هذا العميل` : `✗ Numéro ${val} introuvable parmi les équipements de ce client.`;
        }
        input.classList.add("scan-input-error");
        setTimeout(() => input.classList.remove("scan-input-error"), 500);
        playScannerBeep("error");
    }
}

function filterReturnSerialsTable() {
    const filterVal = document.getElementById("returnFilterInput")?.value.trim().toLowerCase() || "";
    const rows = document.querySelectorAll("#returnSerialsTable tbody tr");
    rows.forEach(row => {
        if (row.classList.contains("empty-row")) return;
        const text = row.textContent.toLowerCase();
        row.style.display = (!filterVal || text.includes(filterVal)) ? "" : "none";
    });
}

function toggleAllReturnCheckboxes(checked) {
    document.querySelectorAll("#returnSerialsTable tbody tr").forEach(row => {
        if (row.style.display !== "none" && !row.classList.contains("empty-row")) {
            const cb = row.querySelector(".return-checkbox");
            if (cb) cb.checked = checked;
        }
    });
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
            loadDashboard();
            if (selectedClientId) {
                loadClientEquipment(selectedClientId);
            }
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
        if (subEl) subEl.textContent = currentLang === 'ar' ? "تم استخراج الملحق 1 والملحق 5 ورخصة الاعتماد ومحضر التثبيت." : "Les formulaires officiels (Annexes 1, 5, Agrément & PV) ont été tamponnés avec succès.";
        container.innerHTML = `
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex1" onclick="openAnnex1Pdf()">
                📄 <span>${t('view_annex1')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenAnnex5" onclick="openAnnex5Pdf()">
                📄 <span>${t('view_annex5')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenAgreement" onclick="openAgreementPdf()">
                📜 <span>${t('view_agreement')}</span>
            </button>
            <button class="btn btn-secondary flex-1" id="btnOpenPvPose" onclick="openPvPosePdf()">
                📋 <span>${t('view_pv_pose')}</span>
            </button>
        `;
    }
}

async function openAgreementPdf() {
    if (lastGeneratedDossier && lastGeneratedDossier.agreement) {
        await window.pywebview.api.open_file(lastGeneratedDossier.agreement);
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
        } else if (previewCurrentDocType === "agreement" && lastGeneratedDossier.agreement) {
            await window.pywebview.api.open_file(lastGeneratedDossier.agreement);
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
            // Keep onboarding open if unlicensed
            if (activeModal.id === "onboardingModal" && (!currentLicenseStatus || !currentLicenseStatus.valid)) {
                return;
            }
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

// --- Database Backup & Restore Handlers ---
async function loadBackupStatus() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const res = await window.pywebview.api.get_backup_status();
        if (res && res.success && res.data) {
            const b = res.data;
            const badge = document.getElementById("lastBackupBadge");
            if (badge) {
                badge.textContent = `${b.last_backup_timestamp} (${b.total_backups_count} archivée(s))`;
            }
        }
    } catch (err) {
        console.warn("Failed to load backup status:", err);
    }
}

async function handleCreateBackup() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        showToast("Création de l'instantané de la base...", "info");
        const res = await window.pywebview.api.create_database_backup();
        if (res && res.success) {
            showToast(`${t('backup_created')} (${res.file_size_kb} KB)`, "success");
            loadBackupStatus();
        } else {
            showToast(res.error || "Erreur de sauvegarde", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleExportBackup() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const res = await window.pywebview.api.export_database_backup();
        if (res && res.success) {
            showToast(t("backup_created"), "success");
            loadBackupStatus();
        } else if (res && !res.cancelled) {
            showToast(res.error || "Erreur d'exportation", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleRestoreBackup() {
    if (!confirm("⚠️ ATTENTION : La restauration remplacera toutes les données actuelles par celles de la sauvegarde choisie.\n\nUne copie de sécurité automatique sera créée au préalable.\n\nSouhaitez-vous continuer ?")) return;

    try {
        if (!window.pywebview || !window.pywebview.api) return;
        showToast("Sélection du fichier de sauvegarde...", "info");
        const res = await window.pywebview.api.restore_database_dialog();
        if (res && res.success) {
            showToast(t("backup_restored"), "success");
            loadDashboard();
            loadModels();
            loadInventoryTable();
            loadClientsTable();
            loadDossierDirectory();
            loadBackupStatus();
            loadInstallerProfile();
        } else if (res && !res.cancelled) {
            showToast(res.error || "Erreur de restauration", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

async function handleOpenBackupsDir() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        await window.pywebview.api.open_backups_directory();
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// --- Installer Profile & Digital Seal / Signature Handlers ---
let installerSealB64 = "";
let installerSigB64 = "";
let installerAgreementDocB64 = "";
let installerAgreementDocName = "";

async function loadInstallerProfile() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const res = await window.pywebview.api.get_installer_profile();
        if (res && res.success && res.data) {
            const p = res.data;
            const compInp = document.getElementById("inst_company_name");
            if (compInp) compInp.value = p.company_name || "";

            const nameInp = document.getElementById("inst_installer_name");
            if (nameInp) nameInp.value = p.installer_name || "";

            const phoneInp = document.getElementById("inst_phone");
            if (phoneInp) phoneInp.value = p.phone || "";

            const cityInp = document.getElementById("inst_city");
            if (cityInp) cityInp.value = p.city || "";

            const refInp = document.getElementById("inst_accreditation_ref");
            if (refInp) refInp.value = p.accreditation_ref || "";

            const dateInp = document.getElementById("inst_accreditation_date");
            if (dateInp) dateInp.value = p.accreditation_date || "";

            const enChk = document.getElementById("inst_seal_enabled");
            if (enChk) enChk.checked = p.enabled !== false;

            installerSealB64 = p.seal_image_b64 || "";
            updateSealThumbnail(installerSealB64);

            installerSigB64 = p.signature_image_b64 || "";
            updateSigThumbnail(installerSigB64);

            installerAgreementDocB64 = p.agreement_doc_b64 || "";
            installerAgreementDocName = p.agreement_doc_name || "";
            updateAgreementDocBadge(installerAgreementDocB64, installerAgreementDocName);

            // Synchronize onboarding inputs if present
            const onbComp = document.getElementById("onb_inst_company");
            if (onbComp && !onbComp.value) onbComp.value = p.company_name || "";
            const onbName = document.getElementById("onb_inst_name");
            if (onbName && !onbName.value) onbName.value = p.installer_name || "";
            const onbPhone = document.getElementById("onb_inst_phone");
            if (onbPhone && !onbPhone.value) onbPhone.value = p.phone || "";
            const onbCity = document.getElementById("onb_inst_city");
            if (onbCity && !onbCity.value) onbCity.value = p.city || "";
            const onbRef = document.getElementById("onb_inst_acc_ref");
            if (onbRef && !onbRef.value) onbRef.value = p.accreditation_ref || "";
            const onbDate = document.getElementById("onb_inst_acc_date");
            if (onbDate && !onbDate.value) onbDate.value = p.accreditation_date || "";

            if (p.seal_image_b64) {
                onbSealBase64 = p.seal_image_b64;
                const onbSealImg = document.getElementById("onbSealThumbImg");
                const onbSealEmpty = document.getElementById("onbSealThumbEmpty");
                if (onbSealImg) {
                    onbSealImg.src = onbSealBase64.startsWith("data:") ? onbSealBase64 : `data:image/png;base64,${onbSealBase64}`;
                    onbSealImg.style.display = "block";
                }
                if (onbSealEmpty) onbSealEmpty.style.display = "none";
            }

            if (p.signature_image_b64) {
                onbSigBase64 = p.signature_image_b64;
                const onbSigImg = document.getElementById("onbSigThumbImg");
                const onbSigEmpty = document.getElementById("onbSigThumbEmpty");
                if (onbSigImg) {
                    onbSigImg.src = onbSigBase64.startsWith("data:") ? onbSigBase64 : `data:image/png;base64,${onbSigBase64}`;
                    onbSigImg.style.display = "block";
                }
                if (onbSigEmpty) onbSigEmpty.style.display = "none";
            }

            if (p.agreement_doc_b64) {
                onbAgreementBase64 = p.agreement_doc_b64;
                onbAgreementName = p.agreement_doc_name || "Agrément";
                const onbAgrBadge = document.getElementById("onbAgreementBadge");
                if (onbAgrBadge) {
                    onbAgrBadge.textContent = `✓ ${onbAgreementName}`;
                    onbAgrBadge.className = "badge badge-success";
                }
            }
        }
    } catch (err) {
        console.warn("Failed to load installer profile:", err);
    }
}

function updateAgreementDocBadge(b64, name) {
    const badge = document.getElementById("agreementDocBadge");
    if (!badge) return;
    if (b64 && b64.length > 50) {
        badge.textContent = name ? `${name}` : t("agreement_doc_badge_custom");
        badge.className = "badge badge-success";
    } else {
        badge.textContent = t("agreement_doc_badge_none");
        badge.className = "badge badge-warning";
    }
}

function handleAgreementFileChosen(e) {
    const file = e.target.files[0];
    if (!file) return;
    installerAgreementDocName = file.name;
    const reader = new FileReader();
    reader.onload = (event) => {
        installerAgreementDocB64 = event.target.result;
        updateAgreementDocBadge(installerAgreementDocB64, installerAgreementDocName);
        showToast(currentLang === 'ar' ? "تم تحميل وثيقة الاعتماد بنجاح" : "Agrément officiel chargé avec succès", "success");
    };
    reader.readAsDataURL(file);
}

function clearAgreementDoc() {
    installerAgreementDocB64 = "";
    installerAgreementDocName = "";
    updateAgreementDocBadge("", "");
    const inp = document.getElementById("agreementFileInput");
    if (inp) inp.value = "";
    showToast(currentLang === 'ar' ? "تم حذف وثيقة الاعتماد" : "Document d'agrément supprimé", "info");
}

function updateSealThumbnail(b64) {
    const img = document.getElementById("sealThumbImg");
    const empty = document.getElementById("sealThumbEmpty");
    if (img && empty) {
        if (b64 && b64.length > 20) {
            img.src = b64.startsWith("data:") ? b64 : `data:image/png;base64,${b64}`;
            img.style.display = "block";
            empty.style.display = "none";
        } else {
            img.style.display = "none";
            empty.style.display = "block";
        }
    }
}

function updateSigThumbnail(b64) {
    const img = document.getElementById("sigThumbImg");
    const empty = document.getElementById("sigThumbEmpty");
    if (img && empty) {
        if (b64 && b64.length > 20) {
            img.src = b64.startsWith("data:") ? b64 : `data:image/png;base64,${b64}`;
            img.style.display = "block";
            empty.style.display = "none";
        } else {
            img.style.display = "none";
            empty.style.display = "block";
        }
    }
}

function handleSealFileChosen(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
        installerSealB64 = event.target.result;
        updateSealThumbnail(installerSealB64);
    };
    reader.readAsDataURL(file);
}

function handleSigFileChosen(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
        installerSigB64 = event.target.result;
        updateSigThumbnail(installerSigB64);
    };
    reader.readAsDataURL(file);
}

function clearSealImage() {
    installerSealB64 = "";
    updateSealThumbnail("");
    const inp = document.getElementById("sealFileInput");
    if (inp) inp.value = "";
}

function clearSigImage() {
    installerSigB64 = "";
    updateSigThumbnail("");
    const inp = document.getElementById("sigFileInput");
    if (inp) inp.value = "";
}

function handleToggleInstallerSeal(e) {
    handleSaveInstallerProfile();
}

async function handleSaveInstallerProfile() {
    try {
        if (!window.pywebview || !window.pywebview.api) return;
        const compName = document.getElementById("inst_company_name").value;
        const instName = document.getElementById("inst_installer_name")?.value || "";
        const instPhone = document.getElementById("inst_phone")?.value || "";
        const instCity = document.getElementById("inst_city")?.value || "";
        const instRef = document.getElementById("inst_accreditation_ref")?.value || "";
        const instDate = document.getElementById("inst_accreditation_date")?.value || "";
        const isEnabled = document.getElementById("inst_seal_enabled").checked;

        const payload = {
            company_name: compName,
            installer_name: instName,
            phone: instPhone,
            city: instCity,
            accreditation_ref: instRef,
            accreditation_date: instDate,
            agreement_doc_b64: installerAgreementDocB64,
            agreement_doc_name: installerAgreementDocName,
            seal_image_b64: installerSealB64,
            signature_image_b64: installerSigB64,
            enabled: isEnabled
        };

        const res = await window.pywebview.api.save_installer_profile(payload);
        if (res && res.success) {
            showToast(t("installer_saved"), "success");
        } else {
            showToast(res.error || "Erreur de sauvegarde profil", "error");
        }
    } catch (err) {
        showToast(err.toString(), "error");
    }
}

// =====================================================================
// Licensing, Unified Onboarding & Interactive Tour
// =====================================================================

let currentLicenseStatus = null;
let currentOnbStep = 1;
let onbSealBase64 = "";
let onbSigBase64 = "";
let onbAgreementBase64 = "";
let onbAgreementName = "";

async function checkLicenseStatus() {
    if (!window.pywebview || !window.pywebview.api) return;
    try {
        const res = await window.pywebview.api.get_license_status();
        currentLicenseStatus = res;
        updateLicenseUI(res);
        return res;
    } catch (err) {
        console.error("License check error:", err);
        return null;
    }
}

function updateLicenseUI(lic) {
    if (!lic) return;
    
    // 1. Sidebar Badge
    const sidebarDot = document.getElementById("licenseSidebarDot");
    const sidebarText = document.getElementById("licenseSidebarText");
    if (sidebarDot && sidebarText) {
        sidebarDot.className = "badge-dot";
        if (lic.tampered) {
            sidebarDot.classList.add("dot-expired");
            sidebarText.textContent = t("license_tampered");
        } else if (lic.valid) {
            sidebarDot.classList.add("dot-valid");
            if (lic.is_lifetime) {
                sidebarText.textContent = "PRO (Permanent)";
            } else {
                sidebarText.textContent = `PRO (${lic.days_left}j)`;
                if (lic.days_left <= 15) {
                    sidebarDot.classList.remove("dot-valid");
                    sidebarDot.classList.add("dot-warning");
                }
            }
        } else {
            sidebarDot.classList.add("dot-expired");
            sidebarText.textContent = t("license_expired");
        }
    }

    // 2. Settings Tab Card
    const licBadge = document.getElementById("licenseStatusBadge");
    const licMid = document.getElementById("licSettingsMachineId");
    const licExp = document.getElementById("licSettingsExpiry");
    const licDays = document.getElementById("licSettingsDaysLeft");

    if (licMid) licMid.value = lic.machine_id || "";
    if (licExp) licExp.value = lic.is_lifetime ? t("lic_lifetime") : (lic.expiry || "—");
    if (licDays) {
        licDays.value = lic.is_lifetime 
            ? "∞" 
            : (lic.valid ? t("lic_days_count").replace("{days}", lic.days_left) : "0");
    }

    if (licBadge) {
        licBadge.className = "badge";
        if (lic.tampered) {
            licBadge.classList.add("badge-danger");
            licBadge.textContent = t("license_tampered");
        } else if (lic.valid) {
            licBadge.classList.add("badge-success");
            licBadge.textContent = lic.is_lifetime ? "Permanent" : "Actif";
        } else {
            licBadge.classList.add("badge-danger");
            licBadge.textContent = t("license_expired");
        }
    }

    // 3. Standalone Modal elements
    const modalMid = document.getElementById("licModalMachineId");
    if (modalMid) modalMid.value = lic.machine_id || "";
    
    const banner = document.getElementById("licModalBanner");
    const bannerIcon = document.getElementById("licModalBannerIcon");
    const bannerTitle = document.getElementById("licModalBannerTitle");
    const bannerDesc = document.getElementById("licModalBannerDesc");

    if (banner && bannerTitle && bannerDesc) {
        banner.className = "alert-box";
        if (lic.tampered) {
            banner.classList.add("alert-danger");
            bannerIcon.textContent = "⚠️";
            bannerTitle.textContent = t("license_tampered");
            bannerDesc.textContent = lic.error || "Horloge système modifiée";
        } else if (lic.valid) {
            banner.classList.add("alert-success");
            bannerIcon.textContent = "✓";
            bannerTitle.textContent = lic.is_lifetime ? t("lic_lifetime") : t("license_active");
            bannerDesc.textContent = lic.is_lifetime ? "Licence complète activée sans limitation." : `${lic.days_left} jours restants (expire le ${lic.expiry}).`;
        } else {
            banner.classList.add("alert-danger");
            bannerIcon.textContent = "✕";
            bannerTitle.textContent = t("lic_req_title");
            bannerDesc.textContent = lic.error || t("lic_req_desc");
        }
    }
}

function openLicenseModal() {
    if (currentLicenseStatus) {
        updateLicenseUI(currentLicenseStatus);
    }
    openModal("licenseModal");
}

async function handleActivateLicenseFromModal() {
    const input = document.getElementById("licModalKeyInput");
    const btn = document.getElementById("btnSubmitLicenseKey");
    if (!input || !input.value.trim()) {
        showToast("Veuillez saisir la clé de licence / يرجى إدخال مفتاح الترخيص", "error");
        return;
    }

    btn.disabled = true;
    try {
        const res = await window.pywebview.api.activate_license(input.value.trim());
        if (res.success) {
            showToast("Licence activée avec succès ! / تم تفعيل الترخيص بنجاح !", "success");
            currentLicenseStatus = res.license;
            updateLicenseUI(res.license);
            setTimeout(() => {
                closeModal("licenseModal");
            }, 1200);
        } else {
            showToast(res.error || "Clé de licence invalide", "error");
        }
    } catch (err) {
        showToast("Erreur lors de l'activation: " + err, "error");
    } finally {
        btn.disabled = false;
    }
}

async function copyMachineId(btn) {
    const mid = currentLicenseStatus?.machine_id || (document.getElementById("onboardingMachineId")?.value) || "";
    if (!mid) return;
    try {
        await navigator.clipboard.writeText(mid);
        const origText = btn.innerHTML;
        btn.innerHTML = `✓ ${t("copied")}`;
        setTimeout(() => {
            btn.innerHTML = origText;
        }, 2000);
    } catch (e) {
        showToast(mid, "info");
    }
}

// --- Onboarding Wizard Logic ---
function goToOnbStep(step) {
    if (step < 1 || step > 4) return;
    
    // Enforcement: Cannot leave Step 2 without a valid license!
    if (step > 2 && (!currentLicenseStatus || !currentLicenseStatus.valid)) {
        showToast(currentLang === "ar" ? "يرجى تفعيل ترخيص صالح للمتابعة" : "Veuillez d'abord activer une licence valide pour continuer", "error");
        return;
    }

    currentOnbStep = step;

    // Update Step indicator dots
    document.querySelectorAll(".wizard-steps-indicator .step-dot").forEach(dot => {
        const s = parseInt(dot.dataset.step, 10);
        dot.classList.remove("active", "completed");
        if (s === currentOnbStep) dot.classList.add("active");
        else if (s < currentOnbStep) dot.classList.add("completed");
    });

    // Update Step Panes
    document.querySelectorAll(".onboarding-step-pane").forEach(pane => pane.classList.remove("active"));
    const activePane = document.getElementById(`onboardingStep${currentOnbStep}`);
    if (activePane) activePane.classList.add("active");

    // If on Step 2 and license is already valid, reflect in UI
    if (currentOnbStep === 2 && currentLicenseStatus && currentLicenseStatus.valid) {
        const alertBox = document.getElementById("onboardingLicAlert");
        const successBox = document.getElementById("onboardingLicSuccessBox");
        const successText = document.getElementById("onboardingLicSuccessText");
        if (alertBox) alertBox.style.display = "none";
        if (successBox) successBox.style.display = "flex";
        if (successText) {
            successText.textContent = currentLicenseStatus.is_lifetime 
                ? (currentLang === "ar" ? "ترخيص دائم (مدى الحياة) مفعّل !" : "Licence Permanente active !") 
                : (currentLang === "ar" ? `الترخيص صالح : ${currentLicenseStatus.days_left} يوماً متبقياً.` : `Licence validée : ${currentLicenseStatus.days_left} jours restants.`);
        }
    }

    // Update Navigation Buttons
    const btnPrev = document.getElementById("btnOnbPrev");
    const btnNext = document.getElementById("btnOnbNext");
    const arrowPrev = currentLang === "ar" ? "→" : "←";
    const arrowNext = currentLang === "ar" ? "←" : "→";

    if (btnPrev) {
        btnPrev.style.display = currentOnbStep === 1 ? "none" : "inline-flex";
        btnPrev.innerHTML = `${arrowPrev} <span>${t("btn_prev")}</span>`;
    }
    if (btnNext) {
        if (currentOnbStep === 4) {
            btnNext.innerHTML = `<span>${currentLang === "ar" ? "حفظ وبدء التشغيل ✓" : "Terminer & Démarrer ✓"}</span>`;
        } else {
            btnNext.innerHTML = `<span>${t("btn_next")}</span> ${arrowNext}`;
        }
    }
}

function onbNextStep() {
    if (currentOnbStep < 4) {
        goToOnbStep(currentOnbStep + 1);
    } else {
        finishOnboarding();
    }
}

function onbPrevStep() {
    if (currentOnbStep > 1) {
        goToOnbStep(currentOnbStep - 1);
    }
}

async function handleOnboardingActivate() {
    const input = document.getElementById("onboardingKeyInput");
    const btn = document.getElementById("btnOnboardingActivate");
    if (!input || !input.value.trim()) {
        showToast("Veuillez saisir votre clé d'activation / يرجى إدخال مفتاح التفعيل", "error");
        return;
    }

    btn.disabled = true;
    try {
        const res = await window.pywebview.api.activate_license(input.value.trim());
        if (res.success) {
            currentLicenseStatus = res.license;
            updateLicenseUI(res.license);
            
            const alertBox = document.getElementById("onboardingLicAlert");
            const successBox = document.getElementById("onboardingLicSuccessBox");
            const successText = document.getElementById("onboardingLicSuccessText");
            if (alertBox) alertBox.style.display = "none";
            if (successBox) successBox.style.display = "flex";
            if (successText) {
                successText.textContent = res.license.is_lifetime 
                    ? "Licence Permanente active !" 
                    : `Licence validée : ${res.license.days_left} jours restants.`;
            }
            showToast("Licence validée avec succès !", "success");
            setTimeout(() => {
                onbNextStep();
            }, 1200);
        } else {
            showToast(res.error || "Clé invalide", "error");
        }
    } catch (e) {
        showToast("Erreur d'activation: " + e, "error");
    } finally {
        btn.disabled = false;
    }
}

function handleOnbAgreementChosen(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        onbAgreementBase64 = e.target.result;
        onbAgreementName = file.name;
        const badge = document.getElementById("onbAgreementBadge");
        if (badge) {
            badge.className = "badge badge-success";
            badge.textContent = `✓ ${file.name}`;
        }
    };
    reader.readAsDataURL(file);
}

function clearOnbAgreementDoc() {
    onbAgreementBase64 = "";
    onbAgreementName = "";
    const input = document.getElementById("onbAgreementFileInput");
    if (input) input.value = "";
    const badge = document.getElementById("onbAgreementBadge");
    if (badge) {
        badge.className = "badge badge-warning";
        badge.textContent = t("agreement_doc_badge_none");
    }
}

function handleOnbSealChosen(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        onbSealBase64 = e.target.result;
        const img = document.getElementById("onbSealThumbImg");
        const empty = document.getElementById("onbSealThumbEmpty");
        if (img) {
            img.src = e.target.result;
            img.style.display = "block";
        }
        if (empty) empty.style.display = "none";
    };
    reader.readAsDataURL(file);
}

function clearOnbSealImage() {
    onbSealBase64 = "";
    const input = document.getElementById("onbSealFileInput");
    if (input) input.value = "";
    const img = document.getElementById("onbSealThumbImg");
    const empty = document.getElementById("onbSealThumbEmpty");
    if (img) img.style.display = "none";
    if (empty) empty.style.display = "block";
}

function handleOnbSigChosen(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        onbSigBase64 = e.target.result;
        const img = document.getElementById("onbSigThumbImg");
        const empty = document.getElementById("onbSigThumbEmpty");
        if (img) {
            img.src = e.target.result;
            img.style.display = "block";
        }
        if (empty) empty.style.display = "none";
    };
    reader.readAsDataURL(file);
}

function clearOnbSigImage() {
    onbSigBase64 = "";
    const input = document.getElementById("onbSigFileInput");
    if (input) input.value = "";
    const img = document.getElementById("onbSigThumbImg");
    const empty = document.getElementById("onbSigThumbEmpty");
    if (img) img.style.display = "none";
    if (empty) empty.style.display = "block";
}

async function handleSelectOnbDossierDir() {
    try {
        const res = await window.pywebview.api.select_dossier_directory();
        if (res && res.success && res.path) {
            const input = document.getElementById("onb_dossier_root");
            if (input) input.value = res.path;
        }
    } catch (e) {
        console.error(e);
    }
}

async function finishOnboarding() {
    const btnNext = document.getElementById("btnOnbNext");
    if (btnNext) btnNext.disabled = true;

    try {
        const profileData = {
            company_name: document.getElementById("onb_inst_company")?.value?.trim() || "",
            installer_name: document.getElementById("onb_inst_name")?.value?.trim() || "",
            phone: document.getElementById("onb_inst_phone")?.value?.trim() || "",
            city: document.getElementById("onb_inst_city")?.value?.trim() || "",
            accreditation_ref: document.getElementById("onb_inst_acc_ref")?.value?.trim() || "",
            accreditation_date: document.getElementById("onb_inst_acc_date")?.value?.trim() || "",
            agreement_doc_b64: onbAgreementBase64,
            agreement_doc_name: onbAgreementName,
            seal_image_b64: onbSealBase64,
            signature_image_b64: onbSigBase64,
            enabled: true
        };

        const dossierRoot = document.getElementById("onb_dossier_root")?.value?.trim() || "";
        const seedDemo = document.getElementById("onb_seed_demo")?.checked ?? true;

        const res = await window.pywebview.api.complete_onboarding({
            installer_profile: profileData,
            dossier_root: dossierRoot,
            seed_demo: seedDemo
        });

        if (res.success) {
            closeModal("onboardingModal");
            showToast(currentLang === "ar" ? "تم اكتمال الإعداد والتثبيت بنجاح !" : "Installation et configuration terminées !", "success");

            // Refresh all application views
            await loadModels();
            await loadDashboard();
            loadInventoryTable();
            loadClientsTable();
            loadDossierDirectory();
            loadInstallerProfile();
        } else {
            showToast(res.error || "Erreur lors de la finalisation", "error");
        }
    } catch (err) {
        showToast("Erreur: " + err, "error");
    } finally {
        if (btnNext) btnNext.disabled = false;
    }
}

// --- App Bootstrapping ---
window.addEventListener("pywebviewready", async () => {
    // 0. System Initialization & Licensing Check
    try {
        const initStatus = await window.pywebview.api.get_system_init_status();
        if (initStatus && initStatus.success) {
            currentLicenseStatus = initStatus.license;
            updateLicenseUI(initStatus.license);

            const onbMachineId = document.getElementById("onboardingMachineId");
            if (onbMachineId && initStatus.license) {
                onbMachineId.value = initStatus.license.machine_id || "";
            }

            const onbDossier = document.getElementById("onb_dossier_root");
            if (onbDossier) {
                onbDossier.value = initStatus.dossier_root || "dossiers";
            }

            // Launch onboarding if uncompleted or if license is invalid
            if (!initStatus.onboarding_completed || !initStatus.license || !initStatus.license.valid) {
                openModal("onboardingModal");
                // If license invalid, step to 2 or 1
                goToOnbStep(initStatus.onboarding_completed ? 2 : 1);
            }
        }
    } catch (err) {
        console.error("System init check error:", err);
    }
    // 1. Instant local UI setup (Zero network blocking)
    switchLanguage(currentLang, false);
    updateSoundButtonUI();
    setScanMode(scanMode);
    setClientFormTab("identity");
    updateDossierCompleteness();

    // Bind assign modal barcode scanner Enter key listener
    const assignScanInput = document.getElementById("assignBarcodeScannerInput");
    if (assignScanInput) {
        assignScanInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleScanToClientSubmit();
            }
        });
    }

    // Bind return modal barcode scanner Enter key listener
    const returnScanInput = document.getElementById("returnBarcodeScannerInput");
    if (returnScanInput) {
        returnScanInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleScanToReturnSubmit();
            }
        });
    }

    // Bind client form input listener for live dossier completeness calculation
    const clientForm = document.getElementById("clientForm");
    if (clientForm) {
        clientForm.addEventListener("input", updateDossierCompleteness);
    }

    // Auto-formatting for license key inputs
    function setupLicenseKeyInput(id) {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener("input", (e) => {
            let val = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
            if (val.length > 8) {
                val = val.substring(0, 8) + "-" + val.substring(8, 111);
            }
            e.target.value = val;
        });
    }
    setupLicenseKeyInput("onboardingKeyInput");
    setupLicenseKeyInput("licModalKeyInput");

    // 2. Primary viewport data loaded first for immediate paint
    await loadModels();
    await loadDashboard();

    // 3. Staggered background tab data population
    setTimeout(() => {
        loadInventoryTable();
        loadClientsTable();
        loadDossierDirectory();
        loadBackupStatus();
        loadInstallerProfile();
    }, 100);
});

// Fallback for standalone browser testing / inspection
document.addEventListener("DOMContentLoaded", () => {
    if (!window.pywebview) {
        switchLanguage(currentLang);
        updateSoundButtonUI();
        setScanMode(scanMode);
        setClientFormTab("identity");
        updateDossierCompleteness();
        const clientForm = document.getElementById("clientForm");
        if (clientForm) {
            clientForm.addEventListener("input", updateDossierCompleteness);
        }
    }
});
