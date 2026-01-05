import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.db import execute_query

router = APIRouter()

class QueryRequest(BaseModel):
    text: Optional[str] = None 
    sql: Optional[str] = None
    username: Optional[str] = "guest" 
    role: str = "nurse"
    mode: str = "generate"

@router.post("/nurse/query")
async def nurse_query(request: QueryRequest):
    # simple safe generator (fallback) and executor so frontend gets responses
    if request.mode == "generate":
        # Enhanced mapping
        mapping = {
            "today": "SELECT * FROM appointments WHERE appointment_date = CURRENT_DATE",
            "allergy": "SELECT p.* FROM patients p JOIN allergies a ON p.patient_id = a.patient_id WHERE LOWER(a.severity) IN ('severe', 'life-threatening')",
            "room 202": "SELECT * FROM appointments WHERE room_number = '202'",
            "pending vitals": "SELECT * FROM patients WHERE patient_id NOT IN (SELECT patient_id FROM medical_records WHERE record_date = CURRENT_DATE)" # Mock logic
        }
        
        generated = "SELECT * FROM appointments WHERE appointment_date = CURRENT_DATE LIMIT 20"
        req_lower = (request.text or "").lower()
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
        sql = request.sql.strip()
        # very basic safety: allow only SELECT queries
        if not sql.lower().startswith("select"):
            return {"error": "only SELECT queries are allowed for execution"}
        try:
            results = execute_query(sql)
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "invalid mode"}

@router.get("/nurse/analytics")
def get_nurse_analytics():
    try:
        # 1. SUMMARY CARDS
        occupied_beds = execute_query("SELECT COUNT(DISTINCT room_number) as count FROM appointments WHERE status != 'Completed' AND room_number IS NOT NULL")[0]['count']
        # Proxy: Patients with appointment today but no medical record today = Pending Vitals/Checks
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
        docs_on_duty = execute_query("SELECT COUNT(*) as count FROM doctors")[0]['count'] 
        alerts_today = execute_query("SELECT COUNT(*) as count FROM allergies WHERE severity IN ('High', 'Severe', 'Life-Threatening')")[0]['count']

        # 2. BED OCCUPANCY TREND (Last 7 Days - Using Appointment count as proxy)
        trend_raw = execute_query("SELECT to_char(appointment_date, 'Mon DD') as date, COUNT(*) as count FROM appointments WHERE appointment_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY 1 ORDER BY MIN(appointment_date)")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]

        # 3. VITALS COLLECTION STATUS (Proxy based on today's appointments status)
        vitals_data = {
            "Completed": execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date::date = CURRENT_DATE AND status = 'Completed'")[0]['count'],
            "Pending": pending_vitals,
            "Missed": execute_query("SELECT COUNT(*) as count FROM appointments WHERE appointment_date::date = CURRENT_DATE AND status = 'Cancelled'")[0]['count']
        }

        # 4. ALERTS BY TYPE
        alerts_raw = execute_query("SELECT severity, COUNT(*) as count FROM allergies GROUP BY severity")
        alerts_data = {row['severity']: row['count'] for row in alerts_raw}

        # 5. WARD WORKLOAD (Using room_number grouping as proxy)
        ward_raw = execute_query("SELECT room_number, COUNT(*) as count FROM appointments WHERE room_number IS NOT NULL GROUP BY room_number ORDER BY count DESC LIMIT 5")
        ward_data = {f"Room {row['room_number']}": row['count'] for row in ward_raw}

        # 6. NURSE INSIGHTS
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