import os
import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.db import execute_query

router = APIRouter()

class QueryRequest(BaseModel):
    text: Optional[str] = None
    sql: Optional[str] = None
    username: Optional[str] = "guest"
    role: str = "billing"
    mode: str = "generate"

class PaymentUpdateRequest(BaseModel):
    invoice_id: int
    status: str  # 'Paid', 'Unpaid', 'Pending', etc.
    payment_amount: Optional[float] = None
    payment_date: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreateRequest(BaseModel):
    patient_id: int
    consultation_charges: Optional[float] = 0
    room_charges: Optional[float] = 0
    medication_charges: Optional[float] = 0
    lab_charges: Optional[float] = 0
    surgery_charges: Optional[float] = 0
    other_charges: Optional[float] = 0
    tax_percentage: Optional[float] = 5.0
    discount_percentage: Optional[float] = 0
    insurance_claim_amount: Optional[float] = 0
    due_days: Optional[int] = 30
    appointment_id: Optional[int] = None
    admission_id: Optional[int] = None

def is_safe_billing_sql(sql: str) -> bool:
    """Prevent access to sensitive clinical data"""
    if not sql:
        return False
    s = sql.lower()
    
    # Forbid destructive operations
    forbidden_keywords = ["drop ", "delete ", "truncate ", "alter ", "create ", "exec", "update ", "insert "]
    for kw in forbidden_keywords:
        if kw in s:
            return False
    
    # Forbid clinical data access
    forbidden_tables = ["medical_records", "prescriptions", "lab_tests", "allergies", "diagnosi"]
    for table in forbidden_tables:
        if table in s:
            return False
    
    return True

def generate_billing_sql(text: str) -> str:
    """Expert NLP-to-SQL for billing queries - PostgreSQL optimized"""
    if not text:
        return "INVALID_SQL_REQUEST"
    
    text_lower = text.lower().strip()
    
    # Mapping of natural language patterns to SQL queries
    mapping = {
        # --- ALL UNPAID INVOICES (MAIN) ---
        "unpaid": """
            SELECT 
                i.invoice_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                COALESCE(p.contact_number, 'N/A') as contact_number,
                i.total_amount,
                i.status,
                i.issue_date,
                COALESCE(i.due_date, i.issue_date + INTERVAL '30 days') as due_date,
                CAST(CURRENT_DATE - i.issue_date AS INTEGER) as days_outstanding,
                CASE 
                    WHEN CURRENT_DATE - i.issue_date > 90 THEN 'Critical'
                    WHEN CURRENT_DATE - i.issue_date > 60 THEN 'Overdue'
                    WHEN CURRENT_DATE - i.issue_date > 30 THEN 'Due Soon'
                    ELSE 'Current'
                END as priority
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE LOWER(i.status) IN ('unpaid', 'pending')
            ORDER BY days_outstanding DESC, i.total_amount DESC
            LIMIT 500
        """,
        
        # --- PENDING INVOICES ---
        "pending": """
            SELECT 
                i.invoice_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                i.total_amount,
                i.status,
                i.issue_date,
                COALESCE(i.due_date, CURRENT_DATE + INTERVAL '30 days') as due_date
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE i.status = 'Pending'
            ORDER BY i.issue_date ASC
            LIMIT 200
        """,
        
        # --- OVERDUE INVOICES ---
        "overdue": """
            SELECT 
                i.invoice_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                i.total_amount,
                CAST(CURRENT_DATE - i.issue_date AS INTEGER) as days_overdue,
                i.status
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE LOWER(i.status) IN ('unpaid', 'pending')
              AND CURRENT_DATE > COALESCE(i.due_date, i.issue_date + INTERVAL '30 days')
            ORDER BY days_overdue DESC
            LIMIT 100
        """,
        
        # --- TOTAL REVENUE / PENDING REVENUE ---
        "revenue": """
            SELECT 
                COUNT(CASE WHEN status = 'Paid' THEN 1 END)::BIGINT as paid_count,
                COUNT(CASE WHEN status IN ('Unpaid', 'Pending') THEN 1 END)::BIGINT as unpaid_count,
                COALESCE(SUM(CASE WHEN status = 'Paid' THEN total_amount ELSE 0 END), 0)::NUMERIC as total_paid,
                COALESCE(SUM(CASE WHEN status IN ('Unpaid', 'Pending') THEN total_amount ELSE 0 END), 0)::NUMERIC as total_pending,
                COALESCE(SUM(total_amount), 0)::NUMERIC as total_revenue
            FROM invoices
        """,
        
        # --- HIGH VALUE INVOICES ---
        "high value": """
            SELECT 
                i.invoice_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                i.total_amount,
                i.status,
                i.issue_date
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE i.total_amount > 5000
            ORDER BY i.total_amount DESC
            LIMIT 50
        """,
        
        # --- PAID INVOICES ---
        "paid": """
            SELECT 
                i.invoice_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                i.total_amount,
                i.status,
                i.issue_date,
                COALESCE(i.payment_date, CURRENT_DATE) as payment_date
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE i.status = 'Paid'
            ORDER BY i.payment_date DESC
            LIMIT 100
        """,
        
        # --- TODAY'S REVENUE ---
        "today": """
            SELECT 
                COUNT(*) as invoice_count,
                COALESCE(SUM(total_amount), 0)::NUMERIC as daily_total,
                COUNT(CASE WHEN status = 'Paid' THEN 1 END) as paid_today,
                COUNT(CASE WHEN status IN ('Unpaid', 'Pending') THEN 1 END) as unpaid_today
            FROM invoices
            WHERE DATE(issue_date) = CURRENT_DATE
        """,
        
        # --- PATIENT INVOICE HISTORY ---
        "patient": """
            SELECT 
                i.invoice_id,
                i.total_amount,
                i.status,
                i.issue_date,
                COALESCE(i.due_date, i.issue_date + INTERVAL '30 days') as due_date
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            ORDER BY i.issue_date DESC
            LIMIT 100
        """,
    }
    
    # Try to match keywords
    for key, sql in mapping.items():
        if key in text_lower:
            return sql
    
    # DEFAULT: Show all unpaid invoices (safest default)
    return mapping["unpaid"]

def generate_billing_recommendations(results: List[Dict[str, Any]], query_text: str) -> List[str]:
    """Generate actionable recommendations based on billing data"""
    recs = []
    
    if not results or len(results) == 0:
        return ["No records found. All invoices appear to be paid."]
    
    text = query_text.lower()
    
    # --- UNPAID ANALYSIS ---
    if "unpaid" in text or "pending" in text:
        unpaid_count = len(results)
        
        if unpaid_count > 100:
            recs.append(f"⚠️ High Volume: {unpaid_count} unpaid invoices. Consider batch collection campaigns.")
        
        # Calculate total outstanding
        if all('total_amount' in r for r in results):
            total_outstanding = sum(float(r.get('total_amount', 0)) for r in results if r.get('total_amount'))
            if total_outstanding > 100000:
                recs.append(f"💰 Critical: ${total_outstanding:,.2f} outstanding. Escalate to management.")
        
        # Check for critical overdue
        if any('days_outstanding' in r for r in results):
            critical_items = [r for r in results if r.get('days_outstanding', 0) > 90]
            if len(critical_items) > 0:
                recs.append(f"🚨 Action Required: {len(critical_items)} invoices over 90 days old. Initiate collection.")
    
    # --- REVENUE ANALYSIS ---
    if "revenue" in text:
        if all('total_pending' in r for r in results):
            pending = sum(float(r.get('total_pending', 0)) for r in results)
            if pending > 50000:
                recs.append(f"📊 Cash Flow Alert: ${pending:,.2f} pending. Monitor collection closely.")
    
    return recs if recs else ["Analysis complete. No immediate actions required."]


@router.post("/billing/query")
async def billing_query(request: QueryRequest):
    """Expert NLP-to-SQL query engine for billing"""
    if request.mode == "generate":
        # Generate SQL from natural language
        generated_sql = generate_billing_sql(request.text or "")
        
        if generated_sql == "INVALID_SQL_REQUEST":
            return {
                "error": "Could not generate query from your input",
                "hint": "Try: 'Show unpaid invoices', 'Find overdue payments', 'Total revenue'",
                "code": "GENERATION_FAILED"
            }
        
        # Audit log
        try:
            safe_q = (request.text or "").replace("'", "''")[:500]
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{(request.username or 'guest').replace(chr(39), chr(39)+chr(39))}', 'billing', '{safe_q}', 'GENERATED')")
        except:
            pass
        
        return {
            "generated_sql": generated_sql,
            "status": "success"
        }
        
    elif request.mode == "execute":
        # Execute generated SQL
        if not request.sql:
            return {"error": "No SQL provided", "code": "MISSING_SQL"}
        
        if len(request.sql) > 5000:
            return {"error": "Query too long", "code": "QUERY_TOO_LONG"}
        
        if not is_safe_billing_sql(request.sql):
            return {"error": "Query rejected - access to clinical data prohibited", "code": "UNSAFE_QUERY"}
        
        try:
            results = execute_query(request.sql)
            
            if not results:
                return {
                    "results": [],
                    "recommendations": ["No records found."],
                    "count": 0
                }
            
            recs = generate_billing_recommendations(results, request.text or "")
            
            return {
                "results": results,
                "recommendations": recs,
                "count": len(results),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": f"Query execution failed",
                "details": str(e)[:200],
                "code": "EXECUTION_ERROR"
            }
    
    return {"error": "Invalid mode", "code": "INVALID_MODE"}


@router.get("/billing/analytics")
def get_billing_analytics():
    """Get billing analytics matching frontend expected format"""
    try:
        # 1. SUMMARY CARDS
        pending_invoices = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Pending'")[0]['count']
        
        # Revenue today
        rev_res = execute_query("SELECT COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE issue_date = CURRENT_DATE AND status = 'Paid'")
        revenue_today = rev_res[0]['total'] if rev_res else 0
        
        overdue_payments = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Unpaid' AND issue_date < CURRENT_DATE - INTERVAL '30 days'")[0]['count']
        
        avg_delay_res = execute_query("SELECT AVG(CURRENT_DATE - issue_date) as days FROM invoices WHERE status = 'Unpaid'")
        if avg_delay_res and avg_delay_res[0]['days'] is not None:
             avg_delay = int(avg_delay_res[0]['days'])
        else:
             avg_delay = 0

        # 2. REVENUE TREND
        trend_raw = execute_query("SELECT to_char(issue_date, 'Mon DD') as date, COALESCE(SUM(total_amount), 0) as total FROM invoices WHERE status = 'Paid' GROUP BY 1 ORDER BY MIN(issue_date) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw] if trend_raw else []
        trend_values = [float(row['total']) for row in trend_raw] if trend_raw else []

        # 3. INVOICE STATUS BREAKDOWN
        status_raw = execute_query("SELECT status, COUNT(*) as count FROM invoices GROUP BY status")
        status_data = {row['status']: row['count'] for row in status_raw} if status_raw else {}

        # 4. INSURANCE PROVIDER ANALYSIS
        prov_raw = execute_query("SELECT insurance_provider, COUNT(*) as count FROM patients GROUP BY insurance_provider")
        prov_data = {row['insurance_provider']: row['count'] for row in prov_raw} if prov_raw else {}

        # 5. INVOICE AGING
        aging_sql = """
            SELECT 
                CASE 
                    WHEN CURRENT_DATE - issue_date <= 7 THEN '0-7 Days'
                    WHEN CURRENT_DATE - issue_date <= 30 THEN '7-30 Days'
                    ELSE '30+ Days'
                END as age_group,
                COUNT(*) as count
            FROM invoices
            WHERE status != 'Paid'
            GROUP BY 1
        """
        aging_raw = execute_query(aging_sql)
        aging_data = {row['age_group']: row['count'] for row in aging_raw} if aging_raw else {}

        # 6. AI FINANCE QUERIES
        try:
            ai_finance = execute_query("SELECT COUNT(*) as count FROM audit_logs WHERE role='billing' AND DATE(timestamp) = CURRENT_DATE")[0]['count']
            most_req = execute_query("SELECT question, COUNT(*) as count FROM audit_logs WHERE role='billing' GROUP BY question ORDER BY count DESC LIMIT 1")
            most_req_txt = most_req[0]['question'] if most_req else "None"
        except:
            ai_finance = 0
            most_req_txt = "None"

        return {
            "summary": {
                "pending": pending_invoices,
                "revenue_today": float(revenue_today) if revenue_today else 0,
                "overdue": overdue_payments,
                "delay": avg_delay
            },
            "trend": {"labels": trend_labels, "data": trend_values},
            "status": status_data,
            "insurance": prov_data,
            "aging": aging_data,
            "ai": {"count": ai_finance, "top_query": most_req_txt}
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/billing/unpaid-invoices")
def get_unpaid_invoices():
    """Get all unpaid invoices for dashboard display"""
    try:
        query = """
            SELECT 
                i.invoice_id,
                p.patient_id,
                COALESCE(p.first_name, 'Unknown') as first_name,
                COALESCE(p.last_name, 'Unknown') as last_name,
                i.total_amount,
                i.status,
                i.issue_date,
                COALESCE(i.due_date, i.issue_date + INTERVAL '30 days') as due_date,
                CAST(CURRENT_DATE - i.issue_date AS INTEGER) as days_outstanding,
                CASE 
                    WHEN CURRENT_DATE - i.issue_date > 90 THEN 'Critical'
                    WHEN CURRENT_DATE - i.issue_date > 60 THEN 'Overdue'
                    WHEN CURRENT_DATE - i.issue_date > 30 THEN 'Due Soon'
                    ELSE 'Current'
                END as priority
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE LOWER(i.status) IN ('unpaid', 'pending')
            ORDER BY days_outstanding DESC, i.total_amount DESC
            LIMIT 500
        """
        results = execute_query(query)
        return {
            "invoices": results,
            "count": len(results) if results else 0,
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.put("/billing/update-payment")
async def update_payment(request: PaymentUpdateRequest):
    """Update invoice payment status"""
    try:
        # Validate input
        if request.invoice_id <= 0:
            return {"error": "Invalid invoice ID", "status": "failed"}
        
        valid_statuses = ['Paid', 'Unpaid', 'Pending', 'Cancelled', 'Partial', 'Insurance-Claim']
        if request.status not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {valid_statuses}", "status": "failed"}
        
        # Build update query based on actual table columns
        payment_date = f"'{request.payment_date}'" if request.payment_date else "CURRENT_TIMESTAMP"
        amount_paid = request.payment_amount if request.payment_amount else 0
        
        # Get current invoice info first
        check_query = f"SELECT invoice_id, total_amount, amount_paid FROM invoices WHERE invoice_id = {request.invoice_id}"
        existing = execute_query(check_query)
        
        if not existing:
            return {"error": "Invoice not found", "status": "failed"}
        
        update_query = f"""
            UPDATE invoices
            SET status = '{request.status}',
                payment_date = {payment_date},
                amount_paid = {amount_paid}
            WHERE invoice_id = {request.invoice_id}
            RETURNING invoice_id, status, payment_date, total_amount, amount_paid
        """
        
        result = execute_query(update_query)
        
        if result:
            return {
                "message": f"Invoice {request.invoice_id} updated to {request.status}",
                "invoice": result[0],
                "status": "success"
            }
        else:
            return {"error": "Failed to update invoice", "status": "failed"}
            
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.get("/billing/payment-analytics")
def get_payment_analytics():
    """Get real-time payment analytics for dashboard"""
    try:
        # Summary cards
        summary_query = """
            SELECT 
                COUNT(CASE WHEN status = 'Pending' THEN 1 END) as pending_count,
                COUNT(CASE WHEN status IN ('Unpaid', 'Pending') AND CURRENT_DATE > (issue_date + INTERVAL '30 days') THEN 1 END) as overdue_count,
                COALESCE(SUM(CASE WHEN DATE(issue_date) = CURRENT_DATE AND status = 'Paid' THEN total_amount ELSE 0 END), 0) as revenue_today,
                COALESCE(SUM(CASE WHEN status IN ('Unpaid', 'Pending') THEN total_amount ELSE 0 END), 0) as pending_revenue
            FROM invoices
        """
        
        summary = execute_query(summary_query)[0] if execute_query(summary_query) else {}
        
        # Invoice status breakdown
        status_query = """
            SELECT status, COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
            FROM invoices
            GROUP BY status
            ORDER BY count DESC
        """
        
        status_data = execute_query(status_query) or []
        
        # Revenue trend (last 7 days)
        trend_query = """
            SELECT 
                TO_CHAR(issue_date, 'Mon DD') as date,
                COALESCE(SUM(CASE WHEN status = 'Paid' THEN total_amount ELSE 0 END), 0) as paid,
                COALESCE(SUM(CASE WHEN status IN ('Unpaid', 'Pending') THEN total_amount ELSE 0 END), 0) as unpaid
            FROM invoices
            WHERE issue_date >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY TO_CHAR(issue_date, 'Mon DD'), issue_date
            ORDER BY issue_date ASC
        """
        
        trend_data = execute_query(trend_query) or []
        
        # Invoice aging
        aging_query = """
            SELECT 
                CASE 
                    WHEN CURRENT_DATE - issue_date <= 7 THEN '0-7 Days'
                    WHEN CURRENT_DATE - issue_date <= 30 THEN '7-30 Days'
                    WHEN CURRENT_DATE - issue_date <= 60 THEN '30-60 Days'
                    ELSE '60+ Days'
                END as age_group,
                COUNT(*) as count,
                COALESCE(SUM(total_amount), 0) as total
            FROM invoices
            WHERE status IN ('Unpaid', 'Pending')
            GROUP BY age_group
            ORDER BY 
                CASE age_group
                    WHEN '0-7 Days' THEN 1
                    WHEN '7-30 Days' THEN 2
                    WHEN '30-60 Days' THEN 3
                    ELSE 4
                END
        """
        
        aging_data = execute_query(aging_query) or []
        
        return {
            "summary": summary,
            "status_breakdown": status_data,
            "revenue_trend": trend_data,
            "invoice_aging": aging_data,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.post("/billing/generate-invoice")
async def generate_invoice(request: InvoiceCreateRequest):
    """Generate a new invoice for a patient"""
    try:
        # Validate patient exists
        patient_check = execute_query(f"SELECT patient_id, first_name, last_name FROM patients WHERE patient_id = {request.patient_id}")
        if not patient_check:
            return {"error": "Patient not found", "status": "failed"}
        
        patient = patient_check[0]
        
        # Calculate amounts
        subtotal = (request.consultation_charges + request.room_charges + 
                   request.medication_charges + request.lab_charges + 
                   request.surgery_charges + request.other_charges)
        
        tax_amount = round(subtotal * (request.tax_percentage / 100), 2)
        discount_amount = round(subtotal * (request.discount_percentage / 100), 2)
        total_amount = round(subtotal + tax_amount - discount_amount, 2)
        patient_payable = round(total_amount - request.insurance_claim_amount, 2)
        
        # Build insert query
        appointment_id = request.appointment_id if request.appointment_id else "NULL"
        admission_id = request.admission_id if request.admission_id else "NULL"
        
        insert_query = f"""
            INSERT INTO invoices (
                patient_id, appointment_id, admission_id,
                consultation_charges, room_charges, medication_charges,
                lab_charges, surgery_charges, other_charges,
                tax_percentage, tax_amount, 
                discount_percentage, discount_amount,
                total_amount, insurance_claim_amount, patient_payable,
                status, issue_date, due_date
            ) VALUES (
                {request.patient_id}, {appointment_id}, {admission_id},
                {request.consultation_charges}, {request.room_charges}, {request.medication_charges},
                {request.lab_charges}, {request.surgery_charges}, {request.other_charges},
                {request.tax_percentage}, {tax_amount},
                {request.discount_percentage}, {discount_amount},
                {total_amount}, {request.insurance_claim_amount}, {patient_payable},
                'Unpaid', CURRENT_DATE, CURRENT_DATE + INTERVAL '{request.due_days} days'
            )
            RETURNING invoice_id, patient_id, total_amount, patient_payable, status, issue_date, due_date
        """
        
        result = execute_query(insert_query)
        
        if result:
            invoice = result[0]
            return {
                "message": f"Invoice #{invoice['invoice_id']} created successfully",
                "invoice": {
                    **invoice,
                    "patient_name": f"{patient['first_name']} {patient['last_name']}",
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "discount_amount": discount_amount
                },
                "status": "success"
            }
        else:
            return {"error": "Failed to create invoice", "status": "failed"}
            
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.get("/billing/invoice/{invoice_id}")
async def get_invoice_details(invoice_id: int):
    """Get detailed invoice information for printing/viewing"""
    try:
        query = f"""
            SELECT 
                i.*,
                p.first_name, p.last_name, p.contact_number, p.email,
                p.address, p.city, p.state, p.pincode,
                p.insurance_provider, p.insurance_number
            FROM invoices i
            INNER JOIN patients p ON i.patient_id = p.patient_id
            WHERE i.invoice_id = {invoice_id}
        """
        
        result = execute_query(query)
        
        if result:
            invoice = result[0]
            return {
                "invoice": invoice,
                "status": "success"
            }
        else:
            return {"error": "Invoice not found", "status": "failed"}
            
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.get("/billing/patients-list")
async def get_patients_for_billing():
    """Get list of patients for invoice creation dropdown"""
    try:
        query = """
            SELECT 
                patient_id, 
                first_name, 
                last_name, 
                contact_number,
                insurance_provider
            FROM patients 
            WHERE is_active = TRUE
            ORDER BY last_name, first_name
            LIMIT 500
        """
        
        result = execute_query(query)
        
        return {
            "patients": result or [],
            "count": len(result) if result else 0,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}