import pytest
import json
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.adapters.gcp_healthcare import GCPHealthcareFHIRAdapter
from app.services.gemini_service import GeminiService
from app.services.gcp_embeddings import GCPEmbeddingsService


@pytest.fixture
def sample_nhcx_bundle():
    adapter = GCPHealthcareFHIRAdapter()
    return adapter.fetch_bundle("default")


def test_gcp_healthcare_adapter_transformation(sample_nhcx_bundle):
    adapter = GCPHealthcareFHIRAdapter()
    claim, summary, metadata = adapter.transform_nhcx_bundle(sample_nhcx_bundle)

    assert claim.claim_id == "NHCX-2026-99120"
    assert metadata["abha_id"] == "91-8844-2211-7700"
    assert metadata["uhid"] == "UHID-99214432"
    assert metadata["patient_name"] == "Rajesh Kumar"
    assert metadata["hospital_name"] == "Apollo Super Specialty Hospital"
    assert len(claim.line_items) == 3
    assert "Acute appendicitis" in summary


@pytest.mark.asyncio
async def test_gcp_healthcare_api_ingest_endpoint(sample_nhcx_bundle):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Ingest raw ABDM / NHCX FHIR Bundle
        response = await client.post("/api/v1/gcp/fhir/ingest-bundle", json=sample_nhcx_bundle)
        assert response.status_code == 200
        data = response.json()

        assert data["claim_id"] == "NHCX-2026-99120"
        assert data["outcome"] in ["AUTO_SETTLE", "PARTIAL_SETTLE"]
        assert "fhir_claim_response" in data
        assert data["fhir_claim_response"]["resourceType"] == "ClaimResponse"
        assert data["fhir_claim_response"]["outcome"] == "complete"
        assert data["gcp_metadata"]["abha_id"] == "91-8844-2211-7700"


def test_gemini_service_availability_and_fallback(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.GEMINI_API_KEY", "")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    gemini = GeminiService()
    gemini.client = None
    assert gemini.is_available() is False

    from app.models.domain import Claim, Decision, DecisionOutcome
    from datetime import datetime, timezone
    dummy_claim = Claim(
        claim_id="CLM-001",
        patient_id="PAT-001",
        hospital_id="HOSP-001",
        policy_id="POL-001",
        admission_time=datetime.now(timezone.utc),
        discharge_time=datetime.now(timezone.utc),
        total_claimed_amount=50000.0,
        line_items=[]
    )
    dummy_decision = Decision(
        decision_id="DEC-001",
        claim_id="CLM-001",
        outcome=DecisionOutcome.AUTO_SETTLE,
        approved_amount=50000.0,
        deductions_amount=0.0,
        audit_hash="test-hash"
    )

    msg = gemini.generate_patient_explanation(dummy_claim, dummy_decision)
    assert "CLM-001" in msg
    assert "AUTO_SETTLE" in msg


def test_gcp_vertex_embeddings_768_dimensions():
    embedder = GCPEmbeddingsService(api_key=None)
    vec1 = embedder.embed_text("Laparoscopic appendectomy surgical procedure")
    vec2 = embedder.embed_text("Appendix surgical package and operative room")
    vec3 = embedder.embed_text("Luxury room television amenities")

    assert vec1.shape == (768,)
    assert vec2.shape == (768,)
    assert vec3.shape == (768,)

    sim_related = embedder.cosine_similarity(vec1, vec2)
    sim_unrelated = embedder.cosine_similarity(vec1, vec3)
    assert -1.0 <= sim_related <= 1.0
