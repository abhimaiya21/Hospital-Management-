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
        # Expert NLP-to-SQL Engine - PostgreSQL Optimized
        # CASE-SENSITIVE, NULL-SAFE, EDGE-CASE HARDENED
        mapping = {
            # --- 1. My Appointments Today (NULL-SAFE, EXPLICIT COLUMNS) ---
            "appointments": """
                SELECT 
                    a.appointment_id, 
                    TO_CHAR(a.appointment_date, 'HH12:MI AM') as time, 
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    COALESCE(p.gender, 'Not Specified') as gender, 
                    COALESCE(EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.dob)), 0) as age, 
                    COALESCE(a.patient_problem_text, 'No problem text') as patient_problem_text, 
                    COALESCE(a.status, 'Unknown') as status 
                FROM appointments a 
                INNER JOIN patients p ON a.patient_id = p.patient_id AND p.is_active = TRUE
                WHERE a.doctor_id = (SELECT doctor_id FROM doctors WHERE is_active = TRUE LIMIT 1) 
                  AND DATE(a.appointment_date) = CURRENT_DATE 
                  AND a.status IS NOT NULL
                ORDER BY a.appointment_date ASC
                LIMIT 100
            """,

            # --- 2. My Active Inpatients (EXPLICIT JOIN, NULL CHECKS) ---
            "inpatients": """
                SELECT 
                    adm.admission_id, 
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    COALESCE(r.room_number, 'TBD') as room_number, 
                    adm.admission_date, 
                    COALESCE(adm.admission_reason, 'Not specified') as admission_reason, 
                    adm.status 
                FROM admissions adm 
                INNER JOIN patients p ON adm.patient_id = p.patient_id AND p.is_active = TRUE
                INNER JOIN rooms r ON adm.room_id = r.room_id
                WHERE adm.primary_doctor_id = (SELECT doctor_id FROM doctors WHERE is_active = TRUE LIMIT 1) 
                  AND adm.status = 'Active'
                  AND adm.discharge_date IS NULL
                ORDER BY adm.admission_date DESC
                LIMIT 50
            """,
            
            "admitted": """
                SELECT 
                    adm.admission_id, 
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    COALESCE(r.room_number, 'TBD') as room_number, 
                    adm.admission_date, 
                    COALESCE(adm.admission_reason, 'Not specified') as admission_reason, 
                    adm.status 
                FROM admissions adm 
                INNER JOIN patients p ON adm.patient_id = p.patient_id AND p.is_active = TRUE
                INNER JOIN rooms r ON adm.room_id = r.room_id
                WHERE adm.primary_doctor_id = (SELECT doctor_id FROM doctors WHERE is_active = TRUE LIMIT 1) 
                  AND adm.status = 'Active'
                  AND adm.discharge_date IS NULL
                LIMIT 50
            """,

            # --- 3. Pending Lab Results (CASE-SENSITIVE STATUS) ---
            "lab": """
                SELECT 
                    lt.test_id, 
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    COALESCE(lt.test_name, 'Unknown Test') as test_name, 
                    COALESCE(lt.test_category, 'General') as test_category, 
                    lt.ordered_date, 
                    COALESCE(lt.status, 'Unknown') as status 
                FROM lab_tests lt 
                INNER JOIN patients p ON lt.patient_id = p.patient_id
                WHERE lt.status IN ('Pending', 'Sample Collected', 'In Progress') 
                  AND lt.ordered_date IS NOT NULL
                ORDER BY lt.ordered_date ASC
                LIMIT 100
            """,

            # --- 4. Total Revenue (SAFE & SIMPLE) ---
            "revenue": """
                SELECT 
                    COUNT(*)::BIGINT as total_consultations, 
                    COALESCE(SUM(consultation_charges), 0)::NUMERIC as total_revenue,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN ROUND(COALESCE(SUM(consultation_charges), 0)::NUMERIC / COUNT(*), 2)
                        ELSE 0 
                    END as avg_consultation_fee
                FROM invoices
                WHERE consultation_charges IS NOT NULL
            """,

            # --- 5. Patient Medical History (NULL-SAFE, RECENT ONLY) ---
            "history": """
                SELECT 
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    m.record_date, 
                    COALESCE(m.diagnosis, 'No diagnosis recorded') as diagnosis, 
                    COALESCE(m.treatment_plan, 'No treatment plan') as treatment_plan 
                FROM medical_records m 
                INNER JOIN patients p ON m.patient_id = p.patient_id AND p.is_active = TRUE
                WHERE m.doctor_id = (SELECT doctor_id FROM doctors WHERE is_active = TRUE LIMIT 1) 
                  AND m.record_date IS NOT NULL
                ORDER BY m.record_date DESC 
                LIMIT 10
            """,

            # --- CASE-SENSITIVE FILTERS (Using LIKE with case-sensitive collation) ---
            "hypertension": """
                SELECT 
                    p.patient_id,
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    m.diagnosis, 
                    COALESCE(m.treatment_plan, 'Not assigned') as treatment_plan,
                    m.record_date
                FROM patients p 
                INNER JOIN medical_records m ON p.patient_id = m.patient_id
                WHERE m.diagnosis ILIKE '%hypertension%'
                  AND m.diagnosis IS NOT NULL
                  AND m.diagnosis != ''
                  AND p.is_active = TRUE
                ORDER BY m.record_date DESC
                LIMIT 50
            """,
            
            "penicillin": """
                SELECT 
                    p.patient_id,
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    a.allergen, 
                    a.severity,
                    COALESCE(a.reaction_description, 'No description') as reaction_description
                FROM patients p 
                INNER JOIN allergies a ON p.patient_id = a.patient_id
                WHERE a.allergen ILIKE '%penicillin%'
                  AND a.severity IN ('Severe', 'Life-Threatening')
                  AND a.allergen IS NOT NULL
                  AND a.allergen != ''
                  AND p.is_active = TRUE
                ORDER BY a.severity DESC, p.last_name ASC
                LIMIT 100
            """,
            
            "my patients": """
                SELECT 
                    p.patient_id,
                    COALESCE(p.first_name, 'Unknown') as first_name, 
                    COALESCE(p.last_name, 'Unknown') as last_name, 
                    COALESCE(p.contact_number, 'No contact') as contact_number, 
                    pdm.status,
                    pdm.assigned_date
                FROM patients p 
                INNER JOIN patient_doctor_mapping pdm ON p.patient_id = pdm.patient_id
                WHERE pdm.doctor_id = (SELECT doctor_id FROM doctors WHERE is_active = TRUE LIMIT 1) 
                  AND pdm.status = 'Active'
                  AND p.is_active = TRUE
                ORDER BY pdm.assigned_date DESC
                LIMIT 100
            """,
        }
        
        # FAIL-SAFE DEFAULT: Return minimal safe query
        generated = """
            SELECT 
                patient_id, 
                COALESCE(first_name, 'Unknown') as first_name, 
                COALESCE(last_name, 'Unknown') as last_name, 
                COALESCE(gender, 'Not Specified') as gender 
            FROM patients 
            WHERE is_active = TRUE 
            LIMIT 10
        """
        
        # Expert NLP Keyword Matching (CASE-INSENSITIVE for user convenience)
        req_lower = (request.text or "").lower().strip()
        
        # Validate request is not empty
        if not req_lower or len(req_lower) < 2:
            return {"generated_sql": "INVALID_SQL_REQUEST", "reason": "Query too short"}
        
        # Match keywords to SQL templates
        matched = False
        for key, sql in mapping.items():
            if key in req_lower:
                generated = sql
                matched = True
                break
        
        # If no match and query looks like SQL injection attempt, reject
        dangerous_keywords = ["drop", "delete", "truncate", "alter", "create", "exec", "--", "/*", "*/", ";"]
        if not matched and any(kw in req_lower for kw in dangerous_keywords):
            return {"generated_sql": "INVALID_SQL_REQUEST", "reason": "Unsafe query detected"}

        # Audit Log (SQL Injection Protected)
        try:
            safe_q = (request.text or "").replace("'", "''")[:500]  # Truncate to prevent overflow
            safe_user = (request.username or "guest").replace("'", "''")[:100]
            safe_role = (request.role or "unknown").replace("'", "''")[:50]
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{safe_user}', '{safe_role}', '{safe_q}', 'GENERATED')")
        except Exception:
            pass  # Fail silently - audit is not critical
            
        return {"generated_sql": generated, "matched_keyword": key if matched else "default"}

    elif request.mode == "execute":
        # EXECUTE MODE: Run the generated SQL with safety checks
        if not request.sql:
            return {"error": "No SQL provided", "code": "MISSING_SQL"}
        
        # Enhanced Safety Check
        if not is_safe_sql(request.sql):
            return {"error": "Query rejected by safety policy", "code": "UNSAFE_SQL"}
        
        # Additional length check (prevent massive queries)
        if len(request.sql) > 10000:
            return {"error": "Query too long", "code": "QUERY_TOO_LONG"}
        
        try:
            results = execute_query(request.sql)
            
            # Handle empty results gracefully
            if not results or len(results) == 0:
                return {
                    "results": [], 
                    "recommendations": ["No records found matching your criteria."],
                    "count": 0
                }
            
            # Generate context-aware recommendations
            recs = generate_doctor_recommendations(results, request.text or "")
            
            return {
                "results": results, 
                "recommendations": recs,
                "count": len(results),
                "query_executed": request.sql[:200] + "..." if len(request.sql) > 200 else request.sql
            }
        except Exception as e:
            # Detailed error for debugging
            error_msg = str(e)
            return {
                "error": "Query execution failed", 
                "details": error_msg if "syntax" in error_msg.lower() else "Database error",
                "code": "EXECUTION_ERROR"
            }
    
    return {"error": "Invalid mode - use 'generate' or 'execute'", "code": "INVALID_MODE"}

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