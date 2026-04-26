import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub Pro", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 10px; background-color: #1c1f26;
        padding: 50px; text-align: center; margin-top: 100px;
    }
    .shop-title { color: #ff4b4b; font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Segoe UI', sans-serif; text-transform: uppercase; }
    .working-on { color: #00ff00; font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold; margin-bottom: 20px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stDateInput>div>div>input { 
        background-color: #1c1f26 !important; color: #00ff00 !important; font-family: 'Courier New', monospace; border: 1px solid #444; 
    }
    .stButton>button { 
        width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; 
        height: 3.5em; border-radius: 5px; border: none; text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #d43f3f; border: 1px solid white; }
    section[data-testid="stSidebar"] { background-color: #1c1f26; border-right: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOG IN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password")
        if st.button("Log In"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# --- 3. DATABASE SETUP ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🛠️ CONTROL")
    if st.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("SELECT VEHICLE", f_df["Name"].tolist())
        if active_v:
            active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]
        with st.expander("Delete Vehicle"):
            if st.button("Confirm Delete"):
                new_f = f_df[f_df["Name"] != active_v].drop(columns=["Name"])
                new_f.to_csv(FLEET, index=False)
                st.rerun()
    with st.expander("Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            pd.concat([pd.read_csv(FLEET), pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("📟 ANTONINO'S GARAGE HUB")
if not active_v:
    st.info("Please add a vehicle to begin.")
    st.stop()

st.markdown(f'<div class="working-on">WORKING ON: {active_v.upper()}</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    # --- FORM INITIALIZATION ---
    mode = st.selectbox("CATEGORY", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    
    km = ""
    if mode != "Legal File":
        km = st.text_input("ODOMETER (KM)")
        
    uploaded_file = st.file_uploader("📷 Attach Photo/Receipt", type=['png', 'jpg', 'jpeg'])
    photo_name = uploaded_file.name if uploaded_file else "None"
    st.divider()

    entry = {k: "" for k in COLS}
    entry["Date"] = datetime.now().strftime("%Y-%m-%d")
    entry["Vehicle"] = active_v
    entry["Type"] = mode
    entry["KM"] = km
    entry["Photo"] = photo_name

    # --- CATEGORY LOGIC ---
    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            st.markdown("### 🏍️ Triple-Oil Service")
            c1, c2, c3 = st.columns(3)
            with c1: entry["Oil_M"] = st.text_input("Engine Oil", "20W-50")
            with c2: entry["Oil_P"] = st.text_input("Primary Oil")
            with c3: entry["Oil_T"] = st.text_input("Trans Oil")
            st.markdown("---")
            o_filter = st.text_input("Filter Model #")
            o_notes = st.text_area("Notes")
            entry["Notes"] = f"Filter: {o_filter} | {o_notes}"
        else:
            o_type = st.selectbox("Oil Type", ["Full Synthetic", "Synthetic Blend", "Conventional"])
            o_grade = st.text_input("Oil Grade")
            o_liters = st.text_input("Liters")
            o_filter = st.text_input("Filter #")
            note_content = st.text_area("Notes")
            entry["Oil_M"] = f"{o_grade} ({o_type})"
            entry["Notes"] = f"{o_liters}L | Filter: {o_filter} | {note_content}"

    elif mode == "Tires":
        st.markdown("### Tires & PSI")
        ft1, ft2 = st.columns([2, 1])
        f_s = ft1.text_input("Front Size")
        f_p = ft2.text_input("Front PSI")
        rt1, rt2 = st.columns([2, 1])
        r_s = rt1.text_input("Rear Size")
        r_p = rt2.text_input("Rear PSI")
        entry["F_Tire"] = f"{f_s} ({f_p} PSI)"
        entry["R_Tire"] = f"{r_s} ({r_p} PSI)"
        entry["Notes"] = st.text_area("Service Notes")

    elif mode == "Repair":
        rep_cat = st.selectbox("System", ["Engine", "Transmission", "Electrical/Electronics", "Audio/Custom", "Suspension", "Brakes", "Exhaust", "Body"])
        entry["Type"] = f"Repair: {rep_cat}"
        entry["Notes"] = st.text_area("Work Details")

    elif mode == "Diagnostic":
        st.markdown("### ⚡ Diagnostic Scan")
        d1, d2 = st.columns(2)
        dtc = d1.text_input("DTC (Engine)")
        abs_c = d1.text_input("ABS")
        srs = d2.text_input("SRS")
        oth = d2.text_input("Body/Other")
        diag_notes = st.text_area("Diagnostic Findings")
        entry["Notes"] = f"DTC:{dtc} | SRS:{srs} | ABS:{abs_c} | Body:{oth} | {diag_notes}"

    elif mode == "Bulbs":
        st.markdown("### 💡 Lighting")
        b_l = st.selectbox("Location", ["Low/High Beam", "Fog Lights", "Turn/Marker", "License Plate", "Tail/Brake", "Reverse", "Interior", "Side Marker/Custom"])
        entry["Type"] = f"Lighting: {b_l}"
        entry["Bulbs"] = st.text_input("Bulb Spec")
        entry["Notes"] = st.text_area("Notes")

    elif mode == "Legal File":
        st.markdown("### 📄 Legal / Papers")
        doc_type = st.selectbox("Document Type", ["Insurance", "Registration", "License"])
        d_col1, d_col2 = st.columns(2)
        if doc_type == "License":
            with d_col1: pay_d = st.date_input("Renewal/Payment Date")
            with d_col2: exp_d = st.date_input("Expiry Date")
            entry["Notes"] = f"Renewed: {pay_d} | Expires: {exp_d}"
        else:
            with d_col1: from_d = st.date_input("From Date")
            with d_col2: to_d = st.date_input("To Date")
            entry["Notes"] = f"Period: {from_d} to {to_d}"
        entry["Type"] = f"Legal: {doc_type}"

    if st.button("💾 SAVE RECORD"):
        pd.concat([pd.read_csv(LOG), pd.DataFrame([entry])],
