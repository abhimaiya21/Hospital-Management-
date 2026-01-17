import os, re, json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.db import execute_query
from huggingface_hub import InferenceClient

router = APIRouter()
# existing client usage kept as-is
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
    # forbid destructive statements
    forbidden = ["delete ", "drop ", "update ", "insert ", ";", "alter ", "create ", "truncate "]
    for kw in forbidden:
        if kw in s:
            return False
    return True

def generate_doctor_recommendations(results: list, query_text: str) -> list:
    recs = []
    if not results: return ["No matching records found."]
    
    # 1. Analyze Diagnosis for Patterns (Schema: medical_records.diagnosis)
    if any('hypertension' in str(r.get('diagnosis', '')).lower() for r in results):
        recs.append("Suggested: Schedule BP monitoring follow-up.")
        recs.append("Review recent lab results for lipid profile.")

    # 2. Analyze Allergies (Schema: allergies.allergen)
    if results and 'allergen' in results[0]:
        val = str(results[0].get('allergen', '')).lower()
        if 'penicillin' in val:
            recs.append("⚠ CRITICAL: Flag patient file for Penicillin Avoidance.")
            recs.append("Suggest alternative antibiotics (e.g., Macrolides).")
            
    # 3. Analyze Lab Results (Schema: lab_tests.results)
    if 'test_name' in results[0] and 'pending' in str(results[0].get('status', '')).lower():
        recs.append("Action: Follow up with Pathology department.")
        
    return recs

@router.post("/doctor/query")
async def doctor_query(request: QueryRequest):
    if request.mode == "generate":
        # Enhanced mapping aligned with 14-table Schema and specific Doctor Policies
        mapping = {
            # --- 1. My Appointments Today ---
            "appointments": """
                SELECT a.appointment_id, TO_CHAR(a.appointment_date, 'HH12:MI AM') as time, 
                       p.first_name, p.last_name, p.gender, 
                       EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.dob)) as age, 
                       a.patient_problem_text, a.status 
                FROM appointments a 
                JOIN patients p ON a.patient_id = p.patient_id 
                WHERE a.doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                  AND DATE(a.appointment_date) = CURRENT_DATE 
                ORDER BY a.appointment_date ASC
            """,

            # --- 2. My Active Inpatients (Admitted) ---
            "inpatients": """
                SELECT adm.admission_id, p.first_name, p.last_name, r.room_number, 
                       adm.admission_date, adm.admission_reason, adm.status 
                FROM admissions adm 
                JOIN patients p ON adm.patient_id = p.patient_id 
                JOIN rooms r ON adm.room_id = r.room_id 
                WHERE adm.primary_doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                  AND adm.status = 'Active' 
                ORDER BY adm.admission_date DESC
            """,
            "admitted": """
                SELECT adm.admission_id, p.first_name, p.last_name, r.room_number, 
                       adm.admission_date, adm.admission_reason, adm.status 
                FROM admissions adm 
                JOIN patients p ON adm.patient_id = p.patient_id 
                JOIN rooms r ON adm.room_id = r.room_id 
                WHERE adm.primary_doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                  AND adm.status = 'Active'
            """,

            # --- 3. Pending Lab Results ---
            "lab": """
                SELECT lt.test_id, p.first_name, p.last_name, lt.test_name, 
                       lt.test_category, lt.ordered_date, lt.status 
                FROM lab_tests lt 
                JOIN patients p ON lt.patient_id = p.patient_id 
                WHERE lt.doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                  AND lt.status IN ('Pending', 'Sample Collected', 'In Progress') 
                ORDER BY lt.ordered_date ASC
            """,

            # --- 4. Total Revenue Generated ---
            "revenue": """
                SELECT COUNT(i.invoice_id) as total_consultations, 
                       SUM(i.consultation_charges) as total_revenue 
                FROM invoices i 
                JOIN appointments a ON i.appointment_id = a.appointment_id 
                WHERE a.doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                  AND a.status = 'Completed'
            """,

            # --- 5. Patient Medical History (Generic Recent) ---
            "history": """
                SELECT p.first_name, p.last_name, m.record_date, m.diagnosis, m.treatment_plan 
                FROM medical_records m 
                JOIN patients p ON m.patient_id = p.patient_id 
                WHERE m.doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) 
                ORDER BY m.record_date DESC 
                LIMIT 10
            """,

            # --- Existing Filters ---
            "hypertension": "SELECT p.first_name, p.last_name, m.diagnosis, m.treatment_plan FROM patients p JOIN medical_records m ON p.patient_id = m.patient_id WHERE LOWER(m.diagnosis) LIKE '%hypertension%' LIMIT 50",
            
            "penicillin": "SELECT p.first_name, p.last_name, a.allergen, a.severity FROM patients p JOIN allergies a ON p.patient_id = a.patient_id WHERE LOWER(a.allergen) LIKE '%penicillin%' AND a.severity IN ('Severe', 'Life-Threatening')",
            
            "my patients": "SELECT p.first_name, p.last_name, p.contact_number, pdm.status FROM patients p JOIN patient_doctor_mapping pdm ON p.patient_id = pdm.patient_id WHERE pdm.doctor_id = (SELECT doctor_id FROM doctors LIMIT 1) AND pdm.status = 'Active'",
        }
        
        generated = "SELECT * FROM patients LIMIT 10" # Default
        req_lower = (request.text or "").lower()
        
        # Simple keyword matching to pick the right SQL
        for key, sql in mapping.items():
            if key in req_lower:
                generated = sql
                break

        try:
            safe_q = (request.text or "").replace("'", "''")
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{request.username or 'guest'}', '{request.role}', '{safe_q}', 'GENERATED')")
        except Exception:
            pass
            
        return {"generated_sql": generated}

    elif request.mode == "execute":
        if not request.sql:
            return {"error": "no sql provided"}
        if not is_safe_sql(request.sql):
            return {"error": "query rejected by safety policy"}
        try:
            results = execute_query(request.sql)
            recs = generate_doctor_recommendations(results, request.text or "")
            return {"results": results, "recommendations": recs}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "invalid mode"}

@router.get("/doctor/analytics")
def get_doctor_analytics():
    try:
        # 1. SUMMARY CARDS
        my_patients = execute_query("SELECT COUNT(*) as count FROM patient_doctor_mapping WHERE status = 'Active'")[0]['count']
        today_appts = execute_query("SELECT COUNT(*) as count FROM appointments WHERE DATE(appointment_date) = CURRENT_DATE")[0]['count']
        pending_reports = execute_query("SELECT COUNT(*) as count FROM medical_records WHERE treatment_plan IS NULL OR treatment_plan = ''")[0]['count']
        critical_patients = execute_query("SELECT COUNT(*) as count FROM allergies WHERE severity = 'Life-Threatening'")[0]['count']

        # 2. APPOINTMENTS TREND
        trend_raw = execute_query("SELECT to_char(appointment_date, 'Mon DD') as date, COUNT(*) as count FROM appointments WHERE appointment_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY 1 ORDER BY MIN(appointment_date)")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]

        # 3. PATIENT CONDITION
        condition_raw = execute_query("SELECT severity, COUNT(*) as count FROM allergies GROUP BY severity")
        condition_data = {row['severity']: row['count'] for row in condition_raw}

        # 4. COMMON DIAGNOSES
        diag_raw = execute_query("SELECT diagnosis, COUNT(*) as count FROM medical_records GROUP BY diagnosis ORDER BY count DESC LIMIT 5")
        diag_data = {row['diagnosis']: row['count'] for row in diag_raw}

        # 5. COMPLIANCE
        comp_raw = execute_query("SELECT status, COUNT(*) as count FROM appointments GROUP BY status")
        compliance_data = {row['status']: row['count'] for row in comp_raw}
        
        # 6. AI USAGE
        try:
            ai_usage = execute_query("SELECT COUNT(*) as count FROM audit_logs WHERE role='doctor' AND DATE(timestamp) = CURRENT_DATE")[0]['count']
        except:
            ai_usage = 0

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

@router.get("/doctor/patients")
def get_doctor_patients():
    """Returns a list of patients assigned to the doctor"""
    try:
        # Improved Logic: Get latest medical record for each patient
        query = """
            SELECT 
                p.patient_id, 
                p.first_name, 
                p.last_name, 
                p.dob, 
                p.gender, 
                p.contact_number, 
                m.diagnosis, 
                m.treatment_plan
            FROM patients p
            LEFT JOIN (
                SELECT DISTINCT ON (patient_id) * FROM medical_records 
                ORDER BY patient_id, record_date DESC
            ) m ON p.patient_id = m.patient_id
            LIMIT 50
        """
        results = execute_query(query)
        return results
    except Exception as e:
        return {"error": str(e)}