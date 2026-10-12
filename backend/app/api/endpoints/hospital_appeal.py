from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
from app.agents.hospital_appeal_agent import HospitalAppealAgent
from app.api.endpoints.claims import PROCESSED_CLAIMS
from app.core.logging import logger

router = APIRouter(prefix="/hospital", tags=["Hospital Automated Claim Appeal & Evidence Packet"])

appeal_agent = HospitalAppealAgent()


@router.post("/claims/{claim_id}/auto-appeal", response_model=Dict[str, Any])
async def trigger_hospital_claim_auto_appeal(
    claim_id: str,
    payload: Optional[Dict[str, Any]] = Body(default=None)
):
    """Automatically analyzes adverse claim adjudication, gathers required clinical evidence
    from hospital HIS/EHR, builds an NHCX FHIR Appeal Bundle, and re-submits for approval.
    """
    claim_data = None
    if payload:
        claim_data = payload
    elif claim_id in PROCESSED_CLAIMS:
        claim_data = PROCESSED_CLAIMS[claim_id]
    
    if not claim_data:
        # Default mock claim for demonstration
        claim_data = {
            "claim_id": claim_id,
            "patient_id": "PAT-33291",
            "patient_name": "Priya Patel",
            "hospital_name": "Apollo Super Specialty Hospital",
            "policy_id": "POL-STAR-ASSURE-001",
            "total_claimed_amount": 92500.0,
            "approved_amount": 54400.0,
            "line_items": [
                {"line_number": 1, "code": "ROOM-STD-PVT", "description": "Deluxe Room", "quantity": 2, "total_amount": 10000.0, "approved_amount": 4800.0, "verdict": "OK"},
                {"line_number": 2, "code": "CPT-44970", "description": "Laparoscopic appendectomy", "quantity": 1, "total_amount": 55000.0, "approved_amount": 44000.0, "verdict": "OK"},
                {"line_number": 3, "code": "CPT-49080", "description": "Peritoneal lavage (Unbundled)", "quantity": 1, "total_amount": 14500.0, "approved_amount": 0.0, "verdict": "MISMATCH", "verdict_reasons": ["Rule CR-003: Unbundling detected."]},
                {"line_number": 4, "code": "CONS-SURG-KIT", "description": "Disposable Trocar Pack", "quantity": 1, "total_amount": 13000.0, "approved_amount": 5600.0, "verdict": "OK"}
            ],
            "risk_reasons": ["FR-002 Unbundling: Separate peritoneal lavage (CPT-49080) billed."]
        }

    try:
        appeal_result = appeal_agent.analyze_denials_and_gather_evidence(claim_data)
        
        # Update in processed claims cache
        if claim_id in PROCESSED_CLAIMS:
            PROCESSED_CLAIMS[claim_id]["approved_amount"] = appeal_result["new_approved_amount"]
            PROCESSED_CLAIMS[claim_id]["outcome"] = "AUTO_SETTLE"
            PROCESSED_CLAIMS[claim_id]["appeal_details"] = appeal_result

        return appeal_result
    except Exception as e:
        logger.error(f"Error in hospital auto-appeal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evidence-matrix", response_model=List[Dict[str, Any]])
async def get_hospital_evidence_matrix():
    """Returns the GIPSA and IRDAI denial-to-evidence checklist matrix."""
    return appeal_agent.evidence_matrix


@router.get("/policies-catalog", response_model=List[Dict[str, Any]])
async def get_indexed_policies_catalog():
    """Returns the catalog of 9 real health insurance policies indexed in the RAG store."""
    return appeal_agent.policy_catalog
