#!/usr/bin/env python3
"""
Test script for billing API endpoints
Tests: NLP-to-SQL generation, query execution, unpaid invoices, and payment updates
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"
BILLING_USER = "finance_staff"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_generate_query(query_text: str) -> Dict[str, Any]:
    """Test NLP-to-SQL query generation"""
    print(f"\n📝 Query: '{query_text}'")
    
    payload = {
        "text": query_text,
        "username": BILLING_USER,
        "role": "billing",
        "mode": "generate"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/billing/query", json=payload, timeout=5)
        data = res.json()
        
        if "generated_sql" in data:
            print(f"✓ SQL Generated:")
            print(f"  {data['generated_sql'][:200]}...")
            return data
        else:
            print(f"✗ Error: {data.get('error', 'Unknown error')}")
            return data
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return {}

def test_execute_query(sql: str, query_context: str) -> Dict[str, Any]:
    """Test SQL execution"""
    print(f"\n▶ Executing query...")
    
    payload = {
        "sql": sql,
        "username": BILLING_USER,
        "role": "billing",
        "mode": "execute",
        "text": query_context
    }
    
    try:
        res = requests.post(f"{BASE_URL}/billing/query", json=payload, timeout=10)
        data = res.json()
        
        if "results" in data:
            count = len(data.get("results", []))
            print(f"✓ Query executed successfully")
            print(f"  Records returned: {count}")
            
            if count > 0:
                print(f"  Sample record: {json.dumps(data['results'][0], indent=2, default=str)[:300]}...")
            
            if data.get("recommendations"):
                print(f"  Recommendations:")
                for rec in data["recommendations"][:2]:
                    print(f"    - {rec}")
            
            return data
        else:
            print(f"✗ Error: {data.get('error', 'Unknown error')}")
            return data
    except Exception as e:
        print(f"✗ Execution error: {e}")
        return {}

def test_get_unpaid_invoices() -> Dict[str, Any]:
    """Test /billing/unpaid-invoices endpoint"""
    print(f"\n📋 Fetching unpaid invoices...")
    
    try:
        res = requests.get(f"{BASE_URL}/billing/unpaid-invoices", timeout=10)
        data = res.json()
        
        if data.get("status") == "success":
            count = len(data.get("invoices", []))
            print(f"✓ Unpaid invoices retrieved")
            print(f"  Total unpaid: {count}")
            
            if count > 0:
                inv = data["invoices"][0]
                print(f"  Sample: Invoice #{inv.get('invoice_id')} - {inv.get('first_name')} {inv.get('last_name')} - ${inv.get('total_amount')}")
                print(f"  Priority: {inv.get('priority')} ({inv.get('days_outstanding')} days outstanding)")
            
            return data
        else:
            print(f"✗ Error: {data.get('error', 'Unknown error')}")
            return data
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return {}

def test_get_analytics() -> Dict[str, Any]:
    """Test /billing/payment-analytics endpoint"""
    print(f"\n📊 Fetching analytics...")
    
    try:
        res = requests.get(f"{BASE_URL}/billing/payment-analytics", timeout=10)
        data = res.json()
        
        if data.get("status") == "success":
            summary = data.get("summary", {})
            print(f"✓ Analytics retrieved")
            print(f"  Pending count: {summary.get('pending_count', 0)}")
            print(f"  Overdue count: {summary.get('overdue_count', 0)}")
            print(f"  Revenue today: ${summary.get('revenue_today', 0)}")
            print(f"  Pending revenue: ${summary.get('pending_revenue', 0)}")
            
            status_data = data.get("status_breakdown", [])
            if status_data:
                print(f"  Status breakdown: {status_data[:2]}")
            
            return data
        else:
            print(f"✗ Error: {data.get('error', 'Unknown error')}")
            return data
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return {}

def test_update_payment(invoice_id: int, amount: float) -> Dict[str, Any]:
    """Test payment update endpoint"""
    print(f"\n💳 Updating payment for invoice #{invoice_id}...")
    
    payload = {
        "invoice_id": invoice_id,
        "status": "Paid",
        "payment_amount": amount,
        "payment_date": "2024-01-15",
        "notes": "Payment received and processed"
    }
    
    try:
        res = requests.put(f"{BASE_URL}/billing/update-payment", json=payload, timeout=5)
        data = res.json()
        
        if data.get("status") == "success":
            print(f"✓ Payment updated successfully")
            print(f"  Invoice: {data.get('invoice', {})}")
            return data
        else:
            print(f"✗ Error: {data.get('error', 'Unknown error')}")
            return data
    except Exception as e:
        print(f"✗ Update error: {e}")
        return {}

def main():
    print_section("BILLING API TEST SUITE")
    print("Testing NLP-to-SQL generation, query execution, and payment updates")
    
    # Test 1: NLP queries
    print_section("TEST 1: NLP-to-SQL Query Generation")
    
    test_queries = [
        "Show all unpaid invoices",
        "Find overdue payments",
        "What is the total pending revenue?",
        "Show high value invoices over $5000",
        "List today's revenue"
    ]
    
    for query in test_queries:
        result = test_generate_query(query)
        if "generated_sql" in result:
            # Execute the generated SQL
            test_execute_query(result["generated_sql"], query)
    
    # Test 2: Get unpaid invoices
    print_section("TEST 2: Direct Unpaid Invoices Endpoint")
    unpaid_result = test_get_unpaid_invoices()
    
    # Test 3: Get analytics
    print_section("TEST 3: Payment Analytics")
    analytics = test_get_analytics()
    
    # Test 4: Update payment (if we have unpaid invoices)
    print_section("TEST 4: Payment Status Update")
    if unpaid_result.get("invoices") and len(unpaid_result["invoices"]) > 0:
        first_invoice = unpaid_result["invoices"][0]
        test_update_payment(first_invoice["invoice_id"], first_invoice["total_amount"])
    else:
        print("⚠ No unpaid invoices available for payment update test")
    
    print_section("TEST SUMMARY")
    print("✓ All endpoint tests completed")
    print("✓ Check results above for any errors or issues")
    print("✓ Frontend should now display real invoice data\n")

if __name__ == "__main__":
    main()
