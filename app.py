import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="Fleet Command Pro", page_icon="🛡️", layout="wide")
PASSWORD = "thisisatest" 
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_database.csv"

# --- DROPDOWN DATA (No Manual Typing) ---
YEARS = list(range(2026, 1995, -1))
MAKES = ["GMC", "Hyundai", "Honda", "Harley-Davidson", "Ford", "Chevrolet", "Toyota", "Ram"]

MODELS = {
    "GMC": ["Terrain", "Sonoma", "Sierra 1500", "Sierra 2500", "Savana"],
    "Hyundai": ["Kona", "Elantra", "Tucson", "Santa Fe"],
    "Honda": ["HR-V", "CR-V", "Civic", "Accord"],
    "Harley-Davidson": ["Street Bob (FXBB)", "Iron 883", "Fat Boy", "Road King", "Heritage Classic"],
    "Ford": ["F-150", "F-550", "Super Duty", "Explorer", "Ranger"],
    "Chevrolet": ["Silverado", "Colorado", "Tahoe", "Equinox"],
    "Toyota": ["Tacoma", "Tundra", "RAV4", "4Runner"],
    "Ram": ["1500", "2500", "3500"]
}

# --- SECURITY ---
with st.sidebar:
    st.title("🔐 Secure Access")
    user_pwd = st.text_input("Access Code", type="password")
    if user_pwd != PASSWORD:
        st.info("Awaiting authorization...")
        st.stop()
    st.divider()

# --- INITIALIZE ---
if not os.path.exists(FLEET_FILE):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET_FILE, index=False)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Date", "Unit", "Type", "Reference", "Notes"]).to_csv(LOG_FILE, index=False)

# --- SIDEBAR REGISTRATION ---
st.sidebar.subheader("🚛 Fleet Inventory")
fleet_df = pd.read_csv(FLEET_FILE)

if not fleet_df.empty:
    fleet_df["Display"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Unit", fleet_df["Display"].tolist())
else:
    active_unit = None

with st.sidebar.expander("➕ Register New Unit"):
    v_year = st.selectbox("Year", YEARS)
    v_make = st.selectbox("Make", MAKES)
    v_model = st.selectbox("Model", MODELS.get(v_make, ["Other"]))
    v_cat = st.radio("Category", ["Car", "Truck", "Motorcycle"]) # Equipment removed
    
    if st.button("Add to Fleet"):
        new_row = pd.DataFrame([{"Year": v_year, "Make": v_make, "Model": v_model, "Category": v_cat}])
        pd.concat([pd.read_csv(FLEET_FILE), new_row], ignore_index=True).to_csv(FLEET_FILE, index=False)
        st.toast(f"{v_model} registered.")
        st.rerun()

if active_unit:
    if st.sidebar.button("🗑️ Delete Selected Unit"):
        updated_fleet = fleet_df[fleet_df["Display"] != active_unit].drop(columns=["Display"])
        updated_fleet.to_csv(FLEET_FILE, index=False)
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🛡️ Fleet Command Center")
st.caption(f"System Online | {datetime.now().strftime('%B %d, %Y')}")

if not active_unit:
    st.info("👈 Use the sidebar to register your first vehicle using the dropdowns.")
    st.stop()

# Layout
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
            pd.concat([pd.read_csv(LOG_FILE), new_entry], ignore_index=True).to_csv(LOG_FILE, index=False)
            st.toast("Entry logged.")
            st.rerun()

with col2:
    st.subheader("📊 Service History")
    history_df = pd.read_csv(LOG_FILE)
    active_history = history_df[history_df["Unit"] == active_unit]
    if not active_history.empty:
        st.dataframe(active_history.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No logs for this unit yet.")
