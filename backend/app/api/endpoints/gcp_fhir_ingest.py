from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional

from app.adapters.gcp_healthcare import GCPHealthcareFHIRAdapter
from app.orchestrator.pipeline import ClaimFlowOrchestrator
from app.api.endpoints.claims import PROCESSED_CLAIMS
from app.core.logging import logger

router = APIRouter(prefix="/gcp/fhir", tags=["Google Cloud Healthcare API (FHIR R4 / NHCX)"])

fhir_adapter = GCPHealthcareFHIRAdapter()
orchestrator = ClaimFlowOrchestrator()


@router.post("/ingest-bundle", response_model=Dict[str, Any])
async def ingest_nhcx_fhir_bundle(bundle: Dict[str, Any] = Body(...)):
    """Ingests a raw FHIR R4 ClaimBundle conforming to India's ABDM / NHCX standards.
    
    Transforms the bundle from Google Cloud Healthcare API FHIR R4 Store into ClaimFlow
    entities, runs real-time orchestration across all 5 agents, and outputs both the
    clearinghouse decision and a compliant FHIR ClaimResponse resource.
    """
    try:
        claim, discharge_summary, metadata = fhir_adapter.transform_nhcx_bundle(bundle)

        # Run through clearinghouse pipeline
        result = await orchestrator.process_claim(
            claim=claim,
            discharge_text=discharge_summary,
            fhir_bundle=bundle,
            policy_tenure_days=200
        )

        # Build FHIR R4 ClaimResponse
        claim_response = fhir_adapter.generate_nhcx_claim_response(
            claim=claim,
            decision=result.decision,
            transaction=result.transaction
        )

        data = result.to_dict()
        data["gcp_metadata"] = metadata
        data["fhir_claim_response"] = claim_response
        data["claim_details"] = claim.model_dump()

        # Save to real-time claims store
        PROCESSED_CLAIMS[claim.claim_id] = data

        return data
    except Exception as e:
        logger.error(f"Error ingesting ABDM/NHCX bundle: {e}")
        raise HTTPException(status_code=500, detail=f"Google Cloud Healthcare FHIR ingestion failed: {str(e)}")


@router.post("/sync-store/{bundle_id}", response_model=Dict[str, Any])
async def sync_bundle_from_gcp_fhir_store(bundle_id: str):
    """Pulls a FHIR Bundle from the configured Google Cloud Healthcare API FHIR Store
    and triggers automated real-time adjudication.
    """
    try:
        raw_bundle = fhir_adapter.fetch_bundle(bundle_id)
        return await ingest_nhcx_fhir_bundle(bundle=raw_bundle)
    except Exception as e:
        logger.error(f"Error fetching bundle {bundle_id} from GCP FHIR Store: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-nhcx", response_model=Dict[str, Any])
async def get_sample_nhcx_bundle():
    """Returns the reference ABDM / NHCX FHIR R4 Bundle for testing and demonstration."""
    return fhir_adapter.fetch_bundle("default")


@router.get("/status", response_model=Dict[str, Any])
async def get_gcp_cloud_status():
    """Returns the live connectivity status of all 3 Google services."""
    from app.services.gemini_service import GeminiService
    from app.services.gcp_embeddings import GCPEmbeddingsService
    from app.core.config import settings

    gemini_svc = GeminiService()
    emb_svc = GCPEmbeddingsService()

    return {
        "live_cloud_mode": gemini_svc.is_available(),
        "services": {
            "google_gemini": {
                "model": "gemini-2.5-flash",
                "connected_to_cloud": gemini_svc.is_available(),
                "mode": "Live Google Cloud (google-genai)" if gemini_svc.is_available() else "Local Deterministic Clinical NLP"
            },
            "google_vertex_embeddings": {
                "model": "text-embedding-004",
                "dimensions": 768,
                "connected_to_cloud": emb_svc.client is not None,
                "mode": "Live Vertex AI (text-embedding-004)" if emb_svc.client is not None else "Local 768-dim Vector Engine"
            },
            "google_healthcare_api": {
                "specification": "FHIR R4",
                "profiles": ["ABDM ClaimBundle", "NHCX ClaimResponse"],
                "active_store_uri": f"projects/{settings.GCP_PROJECT_ID}/locations/{settings.GCP_LOCATION}/datasets/{settings.GCP_DATASET_ID}/fhirStores/{settings.GCP_FHIR_STORE_ID}",
                "status": "Ready for HIS Ingestion"
            }
        }
    }
