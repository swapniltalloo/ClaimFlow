# Workflow: /run-sim

Executes an end-to-end simulation of hospital discharge claims against the ClaimFlow clearinghouse engine.

## Steps
1. Verify Docker infrastructure (`infra/docker-compose.yml`) or local service status.
2. Ensure database contains reference tariffs and policy rules (`python scripts/seed.py`).
3. Run discharge simulator (`python scripts/simulate_discharge.py --count 50`).
4. Generate latency and SLA adherence benchmark report (`python scripts/benchmark.py`).
