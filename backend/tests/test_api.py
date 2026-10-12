import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ClaimFlow Clearinghouse"
        assert data["sla_target_minutes"] == 15.0


@pytest.mark.asyncio
async def test_readiness_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_claims_discharge_api_flow():
    from datetime import datetime, timezone
    payload = {
        "claim": {
            "claim_id": "CLM-API-TEST-001",
            "patient_id": "PAT-001",
            "hospital_id": "HOSP-001",
            "policy_id": "POL-HDFC-OPTIMA-002",
            "admission_time": datetime.now(timezone.utc).isoformat(),
            "discharge_time": datetime.now(timezone.utc).isoformat(),
            "total_claimed_amount": 55000.0,
            "line_items": [
                {
                    "line_number": 1,
                    "service_date": datetime.now(timezone.utc).isoformat(),
                    "item_type": "PROCEDURE",
                    "code": "CPT-44970",
                    "description": "Laparoscopic appendectomy",
                    "unit_price": 55000.0,
                    "total_amount": 55000.0
                }
            ]
        },
        "discharge_summary": "Patient Aarav Sharma admitted with acute appendicitis K35.80. Underwent CPT-44970 laparoscopic appendectomy. Discharged stable."
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Post discharge event
        post_resp = await client.post("/api/v1/claims/discharge", json=payload)
        assert post_resp.status_code == 200
        post_data = post_resp.json()
        assert post_data["claim_id"] == "CLM-API-TEST-001"
        assert post_data["outcome"] in ["AUTO_SETTLE", "PARTIAL_SETTLE"]

        # 2. List claims
        list_resp = await client.get("/api/v1/claims")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) >= 1

        # 3. Get evidence pack
        ev_resp = await client.get("/api/v1/claims/CLM-API-TEST-001/evidence-pack")
        assert ev_resp.status_code == 200
        assert ev_resp.json()["claim_id"] == "CLM-API-TEST-001"

