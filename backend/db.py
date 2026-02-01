import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load variables from .env
load_dotenv()

# ✅ NEW: Connection pool for better performance
_connection_pool: Optional[pool.SimpleConnectionPool] = None

def init_connection_pool():
    """
    Initialize connection pool on startup
    ✅ NEW: Better performance, connection reuse, automatic management
    """
    global _connection_pool
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise Exception("DATABASE_URL environment variable not set.")
        
        # Create pool with min=1, max=20 connections
        _connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=db_url
        )
        print("✅ Connection pool initialized (1-20 connections)")
    except Exception as e:
        print(f"❌ Error initializing connection pool: {e}")
        raise

def get_db_connection():
    """
    ✅ NEW: Get connection from pool instead of creating new ones
    Falls back to direct connection if pool not initialized
    """
    global _connection_pool
    
    try:
        if _connection_pool is not None:
            return _connection_pool.getconn()
        else:
            # Fallback: Direct connection (for backward compatibility)
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise Exception("DATABASE_URL environment variable not set.")
            return psycopg2.connect(db_url)
    except psycopg2.OperationalError as e:
        print(f"❌ Database Operational Error: {e}")
        raise Exception(f"Could not connect to database. Check credentials and server status. Details: {e}")
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        raise e

def return_connection(conn):
    """
    ✅ NEW: Return connection to pool
    """
    global _connection_pool
    try:
        if _connection_pool is not None and conn:
            _connection_pool.putconn(conn)
    except Exception as e:
        print(f"⚠️ Error returning connection to pool: {e}")

def close_connection_pool():
    """
    ✅ NEW: Close all connections in pool (on shutdown)
    """
    global _connection_pool
    try:
        if _connection_pool is not None:
            _connection_pool.closeall()
            print("✅ Connection pool closed")
    except Exception as e:
        print(f"⚠️ Error closing connection pool: {e}")

def execute_query(sql_query: str) -> List[Dict[str, Any]]:
    """
    Execute SQL query with improved error handling and automatic connection return
    ✅ NEW: Connection pooling, automatic rollback on error, proper cleanup
    
    Returns:
        - List of dicts for SELECT queries
        - List with success message for INSERT/UPDATE
        - Dict with error for failed queries
    """
    conn = None
    results = []
    
    try:
        conn = get_db_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql_query)
            
            # Determine query type
            sql_upper = sql_query.strip().upper()
            is_write_query = sql_upper.startswith(('INSERT', 'UPDATE', 'DELETE'))
            
            # If it's a SELECT query or a write query with RETURNING, fetch data
            if cur.description:
                results = cur.fetchall()
                # Convert RealDictRow to regular dict for JSON serialization
                results = [dict(row) for row in results]
            
            # If it's INSERT/UPDATE/DELETE, commit changes
            if is_write_query:
                conn.commit()
                if not results:
                    results = [{"status": "success", "message": "Operation completed successfully."}]
                
    except psycopg2.Error as e:
        # ✅ NEW: Automatic rollback on database error
        if conn:
            try:
                conn.rollback()
            except:
                pass
        print(f"❌ Database error executing query: {e}")
        results = {"error": str(e)}
    except Exception as e:
        # ✅ NEW: Automatic rollback on unexpected error
        if conn:
            try:
                conn.rollback()
            except:
                pass
        print(f"❌ Unexpected error executing query: {e}")
        import traceback
        traceback.print_exc()
        results = {"error": str(e)}
    finally:
        # ✅ NEW: Always return connection to pool
        return_connection(conn)
    
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