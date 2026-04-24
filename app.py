import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIG & SECURITY ---
st.set_page_config(page_title="The Hub: Private Fleet", layout="wide")
PASSWORD = "thisisatest2626" # <--- SET YOUR REAL PASSWORD HERE
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_list.csv"

# Check password in sidebar
st.sidebar.title("🔐 Access Control")
user_pwd = st.sidebar.text_input("Enter Access Code", type="password")

if user_pwd != PASSWORD:
    st.info("Enter the access code in the sidebar to open the fleet logs.")
    st.stop() 

# --- DATA INITIALIZATION ---
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Date", "Vehicle", "Type", "Code/Part", "Notes"]).to_csv(LOG_FILE, index=False)

if not os.path.exists(FLEET_FILE):
    initial_fleet = pd.DataFrame({"Vehicle": ["2012 GMC Terrain", "2018 Hyundai Kona", "2016 Honda HR-V", "2000 GMC Sonoma"]})
    initial_fleet.to_csv(FLEET_FILE, index=False)

# --- HELPER FUNCTIONS ---
def get_fleet():
    return pd.read_csv(FLEET_FILE)["Vehicle"].tolist()

def add_to_fleet(new_car):
    current_fleet = pd.read_csv(FLEET_FILE)
    if new_car not in current_fleet["Vehicle"].values:
        new_row = pd.DataFrame({"Vehicle": [new_car]})
        pd.concat([current_fleet, new_row]).to_csv(FLEET_FILE, index=False)

def remove_from_fleet(car_to_remove):
    current_fleet = pd.read_csv(FLEET_FILE)
    updated_fleet = current_fleet[current_fleet["Vehicle"] != car_to_remove]
    updated_fleet.to_csv(FLEET_FILE, index=False)

def save_log(vehicle, entry_type, detail, notes):
    new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), vehicle, entry_type, detail, notes]], 
                            columns=["Date", "Vehicle", "Type", "Code/Part", "Notes"])
    new_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)

# --- UI SIDEBAR ---
st.sidebar.divider()
st.sidebar.title("🚛 Fleet Management")
fleet = get_fleet()
active_car = st.sidebar.selectbox("Select Vehicle", fleet)

with st.sidebar.expander("➕ Add New Vehicle"):
    new_v = st.text_input("Vehicle Name")
    if st.button("Add"):
        if new_v:
            add_to_fleet(new_v)
            st.rerun()

with st.sidebar.expander("🗑️ Remove Vehicle"):
    to_delete = st.selectbox("Select to delete", fleet)
    if st.button("Confirm Delete"):
        remove_from_fleet(to_delete)
        st.rerun()

# --- MAIN UI ---
st.title("🔧 The Hub: Private Fleet Manager")
st.header(f"Active Unit: {active_car}")

col1, col2 = st.columns(2)
with col1:
    st.subheader("New Entry")
    log_type = st.selectbox("Action", ["Oil Change", "Diagnostic Code", "Repair", "Tires", "Inspection", "Mod"])
    detail = st.text_input("Part # / Code")
    notes = st.text_area("Details (Torque, symptoms, etc.)")
    if st.button("Save Log"):
        save_log(active_car, log_type, detail, notes)
        st.success("Log Saved.")

with col2:
    st.subheader("History")
    try:
        history = pd.read_csv(LOG_FILE)
        st.dataframe(history[history["Vehicle"] == active_car].sort_values("Date", ascending=False), use_container_width=True)
    except:
        st.write("No logs recorded.")
