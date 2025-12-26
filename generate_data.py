import json
import random

# --- 1. CONFIGURATION: Your Specific Hospital Schema ---
doctors = ['Dr. Smith', 'Dr. Jones', 'Dr. Lee', 'Dr. Patel', 'Dr. Garcia']
specialties = ['Cardiology', 'Pediatrics', 'Neurology', 'Oncology']
allergens = ['Peanuts', 'Penicillin', 'Dust', 'Latex', 'Shellfish']
severities = ['Severe', 'Mild', 'Life-Threatening', 'Moderate']

# --- 2. TEMPLATES: The "Skills" to teach the AI ---
templates = [
    # Skill A: Simple Lookup
    (
        "Find contact details for patient {name}.",
        "SELECT contact_number, address FROM patients WHERE full_name = '{name}';"
    ),
    # Skill B: Complex Join (Allergies)
    (
        "List all patients with {severity} {allergen} allergy.",
        "SELECT p.full_name FROM patients p JOIN allergies a ON p.patient_id = a.patient_id WHERE a.allergen = '{allergen}' AND a.severity = '{severity}';"
    ),
    # Skill C: Department Query (Doctors + Patients)
    (
        "Show me patients treated by the {specialty} department.",
        "SELECT DISTINCT p.full_name FROM patients p JOIN appointments app ON p.patient_id = app.patient_id JOIN doctors d ON app.doctor_id = d.doctor_id WHERE d.specialty = '{specialty}';"
    ),
    # Skill D: Date Logic
    (
        "What are the appointments for {doctor} today?",
        "SELECT a.appointment_date, p.full_name FROM appointments a JOIN doctors d ON a.doctor_id = d.doctor_id JOIN patients p ON a.patient_id = p.patient_id WHERE d.full_name = '{doctor}' AND a.appointment_date::DATE = CURRENT_DATE;"
    )
]

# --- 3. SAFETY RULES (The "Societal Concern" aspect) ---
safety_examples = [
    ("Delete all records for patient John Doe.", "I cannot execute this query. The system is Read-Only for safety reasons."),
    ("Drop the appointments table.", "Access Denied. Database modification commands (DROP, DELETE, UPDATE) are strictly prohibited."),
    ("What is Dr. Smith's home address and salary?", "I cannot provide this information. Access to personal doctor data is restricted."),
    ("Update the medical record for patient 5.", "Modification of data is not allowed in this interface.")
]

# --- 4. GENERATION LOOP ---
data = []

# Generate 200 Synthetic "Success" Examples
for _ in range(200):
    nl_template, sql_template = random.choice(templates)
    
    # Fill with random data
    name = f"Patient_{random.randint(1, 100)}"
    doc = random.choice(doctors)
    spec = random.choice(specialties)
    allergen = random.choice(allergens)
    severity = random.choice(severities)
    
    entry = {
        "instruction": "Convert this natural language query into SQL for the hospital database.",
        "input": nl_template.format(name=name, doctor=doc, specialty=spec, allergen=allergen, severity=severity),
        "output": sql_template.format(name=name, doctor=doc, specialty=spec, allergen=allergen, severity=severity)
    }
    data.append(entry)

# Add Safety Examples (Repeat them so the model learns them well)
for _ in range(5): 
    for question, answer in safety_examples:
        entry = {
            "instruction": "System Role: You are a secure SQL assistant.",
            "input": question,
            "output": answer
        }
        data.append(entry)

# Shuffle to mix safety and skills
random.shuffle(data)

# --- 5. SAVE FILE ---
output_file = 'hospital_training_data.jsonl'
with open(output_file, 'w') as f:
    for entry in data:
        f.write(json.dumps(entry) + '\n')

print(f"Success! Generated {len(data)} examples in '{output_file}'")