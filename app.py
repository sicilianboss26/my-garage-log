import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fleet Command Pro", page_icon="🛡️", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #007bff; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SECURITY ---
PASSWORD = "thisisatest2626" 
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_database.csv"

with st.sidebar:
    st.title("🔐 Secure Access")
    user_pwd = st.text_input("Access Code", type="password")
    if user_pwd != PASSWORD:
        st.info("Awaiting authorization...")
        st.stop()
    st.divider()

# --- DATA INITIALIZATION ---
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Date", "Unit", "Type", "Reference", "Notes"]).to_csv(LOG_FILE, index=False)

if not os.path.exists(FLEET_FILE):
    # Starting with a clean, structured database
    initial_data = [
        {"Year": 2012, "Make": "GMC", "Model": "Terrain", "Category": "Car"},
        {"Year": 2018, "Make": "Hyundai", "Model": "Kona", "Category": "Car"},
        {"Year": 2020, "Make": "Harley-Davidson", "Model": "Street Bob", "Category": "Motorcycle"}
    ]
    pd.DataFrame(initial_data).to_csv(FLEET_FILE, index=False)

def get_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

# --- SIDEBAR FLEET MGMT ---
fleet_df = get_data(FLEET_FILE)
# Create a display name for the dropdown: "2012 GMC Terrain"
fleet_df["Display"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
fleet_list = fleet_df["Display"].tolist()

st.sidebar.subheader("🚛 Fleet Inventory")
active_unit = st.sidebar.selectbox("Select Unit", fleet_list)

with st.sidebar.expander("➕ Register New Vehicle"):
    v_cat = st.selectbox("Type", ["Car", "Motorcycle", "Truck/Heavy", "Equipment"])
    v_year = st.number_input("Year", min_value=1900, max_value=2030, value=2024)
    v_make = st.text_input("Make (e.g. GMC, Harley)")
    v_model = st.text_input("Model (e.g. Sonoma, FXBB)")
    
    if st.button("Add to Database"):
        if v_make and v_model:
            new_row = pd.DataFrame([{"Year": v_year, "Make": v_make, "Model": v_model, "Category": v_cat}])
            save_data(pd.concat([get_data(FLEET_FILE), new_row]), FLEET_FILE)
            st.rerun()

with st.sidebar.expander("🗑️ Decommission"):
    to_del = st.selectbox("Select unit to remove", fleet_list)
    if st.button("Delete Permanently"):
        # Filter out the selected unit by matching the components
        current = get_data(FLEET_FILE)
        current["Match"] = current["Year"].astype(str) + " " + current["Make"] + " " + current["Model"]
        updated = current[current["Match"] != to_del].drop(columns=["Match"])
        save_data(updated, FLEET_FILE)
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🛡️ Fleet Command Center")
st.caption(f"System Online | {datetime.now().strftime('%B %d, %Y')}")

# Metrics
history_df = get_data(LOG_FILE)
active_history = history_df[history_df["Unit"] == active_unit]

m1, m2, m3 = st.columns(3)
m1.metric("Selected Unit", active_unit)
m2.metric("Total Logs", len(active_history))
last_date = active_history["Date"].max() if not active_history.empty else "None"
m3.metric("Last Action", last_date)

st.divider()

# Input and Archive
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📝 New Service Entry")
    with st.container(border=True):
        l_type = st.selectbox("Activity", ["Oil Change", "DTC/Diagnostic", "Repair", "Tire Service", "Modification", "Inspection"])
        l_ref = st.text_input("Part # or Fault Code")
        l_notes = st.text_area("Service Notes")
        if st.button("Commit Entry"):
            new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_type, l_ref, l_notes]], 
                                    columns=["Date", "Unit", "Type", "Reference", "Notes"])
            save_data(pd.concat([history_df, new_entry]), LOG_FILE)
            st.toast("Entry logged.")
            st.rerun()

with col2:
    st.subheader("📊 Service History")
    if not active_history.empty:
        st.dataframe(active_history.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for this unit.")

# Quick Ref
st.divider()
specs = {
    "2012 GMC Terrain": "Oil: 5W-30 (5qt) | Socket: 15mm | Filter: PF457G",
    "2018 Hyundai Kona": "Oil: 5W-20 (4.2qt) | Drain Plug: 17mm",
    "2020 Harley-Davidson Street Bob": "Oil: 20W-50 | Primary: 1qt | Transmission: 1qt"
}
if active_unit in specs:
    st.code(f"REFERENCE: {specs[active_unit]}")
