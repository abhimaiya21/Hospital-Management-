"""
COMPREHENSIVE VALIDATION TEST SUITE - ALL PHASES
Hospital AI Triage System Production Readiness Assessment
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

class TestResults:
    def __init__(self):
        self.results = []
        self.phase_status = {}
    
    def add(self, phase, category, test_name, status, details=""):
        self.results.append({
            "phase": phase,
            "category": category,
            "test": test_name,
            "status": status,
            "details": details
        })
    
    def print_summary(self):
        print("\n" + "=" * 100)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 100)
        
        phases = {}
        for r in self.results:
            phase_key = r['phase']
            if phase_key not in phases:
                phases[phase_key] = {"pass": 0, "fail": 0, "total": 0}
            phases[phase_key]["total"] += 1
            if r['status'] == "✅":
                phases[phase_key]["pass"] += 1
            else:
                phases[phase_key]["fail"] += 1
        
        for phase, stats in phases.items():
            status = "✅ PASS" if stats["fail"] == 0 else "❌ FAIL"
            print(f"\n{status} {phase}: {stats['pass']}/{stats['total']} tests passed")
            
        print("\n" + "=" * 100)
        print("DETAILED RESULTS")
        print("=" * 100)
        
        current_phase = None
        for r in self.results:
            if r['phase'] != current_phase:
                print(f"\n=== {r['phase']} ===")
                current_phase = r['phase']
            print(f"{r['status']} [{r['category']}] {r['test']}")
            if r['details'] and r['status'] == "❌":
                print(f"    Details: {r['details'][:200]}")
        
        # Final verdict
        total_pass = sum(p["pass"] for p in phases.values())
        total_tests = sum(p["total"] for p in phases.values())
        total_fail = sum(p["fail"] for p in phases.values())
        
        print("\n" + "=" * 100)
        print(f"OVERALL: {total_pass}/{total_tests} tests passed, {total_fail} failures")
        
        if total_fail == 0:
            print("🎉 VERDICT: SYSTEM PRODUCTION READY ✅")
        else:
            print(f"⚠️  VERDICT: {total_fail} BLOCKERS IDENTIFIED - REQUIRES FIXES ❌")
        print("=" * 100)

tr = TestResults()

def test_api(phase, category, test_name, method, endpoint, data=None, expected_status=200, validate_fn=None):
    """Generic API test function with optional validation"""
    try:
        url = f"{API_V1}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        if response.status_code != expected_status:
            tr.add(phase, category, test_name, "❌", f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}")
            return None
        
        # Additional validation
        if validate_fn:
            resp_data = response.json()
            validation_result = validate_fn(resp_data)
            if validation_result is not True:
                tr.add(phase, category, test_name, "❌", f"Validation failed: {validation_result}")
                return None
        
        tr.add(phase, category, test_name, "✅", f"Status {response.status_code}")
        return response.json() if response.headers.get('content-type', '').startswith('application/json') else response
        
    except requests.exceptions.Timeout:
        tr.add(phase, category, test_name, "❌", "Request timeout (>10s)")
        return None
    except Exception as e:
        tr.add(phase, category, test_name, "❌", f"Exception: {str(e)}")
        return None

# ===============================================
# PHASE 1: MODEL CONFIDENCE SCORING
# ===============================================
print("\n" + "=" * 100)
print("PHASE 1: MODEL CONFIDENCE SCORING")
print("=" * 100)

# Test 1.1: High confidence rule-based case
response = test_api("PHASE 1", "Model Confidence", "High confidence (bike accident)", "POST", "/triage/analyze",
    {"symptoms": "Bike accident fracture leg cannot walk", "age": 45},
    validate_fn=lambda r: True if r.get('severity') == 'HIGH' and r.get('medical_category') == 'Orthopedics' else "Wrong classification")

# Test 1.2: Ambiguous case triggering ML
response = test_api("PHASE 1", "Model Confidence", "Ambiguous case (ML fallback)", "POST", "/triage/analyze",
    {"symptoms": "Not feeling well today", "age": 30},
    validate_fn=lambda r: True if r.get('explainability', {}).get('key_keywords') else "Missing key_keywords in explainability")

# Test 1.3: REFER case
response = test_api("PHASE 1", "Model Confidence", "REFER case (eye cataract)", "POST", "/triage/analyze",
    {"symptoms": "Eye cataract vision blurry", "age": 65},
    validate_fn=lambda r: True if r.get('status') == 'REFER' and r.get('assigned_doctor') == 'None' else "Wrong REFER handling")

# ===============================================
# PHASE 2: CRUD OPERATIONS VALIDATION
# ===============================================
print("\n" + "=" * 100)
print("PHASE 2: CRUD OPERATIONS VALIDATION")
print("=" * 100)

# Triage CRUD
test_api("PHASE 2", "Triage CRUD", "Create triage (analyze)", "POST", "/triage/analyze",
    {"symptoms": "Severe chest pain radiating to left arm", "age": 55})

test_api("PHASE 2", "Triage CRUD", "Batch triage", "POST", "/triage/batch",
    {"cases": [
        {"symptoms": "Fever and cough for 3 days now", "age": 10},
        {"symptoms": "Severe fracture from accident", "age": 40}
    ]})

test_api("PHASE 2", "Triage CRUD", "Read departments", "GET", "/triage/departments",
    validate_fn=lambda r: True if len(r.get('available_departments', {})) == 10 else f"Expected 10 departments, got {len(r.get('available_departments', {}))}")

# Admin CRUD
test_api("PHASE 2", "Admin CRUD", "Read analytics", "GET", "/admin/analytics")
test_api("PHASE 2", "Admin CRUD", "Read all doctors", "GET", "/admin/doctors",
    validate_fn=lambda r: True if isinstance(r, list) else "Expected list of doctors")

# Doctor CRUD
test_api("PHASE 2", "Doctor CRUD", "Read analytics", "GET", "/doctor/analytics")
test_api("PHASE 2", "Doctor CRUD", "Read patients", "GET", "/doctor/patients",
    validate_fn=lambda r: True if isinstance(r, list) else "Expected list of patients")

# Billing CRUD
test_api("PHASE 2", "Billing CRUD", "Read analytics", "GET", "/billing/analytics")

# ===============================================
# PHASE 3: END-TO-END INTEGRATION FLOW
# ===============================================
print("\n" + "=" * 100)
print("PHASE 3: END-TO-END INTEGRATION FLOW")
print("=" * 100)

# Test 3.1: Complete patient journey with Kannada input
test_api("PHASE 3", "Integration", "Triage with Kannada (bike accident)", "POST", "/triage/analyze",
    {"symptoms": "ಅಪಘಾತ ಎಲುಬು ಮುರಿತ ಕಾಲು ನೋವು", "age": 45},
    validate_fn=lambda r: True if 'explanation_kn' in r.get('explainability', {}) else "Missing Kannada explanation")

# Test 3.2: Hindi input
test_api("PHASE 3", "Integration", "Triage with Hindi (chest pain)", "POST", "/triage/analyze",
    {"symptoms": "छाती में तेज दर्द बाएं हाथ में फैल रहा है", "age": 55},
    validate_fn=lambda r: True if 'explanation_hi' in r.get('explainability', {}) else "Missing Hindi explanation")

# Test 3.3: English with room allocation
test_api("PHASE 3", "Integration", "High severity room allocation", "POST", "/triage/analyze",
    {"symptoms": "Severe trauma accident multiple fractures unconscious", "age": 35},
    validate_fn=lambda r: True if r.get('room_allotted') == 'Emergency / ICU' else f"Expected Emergency/ICU, got {r.get('room_allotted')}")

# ===============================================
# PHASE 4: STRICT CONSTRAINT VALIDATION
# ===============================================
print("\n" + "=" * 100)
print("PHASE 4: STRICT CONSTRAINT VALIDATION")
print("=" * 100)

# Test 4.1: 10 department enforcement
response = test_api("PHASE 4", "Constraints", "10 departments only", "GET", "/triage/departments")
if response:
    depts = response.get('available_departments', {})
    expected = {'Cardiology', 'Orthopedics', 'Pediatrics', 'General Medicine', 'ENT', 
                'Gynecology', 'Dermatology', 'Neurology', 'Emergency Medicine', 'Gastroenterology'}
    actual = set(depts.keys())
    if actual == expected:
        tr.add("PHASE 4", "Constraints", "Department list validation", "✅", "All 10 correct departments")
    else:
        tr.add("PHASE 4", "Constraints", "Department list validation", "❌", f"Expected {expected}, got {actual}")

# Test 4.2: Severity rule enforcement (accident always HIGH)
test_api("PHASE 4", "Constraints", "Accident severity rule", "POST", "/triage/analyze",
    {"symptoms": "Minor accident small bruise", "age": 25},
    validate_fn=lambda r: True if r.get('severity') == 'HIGH' else f"Accident must be HIGH, got {r.get('severity')}")

# Test 4.3: Pediatric rule (age < 14)
test_api("PHASE 4", "Constraints", "Pediatric age rule", "POST", "/triage/analyze",
    {"symptoms": "Fever and cough in child", "age": 8},
    validate_fn=lambda r: True if r.get('medical_category') == 'Pediatrics' else f"Expected Pediatrics, got {r.get('medical_category')}")

# Test 4.4: Pediatric exception (female + menstrual)
test_api("PHASE 4", "Constraints", "Pediatric exception (gynec)", "POST", "/triage/analyze",
    {"symptoms": "Menstrual cramps severe pain", "age": 12, "gender": "female"},
    validate_fn=lambda r: True if r.get('medical_category') == 'Gynecology' else f"Expected Gynecology, got {r.get('medical_category')}")

# Test 4.5: Trilingual output
response = test_api("PHASE 4", "Constraints", "Trilingual output validation", "POST", "/triage/analyze",
    {"symptoms": "Heart attack symptoms", "age": 60})
if response:
    exp = response.get('explainability', {})
    if all(k in exp for k in ['explanation_en', 'explanation_kn', 'explanation_hi']):
        tr.add("PHASE 4", "Constraints", "Trilingual check", "✅", "All 3 languages present")
    else:
        tr.add("PHASE 4", "Constraints", "Trilingual check", "❌", f"Missing languages in: {list(exp.keys())}")

# ===============================================
# PHASE 5: BATCH PROCESSING & STRESS TESTING
# ===============================================
print("\n" + "=" * 100)
print("PHASE 5: BATCH PROCESSING & STRESS TESTING")
print("=" * 100)

# Test 5.1: Batch of 50 patients
batch_cases = [
    {"symptoms": f"Patient {i} with various symptoms like fever cough headache", "age": 20 + (i % 60)}
    for i in range(50)
]
test_api("PHASE 5", "Stress Test", "Batch 50 patients", "POST", "/triage/batch",
    {"cases": batch_cases},
    validate_fn=lambda r: True if len(r) == 50 else f"Expected 50 results, got {len(r)}")

# Test 5.2: Edge case - minimum valid symptoms
test_api("PHASE 5", "Edge Cases", "Minimum symptoms (10 chars)", "POST", "/triage/analyze",
    {"symptoms": "fever cold", "age": 30})

# Test 5.3: Edge case - very long symptoms
test_api("PHASE 5", "Edge Cases", "Very long symptoms (1000 chars)", "POST", "/triage/analyze",
    {"symptoms": "severe pain " * 100, "age": 40})

# Test 5.4: Edge case - age boundaries
test_api("PHASE 5", "Edge Cases", "Age boundary (0)", "POST", "/triage/analyze",
    {"symptoms": "newborn breathing issues", "age": 0})

test_api("PHASE 5", "Edge Cases", "Age boundary (120)", "POST", "/triage/analyze",
    {"symptoms": "elderly patient weakness", "age": 120})

# Test 5.5: Concurrent requests simulation
print("Testing concurrent requests (10 sequential)...")
start_time = time.time()
for i in range(10):
    test_api("PHASE 5", "Concurrency", f"Request {i+1}/10", "POST", "/triage/analyze",
        {"symptoms": f"Concurrent test request {i} symptoms", "age": 30 + i})
elapsed = time.time() - start_time
print(f"10 requests completed in {elapsed:.2f}s (avg {elapsed/10:.2f}s per request)")

# ===============================================
# PHASE 6: DATABASE CONSISTENCY (LOGICAL TESTS)
# ===============================================
print("\n" + "=" * 100)
print("PHASE 6: DATABASE CONSISTENCY")
print("=" * 100)

# Test 6.1: Verify doctors exist for all departments
response = test_api("PHASE 6", "Database", "Doctors coverage", "GET", "/admin/doctors")
if response and isinstance(response, list):
    specialties = {d.get('specialty') for d in response}
    dept_map = {
        'Cardiology': 'Cardiology',
        'Orthopedics': 'Orthopedics',
        'Pediatrics': 'Pediatrics',
        'General Medicine': 'General Medicine',
        'ENT': 'ENT',
        'Gynecology': 'Gynecology',
        'Dermatology': 'Dermatology',
        'Neurology': 'Neurology',
        'Emergency Medicine': 'Emergency Medicine',
        'Gastroenterology': 'Gastroenterology'
    }
    missing = set(dept_map.values()) - specialties
    if not missing:
        tr.add("PHASE 6", "Database", "All departments have doctors", "✅", f"Found {len(specialties)} specialties")
    else:
        tr.add("PHASE 6", "Database", "All departments have doctors", "❌", f"Missing: {missing}")

# Test 6.2: Verify billing data integrity
test_api("PHASE 6", "Database", "Billing analytics integrity", "GET", "/billing/analytics",
    validate_fn=lambda r: True if 'summary' in r else "Missing summary in response")

# Test 6.3: Verify patient data integrity
test_api("PHASE 6", "Database", "Patient data integrity", "GET", "/doctor/patients",
    validate_fn=lambda r: True if isinstance(r, list) and len(r) > 0 else "No patients found")

# ===============================================
# FINAL SUMMARY
# ===============================================
tr.print_summary()

print("\n" + "=" * 100)
print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)
