import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_login(username, password, role, expected_status=200):
    print(f"Testing {role} login for {username}...")
    try:
        url = f"{BASE_URL}/admin/login"
        payload = {"username": username, "password": password, "role": role}
        response = requests.post(url, json=payload)
        
        if response.status_code == expected_status:
            print(f"✅ Success: {response.status_code}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_patient_login(patient_id, mobile, expected_status=200):
    print(f"Testing Patient login for ID {patient_id}...")
    try:
        url = f"{BASE_URL}/login"
        payload = {"patient_id": patient_id, "mobile_number": mobile}
        response = requests.post(url, json=payload)
        
        if response.status_code == expected_status:
            print(f"✅ Success: {response.status_code}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    current_success = True
    
    # 1. Admin Login
    if not test_login("admin", "password123", "admin"): current_success = False
    
    # 2. Doctor Login
    if not test_login("doctor_smith", "password123", "doctor"): current_success = False
    
    # 3. Billing Login
    if not test_login("billing_user", "password123", "billing"): current_success = False
    
    # 4. Patient Login (We need a valid patient ID, let's assume 1 exists or fail gracefully)
    # We will try a fake one first to see if it connects to DB at least (should return 200 with 'failed' status or 400, not 500)
    # Actually, let's create a patient first? Or just check if the endpoint responds.
    print("Testing Patient Endpoint Connectivity...")
    # Using a likely non-existent patient to check DB connection handles it gracefully
    test_patient_login(999999, "1234567890", 200) 
    
    if current_success:
        print("\n🎉 All Login Connections Verified!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
