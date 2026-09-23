"""Sales and Order Analytics Tools: Deterministic financial and volume calculations."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from backend.database import execute_query, execute_scalar

def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves an order's detail by Order ID."""
    rows = execute_query(
        "SELECT order_id, customer_id, product_id, product_name, category, order_date, quantity, unit_price, amount, status, payment_status "
        "FROM orders WHERE order_id = ?",
        (order_id.strip().upper(),)
    )
    return rows[0] if rows else None

def get_orders(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves list of orders within an optional date range."""
    if start_date and end_date:
        return execute_query(
            "SELECT order_id, customer_id, product_name, category, order_date, amount, status "
            "FROM orders WHERE order_date BETWEEN ? AND ? ORDER BY order_date DESC LIMIT ?",
            (start_date, end_date, limit)
        )
    return execute_query(
        "SELECT order_id, customer_id, product_name, category, order_date, amount, status "
        "FROM orders ORDER BY order_date DESC LIMIT ?",
        (limit,)
    )

def calculate_sales(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Calculates total gross revenue, net completed revenue, and order volume."""
    where_clause = ""
    params: List[Any] = []
    
    if start_date and end_date:
        where_clause = "WHERE order_date BETWEEN ? AND ?"
        params = [start_date, end_date]
        
    query = f"""
    SELECT 
        COUNT(*) as total_orders,
        SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END) as completed_revenue,
        SUM(CASE WHEN status = 'Returned' THEN amount ELSE 0 END) as returned_revenue,
        SUM(CASE WHEN status = 'Cancelled' THEN amount ELSE 0 END) as cancelled_revenue,
        SUM(amount) as gross_booked_revenue,
        COUNT(CASE WHEN status = 'Completed' THEN 1 END) as completed_orders,
        COUNT(CASE WHEN status = 'Returned' THEN 1 END) as returned_orders,
        COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancelled_orders
    FROM orders {where_clause}
    """
    rows = execute_query(query, tuple(params))
    r = rows[0]
    
    total = r["total_orders"] or 0
    completed_rev = round(r["completed_revenue"] or 0.0, 2)
    returned_rev = round(r["returned_revenue"] or 0.0, 2)
    cancelled_rev = round(r["cancelled_revenue"] or 0.0, 2)
    gross_rev = round(r["gross_booked_revenue"] or 0.0, 2)
    
    avg_order_value = round(completed_rev / r["completed_orders"], 2) if r["completed_orders"] else 0.0
    
    return {
        "period": {"start_date": start_date or "All-Time", "end_date": end_date or "All-Time"},
        "total_orders": total,
        "completed_orders": r["completed_orders"],
        "completed_revenue": completed_rev,
        "returned_revenue": returned_rev,
        "cancelled_revenue": cancelled_rev,
        "gross_booked_revenue": gross_rev,
        "average_order_value": avg_order_value
    }

def calculate_return_rate(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Calculates overall return rate and identifies product-level return anomalies."""
    where_clause = ""
    params: List[Any] = []
    if start_date and end_date:
        where_clause = "WHERE order_date BETWEEN ? AND ?"
        params = [start_date, end_date]
        
    # Overall rates
    overview_query = f"""
    SELECT 
        COUNT(*) as total_orders,
        COUNT(CASE WHEN status = 'Returned' THEN 1 END) as returned_orders,
        SUM(CASE WHEN status = 'Returned' THEN amount ELSE 0 END) as total_refunded_amount
    FROM orders {where_clause}
    """
    overview = execute_query(overview_query, tuple(params))[0]
    total_orders = overview["total_orders"] or 1
    returned_orders = overview["returned_orders"] or 0
    overall_return_rate = round((returned_orders / total_orders) * 100, 2)
    
    # Product breakdown with highest return rates (minimum 10 orders to be statistically relevant)
    product_query = f"""
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        COUNT(o.order_id) as total_ordered,
        COUNT(CASE WHEN o.status = 'Returned' THEN 1 END) as return_count,
        ROUND((CAST(COUNT(CASE WHEN o.status = 'Returned' THEN 1 END) AS REAL) / COUNT(o.order_id)) * 100, 2) as return_rate_pct,
        ROUND(SUM(CASE WHEN o.status = 'Returned' THEN o.amount ELSE 0 END), 2) as refund_amount
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    {where_clause}
    GROUP BY p.product_id, p.product_name, p.category
    HAVING total_ordered >= 1 AND return_count > 0
    ORDER BY return_rate_pct DESC
    LIMIT 5
    """
    top_returned_products = execute_query(product_query, tuple(params))
    
    # Return reasons breakdown from returns table
    reasons_query = """
    SELECT reason, COUNT(*) as count, ROUND(SUM(refund_amount), 2) as total_refunds
    FROM returns
    GROUP BY reason
    ORDER BY count DESC
    """
    reasons = execute_query(reasons_query)
    
    return {
        "overall_return_rate_pct": overall_return_rate,
        "total_returned_orders": returned_orders,
        "total_refund_amount": round(overview["total_refunded_amount"] or 0.0, 2),
        "highest_return_products": top_returned_products,
        "return_reasons_breakdown": reasons
    }

def calculate_cancellation_rate(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """Calculates order cancellation rates across products and categories."""
    where_clause = ""
    params: List[Any] = []
    if start_date and end_date:
        where_clause = "WHERE order_date BETWEEN ? AND ?"
        params = [start_date, end_date]
        
    query = f"""
    SELECT 
        COUNT(*) as total_orders,
        COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) as cancelled_orders,
        ROUND((CAST(COUNT(CASE WHEN status = 'Cancelled' THEN 1 END) AS REAL) / COUNT(*)) * 100, 2) as cancellation_rate_pct,
        ROUND(SUM(CASE WHEN status = 'Cancelled' THEN amount ELSE 0 END), 2) as lost_cancellation_revenue
    FROM orders {where_clause}
    """
    res = execute_query(query, tuple(params))[0]
    return {
        "total_orders": res["total_orders"],
        "cancelled_orders": res["cancelled_orders"],
        "cancellation_rate_pct": res["cancellation_rate_pct"] or 0.0,
        "lost_revenue": res["lost_cancellation_revenue"] or 0.0
    }

def get_top_products(by: str = "revenue", limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves top performing products ranked by completed revenue or sales volume."""
    order_col = "total_revenue" if by == "revenue" else "units_sold"
    query = f"""
    SELECT 
        product_id,
        product_name,
        category,
        SUM(quantity) as units_sold,
        ROUND(SUM(amount), 2) as total_revenue,
        COUNT(order_id) as order_count
    FROM orders
    WHERE status = 'Completed'
    GROUP BY product_id, product_name, category
    ORDER BY {order_col} DESC
    LIMIT ?
    """
    return execute_query(query, (limit,))

def compare_sales_periods(current_start: str, current_end: str, prior_start: str, prior_end: str) -> Dict[str, Any]:
    """Directly compares current period vs prior period to answer 'Why did sales fall this week?'."""
    current_sales = calculate_sales(current_start, current_end)
    prior_sales = calculate_sales(prior_start, prior_end)
    
    rev_diff = round(current_sales["completed_revenue"] - prior_sales["completed_revenue"], 2)
    pct_change = round((rev_diff / (prior_sales["completed_revenue"] or 1)) * 100, 2)
    order_diff = current_sales["completed_orders"] - prior_sales["completed_orders"]
    
    # Category breakdown comparison
    cat_query = """
    SELECT 
        category,
        ROUND(SUM(CASE WHEN order_date BETWEEN ? AND ? AND status='Completed' THEN amount ELSE 0 END), 2) as curr_revenue,
        ROUND(SUM(CASE WHEN order_date BETWEEN ? AND ? AND status='Completed' THEN amount ELSE 0 END), 2) as prior_revenue
    FROM orders
    GROUP BY category
    ORDER BY prior_revenue DESC
    """
    category_comparison = execute_query(cat_query, (current_start, current_end, prior_start, prior_end))
    for c in category_comparison:
        diff = round(c["curr_revenue"] - c["prior_revenue"], 2)
        c["revenue_change"] = diff
        c["pct_change"] = round((diff / (c["prior_revenue"] or 1)) * 100, 1)

    return {
        "current_period": {"start": current_start, "end": current_end, "revenue": current_sales["completed_revenue"], "orders": current_sales["completed_orders"]},
        "prior_period": {"start": prior_start, "end": prior_end, "revenue": prior_sales["completed_revenue"], "orders": prior_sales["completed_orders"]},
        "variance": {
            "revenue_difference": rev_diff,
            "percentage_change": pct_change,
            "order_count_difference": order_diff,
            "trend": "Decrease" if rev_diff < 0 else "Increase"
        },
        "category_breakdown": category_comparison
    }
