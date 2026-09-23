import json
import streamlit as st
def render_chat_message(content):
    import re
    import json
    import plotly.express as px
    
    chart_match = re.search(r'<CHART>(.*?)</CHART>', content, re.DOTALL)
    if chart_match:
        text_content = content.replace(chart_match.group(0), "")
        st.markdown(text_content, unsafe_allow_html=True)
        try:
            chart_data = json.loads(chart_match.group(1))
            
            # SANITIZE DATA: LLMs often accidentally put strings like "$134,925" instead of raw numbers
            raw_y = chart_data.get("y_data") or chart_data.get("values") or chart_data.get("y") or chart_data.get("data") or []
            clean_y = []
            for val in raw_y:
                if isinstance(val, str):
                    cleaned = re.sub(r'[^\d\.\-]', '', val)
                    clean_y.append(float(cleaned) if cleaned else 0.0)
                else:
                    clean_y.append(float(val) if val is not None else 0.0)
            
            # Ensure x and y lengths match to prevent blank grids
            clean_x = chart_data.get("x_data") or chart_data.get("labels") or chart_data.get("x") or chart_data.get("names") or []
            
            # Auto-fallback if AI used weird keys for y-data
            if not clean_y:
                for k, v in chart_data.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], (int, float)):
                        clean_y = [float(x) for x in v]
                        break
            
            # Auto-fallback if AI used weird keys for x-data
            if not clean_x:
                for k, v in chart_data.items():
                    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], str):
                        clean_x = v
                        break
            
            min_len = min(len(clean_x), len(clean_y))
            clean_x = clean_x[:min_len]
            clean_y = clean_y[:min_len]
            
            if min_len == 0:
                st.warning("📊 AI attempted to draw a chart, but the dataset was empty or improperly formatted.")
                return

            chart_type = chart_data.get("type", "bar").lower()
            if chart_type == "bar":
                fig = px.bar(
                    x=clean_x, y=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    labels={'x': chart_data.get("x_label", "X"), 'y': chart_data.get("y_label", "Y")},
                    template="plotly_dark"
                )
            elif chart_type == "pie":
                fig = px.pie(
                    names=clean_x, values=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    template="plotly_dark"
                )
            elif chart_type == "line":
                fig = px.line(
                    x=clean_x, y=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    labels={'x': chart_data.get("x_label", "X"), 'y': chart_data.get("y_label", "Y")},
                    template="plotly_dark"
                )
            elif chart_type == "scatter":
                fig = px.scatter(
                    x=clean_x, y=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    labels={'x': chart_data.get("x_label", "X"), 'y': chart_data.get("y_label", "Y")},
                    template="plotly_dark",
                    size_max=15
                )
                fig.update_traces(marker=dict(size=12))
            elif chart_type == "area":
                fig = px.area(
                    x=clean_x, y=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    labels={'x': chart_data.get("x_label", "X"), 'y': chart_data.get("y_label", "Y")},
                    template="plotly_dark"
                )
            elif chart_type == "donut":
                fig = px.pie(
                    names=clean_x, values=clean_y,
                    title=chart_data.get("title", "Data Chart"),
                    template="plotly_dark",
                    hole=0.4
                )
            else:
                fig = px.bar(x=clean_x, y=clean_y, template="plotly_dark") # fallback
                
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch", key=f"chart_{__import__('uuid').uuid4().hex}")
        except Exception as e:
            st.error(f"Failed to render generative chart: {e}")
    else:
        st.markdown(content, unsafe_allow_html=True)

import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="TechNova AI Assistant", page_icon="🤖", layout="wide")

import os
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/api")


# --- CUSTOM UI & ANIMATIONS ---
st.markdown('''
<style>
/* Base Dark Theme matching InvoiceIQ */
.stApp {
    background-color: #09090e !important; 
    color: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Beautiful Chat Bubbles */
[data-testid="stChatMessage"] {
    background-color: #111116 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    padding: 15px 20px !important;
    margin-bottom: 15px !important;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3) !important;
}
[data-testid="chatAvatarIcon-user"] {
    background-color: #7c3aed !important;
}

/* Giant Clean Typography */
.hero-title {
    font-size: 5rem !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.02em;
    background: linear-gradient(180deg, #ffffff 0%, #a5a5b5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 25px;
    margin-top: 0px;
}
.hero-highlight {
    color: #8b5cf6 !important; 
    -webkit-text-fill-color: #8b5cf6 !important;
    text-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
}
.hero-subtitle {
    color: #9ca3af;
    font-size: 1.15rem;
    line-height: 1.6;
    font-weight: 400;
    margin-bottom: 30px;
    max-width: 90%;
}

/* Glowing Purple Buttons */
.stButton > button {
    background: #6d28d9 !important; 
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px 0 rgba(109, 40, 217, 0.39) !important;
}
.stButton > button:hover {
    background: #7c3aed !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
}

/* Login Card Container */
div[data-testid="stVerticalBlock"] > div[style*="border"] {
    background-color: #111116 !important; 
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.8) !important;
    padding: 15px;
}

/* Inputs */
.stTextInput > div > div > input {
    background-color: #1a1825 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: white !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 1px #8b5cf6 !important;
}

/* Tabs */
div[data-baseweb="tab-list"] {
    background-color: #111116 !important;
    border-radius: 10px !important;
    padding: 6px !important;
    gap: 6px !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
}
div[data-baseweb="tab"] {
    border-radius: 8px !important;
    background: transparent !important;
    border: none !important;
}
div[aria-selected="true"] {
    background: rgba(139, 92, 246, 0.15) !important;
    border: 1px solid rgba(139, 92, 246, 0.3) !important;
    color: #c4b5fd !important;
}
div[data-testid="stTabBody"] {
    animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}


/* Sidebar Button Override */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #cbd5e1 !important;
    box-shadow: none !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    padding: 8px 12px !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
    height: auto !important;
    min-height: 40px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    transform: none !important;
    color: white !important;
}
[data-testid="stSidebar"] div[data-testid="column"]:nth-child(2) .stButton > button {
    justify-content: center !important;
    color: #ef4444 !important;
}

/* INNER WORKSPACE POLISH */
[data-testid="stSidebar"] {
    background-color: #050508 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
.workspace-header {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #f8fafc;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 15px;
    margin-bottom: 30px;
    margin-top: -20px;
}
/* Chat message styling */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 10px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px !important;
    margin-bottom: 10px;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: rgba(139, 92, 246, 0.05) !important;
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 15px !important;
    margin-bottom: 10px;
}
/* Better sidebar radio links */
.stRadio > div[role="radiogroup"] > label {
    background-color: transparent !important;
    border-radius: 8px;
    padding: 8px 12px;
    transition: all 0.2s;
}
.stRadio > div[role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.05) !important;
}
</style>

''', unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your TechNova AI Assistant. How can I help you today?"}]
    st.session_state.current_session_id = None
    st.session_state.current_tag = None

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Custom CSS for the Mac-style window and InvoiceIQ layout
    st.markdown('''
    <style>
    /* Mac-style Login Container Hack */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #111116 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8) !important;
        padding-top: 30px !important;
        position: relative;
        overflow: visible !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        content: '';
        position: absolute;
        top: 18px;
        left: 20px;
        width: 12px; height: 12px;
        border-radius: 50%;
        background-color: #ff5f56;
        box-shadow: 20px 0 0 #ffbd2e, 40px 0 0 #27c93f;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]::after {
        content: 'TechNova Secure Node';
        position: absolute;
        top: 15px;
        left: 0;
        width: 100%;
        text-align: center;
        color: #6b7280;
        font-size: 0.75rem;
        font-weight: 600;
        pointer-events: none;
    }
    

/* Sidebar Button Override */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #cbd5e1 !important;
    box-shadow: none !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    padding: 8px 12px !important;
    font-weight: 400 !important;
    justify-content: flex-start !important;
    height: auto !important;
    min-height: 40px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    transform: none !important;
    color: white !important;
}
[data-testid="stSidebar"] div[data-testid="column"]:nth-child(2) .stButton > button {
    justify-content: center !important;
    color: #ef4444 !important;
}

/* INNER WORKSPACE POLISH */
[data-testid="stSidebar"] {
    background-color: #050508 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
.workspace-header {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #f8fafc;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 15px;
    margin-bottom: 30px;
    margin-top: -20px;
}
/* Chat message styling */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 10px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background-color: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px !important;
    margin-bottom: 10px;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background-color: rgba(139, 92, 246, 0.05) !important;
    border: 1px solid rgba(139, 92, 246, 0.15);
    border-radius: 12px;
    padding: 15px !important;
    margin-bottom: 10px;
}
/* Better sidebar radio links */
.stRadio > div[role="radiogroup"] > label {
    background-color: transparent !important;
    border-radius: 8px;
    padding: 8px 12px;
    transition: all 0.2s;
}
.stRadio > div[role="radiogroup"] > label:hover {
    background-color: rgba(255,255,255,0.05) !important;
}
</style>

    ''', unsafe_allow_html=True)

    # 2-Column SaaS Landing Page Layout
    main_col1, empty_col, main_col2 = st.columns([1.1, 0.1, 1.2])
    
    with main_col1:
        st.markdown('''
        <div style="margin-top: 10px;">
            <div style="display: inline-block; padding: 4px 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; color: #9ca3af; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 25px;">
                NEXT-GEN FINANCIAL AI
            </div>
            <h1 style="font-size: 5rem; font-weight: 800; line-height: 1.05; letter-spacing: -0.02em; background: linear-gradient(180deg, #ffffff 0%, #a5a5b5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 20px 0; padding: 0;">
                Extract.<br>Classify.<br><span style="color: #8b5cf6; -webkit-text-fill-color: #8b5cf6;">Scale with AI.</span>
            </h1>
            <p style="color: #9ca3af; font-size: 1.15rem; line-height: 1.6; font-weight: 400; margin-bottom: 40px; max-width: 95%;">
                TechNova transforms your messy data and operations into structured financial intelligence. 
                Automatically route queries, persist cloud memory, and let your team interrogate numbers with specialist AI agents.
            </p>
        </div>
        ''', unsafe_allow_html=True)

    with main_col2:
        with st.container(border=True):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: left; margin-top: 0px; margin-bottom: 15px; color: #f8fafc; padding-left: 5px;'>Financial Intelligence</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #9ca3af; font-size: 0.85rem; padding-left: 5px; margin-top: -15px; margin-bottom: 20px;'>Live Business Analytics & Secure Auth</p>", unsafe_allow_html=True)
            
            tab1, tab2 = st.tabs(["Secure Access", "Create Identity"])
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("login_form"):
                    st.text_input("Username", key="login_username", placeholder="Enter your TechNova ID")
                    st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
                    st.markdown("<br>", unsafe_allow_html=True)
                    submitted = st.form_submit_button("Initialize Workspace ➔", width="stretch", type="primary")
                    if submitted:
                        if st.session_state.login_username:
                            st.success("Authentication successful! Loading workspace...")
                            import time
                            time.sleep(0.5)
                            st.session_state.logged_in = True
                            st.session_state.username = st.session_state.login_username
                            st.rerun()
                        else:
                            st.error("Access Denied: Missing credentials.")
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                with st.form("register_form"):
                    st.text_input("Choose Username", key="reg_username")
                    st.text_input("Choose Password", type="password", key="reg_password")
                    reg_submit = st.form_submit_button("Register Identity", width="stretch")
                    if reg_submit:
                        if st.session_state.reg_username:
                            st.success("Identity created securely. You may now access the workspace.")
                        else:
                            st.error("Error: Fields cannot be empty.")
    st.stop()

with st.sidebar:
    st.markdown("## ⚡ TechNova OS")
    st.markdown("---")
    page = st.radio("Navigation", ["💬 AI Business Chat", "📊 Executive Dashboard", "🎛️ What-If Simulator"])
    st.markdown("---")
    st.caption("Multi-Agent Architecture v2.0")
    
@st.dialog("💾 Save Chat to Cloud")
def save_chat_dialog():
    session_id = st.text_input("Session Name (e.g., meeting_notes)")
    preset_tags = ["General", "Sales", "Customer Support", "Policy Simulation", "Custom..."]
    chat_tag = st.selectbox("Category", preset_tags)
    if chat_tag == "Custom...":
        chat_tag = st.text_input("Enter Custom Category")
        
    if st.button("Save Now", type="primary", width="stretch"):
        if session_id and chat_tag:
            try:
                import requests
                res = requests.post(f"{API_BASE}/memory/save", json={"session_id": session_id, "tag": chat_tag, "messages": st.session_state.messages})
                res.raise_for_status()
                st.session_state.current_session_id = session_id
                st.session_state.current_tag = chat_tag
                st.success("Saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

with st.sidebar:
    st.markdown("---")
    st.header("☁️ Cloud Memory")
    if st.button("📄 Start New Chat", width="stretch"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your TechNova AI Assistant. How can I help you today?"}]
        st.session_state.current_session_id = None
        st.session_state.current_tag = None
        st.rerun()
        
    if st.button("➕ Rename & Save Chat", width="stretch"):
        save_chat_dialog()
        
    st.markdown("---")
    st.subheader("📁 Your Saved Chats")
    
    try:
        import requests
        chat_list = requests.get(f"{API_BASE}/memory/list").json().get("chats", [])
        if not chat_list:
            st.caption("No chats saved yet.")
        else:
            for c in chat_list:
                c_name = c['session_id'][:25] + "..." if len(c['session_id']) > 25 else c['session_id']
                display_name = f"📄 {c_name}"
                hover_text = f"Name: {c['session_id']} | Category: {c['tag']}"
                
                chat_col, del_col = st.columns([0.8, 0.2])
                with chat_col:
                    if st.button(display_name, key=f"load_{c['tag']}_{c['session_id']}", width="stretch", help=hover_text):
                        try:
                            res = requests.get(f"{API_BASE}/memory/load", params={"session_id": c['session_id'], "tag": c['tag']})
                            if res.status_code == 200:
                                st.session_state.messages = res.json()["messages"]
                                st.session_state.current_session_id = c['session_id']
                                st.session_state.current_tag = c['tag']
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed to load: {e}")
                with del_col:
                    if st.button("🗑️", key=f"del_{c['tag']}_{c['session_id']}", help="Delete Chat"):
                        try:
                            res = requests.delete(f"{API_BASE}/memory/delete", params={"session_id": c['session_id'], "tag": c['tag']})
                            if res.status_code == 200:
                                if st.session_state.get('current_session_id') == c['session_id']:
                                    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your TechNova AI Assistant."}]
                                    st.session_state.current_session_id = None
                                    st.session_state.current_tag = None
                                st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
                            
    except Exception as e:
        st.caption("Could not load cloud memory.")

if page == "💬 AI Business Chat":
    import uuid
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "<CHART>" in msg["content"]:
                render_chat_message(msg["content"])
            else:
                st.markdown(msg["content"])
                
    if prompt := st.chat_input("Deploy a task to the multi-agent swarm...", accept_file="multiple"):
        user_text = prompt.text if hasattr(prompt, 'text') else prompt
        
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            st_status = st.status("Deploying Multi-Agent Swarm...", expanded=True)
            with st_status:
                try:
                    import requests
                    import json
                    
                    payload = {
                        "query": user_text,
                        "chat_history": json.dumps(st.session_state.messages[:-1])
                    }
                    
                    files_to_send = []
                    if hasattr(prompt, 'files') and prompt.files:
                        for f in prompt.files:
                            files_to_send.append(('file', (f.name, f.getvalue(), f.type)))
                            
                    if files_to_send:
                        res = requests.post(f"{API_BASE}/chat", data=payload, files=files_to_send, timeout=120)
                    else:
                        res = requests.post(f"{API_BASE}/chat", data=payload, timeout=120)
                    if res.status_code == 200:
                        data = res.json()
                        st_status.update(label="Tasks Executed Successfully", state="complete", expanded=False)
                        
                        # Handle both "answer" (used in backend) and "response" fallback
                        chat_reply = data.get("answer", data.get("response", "Error: No response found in backend data."))
                        
                        st.markdown(chat_reply)
                        if "<CHART>" in chat_reply:
                            render_chat_message(chat_reply)
                        st.session_state.messages.append({"role": "assistant", "content": chat_reply})
                        
                        if not st.session_state.current_session_id and len(st.session_state.messages) == 3:
                            title_res = requests.post(f"{API_BASE}/memory/generate_title", json={"message": user_text}, timeout=10)
                            if title_res.status_code == 200:
                                gen_id = title_res.json().get("session_id")
                                save_res = requests.post(f"{API_BASE}/memory/save", json={"session_id": gen_id, "tag": "General", "messages": st.session_state.messages})
                                if save_res.status_code == 200:
                                    st.session_state.current_session_id = gen_id
                                    st.session_state.current_tag = "General"
                                    st.rerun()
                    else:
                        st_status.update(label="Agent Swarm Failed", state="error", expanded=True)
                        st.error(f"Agent Error: {res.text}")
                except Exception as e:
                    st_status.update(label="System Offline", state="error", expanded=True)
                    st.error(f"Communication failure: {e}")

elif page == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard")
    st.caption("Real-time telemetry of your business operations")
    
    with st.spinner("Loading live metrics..."):
        try:
            import requests
            import pandas as pd
            import plotly.express as px
            res = requests.get(f"{API_BASE}/dashboard")
            if res.status_code == 200:
                data = res.json()
                ov = data["overview"]
            
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Customers", f"{ov['total_customers']:,}", f"-{ov['inactive_customers']} Inactive", delta_color="inverse")
                col2.metric("Weekly Revenue", f"${ov['current_week_revenue']:,.2f}", f"{ov['revenue_change_pct']}%")
                col3.metric("Weekly Orders", f"{ov['weekly_orders']:,}")
                col4.metric("Return Rate", f"{ov['weekly_return_rate_pct']}%", "High" if ov['weekly_return_rate_pct'] > 5 else "Healthy", delta_color="inverse")
            
                st.markdown("<br>", unsafe_allow_html=True)
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.subheader("🏆 Top Performing Products")
                    df_top = pd.DataFrame(data["top_products"])
                    if not df_top.empty:
                        fig1 = px.bar(df_top, x="product_name", y="total_revenue", color="total_revenue", color_continuous_scale="Purples")
                        fig1.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
                        st.plotly_chart(fig1, use_container_width=True)
                    
                with chart_col2:
                    st.subheader("⚠️ High Return Risk Products")
                    df_ret = pd.DataFrame(data["highest_return_products"])
                    if not df_ret.empty:
                        y_col = "return_rate_pct" if "return_rate_pct" in df_ret.columns else df_ret.columns[-1]
                        fig2 = px.bar(df_ret, y="product_name", x=y_col, orientation='h', color=y_col, color_continuous_scale="Reds")
                        fig2.update_layout(template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color="#f8fafc"))
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.success("✨ Excellent! No high-risk return products detected this week.")
                        st.info("Product quality and fulfillment metrics are operating at optimal levels.")
        except Exception as e:
            st.error(f"Could not connect to the backend API: {e}")

    # AI Document Visualizer (Moved to bottom and wrapped in form)
    st.markdown("---")
    st.subheader("🧠 AI Document Visualizer")
    st.caption("Upload a TechNova internal report to dynamically render custom analytics.")
    
    with st.form("dash_pdf_form"):
        colA, colB = st.columns([1, 1])
        with colA:
            uploaded_pdf = st.file_uploader("Upload Internal TechNova Report (.pdf)", type=["pdf"], key="dash_pdf")
        with colB:
            st.markdown("<br>", unsafe_allow_html=True)
            dash_instructions = st.text_input("Custom AI Instructions (Optional)", placeholder="e.g., Draw a pie chart of Q4 projections")
        
        analyze_btn = st.form_submit_button("Authenticate & Analyze Document", width="stretch", type="primary")
        
        if analyze_btn and uploaded_pdf is not None:
            with st.spinner("Authenticating Document & Extracting Data..."):
                try:
                    import requests
                    files = {'file': (uploaded_pdf.name, uploaded_pdf.getvalue(), uploaded_pdf.type)}
                    res = requests.post(f"{API_BASE}/dashboard/parse_internal_pdf", files=files, data={"instructions": dash_instructions}, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        if not data.get("authorized"):
                            st.error(f"🚨 Security Alert: {data.get('error', 'Unauthorized Document')}")
                        else:
                            st.success("✅ Internal TechNova Document Authenticated.")
                            chart_info = data.get("chart", {})
                            
                            c_type = chart_info.get("type", "bar").lower()
                            import plotly.express as px
                            if c_type in ["pie", "donut"]:
                                fig = px.pie(names=chart_info.get("x_data", []), values=chart_info.get("y_data", []), title=chart_info.get("title", "Custom Graph"), hole=0.4 if c_type=="donut" else 0, template="plotly_dark")
                            elif c_type == "line":
                                fig = px.line(x=chart_info.get("x_data", []), y=chart_info.get("y_data", []), title=chart_info.get("title", "Custom Graph"), template="plotly_dark")
                            else:
                                fig = px.bar(x=chart_info.get("x_data", []), y=chart_info.get("y_data", []), title=chart_info.get("title", "Custom Graph"), labels={'x': chart_info.get("x_label", "X"), 'y': chart_info.get("y_label", "Y")}, template="plotly_dark")
                            
                            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Failed to parse document.")
                except Exception as e:
                    st.error(f"Error: {e}")

elif page == "🎛️ What-If Simulator":
    st.title("🎛️ Campaign Simulator")
    st.caption("Model the financial and policy impact of promotional campaigns")
    
    st.markdown("### 🎯 Competitive Strategy Engine")
    recommended_discount = 10
    
    with st.form("sim_pdf_form"):
        colA, colB = st.columns([1, 1])
        with colA:
            comp_pdf = st.file_uploader("Upload Competitor Pricing Data (.pdf)", type=["pdf"], key="comp_pdf")
        with colB:
            st.markdown("<br>", unsafe_allow_html=True)
            sim_instructions = st.text_input("Strategic Goal (Optional)", placeholder="e.g., We must aggressively beat them by 5%")
        
        analyze_comp = st.form_submit_button("Run Competitive Analysis", width="stretch", type="primary")
        if analyze_comp and comp_pdf is not None:
            with st.spinner("Analyzing Competitor Pricing Strategy..."):
                try:
                    import requests
                    files = {'file': (comp_pdf.name, comp_pdf.getvalue(), comp_pdf.type)}
                    res = requests.post(f"{API_BASE}/simulator/analyze_competitor", files=files, data={"instructions": sim_instructions}, timeout=60)
                    if res.status_code == 200:
                        cdata = res.json()
                        st.info(f"**Competitor Analysis:** {cdata.get('competitor_summary', '')}")
                        recommended_discount = cdata.get("recommended_discount", 10)
                        st.success(f"🎯 **Strategic Recommendation:** We recommend setting the Promotional Discount slider below to **{recommended_discount}%** to capture market share.")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    st.markdown("---")
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.markdown("### 🎛️ Campaign Levers")
        target_customers = st.number_input("Target Audience Size", min_value=1, value=50, step=10)
        avg_order = st.number_input("Estimated Cart Value ($)", min_value=10.0, value=750.0, step=50.0)
        discount = st.slider("Promotional Discount (%)", 0, 30, int(recommended_discount))
        expected_conversion = st.slider("Expected Conversion Rate (%)", 1, 100, 15)
        
        if st.button("🚀 Run Financial Model", type="primary", width="stretch"):
            with st.spinner("Running AI simulations..."):
                try:
                    import requests
                    res = requests.post(f"{API_BASE}/simulate", json={
                        "target_audience_size": target_customers,
                        "estimated_cart_value": avg_order,
                        "promotional_discount_pct": discount,
                        "expected_conversion_rate_pct": expected_conversion
                    })
                    if res.status_code == 200:
                        data = res.json()
                        
                        with col2:
                            st.markdown("### 📊 Projection Results")
                            
                            tab1, tab2, tab3 = st.tabs(["Financial Impact", "Policy Governance", "Risk Assessment"])
                            
                            with tab1:
                                fin = data['financial_projection']
                                st.metric("Projected Net Profit Margin", f"{fin['projected_net_profit_margin_pct']}%", f"{fin['margin_delta_pct']}%")
                                
                                b_col1, b_col2 = st.columns(2)
                                b_col1.metric("Gross GMV", f"${fin['projected_gross_gmv']:,.2f}")
                                b_col1.metric("Promotional Cost", f"-${fin['promotional_discount_cost']:,.2f}")
                                b_col2.metric("Estimated COGS", f"-${fin['estimated_cogs']:,.2f}")
                                b_col2.metric("Converted Customers", f"{fin['estimated_converted_customers']} buyers")
                            
                            with tab2:
                                gov = data['governance_assessment']
                                if gov['is_policy_compliant']:
                                    st.success(f"✨ **APPROVED:** {gov['status']}")
                                else:
                                    st.error(f"🛑 **BLOCKED:** {gov['status']}")
                            
                                st.info(f"**Policy Enforced:** {gov['policy_id']}")
                                st.write(f"The maximum automated discount allowed without VP signoff is **{gov['max_allowed_automated_discount']}**.")
                            
                                if gov['requires_vp_signoff']:
                                    st.warning("This campaign requires manual Executive Approval before it can be executed.")
                                
                            with tab3:
                                st.markdown("##### Identified Risks")
                                for risk in data['assumptions_and_risks']:
                                    st.warning(risk)
                            
                except Exception as e:
                    st.error(f"Simulation failed: {e}")
        else:
            with col2:
                st.markdown("### 📊 Projection Results")
                st.info("👈 Adjust your levers and click 'Run Financial Model' to see projections.")
