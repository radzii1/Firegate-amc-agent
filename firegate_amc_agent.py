
import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ── FIRE GATE BRANDING ──
st.set_page_config(
    page_title="Fire Gate AMC Renewal Agent",
    page_icon="🔥",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #1a1a1a; }
    h1, h2, h3 { color: #E63946 !important; font-family: Arial, sans-serif; }
    p, label, div { color: #FFFFFF !important; }
    .stButton > button {
        background-color: #E63946;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 24px;
        width: 100%;
    }
    .stButton > button:hover { background-color: #C1121F; }
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #2D2D2D;
        color: white;
        border: 1px solid #E63946;
        border-radius: 6px;
    }
    .result-box {
        background-color: #2D2D2D;
        border-left: 4px solid #E63946;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown("""
<div style='text-align:center; padding: 20px 0;'>
    <h1>🔥 Fire Gate Safety & Security</h1>
    <p style='color:#E63946; font-size:16px;'>AMC Renewal Intelligence Agent</p>
    <p style='color:#888; font-size:13px;'>AI-powered renewal proposals in seconds</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── INPUT FORM ──
st.subheader("Client Details")

col1, col2 = st.columns(2)

with col1:
    client_name = st.text_input("Client Name", placeholder="e.g. Dubai Hills Mall")
    system_type = st.selectbox("System Type", [
        "Fire Alarm System (FAS)",
        "Fire Fighting System (FFS)",
        "Emergency Exit Lighting (EEL)",
        "Public Address & Voice Evacuation (PAVA)",
        "CCTV & Access Control",
        "FAS + EEL (Combined)",
        "Full Package (All Systems)"
    ])

with col2:
    contract_value = st.text_input("Contract Value (AED)", placeholder="e.g. 45,000")
    expiry_date = st.text_input("Contract Expiry Date", placeholder="e.g. 30 June 2026")

years_installed = st.selectbox("Years Since Installation", ["1", "2", "3", "4", "5", "6-10", "10+"])

st.divider()

# ── GENERATE BUTTON ──
if st.button("🔥 Generate Renewal Proposal"):
    if not client_name or not contract_value or not expiry_date:
        st.warning("Please fill in all fields.")
    else:
        with st.spinner("Generating professional renewal proposal..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional proposal writer for Fire Gate Safety & Security Systems — 
a leading UAE fire protection company with 20+ years experience and clients including Emaar, DEWA, and NEOM.

Write AMC renewal proposals that are professional, specific to the system type, highlight civil defence compliance risk, and include a clear call to action."""
                    },
                    {
                        "role": "user",
                        "content": f"""Generate a professional AMC renewal proposal for:

Client: {client_name}
System Type: {system_type}
Contract Value: AED {contract_value}
Expiry Date: {expiry_date}
Years Installed: {years_installed}

Include:
1. Professional greeting
2. Expiry reminder
3. What's covered in the AMC
4. Risk of non-renewal (civil defence compliance)
5. Renewal package recommendation
6. Clear next steps
7. Fire Gate sign off"""
                    }
                ],
                temperature=0.3
            )
            proposal = response.choices[0].message.content

        st.subheader("Generated Renewal Proposal")
        st.markdown(f"""
        <div class='result-box'>
            <pre style='color:white; white-space:pre-wrap; font-family:Arial;'>{proposal}</pre>
        </div>
        """, unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="📄 Download Proposal",
            data=proposal,
            file_name=f"AMC_Renewal_{client_name.replace(' ','_')}.txt",
            mime="text/plain"
        )

        st.success("✅ Proposal generated! Review and send to client.")

# ── FOOTER ──
st.divider()
st.markdown("""
<p style='text-align:center; color:#555; font-size:12px;'>
Fire Gate Safety & Security Systems | Your Gateway to Safety<br>
Dubai Investment Park | +971 (4) 271 3794 | info@firegate.ae
</p>
""", unsafe_allow_html=True)
