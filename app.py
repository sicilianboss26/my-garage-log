import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Garage Hub", layout="wide")
DATA_FILE = "maintenance_log.csv"

# --- DATA HANDLING ---
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Date", "Vehicle", "Type", "Code/Part", "Notes"])
    df.to_csv(DATA_FILE, index=False)

def save_entry(vehicle, entry_type, detail, notes):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), vehicle, entry_type, detail, notes]], 
                            columns=["Date", "Vehicle", "Type", "Code/Part", "Notes"])
    new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)

# --- UI ---
st.title("🔧 Garage Hub: Diagnostic & Maintenance")

# Sidebar for Vehicle Selection
fleet = ["2012 GMC Terrain", "2018 Hyundai Kona", "2016 Honda HR-V", "2000 GMC Sonoma"]
active_car = st.sidebar.selectbox("Select Vehicle", fleet)

st.header(f"Currently Wrenching: {active_car}")

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("Log New Activity")
    log_type = st.selectbox("Activity Type", ["Check Engine Code", "Oil Change", "Repair", "Part Upgrade"])
    detail = st.text_input("Code or Part Name (e.g. P0300 or Filter #)")
    notes = st.text_area("What's happening? (Symptoms, torque specs, etc.)")
    
    if st.button("Save to Logbook"):
        save_entry(active_car, log_type, detail, notes)
        st.success("Entry Saved!")

with col2:
    st.subheader("Vehicle History")
    try:
        history_df = pd.read_csv(DATA_FILE)
        car_history = history_df[history_df["Vehicle"] == active_car]
        st.dataframe(car_history.sort_values(by="Date", ascending=False), use_container_width=True)
    except:
        st.write("No history found yet.")

# Quick Spec Reference
st.divider()
st.subheader("📋 Quick Reference")
specs = {
    "2012 GMC Terrain": "Oil: 5W-30 (5qt) | Socket: 15mm | Filter: PF457G",
    "2018 Hyundai Kona": "Oil: 5W-20 (4.2qt) | Drain Plug: 17mm",
    "2016 Honda HR-V": "Oil: 0W-20 (3.9qt) | Filter: PL14610",
    "2000 GMC Sonoma": "Check engine variant for specific torque/fluid specs."
}
st.info(specs.get(active_car, "Specs not yet entered for this vehicle."))
