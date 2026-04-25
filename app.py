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

# ADDED: REMOVE VEHICLE SECTION
with st.sidebar.expander("🗑️ Remove a Vehicle"):
    if not fleet_df.empty:
        to_remove = st.selectbox("Vehicle to Delete", fleet_df["D"].tolist())
        if st.button("Confirm Delete"):
            # Cleanly remove from fleet CSV
            updated_fleet = fleet_df[fleet_df["D"] != to_remove].drop(columns=['D'])
            save_df(updated_fleet, FLEET)
            # Also clean up the log of that vehicle? (Optional - here we just remove from fleet)
            st.success(f"Removed {to_remove}")
            st.rerun()
    else:
        st.write("No vehicles to remove.")

with st.sidebar.expander("➕ Add New Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma, vmo = st.text_input("Make"), st.text_input("Model")
    vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle") and vma and vmo:
        new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
        save_df(pd.concat([get_df(FLEET), new_v]), FLEET)
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

        # KM Logic: Body and Audio Repairs are KM-free
        l_km = 0
        if l_t not in ["Battery", "Bulbs", "Legal"] and sel_comp not in ["Audio", "Body"]:
            l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        
        o_g, o_f, pri, tra, bat, f_sz, r_sz, l_b, h_b, nxt = "", "", "", "", "", "", "", "", "", 0
        l_cost, l_notes = 0.0, ""

        if l_t == "Repair":
            st.write(f"📋 **{sel_comp} Details**")
            parts_data = pd.DataFrame([{"Part": "", "Price": 0.00}])
            edited_parts = st.data_editor(parts_data, num_rows="dynamic", use_container_width=True, key=f"parts_{active_unit}")
            l_cost = float(edited_parts["Price"].sum())
            st.metric("Final Cost", f"${l_cost:,.2f}")
            l_notes = f"{sel_comp} Repair"

        elif l_t == "Oil Change":
            st.write("🛢️ **Engine Fluid**")
            m1, m2 = st.columns(2)
            o_g, o_f = m1.text_input("Oil Grade/Brand"), m2.text_input("Filter Model #")
            if unit_cat == "Motorcycle":
                st.write("⛓️ **Drivetrain Fluids**")
                m3, m4 = st.columns(2)
                pri, tra = m3.text_input("Primary Oil"), m4.text_input("Transmission Oil")
            l_cost = st.number_input("Total Fluid/Parts Cost", min_value=0.0, step=0.01)
            nxt = l_km + 8000

        elif l_t == "Tire Service":
            st.write("🛞 **Front Tires**")
            tf1, tf2, tf3 = st.columns(3)
            f_sz = f"{tf1.text_input('W', key='fw')}/{tf2.text_input('R', key='fr')}R{tf3.text_input('D', key='fd')}"
            st.write("🛞 **Rear Tires**")
            tr1, tr2, tr3 = st.columns(3)
            r_sz = f"{tr1.text_input('W', key='rw')}/{tr2.text_input('R', key='rr')}R{tr3.text_input('D', key='rd')}"
            l_cost = st.number_input("Service Cost", min_value=0.0, step=0.01)

        elif l_t == "Battery":
            st.write("🔋 **Battery Specs**")
            bc1, bc2, bc3 = st.columns(3)
            brand, group, cca = bc1.text_input("Brand"), bc2.text_input("Group"), bc3.text_input("CCA")
            l_cost = st.number_input("Battery Cost", min_value=0.0, step=0.01)
            bat = f"{brand} | Group: {group} | CCA: {cca}"

        elif l_t == "Bulbs":
            st.write("🔦 **Front Lighting**")
            b_c1, b_c2 = st.columns(2)
            l_b, h_b = b
