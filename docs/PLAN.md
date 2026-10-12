# ClaimFlow Phased Implementation Roadmap

## Overview
ClaimFlow is an autonomous AI health insurance clearinghouse designed for the Google Hackathon to parse EHR data in real time, validate hospital bills against policy rules and procedural tariffs, flag suspicious billing patterns, settle legitimate claims within 15 minutes of discharge, and provide hospitals with an automated closed-loop appeal and evidence re-submission engine.

---

## Phase Status Summary

| Phase | Description | Status |
|---|---|---|
| **Phase 0** | Foundations, Scaffolding, Schemas, & Config | **Completed** ✅ |
| **Phase 1** | Synthetic Data & Reference Clinical Taxonomy | **Completed** ✅ |
| **Phase 2** | Multi-Agent Clearinghouse (5 Core Agents) | **Completed** ✅ |
| **Phase 3** | Orchestrator, Async Pipeline & 15-Min SLA Engine | **Completed** ✅ |
| **Phase 4** | Decision Policy & Human-in-the-Loop Review Queue | **Completed** ✅ |
| **Phase 5** | Real-Time Dashboard UI (Vite + Vanilla CSS) | **Completed** ✅ |
| **Phase 6** | Google Cloud Healthcare API & 9 Real Policies Vector RAG | **Completed** ✅ |
| **Phase 7** | Hospital Automated Appeal & Evidence Regeneration Engine | **Completed** ✅ |

---

## Detailed Milestones

### Phase 0: Foundations (Completed ✅)
- [x] Repository scaffolding with standard directory layout.
- [x] Antigravity IDE global rules and workflows.
- [x] Docker Compose definition with PostgreSQL 16 (`pgvector`), Redis 7, and FastAPI.
- [x] Environment configuration management with seamless SQLite fallback.
- [x] Pydantic v2 domain schemas aligned to FHIR R4 and ClaimFlow clearinghouse standards.
- [x] Core FastAPI app structure and health check endpoints.

### Phase 1: Datasets & Reference Dictionaries (Completed ✅)
- [x] Reference medical coding datasets (ICD-10, procedural tariffs, bundling matrix).
- [x] Export `data/synthetic/claims.parquet` with 2,000 cases for fraud model training.
- [x] Reference ABDM / NHCX FHIR R4 claim bundle (`data/reference/nhcx_abdm_sample_bundle.json`).
- [x] Automated validation and distribution audit (`scripts/verify_dataset.py`).

### Phase 2: Core Clearinghouse Agents (Completed ✅)
- [x] **Agent A (EHR Parser):** Extraction of clinical facts, ICD-10 codes, procedure timestamps, and ICU days from unstructured discharge summaries with confidence scoring using Google Gemini API (`gemini-flash-latest`).
- [x] **Agent B (Coding Validator):** Deterministic verification against diagnosis-procedure compatibility matrix, unbundling tables, and line-item validity.
- [x] **Agent C (Policy Agent):** Semantic clause retrieval via 768-dim Google Vertex AI embeddings, rule-driven deductible/copay calculations, and clause citation.
- [x] **Agent D (Fraud Agent):** 4-layer fraud detection (deterministic rules, Isolation Forest anomaly detection, supervised gradient boosting with SHAP explanations, and provider network graphs).
- [x] **Agent E (Settlement Agent):** Decision execution, simulated UPI/NEFT payments with idempotency keys, and immutable audit log entry generation.

### Phase 3: Orchestrator & SLA Engine (Completed ✅)
- [x] Async state machine coordinating parallel execution of Coding Validator and Policy Agent.
- [x] Per-stage latency budgets ensuring execution completes well under the 15-minute (<900s) SLA deadline.

### Phase 4: Decision Policy & Human Review (Completed ✅)
- [x] Configurable risk threshold routing (Auto-settle < 30, Partial settle 30-60, Human Review >= 60, SIU >= 85).
- [x] Evidence pack generation for human adjudicators.

### Phase 5: Frontend Dashboard (Completed ✅)
- [x] Live claims board with real-time SSE updates and scenario selector.
- [x] Split-screen claim inspection view (bill vs. EHR evidence with highlighted mismatches).
- [x] Fraud analytics and hospital SLA countdown timer.

### Phase 6: Google Cloud Healthcare API & 9 Real Policies RAG (Completed ✅)
- [x] Ingested 9 official policy PDFs (448 pages) in `data/policies/` (Star Health, HDFC ERGO, Care Health, Niva Bupa, New India Assurance, Aditya Birla, ICICI Lombard, Bajaj Allianz, Tata AIG).
- [x] Generated 768-dim dense vector embeddings stored in `data/reference/policy_rag_clauses.json`.
- [x] Direct Google Cloud Healthcare API FHIR R4 Store adapter for authentic ABDM / NHCX ClaimBundle ingestion.
- [x] Live Google Cloud status check (`GET /api/v1/gcp/fhir/status`).

### Phase 7: Hospital Automated Appeal & Evidence Engine (Completed ✅)
- [x] GIPSA / IRDAI denial-to-evidence checklist matrix (`data/reference/denial_evidence_matrix.json`).
- [x] `HospitalAppealAgent` automatically gathers clinical evidence, builds NHCX FHIR Appeal Bundle, and drafts formal appeal letters.
- [x] Interactive UI tab with 1-click evidence generation and re-submission.
- [x] Full test suite (38 of 38 unit & integration tests passing).
