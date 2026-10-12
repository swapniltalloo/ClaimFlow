import os
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_PDF = os.path.join(BASE_DIR, "data", "sample_bills", "apollo_clean_hospital_bill.pdf")


@pytest.mark.asyncio
async def test_sample_pdf_download_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/claims/sample-pdf/apollo")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 1000


@pytest.mark.asyncio
async def test_upload_and_adjudicate_pdf_bill():
    assert os.path.exists(SAMPLE_PDF), "Sample PDF bill must exist"

    with open(SAMPLE_PDF, "rb") as f:
        file_content = f.read()

    files = {
        "file": ("apollo_clean_hospital_bill.pdf", file_content, "application/pdf")
    }
    data = {
        "policy_id": "POL-STAR-ASSURE-001",
        "policy_tenure_days": "180"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/claims/upload-pdf", files=files, data=data)
        assert response.status_code == 200
        res = response.json()

        assert "claim_id" in res
        assert res["claim_id"].startswith("CLM-PDF-")
        assert res["outcome"] in ["AUTO_SETTLE", "PARTIAL_SETTLE", "HUMAN_REVIEW"]
        assert "pdf_metadata" in res
        assert res["pdf_metadata"]["patient_name"] == "Priya Sharma"
        assert "apollo" in res["pdf_metadata"]["hospital_name"].lower()
        assert res["approved_amount"] > 0
        assert len(res["line_items"]) >= 3
