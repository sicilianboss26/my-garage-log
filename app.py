import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. TERMINAL SETUP ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 15px; background-color: #262730;
        padding: 40px; text-align: center; margin-top: 50px;
    }
    .shop-title { color: #ff4b4b; font-size: 28px; font-weight: 900; text-transform: uppercase; margin: 0; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; height: 3.5em; border-radius: 8px; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Courier New', monospace; letter-spacing: 2px; }
    div[data-baseweb="select"] { border: 1px solid #ff4b4b; border-radius: 5px; }
    .stTextInput>div>div>input { background-color: #262730; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE LOCK ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password", key="gate_pin")
        if st.button("Unlock"):
            if pin == "1234": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA PERSISTENCE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
# Added "KM" to the columns for better tracking
COLS = ["Date", "Unit", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 Control Panel")
    if st.button("🔒 Lock Terminal"): st.session_state.auth = False; st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("Select Vehicle", f_df["Name"].tolist())
        active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]

        with st.expander("🗑️ Remove Vehicle"):
            if st.button("Confirm Delete"):
                f_df[f_df["Name"] != active_v][["Year", "Make", "Model", "Cat"]].to_csv(FLEET, index=False)
                st.rerun()

    with st.expander("➕ Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma, mo = st.text_input("Make"), st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save to Fleet"):
            new_v = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False); st.rerun()

# --- 5. WORKSPACE ---
st.title("⚙️ Garage Hub Terminal")
if not active_v: st.info("👈 Select a vehicle to start."); st.stop()

col1, col2 = st.columns([1.2, 2], gap="large")

with col1:
    st.subheader(f"Unit: {active_v}")
    
    mode = st.selectbox("Select Service Category", ["Repair", "Oil Change", "Tires", "Bulbs"])
    km_input = st.text_input("Odometer (KM)")
    
    st.divider()
    
    entry = {k: "" for k in COLS}

    if mode == "Repair":
        entry["Notes"] = st.text_area("Work Details (Mechanical, Audio, Electrical)", height=250)

    elif mode == "Oil Change":
        entry["Oil_M"] = st.text_input("Engine Oil Grade", placeholder="e.g. 5W-30")
        if active_cat == "Motorcycle":
            c_p, c_t = st.columns(2)
            with c_p: entry["Oil_P"] = st.text_input("Primary Oil")
            with c_t: entry["Oil_T"] = st.text_input("Trans Oil")
        entry["Notes"] = st.text_input("Filter Brand/Part #")

    elif mode == "Tires":
        if active_cat == "Motorcycle":
            ca, cb = st.columns(2)
            with ca: entry["F_Tire"] = st.text_input("Front Size")
            with cb: entry["R_Tire"] = st.text_input("Rear Size")
            entry["Notes"] = st.text_input("PSI Settings")
        else:
            ca, cb = st.columns(2)
            with ca:
                entry["F_Tire"] = st.text_input("F-Size")
                f_p = st.text_input("F-PSI")
            with cb:
                entry["R_Tire"] = st.text_input("R-Size")
                r_p = st.text_input("R-PSI")
            tq = st.text_input("Lug Nut Torque")
            entry["Notes"] = f"PSI: {f_p}/{r_p} | Torque: {tq}"

    elif mode == "Bulbs":
        if active_cat == "Motorcycle":
            entry["Bulbs"]
