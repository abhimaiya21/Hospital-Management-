"""
Pydantic schemas for Triage API
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum

class SeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class StatusEnum(str, Enum):
    ASSIGNED = "ASSIGNED"
    REFER = "REFER"

class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=10, description="Patient symptoms in any language")
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age")
    gender: Optional[str] = Field(None, pattern=r"^(M|F|Male|Female|Other|male|female|other)$")
    patient_id: Optional[str] = Field(None, description="Optional patient identifier")
    
    @validator('symptoms')
    def validate_symptoms(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError('Symptoms too short')
        return v.strip()

class Explainability(BaseModel):
    key_keywords: List[str]
    explanation_en: str
    explanation_kn: str
    explanation_hi: str

class TriageResponse(BaseModel):
    medical_category: str
    severity: SeverityEnum
    assigned_doctor: Optional[str]
    room_allotted: Optional[str]
    status: StatusEnum
    explainability: Explainability

    class Config:
        extra = "forbid"

class BatchTriageRequest(BaseModel):
    cases: List[TriageRequest]