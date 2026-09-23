"""Responsible AI, Safety, and Security Guardrail Tests."""

import pytest
from backend.database import execute_query, ensure_db_ready
from backend.tools.business_tools import calculate_business_impact, get_business_policy

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    ensure_db_ready()

def test_database_write_prevention():
    """Security Guardrail: Enforces read-only database operations to prevent unauthorized table mutation."""
    with pytest.raises(PermissionError) as exc_info:
        execute_query("UPDATE customers SET total_spent = 999999 WHERE customer_id = 'CUST-1001'")
    assert "Security Alert: Agent attempted forbidden SQL write operation" in str(exc_info.value)

def test_database_delete_prevention():
    """Security Guardrail: Forbids DROP/DELETE statements."""
    with pytest.raises(PermissionError) as exc_info:
        execute_query("DROP TABLE orders")
    assert "Security Alert" in str(exc_info.value)

def test_high_value_refund_human_approval():
    """Governance Guardrail: Mandates human approval for refund requests exceeding $500 (POL-002)."""
    res = calculate_business_impact(action="refund", amount=750.0)
    assert res["requires_human_approval"] is True
    assert res["compliance_status"] == "PENDING_HUMAN_SIGN_OFF"
    assert res["recommended_approver"] == "Finance Operations Manager"

def test_low_value_action_pre_approval():
    """Governance Guardrail: Low-risk routine operations do not require executive intervention."""
    res = calculate_business_impact(action="routine_inquiry", amount=50.0)
    assert res["requires_human_approval"] is False
    assert res["compliance_status"] == "PRE_APPROVED"

def test_policy_pol_006_read_only_rule_active():
    """Verifies that POL-006 Autonomous Database Mutability Safeguard is registered in policy engine."""
    pol = get_business_policy("POL-006")
    assert pol is not None
    assert "strictly granted read-only analytical access" in pol["rule"]
