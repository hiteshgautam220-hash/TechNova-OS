from typing import Annotated, Any, Dict, List, Optional
from pydantic import Field
from agent_framework import tool
from backend.foundry_client import get_foundry_client
from backend.tools.customer_tools import (
    get_customer, get_customer_orders, get_customer_status,
    find_inactive_customers, get_high_value_customers
)

client = get_foundry_client()

@tool(name="get_customer", description="Retrieves single customer profile by Customer ID.")
def tool_get_customer(customer_id: Annotated[str, Field(description="Customer ID")]) -> Optional[Dict[str, Any]]:
    return get_customer(customer_id)

@tool(name="get_customer_orders", description="Retrieves recent orders placed by a specific customer.")
def tool_get_customer_orders(customer_id: Annotated[str, Field(description="Customer ID")], limit: Annotated[int, Field(description="Max orders")] = 10) -> List[Dict[str, Any]]:
    return get_customer_orders(customer_id, limit)

@tool(name="get_customer_status", description="Evaluates customer tier, lifetime value, and inactivity risk status.")
def tool_get_customer_status(customer_id: Annotated[str, Field(description="Customer ID")]) -> Dict[str, Any]:
    return get_customer_status(customer_id)

@tool(name="find_inactive_customers", description="Finds customers with no recent orders and filters by minimum historical spend.")
def tool_find_inactive_customers(
    min_days_inactive: Annotated[int, Field(description="Minimum days inactive")] = 60,
    min_spent: Annotated[float, Field(description="Minimum total spent")] = 0.0
) -> Dict[str, Any]:
    return find_inactive_customers(min_days_inactive, min_spent)

@tool(name="get_high_value_customers", description="Retrieves VIP customers to target for retention.")
def tool_get_high_value_customers(min_spend: Annotated[float, Field(description="Minimum spend")] = 2500.0) -> Dict[str, Any]:
    return get_high_value_customers(min_spend)

CustomerAgent = client.as_agent(
    name="CustomerIntelligenceAgent",
    instructions=(
        "You are the Customer Intelligence Agent.\n"
        "You analyze synthetic TechNova customer data for internal business operations.\n"
        "Use your tools for factual customer information.\n"
        "Focus on tiers, lifetime spend, inactivity, order history and retention cohorts.\n"
        "Never invent customer records.\n"
        "Do not modify customer profiles or payment data.\n"
        "Return concise structured findings for the Manager Agent."
    ),
    tools=[
        tool_get_customer,
        tool_get_customer_orders,
        tool_get_customer_status,
        tool_find_inactive_customers,
        tool_get_high_value_customers
    ],
)

