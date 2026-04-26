import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub Pro v8.1", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .shop-title { color: #ff4b4b; font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; text-align: center; margin-bottom: 20px; }
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

# --- 2. DATABASE INITIALIZATION ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

for file, columns in [(LOG, COLS), (FLEET, ["Year", "Make", "Model", "Cat"])]:
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

# --- 3. SIDEBAR: FLEET MANAGEMENT ---
with st.sidebar:
    st.markdown('<div class="shop-title">GARAGE HUB</div>', unsafe_allow_html=True)
    st.divider()
    
    full_fleet = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not full_fleet.empty:
        full_fleet["Name"] = full_fleet["Year"].astype(str) + " " + full_fleet["Make"] + " " + full_fleet["Model"]
        active_v = st.selectbox("SELECT VEHICLE", full_fleet["Name"].tolist())
        if active_v:
            active_cat = full_fleet[full_fleet["Name"] == active_v]["Cat"].values[0]

    with st.expander("➕ ADD NEW VEHICLE"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Category", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("SAVE TO GARAGE"):
            new_v = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([full_fleet, new_v], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 4. MAIN INTERFACE ---
if not active_v:
    st.title("📟 ANTONINO'S SHOP")
    st.info("Garage empty. Add a vehicle in the sidebar to begin.")
    st.stop()

st.markdown(f'<div class="working-on">ACTIVE: {active_v.upper()}</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    mode = st.selectbox("SERVICE CATEGORY", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("ODOMETER (KM)") if mode not in ["Bulbs", "Legal File"] else ""
    st.divider()

    entry = {k: "" for k in COLS}
    entry.update({"Date": datetime.now().strftime("%Y-%m-%d"), "Vehicle": active_v, "Type": mode, "KM": km})

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            st.markdown("### Triple-Oil Service")
            c1, c2, c3 = st.columns(3)
            with c1: 
                e_oil = st.text_input("Engine Oil", "20W-50")
                e_lit = st.text_input("E-Liters")
            with c2: 
                p_oil = st.text_input("Primary Oil")
                p_lit = st.text_input("P-Liters")
            with c3: 
                t_oil = st.text_input("Trans Oil")
                t_lit = st.text_input("T-Liters")
            entry.update({"Oil_M": f"{e_oil} ({e_lit}L)", "Oil_P": f"{p_oil} ({p_lit}L)", "Oil_T": f"{t_oil} ({t_lit}L)"})
            entry["Notes"] = st.text_area("Additional Service Notes")
        else:
            o_type = st.selectbox("Oil Type", ["Full Synthetic", "Synthetic Blend", "Conventional"])
            o_gr = st.text_input("Grade")
            o_lt = st.text_input("Liters")
            o_fl = st.text_input("Filter #")
            entry
