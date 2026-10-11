from datetime import datetime, date
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class FHIRPeriod(BaseModel):
    start: datetime
    end: Optional[datetime] = None


class FHIRCoding(BaseModel):
    system: str = "http://hl7.org/fhir/sid/icd-10"
    code: str
    display: Optional[str] = None


class FHIRCodeableConcept(BaseModel):
    coding: List[FHIRCoding] = Field(default_factory=list)
    text: Optional[str] = None


class FHIRIdentifier(BaseModel):
    system: Optional[str] = None
    value: str


class FHIRPatient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: str
    identifier: List[FHIRIdentifier] = Field(default_factory=list)
    name: str
    gender: Literal["male", "female", "other", "unknown"]
    birthDate: Optional[date] = None


class FHIREncounter(BaseModel):
    resourceType: Literal["Encounter"] = "Encounter"
    id: str
    status: Literal["planned", "in-progress", "onleave", "finished", "cancelled"] = "finished"
    class_: Optional[str] = Field(default="IMP", alias="class")  # Inpatient
    period: FHIRPeriod
    serviceProvider: Optional[str] = None
    reasonCode: List[FHIRCodeableConcept] = Field(default_factory=list)


class FHIRCondition(BaseModel):
    resourceType: Literal["Condition"] = "Condition"
    id: str
    clinicalStatus: str = "active"
    verificationStatus: str = "confirmed"
    code: FHIRCodeableConcept
    subject: str  # Patient reference e.g., Patient/PAT-123
    encounter: Optional[str] = None
    recordedDate: Optional[datetime] = None


class FHIRProcedure(BaseModel):
    resourceType: Literal["Procedure"] = "Procedure"
    id: str
    status: Literal["completed", "in-progress", "not-done"] = "completed"
    code: FHIRCodeableConcept
    subject: str
    performedPeriod: Optional[FHIRPeriod] = None
    performedDateTime: Optional[datetime] = None


class FHIRMedicationRequest(BaseModel):
    resourceType: Literal["MedicationRequest"] = "MedicationRequest"
    id: str
    status: Literal["active", "completed", "cancelled"] = "completed"
    intent: str = "order"
    medicationCodeableConcept: FHIRCodeableConcept
    subject: str
    authoredOn: Optional[datetime] = None


class FHIRBundleEntry(BaseModel):
    fullUrl: Optional[str] = None
    resource: Dict[str, Any]


class FHIRBundle(BaseModel):
    resourceType: Literal["Bundle"] = "Bundle"
    id: str
    type: Literal["collection", "transaction", "batch"] = "collection"
    entry: List[FHIRBundleEntry] = Field(default_factory=list)
