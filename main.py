"""
Chatzy AI Document Verification Pipeline
---------------------------------------
OCR + LLM-based entity extraction + cross-document validation
Generates outputs/results.json
"""

import os, json, re, unicodedata
from pathlib import Path
from PIL import Image
import pytesseract
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from rapidfuzz import fuzz
from dateutil import parser as dateparser

# ----------------- Configuration -----------------
DATA_DIR = "data/raw"         # your extracted dataset
OUTPUT_JSON = "outputs/results.json"
MODEL_NAME = "google/flan-t5-small"

os.makedirs("outputs", exist_ok=True)

# ----------------- OCR Function -----------------
def ocr_image(path):
    img = Image.open(path).convert("RGB")
    text = pytesseract.image_to_string(img, lang="eng")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n\s+\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text

# ----------------- Load LLM -----------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
gen = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)

PROMPT_TEMPLATE = """
Extract structured fields from the following OCR text of an Indian personal document.
Fields: Full Name, Father's Name, Date of Birth, Complete Address, Phone Number, Email Address, Aadhaar Number, PAN Number, Employee ID, Account Number.
Output JSON only. Empty string if not found.

Input:
\"\"\"{ocr_text}\"\"\"
"""

def parse_ocr_to_json(ocr_text, max_length=512):
    prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text[:max_length*4])
    out = gen(prompt, max_length=256, do_sample=False)[0]["generated_text"]
    out = out.strip()
    try:
        m = re.search(r'\{.*\}', out, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
        return {}
    except:
        return {}

# ----------------- Normalization & Validation -----------------
def normalize_name(s): return re.sub(r'\s+', ' ', (s or "").strip().upper())
def normalize_phone(s): 
    s = re.sub(r'\D','', s or "")
    return s[-10:] if len(s)>10 else s
def normalize_dob(s):
    try: return dateparser.parse(s, dayfirst=True, fuzzy=True).strftime("%Y-%m-%d")
    except: return s
def pan_valid(s): return bool(re.match(r'^[A-Z]{5}\d{4}[A-Z]$', (s or "").upper()))
def aadhaar_valid(s): return bool(re.match(r'^\d{12}$', re.sub(r'\D','', s or "")))
def fuzzy_match(a,b,threshold=85): return fuzz.token_sort_ratio(a,b) >= threshold if a and b else False

def apply_verification_rules(extracted_docs):
    docs = list(extracted_docs.keys())
    norm = {}
    for d in docs:
        doc = extracted_docs[d]
        norm[d] = {
            "Full Name": normalize_name(doc.get("Full Name","")),
            "Father's Name": normalize_name(doc.get("Father's Name","")),
            "Date of Birth": normalize_dob(doc.get("Date of Birth","")),
            "Complete Address": (doc.get("Complete Address","") or "").upper(),
            "Phone Number": normalize_phone(doc.get("Phone Number","")),
            "Email Address": (doc.get("Email Address","") or "").lower(),
            "Aadhaar Number": re.sub(r'\D','', doc.get("Aadhaar Number","")),
            "PAN Number": (doc.get("PAN Number","") or "").upper()
        }
    results = {}
    results['rule_1_name_match'] = {"status": "PASS" if all(fuzzy_match(norm[docs[0]]["Full Name"], norm[d]["Full Name"]) for d in docs[1:]) else "FAIL"}
    results['rule_2_dob_match'] = {"status": "PASS" if all(norm[docs[0]]["Date of Birth"]==norm[d]["Date of Birth"] for d in docs[1:]) else "FAIL"}
    results['rule_3_address_match'] = {"status": "PASS" if all(fuzzy_match(norm[docs[0]]["Complete Address"], norm[d]["Complete Address"], 80) for d in docs[1:]) else "FAIL"}
    results['rule_4_phone_match'] = {"status": "PASS" if all(norm[docs[0]]["Phone Number"]==norm[d]["Phone Number"] for d in docs[1:]) else "FAIL"}
    results['rule_5_father_name_match'] = {"status": "PASS" if all(fuzzy_match(norm[docs[0]]["Father's Name"], norm[d]["Father's Name"]) for d in docs[1:]) else "FAIL"}
    results['rule_6_pan_format'] = {"status": "PASS" if all(pan_valid(norm[d]['PAN Number']) or norm[d]['PAN Number']=="" for d in docs) else "FAIL"}
    results['rule_7_aadhaar_format'] = {"status": "PASS" if all(aadhaar_valid(norm[d]['Aadhaar Number']) or norm[d]['Aadhaar Number']=="" for d in docs) else "FAIL"}
    overall = "VERIFIED" if all(v['status']=="PASS" for v in results.values()) else "FAILED"
    return results, overall

# ----------------- Process Each Person -----------------
def process_person(person_id, filepaths):
    extracted = {}
    for idx, fp in enumerate(filepaths, start=1):
        extracted[f"document_{idx}"] = parse_ocr_to_json(ocr_image(fp))
    verification, overall = apply_verification_rules(extracted)
    return {"person_id": person_id, "extracted_data": extracted, "verification_results": verification, "overall_status": overall}

# ----------------- Main Execution -----------------
all_persons = []
grouped_files = sorted(Path(DATA_DIR).rglob("*.*"))

# Simple grouping by prefix (first 4 chars)
from collections import defaultdict
groups = defaultdict(list)
for f in grouped_files: groups[f.name[:4]].append(str(f))

for pid, files in groups.items():
    all_persons.append(process_person(pid, files[:3]))

# Save JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_persons, f, indent=2)

print(f"✅ Results saved in {OUTPUT_JSON}")
