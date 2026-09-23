"""Customer Intelligence Tools: Deterministic customer fact extraction and segmentation."""

from typing import Any, Dict, List, Optional
from backend.database import execute_query, execute_scalar

def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves single customer profile by Customer ID."""
    rows = execute_query(
        "SELECT customer_id, name, email, phone, city, customer_type, total_orders, total_spent, last_order_date, is_inactive "
        "FROM customers WHERE customer_id = ?",
        (customer_id.strip().upper(),)
    )
    return rows[0] if rows else None

def get_customer_orders(customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves recent orders placed by a specific customer."""
    return execute_query(
        "SELECT order_id, product_id, product_name, category, order_date, quantity, amount, status "
        "FROM orders WHERE customer_id = ? ORDER BY order_date DESC LIMIT ?",
        (customer_id.strip().upper(), limit)
    )

def get_customer_status(customer_id: str) -> Dict[str, Any]:
    """Evaluates customer tier, lifetime value, and inactivity risk status."""
    cust = get_customer(customer_id)
    if not cust:
        return {"error": f"Customer ID '{customer_id}' not found."}
        
    recent_orders = get_customer_orders(customer_id, limit=5)
    return {
        "customer_id": cust["customer_id"],
        "name": cust["name"],
        "tier": cust["customer_type"],
        "total_spent": cust["total_spent"],
        "total_orders": cust["total_orders"],
        "last_order_date": cust["last_order_date"],
        "is_inactive": bool(cust["is_inactive"]),
        "recent_orders_count": len(recent_orders),
        "risk_level": "High (Inactive VIP)" if (cust["is_inactive"] and cust["total_spent"] >= 2000) 
                      else ("Moderate (Inactive)" if cust["is_inactive"] else "Low (Active)")
    }

def find_inactive_customers(min_days_inactive: int = 60, min_spent: float = 0.0) -> Dict[str, Any]:
    """Finds customers with no recent orders and filters by minimum historical spend."""
    rows = execute_query(
        "SELECT customer_id, name, city, customer_type, total_orders, total_spent, last_order_date "
        "FROM customers WHERE is_inactive = 1 AND total_spent >= ? "
        "ORDER BY total_spent DESC",
        (min_spent,)
    )
    
    tier_counts = {"Platinum": 0, "Gold": 0, "Silver": 0, "Standard": 0}
    for r in rows:
        tier = r["customer_type"]
        if tier in tier_counts:
            tier_counts[tier] += 1
            
    return {
        "total_inactive_count": len(rows),
        "criteria": {"min_days_inactive": min_days_inactive, "min_spent": min_spent},
        "tier_distribution": tier_counts,
        "sample_customers": rows[:15],  # top 15 by lifetime spend
        "total_addressable_historical_spend": round(sum(r["total_spent"] for r in rows), 2)
    }

def get_high_value_customers(min_spend: float = 2500.0) -> Dict[str, Any]:
    """Retrieves VIP customers (Gold and Platinum) to target for retention."""
    rows = execute_query(
        "SELECT customer_id, name, city, customer_type, total_orders, total_spent, last_order_date, is_inactive "
        "FROM customers WHERE total_spent >= ? ORDER BY total_spent DESC",
        (min_spend,)
    )
    
    inactive_vips = [r for r in rows if r["is_inactive"]]
    
    return {
        "high_value_count": len(rows),
        "inactive_vip_count": len(inactive_vips),
        "inactive_vips": inactive_vips,
        "top_vip_customers": rows[:10]
    }
