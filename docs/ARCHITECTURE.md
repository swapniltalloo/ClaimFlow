# ClaimFlow Architecture & System Design

## 1. High-Level Pipeline

```
Hospital EHR/HIS ──► Ingestion API (FHIR/HL7 adapter)
                          │
                    Event Bus (Redis Streams)
                          │
               ┌──────────▼──────────────┐
               │ Orchestrator (LangGraph)│
               └─┬─────┬─────┬─────┬─────┘
                 │     │     │     │
                 │     ├─────┴─────┤
                 │     │ Parallel  │
           EHR Parser  │ Coding ‖  │   Fraud       Settlement
             Agent     │ Policy    │   Agent         Agent
                 │     ├─────┬─────┤     │             │
                 └─────┴─────┴─────┴─────┴─────────────┘
                                   │
               PostgreSQL + pgvector + Audit Trail
                                   │
                    Real-time Claims Dashboard
```

## 2. Agent Responsibilities & Bounds

| Agent | Responsibility | Core Principle | Deterministic Bounds |
|---|---|---|---|
| **EHR Parser Agent** | Extracts structured `ClinicalFacts` from free-text discharge summary and FHIR resources. | Extraction & schema transformation only. | Uses strictly constrained Pydantic schemas; flagged confidence; never invents codes. |
| **Coding Validator** | Validates billed line items against diagnosis-procedure matrices, unbundling rules, and limits. | Deterministic rule execution. | Python rule classes; verdicts: `OK`, `MISMATCH`, `UNSUPPORTED`. |
| **Policy Agent** | Semantic clause retrieval via `pgvector` RAG; calculates payable amounts. | Structured clause extraction + math. | Payable amounts calculated purely by formula; every deduction carries an explicit clause citation. |
| **Fraud Agent** | Layer 1: Deterministic rules (FR-001 to FR-008).<br>Layer 2: Isolation Forest anomaly scoring.<br>Layer 3: Supervised XGBoost classifier + SHAP.<br>Layer 4: NetworkX provider graph anomaly signals. | Statistical & algorithmic classification. | Generates risk score 0–100 with explainable top features. |
| **Settlement Agent** | Evaluates composite decision policy against risk threshold, triggers mock payment gateway, records immutable SHA-256 audit entry. | Transaction execution & audit. | Idempotent execution; replaying a claim never duplicates payment. |

## 3. SLA & Latency Budget (15-Minute Target)

| Pipeline Stage | Target Latency | Max Timeout |
|---|---|---|
| Ingestion & Schema Validation | 10 seconds | 20 seconds |
| EHR Parser Extraction | 45 seconds | 90 seconds |
| Coding + Policy (Parallel) | 60 seconds | 120 seconds |
| Layered Fraud Scoring | 15 seconds | 30 seconds |
| Decision Evaluation & Payment | 30 seconds | 60 seconds |
| **Total Pipeline Execution** | **~3 minutes** | **~5.5 minutes** |

*Remaining 9.5 to 12 minutes reserved for queue buffering, retry backoff, and human-in-the-loop review.*

## 4. Google Cloud AI & Healthcare API Integrations

ClaimFlow integrates three core Google Cloud services designed specifically for enterprise health clearinghouses:

```
Hospital HIS Server
        │ (FHIR R4 Bundle)
        ▼
[1. Google Cloud Healthcare API] ──► Asia-South1 FHIR R4 Store (projects/.../fhirStores/nhcx-store)
        │                             │
        │ Ingestion Adapter           ▼
        │ (ABDM & NHCX Profiles)  Discharge Narrative
        │                             │
        ▼                             ▼
ClaimFlow Orchestrator ◄─── [2. Google Gemini API: gemini-2.5-flash]
        │                   (Schema-constrained ClinicalFacts extraction)
        │
        ├──► Coding Validator (CR-001 to CR-006)
        │
        ├──► [3. Google Cloud Vertex AI Embeddings: text-embedding-004]
        │    (768-dim dense vector embeddings for policy clause RAG)
        │
        ├──► Layered Fraud Agent (Rules, Isolation Forest, XGBoost, Graph)
        │
        ▼
Settlement Agent ──► Dispatches compliant NRCES FHIR ClaimResponse Resource back to HIS
```

### 1. Google Cloud Healthcare API (FHIR R4 Store) - Main Ingestion Adapter
- **Role:** Directly connects to hospital Hospital Information System (HIS) endpoints to ingest authentic ABDM (Ayushman Bharat Digital Mission) and NHCX (National Health Claims Exchange) FHIR R4 bundles.
- **Profiles Handled:** NRCES / NDHM ClaimBundle R4 (`https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimBundle`), including `Patient` (ABHA ID), `Encounter`, `Condition`, `Procedure`, `Claim`, and `DocumentReference`.
- **Response Generation:** Generates authentic NDHM FHIR `ClaimResponse` (`https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimResponse`) containing payment transaction identifiers and line-item adjudications.
- **Implementation:** `backend/app/adapters/gcp_healthcare.py` and `backend/app/api/endpoints/gcp_fhir_ingest.py`.

### 2. Google Gemini API (`gemini-2.5-flash` via `google-genai`)
- **Role:** High-speed, schema-constrained clinical NLP extraction.
- **Model:** `gemini-2.5-flash` with Pydantic structured output.
- **Function:** Parses unstructured physician discharge notes, operative reports, and lab narratives into verified ICD-10 diagnostic codes, CPT procedure codes, and admission lengths.
- **Implementation:** `backend/app/services/gemini_service.py` wired into `backend/app/agents/ehr_parser.py`.

### 3. Google Cloud Vertex AI Embeddings (`text-embedding-004`)
- **Role:** Semantic policy clause and exclusion retrieval.
- **Model:** `text-embedding-004` (768-dimensional dense vector embeddings).
- **Function:** Encodes health insurance policy clauses (room rent caps, waiting periods, sub-limits, exclusions) to match billed procedures and line items deterministically.
- **Implementation:** `backend/app/services/gcp_embeddings.py` wired into `backend/app/agents/policy_agent.py`.

