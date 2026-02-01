import sys
sys.path.append('d:/projects/Hospital Management')

from backend.db import execute_query

# Check doctors
doctors = execute_query("SELECT COUNT(*) as count FROM doctors")
print(f"✅ Total Doctors: {doctors[0]['count']}")

# Check patients
patients = execute_query("SELECT COUNT(*) as count FROM patients")
print(f"✅ Total Patients: {patients[0]['count']}")

# Check departments
departments = execute_query("SELECT COUNT(*) as count FROM departments")
print(f"✅ Total Departments: {departments[0]['count']}")

# Check appointments
appointments = execute_query("SELECT COUNT(*) as count FROM appointments")
print(f"✅ Total Appointments: {appointments[0]['count']}")

print("\n📊 Sample Doctors:")
sample_docs = execute_query("SELECT first_name, last_name, specialty FROM doctors LIMIT 3")
for doc in sample_docs:
    print(f"   - Dr. {doc['first_name']} {doc['last_name']} ({doc['specialty']})")

print("\n📊 Sample Patients:")
sample_pats = execute_query("SELECT first_name, last_name FROM patients LIMIT 3")
for pat in sample_pats:
    print(f"   - {pat['first_name']} {pat['last_name']}")
