from typing import Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from backend.tools.document_tools import extract_text_from_document
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.config import settings
from backend.database import ensure_db_ready, execute_query, execute_scalar
from backend.agents.manager_agent import manager_agent
from backend.tools.business_tools import simulate_discount_campaign, get_business_rules
from backend.tools.order_tools import calculate_sales, calculate_return_rate, calculate_cancellation_rate, get_top_products

app = FastAPI(
    title="TechNova AI Multi-Agent Business Operations Assistant API",
    description="Backend orchestration service for AI-103 Project 29 (Course Completion Project)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    ensure_db_ready()

# ChatRequest removed, using Form data

class SimulationRequest(BaseModel):
    target_customer_count: int = Field(default=40, ge=1)
    average_order_value: float = Field(default=750.0, ge=1.0)
    discount_pct: float = Field(default=10.0, ge=0.0, le=50.0)
    expected_conversion_pct: float = Field(default=18.0, ge=0.0, le=100.0)

@app.get("/api/health")
def health_check():
    return {
        "status": "success",
        "database": "connected",
        "configuration": {
            "execution_mode": settings.EXECUTION_MODE,
            "human_approval_threshold_usd": settings.HUMAN_APPROVAL_THRESHOLD_USD,
            "max_discount_allowed_pct": settings.MAX_DISCOUNT_PERCENT
        }
    }

@app.post("/api/chat")
async def chat(query: str = Form(...), chat_history: str = Form("[]"), file: Optional[UploadFile] = File(None)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    from backend.tools.storage_tools import search_chroma
    chroma_memory = search_chroma(query)
    
    import json
    history = json.loads(chat_history)
    context_string = ""
    if chroma_memory:
        context_string += f"\n\n[RELEVANT PAST MEMORY FOUND]:\n{chroma_memory}\n"
        
    if history:
        context_string += "\n\n[IMMEDIATE PREVIOUS CONTEXT]:\n"
        for msg in history[-4:]:
            context_string += f"{msg['role'].upper()}: {msg['content']}\n"
            if "document_context" in msg and msg["document_context"]:
                context_string += f"[ATTACHED DOCUMENT IN THIS TURN]:\n{msg['document_context']}\n"
        context_string += "[END PREVIOUS CONTEXT]\n\n"
    
    final_query = context_string + query


    doc_text_out = None
    if file:
        contents = await file.read()
        doc_text = extract_text_from_document(contents)
        doc_text_out = doc_text
        final_query += f"\n\n[USER ATTACHED A DOCUMENT]:\n{doc_text}\n[END OF DOCUMENT]"
    
    result = await manager_agent.run(final_query)
    
    return {
        "status": "success",
        "answer": result.text,
        "agents_used": ["Manager Agent (Orchestrator)"],
        "extracted_doc": doc_text_out,
    }

@app.post("/api/simulate")
def run_simulation(req: SimulationRequest):
    return simulate_discount_campaign(
        target_customer_count=req.target_customer_count,
        average_order_value=req.average_order_value,
        discount_pct=req.discount_pct,
        expected_conversion_pct=req.expected_conversion_pct
    )

@app.get("/api/dashboard")
def get_dashboard_kpis():
    total_customers = execute_scalar("SELECT COUNT(*) FROM customers")
    inactive_customers = execute_scalar("SELECT COUNT(*) FROM customers WHERE is_inactive = 1")
    curr_sales = calculate_sales("2026-09-14", "2026-09-20")
    prior_sales = calculate_sales("2026-09-07", "2026-09-13")
    returns = calculate_return_rate("2026-09-14", "2026-09-20")
    cancellations = calculate_cancellation_rate("2026-09-14", "2026-09-20")
    top_prods = get_top_products(by="revenue", limit=5)
    
    return {
        "overview": {
            "total_customers": total_customers,
            "inactive_customers": inactive_customers,
            "current_week_revenue": curr_sales["completed_revenue"],
            "prior_week_revenue": prior_sales["completed_revenue"],
            "revenue_change_pct": round(((curr_sales["completed_revenue"] - prior_sales["completed_revenue"]) / (prior_sales["completed_revenue"] or 1)) * 100, 1),
            "weekly_orders": curr_sales["completed_orders"],
            "weekly_return_rate_pct": returns["overall_return_rate_pct"],
            "weekly_cancellation_rate_pct": cancellations["cancellation_rate_pct"]
        },
        "top_products": top_prods,
        "highest_return_products": returns["highest_return_products"]
    }

@app.get("/api/customers")
def list_customers(is_inactive: Optional[int] = Query(None), tier: Optional[str] = Query(None), limit: int = Query(50, le=200)):
    where_clauses = []
    params = []
    if is_inactive is not None:
        where_clauses.append("is_inactive = ?")
        params.append(is_inactive)
    if tier:
        where_clauses.append("customer_type = ?")
        params.append(tier)
    where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT * FROM customers {where_str} ORDER BY total_spent DESC LIMIT ?"
    params.append(limit)
    return execute_query(query, tuple(params))

@app.get("/api/orders")
def list_orders(limit: int = Query(50, le=200)):
    return execute_query("SELECT * FROM orders ORDER BY order_date DESC LIMIT ?", (limit,))

@app.get("/api/returns")
def list_returns():
    return execute_query("SELECT * FROM returns ORDER BY return_date DESC LIMIT 50")

@app.get("/api/policies")
def list_policies():
    return get_business_rules()


from pydantic import BaseModel
from typing import List
import json
from backend.tools.storage_tools import upload_chat_to_blob, download_chat_from_blob

class SaveMemoryRequest(BaseModel):
    session_id: str
    tag: str = "General"
    messages: List[dict]


@app.post("/api/memory/generate_title")
async def generate_title(req: dict):
    query = req.get("query", "")
    if not query.strip() or query == "Document uploaded":
        return {"title": "Document_Analysis"}
    try:
        from backend.foundry_client import get_foundry_client
        client = get_foundry_client()
        namer_agent = client.as_agent(
            name="NamerAgent",
            instructions="You generate short, concise, maximum 3-word file names based on user prompts. Output ONLY the title string, nothing else. No quotes, no spaces (use underscores).",
            tools=[]
        )
        result = await namer_agent.run(f"Generate a file name for this prompt: {query}")
        title = result.text.strip().replace(" ", "_").replace('"', '').replace("'", "").replace(".", "")
        if not title:
            return {"title": "Saved_Session"}
        return {"title": title}
    except Exception as e:
        return {"title": "Saved_Session"}

@app.post("/api/memory/save")
def save_memory(req: SaveMemoryRequest):
    chat_str = json.dumps(req.messages)
    # 1. UI Memory (Blob)
    upload_chat_to_blob(req.session_id, chat_str, req.tag)
    # 2. AI Brain (Chroma)
    from backend.tools.storage_tools import save_to_chroma
    save_to_chroma(req.session_id, chat_str, req.tag)
    return {"status": "saved"}

@app.get("/api/memory/load")
def load_memory(session_id: str, tag: str = "General"):
    data = download_chat_from_blob(session_id, tag)
    return {"messages": json.loads(data)}


@app.delete("/api/memory/delete")
def delete_memory(session_id: str, tag: str = "General"):
    from backend.tools.storage_tools import delete_chat_from_blob
    delete_chat_from_blob(session_id, tag)
    return {"status": "deleted"}

@app.get("/api/memory/list")
def list_memory():
    from backend.tools.storage_tools import list_chats_from_blob
    chats = list_chats_from_blob()
    return {"chats": chats}


@app.post("/api/dashboard/parse_internal_pdf")
async def parse_internal_pdf(file: UploadFile = File(...), instructions: Optional[str] = Form("")):
    try:
        file_bytes = await file.read()
        doc_text = extract_text_from_document(file_bytes)
        
        from backend.foundry_client import get_foundry_client
        client = get_foundry_client()
        
        prompt = f'''
        Analyze this document text:
        {doc_text[:3000]}
        
        USER INSTRUCTIONS FOR CHART: {instructions if instructions else "Extract the top sales/revenue numbers."}
        
        1. Security Check: Does this document explicitly belong to 'TechNova'? If it is from an external competitor, you MUST block it.
        2. If it is NOT TechNova, return exactly this JSON and nothing else: {{"authorized": false, "error": "Unauthorized: External Document Detected."}}
        3. If it IS TechNova, fulfill the User Instructions and return exactly this JSON:
        {{"authorized": true, "chart": {{"type": "bar|pie|line|donut", "title": "Custom Generated Chart", "x_label": "X-Axis", "y_label": "Y-Axis", "x_data": ["Item A", "Item B"], "y_data": [100, 200]}}}}
        
        Return ONLY valid JSON. No markdown backticks. Ensure y_data contains ONLY raw numbers.
        '''
        
        parser_agent = client.as_agent(name="DashboardParser", instructions="You are a strict JSON data extractor and security auditor. Output ONLY pure JSON.", tools=[])
        result = await parser_agent.run(prompt)
        
        import json
        clean_json = result.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
        
    except Exception as e:
        return {"authorized": False, "error": str(e)}

@app.post("/api/simulator/analyze_competitor")
async def analyze_competitor(file: UploadFile = File(...), instructions: Optional[str] = Form("")):
    try:
        file_bytes = await file.read()
        doc_text = extract_text_from_document(file_bytes)
        
        from backend.foundry_client import get_foundry_client
        client = get_foundry_client()
        
        prompt = f'''
        Analyze this competitor pricing/marketing document:
        {doc_text[:3000]}
        
        USER STRATEGY INSTRUCTIONS: {instructions if instructions else "Find their discount and counter it."}
        
        1. Follow the User Instructions to identify the competitor's strategy.
        2. TechNova current baseline profit margin is roughly 25%. A discount over 15% requires VP Approval.
        3. Recommend a specific promotional discount (integer) for TechNova based on the user instructions.
        
        Return exactly this JSON and nothing else:
        {{"competitor_summary": "Short analysis of what the competitor is doing based on instructions.", "recommended_discount": 12}}
        
        Return ONLY valid JSON. No markdown backticks.
        '''
        
        parser_agent = client.as_agent(name="SimulatorParser", instructions="You are a competitive strategy analyst. Output ONLY pure JSON.", tools=[])
        result = await parser_agent.run(prompt)
        
        import json
        clean_json = result.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
        
    except Exception as e:
        return {"error": str(e)}

