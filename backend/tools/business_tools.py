"""Business Analysis Tools: Policy compliance, what-if simulations, and impact calculations."""

import json
from typing import Any, Dict, List, Optional
from backend.database import execute_query
from backend.config import settings

def get_business_policy(policy_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves specific corporate governance policy by ID (e.g. POL-001 to POL-007)."""
    rows = execute_query(
        "SELECT policy_id, name, category, rule, approval_required, conditions_json FROM policies WHERE policy_id = ?",
        (policy_id.strip().upper(),)
    )
    if rows:
        row = dict(rows[0])
        row["approval_required"] = bool(row["approval_required"])
        row["conditions"] = json.loads(row["conditions_json"]) if row["conditions_json"] else {}
        return row
    return None

def get_business_rules() -> List[Dict[str, Any]]:
    """Retrieves all active TechNova corporate policies and guardrails."""
    rows = execute_query("SELECT policy_id, name, category, rule, approval_required, conditions_json FROM policies")
    policies = []
    for r in rows:
        d = dict(r)
        d["approval_required"] = bool(d["approval_required"])
        d["conditions"] = json.loads(d["conditions_json"]) if d["conditions_json"] else {}
        policies.append(d)
    return policies

def calculate_business_impact(action: str, amount: float) -> Dict[str, Any]:
    """Evaluates proposed operational action against safety thresholds and approval requirements."""
    threshold = settings.HUMAN_APPROVAL_THRESHOLD_USD
    requires_approval = (amount > threshold) or (action.lower() in ["refund", "write_off", "bulk_discount", "credit_disbursement"])
    
    return {
        "action": action,
        "amount_usd": amount,
        "policy_governance_rule": "POL-002: High-Value Financial Controls",
        "threshold_usd": threshold,
        "requires_human_approval": requires_approval,
        "recommended_approver": "Finance Operations Manager" if requires_approval else "Automated / Operations Lead",
        "risk_level": "High" if amount > 1000 else ("Medium" if requires_approval else "Low"),
        "compliance_status": "PENDING_HUMAN_SIGN_OFF" if requires_approval else "PRE_APPROVED"
    }

def simulate_discount_campaign(
    target_customer_count: int,
    average_order_value: float,
    discount_pct: float,
    expected_conversion_pct: float = 18.0
) -> Dict[str, Any]:
    """Runs a deterministic what-if financial simulation for customer win-back discount campaigns.
    
    Calculates estimated gross revenue, discount promotional cost, net revenue,
    estimated product cost (COGS @ 60%), net gross profit, and checks policy thresholds.
    """
    # Policy check: Maximum discount is 15.0% without executive sign-off
    max_discount = settings.MAX_DISCOUNT_PERCENT
    policy_compliant = discount_pct <= max_discount
    
    # Financial projections
    estimated_converting_customers = int(round(target_customer_count * (expected_conversion_pct / 100.0)))
    estimated_converting_customers = max(1, estimated_converting_customers) if target_customer_count > 0 else 0
    
    projected_gross_gmv = round(estimated_converting_customers * average_order_value, 2)
    discount_cost = round(projected_gross_gmv * (discount_pct / 100.0), 2)
    projected_net_revenue = round(projected_gross_gmv - discount_cost, 2)
    
    # Standard hardware COGS baseline: ~60% of baseline GMV
    estimated_cogs = round(projected_gross_gmv * 0.60, 2)
    estimated_gross_profit = round(projected_net_revenue - estimated_cogs, 2)
    gross_margin_pct = round((estimated_gross_profit / projected_net_revenue) * 100, 2) if projected_net_revenue > 0 else 0.0

    return {
        "scenario_type": "Win-Back Promotional Simulation",
        "inputs": {
            "target_customer_count": target_customer_count,
            "average_order_value": average_order_value,
            "discount_percentage": discount_pct,
            "expected_conversion_rate_pct": expected_conversion_pct
        },
        "financial_projections": {
            "estimated_converted_customers": estimated_converting_customers,
            "projected_gross_gmv": projected_gross_gmv,
            "promotional_discount_cost": discount_cost,
            "projected_net_revenue": projected_net_revenue,
            "estimated_cogs": estimated_cogs,
            "projected_gross_profit": estimated_gross_profit,
            "projected_profit_margin_pct": gross_margin_pct
        },
        "governance_assessment": {
            "policy_id": "POL-003: Promotional Discount Ceiling",
            "max_allowed_automated_discount": f"{max_discount}%",
            "is_policy_compliant": policy_compliant,
            "requires_vp_signoff": not policy_compliant,
            "status": "APPROVED_FOR_LAUNCH" if policy_compliant else "REQUIRES_VP_APPROVAL"
        },
        "assumptions_and_risks": [
            f"Assumes an industry-standard win-back conversion rate of {expected_conversion_pct}%.",
            f"Estimated hardware product Cost of Goods Sold (COGS) modeled at 60% of GMV.",
            "Risk: Potential margin erosion if repeat purchase velocity does not materialize post-discount.",
            "Risk: Customer discount fatigue if promotions are repeated too frequently."
        ]
    }
