#!/usr/bin/env python
import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/emergency-intake"

payload = {
    "first_name": "John",
    "last_name": "Doe",
    "dob": "1985-06-15",
    "gender": "Male",
    "contact_number": "9876543210",
    "problem_description": "Severe chest pain and difficulty breathing",
    "symptoms": "Chest pain and shortness of breath"
}

try:
    print("=" * 60)
    print("Testing Emergency Intake Endpoint")
    print("=" * 60)
    print(f"\n📍 API URL: {API_URL}")
    print(f"\n📝 Request Payload:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(API_URL, json=payload, timeout=10)
    
    print(f"\n✅ Status Code: {response.status_code}")
    print(f"\n📋 Response:")
    
    data = response.json()
    print(json.dumps(data, indent=2))
    
    # Extract key info
    print(f"\n" + "=" * 60)
    print("KEY INFORMATION FROM DATABASE:")
    print("=" * 60)
    print(f"Patient ID: {data.get('patient_id', 'N/A')}")
    print(f"Department: {data.get('predicted_department', 'N/A')}")
    print(f"Severity: {data.get('severity', 'N/A')}")
    
    if data.get('assigned_doctor'):
        print(f"\nDoctor Details:")
        print(f"  Name: {data['assigned_doctor'].get('full_name', 'N/A')}")
        print(f"  Status: {data['assigned_doctor'].get('status', 'N/A')}")
        print(f"  Room: {data['assigned_doctor'].get('room_number', 'N/A')}")
    
    if data.get('assigned_room'):
        print(f"\nRoom Details:")
        print(f"  Room Number: {data['assigned_room'].get('room_number', 'N/A')}")
        print(f"  Type: {data['assigned_room'].get('room_type', 'N/A')}")
        print(f"  Wing: {data['assigned_room'].get('wing', 'N/A')}")
        print(f"  Floor: {data['assigned_room'].get('floor', 'N/A')}")
        print(f"  Status: {data['assigned_room'].get('status', 'N/A')}")
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: Backend not reachable at {API_URL}")
    print(f"   Error: {str(e)}")
except requests.exceptions.Timeout:
    print(f"❌ Timeout Error: Request took too long")
except Exception as e:
    print(f"❌ Error: {str(e)}")
