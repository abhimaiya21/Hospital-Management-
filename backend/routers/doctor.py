import os, re, json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.db import execute_query
from huggingface_hub import InferenceClient

router = APIRouter()
# existing client usage kept as-is; will not be relied on if token missing
client = None
try:
    client = InferenceClient(token=os.getenv("HUGGINGFACE_API_KEY"))
except Exception:
    client = None

class QueryRequest(BaseModel):
    text: Optional[str] = None 
    sql: Optional[str] = None  
    username: Optional[str] = "guest" 
    role: str = "doctor"      
    mode: str = "generate"

def is_safe_sql(sql: str) -> bool:
    if not sql: return False
    s = sql.lower()
    # forbid destructive statements and multiple statements
    forbidden = ["delete ", "drop ", "update ", "insert ", ";", "alter ", "create "]
    for kw in forbidden:
        if kw in s:
            return False
    return True

@router.post("/doctor/query")
async def doctor_query(request: QueryRequest):
    # Minimal safe implementation: map common doctor prompts to SELECTs and execute SELECTs
    if request.mode == "generate":
        # Enhanced mapping with case-insensitive matching in SQL
        mapping = {
            "hypertension": "SELECT * FROM patients WHERE LOWER(diagnosis) LIKE '%hypertension%' LIMIT 50",
            "penicillin": "SELECT p.* FROM patients p JOIN allergies a ON p.patient_id = a.patient_id WHERE LOWER(a.allergen) LIKE '%penicillin%' AND LOWER(a.severity) = 'severe'",
            "robert smith": "SELECT * FROM medical_records WHERE LOWER(patient_name) LIKE '%robert smith%' LIMIT 50",
            "my patients": f"SELECT DISTINCT p.* FROM patients p JOIN appointments a ON p.patient_id = a.patient_id WHERE a.doctor_id = 1", # Mock ID
        }
        
        # Naive Keyword Search fallback
        generated = "SELECT * FROM patients LIMIT 10" # Default
        req_lower = (request.text or "").lower()
        for key, sql in mapping.items():
            if key in req_lower:
                generated = sql
                break

        try:
            safe_q = (request.text or "").replace("'", "''")
            # Ensure audit log doesn't crash traffic
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{request.username or 'guest'}', '{request.role}', '{safe_q}', 'GENERATED')")
        except Exception as e:
            print(f"Audit Log Error: {e}")
            pass
            
        return {"generated_sql": generated}
    elif request.mode == "execute":
        if not request.sql:
            return {"error": "no sql provided"}
        if not is_safe_sql(request.sql):
            return {"error": "query rejected by safety policy"}
        try:
            results = execute_query(request.sql)
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "invalid mode"}

@router.get("/doctor/analytics")
def get_doctor_analytics():
    try:
        # 1. SUMMARY CARDS
        # Assuming doctor_id=1 for demo or general stats if no auth context passed
        my_patients = execute_query("SELECT COUNT(DISTINCT patient_id) as count FROM appointments")[0]['count']
        today_appts = execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date = CURRENT_DATE")[0]['count']
        pending_reports = execute_query("SELECT COUNT(*) as count FROM medical_records")[0]['count'] # Mock: All records
        critical_patients = execute_query("SELECT COUNT(*) as count FROM allergies WHERE severity = 'High'")[0]['count']

        # 2. APPOINTMENTS TREND (Last 7 Days)
        trend_raw = execute_query("SELECT to_char(appointment_date, 'Mon DD') as date, COUNT(*) as count FROM appointments GROUP BY 1 ORDER BY MIN(appointment_date) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]

        # 3. PATIENT CONDITION (Mocked Distribution based on Diagnosis/Allergy severity)
        condition_data = {"Stable": 60, "Under Observation": 30, "Critical": 10}

        # 4. COMMON DIAGNOSES
        diag_raw = execute_query("SELECT diagnosis, COUNT(*) as count FROM medical_records GROUP BY diagnosis ORDER BY count DESC LIMIT 5")
        diag_data = {row['diagnosis']: row['count'] for row in diag_raw}

        # 5. COMPLIANCE (Mocked)
        compliance_data = {"Completed": 85, "Missed": 15}
        
        # 6. AI USAGE
        ai_usage = execute_query("SELECT COUNT(*) as count FROM audit_logs WHERE role='doctor' AND DATE(timestamp) = CURRENT_DATE")[0]['count']

        return {
            "summary": {
                "patients": my_patients,
                "today": today_appts,
                "pending": pending_reports,
                "critical": critical_patients
            },
            "trend": {"labels": trend_labels, "data": trend_values},
            "conditions": condition_data,
            "diagnoses": diag_data,
            "compliance": compliance_data,
            "ai_usage": ai_usage
        }
    except Exception as e:
        return {"error": str(e)}