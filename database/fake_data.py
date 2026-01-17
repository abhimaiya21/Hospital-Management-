import random
import json
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker with Indian Locale
fake = Faker('en_IN')

# --- CONFIGURATION ---
NUM_PATIENTS = 100
OUTPUT_FILE = "hospital_seed_100.sql"
START_DATE = datetime(2024, 1, 1)
TODAY = datetime.today()

# --- DATA DICTIONARIES ---
DEPARTMENTS = [
    ("Cardiology", "CARD", "Heart related issues", ["Chest pain", "Palpitations"], 
     ["ECG", "Echo", "Troponin"], ["Aspirin", "Atorvastatin", "Metoprolol"]),
    ("Neurology", "NEURO", "Brain issues", ["Migraine", "Seizures"], 
     ["MRI Brain", "EEG", "CT Scan"], ["Paracetamol", "Topiramate", "Levetiracetam"]),
    ("Orthopedics", "ORTHO", "Bone issues", ["Fracture", "Joint pain"], 
     ["X-Ray", "MRI Knee", "Bone Density"], ["Ibuprofen", "Calcium", "Vitamin D"]),
    ("Pediatrics", "PEDS", "Child health", ["Fever", "Infection"], 
     ["CBC", "Urine Culture"], ["Amoxicillin", "Paracetamol syp", "Ibuprofen syp"]),
    ("Oncology", "ONCO", "Cancer treatment", ["Tumor", "Weight loss"], 
     ["Biopsy", "PET Scan", "Tumor Markers"], ["Tamoxifen", "Methotrexate", "Cisplatin"]),
    ("Dermatology", "DERM", "Skin care", ["Acne", "Rash"], 
     ["Skin Biopsy", "Allergy Test"], ["Benzoyl Peroxide", "Clindamycin", "Cetirizine"]),
    ("Gastroenterology", "GASTRO", "Digestion", ["Stomach pain", "Ulcers"], 
     ["Endoscopy", "Colonoscopy", "LFT"], ["Omeprazole", "Pantoprazole", "Probiotics"]),
    ("Gynecology", "GYNE", "Women's health", ["Pregnancy", "PCOS"], 
     ["Ultrasound", "Pap Smear", "Hormone Panel"], ["Folic Acid", "Iron", "Metformin"]),
    ("ENT", "ENT", "Ear Nose Throat", ["Sinusitis", "Ear pain"], 
     ["Audiometry", "Nasal Endoscopy"], ["Otrivin", "Cetirizine", "Augmentin"]),
    ("General Medicine", "GEN", "General health", ["Viral fever", "Weakness"], 
     ["CBC", "Typhoid Test", "Blood Sugar"], ["Paracetamol", "Multivitamins", "Azithromycin"])
]

ROOM_TYPES = ['General Ward', 'Private Room', 'ICU', 'Emergency']

def clean_str(s):
    if s is None: return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def random_date(start, end):
    delta = end - start
    if delta.days <= 0: return end
    return start + timedelta(days=random.randint(0, delta.days), hours=random.randint(0,23))

def generate_sql():
    sql = ["BEGIN;"]
    
    # 1. CLEANUP (Wipe all tables in correct dependency order)
    # We use RESTART IDENTITY to reset auto-increment counters, though we force IDs anyway for safety.
    sql.append("""
    TRUNCATE TABLE 
        lab_tests, prescriptions, invoices, allergies, medical_records, 
        admission_doctor_care, admissions, appointments, patient_doctor_mapping, 
        rooms, patients, doctors, departments, users 
    RESTART IDENTITY CASCADE;
    """)

    doc_ids = []   
    room_ids = []  
    patient_ids = []
    
    print("Generating Infrastructure...")
    
    # 2. USERS (Table 1) - Admin & Billing
    # Force IDs: 1=Admin, 2=Billing
    sql.append("INSERT INTO users (user_id, username, password, role) VALUES (1, 'admin', 'admin123', 'admin');")
    sql.append("INSERT INTO users (user_id, username, password, role) VALUES (2, 'billing', 'billing123', 'billing');")
    
    doc_counter = 1
    user_counter = 3
    
    # 3. DEPARTMENTS (Table 2) & DOCTORS (Table 3)
    # Note: We insert Departments first without head_doctor, then update later to avoid circular key issues.
    for i, (name, code, desc, sym, tests, meds) in enumerate(DEPARTMENTS, 1):
        safe_desc = desc.replace("'", "''")
        # Insert Department
        sql.append(f"INSERT INTO departments (department_id, department_name, department_code, floor_number, wing, description) VALUES ({i}, '{name}', '{code}', {random.randint(1,4)}, '{random.choice(['A','B','C'])}', '{safe_desc}');")
        
        dept_docs = []
        
        # Create 2 Doctors per Department
        for d in range(2):
            u_name = f"dr_{code.lower()}_{d+1}"
            
            # Create User for Doctor
            sql.append(f"INSERT INTO users (user_id, username, password, role) VALUES ({user_counter}, '{u_name}', 'pass123', 'doctor');")
            
            fee = random.choice([500, 800, 1000, 1500])
            seniority = "Senior" if d == 0 else "Junior"
            fname = fake.first_name()
            lname = fake.last_name()
            
            # Create Doctor linked to User and Department
            sql.append(f"INSERT INTO doctors (doctor_id, user_id, department_id, first_name, last_name, specialty, seniority_level, consultation_fee, email, is_available) VALUES ({doc_counter}, {user_counter}, {i}, '{fname}', '{lname}', '{name}', '{seniority}', {fee}, '{u_name}@hospital.com', TRUE);")
            
            doc_ids.append({"id": doc_counter, "dept_id": i, "fee": fee})
            dept_docs.append(doc_counter)
            
            doc_counter += 1
            user_counter += 1
        
        # Update Department Head (Set to first doctor of the department)
        sql.append(f"UPDATE departments SET head_doctor_id = {dept_docs[0]} WHERE department_id = {i};")

    # Sync sequences
    sql.append(f"SELECT setval('users_user_id_seq', {user_counter}, true);")
    sql.append(f"SELECT setval('doctors_doctor_id_seq', {doc_counter}, true);")
    sql.append(f"SELECT setval('departments_department_id_seq', {len(DEPARTMENTS)}, true);")

    # 4. ROOMS (Table 5)
    print("Generating Rooms...")
    r_counter = 1
    for floor in range(1, 5):
        for wing in ['A', 'B', 'C']:
            for num in range(1, 11): 
                r_type = random.choices(ROOM_TYPES, weights=[50, 30, 10, 10], k=1)[0]
                rate = {"General Ward": 1500, "Private Room": 4000, "ICU": 12000, "Emergency": 2500}[r_type]
                capacity = 1
                if r_type == 'General Ward': capacity = 6
                if r_type == 'ICU': capacity = 2
                r_num = f"{wing}-{floor}{num:02d}"
                
                # Start with 0 occupancy
                sql.append(f"INSERT INTO rooms (room_id, room_number, wing, floor_number, room_type, status, daily_rate, bed_capacity, current_occupancy) VALUES ({r_counter}, '{r_num}', '{wing}', {floor}, '{r_type}', 'Available', {rate}, {capacity}, 0);")
                room_ids.append({"id": r_counter, "type": r_type, "rate": rate, "number": r_num})
                r_counter += 1
    
    sql.append(f"SELECT setval('rooms_room_id_seq', {r_counter}, true);")

    # 5. PATIENTS (Table 4) & ALLERGIES (Table 11)
    print(f"Generating {NUM_PATIENTS} Patients...")
    for p in range(1, NUM_PATIENTS + 1):
        gender = random.choice(['Male', 'Female'])
        fname = fake.first_name_male() if gender=='Male' else fake.first_name_female()
        dob = fake.date_of_birth(minimum_age=10, maximum_age=80)
        phone = fake.phone_number()[:15]
        addr = clean_str(fake.address().replace("\n", ", "))
        ins = random.choice(['Star Health', 'HDFC Ergo', 'None', 'Ayushman Bharat'])
        bg = random.choice(['A+', 'B+', 'O+', 'AB-', 'O-'])
        
        sql.append(f"INSERT INTO patients (patient_id, first_name, last_name, dob, gender, blood_group, contact_number, address, insurance_provider) VALUES ({p}, '{fname}', '{fake.last_name()}', '{dob}', '{gender}', '{bg}', '{phone}', {addr}, '{ins}');")
        patient_ids.append(p)
        
        # Allergies
        if random.random() < 0.2:
            allergen = random.choice(['Peanuts', 'Penicillin', 'Dust', 'Pollen', 'Shellfish'])
            sql.append(f"INSERT INTO allergies (patient_id, allergen, severity, allergen_type) VALUES ({p}, '{allergen}', '{random.choice(['Mild', 'Severe'])}', 'Food');")

    sql.append(f"SELECT setval('patients_patient_id_seq', {NUM_PATIENTS}, true);")

    # 6. CLINICAL DATA (Remaining Tables)
    print("Generating Clinical Data...")
    appt_id_counter = 1
    admit_id_counter = 1
    
    for pat_id in patient_ids:
        # Each patient has 1 or 2 interactions
        for _ in range(random.randint(1, 2)):
            dept_idx = random.randint(0, 9)
            dept_data = DEPARTMENTS[dept_idx]
            
            # Find a doctor from this department
            possible_docs = [d for d in doc_ids if d['dept_id'] == (dept_idx + 1)]
            if not possible_docs: continue 
            doc = random.choice(possible_docs)
            
            visit_date = random_date(START_DATE, TODAY)
            symptom = random.choice(dept_data[3])
            prob_text = f"Patient complains of {symptom}"
            severity = random.choice(['Low', 'Medium', 'High'])
            
            # A. Appointments (Table 7)
            sql.append(f"INSERT INTO appointments (appointment_id, patient_id, doctor_id, department_id, appointment_date, patient_problem_text, predicted_specialty, predicted_severity, status) VALUES ({appt_id_counter}, {pat_id}, {doc['id']}, {doc['dept_id']}, '{visit_date}', '{prob_text}', '{dept_data[0]}', '{severity}', 'Completed');")
            curr_appt_id = appt_id_counter
            appt_id_counter += 1
            
            # B. Patient_Doctor_Mapping (Table 6)
            sql.append(f"INSERT INTO patient_doctor_mapping (patient_id, doctor_id, department_id, first_visit_date, is_primary_doctor) VALUES ({pat_id}, {doc['id']}, {doc['dept_id']}, '{visit_date.date()}', TRUE) ON CONFLICT (patient_id, doctor_id) DO NOTHING;")

            # C. Medical_Records (Table 10)
            vitals = json.dumps({"bp": "120/80", "temp": "98.6"})
            diagnosis = f"Acute {symptom} syndrome"
            sql.append(f"INSERT INTO medical_records (patient_id, doctor_id, department_id, appointment_id, diagnosis, vital_signs, record_date) VALUES ({pat_id}, {doc['id']}, {doc['dept_id']}, {curr_appt_id}, '{diagnosis}', '{vitals}', '{visit_date}');")
            
            # D. Lab_Tests (Table 14)
            lab_cost = 0
            if random.random() > 0.5:
                test_name = random.choice(dept_data[4])
                sql.append(f"INSERT INTO lab_tests (patient_id, doctor_id, appointment_id, test_name, test_category, ordered_date, status, results) VALUES ({pat_id}, {doc['id']}, {curr_appt_id}, '{test_name}', 'Pathology', '{visit_date}', 'Completed', 'Normal');")
                lab_cost = random.randint(500, 2000)

            # E. Prescriptions (Table 13)
            med_cost = 0
            if random.random() > 0.3:
                med_name = random.choice(dept_data[5])
                sql.append(f"INSERT INTO prescriptions (patient_id, doctor_id, appointment_id, medication_name, dosage, frequency, quantity) VALUES ({pat_id}, {doc['id']}, {curr_appt_id}, '{med_name}', '500mg', '1-0-1', 10);")
                med_cost = random.randint(200, 1000)

            # F. Invoices (Table 12) - OPD
            total_bill = doc['fee'] + lab_cost + med_cost
            sql.append(f"INSERT INTO invoices (patient_id, appointment_id, consultation_charges, lab_charges, medication_charges, total_amount, status, issue_date) VALUES ({pat_id}, {curr_appt_id}, {doc['fee']}, {lab_cost}, {med_cost}, {total_bill}, 'Paid', '{visit_date.date()}');")

            # G. Admissions (Table 8) & Care (Table 9)
            # Logic: Admitted if severity is Medium/High (30% chance)
            if severity in ['Medium', 'High'] and random.random() < 0.3:
                room = random.choice(room_ids)
                
                # Mixed Status Logic
                is_active = random.choice([True, False])
                
                if is_active:
                    status = 'Active' 
                    adm_date = TODAY - timedelta(days=random.randint(0, 3))
                    disch_val = "NULL"
                    # Update Room Status
                    sql.append(f"UPDATE rooms SET status = 'Occupied', current_occupancy = 1 WHERE room_id = {room['id']};")
                else:
                    status = 'Discharged'
                    adm_date = visit_date
                    stay_days = random.randint(2, 7)
                    actual_disch = adm_date + timedelta(days=stay_days)
                    disch_val = f"'{actual_disch.date()}'"

                sql.append(f"INSERT INTO admissions (admission_id, patient_id, primary_doctor_id, room_id, department_id, admission_date, actual_discharge_date, admission_reason, admission_type, status) VALUES ({admit_id_counter}, {pat_id}, {doc['id']}, {room['id']}, {doc['dept_id']}, '{adm_date}', {disch_val}, '{diagnosis}', 'Emergency', '{status}');")
                
                curr_admit_id = admit_id_counter
                admit_id_counter += 1
                
                sql.append(f"INSERT INTO admission_doctor_care (admission_id, doctor_id, department_id, role_in_care) VALUES ({curr_admit_id}, {doc['id']}, {doc['dept_id']}, 'Primary');")
                
                # Inpatient Invoice
                sql.append(f"INSERT INTO invoices (patient_id, admission_id, room_charges, total_amount, status, issue_date) VALUES ({pat_id}, {curr_admit_id}, 5000, 10000, 'Pending', '{adm_date.date()}');")

    # Sync sequences for tables where we manually set IDs
    sql.append(f"SELECT setval('appointments_appointment_id_seq', {appt_id_counter}, true);")
    sql.append(f"SELECT setval('admissions_admission_id_seq', {admit_id_counter}, true);")

    sql.append("COMMIT;")
    
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write("\n".join(sql))
    
    print(f"DONE! Generated 100 Patient Records (All 14 Tables) in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_sql()