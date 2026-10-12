import os
from pypdf import PdfReader

pdf_dir = "data/policies"
pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

print(f"Total PDFs found: {len(pdf_files)}\n" + "=" * 60)

for f in sorted(pdf_files):
    path = os.path.join(pdf_dir, f)
    try:
        reader = PdfReader(path)
        pages = len(reader.pages)
        first_page = reader.pages[0].extract_text() if pages > 0 else ""
        first_words = " ".join(first_page.split()[:25])
        
        # Scan first 6 pages for core policy sections
        combined_text = " ".join([reader.pages[i].extract_text() or "" for i in range(min(6, pages))]).lower()
        
        has_room_rent = any(w in combined_text for w in ["room rent", "room", "accommodation", "boarding"])
        has_inpatient = any(w in combined_text for w in ["inpatient", "hospitalisation", "hospitalization"])
        has_icu = any(w in combined_text for w in ["icu", "intensive care"])
        has_waiting = any(w in combined_text for w in ["waiting period", "exclusion", "30 days", "pre-existing"])
        has_copay = any(w in combined_text for w in ["copay", "co-payment", "deductible"])

        print(f"File: {f}")
        print(f"  Pages: {pages}")
        print(f"  Snippet: {first_words}...")
        print(f"  Verified Clauses: Room Rent={has_room_rent}, Inpatient={has_inpatient}, ICU={has_icu}, Waiting/Excl={has_waiting}, Copay={has_copay}")
        print("-" * 60)
    except Exception as e:
        print(f"File: {f} -> ERROR: {e}")
        print("-" * 60)
