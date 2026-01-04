import os
import re
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional 
from dotenv import load_dotenv
from backend.db import execute_query 
from huggingface_hub import InferenceClient

load_dotenv()
app = FastAPI()

# 1. CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. AI CONFIGURATION
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
client = InferenceClient(token=HF_API_KEY)

# 3. DATA MODELS
class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

class QueryRequest(BaseModel):
    text: Optional[str] = None 
    sql: Optional[str] = None  
    username: Optional[str] = "guest" 
    role: Optional[str] = "general"      
    mode: str = "generate"     

class DoctorModel(BaseModel):
    first_name: str
    last_name: str
    specialty: str
    email: str
    phone_contact: str

class PatientModel(BaseModel):
    first_name: str
    last_name: str
    dob: str
    gender: str
    contact_number: str
    address: str
    insurance_provider: str

# 4. HELPER: SQL SAFETY GUARD
def is_safe_sql(sql: str) -> bool:
    dangerous_patterns = [r"\bDROP\b", r"\bDELETE\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bGRANT\b", r"\bREVOKE\b"]
    for pattern in dangerous_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            return False
    return True

# 5. HELPER: ROLE-BASED SCHEMA
def get_schema_for_role(role: str) -> str:
    base_schema = """- patients (patient_id, first_name, last_name, dob, gender, contact_number, address, insurance_provider)"""
    if role.lower() == "doctor":
        return f"""{base_schema}
        - doctors (doctor_id, first_name, last_name, specialty, email, phone_contact)
        - appointments (appointment_id, patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status)
        - medical_records (record_id, patient_id, doctor_id, diagnosis, treatment_plan, record_date)
        - allergies (allergy_id, patient_id, allergen, severity)"""
    elif role.lower() == "nurse":
        return f"""{base_schema}
        - doctors (doctor_id, first_name, last_name, specialty, phone_contact)
        - appointments (appointment_id, patient_id, doctor_id, appointment_date, room_number, status)
        - allergies (allergy_id, patient_id, allergen, severity)"""
    elif role.lower() == "billing":
        return f"""{base_schema}
        - invoices (invoice_id, patient_id, amount, status, issue_date)"""
    else: return base_schema

# 6. HELPER: AUDIT LOGGING
def log_audit(username, role, content, status):
    safe_content = content.replace("'", "''")
    log_query = f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{username}', '{role}', '{safe_content}', '{status}')"
    execute_query(log_query)

# --- CORE ENDPOINTS ---

@app.post("/login")
def login(creds: LoginRequest):
    sql = f"SELECT * FROM users WHERE username = '{creds.username}' AND password = '{creds.password}'"
    if creds.role: sql += f" AND role = '{creds.role}'"
    result = execute_query(sql)
    if not result: raise HTTPException(status_code=401, detail="Invalid Credentials or Role")
    return {"status": "success", "role": result[0]['role'], "username": creds.username}

@app.post("/query")
async def query_ai(request: QueryRequest):
    if request.text == "Ping": return {"status": "Online"}
    if request.mode == "generate":
        role_schema = get_schema_for_role(request.role)
        system_prompt = f"""You are a PostgreSQL expert. Schema: {role_schema}
        TASK: Return a JSON object with keys: "sql", "explanation", "risk_level", "confidence", "tables_used".
        Return ONLY raw JSON."""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": request.text}]
        try:
            response = client.chat_completion(messages=messages, model=MODEL_ID, max_tokens=300, temperature=0.1)
            clean_json = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(clean_json)
            return {"generated_sql": ai_data.get("sql"), "explanation": ai_data.get("explanation"), "risk_level": ai_data.get("risk_level"), "confidence": ai_data.get("confidence"), "tables_used": ai_data.get("tables_used")}
        except Exception as e: return {"error": str(e)}
    elif request.mode == "execute":
        if not is_safe_sql(request.sql): return {"error": "Security Alert: SQL blocked."}
        try:
            data = execute_query(request.sql)
            log_audit(request.username, request.role, f"Executed AI Query", "SUCCESS")
            return {"results": data}
        except Exception as e: return {"error": str(e)}

# --- 📊 ADVANCED ANALYTICS ---
@app.get("/analytics")
def get_analytics():
    try:
        # 1. SUMMARY COUNTS
        doc_count = execute_query("SELECT COUNT(*) as count FROM doctors")[0]['count']
        nurse_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'nurse'")[0]['count']
        patient_count = execute_query("SELECT COUNT(*) as count FROM patients")[0]['count']
        active_today = execute_query("SELECT COUNT(DISTINCT username) as count FROM audit_logs WHERE DATE(timestamp) = CURRENT_DATE")[0]['count']
        
        # 2. ROLE DISTRIBUTION
        roles_raw = execute_query("SELECT role, COUNT(*) as count FROM users GROUP BY role")
        roles_data = {row['role']: row['count'] for row in roles_raw}

        # 3. DEPARTMENT LOAD
        dept_raw = execute_query("SELECT specialty, COUNT(*) as count FROM doctors GROUP BY specialty")
        dept_data = {row['specialty']: row['count'] for row in dept_raw}

        # 4. SYSTEM USAGE
        usage_raw = execute_query("SELECT role, COUNT(*) as count FROM audit_logs GROUP BY role")
        usage_data = {row['role']: row['count'] for row in usage_raw}

        # 5. GROWTH TREND
        trend_raw = execute_query("SELECT to_char(timestamp, 'Mon DD') as date, COUNT(*) as count FROM audit_logs GROUP BY 1 ORDER BY MIN(timestamp) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]

        # 🚨 FIX: FETCH ALL RECENT AUDIT LOGS (Visible on dashboard)
        security_logs = execute_query("""
            SELECT username, role, question, status, timestamp 
            FROM audit_logs 
            ORDER BY timestamp DESC LIMIT 10
        """)

        # 7. AUTOMATED INSIGHTS
        insights = ["System health check passed.", f"Workforce consists mainly of {max(roles_data, key=roles_data.get) if roles_data else 'Staff'}."]
        if doc_count > 0 and (patient_count / doc_count) > 10:
            insights.append("⚠️ Doctor utilization is high. Consider hiring.")

        return {
            "counts": { "doctors": doc_count, "nurses": nurse_count, "patients": patient_count },
            "summary": { "active_today": active_today },
            "roles": roles_data,
            "departments": dept_data,
            "usage": usage_data,
            "trend": { "labels": trend_labels, "data": trend_values },
            "security": security_logs,
            "insights": insights
        }
    except Exception as e: return {"error": str(e)}

# --- 👨‍⚕️ DOCTOR CRUD ---
@app.get("/doctors")
def get_doctors():
    return execute_query("SELECT * FROM doctors ORDER BY doctor_id DESC")

@app.post("/doctors")
def add_doctor(doc: DoctorModel):
    sql = f"INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('{doc.first_name}', '{doc.last_name}', '{doc.specialty}', '{doc.email}', '{doc.phone_contact}')"
    execute_query(sql)
    log_audit("admin", "admin", f"Added Doctor: {doc.last_name}", "SUCCESS")
    return {"message": "Doctor added"}

@app.put("/doctors/{id}")
def update_doctor(id: int, doc: DoctorModel):
    sql = f"UPDATE doctors SET first_name='{doc.first_name}', last_name='{doc.last_name}', specialty='{doc.specialty}', email='{doc.email}', phone_contact='{doc.phone_contact}' WHERE doctor_id={id}"
    execute_query(sql)
    log_audit("admin", "admin", f"Updated Doctor ID: {id}", "SUCCESS")
    return {"message": "Doctor updated"}

@app.delete("/doctors/{id}")
def delete_doctor(id: int):
    try:
        execute_query(f"DELETE FROM appointments WHERE doctor_id={id}")
        execute_query(f"DELETE FROM medical_records WHERE doctor_id={id}")
        execute_query(f"DELETE FROM audit_logs WHERE question LIKE '%Doctor%ID: {id}%'")
        execute_query(f"DELETE FROM doctors WHERE doctor_id={id}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- 🛌 PATIENT CRUD ---
@app.get("/patients")
def get_patients():
    return execute_query("SELECT * FROM patients ORDER BY patient_id DESC LIMIT 50")

@app.post("/patients")
def add_patient(pat: PatientModel):
    sql = f"INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('{pat.first_name}', '{pat.last_name}', '{pat.dob}', '{pat.gender}', '{pat.contact_number}', '{pat.address}', '{pat.insurance_provider}')"
    execute_query(sql)
    log_audit("admin", "admin", f"Added Patient: {pat.last_name}", "SUCCESS")
    return {"message": "Patient added"}

@app.put("/patients/{id}")
def update_patient(id: int, pat: PatientModel):
    sql = f"UPDATE patients SET first_name='{pat.first_name}', last_name='{pat.last_name}', dob='{pat.dob}', gender='{pat.gender}', contact_number='{pat.contact_number}', address='{pat.address}', insurance_provider='{pat.insurance_provider}' WHERE patient_id={id}"
    execute_query(sql)
    log_audit("admin", "admin", f"Updated Patient ID: {id}", "SUCCESS")
    return {"message": "Patient updated"}

@app.delete("/patients/{id}")
def delete_patient(id: int):
    try:
        execute_query(f"DELETE FROM appointments WHERE patient_id={id}")
        execute_query(f"DELETE FROM medical_records WHERE patient_id={id}")
        execute_query(f"DELETE FROM allergies WHERE patient_id={id}")
        execute_query(f"DELETE FROM invoices WHERE patient_id={id}")
        execute_query(f"DELETE FROM audit_logs WHERE question LIKE '%Patient%ID: {id}%'")
        execute_query(f"DELETE FROM patients WHERE patient_id={id}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
