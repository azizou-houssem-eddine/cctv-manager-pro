import os
import sys
from db_manager import DatabaseManager
from pdf_generator import PDFGenerator

SAMPLE_MODELS = [
    {
        "model_name": "Hikvision DS-2CD2143G2-I",
        "equipment_designation": "كاميرا مراقبة خارجية شبكية",
        "equipment_nature": "IP Dome 4MP IK10 WDR",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 6,
        "prefix": "HKV-D2143"
    },
    {
        "model_name": "Hikvision DS-2CD2043G2-I",
        "equipment_designation": "كاميرا مراقبة خارجية أنبوبية",
        "equipment_nature": "IP Bullet 4MP IR40m EXIR",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 5,
        "prefix": "HKV-B2043"
    },
    {
        "model_name": "Dahua IPC-HDBW2431E-S-S2",
        "equipment_designation": "كاميرا مراقبة شبكية مضادة للتخريب",
        "equipment_nature": "Dome IP 4MP Starlight PoE",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 5,
        "prefix": "DH-HDBW24"
    },
    {
        "model_name": "Dahua IPC-HFW2431S-S-S2",
        "equipment_designation": "كاميرا مراقبة شبكية للمحيط الخارجي",
        "equipment_nature": "Bullet IP 4MP IR30m IP67",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 8,
        "prefix": "DH-HFW24"
    },
    {
        "model_name": "Hikvision DS-2DE4425IW-DE",
        "equipment_designation": "كاميرا مراقبة متحركة للساحات الواسعة",
        "equipment_nature": "PTZ Speed Dome 4MP 25X Zoom",
        "category": "القسم ب",
        "sub_category": "الفرع 2",
        "low_stock_threshold": 2,
        "prefix": "HKV-PTZ44"
    },
    {
        "model_name": "Dahua DH-SD49225XA-HNR",
        "equipment_designation": "كاميرا متحركة ذكية مزودة بتتبع تلقائي",
        "equipment_nature": "PTZ IP 2MP 25x Starlight+ WizSense",
        "category": "القسم ب",
        "sub_category": "الفرع 2",
        "low_stock_threshold": 2,
        "prefix": "DH-PTZ49"
    },
    {
        "model_name": "Uniview IPC2124LR3-PF28M",
        "equipment_designation": "كاميرا مراقبة ليلية ملونة 24/24",
        "equipment_nature": "Bullet IP 4MP ColorHunter WDR",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 4,
        "prefix": "UNV-CH21"
    },
    {
        "model_name": "Tiandy TC-C34XS Spec:I3/E/Y/2.8mm",
        "equipment_designation": "كاميرا مراقبة ذكية للتعرف البصري",
        "equipment_nature": "Bullet IP 4MP Super Starlight",
        "category": "القسم أ",
        "sub_category": "الفرع 1",
        "low_stock_threshold": 4,
        "prefix": "TD-C34XS"
    },
]

SAMPLE_CLIENTS = [
    {
        "full_name": "Mustapha Benali",
        "father_name": "Abdelkader",
        "mother_name": "Fatima Zohra Khelifi",
        "dob": "14/05/1978",
        "pob": "الجزائر الوسطى",
        "nationality": "جزائرية",
        "doc_number": "1098451203948571",
        "doc_issuer": "دائرة سيدي امحمد",
        "doc_issue_date": "10/02/2021",
        "passport_number": "219847102",
        "passport_issuer": "ولاية الجزائر",
        "passport_issue_date": "15/06/2022",
        "passport_expiry_date": "14/06/2027",
        "address": "12 شارع ديدوش مراد",
        "city": "الجزائر",
        "phone": "0550123456",
        "email": "contact@elamana-logistique.dz",
        "fax": "021634589",
        "profession": "مسير شركة لوجستية",
        "activity_type": "تخزين ونقل البضائع واللوجستيك",
        "company_name": "SARL EL AMANA LOGISTIQUE",
        "company_hq": "المنطقة الصناعية الرغاية، الجزائر",
        "position": "المدير العام",
        "accreditation_ref": "مقرر اعتماد رقم 145/2022",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري (ميناء الجزائر)",
        "storage_location": "مستودع التخزين المركزي - الرغاية",
        "security_conditions": "حراسة أمنية ونظام إنذار ومراقبة متواصلة 24/24",
        "shareholders": "مصطفى بن علي (60%)، رفيق سلطاني (40%)"
    },
    {
        "full_name": "Kaddour Mansouri",
        "father_name": "El Hadj Mohamed",
        "mother_name": "Khaira Belabbes",
        "dob": "22/11/1982",
        "pob": "وهران",
        "nationality": "جزائرية",
        "doc_number": "1158492019384756",
        "doc_issuer": "دائرة السانية",
        "doc_issue_date": "05/09/2020",
        "passport_number": "198374615",
        "passport_issuer": "ولاية وهران",
        "passport_issue_date": "11/04/2021",
        "passport_expiry_date": "10/04/2026",
        "address": "45 نهج جيش التحرير الوطني",
        "city": "وهران",
        "phone": "0560987654",
        "email": "direction@oran-securite.com",
        "fax": "041528974",
        "profession": "مدير مؤسسة تجارية",
        "activity_type": "توزيع وتخزين المعدات الصناعية",
        "company_name": "EURL MEDITERRANEE DISTRIBUTION",
        "company_hq": "حي المشتلة، بئر الجير، وهران",
        "position": "المسير الوحيد",
        "accreditation_ref": "سجل تجاري رقم 31/00-0984712",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري (ميناء وهران)",
        "storage_location": "مقر الشركة - بئر الجير",
        "security_conditions": "كاميرات محيطية ونظام إنذار مضاد للسرقة",
        "shareholders": "قدور منصوري (100%)"
    },
    {
        "full_name": "Rachid Bouzid",
        "father_name": "Lakhdar",
        "mother_name": "Messaouda Dahmani",
        "dob": "03/08/1975",
        "pob": "البليدة",
        "nationality": "جزائرية",
        "doc_number": "1087451928374615",
        "doc_issuer": "دائرة بوفاريك",
        "doc_issue_date": "18/03/2019",
        "passport_number": "",
        "passport_issuer": "",
        "passport_issue_date": "",
        "passport_expiry_date": "",
        "address": "الطريق الوطني رقم 01، المنطقة الصناعية",
        "city": "البليدة",
        "phone": "0555443322",
        "email": "contact@nord-agro.dz",
        "fax": "025381249",
        "profession": "مدير الإنتاج والتطوير",
        "activity_type": "الصناعات الغذائية والتحويلية",
        "company_name": "SPA NORD AGRO INDUSTRIE",
        "company_hq": "المنطقة الصناعية بن بولعيد، البليدة",
        "position": "رئيس مجلس الإدارة",
        "accreditation_ref": "رخصة استغلال صناعية 2018/88",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري / جوي",
        "storage_location": "الوحدة الإنتاجية رقم 02 - بن بولعيد",
        "security_conditions": "حراسة متواصلة 24/24 وأبواب إلكترونية مؤمنة",
        "shareholders": "عائلة بوزيد (70%)، مجمع الاستثمار الشمالي (30%)"
    },
    {
        "full_name": "Dr. Mohamed Lamine Brahimi",
        "father_name": "Tahar",
        "mother_name": "Zoulikha Mechati",
        "dob": "19/01/1985",
        "pob": "قسنطينة",
        "nationality": "جزائرية",
        "doc_number": "1258471930284751",
        "doc_issuer": "دائرة الخروب",
        "doc_issue_date": "14/07/2022",
        "passport_number": "224589103",
        "passport_issuer": "ولاية قسنطينة",
        "passport_issue_date": "08/10/2023",
        "passport_expiry_date": "07/10/2028",
        "address": "حي المنظر الجميل، عمارة ب رقم 04",
        "city": "قسنطينة",
        "phone": "0661223344",
        "email": "dr.brahimi.pharma@gmail.com",
        "fax": "",
        "profession": "صيدلي معتمد",
        "activity_type": "صيدلية ومواد شبه صيدلانية",
        "company_name": "Pharmacie En-Nour",
        "company_hq": "شارع العربي بن مهيدي، قسنطينة",
        "position": "صاحب الصيدلية",
        "accreditation_ref": "اعتماد وزارة الصحة رقم 1892/2015",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بري",
        "storage_location": "مقر الصيدلية ومخزن الأدوية",
        "security_conditions": "نظام إنذار رقمي وكاميرات كشف الحركة",
        "shareholders": "محمد لمين براهيمي (100%)"
    },
    {
        "full_name": "Karim Belkacem",
        "father_name": "Saïd",
        "mother_name": "Yamima Kaci",
        "dob": "30/09/1980",
        "pob": "سطيف",
        "nationality": "جزائرية",
        "doc_number": "1198472910384752",
        "doc_issuer": "دائرة العلمة",
        "doc_issue_date": "29/11/2021",
        "passport_number": "",
        "passport_issuer": "",
        "passport_issue_date": "",
        "passport_expiry_date": "",
        "address": "شارع دبي التجاري رقم 88",
        "city": "سطيف",
        "phone": "0770334455",
        "email": "belkacem.quincaillerie@gmail.com",
        "fax": "",
        "profession": "تاجر جملة",
        "activity_type": "تجارة الجملة لمواد البناء والأجهزة الكهرومنزلية",
        "company_name": "Établissement Belkacem & Frères",
        "company_hq": "المنطقة الحرفية، العلمة، سطيف",
        "position": "المدير المسير",
        "accreditation_ref": "سجل تجاري 19/00-4718293",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري (ميناء بجاية)",
        "storage_location": "المستودع الرئيسي رقم 05 - العلمة",
        "security_conditions": "حراسة ليلية وربط بكاميرات خارجية ذكية",
        "shareholders": "كريم بلقاسم (50%)، سمير بلقاسم (50%)"
    },
    {
        "full_name": "Mme Nadia Benseghir",
        "father_name": "Ammar",
        "mother_name": "Cherifa Boukerche",
        "dob": "12/04/1979",
        "pob": "عنابة",
        "nationality": "جزائرية",
        "doc_number": "1230948571029384",
        "doc_issuer": "دائرة الحجار",
        "doc_issue_date": "16/01/2020",
        "passport_number": "208746192",
        "passport_issuer": "ولاية عنابة",
        "passport_issue_date": "25/08/2021",
        "passport_expiry_date": "24/08/2026",
        "address": "طريق شبيطة مختار، فيلا رقم 14",
        "city": "عنابة",
        "phone": "0550889900",
        "email": "direction@clinique-elafia.dz",
        "fax": "038459012",
        "profession": "مديرة منشأة صحية",
        "activity_type": "عيادة طبية خاصة للجراحة والتوليد",
        "company_name": "Clinique Médico-Chirurgicale El-Afia",
        "company_hq": "حي واد القبة، عنابة",
        "position": "المديرة الإدارية",
        "accreditation_ref": "قرار وزاري مؤرخ في 2017/04/10",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بحري / جوي",
        "storage_location": "الجناح الإداري بالعيادة",
        "security_conditions": "أعوان أمن مؤهلين 24/24 ومراقبة إلكترونية",
        "shareholders": "نادية بن صغير (100%)"
    },
    {
        "full_name": "Yacine Mansouri",
        "father_name": "Djelloul",
        "mother_name": "Aicha Benmansour",
        "dob": "07/10/1988",
        "pob": "تلمسان",
        "nationality": "جزائرية",
        "doc_number": "1138475920193847",
        "doc_issuer": "دائرة المنصورة",
        "doc_issue_date": "22/06/2023",
        "passport_number": "",
        "passport_issuer": "",
        "passport_issue_date": "",
        "passport_expiry_date": "",
        "address": "نهج أول نوفمبر، حي إمامة",
        "city": "تلمسان",
        "phone": "0660778899",
        "email": "supermarche.rondpoint@yahoo.fr",
        "fax": "",
        "profession": "تاجر تجزئة ومسير سوبرماركت",
        "activity_type": "سوبرماركت ومواد غذائية عامة",
        "company_name": "Supermarché Le Rond-Point",
        "company_hq": "مفترق طرق إمامة، تلمسان",
        "position": "المسير المالي",
        "accreditation_ref": "سجل تجاري رقم 13/00-3849102",
        "origin_country": "الصين",
        "import_country": "الجزائر",
        "transport_method": "بري",
        "storage_location": "مستودع السوبرماركت الخلفي",
        "security_conditions": "بوابات مضادة للسرقة وكاميرات تغطي كامل الأروقة",
        "shareholders": "ياسين منصوري (100%)"
    }
]

def seed_database(db: DatabaseManager = None, pdf_gen: PDFGenerator = None) -> dict:
    """
    Populate database with rich Algerian models, clients, serials, and assignments.
    Also compiles ready-to-inspect dossiers in the selected client directory.
    """
    if db is None:
        db = DatabaseManager("cctv_manager.db")
    db.initialize_db()

    if pdf_gen is None:
        pdf_gen = PDFGenerator("templates_pdf")

    # 1. Models & Serials
    model_ids = {}
    created_models = 0
    total_serials_added = 0

    existing_models = {m["model_name"]: m["id"] for m in db.get_camera_models()}

    for sm in SAMPLE_MODELS:
        mname = sm["model_name"]
        if mname in existing_models:
            mid = existing_models[mname]
            db.update_model_threshold(mid, sm["low_stock_threshold"])
        else:
            mid = db.add_camera_model(
                sm["model_name"],
                sm["equipment_designation"],
                sm["equipment_nature"],
                sm["category"],
                sm["sub_category"],
                low_stock_threshold=sm["low_stock_threshold"]
            )
            created_models += 1
        model_ids[mname] = mid

        # Add batch serial numbers (20 serials per model)
        serials_to_add = [
            f"{sm['prefix']}-2024-{1000 + i:04d}"
            for i in range(1, 21)
        ]
        res_batch = db.save_serial_batch(mid, serials_to_add)
        total_serials_added += res_batch if isinstance(res_batch, int) else (res_batch.get("count", 0) if isinstance(res_batch, dict) else len(serials_to_add))

    # 2. Clients
    client_ids = {}
    created_clients = 0
    existing_clients = {c["doc_number"]: c["id"] for c in db.get_clients()}

    for sc in SAMPLE_CLIENTS:
        doc_num = sc["doc_number"]
        if doc_num in existing_clients:
            cid = existing_clients[doc_num]
        else:
            cid = db.add_client(sc)
            created_clients += 1
        client_ids[sc["full_name"]] = cid

    # 3. Targeted Assignments (diverse stock distribution)
    assignments_plan = [
        # Client 1 (SARL EL AMANA): 8 cameras (Hik Dome + Bullet)
        ("Mustapha Benali", "Hikvision DS-2CD2143G2-I", 5),
        ("Mustapha Benali", "Hikvision DS-2CD2043G2-I", 3),

        # Client 2 (EURL MEDITERRANEE): 4 cameras
        ("Kaddour Mansouri", "Dahua IPC-HDBW2431E-S-S2", 3),
        ("Kaddour Mansouri", "Uniview IPC2124LR3-PF28M", 1),

        # Client 3 (SPA NORD AGRO): 15 cameras (drives Dahua Bullet into low-stock alert!)
        ("Rachid Bouzid", "Dahua IPC-HFW2431S-S-S2", 14),
        ("Rachid Bouzid", "Hikvision DS-2DE4425IW-DE", 1),

        # Client 4 (Dr. Brahimi): 3 cameras
        ("Dr. Mohamed Lamine Brahimi", "Tiandy TC-C34XS Spec:I3/E/Y/2.8mm", 3),

        # Client 5 (Karim Belkacem): 4 cameras
        ("Karim Belkacem", "Hikvision DS-2CD2043G2-I", 4),
    ]

    total_assigned = 0
    for cname, mname, qty in assignments_plan:
        cid = client_ids.get(cname)
        mid = model_ids.get(mname)
        if not cid or not mid:
            continue

        avail = db.get_available_serials(mid)
        if len(avail) >= qty:
            to_assign = [s["id"] for s in avail[:qty]]
            db.assign_cameras_batch(cid, to_assign)
            total_assigned += len(to_assign)

    # 4. Generate Initial Dossiers for top 2 clients in the configured directory
    root_dir = db.get_dossier_root_dir()
    dossiers_generated = []
    
    for cname in ["Mustapha Benali", "Kaddour Mansouri"]:
        cid = client_ids.get(cname)
        if not cid:
            continue
        purchases_data = db.get_client_purchases_for_pdf(cid)
        cl = purchases_data.get("client")
        cams = purchases_data.get("cameras", [])
        if cl:
            d_res = pdf_gen.generate_client_dossier(
                cl, cams, base_dir=root_dir, dossier_type="1er dossier"
            )
            dossiers_generated.append({
                "client": cname,
                "folder": d_res.get("folder")
            })

    analytics = db.get_dashboard_analytics()

    return {
        "success": True,
        "models_created": created_models,
        "clients_created": created_clients,
        "serials_ingested": total_serials_added,
        "assignments_made": total_assigned,
        "dossiers_generated": dossiers_generated,
        "dossier_root_dir": root_dir,
        "analytics": analytics
    }

if __name__ == "__main__":
    res = seed_database()
    print("Seed process completed successfully!")
    print(f"- Models Created: {res['models_created']}")
    print(f"- Clients Created: {res['clients_created']}")
    print(f"- Serials Ingested: {res['serials_ingested']}")
    print(f"- Assignments: {res['assignments_made']}")
    print(f"- Dossier Root: {res['dossier_root_dir']}")
    print(f"- Low Stock Alerts: {len(res['analytics'].get('low_stock_alerts', []))}")
