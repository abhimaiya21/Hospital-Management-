from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.db import execute_query

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

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

def log_audit(username, role, content, status):
    safe_content = content.replace("'", "''")
    log_query = f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{username}', '{role}', '{safe_content}', '{status}')"
    execute_query(log_query)

@router.post("/login") # Move this here as Admin manages users
def login(creds: LoginRequest):
    sql = f"SELECT * FROM users WHERE username = '{creds.username}' AND password = '{creds.password}'"
    if creds.role: sql += f" AND role = '{creds.role}'"
    result = execute_query(sql)
    if not result: raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {"status": "success", "role": result[0]['role'], "username": creds.username}

@router.get("/analytics")
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

        # 3. DEPARTMENT LOAD (Fix: Handle comma-separated specialties)
        # unnest(string_to_array(specialty, ',')) splits the string and creates a row for each item
        dept_raw = execute_query("""
            SELECT TRIM(s) as spec, COUNT(*) as count 
            FROM doctors, unnest(string_to_array(specialty, ',')) as s 
            GROUP BY spec
        """)
        dept_data = {row['spec']: row['count'] for row in dept_raw}

        # 4. SYSTEM USAGE
        usage_raw = execute_query("SELECT role, COUNT(*) as count FROM audit_logs GROUP BY role")
        usage_data = {row['role']: row['count'] for row in usage_raw}

        # 5. GROWTH TREND
        trend_raw = execute_query("SELECT to_char(timestamp, 'Mon DD') as date, COUNT(*) as count FROM audit_logs GROUP BY 1 ORDER BY MIN(timestamp) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['count'] for row in trend_raw]

        # 6. FETCH ALL RECENT AUDIT LOGS (Visible on dashboard)
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

@router.get("/doctors")
def get_doctors(): return execute_query("SELECT * FROM doctors ORDER BY doctor_id DESC")

@router.post("/doctors")
def add_doctor(doc: DoctorModel):
    # 1. Insert into Doctors table
    sql = f"INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact) VALUES ('{doc.first_name}', '{doc.last_name}', '{doc.specialty}', '{doc.email}', '{doc.phone_contact}')"
    execute_query(sql)
    
    # 2. Create User Account (Generating a default username/password)
    # Pattern: first letter of firstname + lastname (lowercase)
    username = f"{doc.first_name[0].lower()}.{doc.last_name.lower()}"
    password = "password123" # Default password
    
    # Check if username exists, append random if needed (simple logic handled by catching error or just naive insert)
    # For now, naive insert. In prod, check unique.
    try:
        user_sql = f"INSERT INTO users (username, password, role) VALUES ('{username}', '{password}', 'doctor')"
        execute_query(user_sql)
        msg = f"Doctor added. Login: {username} / {password}"
    except Exception:
        msg = "Doctor added, but user account creation failed (username might exist)."

    log_audit("admin", "admin", f"Added Doctor: {doc.last_name}", "SUCCESS")
    return {"message": msg}

@router.put("/doctors/{id}")
def update_doctor(id: int, doc: DoctorModel):
    sql = f"UPDATE doctors SET first_name='{doc.first_name}', last_name='{doc.last_name}', specialty='{doc.specialty}', email='{doc.email}', phone_contact='{doc.phone_contact}' WHERE doctor_id={id}"
    execute_query(sql)
    log_audit("admin", "admin", f"Updated Doctor ID: {id}", "SUCCESS")
    return {"message": "Doctor updated"}

@router.delete("/doctors/{id}")
def delete_doctor(id: int):
    execute_query(f"DELETE FROM appointments WHERE doctor_id={id}")
    execute_query(f"DELETE FROM medical_records WHERE doctor_id={id}")
    execute_query(f"DELETE FROM audit_logs WHERE question LIKE '%Doctor%ID: {id}%'")
    execute_query(f"DELETE FROM doctors WHERE doctor_id={id}")
    return {"message": "Doctor deleted"}

@router.get("/patients")
def get_patients(): return execute_query("SELECT * FROM patients ORDER BY patient_id DESC LIMIT 50")

@router.post("/patients")
def add_patient(pat: PatientModel):
    sql = f"INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('{pat.first_name}', '{pat.last_name}', '{pat.dob}', '{pat.gender}', '{pat.contact_number}', '{pat.address}', '{pat.insurance_provider}')"
    execute_query(sql)
    log_audit("admin", "admin", f"Added Patient: {pat.last_name}", "SUCCESS")
    return {"message": "Patient added"}

@router.put("/patients/{id}")
def update_patient(id: int, pat: PatientModel):
    sql = f"UPDATE patients SET first_name='{pat.first_name}', last_name='{pat.last_name}', dob='{pat.dob}', gender='{pat.gender}', contact_number='{pat.contact_number}', address='{pat.address}', insurance_provider='{pat.insurance_provider}' WHERE patient_id={id}"
    execute_query(sql)
    log_audit("admin", "admin", f"Updated Patient ID: {id}", "SUCCESS")
    return {"message": "Patient updated"}

@router.delete("/patients/{id}")
def delete_patient(id: int):
    execute_query(f"DELETE FROM appointments WHERE patient_id={id}")
    execute_query(f"DELETE FROM medical_records WHERE patient_id={id}")
    execute_query(f"DELETE FROM allergies WHERE patient_id={id}")
    execute_query(f"DELETE FROM invoices WHERE patient_id={id}")
    execute_query(f"DELETE FROM audit_logs WHERE question LIKE '%Patient%ID: {id}%'")
    execute_query(f"DELETE FROM patients WHERE patient_id={id}")
    return {"message": "Patient deleted"}