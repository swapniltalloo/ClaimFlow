# ClaimFlow API Specification

## Base URL
- Local Development: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 1. Health & Readiness

### `GET /health`
Returns system status and basic operational metrics.

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
Verifies database connection, pgvector availability, and Redis Streams bus connectivity.

---

## 2. Ingestion & Clearinghouse Pipelines

### `POST /api/v1/claims/discharge`
Hospital EHR webhook triggered upon patient discharge.

**Request:**
- `fhir_bundle`: FHIR R4 Inpatient Encounter Bundle (`Patient`, `Encounter`, `Condition`, `Procedure`, `MedicationRequest`).
- `discharge_summary`: Unstructured physician discharge text.
- `hospital_bill`: Itemized line items submitted for insurance settlement.

**Response (Synchronous Ingestion Ack):**
```json
{
  "claim_id": "CLM-2026-00042",
  "status": "INGESTED",
  "ingested_at": "2026-10-11T23:15:00Z",
  "estimated_completion_time": "2026-10-11T23:18:00Z",
  "sla_deadline": "2026-10-11T23:30:00Z"
}
```

---

## 3. Claim State & Adjudication

### `GET /api/v1/claims/{claim_id}`
Retrieves real-time processing status, line-item verdicts, fraud score, and audit citations.

### `GET /api/v1/claims/{claim_id}/evidence-pack`
Generates an evidence dossier for human reviewer queues (mismatches, EHR excerpts, policy clause citations).

### `POST /api/v1/claims/{claim_id}/adjudicate`
Manual override / approval action from human adjudicator.
