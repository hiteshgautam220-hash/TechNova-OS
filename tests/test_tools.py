"""Unit tests for deterministic tool functions."""

import pytest
from backend.database import ensure_db_ready
from backend.tools import customer_tools, order_tools, business_tools

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    ensure_db_ready()

def test_get_customer_valid():
    cust = customer_tools.get_customer("CUST-1001")
    assert cust is not None
    assert cust["customer_id"] == "CUST-1001"
    assert "name" in cust
    assert "customer_type" in cust

def test_get_customer_invalid():
    cust = customer_tools.get_customer("CUST-99999")
    assert cust is None

def test_find_inactive_customers():
    res = customer_tools.find_inactive_customers(min_days_inactive=60, min_spent=0.0)
    assert "total_inactive_count" in res
    assert res["total_inactive_count"] > 0
    assert "tier_distribution" in res
    assert res["total_addressable_historical_spend"] > 0

def test_calculate_sales_period():
    sales = order_tools.calculate_sales("2026-09-14", "2026-09-20")
    assert sales["total_orders"] > 0
    assert sales["completed_revenue"] >= 0.0
    assert sales["average_order_value"] >= 0.0

def test_calculate_return_rate():
    ret = order_tools.calculate_return_rate()
    assert ret["overall_return_rate_pct"] >= 0.0
    assert len(ret["highest_return_products"]) > 0
    # NovaSound ANC 700 should be the highest return product
    highest = ret["highest_return_products"][0]
    assert highest["product_id"] == "PRD-301" or highest["return_rate_pct"] > 5.0

def test_compare_sales_periods():
    comp = order_tools.compare_sales_periods(
        current_start="2026-09-14",
        current_end="2026-09-20",
        prior_start="2026-09-07",
        prior_end="2026-09-13"
    )
    assert "variance" in comp
    assert "revenue_difference" in comp["variance"]
    assert "percentage_change" in comp["variance"]

def test_simulate_discount_campaign_compliant():
    # 10% discount is compliant (<=15%)
    sim = business_tools.simulate_discount_campaign(
        target_customer_count=40,
        average_order_value=750.0,
        discount_pct=10.0,
        expected_conversion_pct=18.0
    )
    assert sim["governance_assessment"]["is_policy_compliant"] is True
    assert sim["financial_projections"]["projected_net_revenue"] > 0
    assert sim["financial_projections"]["promotional_discount_cost"] > 0

def test_simulate_discount_campaign_ceiling_exceeded():
    # 20% discount exceeds ceiling
    sim = business_tools.simulate_discount_campaign(
        target_customer_count=40,
        average_order_value=750.0,
        discount_pct=20.0,
        expected_conversion_pct=18.0
    )
    assert sim["governance_assessment"]["is_policy_compliant"] is False
    assert sim["governance_assessment"]["requires_vp_signoff"] is True
