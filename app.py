import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fleet Command Pro", page_icon="🛡️", layout="wide")

# --- SECURITY ---
PASSWORD = "1234" 
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_database.csv"

with st.sidebar:
    st.title("🔐 Secure Access")
    user_pwd = st.text_input("Access Code", type="password")
    if user_pwd != PASSWORD:
        st.stop()
    st.divider()

# --- DATA HANDLING ---
if not os.path.exists(FLEET_FILE):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET_FILE, index=False)
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Date", "Unit", "Type", "Reference", "Oil_Grade", "Oil_Qty", "Tire_Size", "Notes"]).to_csv(LOG_FILE, index=False)

def get_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

# --- SIDEBAR ---
fleet_df = get_data(FLEET_FILE)
if not fleet_df.empty:
    fleet_df["Display"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    fleet_list = fleet_df["Display"].tolist()
else:
    fleet_list = []

st.sidebar.subheader("🚛 Fleet Inventory")
active_unit = st.sidebar.selectbox("Select Unit", fleet_list) if fleet_list else None

with st.sidebar.expander("➕ Register New Unit"):
    v_year = st.selectbox("Year", list(range(2026, 1980, -1)))
    v_make = st.text_input("Make")
    v_model = st.text_input("Model")
    v_cat = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Add to Fleet"):
        if v_make and v_model:
            new_row = pd.DataFrame([{"Year": v_year, "Make": v_make, "Model": v_model, "Category": v_cat}])
            save_data(pd.concat([get_data(FLEET_FILE), new_row], ignore_index=True), FLEET_FILE)
            st.rerun()

# --- MAIN DASHBOARD ---
st.title("🛡️ Fleet Command Center")

if not active_unit:
    st.info("👈 Open the sidebar to register a vehicle.")
    st.stop()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📝 New Service Entry")
    with st.container(border=True):
        l_type = st.selectbox("Activity", ["Oil Change", "Tire Service", "DTC/Diagnostic", "Repair", "Modification", "Inspection"])
        
        oil_grade, oil_qty, tire_size = "", "", ""
        ref_label = "Reference (Part # or Code)"
        
        # --- DYNAMIC UI LOGIC ---
        if l_type == "Oil Change":
            ref_label = "Oil Filter Part #"
            c1, c2 = st.columns(2)
            oil_grade = c1.text_input("Oil Grade (e.g. 5W-30)")
            oil_qty = c2.text_input("Capacity (Liters)")
            
        elif l_type == "Tire Service":
            # REMOVED BRAND - Just the Dimensions
            st.write("**Enter Tire Dimensions**")
            t1, t2, t3 = st.columns(3)
            tw = t1.text_input("Width (225)")
            ta = t2.text_input("Ratio (65)")
            tr = t3.text_input("Rim (17)")
            if tw and ta and tr:
                tire_size = f"{tw}/{ta}/R{tr}"
            ref_label = None # Hides the Brand/Reference box for tires
        
        # Only show the reference box if it's not a Tire Service
        l_ref = st.text_input(ref_label) if ref_label else ""
        
        l_notes = st.text_area("Service Notes")
        
        if st.button("Save Entry"):
            new_entry = pd.DataFrame([[
                datetime.now().strftime("%Y-%m-%d"), 
                active_unit, l_type, l_ref, oil_grade, oil_qty, tire_size, l_notes
            ]], columns=["Date", "Unit", "Type", "Reference", "Oil_Grade", "Oil_Qty", "Tire_Size", "Notes"])
            
            save_data(pd.concat([get_data(LOG_FILE), new_entry], ignore_index=True), LOG_FILE)
            st.toast("Service Logged.")
            st.rerun()

with col2:
    st.subheader("📊 Service History")
    hist = get_data(LOG_FILE)
    active_hist = hist[hist["Unit"] == active_unit] if not hist.empty else pd.DataFrame()
    if not active_hist.empty:
        st.dataframe(active_hist.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No logs found.")
