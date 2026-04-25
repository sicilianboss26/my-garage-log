import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & CUSTOM THEME ---
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
    div[data-baseweb="input"] { background-color: #1a1c1e !important; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        input_pin = st.text_input("Enter Shop PIN", type="password")
        if st.button("Unlock Terminal"):
            if input_pin == "1234": st.session_state.authenticated = True; st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA STORAGE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]
if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 Shop Control")
    if st.button("🔒 Lock App"): st.session_state.authenticated = False; st.rerun()
    st.divider()
    fleet_df = pd.read_csv(FLEET)
    active_unit, active_cat = None, None
    if not fleet_df.empty:
        fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
        active_unit = st.selectbox("Select Vehicle", fleet_df["D"].tolist())
        active_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]
        with st.expander("🗑️ Remove Vehicle"):
            if st.button("Delete Active Unit"):
                pd.read_csv(FLEET)[fleet_df["D"] != active_unit].to_csv(FLEET, index=False)
                st.rerun()
    with st.expander("➕ Add Vehicle"):
        vy, vma, vmo = st.selectbox("Year", range(2027, 1990, -1)), st.text_input("Make"), st.text_input("Model")
        vct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle", "E-Bike"])
        if st.button("Save"):
            new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
            pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False); st.rerun()

# --- 5. DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit: st.info("👈 Add a vehicle to start."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.subheader(f"⚙️ {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Repair", "Oil Change", "Tires", "Bulbs", "3D Printed Part", "Legal"])
        data = {k: "" for k in COLS}
        
        if l_t == "Repair":
            data["Notes"] = st.text_area("Mechanical, Audio, or Electrical details")
        
        elif l_t == "Oil Change":
            data["Oil_M"] = st.text_input("Engine Oil (Grade/Brand)")
            if active_cat == "Motorcycle":
                data["Oil_P"] = st.text_input("Primary Oil")
                data["Oil_T"] = st.text_input("Transmission Oil")
            data["Notes"] = st.text_area("Filter info/Notes")
            
        elif l_t == "Tires":
            if active_cat == "Motorcycle":
                data["F_Tire"] = st.text_input("Front Tire Size/Model")
                data["R_Tire"] = st.text_input("Rear Tire Size/Model")
            else:
                data["Notes"] = st.text_input("Tire Notes (Rotation/Brand)")
                
        elif l_t == "Bulbs":
            if active_cat == "Motorcycle":
                data["Bulbs"] = st.selectbox("Spec", ["H4 Headlight", "1157 Turn Signal", "LED Upgrade"])
            else:
                data["Bulbs"] = st.selectbox("Spec", ["H11 Low Beam", "9005 High Beam", "Fog Light", "License Plate"])
            data["Notes"] = st.text_area("Notes")

        if st.button("💾 Save to File"):
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_t, data["Notes"], data["Oil_M"], data["Oil_P"], data["Oil_T"], data["F_Tire"], data["R_Tire"], data["Bulbs"]]], columns=COLS)
            pd.concat([pd.read_csv(LOG), new_row]).to_csv(LOG, index=False)
            st.success("Entry Logged"); st.rerun()

with c2:
    st.subheader("📊 History")
    hist = pd.read_csv(LOG)
    if not hist.empty:
        st.dataframe(hist[hist["Unit"] == active_unit], use_container_width=True, hide_index=True)
