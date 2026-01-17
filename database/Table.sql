DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS allergies CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS patients CASCADE;
DROP TABLE IF EXISTS doctors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;



-- 1. USERS TABLE (Authentication System)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('doctor', 'billing', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. DEPARTMENTS TABLE (Hospital Structure)
-- Exactly 10 major departments, each with 2 doctors minimum
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) UNIQUE NOT NULL,
    department_code VARCHAR(10) UNIQUE NOT NULL,
    floor_number INT NOT NULL CHECK (floor_number BETWEEN 1 AND 4),
    wing VARCHAR(5) NOT NULL CHECK (wing IN ('A', 'B', 'C')),
    head_doctor_id INT,
    total_beds INT DEFAULT 0,
    description TEXT,
    contact_extension VARCHAR(10)
);

-- 3. DOCTORS TABLE (Resource Management)
-- Minimum 20 doctors (2 per department), linked to departments and users
CREATE TABLE doctors (
    doctor_id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(user_id),
    department_id INT NOT NULL REFERENCES departments(department_id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialty VARCHAR(50) NOT NULL,
    seniority_level VARCHAR(20) NOT NULL CHECK (seniority_level IN ('Junior', 'Senior', 'Consultant')),
    qualification VARCHAR(100), -- e.g., 'MBBS, MD (Cardiology)'
    experience_years INT DEFAULT 0,
    current_workload INT DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    phone_contact VARCHAR(15),
    email VARCHAR(100) UNIQUE NOT NULL,
    doctor_room_number VARCHAR(10) UNIQUE, -- Ground floor cabin (G-001 to G-050)
    consultation_fee DECIMAL(8, 2) DEFAULT 500.00,
    languages_spoken VARCHAR(200) -- e.g., 'Hindi, English, Tamil'
);

-- Add foreign key for department head
ALTER TABLE departments 
ADD CONSTRAINT fk_head_doctor 
FOREIGN KEY (head_doctor_id) REFERENCES doctors(doctor_id);

-- 4. PATIENTS TABLE (Supports ~1000 patients with Indian demographics)
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE NOT NULL,
    gender VARCHAR(10) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    blood_group VARCHAR(5) CHECK (blood_group IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')),
    contact_number VARCHAR(15) NOT NULL,
    emergency_contact VARCHAR(15),
    emergency_contact_name VARCHAR(100),
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    insurance_provider VARCHAR(100),
    insurance_number VARCHAR(50),
    registered_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- 5. ROOMS TABLE (Structured Wing-based Allocation)
-- Total: 240 patient rooms (60 per floor × 4 floors) + 50 ground floor rooms
CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    wing VARCHAR(10) NOT NULL CHECK (wing IN ('A', 'B', 'C', 'Ground')),
    floor_number INT NOT NULL CHECK (floor_number BETWEEN 0 AND 4),
    room_type VARCHAR(30) NOT NULL CHECK (room_type IN (
        'General Ward', 
        'Private Room', 
        'ICU', 
        'Emergency',
        'Operating Theater',
        'Doctor Cabin',
        'Consultation Room',
        'Observation Room'
    )),
    department_id INT REFERENCES departments(department_id),
    bed_capacity INT DEFAULT 1 CHECK (bed_capacity BETWEEN 1 AND 6),
    current_occupancy INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Available' CHECK (status IN ('Available', 'Occupied', 'Maintenance', 'Cleaning')),
    amenities TEXT,
    has_ac BOOLEAN DEFAULT FALSE,
    has_attached_bathroom BOOLEAN DEFAULT FALSE,
    daily_rate DECIMAL(8, 2),
    CONSTRAINT valid_occupancy CHECK (current_occupancy <= bed_capacity)
);

-- 6. PATIENT_DOCTOR_MAPPING TABLE (Many-to-Many Relationship)
-- Allows patients to visit multiple doctors across departments
CREATE TABLE patient_doctor_mapping (
    mapping_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    department_id INT NOT NULL REFERENCES departments(department_id),
    first_visit_date DATE DEFAULT CURRENT_DATE,
    last_visit_date DATE,
    total_visits INT DEFAULT 1,
    is_primary_doctor BOOLEAN DEFAULT FALSE, -- One primary doctor per patient
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Transferred')),
    notes TEXT,
    UNIQUE(patient_id, doctor_id)
);

-- 7. APPOINTMENTS TABLE (AI-Powered Scheduling)
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    department_id INT NOT NULL REFERENCES departments(department_id),
    room_id INT REFERENCES rooms(room_id),
    
    appointment_date TIMESTAMP NOT NULL,
    scheduled_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INT DEFAULT 30,
    
    -- Patient Input
    patient_problem_text TEXT NOT NULL,
    symptoms TEXT,
    
    -- ML Predictions
    predicted_specialty VARCHAR(50),
    predicted_severity VARCHAR(20) CHECK (predicted_severity IN ('Low', 'Medium', 'High', 'Critical', 'Emergency')),
    confidence_score DECIMAL(5, 4), -- 0.0000 to 1.0000
    
    -- Explainable AI (XAI)
    ai_justification TEXT,
    keywords_detected TEXT,
    
    appointment_type VARCHAR(30) CHECK (appointment_type IN ('Consultation', 'Follow-up', 'Emergency', 'Surgery', 'Checkup')),
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'Admitted', 'In-Progress', 'No-Show')),
    
    cancellation_reason TEXT,
    notes TEXT
);

-- 8. ADMISSIONS TABLE (Inpatient Tracking)
CREATE TABLE admissions (
    admission_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    primary_doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    room_id INT NOT NULL REFERENCES rooms(room_id),
    department_id INT NOT NULL REFERENCES departments(department_id),
    
    admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_discharge_date DATE,
    actual_discharge_date TIMESTAMP,
    
    admission_reason TEXT NOT NULL,
    admission_type VARCHAR(20) CHECK (admission_type IN ('Emergency', 'Planned', 'Transfer')),
    admission_source VARCHAR(30) CHECK (admission_source IN ('Emergency', 'OPD', 'Referral', 'Direct')),
    
    bed_number VARCHAR(10),
    
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Discharged', 'Transferred', 'Deceased')),
    discharge_summary TEXT
);

-- 9. ADMISSION_DOCTOR_CARE TABLE (Multiple doctors treating one admission)
-- Allows collaborative care across departments
CREATE TABLE admission_doctor_care (
    care_id SERIAL PRIMARY KEY,
    admission_id INT NOT NULL REFERENCES admissions(admission_id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    department_id INT NOT NULL REFERENCES departments(department_id),
    care_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    care_end_date TIMESTAMP,
    role_in_care VARCHAR(50), -- e.g., 'Primary', 'Consultant', 'Specialist'
    notes TEXT,
    UNIQUE(admission_id, doctor_id)
);

-- 10. MEDICAL_RECORDS TABLE (Clinical Documentation)
CREATE TABLE medical_records (
    record_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    department_id INT REFERENCES departments(department_id),
    appointment_id INT REFERENCES appointments(appointment_id),
    admission_id INT REFERENCES admissions(admission_id),
    
    diagnosis TEXT NOT NULL,
    symptoms_observed TEXT,
    treatment_plan TEXT,
    medications_prescribed TEXT,
    lab_tests_ordered TEXT,
    
    vital_signs JSONB, -- {"bp": "120/80", "temp": "98.6", "pulse": "72", "spo2": "98"}
    
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    clinical_notes TEXT
);

-- 11. ALLERGIES TABLE (Patient Safety)
CREATE TABLE allergies (
    allergy_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    allergen VARCHAR(100) NOT NULL,
    allergen_type VARCHAR(30) CHECK (allergen_type IN ('Drug', 'Food', 'Environmental', 'Other')),
    severity VARCHAR(20) CHECK (severity IN ('Mild', 'Moderate', 'Severe', 'Life-Threatening')),
    reaction_description TEXT,
    diagnosed_date DATE,
    diagnosed_by INT REFERENCES doctors(doctor_id)
);

-- 12. INVOICES TABLE (Billing System)
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    appointment_id INT REFERENCES appointments(appointment_id),
    admission_id INT REFERENCES admissions(admission_id),
    
    consultation_charges DECIMAL(10, 2) DEFAULT 0,
    room_charges DECIMAL(10, 2) DEFAULT 0,
    medication_charges DECIMAL(10, 2) DEFAULT 0,
    lab_charges DECIMAL(10, 2) DEFAULT 0,
    surgery_charges DECIMAL(10, 2) DEFAULT 0,
    other_charges DECIMAL(10, 2) DEFAULT 0,
    
    subtotal DECIMAL(10, 2) GENERATED ALWAYS AS (
        consultation_charges + room_charges + medication_charges + 
        lab_charges + surgery_charges + other_charges
    ) STORED,
    
    tax_percentage DECIMAL(5, 2) DEFAULT 5.00,
    tax_amount DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2),
    
    insurance_claim_amount DECIMAL(10, 2) DEFAULT 0,
    patient_payable DECIMAL(10, 2),
    amount_paid DECIMAL(10, 2) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'Unpaid' CHECK (status IN ('Paid', 'Unpaid', 'Pending', 'Partial', 'Insurance-Claim')),
    issue_date DATE DEFAULT CURRENT_DATE,
    due_date DATE,
    payment_date TIMESTAMP,
    payment_mode VARCHAR(20) CHECK (payment_mode IN ('Cash', 'Card', 'UPI', 'Net Banking', 'Insurance'))
);

-- 13. PRESCRIPTIONS TABLE (Medication Tracking)
CREATE TABLE prescriptions (
    prescription_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    appointment_id INT REFERENCES appointments(appointment_id),
    admission_id INT REFERENCES admissions(admission_id),
    
    medication_name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(50),
    quantity INT,
    
    instructions TEXT,
    prescribed_date DATE DEFAULT CURRENT_DATE,
    refills_allowed INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- 14. LAB_TESTS TABLE (Diagnostic Tracking)
CREATE TABLE lab_tests (
    test_id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(patient_id),
    doctor_id INT NOT NULL REFERENCES doctors(doctor_id),
    appointment_id INT REFERENCES appointments(appointment_id),
    admission_id INT REFERENCES admissions(admission_id),
    
    test_name VARCHAR(200) NOT NULL,
    test_type VARCHAR(50),
    test_category VARCHAR(50) CHECK (test_category IN ('Blood', 'Urine', 'Imaging', 'Pathology', 'Radiology', 'Other')),
    ordered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sample_collected_date TIMESTAMP,
    
    results TEXT,
    results_date TIMESTAMP,
    normal_range VARCHAR(100),
    abnormal_flag BOOLEAN DEFAULT FALSE,
    
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Sample Collected', 'In Progress', 'Completed', 'Cancelled')),
    technician_notes TEXT
);

TRUNCATE TABLE 
    invoices, 
    allergies, 
    medical_records, 
    appointments, 
    patients, 
    doctors, 
    rooms, 
    users
RESTART IDENTITY CASCADE;

INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

SELECT * FROM appointments WHERE appointment_date = CURRENT_DATE;
