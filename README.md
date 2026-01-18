# Hospital Management System

A comprehensive web-based Hospital Management System designed to streamline hospital operations, including patient management, doctor scheduling, billing, and intelligent patient intake.

## Features

### 🏥 Patient Management
- **Admit & Discharge**: Easily admit new patients and discharge them with generated summaries.
- **Patient Records**: Maintain detailed records of patient history, diagnosis, and treatment.
- **Emergency Intake**: Dedicated workflow for emergency cases with ML-based severity triage.

### 👨‍⚕️ Doctor & Staff Portal
- **Dual Login System**: Secure login for Admin and Doctors.
- **Doctor Dashboard**: View assigned patients, upcoming appointments, and daily schedules.
- **Availability Management**: Doctors can set their availability and consultation hours.

### 🤖 Intelligent Features
- **AI-Powered Triage**: Uses Machine Learning (Scikit-learn) to classify patient symptoms into severity levels (Low, Medium, High, Emergency) and recommend appropriate specialists.
- **Smart Room Allocation**: Automatically suggests General Ward or ICU based on severity and availability.

### 💰 Billing & Admin
- **Invoicing**: Generate detailed bills for treatments, room charges, and medicines.
- **Dashboard Analytics**: Real-time overview of hospital stats (Total Patients, Revenue, Occupancy).

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Machine Learning**: Scikit-learn, Pandas
- **Server**: Uvicorn

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL installed and running
- Git

### Steps

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd "Hospital Management"
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Configuration**
    - Ensure PostgreSQL is running.
    - Update database credentials in the `.env` file or configuration settings (e.g., `db.py`).

5.  **Run the Application**
    ```bash
    uvicorn backend.main:app --reload
    ```
    The API will be available at `http://localhost:8000`.
    The Frontend can be accessed via `index.html` (or served via the backend if configured).

## Usage

1.  **Admin Login**: Access the Admin Dashboard to manage doctors, view revenue, and oversee hospital operations.
2.  **Patient Intake**: Use the intake form to register new patients. The system will auto-classify severity.
3.  **Doctor View**: Doctors log in to see their specific patient list and manage appointments.

## License
MIT License
