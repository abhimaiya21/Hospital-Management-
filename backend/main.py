from typing import Dict, Any
import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import the split router modules from your backend.routers package
from backend.routers import admin, doctor, billing, patient, triage
from backend.db import init_connection_pool, close_connection_pool  # ✅ NEW

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="MediPortal Multi-Role API",
    description="Modular backend for Hospital Management System",
    version="2.0.0"
)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
# Note: All routers are served under /api/v1
api_prefix = "/api/v1"
app.include_router(admin.router, prefix=f"{api_prefix}/admin", tags=["Admin"])
app.include_router(doctor.router, prefix=f"{api_prefix}", tags=["Doctor"])
app.include_router(billing.router, prefix=f"{api_prefix}", tags=["Billing"])
app.include_router(patient.router, prefix=f"{api_prefix}", tags=["Patient"])
app.include_router(triage.router, prefix=f"{api_prefix}", tags=["Medical Triage"])

# --- 3. STARTUP EVENT (✅ NEW) ---
@app.on_event("startup")
def startup_event():
    """Initialize connection pool when application starts"""
    try:
        init_connection_pool()
        print("✅ MediPortal Backend started with connection pooling")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize connection pool: {e}")

# --- 4. SHUTDOWN EVENT (✅ NEW) ---
@app.on_event("shutdown")
def shutdown_event():
    """Close connection pool when application shuts down"""
    close_connection_pool()

# --- 5. HEALTH CHECK ROOT ENDPOINT ---
@app.get("/")
def health_check() -> Dict[str, Any]:
    """
    Used by index.html to verify the backend status on page load.
    """
    return {
        "status": "MediPortal Backend is Online",
        "modular_mode": True,
        "active_routers": ["admin", "doctor", "billing", "patient", "triage"],
        "connection_pooling": True  # ✅ NEW: Indicates pooling is active
    }

# --- 6. SERVE FRONTEND STATIC FILES ---
# Mount the frontend folder to serve HTML, CSS, JS files
frontend_path = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")


# --- 4. START SERVER ---
if __name__ == "__main__":
    # Runs the server on localhost:8000
    # Command to run manually: uvicorn backend.main:app --reload
    uvicorn.run(app, host="127.0.0.1", port=8000)