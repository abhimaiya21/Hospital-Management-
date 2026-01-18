from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional
from ..ml_service import predict_department
from ..db import get_available_doctor, get_available_room, create_emergency_patient, create_emergency_appointment, verify_patient_login

router = APIRouter()


class PatientLoginRequest(BaseModel):
    patient_id: int
    mobile_number: str


class SymptomCheck(BaseModel):
    patient_id: int
    problem_description: str


class EmergencyPatientIntake(BaseModel):
    # Patient Demographics
    first_name: str
    last_name: str
    dob: date
    gender: str
    blood_group: Optional[str] = None
    contact_number: str
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    
    # Medical Condition
    problem_description: str
    symptoms: Optional[str] = None


@router.post("/login")
def patient_login(request: PatientLoginRequest):
    """
    Patient Login Endpoint
    
    Authenticates patients using patient_id and mobile_number (contact_number).
    This is separate from the staff login system which uses username/password.
    
    Args:
        request: PatientLoginRequest with patient_id and mobile_number
        
    Returns:
        Success response with patient details and redirect URL
        Or failure response with error message
    """
    try:
        # Validate input
        if not request.mobile_number or len(request.mobile_number.strip()) == 0:
            raise HTTPException(status_code=400, detail="Mobile number is required")
        
        if request.patient_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid patient ID")
        
        # Verify credentials against database
        patient = verify_patient_login(request.patient_id, request.mobile_number.strip())
        
        if not patient:
            return {
                "status": "failed",
                "message": "Invalid Patient ID or Mobile Number. Please check your credentials."
            }
        
        # Successful login
        return {
            "status": "success",
            "message": "Login successful",
            "redirect_url": "patient.html",
            "patient": {
                "patient_id": patient['patient_id'],
                "full_name": patient['full_name'],
                "first_name": patient['first_name'],
                "last_name": patient['last_name'],
                "contact_number": patient['contact_number'],
                "email": patient['email'],
                "gender": patient['gender'],
                "blood_group": patient['blood_group']
            }
        }
        
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Patient Login Error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed due to server error: {str(e)}")


@router.post("/predict-and-assign")
def assign_doctor(request: SymptomCheck):
    """
    Predicts the department based on symptoms and assigns an available doctor.
    
    Flow:
    1. Use ML to predict department from symptom description
    2. Query database for available doctor in that department
    3. Return assignment or waitlist status
    """
    try:
        # Validate input
        if not request.problem_description or len(request.problem_description.strip()) == 0:
            raise HTTPException(status_code=400, detail="Problem description cannot be empty")
        
        # 1. Use ML to predict the department based on symptoms
        try:
            predicted_dept_name, confidence = predict_department(request.problem_description)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ML prediction error: {str(e)}")
        
        # Validate ML output
        if not predicted_dept_name or not isinstance(predicted_dept_name, str):
            raise HTTPException(status_code=500, detail="Invalid prediction from ML model")
        
        predicted_dept_name = predicted_dept_name.strip()
        
        # 2. Check Database for an available doctor in that department
        try:
            doctor = get_available_doctor(predicted_dept_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        response_data = {
            "patient_id": request.patient_id,
            "symptoms": request.problem_description,
            "predicted_department": predicted_dept_name,
            "confidence_score": round(float(confidence), 4)
        }

        if not doctor:
            # Case: Department exists, but no doctors are available/free
            response_data["status"] = "Waitlist"
            response_data["message"] = f"We have identified you need {predicted_dept_name}, but no doctors are currently available. You've been added to the waitlist."
            return response_data

        # Case: Doctor found and assigned
        response_data["status"] = "Assigned"
        response_data["assigned_doctor"] = {
            "doctor_id": doctor['doctor_id'],
            "first_name": doctor['first_name'],
            "last_name": doctor['last_name'],
            "full_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
            "room_number": doctor['room_number'],
            "consultation_fee": doctor['consultation_fee'],
            "department": doctor['department_name']
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/emergency-intake")
def emergency_patient_intake(request: EmergencyPatientIntake):
    """
    Emergency Patient Registration and Assignment System
    
    Flow:
    1. Create new patient record with emergency priority
    2. Use ML to predict department and severity (default: Critical/Emergency)
    3. Assign available doctor based on specialization
    4. Assign available room based on severity (Emergency/ICU/General)
    5. Create emergency appointment with all assignments
    6. Return complete registration details
    
    Returns:
        Complete patient registration with doctor and room assignments
    """
    response_data = {
        "registration_status": "pending",
        "patient_created": False,
        "doctor_assigned": False,
        "room_assigned": False,
        "appointment_created": False,
        "messages": []
    }
    
    try:
        # Step 1: Validate Input
        if not request.problem_description or len(request.problem_description.strip()) == 0:
            raise HTTPException(status_code=400, detail="Problem description cannot be empty")
        
        response_data["messages"].append("✅ Input validated")
        
        # Step 2: Create Patient Record (EMERGENCY PRIORITY)
        try:
            patient_data = {
                "first_name": request.first_name,
                "last_name": request.last_name,
                "dob": request.dob,
                "gender": request.gender,
                "blood_group": request.blood_group,
                "contact_number": request.contact_number,
                "emergency_contact": request.emergency_contact,
                "emergency_contact_name": request.emergency_contact_name,
                "email": request.email,
                "address": request.address,
                "city": request.city,
                "state": request.state,
                "pincode": request.pincode
            }
            
            patient_id = create_emergency_patient(patient_data)
            response_data["patient_id"] = patient_id
            response_data["patient_created"] = True
            response_data["messages"].append(f"✅ PATIENT REGISTERED - ID: {patient_id}")
            
        except Exception as e:
            response_data["messages"].append(f"❌ Patient creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Patient registration failed: {str(e)}")
        
        # Step 3: ML Prediction for Department & Severity
        try:
            predicted_dept_name, confidence = predict_department(request.problem_description)
            predicted_dept_name = predicted_dept_name.strip()
            
            # Default to Emergency/Critical severity for all new patients
            severity = "Emergency"
            
            response_data["predicted_department"] = predicted_dept_name
            response_data["confidence_score"] = round(float(confidence), 4)
            response_data["severity"] = severity
            response_data["messages"].append(f"✅ ML PREDICTION: {predicted_dept_name} (Confidence: {round(confidence*100, 2)}%)")
            
        except Exception as e:
            response_data["messages"].append(f"❌ ML prediction error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"ML prediction failed: {str(e)}")
        
        # Step 4: Assign Doctor
        try:
            doctor = get_available_doctor(predicted_dept_name)
            
            if not doctor:
                response_data["doctor_status"] = "Doctor Not Available"
                response_data["messages"].append(f"⚠️ DOCTOR NOT AVAILABLE in {predicted_dept_name}")
                response_data["assigned_doctor"] = {
                    "status": "unavailable",
                    "message": f"No doctors currently available in {predicted_dept_name} department"
                }
            else:
                response_data["doctor_assigned"] = True
                response_data["doctor_status"] = "Assigned"
                response_data["assigned_doctor"] = {
                    "doctor_id": doctor['doctor_id'],
                    "first_name": doctor['first_name'],
                    "last_name": doctor['last_name'],
                    "full_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
                    "room_number": doctor['room_number'],
                    "consultation_fee": doctor['consultation_fee'],
                    "department": doctor['department_name'],
                    "status": "available"
                }
                response_data["messages"].append(f"✅ DOCTOR ASSIGNED: Dr. {doctor['first_name']} {doctor['last_name']}")
                
        except Exception as e:
            response_data["messages"].append(f"❌ Doctor assignment error: {str(e)}")
            response_data["doctor_status"] = "Error"
        
        # Step 5: Assign Room
        try:
            room = get_available_room(severity)
            
            if not room:
                response_data["room_status"] = "Room Not Available – Immediate Attention Required"
                response_data["messages"].append("⚠️ ROOM NOT AVAILABLE - IMMEDIATE ATTENTION REQUIRED")
                response_data["assigned_room"] = {
                    "status": "unavailable",
                    "message": "No rooms available - Patient needs immediate attention in waiting area"
                }
            else:
                response_data["room_assigned"] = True
                response_data["room_status"] = "Assigned"
                response_data["assigned_room"] = {
                    "room_id": room['room_id'],
                    "room_number": room['room_number'],
                    "room_type": room['room_type'],
                    "wing": room['wing'],
                    "floor": room['floor_number'],
                    "status": "assigned"
                }
                response_data["messages"].append(f"✅ ROOM ASSIGNED: {room['room_number']} ({room['room_type']})")
                
        except Exception as e:
            response_data["messages"].append(f"❌ Room assignment error: {str(e)}")
            response_data["room_status"] = "Error"
        
        # Step 6: Create Emergency Appointment
        if response_data["patient_created"]:
            try:
                appointment_data = {
                    "patient_id": patient_id,
                    "doctor_id": doctor['doctor_id'] if doctor else None,
                    "department_id": doctor['department_id'] if doctor else None,
                    "room_id": room['room_id'] if room else None,
                    "problem_description": request.problem_description,
                    "symptoms": request.symptoms or request.problem_description,
                    "predicted_specialty": predicted_dept_name,
                    "severity": severity,
                    "confidence_score": float(confidence)
                }
                
                if doctor:  # Only create appointment if doctor is available
                    appointment_id = create_emergency_appointment(appointment_data)
                    response_data["appointment_id"] = appointment_id
                    response_data["appointment_created"] = True
                    response_data["messages"].append(f"✅ EMERGENCY APPOINTMENT CREATED - ID: {appointment_id}")
                else:
                    response_data["messages"].append("⚠️ APPOINTMENT NOT CREATED - No doctor available (Patient in waitlist)")
                    
            except Exception as e:
                response_data["messages"].append(f"⚠️ Appointment creation warning: {str(e)}")
        
        # Final Status
        if response_data["patient_created"] and response_data["doctor_assigned"] and response_data["room_assigned"]:
            response_data["registration_status"] = "complete"
            response_data["overall_message"] = "🎉 EMERGENCY REGISTRATION COMPLETE - Patient, Doctor, and Room Assigned"
        elif response_data["patient_created"]:
            response_data["registration_status"] = "partial"
            response_data["overall_message"] = "⚠️ PATIENT REGISTERED - Awaiting doctor/room availability"
        else:
            response_data["registration_status"] = "failed"
            response_data["overall_message"] = "❌ REGISTRATION FAILED"
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        response_data["registration_status"] = "error"
        response_data["overall_message"] = f"❌ SYSTEM ERROR: {str(e)}"
        response_data["messages"].append(f"❌ Fatal error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))