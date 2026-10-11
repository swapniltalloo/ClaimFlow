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
