import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Garage Hub 2.1", layout="wide")
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_list.csv"

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
st.sidebar.title("🚛 Fleet Management")
fleet = get_fleet()
active_car = st.sidebar.selectbox("Select Vehicle", fleet)

st.sidebar.divider()
with st.sidebar.expander("➕ Add New Vehicle"):
    new_vehicle_name = st.text_input("Vehicle Name")
    if st.button("Add to Fleet"):
        if new_vehicle_name:
            add_to_fleet(new_vehicle_name)
            st.rerun()

with st.sidebar.expander("🗑️ Remove a Vehicle"):
    to_delete = st.selectbox("Select vehicle to delete", fleet)
    confirm = st.checkbox(f"Confirm deleting {to_delete}")
    if st.button("Delete Permanently"):
        if confirm:
            remove_from_fleet(to_delete)
            st.rerun()
        else:
            st.warning("Please check the box to confirm.")

# --- MAIN UI ---
st.title("🔧 Garage Hub 2.1")
st.header(f"Currently Wrenching: {active_car}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Log Activity")
    log_type = st.selectbox("Type", ["Check Engine Code", "Oil Change", "Repair", "Part Upgrade", "Inspection"])
    detail = st.text_input("Code/Part #")
    notes = st.text_area("Notes (Specs, symptoms, etc.)")
    
    if st.button("Save Entry"):
        save_log(active_car, log_type, detail, notes)
        st.success(f"Saved for {active_car}!")

with col2:
    st.subheader("History")
    try:
        history = pd.read_csv(LOG_FILE)
        filtered = history[history["Vehicle"] == active_car]
        st.dataframe(filtered.sort_values(by="Date", ascending=False), use_container_width=True)
    except:
        st.write("No logs yet.")

# Quick Specs
st.divider()
specs = {
    "2012 GMC Terrain": "Oil: 5W-30 (5qt) | Socket: 15mm | Filter: PF457G",
    "2018 Hyundai Kona": "Oil: 5W-20 (4.2qt) | Drain Plug: 17mm",
    "2016 Honda HR-V": "Oil: 0W-20 (3.9qt) | Filter: PL14610"
}
if active_car in specs:
    st.info(f"💡 Quick Spec: {specs[active_car]}")
