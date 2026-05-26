
import streamlit as st
from openai import OpenAI
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ── MEMORY ──
if "client_memory" not in st.session_state:
    st.session_state.client_memory = {}

if "agent_log" not in st.session_state:
    st.session_state.agent_log = []

# ── TOOLS ──
def research_system(system_type):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a UAE fire safety compliance expert. Return JSON only."},
            {"role": "user", "content": f"""For system: {system_type}
Return JSON:
{{
    "system_description": "brief description",
    "nfpa_standards": ["standards list"],
    "maintenance_requirements": ["maintenance tasks"],
    "civil_defence_requirements": ["UAE requirements"]
}}"""}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)

def assess_risk(expiry_date, system_type, years_installed):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a UAE fire safety risk assessor. Return JSON only."},
            {"role": "user", "content": f"""Assess risk for:
System: {system_type}
Expiry: {expiry_date}
Years Installed: {years_installed}
Today: May 2026

Return JSON:
{{
    "risk_score": <0-10>,
    "risk_level": "<Low/Medium/High/Critical>",
    "compliance_risks": ["risks list"],
    "days_until_expiry": <integer>,
    "urgent": <true/false>
}}"""}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    return json.loads(response.choices[0].message.content)

def write_proposal(client_name, contact_person, system_type, contract_value, expiry_date, research, risk):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Fire Gate's senior proposal writer. Write complete, professional AMC renewal proposals. No placeholders."},
            {"role": "user", "content": f"""Write complete AMC renewal proposal:
Client: {client_name}
Contact: {contact_person}
System: {system_type}
Value: AED {contract_value}
Expiry: {expiry_date}
Risk: {risk.get('risk_level')} ({risk.get('risk_score')}/10)
NFPA: {', '.join(research.get('nfpa_standards', []))}
Compliance Risks: {', '.join(risk.get('compliance_risks', []))}

Return JSON:
{{
    "subject": "email subject",
    "body": "complete proposal letter",
    "recommended_package": "package recommendation",
    "estimated_value": "AED {contract_value}"
}}"""}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)

def run_agent(client_name, contact_person, system_type, contract_value, expiry_date, years_installed):
    log = []
    
    # Step 1: Memory
    memory = st.session_state.client_memory.get(client_name, {})
    if memory:
        log.append(("💾", "Memory", f"Found existing client: {client_name}"))
    else:
        log.append(("💾", "Memory", f"New client: {client_name}"))
    
    # Step 2: Research
    log.append(("🔍", "Research", f"Looking up {system_type} requirements..."))
    research = research_system(system_type)
    log.append(("🔍", "Research", f"Found {len(research.get('nfpa_standards', []))} NFPA standards"))
    
    # Step 3: Risk
    log.append(("⚠️", "Risk Assessor", f"Calculating compliance risk..."))
    risk = assess_risk(expiry_date, system_type, years_installed)
    log.append(("⚠️", "Risk Assessor", f"Risk: {risk.get('risk_level')} ({risk.get('risk_score')}/10)"))
    
    # Step 4: Proposal
    log.append(("✍️", "Proposal Writer", "Generating renewal proposal..."))
    proposal = write_proposal(client_name, contact_person, system_type, contract_value, expiry_date, research, risk)
    log.append(("✍️", "Proposal Writer", "Proposal complete!"))
    
    # Step 5: Save memory
    st.session_state.client_memory[client_name] = {
        "system_type": system_type,
        "contract_value": contract_value,
        "expiry_date": expiry_date,
        "risk_level": risk.get('risk_level')
    }
    log.append(("💾", "Memory", f"Saved {client_name} to memory"))
    
    return research, risk, proposal, log

# ── PAGE CONFIG ──
st.set_page_config(page_title="Fire Gate | AMC Agent", page_icon="🔥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0D1B2A; }
h1,h2,h3,h4 { color: #E63946 !important; }
p, label, div, span { color: #CBD5E1; }
.stTextInput input, .stSelectbox > div > div {
    background-color: #162032 !important;
    color: #FFFFFF !important;
    border: 1px solid #1E3A5F !important;
    border-radius: 8px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #E63946, #C1121F) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    width: 100% !important;
}
.stButton > button:hover { background: #C1121F !important; }
.stDownloadButton > button {
    background: transparent !important;
    color: #E63946 !important;
    border: 1px solid #E63946 !important;
    border-radius: 8px !important;
    width: 100% !important;
}
hr { border-color: #1E3A5F !important; }
.stSpinner { color: #E63946 !important; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown("""
<div style='background:linear-gradient(135deg,#1a0505,#2D0A0A);border-bottom:2px solid #E63946;padding:20px 32px;margin:-1rem -1rem 2rem -1rem;text-align:center;'>
    <div style='font-size:26px;font-weight:700;color:#fff;letter-spacing:3px;'>🔥 FIRE GATE SAFETY & SECURITY</div>
    <div style='font-size:11px;color:#888;letter-spacing:4px;margin-top:4px;'>YOUR GATEWAY TO SAFETY</div>
    <div style='display:inline-block;background:#E63946;color:white;font-size:11px;font-weight:600;padding:4px 14px;border-radius:20px;margin-top:8px;letter-spacing:1px;'>AMC RENEWAL INTELLIGENCE AGENT</div>
</div>
""", unsafe_allow_html=True)

# ── STATS ──
c1,c2,c3,c4 = st.columns(4)
for col, num, label in [(c1,"500+","Employees"),(c2,"20+","Years"),(c3,"24/7","Response"),(c4,"UAE+KSA","Coverage")]:
    col.markdown(f"""<div style='background:#162032;border:1px solid #1E3A5F;border-radius:10px;padding:14px;text-align:center;'>
    <div style='font-size:20px;font-weight:700;color:#E63946;'>{num}</div>
    <div style='font-size:11px;color:#64748B;text-transform:uppercase;letter-spacing:1px;'>{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── LAYOUT ──
left, right = st.columns([1, 1.2])

with left:
    st.markdown("#### 📋 Client Details")
    client_name = st.text_input("Client Name", placeholder="e.g. Dubai Hills Mall")
    contact_person = st.text_input("Contact Person", placeholder="e.g. Mr. Ahmed Al Mansouri")
    system_type = st.selectbox("System Type", [
        "Fire Alarm System (FAS)",
        "Fire Fighting System (FFS)",
        "Emergency Exit Lighting (EEL)",
        "Public Address & Voice Evacuation (PAVA)",
        "CCTV & Access Control",
        "FAS + EEL Combined",
        "Full Package — All Systems"
    ])
    contract_value = st.text_input("Contract Value (AED)", placeholder="e.g. 45,000")
    expiry_date = st.text_input("Expiry Date", placeholder="e.g. 30 June 2026")
    years_installed = st.selectbox("Years Installed", ["1","2","3","4","5","6-10","10+"])
    
    generate = st.button("🔥 Run AMC Renewal Agent")
    
    # Memory panel
    if st.session_state.client_memory:
        st.markdown("#### 💾 Client Memory")
        for name, data in st.session_state.client_memory.items():
            st.markdown(f"""<div style='background:#162032;border:1px solid #1E3A5F;border-radius:8px;padding:10px;margin-bottom:6px;'>
            <div style='color:#E63946;font-weight:600;font-size:13px;'>{name}</div>
            <div style='color:#64748B;font-size:12px;'>{data.get('system_type')} · {data.get('risk_level')} risk</div>
            </div>""", unsafe_allow_html=True)

with right:
    if generate:
        if not client_name or not contract_value or not expiry_date:
            st.warning("Please fill in all required fields.")
        else:
            # Agent log
            st.markdown("#### 🤖 Agent Running...")
            log_placeholder = st.empty()
            
            with st.spinner("Agent working..."):
                research, risk, proposal, log = run_agent(
                    client_name, contact_person, system_type,
                    contract_value, expiry_date, years_installed
                )
            
            # Show log
            log_html = ""
            for emoji, tool, message in log:
                log_html += f"""<div style='display:flex;gap:8px;margin-bottom:6px;align-items:center;'>
                <span>{emoji}</span>
                <span style='color:#E63946;font-size:12px;font-weight:600;min-width:100px;'>{tool}</span>
                <span style='color:#94A3B8;font-size:12px;'>{message}</span>
                </div>"""
            log_placeholder.markdown(f"""<div style='background:#162032;border:1px solid #1E3A5F;border-radius:10px;padding:16px;margin-bottom:16px;'>{log_html}</div>""", unsafe_allow_html=True)
            
            # Risk score
            risk_color = {"Low":"#22C55E","Medium":"#F59E0B","High":"#EF4444","Critical":"#DC2626"}.get(risk.get('risk_level'),'#E63946')
            st.markdown(f"""<div style='background:#162032;border:2px solid {risk_color};border-radius:10px;padding:16px;margin-bottom:16px;text-align:center;'>
            <div style='font-size:13px;color:#64748B;letter-spacing:1px;text-transform:uppercase;'>Compliance Risk Score</div>
            <div style='font-size:36px;font-weight:700;color:{risk_color};'>{risk.get('risk_score')}/10</div>
            <div style='font-size:14px;font-weight:600;color:{risk_color};'>{risk.get('risk_level').upper()} RISK</div>
            </div>""", unsafe_allow_html=True)
            
            # Proposal
            st.markdown("#### 📄 Generated Proposal")
            st.markdown(f"""<div style='background:#162032;border:1px solid #E63946;border-radius:10px;padding:20px;max-height:400px;overflow-y:auto;'>
            <pre style='color:#E2E8F0;white-space:pre-wrap;font-family:Inter;font-size:13px;line-height:1.7;'>{proposal.get('body','')}</pre>
            </div>""", unsafe_allow_html=True)
            
            st.download_button(
                "📄 Download Proposal",
                data=proposal.get('body',''),
                file_name=f"FireGate_AMC_{client_name.replace(' ','_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# ── FOOTER ──
st.divider()
st.markdown("""<p style='text-align:center;color:#334155;font-size:12px;'>
🔥 Fire Gate Safety & Security Systems | Your Gateway to Safety<br>
Dubai Investment Park | +971 (4) 271 3794 | info@firegate.ae | Civil Defence Approved
</p>""", unsafe_allow_html=True)
