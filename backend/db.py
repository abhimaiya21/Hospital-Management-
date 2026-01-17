import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
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