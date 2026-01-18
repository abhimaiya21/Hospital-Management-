import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_db_connection():
    try:
        # Ensure DATABASE_URL is set
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ Error: DATABASE_URL environment variable not set.")
            raise Exception("DATABASE_URL environment variable not set.")
            
        conn = psycopg2.connect(db_url)
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Database Operational Error: {e}")
        raise Exception(f"Could not connect to database. Check credentials and server status. Details: {e}")
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        raise e



def execute_query(sql_query: str):
    """
    Connects to DB, runs the SQL, and returns results as JSON.
    """
    conn = get_db_connection()
    results = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query)
            
            # If it's a SELECT query, return data
            if cur.description:
                results = cur.fetchall()
            else:
                # If it's INSERT/UPDATE, commit changes
                conn.commit()
                results = [{"status": "success", "message": "Operation completed."}]
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    finally:
        conn.close()
        
    return results


def verify_patient_login(patient_id, mobile_number):
    """
    Verifies patient login credentials using patient_id and contact_number.
    
    Args:
        patient_id (int): Patient ID from the patients table
        mobile_number (str): Contact number for verification
        
    Returns:
        dict: Patient information if credentials are valid
        None: If credentials are invalid or patient not found
    """
    conn = get_db_connection()
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT 
                    patient_id,
                    first_name,
                    last_name,
                    contact_number,
                    email,
                    dob,
                    gender,
                    blood_group,
                    is_active
                FROM patients
                WHERE patient_id = %s 
                  AND contact_number = %s
                  AND is_active = TRUE
            """
            
            cursor.execute(query, (patient_id, mobile_number))
            patient = cursor.fetchone()
            
            if patient:
                return {
                    "patient_id": patient['patient_id'],
                    "first_name": patient['first_name'],
                    "last_name": patient['last_name'],
                    "full_name": f"{patient['first_name']} {patient['last_name']}",
                    "contact_number": patient['contact_number'],
                    "email": patient['email'],
                    "dob": str(patient['dob']) if patient['dob'] else None,
                    "gender": patient['gender'],
                    "blood_group": patient['blood_group'],
                    "is_active": patient['is_active']
                }
            return None
            
    except Exception as e:
        print(f"❌ Error verifying patient login: {e}")
        raise e
        
    finally:
        conn.close()


# specific imports depend on your existing db setup (e.g., psycopg2, sqlite3, sqlalchemy)

def get_available_doctor(department_name):
    """
    Finds an available doctor belonging to the predicted department.
    
    Args:
        department_name (str): Department name from ML model prediction (e.g., 'Cardiology')
        
    Returns:
        dict: Doctor information with doctor_id, first_name, last_name, room_number, consultation_fee
        None: If no available doctor is found
        
    Raises:
        Exception: If database query fails
    """
    conn = get_db_connection()
    
    try:
        # Use RealDictCursor to get results as dictionaries instead of tuples
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # SQL Query:
            # 1. JOIN doctors and departments tables.
            # 2. Filter where department_name matches our prediction (case-insensitive).
            # 3. Filter where doctor is_available is TRUE.
            # 4. Order by workload to assign less busy doctors first.
            # 5. LIMIT 1 to get just one doctor.
            
            query = """
                SELECT 
                    d.doctor_id, 
                    d.first_name, 
                    d.last_name, 
                    d.doctor_room_number,
                    d.consultation_fee,
                    dept.department_id,
                    dept.department_name
                FROM doctors d
                JOIN departments dept ON d.department_id = dept.department_id
                WHERE LOWER(TRIM(dept.department_name)) = LOWER(TRIM(%s))
                  AND d.is_available = TRUE
                ORDER BY d.current_workload ASC
                LIMIT 1;
            """
            
            # Use parameterized query to prevent SQL injection
            cursor.execute(query, (department_name,))
            doctor = cursor.fetchone()
            
            # Return a dictionary for easier usage
            if doctor:
                return {
                    "doctor_id": doctor['doctor_id'],
                    "first_name": doctor['first_name'],
                    "last_name": doctor['last_name'],
                    "room_number": doctor['doctor_room_number'],
                    "consultation_fee": float(doctor['consultation_fee']),
                    "department_id": doctor['department_id'],
                    "department_name": doctor['department_name']
                }
            return None
            
    except Exception as e:
        print(f"❌ Error fetching available doctor: {e}")
        raise e
        
    finally:
        conn.close()


def get_available_room(severity_level, department_id=None):
    """
    Finds an available room based on severity level.
    
    Args:
        severity_level (str): 'Emergency', 'Critical', 'High', 'Medium', 'Low'
        department_id (int, optional): Preferred department
        
    Returns:
        dict: Room information with room_id, room_number, room_type
        None: If no available room is found
    """
    conn = get_db_connection()
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Map severity to room type priority
            if severity_level in ['Emergency', 'Critical']:
                room_types = ['Emergency', 'ICU', 'Private Room', 'General Ward']
            elif severity_level == 'High':
                room_types = ['ICU', 'Private Room', 'General Ward']
            else:
                room_types = ['General Ward', 'Private Room']
            
            # Find first available room
            for room_type in room_types:
                query = """
                    SELECT 
                        room_id, 
                        room_number, 
                        room_type,
                        wing,
                        floor_number,
                        bed_capacity,
                        current_occupancy
                    FROM rooms
                    WHERE room_type = %s 
                      AND status = 'Available'
                      AND current_occupancy < bed_capacity
                    ORDER BY current_occupancy ASC
                    LIMIT 1;
                """
                
                cursor.execute(query, (room_type,))
                room = cursor.fetchone()
                
                if room:
                    return {
                        "room_id": room['room_id'],
                        "room_number": room['room_number'],
                        "room_type": room['room_type'],
                        "wing": room['wing'],
                        "floor_number": room['floor_number']
                    }
            
            return None
            
    except Exception as e:
        print(f"❌ Error fetching available room: {e}")
        raise e
        
    finally:
        conn.close()


def create_emergency_patient(patient_data):
    """
    Creates a new patient record with emergency priority.
    
    Args:
        patient_data (dict): Patient information
        
    Returns:
        int: patient_id of newly created patient
        
    Raises:
        Exception: If insertion fails
    """
    conn = get_db_connection()
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                INSERT INTO patients (
                    first_name, last_name, dob, gender, blood_group,
                    contact_number, emergency_contact, emergency_contact_name,
                    email, address, city, state, pincode,
                    registered_date, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE, TRUE
                ) RETURNING patient_id;
            """
            
            cursor.execute(query, (
                patient_data.get('first_name'),
                patient_data.get('last_name'),
                patient_data.get('dob'),
                patient_data.get('gender'),
                patient_data.get('blood_group'),
                patient_data.get('contact_number'),
                patient_data.get('emergency_contact'),
                patient_data.get('emergency_contact_name'),
                patient_data.get('email'),
                patient_data.get('address'),
                patient_data.get('city'),
                patient_data.get('state'),
                patient_data.get('pincode')
            ))
            
            result = cursor.fetchone()
            patient_id = result['patient_id']
            conn.commit()
            
            return patient_id
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating patient: {e}")
        raise e
        
    finally:
        conn.close()


def create_emergency_appointment(appointment_data):
    """
    Creates an emergency appointment with room assignment.
    
    Args:
        appointment_data (dict): Appointment details
        
    Returns:
        int: appointment_id of newly created appointment
    """
    conn = get_db_connection()
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                INSERT INTO appointments (
                    patient_id, doctor_id, department_id, room_id,
                    appointment_date, patient_problem_text, symptoms,
                    predicted_specialty, predicted_severity, confidence_score,
                    appointment_type, status
                ) VALUES (
                    %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, 'Emergency', 'Scheduled'
                ) RETURNING appointment_id;
            """
            
            cursor.execute(query, (
                appointment_data.get('patient_id'),
                appointment_data.get('doctor_id'),
                appointment_data.get('department_id'),
                appointment_data.get('room_id'),
                appointment_data.get('problem_description'),
                appointment_data.get('symptoms'),
                appointment_data.get('predicted_specialty'),
                appointment_data.get('severity'),
                appointment_data.get('confidence_score')
            ))
            
            result = cursor.fetchone()
            appointment_id = result['appointment_id']
            conn.commit()
            
            # Update room occupancy
            if appointment_data.get('room_id'):
                update_query = """
                    UPDATE rooms 
                    SET current_occupancy = current_occupancy + 1,
                        status = CASE 
                            WHEN current_occupancy + 1 >= bed_capacity THEN 'Occupied'
                            ELSE 'Available'
                        END
                    WHERE room_id = %s;
                """
                cursor.execute(update_query, (appointment_data.get('room_id'),))
                conn.commit()
            
            return appointment_id
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating appointment: {e}")
        raise e
        
    finally:
        conn.close()