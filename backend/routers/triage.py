"""
FastAPI routes for Triage System with Database Persistence
"""
from fastapi import APIRouter
from typing import List, Dict, Any
from backend.core.triage_engine import MedicalTriageEngine
from backend.db import execute_query
from backend.schemas.triage import (
    TriageRequest, TriageResponse, BatchTriageRequest,
    Explainability, SeverityEnum, StatusEnum
)

router = APIRouter(prefix="/triage", tags=["Medical Triage"])

# Initialize engine (singleton)
engine = MedicalTriageEngine.get_instance()

def _fallback_response() -> TriageResponse:
    return TriageResponse(
        medical_category="REFER",
        severity=SeverityEnum.LOW,
        assigned_doctor="None",
        room_allotted="None",
        status=StatusEnum.REFER,
        explainability=Explainability(
            key_keywords=[],
            explanation_en="Specialized care not available in current hospital.",
            explanation_kn="ಸ್ಥಿತಿಗಾಗಿ ಪ್ರಸ್ತುತ ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲದ ವಿಶೇಷ ವಿಭಾಗದ ಅಗತ್ಯವಿದೆ.",
            explanation_hi="इस स्थिति के लिए वर्तमान अस्पताल में उपलब्ध नहीं विशेष विभाग की आवश्यकता है।"
        )
    )

def _save_triage_result(result: dict, request: TriageRequest) -> int:
    """
    Save triage analysis result to database
    Returns: triage_id
    ✅ NEW: Persists triage analysis to database
    """
    try:
        # Escape strings for SQL safety
        symptoms = request.symptoms.replace("'", "''")
        exp_en = result['explainability']['explanation_en'].replace("'", "''")
        exp_kn = result['explainability']['explanation_kn'].replace("'", "''")
        exp_hi = result['explainability']['explanation_hi'].replace("'", "''")
        
        insert_query = f"""
        INSERT INTO triage_results (
            symptoms,
            patient_age,
            patient_gender,
            medical_category,
            severity,
            assigned_doctor,
            room_allotted,
            triage_status,
            explanation_en,
            explanation_kn,
            explanation_hi,
            detected_language,
            confidence_score,
            model_version,
            analysis_timestamp
        ) VALUES (
            '{symptoms}',
            {request.age if request.age else 'NULL'},
            {'NULL' if not request.gender else f"'{request.gender}'"},
            '{result['medical_category'].replace("'", "''")}',
            '{result['severity']}',
            '{result['assigned_doctor'].replace("'", "''")}',
            '{result['room_allotted'].replace("'", "''")}',
            '{result['status']}',
            '{exp_en}',
            '{exp_kn}',
            '{exp_hi}',
            '{result['metadata']['detected_language']}',
            {result['metadata']['confidence']},
            '1.0',
            CURRENT_TIMESTAMP
        )
        RETURNING triage_id;
        """
        
        result_data = execute_query(insert_query)
        if result_data and len(result_data) > 0 and 'triage_id' in result_data[0]:
            return result_data[0].get('triage_id')
        return None
    except Exception as e:
        print(f"❌ Error saving triage result: {e}")
        return None

@router.post("/analyze", response_model=TriageResponse)
async def analyze_symptoms(request: TriageRequest) -> TriageResponse:
    """
    Analyze patient symptoms and provide triage recommendations
    Supports English, Kannada (ಕನ್ನಡ), and Hindi (हिन्दी)
    
    ✅ NEW: Results now saved to database
    """
    try:
        result = engine.analyze(
            symptoms=request.symptoms,
            age=request.age,
            gender=request.gender
        )

        # ✅ SAVE TO DATABASE (NEW)
        triage_id = _save_triage_result(result, request)
        if triage_id:
            print(f"✅ Triage result saved with ID: {triage_id}")
        else:
            print("⚠️ Triage result could not be saved to database")

        # Map to response model
        return TriageResponse(
            medical_category=result['medical_category'],
            severity=SeverityEnum(result['severity']),
            assigned_doctor=result['assigned_doctor'],
            room_allotted=result['room_allotted'],
            status=StatusEnum(result['status']),
            explainability=Explainability(**result['explainability'])
        )

    except Exception as e:
        print(f"❌ Triage analysis error: {e}")
        return _fallback_response()

@router.post("/batch", response_model=List[TriageResponse])
async def batch_analyze(request: BatchTriageRequest) -> List[TriageResponse]:
    """Analyze multiple patients at once and save all to database"""
    try:
        results: List[TriageResponse] = []
        for case in request.cases:
            result = engine.analyze(
                symptoms=case.symptoms,
                age=case.age,
                gender=case.gender
            )
            
            # ✅ SAVE EACH BATCH RESULT (NEW)
            triage_id = _save_triage_result(result, case)
            if triage_id:
                print(f"✅ Batch triage saved: ID {triage_id}")
            
            results.append(TriageResponse(
                medical_category=result['medical_category'],
                severity=SeverityEnum(result['severity']),
                assigned_doctor=result['assigned_doctor'],
                room_allotted=result['room_allotted'],
                status=StatusEnum(result['status']),
                explainability=Explainability(**result['explainability'])
            ))
        return results
    except Exception as e:
        print(f"❌ Batch analysis error: {e}")
        return [_fallback_response() for _ in request.cases]

@router.get("/departments")
async def get_available_departments() -> Dict[str, Any]:
    """Get list of available departments with translations"""
    depts = {
        "Cardiology": {"en": "Cardiology", "kn": "ಹೃದಯರೋಗ ವಿಭಾಗ", "hi": "हृदय रोग विभाग"},
        "Gastroenterology": {"en": "Gastroenterology", "kn": "ಜೀರ್ಣಾಂಗ ರೋಗ ವಿಭಾಗ", "hi": "गैस्ट्रोएंटरोलॉजी विभाग"},
        "ENT": {"en": "ENT", "kn": "ಕಿವಿ-ಮೂಗು-ಗಂಟಲು ವಿಭಾಗ", "hi": "कान-नाक-गला विभाग"},
        "Gynecology": {"en": "Gynecology", "kn": "ಪ್ರಸೂತಿ ಮತ್ತು ಸ್ತ್ರೀರೋಗ ವಿಭಾಗ", "hi": "प्रसूति एवं स्त्री रोग विभाग"},
        "General Medicine": {"en": "General Medicine", "kn": "ಸಾಮಾನ್ಯ ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "सामान्य चिकित्सा विभाग"},
        "Neurology": {"en": "Neurology", "kn": "ನರವಿಜ್ಞಾನ ವಿಭಾಗ", "hi": "न्यूरोलॉजी विभाग"},
        "Pediatrics": {"en": "Pediatrics", "kn": "ಮಕ್ಕಳ ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "बाल रोग विभाग"},
        "Dermatology": {"en": "Dermatology", "kn": "ಚರ್ಮರೋಗ ವಿಭಾಗ", "hi": "त्वचा रोग विभाग"},
        "Emergency Medicine": {"en": "Emergency Medicine", "kn": "ತುರ್ತು ವೈದ್ಯಕೀಯ ವಿಭಾಗ", "hi": "आपातकालीन चिकित्सा विभाग"},
        "Orthopedics": {"en": "Orthopedics", "kn": "ಅಸ್ಥಿ ಮತ್ತು ಸಂಧಿ ರೋಗ ವಿಭಾಗ", "hi": "अस्थि एवं जोड़ रोग विभाग"}
    }
    return {"available_departments": depts, "total": len(depts)}

@router.get("/history/{patient_id}")
async def get_triage_history(patient_id: int) -> Dict[str, Any]:
    """Get all triage analyses for a specific patient ✅ NEW"""
    try:
        query = f"""
        SELECT 
            triage_id,
            symptoms,
            medical_category,
            severity,
            assigned_doctor,
            room_allotted,
            triage_status,
            explanation_en,
            explanation_kn,
            explanation_hi,
            confidence_score,
            analysis_timestamp
        FROM triage_results
        WHERE patient_id = {patient_id}
        ORDER BY analysis_timestamp DESC
        LIMIT 50;
        """
        results = execute_query(query)
        return {"patient_id": patient_id, "history": results, "total": len(results) if isinstance(results, list) else 0}
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return {"patient_id": patient_id, "history": [], "error": str(e)}


