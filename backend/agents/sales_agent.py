from typing import Annotated, Any, Dict, List, Optional
from pydantic import Field
from agent_framework import tool
from backend.foundry_client import get_foundry_client
from backend.tools.order_tools import get_order, get_orders, calculate_sales, calculate_return_rate, calculate_cancellation_rate, get_top_products, compare_sales_periods
import datetime

client = get_foundry_client()
today = datetime.date.today().strftime("%Y-%m-%d")

@tool(name="get_order", description="Retrieves an order's detail by Order ID.")
def tool_get_order(order_id: Annotated[str, Field(description="Order ID")]) -> Optional[Dict[str, Any]]: return get_order(order_id)
@tool(name="get_orders", description="Retrieves list of orders within an optional date range.")
def tool_get_orders(start_date: Annotated[Optional[str], Field(description="Start date YYYY-MM-DD")] = None, end_date: Annotated[Optional[str], Field(description="End date YYYY-MM-DD")] = None, limit: Annotated[int, Field(description="Max orders")] = 50) -> List[Dict[str, Any]]: return get_orders(start_date, end_date, limit)
@tool(name="calculate_sales", description="Calculates total gross revenue, net completed revenue, and order volume.")
def tool_calculate_sales(start_date: Annotated[Optional[str], Field(description="Start date YYYY-MM-DD")] = None, end_date: Annotated[Optional[str], Field(description="End date YYYY-MM-DD")] = None) -> Dict[str, Any]: return calculate_sales(start_date, end_date)
@tool(name="calculate_return_rate", description="Calculates overall return rate and identifies product-level return anomalies.")
def tool_calculate_return_rate(start_date: Annotated[Optional[str], Field(description="Start date YYYY-MM-DD")] = None, end_date: Annotated[Optional[str], Field(description="End date YYYY-MM-DD")] = None) -> Dict[str, Any]: return calculate_return_rate(start_date, end_date)
@tool(name="calculate_cancellation_rate", description="Calculates order cancellation rates across products and categories.")
def tool_calculate_cancellation_rate(start_date: Annotated[Optional[str], Field(description="Start date YYYY-MM-DD")] = None, end_date: Annotated[Optional[str], Field(description="End date YYYY-MM-DD")] = None) -> Dict[str, Any]: return calculate_cancellation_rate(start_date, end_date)
@tool(name="get_top_products", description="Retrieves top performing products ranked by completed revenue or sales volume.")
def tool_get_top_products(by: Annotated[str, Field(description="Rank by 'revenue' or 'units_sold'")] = "revenue", limit: Annotated[int, Field(description="Max products")] = 5) -> List[Dict[str, Any]]: return get_top_products(by, limit)
@tool(name="compare_sales_periods", description="Directly compares current period vs prior period.")
def tool_compare_sales_periods(current_start: Annotated[str, Field(description="Current start date YYYY-MM-DD")], current_end: Annotated[str, Field(description="Current end date YYYY-MM-DD")], prior_start: Annotated[str, Field(description="Prior start date YYYY-MM-DD")], prior_end: Annotated[str, Field(description="Prior end date YYYY-MM-DD")]) -> Dict[str, Any]: return compare_sales_periods(current_start, current_end, prior_start, prior_end)

SalesAgent = client.as_agent(
    name="SalesOrderAgent",
    instructions=(
        "You are the Chief Financial Analyst at TechNova.\n"
        "Your job is to execute highly accurate queries on the order database.\n"
        "\n"
        "### BEHAVIOR RULES:\n"
        "1. Always format monetary values in USD.\n"
        "2. If you notice a high return rate or a massive drop in sales, highlight it as an '⚠️ Anomaly' in your response.\n"
        "3. Never guess numbers. Only report the exact mathematical outputs from your tools.\n"
        "4. IDENTITY GUARDRAIL: Only calculate and report database metrics for TechNova. If comparing against external competitor data provided by the user, clearly distinguish between TechNova's internal database metrics and the external competitor data.\n"
        "\n"
        f"CRITICAL: The current date is {today}. The database contains data through mid-September 2026. Use September 2026 for relative date math."
    ),
    tools=[tool_get_order, tool_get_orders, tool_calculate_sales, tool_calculate_return_rate, tool_calculate_cancellation_rate, tool_get_top_products, tool_compare_sales_periods],
)
