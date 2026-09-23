"""Integration tests for multi-agent cognitive orchestration."""

import pytest
from backend.database import ensure_db_ready
from backend.agents.manager_agent import ManagerAgent

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    ensure_db_ready()

@pytest.fixture
def manager():
    return ManagerAgent()

def test_scenario_1_sales_slump(manager):
    report = manager.orchestrate("Why did sales fall this week?")
    assert "Executive Root-Cause Investigation" in report.title
    assert len(report.kpis) > 0
    assert len(report.observed_changes) > 0
    assert len(report.contributing_factors) > 0
    assert len(report.proposed_action_plan) > 0
    assert len(report.trace_steps) > 0
    assert "Sales & Order Agent" in report.participating_agents

def test_scenario_2_inactive_customers(manager):
    report = manager.orchestrate("Find valuable inactive customers and prepare a recovery campaign.")
    assert "Customer Intelligence & Retention" in report.title
    assert len(report.target_customer_segments) > 0
    assert "Customer Intelligence Agent" in report.participating_agents

def test_scenario_3_return_rates(manager):
    report = manager.orchestrate("Which products have the highest return rate?")
    assert "Quality Engineering" in report.title
    assert "NovaSound ANC 700" in report.executive_summary or "NovaSound ANC 700" in str(report.kpis)
    assert "Sales & Order Agent" in report.participating_agents

def test_scenario_4_what_if_discount(manager):
    report = manager.orchestrate("What could happen if we give inactive customers a 10% discount?")
    assert "What-If Scenario Modeling" in report.title
    assert "10.0%" in report.kpis["Modeled Discount Rate"]
    assert "Business Analysis Agent" in report.participating_agents

def test_scenario_5_management_report(manager):
    report = manager.orchestrate("Prepare a management report for this week.")
    assert "Management Operations Report" in report.title
    assert len(report.participating_agents) >= 3
    assert len(report.trace_steps) >= 5
