# ClaimFlow Phased Implementation Roadmap

## Overview
ClaimFlow is an AI clearinghouse designed to parse EHR data in real time, validate hospital bills against policy rules and procedural tariffs, flag suspicious billing patterns, and settle legitimate claims within 15 minutes of discharge.

---

## Phase Breakdown

### Phase 0: Foundations (Completed)
- [x] Repository scaffolding with standard directory layout.
- [x] Antigravity IDE global rules (`.agent/rules/project.md`) and workflows.
- [x] Docker Compose definition (`infra/docker-compose.yml`) with PostgreSQL 16 (`pgvector`), Redis 7, and FastAPI.
- [x] Environment configuration management with fallback capabilities.
- [x] Pydantic v2 domain schemas aligned to FHIR R4 and ClaimFlow clearinghouse standards.
- [x] Core FastAPI app structure and health check endpoints.

### Phase 1: Synthetic Data Engine (In Progress)
- [x] Reference medical coding datasets (ICD-10, tariffs, unbundling matrix).
- [x] Insurance policy models (Silver Care, Gold Comprehensive, Corporate Floater).
- [x] Clinical discharge summary generation engine (unstructured EHR text).
- [x] Injected fraud generator covering 8 distinct patterns with ground truth labels.
- [ ] Export `data/synthetic/claims.parquet` with 2,000 cases.
- [ ] Automated validation and distribution audit (`scripts/verify_dataset.py`).

### Phase 2: Core Agents (Upcoming)
- **Agent A (EHR Parser):** Extraction of clinical facts, ICD-10 codes, procedure timestamps, and ICU days from unstructured discharge summaries with confidence scoring.
- **Agent B (Coding Validator):** Deterministic verification against diagnosis-procedure compatibility matrix, unbundling tables, and line-item validity.
- **Agent C (Policy Agent):** Vector RAG on policy clauses with pgvector, rule-driven deductible/copay calculations, and clause citation.
- **Agent D (Fraud Agent):** 4-layer fraud detection (deterministic rules, Isolation Forest anomaly detection, supervised gradient boosting with SHAP explanations, and provider network graphs).
- **Agent E (Settlement Agent):** Decision execution, simulated UPI/NEFT payments with idempotency keys, and immutable audit log entry generation.

### Phase 3: Orchestrator & SLA Engine
- LangGraph state machine coordinating parallel execution of Coding Validator and Policy Agent.
- Per-stage latency budgets and automated fallback to human review on failure or SLA breach.

### Phase 4: Decision Policy & Human-in-the-Loop Review
- Configurable risk threshold routing (Auto-settle < 30, Partial settle 30-60, Human Review >= 60, SIU >= 85).
- Evidence pack generation for human adjudicators.

### Phase 5: Frontend Dashboard
- Live claims board with real-time SSE / WebSocket updates.
- Split-screen claim inspection view (bill vs. EHR evidence with highlighted mismatches).
- Fraud analytics and hospital SLA countdown timer.

### Phase 6 & 7: Testing, Evaluation & Demo Packaging
- Benchmark latency suite (`scripts/benchmark.py`).
- Precision / recall evaluation per fraud pattern (`docs/FRAUD_EVAL.md`).
- Antigravity browser agent automated walkthrough of the 3 key demo flows.
