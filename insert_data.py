import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)  # Ensures consistent results every time you run it

# Configuration
NUM_PATIENTS = 50
NUM_DOCTORS = 10
NUM_APPOINTMENTS = 100
NUM_RECORDS = 80
NUM_ALLERGIES = 30

def generate_sql_file():
    print("Generating SQL data...")
    
    with open("insert_data.sql", "w") as f:
        
        # 1. Generate Doctors
        specialties = ['Cardiology', 'Pediatrics', 'Neurology', 'General Practice', 'Oncology', 'Dermatology']
        doctor_ids = list(range(1, NUM_DOCTORS + 1))
        
        f.write("-- INSERT DOCTORS\n")
        for i in doctor_ids:
            name = fake.name()
            spec = random.choice(specialties)
            email = f"{name.replace(' ', '.').lower()}@hospital.com"
            f.write(f"INSERT INTO doctors (full_name, specialty, email) VALUES ('Dr. {name}', '{spec}', '{email}');\n")
            
        # 2. Generate Patients
        patient_ids = list(range(1, NUM_PATIENTS + 1))
        
        f.write("\n-- INSERT PATIENTS\n")
        for i in patient_ids:
            name = fake.name()
            dob = fake.date_of_birth(minimum_age=1, maximum_age=90)
            gender = random.choice(['Male', 'Female'])
            phone = fake.phone_number()[:15] # Truncate to fit
            addr = fake.address().replace('\n', ', ')
            f.write(f"INSERT INTO patients (full_name, dob, gender, contact_number, address) VALUES ('{name}', '{dob}', '{gender}', '{phone}', '{addr}');\n")

        # 3. Generate Allergies (Crucial for your 'Medical Error' scenario)
        common_allergens = ['Penicillin', 'Peanuts', 'Latex', 'Shellfish', 'Dust Mites', 'Pollen', 'Sulfa Drugs']
        severities = ['Mild', 'Moderate', 'Severe', 'Life-Threatening']
        
        f.write("\n-- INSERT ALLERGIES\n")
        for _ in range(NUM_ALLERGIES):
            pid = random.choice(patient_ids)
            allergen = random.choice(common_allergens)
            severity = random.choice(severities)
            f.write(f"INSERT INTO allergies (patient_id, allergen, severity) VALUES ({pid}, '{allergen}', '{severity}');\n")

        # 4. Generate Appointments (Linking Doctors and Patients)
        f.write("\n-- INSERT APPOINTMENTS\n")
        for _ in range(NUM_APPOINTMENTS):
            pid = random.choice(patient_ids)
            did = random.choice(doctor_ids)
            # Random date within last year
            appt_date = fake.date_time_between(start_date='-1y', end_date='now')
            reason = fake.sentence(nb_words=6)
            status = random.choice(['Scheduled', 'Completed', 'Cancelled', 'No Show'])
            f.write(f"INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason_for_visit, status) VALUES ({pid}, {did}, '{appt_date}', '{reason}', '{status}');\n")

        # 5. Generate Medical Records
        f.write("\n-- INSERT MEDICAL RECORDS\n")
        for _ in range(NUM_RECORDS):
            pid = random.choice(patient_ids)
            did = random.choice(doctor_ids)
            diagnosis = fake.sentence(nb_words=4)
            treatment = fake.sentence(nb_words=8)
            rec_date = fake.date_between(start_date='-1y', end_date='today')
            f.write(f"INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment_plan, record_date) VALUES ({pid}, {did}, '{diagnosis}', '{treatment}', '{rec_date}');\n")

    print("Done! 'insert_data.sql' created successfully.")

if __name__ == "__main__":
    generate_sql_file()