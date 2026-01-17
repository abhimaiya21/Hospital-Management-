# Hospital Management System

A comprehensive Hospital Management System with Python FastAPI backend and HTML/JavaScript frontend. This system includes modules for Admin, Doctors, Patients, and Billing.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
4. [Running the Application](#running-the-application)
5. [Database Setup](#database-setup)
6. [Running Tests](#running-tests)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:

### 1. **Python 3.12**

- **Windows:**
  - Download from [python.org](https://www.python.org/downloads/)
  - Choose Python 3.12.x (latest stable)
  - **Important:** During installation, check the box "Add Python to PATH"
  - Verify installation:
    ```powershell
    python --version
    ```
    Should show: `Python 3.12.x`

- **Mac:**

  ```bash
  brew install python@3.12
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt-get update
  sudo apt-get install python3.12 python3.12-venv python3.12-dev
  ```

### 2. **Git**

- Download from [git-scm.com](https://git-scm.com/)
- Verify installation:
  ```powershell
  git --version
  ```

### 3. **PostgreSQL (Optional but Recommended)**

- Download from [postgresql.org](https://www.postgresql.org/download/)
- Note: The current setup uses SQLite by default

### 4. **Text Editor/IDE**

- Visual Studio Code (recommended) or any code editor

---

## Project Structure

```
Hospital Management/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── db.py                   # Database configuration
│   ├── routers/
│   │   ├── admin.py           # Admin endpoints
│   │   ├── doctor.py          # Doctor endpoints
│   │   ├── billing.py         # Billing endpoints
│   │   └── patient.py         # Patient endpoints
│   └── __pycache__/           # Python cache (auto-generated)
├── frontend/
│   ├── index.html             # Main dashboard
│   ├── admin.html             # Admin panel
│   ├── doctor.html            # Doctor panel
│   ├── patient.html           # Patient panel
│   ├── billing.html           # Billing panel
│   └── diagnostic.html        # Diagnostic panel
├── database/
│   ├── Table.sql              # Database table structure
│   ├── hospital_seed_100.sql  # Sample data (100 records)
│   └── fake_data.py           # Python script to generate fake data
├── tests/
│   └── (test files)           # Unit and integration tests
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
└── README.md                  # This file
```

---

## Step-by-Step Setup Guide

### Step 1: Clone the Repository from GitHub

Open your terminal/PowerShell and run:

```powershell
# Navigate to where you want to store the project
cd C:\Users\YourUsername\Projects  # or any desired location

# Clone the repository
git clone https://github.com/your-username/Hospital-Management.git

# Navigate into the project folder
cd "Hospital Management"
```

**Note:** Replace `https://github.com/your-username/Hospital-Management.git` with your actual GitHub repository URL.

---

### Step 2: Create a Python Virtual Environment

A virtual environment keeps your project dependencies isolated from system Python.

**Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then retry the Activate.ps1 command
```

**Mac/Linux (Bash/Zsh):**

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

**Verify activation:** Your terminal prompt should show `(venv)` at the beginning.

---

### Step 3: Upgrade pip and Install Dependencies

Ensure pip is up to date and install required packages:

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all required dependencies from requirements.txt
pip install -r requirements.txt
```

**Expected packages to be installed:**

- `fastapi==0.128.0` - Web framework
- `uvicorn==0.40.0` - ASGI server
- `psycopg2-binary==2.9.11` - PostgreSQL adapter
- `python-dotenv==1.2.1` - Environment variable management
- `pydantic==2.12.5` - Data validation
- And 20+ other dependencies (see requirements.txt)

---

### Step 4: Create Environment Variables File

Create a `.env` file in the project root directory with the following configuration:

**Windows:** Create file `Hospital Management\.env`
**Mac/Linux:** Create file `Hospital Management/.env`

```env
# Database Configuration
DATABASE_URL=sqlite:///./hospital.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db

# FastAPI Configuration
API_TITLE=MediPortal Multi-Role API
API_VERSION=2.0.0

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

### Step 5: Setup the Database

#### Option A: Using SQLite (Easiest)

The backend is already configured to use SQLite by default. The database will be created automatically when you first run the application.

To seed sample data:

```powershell
# Stay in the project root directory with venv activated
python database/fake_data.py
```

#### Option B: Using PostgreSQL (Advanced)

1. **Install and start PostgreSQL** (if not already running)

2. **Create a database:**

   ```sql
   CREATE DATABASE hospital_db;
   ```

3. **Run the SQL schema:**

   ```powershell
   # Connect to PostgreSQL and run the table setup
   psql -U postgres -d hospital_db -f database/Table.sql
   ```

4. **Seed sample data:**

   ```powershell
   python database/fake_data.py
   ```

5. **Update `.env` file:**
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hospital_db
   ```

---

## Running the Application

You need to run both the backend server and frontend server. **Open two separate terminal windows** for this.

### Terminal 1: Start the Backend Server

With the virtual environment activated, run:

```powershell
# Navigate to project root if not already there
cd "Hospital Management"

# Start the FastAPI backend server
python -m uvicorn backend.main:app --reload
```

**Output should show:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Backend is now running at:** `http://localhost:8000`

---

### Terminal 2: Start the Frontend Server

Open **another terminal window** and run:

```powershell
# Navigate to the frontend directory
cd "Hospital Management\frontend"

# Start the Python HTTP server on port 5500
python -m http.server 5500
```

**Output should show:**

```
Serving HTTP on 0.0.0.0 port 5500 (http://0.0.0.0:5500/) ...
```

**Frontend is now running at:** `http://localhost:5500`

---

### Access the Application

1. **Open your web browser** and navigate to:

   ```
   http://localhost:5500
   ```

2. **Available Pages:**
   - **Main Dashboard:** `http://localhost:5500/index.html`
   - **Admin Panel:** `http://localhost:5500/admin.html`
   - **Doctor Panel:** `http://localhost:5500/doctor.html`
   - **Patient Panel:** `http://localhost:5500/patient.html`
   - **Billing Panel:** `http://localhost:5500/billing.html`
   - **Diagnostic Panel:** `http://localhost:5500/diagnostic.html`

### API Documentation

FastAPI automatically generates interactive API documentation. Access it at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Database Setup

### Database Schema

The database includes tables for:

- **Users** - Admin, Doctors, Patients
- **Appointments** - Doctor-Patient appointments
- **Diagnoses** - Medical diagnoses
- **Billing** - Invoice and payment records

### Generate Sample Data

To populate the database with 100 sample records:

```powershell
python database/fake_data.py
```

### Database File Location

- **SQLite:** `hospital.db` (in project root)
- **PostgreSQL:** Use PostgreSQL admin tools

---

## Running Tests

To run unit tests and validate the system:

```powershell
# Install pytest if not already included
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_admin.py -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=backend
```

---

## Common Commands Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Install new package
pip install package_name

# Export current dependencies
pip freeze > requirements.txt

# Start backend server (development mode with auto-reload)
python -m uvicorn backend.main:app --reload

# Start backend server (production mode)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start frontend server (on port 5500)
cd frontend
python -m http.server 5500

# Start frontend server (on different port, e.g., 8080)
cd frontend
python -m http.server 8080
```

---

## Troubleshooting

### Issue 1: "Python command not found"

**Solution:**

- Ensure Python 3.12 is installed and added to PATH
- Restart terminal after installing Python
- Try `python3` instead of `python`

### Issue 2: "Module not found" error

**Solution:**

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 3: Port 8000 already in use

**Solution:**

```powershell
# Use a different port
python -m uvicorn backend.main:app --reload --port 8001
```

### Issue 4: Database connection error

**Solution:**

- Verify `.env` file exists in project root
- Check `DATABASE_URL` is correct
- For PostgreSQL: ensure PostgreSQL service is running

### Issue 5: CORS error in browser console

**Solution:**

- CORS is already enabled in `backend/main.py`
- Check that frontend is accessing correct API URL: `http://localhost:8000`

### Issue 6: "Permission denied" on Linux/Mac

**Solution:**

```bash
# Make scripts executable
chmod +x venv/bin/activate
```

---

## Project Technology Stack

| Component                | Technology               |
| ------------------------ | ------------------------ |
| Backend                  | Python 3.12 + FastAPI    |
| Frontend                 | HTML5 + CSS + JavaScript |
| Database                 | SQLite / PostgreSQL      |
| Server                   | Uvicorn (ASGI)           |
| Data Validation          | Pydantic                 |
| Task: Generate fake data | Faker                    |

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Virtual Environments](https://docs.python.org/3.12/library/venv.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Git Tutorial](https://git-scm.com/doc)

---

## Support & Contributing

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error messages in the terminal
3. Check API documentation at `http://localhost:8000/docs`
4. Create an issue on GitHub

---

## License

This project is provided as-is for educational purposes.

---

**Last Updated:** January 2026  
**Python Version:** 3.12+
