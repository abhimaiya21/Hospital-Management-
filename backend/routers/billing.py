from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.db import execute_query

router = APIRouter()

class QueryRequest(BaseModel):
    text: Optional[str] = None
    sql: Optional[str] = None
    username: Optional[str] = "guest"
    role: str = "billing"
    mode: str = "generate"

@router.post("/billing/query")
async def billing_query(request: QueryRequest):
    if request.mode == "generate":
        mapping = {
            "unpaid": "SELECT * FROM invoices WHERE LOWER(status) = 'unpaid' ORDER BY created_at DESC LIMIT 100",
            "10000": "SELECT * FROM invoices WHERE amount > 10000 ORDER BY amount DESC",
            "pending revenue": "SELECT SUM(amount) as pending_total FROM invoices WHERE LOWER(status) = 'unpaid' OR status = 'Pending'",
            "overdue": "SELECT * FROM invoices WHERE LOWER(status) = 'overdue'"
        }
        
        generated = "SELECT * FROM invoices LIMIT 50"
        req_lower = (request.text or "").lower()
        for key, sql in mapping.items():
            if key in req_lower:
                generated = sql
                break

        try:
            safe_q = (request.text or "").replace("'", "''")
            execute_query(f"INSERT INTO audit_logs (username, role, question, status) VALUES ('{request.username or 'guest'}', '{request.role}', '{safe_q}', 'GENERATED')")
        except Exception:
            pass
        return {"generated_sql": generated}
    elif request.mode == "execute":
        if not request.sql:
            return {"error": "no sql provided"}
        sql = request.sql.strip()
        if not sql.lower().startswith("select"):
            return {"error": "only SELECT queries allowed"}
        try:
            results = execute_query(sql)
            return {"results": results}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "invalid mode"}

@router.get("/billing/analytics")
def get_billing_analytics():
    try:
        # 1. SUMMARY CARDS
        # Assuming table 'invoices' has columns: invoice_id, amount, status, issue_date (timestamp/date)
        pending_invoices = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Pending'")[0]['count']
        revenue_today = execute_query("SELECT COALESCE(SUM(amount), 0) as total FROM invoices WHERE issue_date = CURRENT_DATE AND status = 'Paid'")[0]['total']
        # Proxy Overdue: Unpaid invoices older than 30 days
        overdue_payments = execute_query("SELECT COUNT(*) as count FROM invoices WHERE status = 'Unpaid' AND issue_date < CURRENT_DATE - INTERVAL '30 days'")[0]['count']
        
        # Calc average delay: simple proxy using age of unpaid invoices
        avg_delay_res = execute_query("SELECT AVG(CURRENT_DATE - issue_date) as days FROM invoices WHERE status = 'Unpaid'")
        avg_delay = int(avg_delay_res[0]['days']) if avg_delay_res and avg_delay_res[0]['days'] else 0

        # 2. REVENUE TREND (Last 7 Days)
        trend_raw = execute_query("SELECT to_char(issue_date, 'Mon DD') as date, SUM(amount) as total FROM invoices WHERE status = 'Paid' GROUP BY 1 ORDER BY MIN(issue_date) LIMIT 7")
        trend_labels = [row['date'] for row in trend_raw]
        trend_values = [row['total'] for row in trend_raw]

        # 3. INVOICE STATUS BREAKDOWN
        status_raw = execute_query("SELECT status, COUNT(*) as count FROM invoices GROUP BY status")
        status_data = {row['status']: row['count'] for row in status_raw}

        # 4. INSURANCE PROVIDER ANALYSIS
        # Using patients table to link insurance provider to mock claims volume
        prov_raw = execute_query("SELECT insurance_provider, COUNT(*) as count FROM patients GROUP BY insurance_provider")
        prov_data = {row['insurance_provider']: row['count'] for row in prov_raw}

        # 5. INVOICE AGING (Proxied from issue_date)
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