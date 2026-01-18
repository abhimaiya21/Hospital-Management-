import csv
import random

# These MUST match the 'department_name' values in your 'departments' table
DEPARTMENTS = [
    "Cardiology", "Dermatology", "Orthopedics", "General Medicine", 
    "Neurology", "Pediatrics", "ENT", "Gynecology", "Oncology", "Psychiatry"
]

def generate_training_data():
    # 1. Define symptom patterns for each department
    data_patterns = {
        "Cardiology": ["chest pain", "heart palpitations", "shortness of breath", "left arm pain", "heart attack history"],
        "Dermatology": ["skin rash", "itchy skin", "acne", "hair loss", "redness", "blisters"],
        "Orthopedics": ["joint pain", "fracture", "back pain", "knee injury", "bone hurts", "muscle tear"],
        "General Medicine": ["fever", "cold", "flu", "headache", "weakness", "body pain", "nausea"],
        "Neurology": ["migraine", "seizures", "dizziness", "numbness", "loss of balance"],
        # Add other departments as needed...
    }

    # 2. Generate the CSV file
    file_path = '../backend/training_data.csv'
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["symptoms", "department"]) # Headers

        print(f"Generating synthetic data for {len(data_patterns)} departments...")
        
        # Create 1000 rows of data
        for _ in range(1000):
            # Pick a random department from our patterns
            dept = random.choice(list(data_patterns.keys()))
            # Pick a random symptom associated with that department
            symptom = random.choice(data_patterns[dept])
            
            # Create variations of the sentence to make the model robust
            variations = [
                f"I have {symptom}",
                f"suffering from {symptom}",
                f"severe {symptom} since yesterday",
                f"{symptom}",
                f"experiencing {symptom}"
            ]
            text = random.choice(variations)
            
            writer.writerow([text, dept])

    print(f"✅ Success! Training data saved to {file_path}")

if __name__ == "__main__":
    generate_training_data()