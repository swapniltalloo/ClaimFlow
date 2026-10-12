# ClaimFlow API Specification

## Base URL & Interactive Docs
- **Local Development Server:** `http://localhost:8000`
- **Interactive Swagger OpenAPI Docs:** `http://localhost:8000/docs`
- **Interactive ReDoc Documentation:** `http://localhost:8000/redoc`

---

## 1. System Health & Readiness

### `GET /health`
Returns system status, service name, environment, and 15-minute SLA target.

**Response:**
```json
{
  "status": "healthy",
  "service": "ClaimFlow Clearinghouse",
  "environment": "development",
  "sla_target_minutes": 15.0
}
```

### `GET /ready`
Verifies database connection (PostgreSQL / SQLite fallback), vector store availability, and runtime engine.

---

## 2. Ingestion & Claims Clearinghouse

### `POST /api/v1/claims/discharge`
Hospital EHR webhook / discharge endpoint triggered upon patient discharge.

**Request Body (`application/json`):**
```json
{
  "claim": {
    "claim_id": "CLM-2026-00042",
    "patient_id": "PAT-99120",
    "policy_id": "POL-STAR-ASSURE-001",
    "hospital_id": "HOSP-001",
    "hospital_name": "Apollo Super Specialty Hospital",
    "primary_diagnosis": "Acute Appendicitis (ICD-10: K35.80)",
    "total_claimed_amount": 92500.0,
    "line_items": [...]
  },
  "discharge_summary": "Patient presented with acute lower abdominal pain...",
  "fhir_bundle": null,
  "policy_tenure_days": 180
}
```

**Response:** Full adjudication payload including stage latencies, line-item verdicts (`OK`, `DEDUCTION`, `MISMATCH`), composite fraud score, payable amount, and mock UPI/NEFT transaction receipt.

---

### `POST /api/v1/claims/upload-pdf`
Uploads a hospital bill PDF, extracts structured clinical and billing line items via **Google Gemini Flash** + **`pypdf`**, and executes real-time 15-minute clearinghouse adjudication.

**Request (`multipart/form-data`):**
- `file`: The hospital discharge invoice or itemized bill PDF file.
- `policy_id`: Selected insurance policy ID (e.g., `POL-STAR-ASSURE-001`, `POL-HDFC-OPTIMA-001`, etc.).
- `policy_tenure_days`: Policy in-force tenure (integer, default: `180`).

**Response:**
```json
{
  "claim_id": "CLM-PDF-152144",
  "outcome": "PARTIAL_SETTLE",
  "approved_amount": 68500.0,
  "deductions_amount": 4500.0,
  "line_items": [...],
  "pdf_metadata": {
    "filename": "apollo_clean_hospital_bill.pdf",
    "pages_parsed": 1,
    "extraction_engine": "Google Gemini Flash (Clinical NLP & Table Parser)",
    "patient_name": "Priya Sharma",
    "hospital_name": "Apollo Super Specialty Hospital",
    "primary_diagnosis": "Acute Appendicitis",
    "total_claimed_amount": 73000.0
  },
  "stage_latencies": {...},
  "audit_hash": "..."
}
```

---

### `GET /api/v1/claims/sample-pdf/{sample_name}`
Downloads or streams pre-generated sample hospital bill PDFs for immediate testing (`apollo`, `max`).

---

### `GET /api/v1/claims`
Lists all processed claims and their current clearinghouse adjudication statuses.

---

### `GET /api/v1/claims/{claim_id}`
Retrieves full details, breakdown, stage execution times, and audit verdicts for a specific claim.

---

### `GET /api/v1/claims/{claim_id}/evidence-pack`
Generates an evidence dossier for human reviewer queues (mismatches, EHR excerpts, policy clause citations).

---

### `POST /api/v1/claims/{claim_id}/adjudicate`
Manual override / approval action from human adjudicator or medical director.

---

## 3. Google Cloud Healthcare API & ABDM / NHCX Ingestion

### `POST /api/v1/gcp/fhir/ingest-bundle`
Ingests a raw FHIR R4 ClaimBundle conforming to India's **ABDM** (Ayushman Bharat Digital Mission) and **NHCX** (National Health Claims Exchange) standards.
- Ingests `Patient` (ABHA ID), `Encounter`, `Condition`, `Procedure`, and itemized `Claim`.
- Automatically executes full 5-agent clearinghouse adjudication.
- Returns clearinghouse decision **plus** a compliant NDHM `ClaimResponse` resource.

---

### `POST /api/v1/gcp/fhir/sync-store/{bundle_id}`
Pulls a FHIR Bundle directly from the configured Google Cloud Healthcare API FHIR R4 Store (`projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}/datasets/{GCP_DATASET_ID}/fhirStores/{GCP_FHIR_STORE_ID}`) and runs end-to-end adjudication.

---

### `GET /api/v1/gcp/fhir/sample-nhcx`
Returns the reference 254-line ABDM / NHCX FHIR R4 ClaimBundle for demonstration and testing.

---

### `GET /api/v1/gcp/fhir/status`
Returns live connectivity and authentication status for Google Cloud integrations:
- **Google Gemini API:** Active model (`gemini-flash-latest`), connection status.
- **Google Cloud Vertex AI Embeddings:** Active model (`text-embedding-004`), 768-dim embeddings.
- **Google Cloud Healthcare API:** Active FHIR R4 Store URI, masked API key status.

---

## 4. Hospital Automated Claim Appeal & Evidence Engine

### `POST /api/v1/hospital/claims/{claim_id}/auto-appeal`
Hospital-side closed-loop appeal generator:
1. Detects adverse adjudication or query codes (`IRDAI-QRY-001`, `IRDAI-QRY-002`, `IRDAI-DEN-003`).
2. Gathers missing clinical proofs from hospital HIS (operative notes, implant invoices, histopathology reports).
3. Builds an authentic NHCX FHIR Appeal Bundle with `Communication` and `DocumentReference` resources.
4. Generates a formal legal appeal letter citing GIPSA empanelment rules and re-submits for approval.

---

### `GET /api/v1/hospital/evidence-matrix`
Returns the GIPSA and IRDAI denial-to-evidence checklist matrix mapping 6 standard denial patterns to required hospital documentation.

---

### `GET /api/v1/hospital/policies-catalog`
Returns the catalog of 9 real health insurance policies indexed in the RAG store (Star Health, HDFC ERGO, Care Health, Niva Bupa, New India Assurance, Aditya Birla, ICICI Lombard, Bajaj Allianz, Tata AIG).
