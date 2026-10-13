import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dateutil import parser as dt_parser
from app.models.domain import ClinicalFacts
from app.services.gemini_service import GeminiService
from app.core.logging import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REF_DATA_PATH = os.path.join(BASE_DIR, "data", "reference", "icd10_codes.json")
TARIFFS_PATH = os.path.join(BASE_DIR, "data", "reference", "procedure_tariffs.json")


class EHRParserAgent:
    """Agent A: EHR Parser Agent.
    
    Parses unstructured hospital discharge summaries and FHIR bundles into schema-validated
    ClinicalFacts using Google Gemini 2.5 Flash and verified ICD-10 lookups.
    """

    def __init__(self, icd10_path: Optional[str] = None, tariffs_path: Optional[str] = None):
        self.icd10_path = icd10_path or REF_DATA_PATH
        self.tariffs_path = tariffs_path or TARIFFS_PATH
        self.icd10_catalog = self._load_json(self.icd10_path)
        self.tariffs_catalog = self._load_json(self.tariffs_path)
        self.gemini = GeminiService()

        # Precompute lookup maps
        self.code_to_diag = {d["code"]: d for d in self.icd10_catalog}
        self.code_to_tariff = {t["code"]: t for t in self.tariffs_catalog}

    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def parse(
        self,
        discharge_text: str,
        patient_id: Optional[str] = None,
        fhir_bundle: Optional[Dict[str, Any]] = None
    ) -> ClinicalFacts:
        """Parses clinical narrative into structured ClinicalFacts with schema validation."""
        # Check if Google Gemini API is available for structured extraction
        if self.gemini.is_available():
            gemini_facts = self.gemini.parse_clinical_summary(discharge_text, patient_id or "PAT-UNKNOWN")
            if gemini_facts:
                # Enrich with clinical evidence snippets & medications
                meds, med_snippet = self._extract_medications(discharge_text)
                if meds and not gemini_facts.prescribed_medications:
                    gemini_facts.prescribed_medications = meds
                if med_snippet:
                    gemini_facts.evidence_snippets.setdefault("medications", med_snippet)

                admit_dt, disch_dt, d_snippets, _ = self._extract_dates(discharge_text)
                _, _, stay_snippets, _ = self._extract_stay_duration(discharge_text, admit_dt, disch_dt)
                d_snippets.update(stay_snippets)
                for k, v in d_snippets.items():
                    gemini_facts.evidence_snippets.setdefault(k, v)

                # Validate uncertainties on vague narratives
                has_explicit_dates = "admit_time" in d_snippets or "admission date" in discharge_text.lower()
                has_explicit_icd = any(re.search(r'\b' + re.escape(d["code"]) + r'\b', discharge_text) for d in self.icd10_catalog)
                if not has_explicit_dates:
                    gemini_facts.flagged_uncertainties.append("Missing explicit admission or discharge dates.")
                if not has_explicit_icd:
                    gemini_facts.flagged_uncertainties.append("Diagnosis inferred without explicit ICD-10 notation.")
                if gemini_facts.flagged_uncertainties:
                    gemini_facts.confidence_score = min(gemini_facts.confidence_score, 0.75)

                return gemini_facts

        evidence_snippets: Dict[str, str] = {}
        field_confidences: Dict[str, float] = {}
        flagged_uncertainties: List[str] = []

        # 1. Extract Patient ID if not explicitly provided
        extracted_patient_id = patient_id
        if not extracted_patient_id:
            uhid_match = re.search(r'UHID[:\s]+([A-Z0-9\-]+)', discharge_text, re.IGNORECASE)
            pat_match = re.search(r'PAT[:\s\-]+([A-Z0-9\-]+)', discharge_text, re.IGNORECASE)
            if uhid_match:
                extracted_patient_id = uhid_match.group(1).strip()
            elif pat_match:
                extracted_patient_id = f"PAT-{pat_match.group(1).strip()}"
            else:
                extracted_patient_id = "PAT-UNKNOWN"
                flagged_uncertainties.append("patient_id: not found in narrative")
                field_confidences["patient_id"] = 0.5
        field_confidences.setdefault("patient_id", 1.0)

        # 2. Extract Admission & Discharge Timestamps
        admit_time, disch_time, date_snippets, date_conf = self._extract_dates(discharge_text)
        evidence_snippets.update(date_snippets)
        field_confidences["admit_time"] = date_conf.get("admit_time", 0.5)
        field_confidences["discharge_time"] = date_conf.get("discharge_time", 0.5)
        if date_conf.get("admit_time", 1.0) < 0.7:
            flagged_uncertainties.append("admit_time: low confidence extraction")
        if date_conf.get("discharge_time", 1.0) < 0.7:
            flagged_uncertainties.append("discharge_time: low confidence extraction")

        # 3. Extract Length of Stay & ICU Days
        icu_days, room_days, los_snippets, los_conf = self._extract_stay_duration(discharge_text, admit_time, disch_time)
        evidence_snippets.update(los_snippets)
        field_confidences["icu_stay_days"] = los_conf.get("icu_stay_days", 0.9)
        field_confidences["room_stay_days"] = los_conf.get("room_stay_days", 0.9)

        # 4. Extract & Verify Diagnosis (ICD-10)
        diag_code, diag_name, diag_snippet, diag_conf = self._extract_diagnosis(discharge_text, fhir_bundle)
        if diag_snippet:
            evidence_snippets["primary_diagnosis"] = diag_snippet
        field_confidences["primary_diagnosis_code"] = diag_conf
        if diag_conf < 0.75:
            flagged_uncertainties.append(f"primary_diagnosis: matched with confidence {diag_conf:.2f}")

        # 5. Extract Procedures
        procedure_codes, proc_snippet, proc_conf = self._extract_procedures(discharge_text, fhir_bundle)
        if proc_snippet:
            evidence_snippets["performed_procedures"] = proc_snippet
        field_confidences["performed_procedure_codes"] = proc_conf

        # 6. Extract Medications
        medications, med_snippet = self._extract_medications(discharge_text)
        if med_snippet:
            evidence_snippets["prescribed_medications"] = med_snippet
        field_confidences["prescribed_medications"] = 0.95 if medications else 0.7

        # 7. Aggregate Confidence Score
        confidence_score = sum(field_confidences.values()) / max(len(field_confidences), 1)

        # Build schema-validated ClinicalFacts
        return ClinicalFacts(
            patient_id=extracted_patient_id,
            primary_diagnosis_code=diag_code,
            primary_diagnosis_name=diag_name,
            secondary_diagnoses=[],
            admit_time=admit_time,
            discharge_time=disch_time,
            icu_stay_days=icu_days,
            room_stay_days=room_days,
            performed_procedure_codes=procedure_codes,
            prescribed_medications=medications,
            confidence_score=round(confidence_score, 3),
            field_confidences=field_confidences,
            evidence_snippets=evidence_snippets,
            flagged_uncertainties=flagged_uncertainties
        )

    def _extract_dates(self, text: str) -> Tuple[datetime, datetime, Dict[str, str], Dict[str, float]]:
        snippets = {}
        confidences = {}
        now = datetime.now(timezone.utc)
        default_admit = now
        default_disch = now

        admit_match = re.search(r'ADMISSION DATE[:\s]+([^\n\r]+)', text, re.IGNORECASE)
        if admit_match:
            raw_str = admit_match.group(1).strip()
            snippets["admit_time"] = admit_match.group(0).strip()
            try:
                admit_dt = dt_parser.parse(raw_str)
                if admit_dt.tzinfo is None:
                    admit_dt = admit_dt.replace(tzinfo=timezone.utc)
                default_admit = admit_dt
                confidences["admit_time"] = 0.98
            except Exception:
                confidences["admit_time"] = 0.4
        else:
            confidences["admit_time"] = 0.3

        disch_match = re.search(r'DISCHARGE DATE[:\s]+([^\n\r]+)', text, re.IGNORECASE)
        if disch_match:
            raw_str = disch_match.group(1).strip()
            snippets["discharge_time"] = disch_match.group(0).strip()
            try:
                disch_dt = dt_parser.parse(raw_str)
                if disch_dt.tzinfo is None:
                    disch_dt = disch_dt.replace(tzinfo=timezone.utc)
                default_disch = disch_dt
                confidences["discharge_time"] = 0.98
            except Exception:
                confidences["discharge_time"] = 0.4
        else:
            confidences["discharge_time"] = 0.3

        return default_admit, default_disch, snippets, confidences

    def _extract_stay_duration(self, text: str, admit_dt: datetime, disch_dt: datetime) -> Tuple[int, int, Dict[str, str], Dict[str, float]]:
        snippets = {}
        conf = {}
        icu_days = 0
        room_days = 1

        # Look for structured stay pattern e.g. "LENGTH OF STAY: 4 Days (Room Days: 3, ICU Days: 1)"
        los_match = re.search(r'LENGTH OF STAY[:\s]+([^\n\r]+)', text, re.IGNORECASE)
        if los_match:
            snippets["length_of_stay"] = los_match.group(0).strip()
            raw_line = los_match.group(1)
            icu_search = re.search(r'ICU Days[:\s]+(\d+)', raw_line, re.IGNORECASE)
            room_search = re.search(r'Room Days[:\s]+(\d+)', raw_line, re.IGNORECASE)
            if icu_search:
                icu_days = int(icu_search.group(1))
            if room_search:
                room_days = int(room_search.group(1))
            conf["icu_stay_days"] = 0.98
            conf["room_stay_days"] = 0.98
        else:
            # Fallback to date difference
            delta = (disch_dt - admit_dt).total_seconds() / 86400.0
            room_days = max(1, int(round(delta)))
            conf["room_stay_days"] = 0.8
            conf["icu_stay_days"] = 0.8

            # Scan for explicit ICU mention in text
            icu_mention = re.search(r'ICU for (\d+) days', text, re.IGNORECASE)
            if icu_mention:
                icu_days = int(icu_mention.group(1))
                snippets["icu_mention"] = icu_mention.group(0).strip()
                conf["icu_stay_days"] = 0.95

        return icu_days, room_days, snippets, conf

    def _extract_diagnosis(self, text: str, fhir_bundle: Optional[Dict[str, Any]]) -> Tuple[str, str, str, float]:
        # Check FHIR bundle first if provided
        if fhir_bundle and "entry" in fhir_bundle:
            for entry in fhir_bundle.get("entry", []):
                res = entry.get("resource", {})
                if res.get("resourceType") == "Condition":
                    coding = res.get("code", {}).get("coding", [])
                    if coding:
                        code = coding[0].get("code")
                        display = coding[0].get("display", "Condition from FHIR")
                        if code in self.code_to_diag:
                            return code, self.code_to_diag[code]["name"], f"FHIR Condition Resource: {code} ({display})", 1.0

        # Direct exact code search in text (e.g., K35.80, I21.09)
        for diag in self.icd10_catalog:
            code = diag["code"]
            if re.search(r'\b' + re.escape(code) + r'\b', text):
                snippet = f"Found explicit ICD-10 code reference {code}: {diag['name']}"
                return code, diag["name"], snippet, 0.99

        # Search for key disease diagnostic keywords
        lower_text = text.lower()
        best_match = None
        best_score = 0.0
        best_snippet = ""

        for diag in self.icd10_catalog:
            diag_name = diag["name"].lower()
            # Extract main tokens (excluding stop words)
            tokens = [t for t in re.findall(r'[a-z]{3,}', diag_name) if t not in {"and", "with", "for", "the", "part", "unspecified", "without"}]
            if not tokens:
                continue

            matched_tokens = [t for t in tokens if t in lower_text]
            token_ratio = len(matched_tokens) / len(tokens)

            # Check for clinical matches
            if token_ratio > best_score and token_ratio >= 0.5:
                best_score = token_ratio
                best_match = diag
                # Find matching line for snippet
                for line in text.splitlines():
                    if any(t in line.lower() for t in matched_tokens):
                        best_snippet = line.strip()
                        break

        if best_match and best_score >= 0.5:
            conf = min(0.95, round(best_score * 0.95, 2))
            return best_match["code"], best_match["name"], best_snippet or best_match["name"], conf

        # Fallback unknown
        return "UNKNOWN", "Unspecified Condition", "No conclusive diagnostic match found", 0.3

    def _extract_procedures(self, text: str, fhir_bundle: Optional[Dict[str, Any]]) -> Tuple[List[str], str, float]:
        procs: List[str] = []
        snippets: List[str] = []

        # Exact CPT codes in text
        for tariff in self.tariffs_catalog:
            code = tariff["code"]
            if code.startswith("CPT-"):
                if re.search(r'\b' + re.escape(code) + r'\b', text):
                    procs.append(code)
                    snippets.append(f"Explicit procedure code {code}: {tariff['description']}")

        # Look in "PROCEDURES PERFORMED:" section
        proc_section = re.search(r'PROCEDURES PERFORMED[:\s]+([^\n\r=]+)', text, re.IGNORECASE)
        if proc_section:
            section_text = proc_section.group(1).strip()
            snippets.append(section_text)
            # Match keywords from tariffs
            lower_sec = section_text.lower()
            for tariff in self.tariffs_catalog:
                code = tariff["code"]
                desc = tariff["description"].lower()
                if "appendectomy" in desc and "appendectomy" in lower_sec:
                    if code not in procs and "uncomplicated" in desc:
                        procs.append(code)
                elif "knee" in desc and "knee" in lower_sec:
                    if code not in procs:
                        procs.append(code)
                elif "cataract" in desc and "cataract" in lower_sec:
                    if code not in procs:
                        procs.append(code)
                elif "hernia" in desc and "hernia" in lower_sec:
                    if code not in procs:
                        procs.append(code)

        conf = 0.95 if procs else 0.8
        snippet_text = " | ".join(snippets) if snippets else "No invasive surgical procedure performed."
        return procs, snippet_text, conf

    def _extract_medications(self, text: str) -> Tuple[List[str], str]:
        meds = []
        snippet = ""
        med_section = re.search(r'DISCHARGE MEDICATIONS[:\s]+(.*?)(?=CONDITION AT DISCHARGE|ATTENDING PHYSICIAN|===|$)', text, re.DOTALL | re.IGNORECASE)
        if med_section:
            snippet = med_section.group(0).strip()
            lines = med_section.group(1).strip().splitlines()
            for line in lines:
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', line).strip()
                if cleaned:
                    meds.append(cleaned)
        return meds, snippet
