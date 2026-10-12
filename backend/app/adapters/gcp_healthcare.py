import os
import json
import base64
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dateutil import parser as dt_parser

from app.models.domain import Claim, LineItem, LineItemType, LineItemVerdict, Decision, DecisionOutcome
from app.services.payment import PaymentTransaction
from app.core.config import settings
from app.core.logging import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SAMPLE_NHCX_PATH = os.path.join(BASE_DIR, "data", "reference", "nhcx_abdm_sample_bundle.json")


class GCPHealthcareFHIRAdapter:
    """Google Cloud Healthcare API (FHIR R4 Store) Adapter.
    
    Ingests and transforms National Health Claims Exchange (NHCX) and
    Ayushman Bharat Digital Mission (ABDM) FHIR R4 bundles from Google Cloud
    Healthcare API FHIR stores into ClaimFlow adjudication structures, and writes
    back FHIR ClaimResponse resources.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        dataset_id: Optional[str] = None,
        fhir_store_id: Optional[str] = None
    ):
        self.project_id = project_id or os.environ.get("GCP_PROJECT_ID", "claimflow-hackathon-2026")
        self.location = location or os.environ.get("GCP_LOCATION", "asia-south1")  # Google Cloud India region
        self.dataset_id = dataset_id or os.environ.get("GCP_DATASET_ID", "abdm-nhcx-dataset")
        self.fhir_store_id = fhir_store_id or os.environ.get("GCP_FHIR_STORE_ID", "nhcx-claims-store")

        self.base_url = (
            f"https://healthcare.googleapis.com/v1/projects/{self.project_id}/"
            f"locations/{self.location}/datasets/{self.dataset_id}/"
            f"fhirStores/{self.fhir_store_id}/fhir"
        )

    def transform_nhcx_bundle(self, bundle: Dict[str, Any]) -> Tuple[Claim, str, Dict[str, Any]]:
        """Parses an authentic ABDM / NHCX FHIR R4 Bundle into ClaimFlow domain structures.
        
        Returns:
            Tuple of:
            - Claim object
            - Discharge summary free-text narrative
            - Extracted metadata dictionary (ABHA ID, UHID, hospital name)
        """
        entries = bundle.get("entry", [])
        resources = {}
        for entry in entries:
            res = entry.get("resource", {})
            rtype = res.get("resourceType")
            if rtype:
                resources.setdefault(rtype, []).append(res)

        # 1. Extract Patient (ABHA & UHID)
        patient_res = resources.get("Patient", [{}])[0]
        patient_id = patient_res.get("id", "PAT-ABHA-UNKNOWN")
        patient_name = "Patient"
        if patient_res.get("name"):
            patient_name = patient_res["name"][0].get("text", "Unknown Patient")
        
        abha_id = None
        uhid = None
        for ident in patient_res.get("identifier", []):
            sys_uri = ident.get("system", "")
            if "ndhm.gov.in" in sys_uri or "healthid" in sys_uri:
                abha_id = ident.get("value")
            elif "uhid" in sys_uri:
                uhid = ident.get("value")

        # 2. Extract Encounter
        encounter_res = resources.get("Encounter", [{}])[0]
        hospital_name = "Hospital Provider"
        hospital_id = "HOSP-001"
        admit_time = datetime.now(timezone.utc)
        disch_time = datetime.now(timezone.utc)

        sp = encounter_res.get("serviceProvider", {})
        if sp.get("display"):
            hospital_name = sp["display"]
        if sp.get("reference"):
            hospital_id = sp["reference"].split("/")[-1]

        period = encounter_res.get("period", {})
        if period.get("start"):
            admit_time = dt_parser.parse(period["start"])
            if admit_time.tzinfo is None:
                admit_time = admit_time.replace(tzinfo=timezone.utc)
        if period.get("end"):
            disch_time = dt_parser.parse(period["end"])
            if disch_time.tzinfo is None:
                disch_time = disch_time.replace(tzinfo=timezone.utc)

        # 3. Extract DocumentReference (Discharge Summary)
        discharge_text = ""
        doc_res = resources.get("DocumentReference", [{}])[0]
        for content_item in doc_res.get("content", []):
            att = content_item.get("attachment", {})
            if att.get("data"):
                raw_data = att["data"]
                # Decode if base64, otherwise use direct string
                try:
                    discharge_text = base64.b64decode(raw_data).decode("utf-8")
                except Exception:
                    discharge_text = raw_data
            elif att.get("title") and not discharge_text:
                discharge_text = att.get("title", "")

        if not discharge_text:
            discharge_text = f"EHR Discharge Encounter for {patient_name} (ABHA: {abha_id or 'N/A'}). Admitted on {admit_time.strftime('%Y-%m-%d')} and discharged {disch_time.strftime('%Y-%m-%d')}."

        # 4. Extract NHCX Claim & Line Items
        claim_res = resources.get("Claim", [{}])[0]
        claim_id = claim_res.get("id", f"CLM-NHCX-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        for ident in claim_res.get("identifier", []):
            if "nhcx" in ident.get("system", ""):
                claim_id = ident.get("value", claim_id)

        policy_id = "POL-GOLD-002"
        for ins in claim_res.get("insurance", []):
            cov_ref = ins.get("coverage", {}).get("reference", "")
            if cov_ref:
                policy_id = cov_ref.split("/")[-1]

        line_items: List[LineItem] = []
        raw_items = claim_res.get("item", [])
        total_claimed = 0.0

        for it in raw_items:
            seq = it.get("sequence", len(line_items) + 1)
            code = "PROC-GEN"
            desc = "Healthcare Service"
            itype = LineItemType.PROCEDURE

            codings = it.get("productOrService", {}).get("coding", [])
            if codings:
                code = codings[0].get("code", code)
                desc = codings[0].get("display", desc)

            # Categorize item type
            if "ROOM" in code or "BED" in code:
                itype = LineItemType.ROOM_ICU
            elif "MED" in code or "DRUG" in code:
                itype = LineItemType.MEDICATION
            elif "LAB" in code or "IMG" in code:
                itype = LineItemType.INVESTIGATION
            elif "CONS" in code:
                itype = LineItemType.CONSUMABLE

            qty = float(it.get("quantity", {}).get("value", 1.0))
            unit_price = float(it.get("unitPrice", {}).get("value", 0.0))
            net = float(it.get("net", {}).get("value", qty * unit_price))
            total_claimed += net

            line_items.append(LineItem(
                line_number=seq,
                service_date=admit_time,
                item_type=itype,
                code=code,
                description=desc,
                quantity=qty,
                unit_price=unit_price if unit_price > 0 else net / max(1.0, qty),
                total_amount=net,
                verdict=LineItemVerdict.PENDING
            ))

        claim = Claim(
            claim_id=claim_id,
            patient_id=patient_id,
            hospital_id=hospital_id,
            policy_id=policy_id,
            admission_time=admit_time,
            discharge_time=disch_time,
            total_claimed_amount=round(total_claimed, 2),
            line_items=line_items
        )

        metadata = {
            "source": "Google Cloud Healthcare API (FHIR R4 Store)",
            "profile": "NHCX/ABDM ClaimBundle",
            "abha_id": abha_id,
            "uhid": uhid,
            "patient_name": patient_name,
            "hospital_name": hospital_name,
            "fhir_bundle_id": bundle.get("id")
        }

        return claim, discharge_text, metadata

    def fetch_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """Fetches FHIR Bundle from Google Cloud Healthcare API or local sandbox store."""
        # Check if local sample or file
        if bundle_id in {"NHCX-ABDM-CLAIM-BUNDLE-001", "default", "sample"} or not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            if os.path.exists(SAMPLE_NHCX_PATH):
                with open(SAMPLE_NHCX_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)

        # In production GCP mode with GOOGLE_APPLICATION_CREDENTIALS, use google-auth session:
        try:
            import google.auth
            from google.auth.transport.requests import AuthorizedSession
            credentials, project = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            authed_session = AuthorizedSession(credentials)
            url = f"{self.base_url}/Bundle/{bundle_id}"
            resp = authed_session.get(url)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(f"GCP Healthcare API returned {resp.status_code}. Fallback to sample bundle.")
        except Exception as e:
            logger.info(f"Google Cloud Healthcare API authentication note: {e}. Using ABDM/NHCX reference bundle.")

        with open(SAMPLE_NHCX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_nhcx_claim_response(
        self,
        claim: Claim,
        decision: Decision,
        transaction: Optional[PaymentTransaction] = None
    ) -> Dict[str, Any]:
        """Builds a compliant FHIR R4 ClaimResponse resource for Google Cloud Healthcare API."""
        return {
            "resourceType": "ClaimResponse",
            "id": f"RESP-{decision.decision_id}",
            "meta": {
                "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/ClaimResponse"]
            },
            "status": "active",
            "type": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/claim-type", "code": "institutional"}]
            },
            "use": "claim",
            "patient": {"reference": f"Patient/{claim.patient_id}"},
            "created": datetime.now(timezone.utc).isoformat(),
            "insurer": {"display": "ClaimFlow Autonomous Clearinghouse"},
            "outcome": "complete" if decision.outcome in {DecisionOutcome.AUTO_SETTLE, DecisionOutcome.PARTIAL_SETTLE} else "queued",
            "disposition": decision.reviewer_notes or f"Claim adjudicated: {decision.outcome.value}",
            "total": [
                {
                    "category": {"coding": [{"code": "submitted"}]},
                    "amount": {"value": claim.total_claimed_amount, "currency": "INR"}
                },
                {
                    "category": {"coding": [{"code": "benefit"}]},
                    "amount": {"value": decision.approved_amount, "currency": "INR"}
                }
            ],
            "payment": {
                "type": {"coding": [{"code": "electronic"}]},
                "amount": {"value": decision.approved_amount, "currency": "INR"},
                "identifier": {"value": transaction.transaction_id if transaction else "NONE"},
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")
            } if transaction else None,
            "adjudication": [
                {
                    "category": {"coding": [{"code": "clause_citation"}]},
                    "reason": {"text": cit}
                } for cit in decision.clause_citations
            ]
        }
