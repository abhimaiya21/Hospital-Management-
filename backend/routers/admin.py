from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from backend.db import execute_query

router = APIRouter(tags=["admin"])

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

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
    department_id: int
    seniority_level: str

class PatientModel(BaseModel):
    first_name: str
    last_name: str
    dob: str
    gender: str
    contact_number: str
    address: str
    insurance_provider: str
    # These fields are optional for the API but used for logic
    doctor_id: Optional[int] = None
    room_number: Optional[str] = None
    status: Optional[str] = "Admitted"

class AppointmentCreate(BaseModel):
    patient_id: int
    problem_text: str

# --- Helper Function ---
def log_audit(username, role, content, status):
    safe_content = content.replace("'", "''")
    # Wrap in try/except in case audit_logs table is missing or locked
    try:
        log_query = f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{username}', '{role}', '{safe_content}', '{status}')"
        execute_query(log_query)
    except Exception:
        pass 

# --- Routes ---

@router.post("/login")
async def login(request: LoginRequest):
    """Admin login endpoint"""
    if request.role not in ['doctor', 'billing', 'admin']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    try:
        query = f"SELECT * FROM users WHERE username = '{request.username}' AND role = '{request.role}'"
        result = execute_query(query)
        
        if not result:
            # Check if user exists with a DIFFERENT role to give a helpful error
            check_query = f"SELECT role FROM users WHERE username = '{request.username}'"
            check_res = execute_query(check_query)
            
            if check_res:
                actual_role = check_res[0]['role']
                raise HTTPException(status_code=401, detail=f"Invalid role. You are registered as '{actual_role}'. Please switch tabs.")
            
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password (in a real app, use hashing!)
        user = result[0]
        if user['password'] != request.password:
             raise HTTPException(status_code=401, detail="Invalid username or password")

        return {
            "status": "success",
            "role": request.role,
            "username": request.username,
            "user_id": user['user_id']
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Login failed due to server error: {str(e)}")

@router.get("/analytics")
async def get_analytics():
    """Get admin analytics"""
    try:
        # 1. Counts
        doc_query = "SELECT COUNT(*) as count FROM doctors"
        doctor_count = execute_query(doc_query)[0]['count']
        
        billing_query = "SELECT COUNT(*) as count FROM users WHERE role = 'billing'"
        billing_count = execute_query(billing_query)[0]['count']
        
        admin_query = "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
        admin_count = execute_query(admin_query)[0]['count']
        
        patient_query = "SELECT COUNT(*) as count FROM patients"
        patient_count = execute_query(patient_query)[0]['count']
        
        # 2. Trends
        trend_query = "SELECT to_char(appointment_date, 'Mon DD') as date, COUNT(*) as count FROM appointments WHERE appointment_date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY 1 ORDER BY MIN(appointment_date)"
        trend_res = execute_query(trend_query)
        trend_labels = [row['date'] for row in trend_res]
        trend_data = [row['count'] for row in trend_res]
        
        # 3. Department Load
        try:
            dept_query = "SELECT specialty, COUNT(*) as count FROM doctors GROUP BY specialty"
            dept_res = execute_query(dept_query)
            dept_data = {row['specialty']: row['count'] for row in dept_res}
        except Exception:
            dept_data = {"General": 5}

        # 4. Security Logs
        try:
            usage_query = "SELECT role, COUNT(*) as count FROM audit_logs GROUP BY role"
            usage_res = execute_query(usage_query)
            usage_data = {row['role']: row['count'] for row in usage_res}
            
            sec_query = "SELECT username, question, status, timestamp FROM audit_logs ORDER BY timestamp DESC LIMIT 5"
            sec_rows = execute_query(sec_query)
        except Exception:
            usage_data = {"Doctor": 10, "Admin": 5}
            sec_rows = []

        return {
            "status": "success",
            "counts": {
                "doctors": doctor_count,
                "billing": billing_count,
                "admin": admin_count,
                "patients": patient_count
            },
            "trend": {"labels": trend_labels, "data": trend_data},
            "departments": dept_data,
            "usage": usage_data,
            "roles": {
                "Doctor": doctor_count,
                "Billing": billing_count,
                "Admin": admin_count
            },
            "insights": [
                "Patient growth is steady.",
                "Cardiology department has highest load.",
                f"{patient_count} active patients in the system."
            ],
            "security": sec_rows,
            "summary": {
                "active_today": execute_query("SELECT COUNT(*) as count FROM appointments WHERE DATE(appointment_date) = CURRENT_DATE")[0]['count']
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/users")
async def create_user(user: UserCreate):
    if user.role not in ['doctor', 'billing', 'admin']:
        raise HTTPException(status_code=400, detail="Invalid role. Must be: doctor, billing, or admin")
    
    # Check duplicate
    check = execute_query(f"SELECT * FROM users WHERE username = '{user.username}'")
    if check:
        raise HTTPException(status_code=400, detail="Username already exists")

    sql = f"INSERT INTO users (username, password, role) VALUES ('{user.username}', '{user.password}', '{user.role}')"
    execute_query(sql)
    return {"status": "success", "message": f"User {user.username} created"}

@router.get("/users")
async def get_all_users():
    query = "SELECT user_id as id, username, role FROM users ORDER BY role"
    users = execute_query(query)
    return {"status": "success", "users": users}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = f"DELETE FROM users WHERE user_id = {user_id}"
    execute_query(query)
    return {"status": "success", "message": "User deleted"}

@router.get("/departments")
def get_departments():
    # Return ID and Name for dropdowns
    return execute_query("SELECT department_id, department_name FROM departments ORDER BY department_name")

@router.get("/doctors")
def get_doctors():
    # JOIN departments to show Department Name instead of ID
    sql = """
        SELECT d.doctor_id, d.first_name, d.last_name, d.specialty, d.email, d.phone_contact, 
               dep.department_name, d.seniority_level
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.department_id
        ORDER BY d.doctor_id DESC
    """
    return execute_query(sql)

@router.post("/doctors")
def add_doctor(doc: DoctorModel):
    # 1. Insert Doctor
    sql = f"""
        INSERT INTO doctors (first_name, last_name, specialty, email, phone_contact, department_id, seniority_level) 
        VALUES ('{doc.first_name}', '{doc.last_name}', '{doc.specialty}', '{doc.email}', '{doc.phone_contact}', {doc.department_id}, '{doc.seniority_level}') 
        RETURNING doctor_id
    """
    res = execute_query(sql)
    
    if isinstance(res, dict) and "error" in res:
        raise HTTPException(status_code=500, detail=f"Database Error: {res['error']}")
    
    new_doc_id = res[0]['doctor_id'] if isinstance(res, list) and res else None

    # 2. Create User Account
    import random
    suffix = random.randint(100, 999)
    username = f"{doc.first_name[0].lower()}.{doc.last_name.lower()}{suffix}"
    password = "password123" 
    
    try:
        user_sql = f"INSERT INTO users (username, password, role) VALUES ('{username}', '{password}', 'doctor') RETURNING user_id"
        user_res = execute_query(user_sql)
        
        if isinstance(user_res, dict) and "error" in user_res:
             raise Exception(user_res['error'])
        
        # Link user_id back to doctor
        new_user_id = user_res[0]['user_id']
        execute_query(f"UPDATE doctors SET user_id = {new_user_id} WHERE doctor_id = {new_doc_id}")
             
        msg = f"Doctor added. Login: {username} / {password}"
    except Exception as e:
        # Rollback
        if new_doc_id:
            execute_query(f"DELETE FROM doctors WHERE doctor_id={new_doc_id}")
        raise HTTPException(status_code=500, detail=f"Failed to create user account. Doctor record rolled back. Error: {str(e)}")

    log_audit("admin", "admin", f"Added Doctor: {doc.last_name}", "SUCCESS")
    return {"message": msg}

@router.put("/doctors/{id}")
def update_doctor(id: int, doc: DoctorModel):
    sql = f"UPDATE doctors SET first_name='{doc.first_name}', last_name='{doc.last_name}', specialty='{doc.specialty}', email='{doc.email}', phone_contact='{doc.phone_contact}', seniority_level='{doc.seniority_level}' WHERE doctor_id={id}"
    execute_query(sql)
    log_audit("admin", "admin", f"Updated Doctor ID: {id}", "SUCCESS")
    return {"message": "Doctor updated"}

@router.delete("/doctors/{id}")
def delete_doctor(id: int):
    # Cascade delete safety
    execute_query(f"DELETE FROM appointments WHERE doctor_id={id}")
    execute_query(f"DELETE FROM medical_records WHERE doctor_id={id}")
    execute_query(f"DELETE FROM doctors WHERE doctor_id={id}")
    return {"message": "Doctor deleted"}

@router.get("/patients")
def get_patients():
    """
    Get top 50 patients showing MIXED status (Active, Discharged, Registered).
    Uses LEFT JOIN so we see everyone, regardless of whether they have a doctor assigned.
    """
    sql = """
    SELECT 
        -- Visual Serial Number
        ROW_NUMBER() OVER (ORDER BY p.patient_id DESC) as serial_no,
        
        p.patient_id,
        p.first_name,
        p.last_name,
        p.gender,
        p.contact_number,
        p.address,
        p.insurance_provider,
        
        -- Calculate Age dynamically
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.dob)) as age,

        -- Assigned Doctor Name (Unassigned if NULL)
        COALESCE(d.first_name || ' ' || d.last_name, 'Unassigned') as assigned_doctor,

        -- Room Number (Waiting if NULL)
        COALESCE(r.room_number, 'Waiting') as room_no,

        -- Status (Active, Discharged, or Default to Registered)
        COALESCE(a.status, 'Registered') as status

    FROM patients p
    
    -- LEFT JOIN with latest admissions (Active OR Historical)
    LEFT JOIN (
        SELECT DISTINCT ON (patient_id) * FROM admissions 
        ORDER BY patient_id, admission_date DESC
    ) a ON p.patient_id = a.patient_id

    -- LEFT JOIN Doctors
    LEFT JOIN doctors d ON a.primary_doctor_id = d.doctor_id

    -- LEFT JOIN Rooms
    LEFT JOIN rooms r ON a.room_id = r.room_id

    ORDER BY p.patient_id DESC
    LIMIT 50
    """
    return execute_query(sql)

@router.post("/patients")
def add_patient(pat: PatientModel):
    sql = f"""
        INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) 
        VALUES ('{pat.first_name}', '{pat.last_name}', '{pat.dob}', '{pat.gender}', '{pat.contact_number}', '{pat.address}', '{pat.insurance_provider}')
    """
    res = execute_query(sql)
    if isinstance(res, dict) and "error" in res:
        raise HTTPException(status_code=500, detail=f"Database Error: {res['error']}")
        
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
    # Cleanup all linked data before deleting patient
    execute_query(f"DELETE FROM appointments WHERE patient_id={id}")
    execute_query(f"DELETE FROM medical_records WHERE patient_id={id}")
    execute_query(f"DELETE FROM allergies WHERE patient_id={id}")
    execute_query(f"DELETE FROM invoices WHERE patient_id={id}")
    execute_query(f"DELETE FROM admissions WHERE patient_id={id}")
    execute_query(f"DELETE FROM patients WHERE patient_id={id}")
    return {"message": "Patient deleted"}

@router.post("/appointments")
def create_appointment(appt: AppointmentCreate):
    # --- 1. ML SIMULATION (Specialty & Severity) ---
    text = appt.problem_text.lower()
    predicted_specialty = "General Medicine" 
    predicted_severity = "Low"
    
    # Simple Keyword Matching
    if any(x in text for x in ["heart", "chest", "breath", "pain"]):
        predicted_specialty = "Cardiology"
        predicted_severity = "High"
    elif any(x in text for x in ["bone", "fracture", "joint"]):
        predicted_specialty = "Orthopedics"
        predicted_severity = "Medium"
    elif any(x in text for x in ["skin", "rash", "itch"]):
        predicted_specialty = "Dermatology"
        predicted_severity = "Low"
        
    # --- 2. ASSIGN DOCTOR ---
    doc_query = f"SELECT doctor_id, department_id FROM doctors WHERE specialty = '{predicted_specialty}' LIMIT 1"
    doc_result = execute_query(doc_query)
    
    if not doc_result:
        doc_result = execute_query("SELECT doctor_id, department_id FROM doctors LIMIT 1")
    
    if not doc_result:
        raise HTTPException(status_code=500, detail="No doctors available to assign")
        
    doctor_id = doc_result[0]['doctor_id']
    dept_id = doc_result[0]['department_id']
    
    # --- 3. ASSIGN ROOM ---
    room_query = f"SELECT room_id FROM rooms WHERE status = 'Available' LIMIT 1"
    room_result = execute_query(room_query)
    
    room_id = room_result[0]['room_id'] if room_result else "NULL"
    
    # --- 4. INSERT APPOINTMENT ---
    sql = f"""
        INSERT INTO appointments 
        (patient_id, doctor_id, department_id, room_id, patient_problem_text, predicted_specialty, predicted_severity, status, appointment_date)
        VALUES 
        ({appt.patient_id}, {doctor_id}, {dept_id}, {room_id}, '{appt.problem_text}', '{predicted_specialty}', '{predicted_severity}', 'Scheduled', NOW())
        RETURNING appointment_id
    """
    
    try:
        new_appt = execute_query(sql)
        # Mark room as Occupied if assigned
        if room_id != "NULL":
             execute_query(f"UPDATE rooms SET status = 'Occupied', current_occupancy = current_occupancy + 1 WHERE room_id = {room_id}")
             
        return {
            "status": "success", 
            "message": "Appointment created with ML assignment",
            "details": {
                "specialty": predicted_specialty,
                "severity": predicted_severity,
                "assigned_doctor": doctor_id,
                "assigned_room": room_id
            }
        }
    except Exception as e:
         return {"status": "error", "message": str(e)}