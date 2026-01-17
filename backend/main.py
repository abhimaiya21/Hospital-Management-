import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import the split router modules from your backend.routers package
from backend.routers import admin, doctor, billing, patient

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="MediPortal Multi-Role API",
    description="Modular backend for Hospital Management System",
    version="2.0.0"
)

# --- 1. CORS CONFIGURATION ---
# This allows your frontend (HTML/JS) to communicate with the FastAPI server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change to specific domain for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- 2. INCLUDE ROUTERS ---
# This connects the split files to the main 'app' instance.
# Note: You can add prefixes like prefix="/admin" if you want to group them.
app.include_router(admin.router)
app.include_router(doctor.router)
app.include_router(billing.router)
app.include_router(patient.router)

# --- 3. HEALTH CHECK ROOT ENDPOINT ---
@app.get("/")
def health_check():
    """
    Used by index.html to verify the backend status on page load.
    """
    return {
        "status": "MediPortal Backend is Online",
        "modular_mode": True,
        "active_routers": ["admin", "doctor", "billing", "patient"]
    }

# --- 4. START SERVER ---
if __name__ == "__main__":
    # Runs the server on localhost:8000
    # Command to run manually: uvicorn backend.main:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000)