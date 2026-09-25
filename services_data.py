"""
Official services knowledge base for NextStep AI (v2.1).
Supports verified detailed data for core Indian & Telangana services:
- Passport (Central)
- Aadhaar (Central)
- PAN Card (Central)
- Voter ID (Central / ECI)
- Driving Licence & Vehicle RC (Central / Telangana RTO)
- Birth Certificate (Telangana / GHMC / MeeSeva)
- Death Certificate (Telangana / GHMC / MeeSeva)
- Caste, Income & Residence Certificates (Telangana / MeeSeva)
- Property Tax (Telangana / GHMC / CDMA)
- Telangana ePASS / Welfare Schemes (Telangana / Central)
- Business / MSME Udyam Registration (Central & TS-iPASS)
- Income Tax Return (ITR) Filing (Central)
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
        "keywords": ["passport", "tatkaal passport", "passport renewal", "reissue passport", "fresh passport", "pso", "psk", "need a passport", "apply for passport", "passport application", "passport seva"],
        "documents": [
            {"name": "Proof of Address (Aadhaar / Utility Bill / Bank Passbook)", "status": "Typically required", "required": True, "why_needed": "Verifies current residential address for police verification", "check_note": "Name and address must match exactly"},
            {"name": "Proof of Date of Birth (Aadhaar / Birth Cert / Matriculation Cert)", "status": "Typically required", "required": True, "why_needed": "Mandatory DOB proof for passport issuance", "check_note": "DOB format must be DD/MM/YYYY"},
            {"name": "Photo Identity Proof (Aadhaar / Voter ID / PAN)", "status": "Typically required", "required": True, "why_needed": "Government photo identity confirmation", "check_note": "Must be valid and unexpired"},
            {"name": "Old Passport", "status": "May be required depending on your case", "required": False, "why_needed": "Mandatory only in case of renewal or re-issue", "check_note": "Carry original old booklet + self-attested copies"}
        ],
        "steps": [
            {"step": 1, "title": "Register on Passport Seva Portal", "description": "Create an account on passportindia.gov.in and choose your nearest Passport Seva Kendra (PSK) or Post Office PSK."},
            {"step": 2, "title": "Fill Application Form", "description": "Select 'Fresh Passport' or 'Re-issue', complete personal details, and upload scanned copies of required documents."},
            {"step": 3, "title": "Pay Application Fee & Book Appointment", "description": "Pay ₹1,500 (Normal) or ₹3,500 (Tatkaal) online and select an available date and time slot for PSK visit."},
            {"step": 4, "title": "Visit PSK for Biometrics & Document Verification", "description": "Visit designated PSK with original documents. Get biometrics (photo & fingerprints) captured."},
            {"step": 5, "title": "Police Verification & Delivery", "description": "Track police verification status online. Passport will be printed and dispatched via Speed Post."}
        ],
        "verification_notes": "Fees (₹1,500 normal / ₹3,500 Tatkaal) and document checklists are verified against MEA guidelines."
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
        "keywords": ["aadhaar", "aadhar", "uidai", "aadhaar update", "download aadhaar", "myaadhaar", "aadhaar link", "address update aadhaar", "aadhaar card", "enrol aadhaar"],
        "documents": [
            {"name": "Proof of Identity (POI) - PAN / Voter ID / Passport", "status": "Typically required", "required": True, "why_needed": "Confirms identity for name/photo changes", "check_note": "Must show photo and full name"},
            {"name": "Proof of Address (POA) - Electricity Bill / Bank Statement / Rent Agreement", "status": "Typically required", "required": True, "why_needed": "Verifies address change or new enrolment", "check_note": "Bill must be under 3 months old"},
            {"name": "Proof of Date of Birth (PDB) - Birth Cert / SSLC Certificate", "status": "May be required depending on your case", "required": False, "why_needed": "Required only if updating date of birth", "check_note": "UIDAI allows DOB correction only once"},
            {"name": "Existing Aadhaar Number / Acknowledgement Slip", "status": "Typically required", "required": True, "why_needed": "For demographic or biometric updates", "check_note": "Have 12-digit Aadhaar number ready"}
        ],
        "steps": [
            {"step": 1, "title": "Visit myAadhaar Portal or Book ASK Appointment", "description": "Go to uidai.gov.in or myaadhaar.uidai.gov.in. Book an appointment at an Aadhaar Seva Kendra (ASK)."},
            {"step": 2, "title": "Online Demographic / Address Update", "description": "Address updates can be submitted online with valid POA document upload (Fee ₹50)."},
            {"step": 3, "title": "Visit ASK for Biometric Capture", "description": "For mobile link, photo, or biometric update, visit ASK with original documents."},
            {"step": 4, "title": "Receive Enrolment / Update Slip", "description": "Collect the 14-digit Enrolment ID (EID) slip to track your update status online."},
            {"step": 5, "title": "Download e-Aadhaar", "description": "Once updated, download password-protected e-Aadhaar PDF from myaadhaar.uidai.gov.in."}
        ],
        "verification_notes": "Aadhaar enrolment is free. Demographic update is ₹50 and biometric update is ₹100 as per UIDAI official rules."
    },
    "pan": {
        "id": "pan",
        "title": "PAN Card Services",
        "category": "Taxation & Finance",
        "jurisdiction": "Central",
        "jurisdiction_label": "Central Government (Income Tax Dept / Protean NSDL)",
        "icon": "💳",
        "description": "Apply for new Permanent Account Number (PAN Card), instant e-PAN, or correct existing PAN details.",
        "official_url": "https://www.incometax.gov.in/iec/foportal/",
        "portal_name": "Official Income Tax e-Filing & Protean Portal",
        "is_verified": True,
        "keywords": ["pan", "pan card", "e-pan", "instant pan", "pan correction", "nsdl pan", "protean pan", "apply for pan", "apply pan", "new pan"],
        "documents": [
            {"name": "Aadhaar Card (Linked with Active Mobile Number)", "status": "Typically required", "required": True, "why_needed": "Mandatory for Instant e-PAN or e-KYC paperless route", "check_note": "Mobile number must receive OTP"},
            {"name": "Proof of Identity (Aadhaar / Passport / Voter ID)", "status": "May be required depending on your case", "required": False, "why_needed": "For non-Aadhaar physical application route", "check_note": "Clear copy required"},
            {"name": "Proof of Address (Utility Bill / Bank Passbook)", "status": "May be required depending on your case", "required": False, "why_needed": "For physical card delivery address validation", "check_note": "Address must match Aadhaar"},
            {"name": "Proof of DOB (Birth Cert / Passport / SSLC Marks Card)", "status": "May be required depending on your case", "required": False, "why_needed": "Mandatory DOB verification for physical PAN", "check_note": "DOB must match Aadhaar record"}
        ],
        "steps": [
            {"step": 1, "title": "Choose Application Type", "description": "For free instant e-PAN, use incometax.gov.in. For physical PAN card, use Protean (NSDL) or UTIITSL portal."},
            {"step": 2, "title": "Fill Application Form 49A Online", "description": "Enter personal details, Aadhaar number, and select digital e-KYC mode for paperless processing."},
            {"step": 3, "title": "Aadhaar OTP Authentication", "description": "Authenticate via OTP sent to your Aadhaar-registered mobile number."},
            {"step": 4, "title": "Pay Processing Fee (For Physical Card)", "description": "Instant e-PAN is free. Physical card delivery costs approx ₹107 within India."},
            {"step": 5, "title": "Download e-PAN / Receive Physical Card", "description": "Download e-PAN PDF within hours, or receive physical plastic card via post in 7-10 working days."}
        ],
        "verification_notes": "Instant e-PAN via Income Tax portal is completely free for Aadhaar holders. Physical card application costs ₹107."
    },
    "voter_id": {
        "id": "voter_id",
        "title": "Voter ID / Election Card Services",
        "category": "Electoral Services",
        "jurisdiction": "Central",
        "jurisdiction_label": "Election Commission of India (ECI / Voter Services Portal)",
        "icon": "🗳️",
        "description": "Apply for new Voter ID (Form 6), address change/shifting (Form 8), or download e-EPIC.",
        "official_url": "https://voters.eci.gov.in/",
        "portal_name": "Official Voter Services Portal (ECI)",
        "is_verified": True,
        "keywords": ["voter", "voter id", "election card", "nvsp", "e-epic", "voter registration", "form 6", "form 8", "shift voter address"],
        "documents": [
            {"name": "Passport Size Photograph", "status": "Typically required", "required": True, "why_needed": "For printing on Voter ID / e-EPIC", "check_note": "White background, clear recent photo"},
            {"name": "Proof of Age / DOB (Aadhaar / Birth Cert / Birth Certificate)", "status": "Typically required", "required": True, "why_needed": "Confirms age eligibility (18+ years)", "check_note": "Applicant must be 18 on qualifying date"},
            {"name": "Proof of Address (Aadhaar / Electricity Bill / Water Bill / Rent Agreement)", "status": "Typically required", "required": True, "why_needed": "Determines constituency & polling station", "check_note": "Must reflect current address"}
        ],
        "steps": [
            {"step": 1, "title": "Access ECI Voter Portal", "description": "Visit voters.eci.gov.in and log in or create an account using your mobile number."},
            {"step": 2, "title": "Select Required Form", "description": "Choose Form 6 for new voter enrolment, or Form 8 for address change / correction."},
            {"step": 3, "title": "Upload Photo & Supporting Documents", "description": "Fill personal details, upload photograph, age proof, and current address proof."},
            {"step": 4, "title": "Field Verification by BLO", "description": "Booth Level Officer (BLO) will conduct field verification at your residence."},
            {"step": 5, "title": "Download e-EPIC Voter Card", "description": "Upon approval, download digitally signed e-EPIC PDF from voters.eci.gov.in."}
        ],
        "verification_notes": "Voter enrolment and address correction via Form 6 / Form 8 on ECI portal are free of charge."
    },
    "driving_licence": {
        "id": "driving_licence",
        "title": "Driving Licence & Vehicle RTO Services",
        "category": "Transport & RTO",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana Transport Dept / Ministry of Road Transport (Parivahan)",
        "icon": "🚗",
        "description": "Apply for Learner's Licence (LLR), Permanent Driving Licence (DL), DL renewal, or vehicle RC transfer in Telangana.",
        "official_url": "https://parivahan.gov.in/",
        "portal_name": "Official Parivahan Sewa & Telangana Transport Portal",
        "is_verified": True,
        "keywords": ["driving licence", "driving license", "llr", "dl renewal", "rto telangana", "parivahan", "vehicle rc", "rto hyderabad", "renew driving licence", "renew driving license", "renew my driving licence", "renew my driving license", "driving permit", "rto"],
        "documents": [
            {"name": "Proof of Age (Aadhaar / Passport / SSLC Certificate)", "status": "Typically required", "required": True, "why_needed": "Confirms minimum age eligibility (18+ for 4-wheeler/non-geared)", "check_note": "Name must match Aadhaar"},
            {"name": "Proof of Address (Aadhaar / Utility Bill / Passport)", "status": "Typically required", "required": True, "why_needed": "Assigns local RTO jurisdiction", "check_note": "Must belong to Telangana state for TS RTO"},
            {"name": "Learner's Licence (LLR) Number", "status": "May be required depending on your case", "required": False, "why_needed": "Mandatory before applying for Permanent DL", "check_note": "LLR must be valid (>30 days old and <180 days old)"},
            {"name": "Medical Certificate (Form 1-A)", "status": "May be required depending on your case", "required": False, "why_needed": "Required for applicants over 40 years or commercial DL", "check_note": "Signed by registered medical practitioner"}
        ],
        "steps": [
            {"step": 1, "title": "Apply for Learner's Licence (LLR) Online", "description": "Visit parivahan.gov.in or transport.telangana.gov.in, fill LLR application, and pass online road safety test."},
            {"step": 2, "title": "Book Slot for Permanent DL Test", "description": "After 30 days of LLR issuance, log in to Parivahan portal and book a driving slot at your local TS RTO."},
            {"step": 3, "title": "Visit RTO for Driving Track Test", "description": "Appear at the designated RTO track with your vehicle, LLR, and original documents."},
            {"step": 4, "title": "Biometric Capture & Test Approval", "description": "Upon passing the driving test, complete photo and biometric capture at RTO desk."},
            {"step": 5, "title": "Receive Smart Card DL", "description": "Smart card DL will be dispatched via post, or download digital DL on DigiLocker / mParivahan app."}
        ],
        "verification_notes": "Official fees: LLR test fee ₹150 + ₹50 slot fee; Permanent DL fee ₹200 + ₹300 test fee + ₹200 smart card fee."
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
        "keywords": ["birth certificate", "birth registration", "born certificate", "meeseva birth cert", "ghmc birth certificate", "birth cert", "apply for a birth certificate", "newborn", "birth"],
        "documents": [
            {"name": "Hospital Birth Discharge Slip / Birth Report", "status": "Typically required", "required": True, "why_needed": "Issued by hospital / nursing home where child was born", "check_note": "Contains official hospital stamp and reference"},
            {"name": "Parents' Aadhaar Cards", "status": "Typically required", "required": True, "why_needed": "Identity and address proof of both mother and father", "check_note": "Names must match hospital admission records"},
            {"name": "Parents' Marriage Certificate or Ration Card", "status": "May be required depending on your case", "required": False, "why_needed": "Verification of parents' legal relationship", "check_note": "Helpful in case of name discrepancies"},
            {"name": "Affidavit from Revenue Officer / Magistrate", "status": "May be required depending on your case", "required": False, "why_needed": "Mandatory for Late Birth Registration (>1 year after birth)", "check_note": "Requires RDO approval in Telangana"}
        ],
        "steps": [
            {"step": 1, "title": "Hospital Registration Check", "description": "Hospitals in Telangana automatically record births in GHMC/CDMA portal. Obtain hospital reference number."},
            {"step": 2, "title": "Apply via MeeSeva Portal / Center", "description": "Visit ts.meeseva.telangana.gov.in or any authorized MeeSeva kiosk in Telangana with hospital slip and parents' Aadhaar."},
            {"step": 3, "title": "Fill Birth Certificate Application", "description": "Provide child's name (or apply for name inclusion), DOB, place of birth, and parents' details."},
            {"step": 4, "title": "Pay Service Fee", "description": "Pay official MeeSeva user charges (approx ₹35 - ₹50 per copy)."},
            {"step": 5, "title": "Download Digitally Signed Certificate", "description": "Once approved by GHMC Registrar, download digitally signed PDF from MeeSeva or collect printed copy."}
        ],
        "verification_notes": "Birth registration within 21 days is free at local municipal offices. Late registration beyond 1 year requires RDO permission."
    },
    "death_certificate": {
        "id": "death_certificate",
        "title": "Death Certificate Services",
        "category": "Civil Registration",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana State Government (GHMC / MeeSeva)",
        "icon": "📜",
        "description": "Register death or obtain official death certificate in Greater Hyderabad (GHMC) and Telangana state.",
        "official_url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "portal_name": "Official Telangana MeeSeva & GHMC Portal",
        "is_verified": True,
        "keywords": ["death certificate", "death registration", "meeseva death certificate", "ghmc death certificate"],
        "documents": [
            {"name": "Medical Certificate of Cause of Death (Form 4/4A)", "status": "Typically required", "required": True, "why_needed": "Issued by attending doctor or hospital", "check_note": "Must state medical cause of death"},
            {"name": "Cremation / Burial Ground Slip", "status": "Typically required", "required": True, "why_needed": "Confirms disposal of mortal remains in municipal limits", "check_note": "Issued by authorized cemetery/crematorium"},
            {"name": "Deceased Person's Aadhaar Card", "status": "Typically required", "required": True, "why_needed": "For identity verification and record marking", "check_note": "Aadhaar number will be recorded"},
            {"name": "Applicant's Aadhaar Card & ID Proof", "status": "Typically required", "required": True, "why_needed": "Confirms relationship of applicant (family member)", "check_note": "Address proof of applicant"}
        ],
        "steps": [
            {"step": 1, "title": "Obtain Hospital & Burial Slips", "description": "Collect Form 4 death report from hospital and burial/crematorium acknowledgement slip."},
            {"step": 2, "title": "Apply via MeeSeva Portal / GHMC Citizen Center", "description": "Submit application on ts.meeseva.telangana.gov.in or at any GHMC Citizen Service Center."},
            {"step": 3, "title": "Verification by Municipal Health Officer", "description": "GHMC Assistant Medical Officer of Health (AMOH) verifies records."},
            {"step": 4, "title": "Download Digitally Signed Certificate", "description": "Download death certificate PDF from MeeSeva portal after approval."}
        ],
        "verification_notes": "Death registration within 21 days is free. Official MeeSeva application fee is ₹35 per certified copy."
    },
    "caste_income_certificate": {
        "id": "caste_income_certificate",
        "title": "Caste, Income & Residence Certificates",
        "category": "Revenue Services",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana Revenue Dept (MeeSeva / Revenue Department)",
        "icon": "📑",
        "description": "Apply for Integrated Community, Nativity, Caste Certificate, or Annual Income Certificate in Telangana.",
        "official_url": "https://ts.meeseva.telangana.gov.in/meeseva/home.htm",
        "portal_name": "Official Telangana MeeSeva Portal",
        "is_verified": True,
        "keywords": ["caste certificate", "income certificate", "residence certificate", "meeseva caste", "meeseva income", "nativity certificate", "integrated certificate", "caste", "income cert", "get an income certificate", "meeseva", "meeseva services"],
        "documents": [
            {"name": "Applicant & Father's Aadhaar Cards", "status": "Typically required", "required": True, "why_needed": "Identity & demographic details verification", "check_note": "Aadhaar must be linked to active mobile"},
            {"name": "Ration Card / Food Security Card / Voter ID", "status": "Typically required", "required": True, "why_needed": "Family income and household validation", "check_note": "Name must feature on card"},
            {"name": "Salary Certificate / IT Returns / Property Tax Receipt", "status": "May be required depending on your case", "required": False, "why_needed": "Income proof for Income Certificate application", "check_note": "Employer salary slip or self-declaration"},
            {"name": "School Leaving Certificate / Bonafide Certificate", "status": "May be required depending on your case", "required": False, "why_needed": "Caste and nativity proof for students", "check_note": "Shows caste recorded during admission"}
        ],
        "steps": [
            {"step": 1, "title": "Log in to MeeSeva Portal", "description": "Access ts.meeseva.telangana.gov.in or visit nearest MeeSeva kiosk."},
            {"step": 2, "title": "Select Certificate Type & Fill Form", "description": "Choose 'Income Certificate' or 'Integrated Caste Certificate' under Revenue services."},
            {"step": 3, "title": "Upload Scanned Documents & Submit Application", "description": "Upload Aadhaar, ration card, self-declaration form, and income proofs."},
            {"step": 4, "title": "MRO / VRO Field Enquiry", "description": "Village Revenue Officer (VRO) and Tahsildar verify details."},
            {"step": 5, "title": "Download Certificate with QR Code", "description": "Download digitally signed certificate from MeeSeva upon Tahsildar approval."}
        ],
        "verification_notes": "Official MeeSeva application user fee is ₹45. Income certificate validity in Telangana is 1 year."
    },
    "property_tax": {
        "id": "property_tax",
        "title": "Property Tax Payment & Assessment",
        "category": "Municipal Services",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana State Government (GHMC / CDMA)",
        "icon": "🏠",
        "description": "Pay property tax, calculate assessment, download tax receipt, or search PTIN in Greater Hyderabad (GHMC) and Telangana Municipalities.",
        "official_url": "https://www.ghmc.gov.in/",
        "portal_name": "Official GHMC & CDMA Telangana Portal",
        "is_verified": True,
        "keywords": ["property tax", "house tax", "ghmc property tax", "ptin", "telangana property tax", "cdma property tax", "pay property tax", "ghmc tax", "pay house tax", "tax demand", "tax notice"],
        "documents": [
            {"name": "Property Tax Identification Number (PTIN)", "status": "Typically required", "required": True, "why_needed": "10-digit unique PTIN number for existing property", "check_note": "Find on previous receipt or search by owner name"},
            {"name": "Registered Sale Deed / Ownership Documents", "status": "May be required depending on your case", "required": False, "why_needed": "Required only for fresh property assessment / mutation", "check_note": "Must be registered at Sub-Registrar Office"},
            {"name": "Occupancy Certificate (OC) / Building Plan", "status": "May be required depending on your case", "required": False, "why_needed": "For new building tax assessment", "check_note": "Issued by GHMC town planning wing"},
            {"name": "Owner's Aadhaar Card & Mobile Number", "status": "Typically required", "required": True, "why_needed": "For OTP authentication during online payment", "check_note": "OTP will be sent to registered mobile"}
        ],
        "steps": [
            {"step": 1, "title": "Locate 10-Digit PTIN Number", "description": "Find PTIN on previous receipt or search by door number on ghmc.gov.in or cdma.telangana.gov.in."},
            {"step": 2, "title": "Access GHMC Property Tax Portal", "description": "Navigate to Property Tax payment section on GHMC portal."},
            {"step": 3, "title": "Verify Outstanding Dues & Rebates", "description": "Enter PTIN, verify property details, and check 5% early bird rebate (applicable in April)."},
            {"step": 4, "title": "Pay Online", "description": "Pay securely using Net Banking, UPI, Credit/Debit Card, or at MeeSeva center."},
            {"step": 5, "title": "Download Receipt", "description": "Download digitally signed official GHMC property tax receipt."}
        ],
        "verification_notes": "Verified against GHMC & CDMA Telangana portals. 5% early bird discount applies if paid before April 30."
    },
    "welfare_schemes": {
        "id": "welfare_schemes",
        "title": "Telangana Welfare Schemes & ePASS Scholarships",
        "category": "Welfare & Scholarships",
        "jurisdiction": "Telangana",
        "jurisdiction_label": "Telangana Welfare Departments (ePASS / Govt of Telangana)",
        "icon": "🎓",
        "description": "Apply for ePASS post-matric scholarship, Kalyana Lakshmi / Shaadi Mubarak, Rythu Bandhu, or pension schemes in Telangana.",
        "official_url": "https://telanganaepass.cgg.gov.in/",
        "portal_name": "Official Telangana ePASS & Welfare Portal",
        "is_verified": True,
        "keywords": ["epass", "epass telangana", "scholarship telangana", "kalyana lakshmi", "shaadi mubarak", "rythu bandhu", "aasara pension"],
        "documents": [
            {"name": "Student / Beneficiary Aadhaar Card", "status": "Typically required", "required": True, "why_needed": "Mandatory DBTL / Direct Benefit Transfer verification", "check_note": "Aadhaar must be seeded with Bank Account"},
            {"name": "Valid Income Certificate (MeeSeva)", "status": "Typically required", "required": True, "why_needed": "Verifies family income criteria (<₹2 Lakhs p.a. for urban)", "check_note": "Must be issued in current financial year"},
            {"name": "Caste Certificate (MeeSeva)", "status": "Typically required", "required": True, "why_needed": "Determines category (SC/ST/BC/EBC/Minority)", "check_note": "Permanent caste certificate copy"},
            {"name": "Bank Passbook First Page Copy", "status": "Typically required", "required": True, "why_needed": "For direct bank transfer of scholarship / assistance", "check_note": "IFSC code and account number clearly legible"}
        ],
        "steps": [
            {"step": 1, "title": "Access Telangana ePASS Portal", "description": "Visit telanganaepass.cgg.gov.in for scholarships or designated welfare portal."},
            {"step": 2, "title": "Select Fresh / Renewal Application", "description": "Choose appropriate scheme link (Fresh Post-Matric Scholarship / Kalyana Lakshmi)."},
            {"step": 3, "title": "Enter Aadhaar & CET/SSC Details", "description": "Provide SSC hall ticket number, Aadhaar number, and MeeSeva certificate IDs."},
            {"step": 4, "title": "Upload Document Scans", "description": "Upload scanned bank passbook, income cert, caste cert, and college bonafide."},
            {"step": 5, "title": "College / District Welfare Officer Verification", "description": "Application will be verified by institution principal and District Welfare Officer."}
        ],
        "verification_notes": "Official ePASS portal managed by CGG Telangana. No fee is charged for online application submission."
    },
    "business_msme": {
        "id": "business_msme",
        "title": "Business & MSME Udyam Registration",
        "category": "Business & Commerce",
        "jurisdiction": "Central",
        "jurisdiction_label": "Ministry of MSME & Telangana TS-iPASS",
        "icon": "💼",
        "description": "Register Micro, Small, or Medium Enterprise (Udyam Registration) or apply for TS-iPASS industrial clearances in Telangana.",
        "official_url": "https://udyamregistration.gov.in/",
        "portal_name": "Official Udyam MSME Portal & TS-iPASS",
        "is_verified": True,
        "keywords": ["udyam", "msme", "business registration", "ts-ipass", "gst", "udyog aadhaar", "company registration"],
        "documents": [
            {"name": "Entrepreneur's Aadhaar Card", "status": "Typically required", "required": True, "why_needed": "Mandatory for Udyam registration", "check_note": "Aadhaar must belong to proprietor or partner/director"},
            {"name": "PAN Card of Business / Proprietor", "status": "Typically required", "required": True, "why_needed": "ITR and investment/turnover verification", "check_note": "GSTIN and ITR data fetched automatically"},
            {"name": "Bank Account Details", "status": "Typically required", "required": True, "why_needed": "Account number and IFSC for government subsidies", "check_note": "Business or savings bank account"},
            {"name": "GSTIN Number", "status": "May be required depending on your case", "required": False, "why_needed": "Mandatory for enterprises liable under GST rules", "check_note": "Fetched automatically via PAN link"}
        ],
        "steps": [
            {"step": 1, "title": "Access Official Udyam Portal", "description": "Visit udyamregistration.gov.in (Official Govt site - completely free)."},
            {"step": 2, "title": "Enter Aadhaar & OTP Verification", "description": "Enter 12-digit Aadhaar and authenticate via OTP received on registered mobile."},
            {"step": 3, "title": "Fill Enterprise Details", "description": "Enter business name, activity type (Manufacturing/Services), bank details, and employee count."},
            {"step": 4, "title": "PAN & GST Validation", "description": "System validates PAN and investment details with Income Tax database."},
            {"step": 5, "title": "Download Udyam Registration Certificate", "description": "Instant generation of lifetime Udyam Registration Certificate with QR Code."}
        ],
        "verification_notes": "Udyam Registration is 100% free of charge on udyamregistration.gov.in. Beware of private fake portals charging fees."
    },
    "itr_filing": {
        "id": "itr_filing",
        "title": "Income Tax Return (ITR) Filing",
        "category": "Taxation & Finance",
        "jurisdiction": "Central",
        "jurisdiction_label": "Central Government (Income Tax Department)",
        "icon": "📊",
        "description": "File annual Income Tax Return (ITR-1, ITR-2, ITR-4), check tax refund status, or link PAN with Aadhaar.",
        "official_url": "https://www.incometax.gov.in/iec/foportal/",
        "portal_name": "Official Income Tax e-Filing Portal",
        "is_verified": True,
        "keywords": ["itr", "income tax return", "itr filing", "tax refund", "form 16", "26as", "ais", "pan aadhaar link"],
        "documents": [
            {"name": "Form 16 / Form 16A", "status": "Typically required", "required": True, "why_needed": "Issued by employer showing salary and TDS deducted", "check_note": "Part A & Part B signed by employer"},
            {"name": "Annual Information Statement (AIS) & Form 26AS", "status": "Typically required", "required": True, "why_needed": "Consolidated record of tax deducted, dividend, and interest income", "check_note": "Download directly from e-Filing portal"},
            {"name": "Bank Account Statements & Interest Certificates", "status": "Typically required", "required": True, "why_needed": "Reports interest earned on savings/FD accounts", "check_note": "Ensure bank account is pre-validated for refund"},
            {"name": "Tax Saving Proofs (Section 80C, 80D, HRA)", "status": "May be required depending on your case", "required": False, "why_needed": "Claims deductions under Old Tax Regime", "check_note": "ELSS, PPF, LIC, Health Insurance receipts"}
        ],
        "steps": [
            {"step": 1, "title": "Log in to e-Filing Portal", "description": "Visit incometax.gov.in using your PAN / Aadhaar as User ID and password."},
            {"step": 2, "title": "Verify Pre-filled Data (AIS & 26AS)", "description": "Check pre-filled income, salary, and TDS details under 'File Income Tax Return'."},
            {"step": 3, "title": "Choose Tax Regime & Form (ITR-1 / ITR-2)", "description": "Select Assessment Year and opt for New Tax Regime or Old Tax Regime."},
            {"step": 4, "title": "Submit & e-Verify via Aadhaar OTP", "description": "Complete e-Verification within 30 days using Aadhaar OTP or Net Banking to complete filing."},
            {"step": 5, "title": "Track Refund Status", "description": "Track processing and tax refund credit directly on portal dashboard."}
        ],
        "verification_notes": "Verified against Income Tax Department rules. e-Verification within 30 days is mandatory for ITR processing."
    }
}


# General fallback guidance for state vs central determination
JURISDICTION_RULES = {
    "telangana_keywords": ["telangana", "hyderabad", "ghmc", "meeseva", "cyberabad", "secunderabad", "warangal", "cdma", "ts", "epass ts", "ts-ipass"],
    "central_keywords": ["passport", "aadhaar", "pan", "income tax", "pancard", "railway", "irctc", "passport seva", "uidai", "epfo", "voter", "udyam", "itr"]
}


# Notice Parsing Helper Template
NOTICE_PARSER_TEMPLATE = {
    "supported_notices": ["Tax Notice", "RTO Notice", "Municipal Property Tax Demand", "Aadhaar Correction Notice", "Passport Verification Query"],
    "disclaimer": "This explanation is informational only. Always verify official requirements against the issuing authority."
}


# "Do It For Me" Automation Limits Template
DO_IT_FOR_ME_RULES = {
    "internal_safe_actions": [
        "Organize document checklist",
        "Prepare draft form-field responses",
        "Generate step-by-step submission plan",
        "Identify exact official government portal URL"
    ],
    "external_portal_restrictions": [
        "Cannot submit applications directly on external portal",
        "Cannot bypass OTP, CAPTCHA, or password controls",
        "Cannot access private government accounts without authorized user login"
    ]
}


def get_verified_service_by_key(service_key: str):
    """Returns curated service details for supported services."""
    return SERVICES_DATABASE.get(service_key.lower())


import re

def search_service_by_query(query: str):
    """Matches query text against keywords in the local knowledge base using word boundaries and scoring."""
    if not query:
        return None
    query_lower = query.lower().strip()

    best_service = None
    best_score = 0

    for key, service in SERVICES_DATABASE.items():
        for kw in service["keywords"]:
            kw_lower = kw.lower()
            # Escape regex characters
            pattern = r'\b' + re.escape(kw_lower) + r'\b'
            if re.search(pattern, query_lower):
                # Score based on length of matched keyword (longer keywords are more specific)
                score = len(kw_lower) * 10
                # Exact title or id match bonus
                if kw_lower == key or kw_lower == service["title"].lower():
                    score += 50
                if score > best_score:
                    best_score = score
                    best_service = service
            elif len(kw_lower) > 3 and kw_lower in query_lower:
                # Substring match for longer multi-word phrases
                score = len(kw_lower) * 5
                if score > best_score:
                    best_score = score
                    best_service = service

    return best_service
