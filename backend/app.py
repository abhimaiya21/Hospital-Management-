import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.db import execute_query 

# Load environment variables
load_dotenv()

app = FastAPI()

# 1. CORS SETUP (Allows Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. CONFIGURATION
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"

# 3. DATA MODELS
class LoginRequest(BaseModel):
    username: str
    password: str

class QueryRequest(BaseModel):
    text: str

# 4. LOGIN ENDPOINT (Instant, No AI)
@app.post("/login")
def login(creds: LoginRequest):
    print(f"🔐 Login attempt: {creds.username}")
    
    # Simple SQL check (Use parameterized queries in production!)
    sql = f"SELECT * FROM users WHERE username = '{creds.username}' AND password = '{creds.password}'"
    result = execute_query(sql)
    
    if not result:
        print("❌ Login Failed: Invalid Credentials")
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    user_role = result[0]['role']
    print(f"✅ Success! {creds.username} is a {user_role}")
    
    return {
        "status": "success", 
        "role": user_role, 
        "username": creds.username
    }

# 5. AI QUERY ENDPOINT (With Timeout Fix)
@app.post("/query")
async def query_ai(request: QueryRequest):
    # A. Health Check Ping (For Frontend Status Dot)
    if request.text == "Ping":
        return {"status": "Online"}

    # B. The AI Logic
    schema = "Schema: patients, doctors, appointments, medical_records, invoices, users."
    prompt = f"You are SQL expert. {schema} Convert to PostgreSQL SQL: {request.text}"
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        # TIMEOUT FIX: We wait 30 seconds before giving up
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(HF_URL, headers=headers, json={"inputs": prompt})
            
    except httpx.ConnectTimeout:
        print("❌ AI Timeout: Hugging Face took too long.")
        return {"generated_sql": "-- Error", "results": {"error": "AI Server timed out. Please try again."}}
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return {"generated_sql": "-- Error", "results": {"error": str(e)}}

    # C. Handle AI Response
    if response.status_code != 200:
        return {"generated_sql": "Error", "results": {"error": f"AI Error: {response.text}"}}
        
    try:
        ai_data = response.json()
        # Parse output (Hugging Face sometimes returns a list, sometimes a dict)
        if isinstance(ai_data, list) and len(ai_data) > 0:
            sql = ai_data[0].get('generated_text', '').strip()
        elif isinstance(ai_data, dict) and 'generated_text' in ai_data:
            sql = ai_data['generated_text'].strip()
        else:
            sql = "SELECT * FROM patients LIMIT 1;" # Fallback
            
        print(f"🤖 AI Suggested: {sql}")
        
        # D. Run SQL in Database
        data = execute_query(sql)
        return {"generated_sql": sql, "results": data}
        
    except Exception as e:
        return {"generated_sql": "Error Parsing", "results": {"error": str(e)}}