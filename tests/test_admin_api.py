import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1/admin"

print("🧪 Testing Admin API Endpoints\n")
print("=" * 60)

# Test 1: Analytics
print("\n1️⃣  Testing GET /api/v1/admin/analytics")
try:
    response = requests.get(f"{BASE_URL}/analytics")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS!")
        print(f"   - Doctors: {data.get('counts', {}).get('doctors', 'N/A')}")
        print(f"   - Patients: {data.get('counts', {}).get('patients', 'N/A')}")
        print(f"   - Active Today: {data.get('summary', {}).get('active_today', 'N/A')}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Get Doctors
print("\n2️⃣  Testing GET /api/v1/admin/doctors")
try:
    response = requests.get(f"{BASE_URL}/doctors")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        doctors = response.json()
        print(f"   ✅ SUCCESS! Found {len(doctors)} doctors")
        if len(doctors) > 0:
            doc = doctors[0]
            print(f"   Sample: Dr. {doc.get('first_name')} {doc.get('last_name')} - {doc.get('specialty')}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Get Patients
print("\n3️⃣  Testing GET /api/v1/admin/patients")
try:
    response = requests.get(f"{BASE_URL}/patients")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        patients = response.json()
        print(f"   ✅ SUCCESS! Found {len(patients)} patients")
        if len(patients) > 0:
            pat = patients[0]
            print(f"   Sample: {pat.get('first_name')} {pat.get('last_name')} - Age {pat.get('age')}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 4: Get Departments
print("\n4️⃣  Testing GET /api/v1/admin/departments")
try:
    response = requests.get(f"{BASE_URL}/departments")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        depts = response.json()
        print(f"   ✅ SUCCESS! Found {len(depts)} departments")
        if len(depts) > 0:
            print(f"   Sample departments: {', '.join([d['department_name'] for d in depts[:3]])}")
    else:
        print(f"   ❌ FAILED: {response.text}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("✅ All API endpoints tested!")
print("📝 Now refresh the admin page in browser to see the data")
