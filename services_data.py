"""
Official services knowledge base for NextStep AI.
Supports verified detailed data for core services:
- Passport
- Aadhaar
- PAN Card
- Birth Certificate
- Property Tax
"""

SERVICES_DATABASE = {
    "passport": {
        "id": "passport",
        "title": "Passport Services",
        "category": "Identity & Travel",
        "jurisdiction": "Central",
        "jurisdiction_label": "Central Government (Ministry of External Affairs)",
        "icon": "🛂",
        "description": "Apply for fresh passport, re-issue, or renewal through Passport Seva Kendras across India.",
        "official_url": "https://www.passportindia.gov.in/",
        "portal_name": "Official Passport Seva Portal (MEA)",
        "is_verified": True,
        "keywords": ["passport", "tatkaal passport", "passport renewal", "reissue passport", "fresh passport", "pso", "psk"],
        "documents": [
            {"name": "Proof of Address (Aadhaar / Utility Bill / Bank Passbook)", "required": True, "notes": "Must match current residential address"},
            {"name": "Proof of Date of Birth (Aadhaar / Birth Certificate / School Leaving Cert)", "required": True, "notes": "Required for DOB verification"},
            {"name": "Identity Proof (Aadhaar / Voter ID / PAN)", "required": True, "notes": "Photo ID issued by government"},
            {"name": "Old Passport", "required": False, "notes": "Mandatory only in case of renewal or re-issue"}
        ],
        "steps": [
            {"step": 1, "title": "Register on Passport Seva Portal", "description": "Create an account on passportindia.gov.in and choose your nearest Passport Seva Kendra (PSK) or Post Office PSK."},
            {"step": 2, "title": "Fill Application Form", "description": "Select 'Fresh Passport' or 'Re-issue', complete personal details, and upload scanned copies of required documents."},
            {"step": 3, "title": "Pay Application Fee & Book Appointment", "description": "Pay ₹1,500 (Normal) or ₹3,500 (Tatkaal) online and select an available date and time slot for PSK visit."},
            {"step": 4, "title": "Visit PSK for Biometrics & Document Verification", "description": "Visit the designated PSK with original documents. Get biometrics (photo & fingerprints) taken."},
            {"step": 5, "title": "Police Verification & Delivery", "description": "Track police verification status online. Passport will be printed and sent via Speed Post after verification."}
        ],
        "verification_notes": "Fees (₹1,500 normal / ₹3,500 Tatkaal) and document checklists are verified against MEA guidelines. Tatkaal requires 3 specific Annexure documents."
    },
    "aadhaar": {
        "id": "aadhaar",
        "title": "Aadhaar Services",
        "category": "Identity & Civil",
        "jurisdiction": "Central",
        "jurisdiction_label": "Central Government (UIDAI)",
        "icon": "🪪",
        "description": "Enrol for a new Aadhaar card, update biometric/demographic details (Name, Address, Mobile, DOB).",
        "official_url": "https://uidai.gov.in/",
        "portal_name": "Official UIDAI Portal / myAadhaar",
        "is_verified": True,
        "keywords": ["aadhaar", "aadhar", "uidai", "aadhaar update", "download aadhaar", "myaadhaar", "aadhaar link"],
        "documents": [
            {"name": "Proof of Identity (POI) - PAN / Voter ID / Passport", "required": True, "notes": "For name and identity verification"},
            {"name": "Proof of Address (POA) - Bank Statement / Electricity Bill / Ration Card", "required": True, "notes": "For address change or fresh enrolment"},
            {"name": "Proof of Date of Birth (PDB) - Birth Cert / SSLC Marks Card", "required": True, "notes": "Required if DOB needs updating"},
            {"name": "Existing Aadhaar Number / Slip", "required": False, "notes": "Mandatory for demographic/biometric updates"}
        ],
        "steps": [
            {"step": 1, "title": "Visit myAadhaar Portal or Book Appointment", "description": "Go to uidai.gov.in or myaadhaar.uidai.gov.in. Book an appointment at an Aadhaar Seva Kendra (ASK)."},
            {"step": 2, "title": "Online Demographic Update (If applicable)", "description": "Address update can be submitted online with valid POI/POA document upload (Fee ₹50)."},
            {"step": 3, "title": "Visit Aadhaar Seva Kendra for Biometric Capture", "description": "For new enrolment, mobile link, or biometric update (iris/fingerprint/photo), visit ASK with original documents."},
            {"step": 4, "title": "Receive Enrolment / Update Slip", "description": "Collect the 14-digit Enrolment ID (EID) slip to track your update status online."},
            {"step": 5, "title": "Download e-Aadhaar", "description": "Once generated, download your password-protected e-Aadhaar PDF from myaadhaar.uidai.gov.in."}
        ],
        "verification_notes": "Aadhaar enrolment is free of charge. Demographic update fee is ₹50 and biometric update fee is ₹100 as per UIDAI official rules."
    },
    "pan": {
        "id": "pan",
        "title": "PAN Card Services",
        "category": "Taxation & Finance",
        "jurisdiction": "Central",
        "jurisdiction_label": "Central Government (Income Tax Dept / Protean / NSDL)",
        "icon": "💳",
        "description": "Apply for new Permanent Account Number (PAN Card), instant e-PAN, or correct existing PAN details.",
        "official_url": "https://www.incometax.gov.in/iec/foportal/",
        "portal_name": "Official Income Tax e-Filing & Protean (NSDL) Portal",
        "is_verified": True,
        "keywords": ["pan", "pan card", "e-pan", "instant pan", "pan correction", "nsdl pan", "protean pan"],
        "documents": [
            {"name": "Aadhaar Card (Linked with active Mobile Number)", "required": True, "notes": "Required for Instant e-PAN or e-KYC paperless processing"},
            {"name": "Proof of Identity (Aadhaar / Passport / Voter ID)", "required": True, "notes": "For non-Aadhaar standard physical applications"},
            {"name": "Proof of Address (Utility Bill / Bank Passbook)", "required": True, "notes": "Residential address proof"},
            {"name": "Proof of DOB (Birth Cert / Passport / Matriculation Cert)", "required": True, "notes": "Mandatory date of birth proof"}
        ],
        "steps": [
            {"step": 1, "title": "Choose Application Type (Instant e-PAN vs Physical)", "description": "For free instant e-PAN, visit efiling.incometax.gov.in. For physical PAN card, visit Protean (NSDL) or UTIITSL portal."},
            {"step": 2, "title": "Fill Form 49A Online", "description": "Enter basic personal details, Aadhaar number, and select digital e-KYC mode for fastest processing."},
            {"step": 3, "title": "Aadhaar OTP Authentication", "description": "Authenticate via OTP sent to your Aadhaar-registered mobile number."},
            {"step": 4, "title": "Pay Processing Fee (For Physical Card)", "description": "Instant e-PAN is free. Physical card delivery costs approx. ₹107 within India."},
            {"step": 5, "title": "Download e-PAN / Receive Physical Card", "description": "Download e-PAN PDF within hours, or receive physical plastic card via post in 7-10 working days."}
        ],
        "verification_notes": "Instant e-PAN via Income Tax portal is completely free of cost for Aadhaar holders. Physical card application via NSDL/UTIITSL costs ₹107."
    },
    "birth_certificate": {
        "id": "birth_certificate",
        "title": "Birth Certificate Services",
        "category": "Civil Registration",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana State Government (MeeSeva / GHMC / CDMA)",
        "icon": "👶",
        "description": "Register birth, obtain birth certificate copy, or apply for late birth registration in Telangana.",
        "official_url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "portal_name": "Official Telangana MeeSeva & GHMC Portal",
        "is_verified": True,
        "keywords": ["birth certificate", "birth registration", "born certificate", "meeseva birth cert", "ghmc birth certificate"],
        "documents": [
            {"name": "Hospital Birth Discharge Slip / Birth Report", "required": True, "notes": "Issued by hospital / nursing home where child was born"},
            {"name": "Parents' Aadhaar Cards", "required": True, "notes": "Identity and address proof of both mother and father"},
            {"name": "Parents' Marriage Certificate or Ration Card", "required": False, "notes": "For verification of parents' names"},
            {"name": "Affidavit from Magistrate / Revenue Officer", "required": False, "notes": "Mandatory only for Late Birth Registration (>1 year after birth)"}
        ],
        "steps": [
            {"step": 1, "title": "Hospital Registration Check", "description": "Hospitals in Telangana automatically record births in the Municipal / GHMC portal. Obtain hospital reference number."},
            {"step": 2, "title": "Apply via MeeSeva Portal / Franchise Kiosk", "description": "Visit ts.meeseva.telangana.gov.in or any authorized MeeSeva center in Telangana with hospital slip and parents' Aadhaar."},
            {"step": 3, "title": "Fill Birth Certificate Application", "description": "Provide child's name (or apply for name inclusion), date of birth, place of birth, and parents' details."},
            {"step": 4, "title": "Pay Service Fee", "description": "Pay official MeeSeva user charges (approx. ₹35 - ₹50 per copy)."},
            {"step": 5, "title": "Download Digitally Signed Certificate", "description": "Once approved by GHMC/Municipal Registrar, download digitally signed PDF from MeeSeva or collect printed copy."}
        ],
        "verification_notes": "In Telangana, birth registration within 21 days is free at local municipal offices. Registration beyond 1 year requires a Revenue Divisional Officer (RDO) / Magistrate permission."
    },
    "property_tax": {
        "id": "property_tax",
        "title": "Property Tax Payment & Assessment",
        "category": "Municipal Services",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana State Government (GHMC / CDMA / CDMA Telangana)",
        "icon": "🏠",
        "description": "Pay property tax, calculate assessment, download tax receipt, or search PTIN in Greater Hyderabad (GHMC) and Telangana Municipalities.",
        "official_url": "https://www.ghmc.gov.in/",
        "portal_name": "Official GHMC & Telangana Municipal Administration Portal",
        "is_verified": True,
        "keywords": ["property tax", "house tax", "ghmc property tax", "ptin", "telangana property tax", "cdma property tax"],
        "documents": [
            {"name": "Property Tax Identification Number (PTIN)", "required": True, "notes": "10-digit unique PTIN number for existing properties"},
            {"name": "Registered Sale Deed / Property Ownership Documents", "required": False, "notes": "Required only for fresh property tax assessment"},
            {"name": "Occupancy Certificate (OC) / Building Permission Copy", "required": False, "notes": "For new building assessment"},
            {"name": "Owner's Aadhaar Card & Mobile Number", "required": True, "notes": "For OTP verification during online payment"}
        ],
        "steps": [
            {"step": 1, "title": "Locate Your 10-Digit PTIN Number", "description": "Find PTIN on previous property tax receipt or search by owner name / door number on ghmc.gov.in or cdma.telangana.gov.in."},
            {"step": 2, "title": "Access GHMC / CDMA Property Tax Portal", "description": "Navigate to the online Property Tax payment section on GHMC portal or CDMA Telangana website."},
            {"step": 3, "title": "Verify Outstanding Dues & Early Bird Discount", "description": "Enter PTIN, verify property details, owner name, and calculated annual tax. Check for 5% early bird rebate (if paying in April)."},
            {"step": 4, "title": "Make Online Payment", "description": "Pay securely using Net Banking, UPI, Credit/Debit Card, or via MeeSeva center."},
            {"step": 5, "title": "Download Instant Tax Receipt", "description": "Save and print the official digitally signed GHMC property tax receipt for official records."}
        ],
        "verification_notes": "Verified against GHMC and Commissioner & Director of Municipal Administration (CDMA Telangana) portals. Early bird rebate of 5% is applicable if paid before April 30."
    }
}


# General fallback guidance for state vs central determination
JURISDICTION_RULES = {
    "telangana_keywords": ["telangana", "hyderabad", "ghmc", "meeseva", "cyberabad", "secunderabad", "warangal", "cdma", "ts", "epass ts"],
    "central_keywords": ["passport", "aadhaar", "pan", "income tax", "pancard", "railway", "irctc", "passport seva", "uidai", "epfo", "provident fund"]
}


def get_verified_service_by_key(service_key: str):
    """Returns curated service details for supported services."""
    return SERVICES_DATABASE.get(service_key.lower())


def search_service_by_query(query: str):
    """Fuzzy matches query text against keywords in the local knowledge base."""
    query_lower = query.lower()
    for key, service in SERVICES_DATABASE.items():
        for kw in service["keywords"]:
            if kw in query_lower:
                return service
    return None
