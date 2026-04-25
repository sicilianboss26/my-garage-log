import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. PRO-GRADE INTERFACE STYLING ---
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
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { 
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

# --- 2. AUTHENTICATION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Terminal Access</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter Tech PIN", type="password")
        if st.button("Initialize System"):
            if pin == "1234": st.session_state.auth = True; st.rerun()
            else: st.error("Unauthorized Access")
    st.stop()

# --- 3. DATABASE CORE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. FLEET CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛠️ SYSTEM CONTROL")
    if st.button("🔒 LOCK TERMINAL"): st.session_state.auth = False; st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("ACTIVE UNIT", f_df["Name"].tolist())
        active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]

        with st.expander("🗑️ DECOMMISSION UNIT"):
            if st.button("CONFIRM DELETE VEHICLE"):
                updated_fleet = f_df[f_df["Name"] != active_v][["Year", "Make", "Model", "Cat"]]
                updated_fleet.to_csv(FLEET, index=False); st.rerun()

    with st.expander("➕ ADD TO FLEET"):
        y = st.selectbox("YEAR", range(2027, 1990, -1))
        ma, mo = st.text_input("MAKE"), st.text_input("MODEL")
        ct = st.radio("CATEGORY", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("REGISTER VEHICLE"):
            new_row = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([pd.read_csv(FLEET), new_row]).to_csv(FLEET, index=False); st.rerun()

# --- 5. DIAGNOSTIC WORKSPACE ---
st.title("📟 ANTONINO'S GARAGE HUB")
if not active_v: st.warning("SYSTEM READY: PLEASE REGISTER A UNIT."); st.stop()

col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    st.subheader(f"UNIT ID: {active_v}")
    
    mode = st.selectbox("SERVICE CATEGORY", ["Oil Change", "Tires", "Repair", "Bulbs", "Legal File", "Admin: History Manager"])
    km = st.text_input("ODOMETER (KM)")
    
    # PHOTO UPLOADER (CAMERA/GALLERY)
    uploaded_file = st.file_uploader("📷 Attach Photo or Receipt", type=['png', 'jpg', 'jpeg'])
    photo_name = "None"
    if uploaded_file: photo_name = uploaded_file.name

    st.divider()
    entry = {k: "" for k in COLS}

    if mode == "Admin: History Manager":
        full_log = pd.read_csv(LOG)
        unit_rows = full_log[full_log["Unit"] == active_v]
        if not unit_rows.empty:
            unit_rows['Display'] = unit_rows['Date'] + " - " + unit_rows['Type']
            target = st.selectbox("Select Record to Remove", unit_rows.index, format_func=lambda x: unit_rows.loc[x, 'Display'])
            if st.button("🗑️ DELETE PERMANENTLY"):
                pd.read_csv(LOG).drop(target).to_csv(LOG, index=False); st.success("Deleted"); st.rerun()

    elif mode == "Oil Change":
        entry["Oil_M"] = st.text_input("Engine Oil Grade")
        if active_cat == "Motorcycle":
            c1, c2 = st.columns(2); with c1: entry["Oil_P"] = st.text_input("Primary Oil"); with c2: entry["Oil_T"] = st.text_input("Trans Oil")
        entry["Notes"] = st.text_input("Filter/Notes")
        if st.button("SAVE OIL LOG"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, km, entry["Notes"], entry["Oil_M"], entry["Oil_P"], entry["Oil_T"], "", "", "", photo_name]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False); st.rerun()

    elif mode == "Tires":
        c1, c2 = st.columns(2)
        with c1: entry["F_Tire"] = st.text_input("Front Size / PSI")
        with c2: entry["R_Tire"] = st.text_input("Rear Size / PSI")
        entry["Notes"] = st.text_input("Torque / Misc")
        if st.button("SAVE TIRE LOG"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, km, entry["Notes"], "", "", "", entry["F_Tire"], entry["R_Tire"], "", photo_name]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False); st.rerun()

    elif mode == "Repair":
        entry["Notes"] = st.text_area("Work Performed Details")
        if st.button("SAVE REPAIR LOG"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, km, entry["Notes"], "", "", "", "", "", "", photo_name]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False); st.rerun()

    elif mode == "Bulbs":
        entry["Bulbs"] = st.text_input("Bulb Spec")
        entry["Notes"] = st.text_input("Location")
        if st.button("SAVE BULB LOG"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, "", entry["Notes"], "", "", "", "", "", entry["Bulbs"], photo_name]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False); st.rerun()

    elif mode == "Legal File":
        l_type = st.selectbox("Type", ["Registration", "Insurance", "Inspection"])
        if st.button("LOG LEGAL UPDATE"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, "", f"{l_type} Verified", "", "", "", "", "", "", photo_name]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False); st.rerun()

with col2:
    st.subheader(f"📋 {active_v} HISTORY")
    hist_df = pd.read_csv(LOG)
    if not hist_df.empty:
        unit_history = hist_df[hist_df["Unit"] == active_v].sort_values(by="Date", ascending=False)
        st.dataframe(unit_history, use_container_width=True, hide_index=True)
