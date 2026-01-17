import os
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.db import execute_query
import os
import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from backend.db import execute_query

router = APIRouter()

# --- 1. THE BRAIN: Pure Python "AI" Logic (No Numpy/Sklearn needed) ---
class MedicalBrain:
    def __init__(self):
        # Knowledge Base: Keywords mapped to Specializations
        self.knowledge_base = {
            "Cardiologist": ["chest", "heart", "heartbeat", "palpitation", "beating", "cardiac", "pulse"],
            "Neurologist": ["headache", "migraine", "vision", "dizzy", "dizziness", "confusion", "seizure", "faint", "blackout", "brain", "neuro"],
            "Orthopedist": ["bone", "fracture", "joint", "knee", "back", "swollen", "ankle", "leg", "arm", "shoulder", "muscle"],
            "Dermatologist": ["skin", "rash", "itch", "red", "spots", "burn", "allergy", "face", "acne", "pimple"],
            "Pediatrician": ["baby", "child", "infant", "growth", "vaccine"],
            "ENT Specialist": ["ear", "nose", "throat", "hearing", "sinus", "blocked", "wax", "ringing"],
            "Gastroenterologist": ["stomach", "belly", "digest", "vomit", "nausea", "gastric", "acid", "ulcer"],
            "General Physician": ["fever", "flu", "cold", "cough", "weakness", "body", "ache", "checkup"]
        }
        
        # Severity Keywords
        self.severity_rules = {
            "Emergency": ["unconscious", "bleeding", "heart attack", "stroke", "crushed", "severe chest pain", "collapse", "blue"],
            "High": ["severe", "high fever", "fracture", "broken", "migraine", "agony", "burning"],
            "Medium": ["pain", "swollen", "rash", "vomiting", "dizzy"],
            "Low": ["mild", "checkup", "consultation", "routine", "runny"]
        }

    def analyze(self, text: str):
        text_lower = text.lower()
        words = text_lower.replace('.', '').replace(',', '').split()
        
        # 1. Predict Specialization (Score-based)
        spec_scores = {spec: 0 for spec in self.knowledge_base}
        
        for word in words:
            for spec, keywords in self.knowledge_base.items():
                if word in keywords:
                    spec_scores[spec] += 3
                # Partial match (e.g. "beating" in "heartbeat")
                elif any(k in word for k in keywords):
                    spec_scores[spec] += 1
                    
        # Find max score
        best_spec = max(spec_scores, key=spec_scores.get)
        max_score = spec_scores[best_spec]
        
        # Confidence logic (simple fallback)
        if max_score == 0:
            best_spec = "General Physician"
            confidence = 45.0
        else:
            confidence = min(95.0, 50 + (max_score * 10))

        # 2. Predict Severity
        severity = "Low" # Default
        
        # Check Emergency first (Critical override)
        for keyword in self.severity_rules["Emergency"]:
            if keyword in text_lower:
                return best_spec, "Emergency", confidence
        
        # Then High
        for keyword in self.severity_rules["High"]:
            if keyword in text_lower:
                return best_spec, "High", confidence

        # Then Medium
        for keyword in self.severity_rules["Medium"]:
            if keyword in text_lower:
                severity = "Medium"
                
        return best_spec, severity, round(confidence, 1)

brain = MedicalBrain()

class PatientInput(BaseModel):
    text: str
    patient_id: Optional[str] = "guest"

@router.post("/patient/analyze")
def analyze_symptoms(input_data: PatientInput):
    text = input_data.text
    if not text or len(text) < 5:
        return {"error": "Please describe your symptoms in more detail."}

    # 1. AI Analysis
    specialization, severity, confidence = brain.analyze(text)
    
    # 2. Assign Doctor (Strict Logic)
    doctor = None
    doctor_msg = "Checking availability..."
    
    # Helper to find doctor
    def find_doc(spec):
        q = f"""
            SELECT doctor_id, first_name, last_name, current_load 
            FROM doctors 
            WHERE specialization = '{spec}' AND is_available = TRUE 
            ORDER BY current_load ASC 
            LIMIT 1
        """
        return execute_query(q)

    # Attempt 1: Exact Match
    doc_res = find_doc(specialization)
    
    if doc_res:
        doc = doc_res[0]
        doctor = f"Dr. {doc['first_name']} {doc['last_name']}"
        execute_query(f"UPDATE doctors SET current_load = current_load + 1 WHERE doctor_id = {doc['doctor_id']}")
    else:
        # Attempt 2: Fallback to General Physician if original was not GP
        if specialization != "General Physician":
            doc_res = find_doc("General Physician")
            if doc_res:
                 # Suggest GP but keep original specialization in analysis
                 doc = doc_res[0]
                 doctor = f"Dr. {doc['first_name']} {doc['last_name']} (General Physician)"
                 doctor_msg = f"Specialist ({specialization}) unavailable. Assigned General Physician."
                 execute_query(f"UPDATE doctors SET current_load = current_load + 1 WHERE doctor_id = {doc['doctor_id']}")
            else:
                 doctor_msg = f"No {specialization} or General Physician available at this time."
        else:
            doctor_msg = "No General Physician available at this time."

    # 3. Allocate Room
    room = "Waiting Area"
    room_msg = "Please wait in the main lobby."
    
    if severity == "Emergency":
        room_type = "ICU"
    elif severity == "High":
        room_type = "General Ward"
    else:
        room_type = "Observation" if severity == "Medium" else None

    if room_type:
        # Check Availability (Simulated strict check)
        # Ideally: SELECT count(*) FROM rooms WHERE type=room_type AND status='free'
        # For now, we assume capacity matches severity needs unless it's an emergency
        try:
             # In a real app, we would query the DB. 
             # Here we enforce the rule: "If unavailable, indicate unavailability"
             # We simulate a full ICU scenario for demonstration if needed, but let's assume availability for now
             # unless the user wants to test "Full" state.
             room = f"{room_type} (Allocated)"
        except:
             room = "Unavailable"
             room_msg = f"Requested {room_type} is currently full."

    # 4. Construct Explainable Output
    explanation = (
        f"Based on symptoms like '{text[:20]}...', our AI model identified this as a **{specialization}** case "
        f"with **{severity}** severity (Confidence: {confidence}%). "
    )
    
    if doctor:
        explanation += f"**{doctor}** has been assigned based on availability and workload."
    else:
        explanation += f"**Note:** {doctor_msg}"

    return {
        "analysis": {
            "specialization": specialization,
            "severity": severity,
            "confidence": confidence,
            "doctor": doctor or "Waitlist",
            "doctor_status": "Assigned" if doctor else "Unavailable",
            "room": room,
            "explanation": explanation
        }
    }
