import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIG ---
st.set_page_config(page_title="Fleet Command Pro", page_icon="🛡️", layout="wide")
PASSWORD = "yourpassword123" 
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_database.csv"

# --- DATA HANDLING ---
if not os.path.exists(FLEET_FILE):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET_FILE, index=False)
if not os.path.exists(LOG_FILE):
    # Added extra columns for Motorcycle-specific oils
    pd.DataFrame(columns=["Date", "Unit", "Type", "Reference", "Oil_Grade", "Oil_Qty", "Trans_Oil", "Primary_Oil", "Tire_Size", "Notes"]).to_csv(LOG_FILE, index=False)

def get_data(file): return pd.read_csv(file)
def save_data(df, file): df.to_csv(file, index=False)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔐 Access")
    if st.text_input("Code", type="password") != PASSWORD: st.stop()
    st.divider()

fleet_df = get_data(FLEET_FILE)
active_unit = None
unit_category = "Car"

if not fleet_df.empty:
    fleet_df["Display"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Unit", fleet_df["Display"].tolist())
    # Identify if the selected unit is a Motorcycle
    unit_category = fleet_df[fleet_df["Display"] == active_unit]["Category"].values[0]

with st.sidebar.expander("➕ Register New Unit"):
    v_year = st.selectbox("Year", list(range(2026, 1980, -1)))
    v_make = st.text_input("Make")
    v_model = st.text_input("Model")
    v_cat = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Add to Fleet"):
        save_data(pd.concat([get_data(FLEET_FILE), pd.DataFrame([{"Year": v_year, "Make": v_make, "Model": v_model, "Category": v_cat}])], ignore_index=True), FLEET_FILE)
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🛡️ Fleet Command Center")
if not active_unit:
    st.info("👈 Register a vehicle to begin.")
    st.stop()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📝 New Service Entry")
    with st.container(border=True):
        l_type = st.selectbox("Activity", ["Oil Change", "Tire Service", "DTC/Diagnostic", "Repair", "Modification", "Inspection"])
        
        oil_grade, oil_qty, trans_oil, prim_oil, tire_size = "", "", "", "", ""
        ref_label = "Reference (Part # or Code)"
        
        if l_type == "Oil Change":
            ref_label = "Oil Filter Part #"
            st.write("**Engine Oil Specs**")
            c1, c2 = st.columns(2)
            oil_grade = c1.text_input("Motor Oil Grade")
            oil_qty = c2.text_input("Capacity (Liters)")
            
            # SHOW MOTORCYCLE SPECIFIC OILS
            if unit_category == "Motorcycle":
                st.divider()
                st.write("**Drivetrain Oils**")
                c3, c4 = st.columns(2)
                trans_oil = c3.text_input("Transmission Oil")
                prim_oil = c4.text_input("Primary / Gear Oil")
            
        elif l_type == "Tire Service":
            st.write("**Tire Dimensions**")
            t1, t2, t3 = st.columns(3)
            tw, ta, tr = t1.text_input("W"), t2.text_input("A"), t3.text_input("R")
            if tw and ta and tr: tire_size = f"{tw}/{ta}/R{tr}"
            ref_label = None

        l_ref = st.text_input(ref_label) if ref_label else ""
        l_notes = st.text_area("Service Notes")
        
        if st.button("Save Entry"):
            new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_type, l_ref, oil_grade, oil_qty, trans_oil, prim_oil, tire_size, l_notes]], 
                                    columns=["Date", "Unit", "Type", "Reference", "Oil_Grade", "Oil_Qty", "Trans_Oil", "Primary_Oil", "Tire_Size", "Notes"])
            save_data(pd.concat([get_data(LOG_FILE), new_entry], ignore_index=True), LOG_FILE)
            st.rerun()

with col2:
    st.subheader(f"📊 History: {active_unit}")
    hist = get_data(LOG_FILE)
    if not hist.empty:
        st.dataframe(hist[hist["Unit"] == active_unit].sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
