# 🏥 Hospital Management System

A comprehensive web-based Hospital Management System with AI-powered patient triage, billing management, and multi-portal access for doctors, patients, and administrators.

## ✨ Features

### 🏥 Patient Management

- Patient registration and records
- Emergency intake with AI-powered triage
- Appointment scheduling
- Medical history tracking

### 👨‍⚕️ Doctor Portal

- Patient assignments and schedules
- Consultation management
- Prescription writing
- Department-wise organization

### 💰 Billing & Finance

- Invoice generation and management
- Payment tracking (Paid/Unpaid/Pending)
- Mark payments as received
- Print invoices
- Revenue analytics and dashboards
- AI-powered billing queries

### 🔐 Admin Dashboard

- Hospital-wide analytics
- Doctor and department management
- User management
- System monitoring

### 🤖 AI-Powered Features

- **Smart Triage**: ML-based severity classification (Low/Medium/High/Emergency)
- **Specialist Recommendation**: Auto-suggest appropriate department
- **Multilingual Support**: English, Hindi, Kannada
- **Natural Language Queries**: Ask billing questions in plain English

## 🛠️ Tech Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Backend  | Python, FastAPI         |
| Database | PostgreSQL              |
| Frontend | HTML5, CSS3, JavaScript |
| ML/AI    | Scikit-learn, Pandas    |
| Server   | Uvicorn                 |

## 📁 Project Structure

```
Hospital Management/
├── backend/
│   ├── main.py              # FastAPI application entry
│   ├── db.py                # Database connection & queries
│   ├── routers/
│   │   ├── admin.py         # Admin API endpoints
│   │   ├── billing.py       # Billing & invoice APIs
│   │   ├── doctor.py        # Doctor portal APIs
│   │   ├── patient.py       # Patient management APIs
│   │   └── triage.py        # AI triage APIs
│   ├── core/
│   │   ├── triage_engine.py # ML triage logic
│   │   ├── rule_engine.py   # Business rules
│   │   └── multilingual.py  # Language support
│   └── models/              # ML model files
├── frontend/
│   ├── index.html           # Login page
│   ├── admin.html           # Admin dashboard
│   ├── billing.html         # Billing portal
│   ├── doctor.html          # Doctor portal
│   ├── patient.html         # Patient portal
│   └── emergency_intake.html # Emergency triage
├── database/
│   ├── Table.sql            # Database schema
│   └── hospital_seed_100.sql # Sample data
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

### Quick Start

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd "Hospital Management"
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv

   # Windows
   .\venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**

   Create a `.env` file:

   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db
   ```

5. **Initialize Database**

   ```bash
   # Run the schema
   psql -U postgres -d hospital_db -f database/Table.sql

   # Load sample data
   psql -U postgres -d hospital_db -f database/hospital_seed_100.sql
   ```

6. **Start the Backend**

   ```bash
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```

7. **Serve the Frontend**

   ```bash
   # In a new terminal
   python -m http.server 5500
   ```

8. **Access the Application**
   - Frontend: http://127.0.0.1:5500/frontend/index.html
   - API Docs: http://127.0.0.1:8000/docs

## 🔑 Default Credentials

| Role    | Username  | Password   |
| ------- | --------- | ---------- |
| Admin   | admin     | admin123   |
| Billing | billing   | billing123 |
| Doctor  | dr_sharma | doctor123  |

## 📡 API Endpoints

### Triage

- `POST /api/v1/triage/analyze` - Analyze patient symptoms
- `POST /api/v1/triage/batch` - Batch process patients
- `GET /api/v1/triage/departments` - List departments

### Billing

- `POST /api/v1/billing/query` - AI-powered billing queries
- `GET /api/v1/billing/analytics` - Dashboard analytics
- `PUT /api/v1/billing/update-payment` - Update payment status
- `POST /api/v1/billing/generate-invoice` - Create new invoice
- `GET /api/v1/billing/invoice/{id}` - Get invoice details

### Admin

- `GET /api/v1/admin/analytics` - Hospital statistics
- `GET /api/v1/admin/doctors` - List all doctors
- `GET /api/v1/admin/departments` - List departments

### Doctor

- `GET /api/v1/doctor/patients` - Get assigned patients
- `GET /api/v1/doctor/schedule` - View schedule

## 🧪 Testing

```bash
# Run comprehensive tests
python comprehensive_test.py

# Run specific API tests
python test_billing_api.py
python test_admin_api.py
```

## 📊 Key Metrics

| Metric              | Value          |
| ------------------- | -------------- |
| Departments         | 10             |
| Sample Patients     | 100+           |
| Sample Doctors      | 20+            |
| ML Accuracy         | 95%+           |
| Supported Languages | 3 (EN, HI, KN) |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for better healthcare management**
