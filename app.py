import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub", page_icon="🔧", layout="wide")

# This image is a professional, dark workshop setting
bg_img = "https://images.unsplash.com/photo-1507702553912-a15641ec5821?q=80&w=2600&auto=format&fit=crop"

st.markdown(f"""
    <style>
    /* Full Page Background */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{bg_img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Neon Glassmorphism effect for all main containers */
    [data-testid="stVerticalBlock"] > div:has(div.login-card), 
    .dash-header, .stForm, [data-testid="column"], [data-testid="stExpander"] {{
        background: rgba(15, 15, 15, 0.85) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}

    /* Title & Headers */
    .shop-logo {{ 
        font-size: 60px; font-weight: 900; color: #ff4b4b; 
        text-shadow: 0px 0px 10px rgba(255, 75, 75, 0.5); 
        letter-spacing: 3px; margin-bottom: 0px;
    }}
    .shop-subtitle {{ 
        color: #888; font-family: 'Courier New'; font-size: 14px; 
        letter-spacing: 10px; margin-bottom: 40px; text-transform: uppercase; 
    }}
    
    .working-on {{ color: #00ff00; font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; text-shadow: 0 0 10px rgba(0, 255, 0, 0.3); }}
    .current-time {{ color: #ff4b4b; font-size: 18px; font-weight: 800; text-transform: uppercase; }}

    /* Input Fields - Neon Green Text */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        color: #00ff00 !important;
        border: 1px solid #333 !important;
        font-family: 'Courier New', monospace !important;
    }}

    /* Buttons */
    .stButton>button {{ 
        width: 100%; background: linear-gradient(135deg, #ff4b4b 0%, #a10000 100%); 
        color: white; font-weight: 900; font-size: 16px;
        height: 3.5em; border-radius: 8px; border: none; text-transform: uppercase;
        box-shadow: 0 4px 10px rgba(255, 75, 75, 0.2);
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.6);
        transform: translateY(-2px);
    }}
    
    /* Sidebar Overhaul */
    section[data-testid="stSidebar"] {{ 
        background-color: rgba(10, 10, 10, 0.95) !important; 
        border-right: 1px solid #ff4b4b;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIME LOGIC (MONTREAL OFFSET UTC-4) ---
local_now = datetime.utcnow() - timedelta(hours=4)
display_time = local_now.strftime("%A, %B %d, %Y | %I:%M %p")

# --- 3. FRONT ACCESS ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div style="text-align:center; padding: 50px 0;">', unsafe_allow_html=True)
        st.markdown('<div class="shop-logo">GARAGE HUB</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">SYSTEM ONLINE</div>', unsafe_allow_html=True)
        pin = st.text_input("ACCESS PIN", type="password", placeholder="****")
        if st.button("AUTHENTICATE"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DATABASE SETUP ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

for f in [LOG, FLEET]:
    if not os.path.exists(f):
        pd.DataFrame(columns=COLS if f==LOG else ["Year", "Make", "Model", "Cat"]).to_csv(f, index=False)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 HUB CONTROL")
    if st.button("LOCK SYSTEM"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("SELECT ACTIVE BAY", f_df["Name"].tolist())
        if active_v:
            active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]
        
        with st.expander("DELETE UNIT"):
            if st.button("CONFIRM SCRAP"):
                new_f = f_df[f_df["Name"] != active_v].drop(columns=["Name"])
                new_f.to_csv(FLEET, index=False)
                st.rerun()
    
    with st.expander("REGISTER NEW UNIT"):
        y = st.selectbox("Year", range(2027, 1980, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("SAVE TO FLEET"):
            df_fleet = pd.read_csv(FLEET)
            new_row = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([df_fleet, new_row], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. DASHBOARD HEADER ---
if active_v:
    st.markdown(f"""
        <div class="dash-header">
            <div class="current-time">{display_time}</div>
            <div class="working-on">CURRENT VEHICLE: {active_v.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("FLEET EMPTY. ADD A VEHICLE IN THE SIDEBAR.")
    st.stop()

# --- 7. DATA ENTRY & LOGS ---
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    st.markdown("### ⚙️ LOG SERVICE")
    mode = st.selectbox("TASK", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("KM READING") if mode != "Legal File" else ""
    st.divider()

    entry = {k: "" for k in COLS}
    entry.update({"Date": local_now.strftime("%Y-%m-%d"), "Vehicle": active_v, "Type": mode, "KM": km})

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            c1, c2, c3 = st.columns(3)
            entry["Oil_M"] = c1.text_input("Motor")
            entry["Oil_P"] = c2.text_input("Primary")
            entry["Oil_T"] = c3.text_input("Trans")
        else:
            o_t = st.selectbox("Type", ["Full Synth", "Blend", "Conventional"])
            o_g = st.text_input("Grade")
            entry["Oil_M"] = f"{o_g} ({o_t})"
        entry["Notes"] = st.text_area("Notes / Filter #")

    elif mode == "Tires":
        t1, t2 = st.columns([2, 1])
        f_s, f_p = t1.text_input("Front Size"), t2.text_input("Front PSI")
        t3, t4 = st.columns([2, 1])
        r_s, r_p = t3.text_input("Rear Size"), t4.text_input("Rear PSI")
        entry["F_Tire"], entry["R_Tire"] = f"{f_s} ({f_p})", f"{r_s} ({r_p})"
        entry["Notes"] = st.text_area("Condition")

    elif mode == "Repair":
        rep_sys = st.selectbox("System", ["Engine", "Transmission", "Electrical", "Audio", "Suspension", "Brakes", "Exhaust", "Body"])
        entry["Type"] = f"Repair: {rep_sys}"
        entry["Notes"] = f"Parts: {st.text_area('Parts')} | Work: {st.text_area('Summary')}"

    elif mode == "Diagnostic":
        dtc = st.text_input("DTC / Fault Codes")
        entry["Notes"] = f"CODES: {dtc} | FINDINGS: {st.text_area('Tech Notes')}"

    elif mode == "Bulbs":
        entry["Type"] = f"Bulb: {st.selectbox('Position', ['Low', 'High', 'Fog', 'Signal', 'Tail'])}"
        entry["Notes"] = f"Spec: {st.text_input('Spec')} | {st.text_area('Notes')}"

    elif mode == "Legal File":
        entry["Type"] = f"Legal: {st.selectbox('Doc', ['Registration', 'Insurance', 'License', 'Safety'])}"
        entry["Notes"] = f"Expiry: {st.date_input('Valid Until')}"

    if st.button("💾 SAVE RECORD TO LOG"):
        df_l = pd.read_csv(LOG)
        pd.concat([df_l, pd.DataFrame([entry])], ignore_index=True).to_csv(LOG, index=False)
        st.rerun()

with col2:
    st.markdown("### 📋 HISTORY")
    h_df = pd.read_csv(LOG)
    if not h_df.empty:
        v_h = h_df[h_df["Vehicle"] == active_v].sort_values(by="Date", ascending=False)
        st.dataframe(v_h, use_container_width=True, hide_index=True)
        
        with st.expander("📝 EDIT / DELETE LOGS"):
            if not v_h.empty:
                v_h['Display'] = v_h['Date'] + " - " + v_h['Type']
                sel_idx = st.selectbox("Select Record", v_h.index, format_func=lambda x: v_h.loc[x, 'Display'])
                c_del, c_up = st.columns(2)
                if c_del.button("🗑️ DELETE"):
                    h_df.drop(sel_idx).to_csv(LOG, index=False)
                    st.rerun()
                up_notes = st.text_area("Edit Notes", value=str(h
