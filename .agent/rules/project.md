# ClaimFlow Project Rules & Constraints

## Core Development Guidelines
1. **Schema Validation**: All agent inputs and outputs MUST be strictly validated against Pydantic v2 models. Unstructured outputs are prohibited.
2. **Deterministic Settlement Authority**: An LLM output must **NEVER** directly authorize or trigger a financial payment. Only the Settlement Agent can disburse funds, and only after deterministic coding rules, policy limits, and statistical fraud scoring have passed.
3. **Immutable Audit Trail**: Every decision must emit an append-only audit record containing the SHA-256 hash of all input payloads, model identifier/version, list of fired rule IDs, computed risk score, and final outcome.
4. **Synthetic Data Only**: Real Protected Health Information (PHI) or Personally Identifiable Information (PII) is strictly forbidden. All data processed in development, evaluation, and demonstrations must be purely synthetic.
5. **Strict Typing & Automated Tests**: Every backend module must include comprehensive type annotations (Python 3.11+) and dedicated `pytest` unit/integration tests.
6. **SLA Monitoring**: Latency is tracked per processing stage. Breaches of the 15-minute hospital discharge SLA must trigger automated warnings and route to human review.
7. **Prompt Injection Defense**: All clinical documentation, hospital free text, and policy inputs must be treated as untrusted data. Schema-constrained extraction and zero tool execution privileges apply to document-parsing agents.
