import os
import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.db import execute_query, get_db_connection

router = APIRouter()

class QueryRequest(BaseModel):
    text: Optional[str] = None
    sql: Optional[str] = None
    username: Optional[str] = "guest"
    role: str = "billing"
    mode: str = "generate"

def generate_billing_sql(text: str) -> str:
    text = text.lower()
    
    # 1. Patients with multiple unpaid invoices (moved to top)
    if "multiple" in text and "unpaid" in text:
        return """
            SELECT p.first_name, p.last_name, COUNT(i.invoice_id) as unpaid_count, SUM(i.amount) as total_due 
            FROM patients p 
            JOIN invoices i ON p.patient_id = i.patient_id 
            WHERE LOWER(i.status) = 'unpaid' 
            GROUP BY p.patient_id, p.first_name, p.last_name 
            HAVING COUNT(i.invoice_id) > 1
        """.strip()

    # 2. Unpaid Invoices
    if "unpaid" in text and "invoice" in text:
        return "SELECT i.invoice_id, p.first_name, p.last_name, i.amount, i.status, i.issue_date FROM invoices i JOIN patients p ON i.patient_id = p.patient_id WHERE LOWER(i.status) = 'unpaid' ORDER BY i.issue_date ASC"

    # 3. Total Pending Amount
    # "Total pending amount" or "Pending revenue"
    if "total" in text and ("pending" in text or "revenue" in text):
        return "SELECT SUM(amount) as total_pending_revenue FROM invoices WHERE LOWER(status) IN ('pending', 'unpaid')"

    # 4. Large Invoices > 10000
    if "10000" in text:
        return "SELECT * FROM invoices WHERE amount > 10000 ORDER BY amount DESC"

    # Default/Fallback
    return "SELECT * FROM invoices ORDER BY issue_date DESC LIMIT 10"

def generate_billing_recommendations(results: List[Dict[str, Any]], query_text: str) -> List[str]:
    recs = []
    text = query_text.lower()
    
    if not results:
        return ["No records found requiring action."]

    # Logic for Unpaid/Pending
    if "unpaid" in text or "pending" in text:
        # Check for high total due in summary query
        if results and 'total_pending_revenue' in results[0]:
             total = results[0]['total_pending_revenue']
             if total and total > 50000:
                  recs.append(f"💰 High outstanding balance (${total}). Initiate bulk reminders.")
        
        # Check for multiple unpaid in list query
        unpaid_count_val = len(results)
        if unpaid_count_val > 50 and 'invoice_id' in results[0]: 
             recs.append(f"High number of unpaid invoices ({unpaid_count_val}). Review collections strategy.")
             
        # Check for specific patients with multiple unpaid
        if 'unpaid_count' in results[0]:
            recs.append("Found patients with repeated unpaid invoices. Escalate to billing manager.")

    return recs

@router.post("/billing/query")
async def billing_query(request: QueryRequest):
    if request.mode == "generate":
        generated_sql = generate_billing_sql(request.text or "")
        try:
            safe_q = (request.text or "").replace("'", "''")
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{request.username or 'guest'}', '{request.role}', '{safe_q}', 'GENERATED')")
        except Exception:
            pass
        return {"generated_sql": generated_sql}
        
    elif request.mode == "execute":
        if not request.sql:
            return {"error": "no sql provided"}
        sql = request.sql.strip()
        
        # SAFETY CHECK: Billing cannot access 'medical_records'
        if "medical_records" in sql.lower() or "diagnosis" in sql.lower() or "treatment_plan" in sql.lower():
            return {"error": "⛔ ACCESS DENIED: Billing cannot view medical records."}
            
        try:
            results = execute_query(sql)
            recs = generate_billing_recommendations(results, request.text or "")
            return {
                "results": results,
                "recommendations": recs
            }
        except Exception as e:
            return {"error": str(e)}

    return {"error": "invalid mode"}

@router.get("/billing/analytics")
def get_billing_analytics():
    try:
        # 1. SUMMARY CARDS
        pending_invoices = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Pending'")[0]['count']
        revenue_today = execute_query("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE issue_date = CURRENT_DATE AND status = 'Paid'")[0]['total']
        overdue_payments = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Unpaid' AND issue_date < CURRENT_DATE - INTERVAL '30 days'")[0]['count']
        
        avg_delay_res = execute_query("SELECT AVG(CURRENT_DATE - issue_date) as days FROM invoices WHERE status = 'Unpaid'")
        avg_delay = int(avg_delay_res[0]['days']) if avg_delay_res and avg_delay_res[0]['days'] else 0

        # 2. REVENUE TREND
        trend_raw = execute_query("SELECT to_char(issue_date, 'Mon DD') as date, SUM(amount) as total FROM invoices WHERE status = 'Paid' GROUP BY 1 ORDER BY MIN(issue_date) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['total'] for row in trend_raw]

        # 3. INVOICE STATUS BREAKDOWN
        status_raw = execute_query("SELECT status, COUNT(*) as count FROM invoices GROUP BY status")
        status_data = {row['status']: row['count'] for row in status_raw}

        # 4. INSURANCE PROVIDER ANALYSIS
        prov_raw = execute_query("SELECT insurance_provider, COUNT(*) as count FROM patients GROUP BY insurance_provider")
        prov_data = {row['insurance_provider']: row['count'] for row in prov_raw}

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
        aging_data = {row['age_group']: row['count'] for row in aging_raw}

        # 6. AI FINANCE QUERIES
        ai_finance = execute_query("SELECT COUNT(*) as count FROM audit_logs WHERE role='billing' AND DATE(timestamp) = CURRENT_DATE")[0]['count']
        most_req = execute_query("SELECT question, COUNT(*) as count FROM audit_logs WHERE role='billing' GROUP BY question ORDER BY count DESC LIMIT 1")
        most_req_txt = most_req[0]['question'] if most_req else "None"

        return {
            "summary": {
                "pending": pending_invoices,
                "revenue_today": revenue_today,
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