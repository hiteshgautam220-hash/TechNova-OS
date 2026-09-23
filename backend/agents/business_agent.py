from typing import Annotated, Any, Dict, List, Optional
from pydantic import Field
from agent_framework import tool
from backend.foundry_client import get_foundry_client
from backend.tools.business_tools import (
    get_business_policy, get_business_rules, calculate_business_impact,
    simulate_discount_campaign
)

client = get_foundry_client()

@tool(name="get_business_policy", description="Retrieves specific corporate governance policy by ID.")
def tool_get_business_policy(policy_id: Annotated[str, Field(description="Policy ID")]) -> Optional[Dict[str, Any]]:
    return get_business_policy(policy_id)

@tool(name="get_business_rules", description="Retrieves all active TechNova corporate policies and guardrails.")
def tool_get_business_rules() -> List[Dict[str, Any]]:
    return get_business_rules()

@tool(name="calculate_business_impact", description="Evaluates proposed operational action against safety thresholds and approval requirements.")
def tool_calculate_business_impact(
    action: Annotated[str, Field(description="Action name")],
    amount: Annotated[float, Field(description="Amount in USD")]
) -> Dict[str, Any]:
    return calculate_business_impact(action, amount)

@tool(name="simulate_discount_campaign", description="Runs a deterministic what-if financial simulation for customer win-back discount campaigns.")
def tool_simulate_discount_campaign(
    target_customer_count: Annotated[int, Field(description="Target customer count")],
    average_order_value: Annotated[float, Field(description="Average order value")],
    discount_pct: Annotated[float, Field(description="Discount percentage")],
    expected_conversion_pct: Annotated[float, Field(description="Expected conversion rate")] = 18.0
) -> Dict[str, Any]:
    return simulate_discount_campaign(target_customer_count, average_order_value, discount_pct, expected_conversion_pct)

BusinessAgent = client.as_agent(
    name="BusinessAnalysisAgent",
    instructions=(
        "You are the Business Analysis Agent.\n"
        "You combine factual findings from specialist agents and apply the configured TechNova policies. "
        "Use policy and simulation tools where needed.\n"
        "Separate observed facts from possible contributing factors.\n"
        "Never invent policies.\n"
        "Do not execute actions above the configured approval thresholds.\n"
        "Return findings, risks, assumptions and proposed management actions."
    ),
    tools=[
        tool_get_business_policy, tool_get_business_rules,
        tool_calculate_business_impact, tool_simulate_discount_campaign
    ],
)

