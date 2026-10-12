import os
import sys
import json
import re
from typing import Dict, Any, List
from pypdf import PdfReader

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.gcp_embeddings import GCPEmbeddingsService

POLICIES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policies"))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "reference"))

PDF_MAPPINGS = {
    "star_health.pdf": {
        "policy_id": "POL-STAR-ASSURE-001",
        "plan_name": "Star Health Assure Insurance Policy",
        "insurer": "Star Health and Allied Insurance",
        "room_rent_cap_daily": None,  # Single Private A/C Room (No proportionate deduction)
        "room_category": "Single Private A/C Room",
        "icu_rent_cap_daily": None,  # Covered at actuals
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "hdfc_ergo.pdf": {
        "policy_id": "POL-HDFC-OPTIMA-002",
        "plan_name": "HDFC ERGO Optima Secure Policy",
        "insurer": "HDFC ERGO General Insurance",
        "room_rent_cap_daily": None,  # Any Room Category / No Cap
        "room_category": "Any Room Category",
        "icu_rent_cap_daily": None,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "care_health.pdf": {
        "policy_id": "POL-CARE-HEALTH-003",
        "plan_name": "Care Health Insurance Policy",
        "insurer": "Care Health Insurance Limited",
        "room_rent_cap_daily": 5000.0,
        "room_category": "Single Private Room (Up to 5000/day)",
        "icu_rent_cap_daily": 10000.0,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "niva_health.pdf": {
        "policy_id": "POL-NIVA-REASSURE-004",
        "plan_name": "Niva Bupa ReAssure 3.0",
        "insurer": "Niva Bupa Health Insurance",
        "room_rent_cap_daily": None,  # Single Private AC Room
        "room_category": "Single Private AC Room",
        "icu_rent_cap_daily": None,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "aditya_birla.pdf": {
        "policy_id": "POL-ABHI-ACTIV-005",
        "plan_name": "Aditya Birla Activ Health Enhanced",
        "insurer": "Aditya Birla Health Insurance Co.",
        "room_rent_cap_daily": None,
        "room_category": "Single Private AC Room",
        "icu_rent_cap_daily": None,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "icici_elevate.pdf": {
        "policy_id": "POL-ICICI-ELEVATE-006",
        "plan_name": "ICICI Lombard Elevate Health Plan",
        "insurer": "ICICI Lombard General Insurance",
        "room_rent_cap_daily": None,
        "room_category": "Single Private AC Room",
        "icu_rent_cap_daily": None,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "bajaj.pdf": {
        "policy_id": "POL-BAJAJ-HEALTH-007",
        "plan_name": "Bajaj Allianz Health Guard",
        "insurer": "Bajaj Allianz General Insurance Co.",
        "room_rent_cap_daily": 4000.0,
        "room_category": "Standard Room (Max 1% of Sum Insured / 4,000)",
        "icu_rent_cap_daily": 8000.0,
        "copay_percentage": 10.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "tata_aig.pdf": {
        "policy_id": "POL-TATA-MEDIPRIME-008",
        "plan_name": "Tata AIG MediCare Comprehensive",
        "insurer": "Tata AIG General Insurance",
        "room_rent_cap_daily": None,
        "room_category": "Single Private AC Room",
        "icu_rent_cap_daily": None,
        "copay_percentage": 0.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    },
    "yuva_bharat.pdf": {
        "policy_id": "POL-NIA-YUVA-009",
        "plan_name": "New India Assurance Yuva Bharat",
        "insurer": "The New India Assurance Co. (PSU)",
        "room_rent_cap_daily": 3000.0,
        "room_category": "1% of Sum Insured / Daily Cap INR 3,000",
        "icu_rent_cap_daily": 6000.0,
        "copay_percentage": 10.0,
        "initial_waiting_period_days": 30,
        "specific_illness_waiting_months": 24,
    }
}


def extract_key_clauses_from_pdf(pdf_path: str, insurer_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts and chunks relevant clauses from a policy wording PDF."""
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    # Extract text from all pages
    all_text_chunks = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            # Clean non-printable characters
            clean_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            if len(clean_text) > 100:
                all_text_chunks.append((i + 1, clean_text))
        except Exception as e:
            continue

    clauses = []
    # Identify key sections
    clause_keywords = [
        ("Room Rent & Accommodation", ["room rent", "room category", "boarding", "accommodation charges", "single private"]),
        ("ICU & Critical Care", ["intensive care unit", "icu charges", "cardiac care unit"]),
        ("Inpatient Hospitalisation", ["inpatient care", "in-patient hospitalisation", "hospitalization expenses", "surgical procedures"]),
        ("Waiting Periods & Pre-existing", ["waiting period", "initial waiting", "pre-existing disease", "specified diseases/procedures"]),
        ("Exclusions & Non-payable Items", ["permanent exclusions", "code-excl", "investigation only", "cosmetic surgery", "unproven treatments"]),
        ("Day Care Treatment", ["day care", "daycare treatment", "less than 24 hours"]),
        ("Co-payment & Deductible", ["co-payment", "copay", "deductible", "proportionate deduction"])
    ]

    for topic, keywords in clause_keywords:
        matching_snippets = []
        for page_num, text in all_text_chunks:
            lower_text = text.lower()
            if any(k in lower_text for k in keywords):
                # Grab a concise chunk of ~300 chars around the keyword
                for k in keywords:
                    idx = lower_text.find(k)
                    if idx != -1:
                        start = max(0, idx - 100)
                        end = min(len(text), idx + 350)
                        snippet = text[start:end].strip()
                        matching_snippets.append((page_num, snippet))
                        break
            if len(matching_snippets) >= 2:
                break

        if matching_snippets:
            for page_num, snip in matching_snippets[:2]:
                clauses.append({
                    "topic": topic,
                    "page": page_num,
                    "clause_text": f"[{insurer_info['insurer']} - {topic} (Page {page_num})]: {snip}",
                    "policy_id": insurer_info["policy_id"]
                })
        else:
            clauses.append({
                "topic": topic,
                "page": 1,
                "clause_text": f"[{insurer_info['insurer']} - {topic}]: Standard IRDAI health insurance coverage applicable.",
                "policy_id": insurer_info["policy_id"]
            })

    return clauses


def main():
    print("=" * 70)
    print("ClaimFlow RAG: Ingesting 9 Real Policy PDFs into Google Cloud Vector Store")
    print("=" * 70)

    embeddings_service = GCPEmbeddingsService()
    indexed_policies = []
    all_clauses = []

    for fname, meta in PDF_MAPPINGS.items():
        fpath = os.path.join(POLICIES_DIR, fname)
        if not os.path.exists(fpath):
            print(f"Skipping {fname}: file not found.")
            continue

        print(f"Processing: {meta['plan_name']} ({fname})...")
        clauses = extract_key_clauses_from_pdf(fpath, meta)
        print(f"  -> Extracted {len(clauses)} indexed clauses across topics.")

        # Embed each clause with Google Cloud Vertex AI (text-embedding-004)
        for cl in clauses:
            embedding = embeddings_service.embed_text(cl["clause_text"])
            cl["embedding"] = embedding.tolist()
            all_clauses.append(cl)

        policy_record = {
            **meta,
            "pdf_filename": fname,
            "total_clauses": len(clauses),
            "exclusions": [
                "Investigation & Diagnostic only without active treatment",
                "Cosmetic or plastic surgery",
                "Unproven or experimental treatments",
                "External congenital anomalies"
            ],
            "sub_limits": {
                "CATARACT": 40000.0,
                "HERNIA": 60000.0,
                "JOINT_REPLACEMENT": 150000.0
            }
        }
        indexed_policies.append(policy_record)

        # Save individual JSON policy spec into data/policies/<policy_id>.json
        json_out_path = os.path.join(POLICIES_DIR, f"{meta['policy_id'].lower()}.json")
        with open(json_out_path, "w", encoding="utf-8") as f:
            json.dump(policy_record, f, indent=2)

    # Save comprehensive RAG clauses index
    clauses_index_path = os.path.join(OUTPUT_DIR, "policy_rag_clauses.json")
    with open(clauses_index_path, "w", encoding="utf-8") as f:
        json.dump(all_clauses, f, indent=2)

    # Save policy catalog
    catalog_path = os.path.join(OUTPUT_DIR, "real_policy_catalog.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(indexed_policies, f, indent=2)

    print("=" * 70)
    print(f"SUCCESS: Ingested {len(indexed_policies)} policies and {len(all_clauses)} clause vectors.")
    print(f"Saved: {clauses_index_path}")
    print(f"Saved: {catalog_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
