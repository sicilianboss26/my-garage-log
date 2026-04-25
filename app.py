import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP & CUSTOM THEME ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #111214 !important; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    .stButton>button:hover { background-color: #ff3333; border: none; color: white; }
    div[data-testid="stExpander"] { border: 1px solid #333; border-radius: 8px; background-color: #262730; }
    h1, h2, h3 { color: #ff4b4b !important; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("🔧 Antonino's Shop")
    pin = st.text_input("Access Pin", type="password")
if pin != "1234":
    st.info("Awaiting secure pin..."); st.stop()

# --- 2. DATA ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_KM", "Notes", "Photo", "Oil_G", "Oil_F", "Primary_Oil", "Trans_Oil", "Batt", "F_Tire", "R_Tire", "Low_B", "High_B"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. SIDEBAR / FLEET MANAGEMENT ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"

if not fleet_df.empty:
    fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Active Vehicle", fleet_df["D"].tolist())
    unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]

st.sidebar.markdown("---")

with st.sidebar.expander("➕ Add New Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma, vmo = st.text_input("Make"), st.text_input("Model")
    vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle") and vma and vmo:
        save_df(pd.concat([get_df(FLEET), pd.DataFrame([{"Year":vy,"Make":vma,"Model":vmo,"Category":vct}])]), FLEET)
        st.rerun()

# --- 4. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.subheader(f"⚙️ Working on: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Repair", "Oil Change", "Tire Service", "Battery", "Bulbs", "Legal"], key=f"t_{active_unit}")
        
        sel_comp = "None"
        if l_t == "Repair":
            sel_comp = st.selectbox("System", ["Engine", "Transmission", "Suspension", "Brakes", "Electrical", "Body", "Audio"])

        # KM logic: Hidden for Battery, Bulbs, Legal, Audio, and Body
        l_km = 0
        if l_t not in ["Battery", "Bulbs", "Legal"] and sel_comp not in ["Audio", "Body"]:
            l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        
        o_g, o_f, pri, tra, bat, f_sz, r_sz, l_b, h_b, nxt = "", "", "", "", "", "", "", "", "", 0
        l_cost = 0.0
        l_notes = ""

        if l_t == "Repair":
            st.write(f"📋 **{sel_comp} Details**")
            parts_data = pd.DataFrame([{"Part": "", "Price": 0.00}])
            edited_parts = st.data_editor(parts_data, num_rows="dynamic", use_container_width=True)
            l_cost = float(edited_parts["Price"].sum())
            st.metric("Final Cost", f"${l_cost:,.2f}")
            l_notes = f"{sel_comp} Repair"

        elif l_t == "Oil Change":
            m1, m2 = st.columns(2); o_g, o_f = m1.text_input("Grade"), m2.text_input("Filter #")
            if unit_cat == "Motorcycle":
                m3, m4 = st.columns(2); pri, tra = m3.text_input("Primary"), m4.text_input("Trans")
            l_cost = st.number_input("
