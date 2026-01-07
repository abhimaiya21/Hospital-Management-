import os
import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.db import execute_query, get_db_connection

router = APIRouter()

class QueryRequest(BaseModel):
    text: Optional[str] = None 
    sql: Optional[str] = None
    username: Optional[str] = "guest" 
    role: str = "nurse"
    mode: str = "generate"

def generate_nurse_sql(text: str) -> str:
    text = text.lower()
    
    # 1. Diagnosis Search (e.g. "Patients with Covid-19")
    diag_match = re.search(r"patients?\s+with\s+(.+)", text)
    if diag_match and "severity" not in text and "allergy" not in text:
        condition = diag_match.group(1).strip()
        safe_condition = condition.replace("'", "''")
        return f"""
            SELECT p.first_name, p.last_name, m.diagnosis, m.treatment_plan, m.record_date 
            FROM medical_records m 
            JOIN patients p ON m.patient_id = p.patient_id 
            WHERE m.diagnosis ILIKE '%{safe_condition}%' 
            ORDER BY m.record_date DESC LIMIT 20
        """.strip()

    # 2. Cardiology appointments with allergy risks (Legacy)
    if "cardio" in text and "allergy" in text:
        return """
            SELECT a.appointment_id, p.first_name, p.last_name, d.specialty, al.allergen, al.severity 
            FROM appointments a 
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id 
            JOIN patients p ON a.patient_id = p.patient_id 
            JOIN allergies al ON p.patient_id = al.patient_id 
            WHERE LOWER(d.specialty) LIKE '%cardio%' 
            AND LOWER(al.severity) IN ('severe', 'life-threatening')
        """.strip()

    # 3. Room Search
    room_match = re.search(r"room\s+([a-z0-9\-]+)", text)
    if room_match:
        room_num = room_match.group(1)
        return f"SELECT a.appointment_id, p.first_name, p.last_name, a.appointment_date, a.room_number, a.status FROM appointments a JOIN patients p ON a.patient_id = p.patient_id WHERE LOWER(a.room_number) = '{room_num.lower()}' AND a.status IN ('Scheduled', 'In Progress') ORDER BY a.appointment_date ASC LIMIT 1"

    # 4. Today's Appointments
    if "today" in text and "appointment" in text:
        return "SELECT a.appointment_id, p.first_name, p.last_name, d.full_name as doctor, a.appointment_date, a.reason_for_visit, a.status FROM appointments a JOIN patients p ON a.patient_id = p.patient_id LEFT JOIN doctors d ON a.doctor_id = d.doctor_id WHERE a.appointment_date::date = CURRENT_DATE"

    # 5. Patients with Severe Allergies
    if "allergy" in text and ("severe" in text or "life-threatening" in text):
        return "SELECT p.first_name, p.last_name, a.allergen, a.severity FROM patients p JOIN allergies a ON p.patient_id = a.patient_id WHERE LOWER(a.severity) IN ('severe', 'life-threatening')"

    # 6. Pending Vitals
    if "vital" in text and "pending" in text:
        return """
            SELECT p.first_name, p.last_name, a.appointment_date 
            FROM appointments a 
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.appointment_date::date = CURRENT_DATE 
            AND NOT EXISTS (
                SELECT 1 FROM medical_records m 
                WHERE m.patient_id = a.patient_id 
                AND m.record_date = CURRENT_DATE
            )
        """.strip()

    # Default/Fallback
    return "SELECT * FROM appointments WHERE appointment_date::date = CURRENT_DATE LIMIT 5"

def generate_recommendations(results: List[Dict[str, Any]], query_text: str) -> List[str]:
    recs = []
    text = query_text.lower()
    
    if not results:
        return ["No matched records found for this query."]

    # Diagnosis Logic
    if "with" in text and "patients" in text:
         if any("covid" in r.get('diagnosis', '').lower() for r in results):
             recs.append("⚠️ infectious case detected. Ensure isolation protocols.")
         elif any("fracture" in r.get('diagnosis', '').lower() for r in results):
             recs.append("Ensure mobility assistance is available.")
         else:
             recs.append("Review treatment plan and monitor vitals.")
             
    # Allergy Logic
    if "allergy" in text:
        severe_count = sum(1 for r in results if r.get('severity', '').lower() in ['severe', 'life-threatening'])
        if severe_count > 0:
            recs.append(f"⚠️ Found {severe_count} patient(s) with Life-Threatening allergies. ALERT PHYSICIAN immediately.")

    # Appointment Logic
    if "appointment" in text:
        cancelled = sum(1 for r in results if r.get('status', '').lower() == 'cancelled')
        if cancelled > 1:
            recs.append(f"Found {cancelled} cancelled appointments. Contact patients for rescheduling.")
            
    # Room Logic
    if "room" in text:
        if results:
             recs.append("✅ Verify patient identity matches wristband and check vitals.")

    return recs

@router.post("/nurse/query")
async def nurse_query(request: QueryRequest):
    if request.mode == "generate":
        generated_sql = generate_nurse_sql(request.text or "")
        try:
            safe_q = (request.text or "").replace("'", "''")
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{request.username or 'guest'}', '{request.role}', '{safe_q}', 'GENERATED')")
        except Exception:
            pass
        return {"generated_sql": generated_sql}

    elif request.mode == "execute":
        if not request.sql:
            return {"error": "no sql provided"}
        sql = request.sql.strip()
        if "invoices" in sql.lower():
            return {"error": "⛔ ACCESS DENIED: Nurses cannot view billing data."}
        try:
            results = execute_query(sql)
            recs = generate_recommendations(results, request.text or "")
            return {
                "results": results,
                "recommendations": recs
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": "invalid mode"}

@router.get("/nurse/analytics")
def get_nurse_analytics():
    try:
        # Fixed analytics queries with ::date and exception handling for missing tables
        occupied_beds = execute_query("SELECT COUNT(DISTINCT room_number) as count FROM appointments WHERE status != 'Completed' AND room_number IS NOT NULL")[0]['count']
        pending_vitals = execute_query("""
            SELECT COUNT(*) as count 
            FROM appointments a 
            WHERE a.appointment_date::date = CURRENT_DATE 
            AND a.status = 'Scheduled'
            AND NOT EXISTS (
                SELECT 1 FROM medical_records m 
                WHERE m.patient_id = a.patient_id 
                AND m.record_date = CURRENT_DATE
            )
        """)[0]['count']
        
        try:
            docs_on_duty = execute_query("SELECT COUNT(*) as count FROM doctors")[0]['count']
        except:
             docs_on_duty = 0

        try:     
            alerts_today = execute_query("SELECT COUNT(*) as count FROM allergies WHERE severity IN ('High', 'Severe', 'Life-Threatening')")[0]['count']
        except:
            alerts_today = 0
            
        trend_raw = execute_query("SELECT to_char(appointment_date, 'Mon DD') as date, COUNT(*) as count FROM appointments WHERE appointment_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY 1 ORDER BY MIN(appointment_date)")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]
        
        vitals_data = {
            "Completed": execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date::date = CURRENT_DATE AND status = 'Completed'")[0]['count'],
            "Pending": pending_vitals,
            "Missed": execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date::date = CURRENT_DATE AND status = 'Cancelled'")[0]['count']
        }
        
        try:
            alerts_raw = execute_query("SELECT severity, COUNT(*) as count FROM allergies GROUP BY severity")
            alerts_data = {row['severity']: row['count'] for row in alerts_raw}
        except:
            alerts_data = {}
            
        ward_raw = execute_query("SELECT room_number, COUNT(*) as count FROM appointments WHERE room_number IS NOT NULL GROUP BY room_number ORDER BY count DESC LIMIT 5")
        ward_data = {f"Room {row['room_number']}": row['count'] for row in ward_raw}
        
        insights = [
            f"Room {list(ward_data.keys())[0]} has the highest patient load." if ward_data else "Ward load is balanced.",
            "Alerts for 'Severe' allergies have increased." if alerts_data.get('Severe', 0) > 5 else "Allergy alerts are within normal range."
        ]
        
        return {
            "summary": {
                "beds": occupied_beds,
                "vitals": pending_vitals,
                "doctors": docs_on_duty,
                "alerts": alerts_today
            },
            "trend": {"labels": trend_labels, "data": trend_values},
            "vitals": vitals_data,
            "alerts": alerts_data,
            "workload": ward_data,
            "insights": insights
        }
    except Exception as e:
        return {"error": str(e)}