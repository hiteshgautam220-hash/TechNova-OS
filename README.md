# AI Multi-Agent Business Operations Assistant
### AI-103 Course Completion Master Project | Project 29 (Chitkara University)
*Autonomous Multi-Agent Collaboration for Operational Diagnostics, Sales Intelligence & Strategic Decision-Making*

---

## 1. Executive Summary & Problem Context

In contemporary e-commerce and retail hardware enterprises (such as our fictional company **TechNova Electronics**), business managers face operational blind spots when sales drop, cancellation rates spike, or high-value customer cohorts disengage. Conventional dashboards display raw numbers but fail to provide root-cause analysis, cross-functional synthesis, or policy-audited recommendations.

**Project 29 Direction**: This solution is explicitly **NOT a customer-facing support chatbot**. Instead, it is an **Internal Business Operations Assistant for Managers and Operations Leads**. The user interacts with a unified executive interface while **four collaborative AI agents** orchestrate behind the scenes to analyze data, calculate deterministic metrics, audit governance policies, and formulate actionable management reports.

```
                         USER (Operations Lead / Business Manager)
                                            │
                                            ▼
                       ┌────────────────────────────────────────┐
                       │  STREAMLIT UI (Dark Blue & Mustard)    │
                       │   • Operations Chat & Live Trace       │
                       │   • Sales Analytics & Returns          │
                       │   • Customer Intelligence Explorer     │
                       │   • What-If Campaign Sandbox           │
                       │   • Responsible AI & Governance Center │
                       └────────────────────┬───────────────────┘
                                            │ HTTP / REST
                                            ▼
                       ┌────────────────────────────────────────┐
                       │        FASTAPI BACKEND SERVICE         │
                       │   • Request Validation & Routing       │
                       │   • Session & Trace Management         │
                       └────────────────────┬───────────────────┘
                                            │
                                            ▼
                       ┌────────────────────────────────────────┐
                       │      MANAGER AGENT (ORCHESTRATOR)      │
                       │  Decomposes Tasks & Reconciles Facts   │
                       └───────┬────────────┬───────────┬───────┘
                               │            │           │
            ┌──────────────────┘            │           └──────────────────┐
            ▼                               ▼                              ▼
┌───────────────────────┐       ┌───────────────────────┐      ┌───────────────────────┐
│  CUSTOMER INTELLIGENCE│       │     SALES & ORDER     │      │   BUSINESS ANALYSIS   │
│         AGENT         │       │         AGENT         │      │         AGENT         │
│ • Inactive cohorts    │       │ • Revenue calculations│      │ • Policy compliance   │
│ • VIP classification  │       │ • Period comparisons  │      │ • What-If modeling    │
│ • LTV & Churn Risk    │       │ • Return diagnostics  │      │ • Action plans        │
└───────────┬───────────┘       └───────────┬───────────┘      └───────────┬───────────┘
            │                               │                              │
            └───────────────────────┬───────┴──────────────────────────────┘
                                    │ Tool Invocations
                                    ▼
                       ┌────────────────────────────────────────┐
                       │       DETERMINISTIC TOOLS LAYER        │
                       │   • customer_tools.py (5 functions)    │
                       │   • order_tools.py (7 functions)       │
                       │   • business_tools.py (4 functions)    │
                       └────────────────────┬───────────────────┘
                                            │ SQL (Read-Only)
                                            ▼
                       ┌────────────────────────────────────────┐
                       │      TECHNOVA SQLITE OPERATIONAL DB    │
                       │   • customers (160 synthetic profiles) │
                       │   • products (25 tech hardware SKUs)   │
                       │   • orders (1,400+ transactions)       │
                       │   • returns (150+ defect records)      │
                       │   • policies (POL-001 to POL-007)      │
                       └────────────────────────────────────────┘
```

---

## 2. The 4-Agent Cognitive Architecture

| Agent | Core Responsibility | Permitted Capabilities | Strict Boundaries (Prohibited) |
| :--- | :--- | :--- | :--- |
| **1. Manager Agent** *(Orchestrator)* | Understand requests, decompose subtasks, sequence specialist delegation, synthesize final executive report | Task decomposition, cross-agent coordination, fact reconciliation, final report formatting | Direct DB writes, inventing financial facts, executing automated payments |
| **2. Customer Intelligence Agent** | Customer behavior, inactivity detection, churn risk, and retention segmentation | Retrieve customer history, calculate LTV, identify inactive VIP accounts, draft outreach cohorts | Mutating customer profiles, altering payment info, financial decisions |
| **3. Sales & Order Agent** | Quantitative revenue analysis, return rate diagnostics, and period-over-period comparisons | Deterministic revenue calculation, period variance comparison, cancellation rate calculation | Issuing refunds, deleting/modifying orders, writing to financial ledgers |
| **4. Business Analysis Agent** | Synthesize insights, audit corporate policies (POL-001 to POL-007), model what-if scenarios | Policy evaluation, what-if margin modeling, action plan formulation | Inventing corporate policies, executing actions >$500 without human review |

---

## 3. Technology Stack & Azure Foundry Integration

- **AI Model & Cloud**: Microsoft Foundry / Azure OpenAI (`gpt-4o-mini-business`) via `azure-ai-projects` and `azure-identity`.
- **Dual-Engine Execution**: Built-in high-fidelity local deterministic engine ensures instant, reliable offline demonstration and testing with **zero cloud spend**.
- **Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn.
- **Frontend**: Streamlit styled with a custom **Dark Blue** (`#0B192C` / `#1E293B`) and **Mustard Orange** (`#FFB200` / `#D97706`) executive palette, interactive Plotly charts, and live agent trace logs.
- **Data Layer**: SQLite with deterministic seed generator for TechNova Electronics.

### Azure $100 Student Credit Protection Strategy
1. **Single Model Deployment**: Only one general-purpose `gpt-4o-mini` deployment is provisioned in Azure Foundry to serve all 4 agents.
2. **Local Data & Compute**: SQLite database runs locally—no expensive Cosmos DB or Azure AI Search instances required.
3. **Local Dev Envelope**: Students use local execution mode for testing, reserving the Azure subscription strictly for final validation and recording.

---

## 4. The 5 Core Demo Scenarios

The system natively supports the 5 core assignment evaluation questions:

1. **"Why did sales fall this week?"**
   - *Flow*: User $\rightarrow$ Manager $\rightarrow$ Sales Agent (compares 7-day periods) $\rightarrow$ Customer Agent (checks VIP activity) $\rightarrow$ Business Agent (checks policies & stock issues) $\rightarrow$ Manager (Executive Report).
   - *Findings*: Demonstrates a 45.1% revenue decline driven by the expiration of a prior-week promotional blitz, stock shortage in flagship `NovaBook Pro 16`, and an elevated return rate in `NovaSound ANC 700`.

2. **"Find valuable inactive customers and prepare a recovery campaign."**
   - *Findings*: Discovers 40 accounts inactive for 60+ days ($79,600+ past lifetime spend), highlights 12 Gold/Platinum VIP accounts, and structures a tiered re-engagement campaign.

3. **"Which products have the highest return rate?"**
   - *Findings*: Diagnoses `NovaSound ANC 700` as an acute outlier with a 14.8% return rate (violating policy POL-007's 8.0% threshold), citing Bluetooth/audio hardware defects.

4. **"What could happen if we give inactive customers a 10% discount?"**
   - *Findings*: Runs a deterministic what-if financial model projecting 7 conversions out of 40 accounts, generating $4,725.00 net revenue and $1,575.00 gross margin (33.3% margin). Verifies compliance under policy POL-003.

5. **"Prepare a management report for this week."**
   - *Findings*: Synthesizes multi-agent findings across revenue, customer tiers, return rates, root causes, and provides an actionable 4-step management roadmap.

---

## 5. Responsible AI & Governance Safeguards (15% Weight)

To satisfy the **15% Responsible AI evaluation rubric**, the architecture embeds four strict guardrails:
1. **Synthetic Data Policy**: 100% synthetic dataset (`TechNova`). Zero real-customer personally identifiable information (PII) is stored or processed.
2. **Bounded Read-Only SQL**: The database driver explicitly intercepts and rejects any `INSERT`, `UPDATE`, `DELETE`, or `DROP` statements from AI agents.
3. **Human-in-the-Loop Safeguards**:
   - **POL-002**: Any refund or financial disbursement over **$500.00 USD** is blocked from automated execution and flagged for manual Finance Manager approval.
   - **POL-003**: Customer recovery promotional discounts are strictly capped at **15.0%**. Any discount exceeding 15% requires VP of Sales sign-off.
4. **Full Traceability & Auditability**: Every reasoning step, delegation event, tool parameter, and SQL execution is logged in real-time in the interactive trace viewer.

---

## 6. Project Structure

```
ai-business-assistant/
├── .env.example                # Environment configuration template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── run_all.bat                 # One-click launch for backend & frontend
├── run_backend.bat             # Starts FastAPI on :8000
├── run_frontend.bat            # Starts Streamlit on :8501
├── README.md                   # Complete documentation
│
├── backend/
│   ├── config.py               # Settings & environment variables
│   ├── database.py             # Thread-safe SQLite manager & read-only guardrails
│   ├── main.py                 # FastAPI endpoints & CORS
│   ├── agents/
│   │   ├── base_agent.py       # Agent contract & trace logging
│   │   ├── manager_agent.py    # Central Orchestrator & report builder
│   │   ├── customer_agent.py   # Customer intelligence specialist
│   │   ├── sales_agent.py      # Sales & order analytics specialist
│   │   └── business_agent.py   # Business analysis & policy specialist
│   ├── tools/
│   │   ├── customer_tools.py   # Customer filtering & LTV calculations
│   │   ├── order_tools.py      # Revenue, period comparisons, return rates
│   │   └── business_tools.py   # Policies, impact checks, what-if simulations
│   └── data/
│       ├── seed_data.py        # TechNova dataset generator
│       ├── policies.json       # Corporate rules (POL-001 to POL-007)
│       ├── customers.csv       # 160 customer records
│       ├── products.csv        # 25 tech hardware products
│       ├── orders.csv          # 1,400+ transactions
│       └── returns.csv         # 150+ return defect records
│
├── frontend/
│   ├── app.py                  # Streamlit application entry point
│   ├── styles.py               # Custom Dark Blue & Mustard Orange CSS
│   └── components/
│       ├── chat_view.py        # Operations chat & live trace viewer
│       ├── analytics_view.py   # Sales trends & return diagnostics charts
│       ├── customer_view.py    # Customer cohort explorer & search
│       ├── simulator_view.py   # What-If promotional campaign sandbox
│       └── governance_view.py  # Responsible AI & safety audit center
│
└── tests/
    ├── test_tools.py           # Unit tests for deterministic tools
    ├── test_agents.py          # Integration tests for all 5 demo scenarios
    └── test_responsible_ai.py  # Safety guardrails & read-only checks
```

---

## 7. Quickstart Guide

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Windows PowerShell or Command Prompt

### Step 1: Clone & Setup Environment
```bash
# Navigate to project folder
cd ai-business-assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*(By default, `EXECUTION_MODE=local` is enabled for instant, zero-cost offline demonstration. To connect to Azure Foundry, add your `PROJECT_ENDPOINT` or `AZURE_OPENAI_API_KEY` and set `EXECUTION_MODE=azure`.)*

### Step 3: Run Application
You can run both services with a single double-click on `run_all.bat`, or in two separate terminals:

**Terminal 1 (Backend API):**
```bash
run_backend.bat
# API will start at http://127.0.0.1:8000
# OpenAPI Docs: http://127.0.0.1:8000/docs
```

**Terminal 2 (Streamlit UI):**
```bash
run_frontend.bat
# UI will open at http://127.0.0.1:8501
```

---

## 8. Automated Testing Suite

Run the full pytest suite:
```bash
.venv\Scripts\activate
pytest -v
```

The test suite validates:
- `tests/test_tools.py`: Deterministic metrics, sales comparisons, return rates, and what-if calculations.
- `tests/test_agents.py`: End-to-end multi-agent orchestration for all 5 core evaluation scenarios.
- `tests/test_responsible_ai.py`: Enforces read-only DB write interception, POL-002 human approval flags, and policy validation.

---

## 9. Five-Minute Presentation & Video Script

| Time | Slide / Screen | Script & Narration Outline |
| :--- | :--- | :--- |
| **0:00 - 0:30** | Title Slide | *"Welcome. We are Team 29 presenting our AI-103 Course Completion project: The AI Multi-Agent Business Operations Assistant. Our project addresses the challenge of operational diagnostics in modern enterprise commerce."* |
| **0:30 - 1:00** | Problem Statement | *"Conventional chatbots are customer-facing FAQ bots. Business operations leaders, however, need deep internal diagnostics when revenue contracts or customer churn accelerates. Our system creates an internal operations team of four specialized agents."* |
| **1:00 - 2:00** | Architecture & AI-103 Concepts | *"The system architecture uses Microsoft Foundry with a single GPT-4o-mini deployment. The Manager Agent acts as Orchestrator, dispatching tasks to Customer Intelligence, Sales & Order Analytics, and Business Analysis agents. Crucially, factual numbers are calculated deterministically via Python tools, eliminating LLM hallucinations."* |
| **2:00 - 4:00** | Live Technical Demo | *1. Click 'Why did sales fall this week?' $\rightarrow$ Show the live multi-agent trace delegating to Sales and Customer agents $\rightarrow$ Review generated Executive Report with KPIs and Action Plan.<br>2. Switch to 'What-If Simulator' $\rightarrow$ Adjust discount slider $\rightarrow$ Show how exceeding 15% immediately triggers policy POL-003 VP sign-off.<br>3. Inspect 'Governance Center' $\rightarrow$ Test safety check to prove autonomous financial writes are blocked.* |
| **4:00 - 5:00** | Responsible AI & Future Scope | *"Our system demonstrates responsible AI by design: 100% synthetic data, strict read-only database boundaries, and mandatory human-in-the-loop checkpoints for actions over $500. Future enhancements include live ERP integrations and automated supply replenishment triggers. Thank you!"* |

---

## 10. Team Roles & Contributions

- **Team Lead (Architecture & Orchestration)**: Multi-agent cognitive architecture, Manager Agent orchestration, FastAPI backend routing, Azure Foundry integration.
- **Specialist 2 (Customer Intelligence)**: Customer data tools, inactivity segmentation, LTV metrics, and churn risk detection.
- **Specialist 3 (Sales & Order Analytics)**: Sales calculations, return rate diagnostics, period-over-period variance tools, TechNova data seed generator.
- **Specialist 4 (Business Analysis & Quality)**: Corporate policy engine (`policies.json`), what-if campaign simulation logic, automated test suite, and Responsible AI guardrails.
- **Specialist 5 (Frontend UI & Presentation)**: Streamlit executive interface, Dark Blue & Mustard Orange design system, interactive Plotly visualizations, documentation, and video production.
