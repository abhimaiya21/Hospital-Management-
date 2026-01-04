import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(12345)  # Seed for reproducibility

# CONFIGURATION
NUM_RECORDS = 100
DOCTOR_ID_RANGE = (1, 20)   # Adjust if you have more/fewer doctors
PATIENT_ID_RANGE = (1, 100) # Since we are creating 100 new patients, IDs will be 1-100 (after truncation)

output_file = "insert_fresh_data.sql"

# Tracking sets to ensure uniqueness where required
generated_emails = set()
generated_usernames = set()

def generate_sql():
    with open(output_file, "w") as f:
        f.write("-- FRESH FAKE DATA GENERATION\n")
        f.write("BEGIN;\n\n")

        # ---------------------------------------
        # 1. GENERATE PATIENTS (100 rows)
        # ---------------------------------------
        f.write("-- 1. PATIENTS \n")
        print(f"Generating {NUM_RECORDS} Patients...")
        
        insurers = ['United Health', 'Aetna', 'Star Health', 'ICICI Lombard', 'Blue Cross', 'Medicare', 'Cigna', 'None']
        genders = ['Male', 'Female', 'Other']

        for _ in range(NUM_RECORDS):
            f_name = fake.first_name().replace("'", "''")
            l_name = fake.last_name().replace("'", "''")
            dob = fake.date_of_birth(minimum_age=1, maximum_age=90)
            gender = random.choice(genders)
            phone = fake.phone_number()[:15]
            addr = fake.address().replace("\n", ", ").replace("'", "''")
            ins = random.choice(insurers)

            sql = f"INSERT INTO patients (first_name, last_name, dob, gender, contact_number, address, insurance_provider) VALUES ('{f_name}', '{l_name}', '{dob}', '{gender}', '{phone}', '{addr}', '{ins}');\n"
            f.write(sql)
        
        f.write("\n")

        # ---------------------------------------
        # 2. GENERATE APPOINTMENTS
        # ---------------------------------------
        f.write("-- 2. APPOINTMENTS \n")
        print(f"Generating {NUM_RECORDS} Appointments...")
        
        statuses = ['Scheduled', 'Completed', 'Cancelled']
        
        for _ in range(NUM_RECORDS):
            # We assume patient IDs 1 to 100 exist because we just created them
            pid = random.randint(1, NUM_RECORDS) 
            did = random.randint(*DOCTOR_ID_RANGE)
            appt_date = fake.date_time_between(start_date='-1y', end_date='+30d')
            room = f"R-{random.randint(100, 599)}"
            reason = fake.sentence(nb_words=6).replace("'", "''")
            status = random.choice(statuses)

            sql = f"INSERT INTO appointments (patient_id, doctor_id, appointment_date, room_number, reason_for_visit, status) VALUES ({pid}, {did}, '{appt_date}', '{room}', '{reason}', '{status}');\n"
            f.write(sql)
            
        f.write("\n")

        # ---------------------------------------
        # 3. GENERATE MEDICAL RECORDS
        # ---------------------------------------
        f.write("-- 3. MEDICAL RECORDS \n")
        print(f"Generating {NUM_RECORDS} Medical Records...")
        
        diagnoses = ['Hypertension', 'Diabetes Type 2', 'Viral Fever', 'Migraine', 'Fracture', 'Asthma', 'Bronchitis', 'Anemia', 'Gastritis', 'Covid-19', 'Pneumonia', 'Arthritis']
        
        for _ in range(NUM_RECORDS):
            pid = random.randint(1, NUM_RECORDS)
            did = random.randint(*DOCTOR_ID_RANGE)
            diag = random.choice(diagnoses)
            plan = fake.sentence(nb_words=10).replace("'", "''")
            r_date = fake.date_between(start_date='-1y', end_date='today')

            sql = f"INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES ({pid}, {did}, '{diag}', '{plan}', '{r_date}');\n"
            f.write(sql)
            
        f.write("\n")

        # ---------------------------------------
        # 4. GENERATE ALLERGIES
        # ---------------------------------------
        f.write("-- 4. ALLERGIES \n")
        print(f"Generating {NUM_RECORDS} Allergies...")
        
        allergens = ['Peanuts', 'Dust', 'Pollen', 'Penicillin', 'Shellfish', 'Latex', 'Milk', 'Soy', 'Eggs', 'Bee Stings']
        severities = ['Mild', 'Moderate', 'Severe', 'Life-Threatening']
        
        for _ in range(NUM_RECORDS):
            pid = random.randint(1, NUM_RECORDS)
            allergen = random.choice(allergens)
            severity = random.choice(severities)

            sql = f"INSERT INTO allergies (patient_id, allergen, severity) VALUES ({pid}, '{allergen}', '{severity}');\n"
            f.write(sql)
            
        f.write("\n")

        # ---------------------------------------
        # 5. GENERATE INVOICES
        # ---------------------------------------
        f.write("-- 5. INVOICES \n")
        print(f"Generating {NUM_RECORDS} Invoices...")
        
        inv_statuses = ['Paid', 'Unpaid', 'Pending']
        
        for _ in range(NUM_RECORDS):
            pid = random.randint(1, NUM_RECORDS)
            amount = round(random.uniform(50.00, 20000.00), 2)
            status = random.choice(inv_statuses)
            i_date = fake.date_between(start_date='-6m', end_date='today')

            sql = f"INSERT INTO invoices (patient_id, amount, status, issue_date) VALUES ({pid}, {amount}, '{status}', '{i_date}');\n"
            f.write(sql)

        f.write("\nCOMMIT;\n")
        print(f"✅ DONE! SQL saved to {output_file}")

if __name__ == "__main__":
    generate_sql()