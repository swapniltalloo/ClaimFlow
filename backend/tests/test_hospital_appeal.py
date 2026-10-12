import pytest
from app.agents.hospital_appeal_agent import HospitalAppealAgent
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_real_policies_catalog_and_rag_clauses():
    """Verifies that all 9 real policy PDFs are indexed with clauses and coverage limits."""
    agent = HospitalAppealAgent()
    assert len(agent.policy_catalog) >= 9, f"Expected 9 real policies, found {len(agent.policy_catalog)}"
    
    # Check that Star Health, HDFC ERGO, Care, etc. exist
    insurers = [p["insurer"] for p in agent.policy_catalog]
    assert any("Star Health" in ins for ins in insurers)
    assert any("HDFC ERGO" in ins for ins in insurers)
    assert any("Care Health" in ins for ins in insurers)
    assert any("New India" in ins for ins in insurers)


def test_denial_evidence_matrix_standards():
    """Verifies that GIPSA/IRDAI evidence matrix covers all standard clinical denial reasons."""
    agent = HospitalAppealAgent()
    assert len(agent.evidence_matrix) >= 5
    
    categories = [m["category"] for m in agent.evidence_matrix]
    assert "IMPLANT_VERIFICATION" in categories
    assert "PATHOLOGY_VERIFICATION" in categories
    assert "MEDICAL_NECESSITY" in categories
    assert "UNBUNDLING_DISPUTE" in categories
    assert "WAITING_PERIOD_DISPUTE" in categories


def test_hospital_appeal_agent_evidence_gathering_and_nhcx_bundle():
    """Verifies that HospitalAppealAgent identifies adverse adjudication, gathers matching
    clinical evidence, and constructs a compliant NHCX FHIR appeal bundle.
    """
    agent = HospitalAppealAgent()
    mock_denied_claim = {
        "claim_id": "CLM-TEST-APPEAL-001",
        "patient_id": "PAT-9912",
        "patient_name": "Ramesh Gupta",
        "hospital_name": "Apollo Super Specialty Hospital",
        "policy_id": "POL-STAR-ASSURE-001",
        "total_claimed_amount": 75000.0,
        "approved_amount": 45000.0,
        "line_items": [
            {
                "line_number": 1,
                "code": "CPT-44970",
                "description": "Laparoscopic appendectomy",
                "total_amount": 45000.0,
                "approved_amount": 45000.0,
                "verdict": "OK"
            },
            {
                "line_number": 2,
                "code": "CPT-49080",
                "description": "Peritoneal lavage (Unbundled)",
                "total_amount": 15000.0,
                "approved_amount": 0.0,
                "verdict": "MISMATCH",
                "verdict_reasons": ["Rule CR-003: Unbundling detected."]
            },
            {
                "line_number": 3,
                "code": "CONS-IMPLANT-KIT",
                "description": "Laparoscopic Trocar Implant Pack",
                "total_amount": 15000.0,
                "approved_amount": 0.0,
                "verdict": "UNSUPPORTED",
                "verdict_reasons": ["Rule CR-005: Implant documentation missing."]
            }
        ],
        "risk_reasons": ["FR-002 Unbundling", "Missing implant invoice"]
    }

    result = agent.analyze_denials_and_gather_evidence(mock_denied_claim)

    assert result["appeal_status"] == "SUBMITTED_AND_APPROVED"
    assert len(result["gathered_documents"]) >= 3
    assert result["new_approved_amount"] > result["original_approved"]
    assert "NHCX-APPEAL-BUNDLE" in result["bundle_id"]

    # Verify NHCX FHIR Bundle structure
    fhir_bundle = result["fhir_appeal_bundle"]
    assert fhir_bundle["resourceType"] == "Bundle"
    assert any(e["resource"]["resourceType"] == "Communication" for e in fhir_bundle["entry"])
    assert any(e["resource"]["resourceType"] == "DocumentReference" for e in fhir_bundle["entry"])

    # Verify Appeal Letter contains insurer name
    assert "Star Health" in result["appeal_letter"]


def test_api_hospital_auto_appeal_endpoint():
    """Tests the FastAPI /api/v1/hospital/claims/{claim_id}/auto-appeal endpoint."""
    response = client.post("/api/v1/hospital/claims/CLM-2026-00102/auto-appeal", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["appeal_status"] == "SUBMITTED_AND_APPROVED"
    assert data["new_approved_amount"] > 54000.0
    assert len(data["gathered_documents"]) >= 1
