#!/usr/bin/env python
import requests

response = requests.get('http://127.0.0.1:8000/api/v1/admin/patients')
data = response.json()

print('Recent Patients with Room & Doctor Info:')
print('=' * 80)
for p in data[:10]:
    print(f"ID: {p['patient_id']:3d} | Name: {p['first_name']:10s} {p['last_name']:10s} | Doctor: {p.get('assigned_doctor', 'N/A'):20s} | Room: {p.get('room_no', 'N/A')}")
