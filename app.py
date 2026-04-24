import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. ACCESS CONTROL ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

with st.sidebar:
    st.title("🔧 Antonino's Shop")
    user_pin = st.text_input("Enter Pin", type="password", key="main_login")

if user_pin != "1234":
    st.info("Please enter the pin in the sidebar to unlock.")
    st.stop()

# --- 2. CONFIG ---
LOG_FILE = "maintenance_log.csv"
FLEET_FILE = "fleet_database.csv"
IMG_DIR = "service_photos"

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- 3. DATA SETUP ---
if not os.path.exists(FLEET_FILE):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET_FILE, index=False)

if not os.path.exists(LOG_FILE):
    cols = ["Date", "Unit", "Kilometers", "Next_Service_KM", "Type", "Reference", "Oil_Grade", "Oil_Qty", 
            "Oil_Filter", "Air_Filter", "Battery_Size", "Tire_Size", "Tire_Season", "Next_Tire_Date", "Low_Beam", "High_Beam", 
            "Fog_Light", "Blinker_Brake", "Dome_Light", "Insurance_Expiry", "Reg_Expiry", "Photo_Path", "Notes"]
    pd.DataFrame(columns=cols).to_csv(LOG_FILE, index=False)

def get_data(file):
    return pd.read_csv(file)

def save_data(df, file):
    df.to_csv(file, index=False)

# --- 4. VEHICLE SELECTION ---
fleet_df = get_data(FLEET_FILE)
active_unit = None
unit_category = "Car"

if not fleet_df.empty:
    fleet_df["Display"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Vehicle", fleet_df["Display"].tolist())
    unit_category = fleet_df[fleet_df["Display"] == active_unit]["Category"].values[0]

with st.sidebar.expander("➕ Add New Vehicle"):
    v_year = st.selectbox("Year", list(range(2027, 1980, -1)))
    v_make = st.text_input("Make (e.g. GMC, Harley)")
    v_model = st.text_input("Model")
    v_cat = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Add to Garage"):
        if v_make and v_model:
            new_v = pd.DataFrame([{"Year": v_year, "Make": v_make, "Model": v_model, "Category": v_cat}])
            save_data(pd.concat([get_data(FLEET_FILE), new_v], ignore_index=True), FLEET_FILE)
            st.rerun()

# --- 5. DASHBOARD ---
st.title("🛠️ The Garage Hub")

if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to open your shop logs.")
    st.stop()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📝 Log Activity")
    with st.container(border=True):
        l_km = st.number_input("Current Odometer (KM)", min_value=0, step=1)
        l_type = st.selectbox("Activity", ["Oil Change", "Tire Swap", "Lighting/Bulbs", "Battery/Electrical", "Repair/Filters", "Paperwork & Legal", "DTC/Diagnostic"])
        
        # Reset variables for each loop
        o_grade, o_qty, o_filt, a_filt, b_size, t_size, t_season, p_path = "", "", "", "", "", "", "", ""
        low_b, high_b, fog_l, blink_b, dome_l = "", "", "", "", ""
        ins_exp, reg_exp, l_next_km, next_t_date = "", "", 0, ""
        
        if l_type == "Oil Change":
            c1, c2 = st.columns(2)
            o_grade = c1.text_input("Oil Grade")
            o_qty = c2.text_input("Liters")
            o_filt = st.text_input("Oil Filter #")
            l_next_km = st.number_input("Next Service Due (KM)", value=int(l_km + 8000))
        
        elif l_type == "Tire Swap":
            t_season = st.radio("Installed:", ["Winters ❄️", "Summers ☀️"])
            def_d = datetime(2026, 12, 1) if "Summers" in t_season else datetime(2027, 3, 15)
            next_t_date = st.date_input("Next Swap Deadline", value=def_d)
            t_size = st.text_input("Tire Size")

        elif l_type == "Paperwork & Legal":
            ins_exp = st.date_input("Insurance Renewal")
            reg_exp = st.date_input("Plates Renewal")

        elif l_type == "Lighting/Bulbs":
            cl1, cl2 = st.columns(2)
            low_b = cl1.text_input("Low Beam")
            high_b = cl2.text_input("High Beam")
            cl3, cl4 = st.columns(2)
            fog_l = cl3.text_input("Fog Lights")
            blink_b = cl4.text_input("Blinker/Brake")

        l_ref = st.text_input("Part # / Ref")
        l_notes = st.text_area("Notes")
        uploaded_photo = st.camera_input("Take Photo")
        
        if st.button("Commit to Log"):
            if uploaded_photo:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                p_path = f"{IMG_DIR}/{active_unit.replace(' ', '_')}_{ts}.jpg"
                Image.open(uploaded_photo).save(p_path)

            new_row = pd.DataFrame([[
                datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, l_next_km, l_type, l_ref, 
                o_grade, o_qty, o_filt, a_filt, b_size, t_size, t_season, str(next_t_date), 
                low_b, high_b, fog_l, blink_b, dome_l, str(ins_exp), str(reg_exp), p_path, l_notes
            ]], columns=["Date", "Unit", "Kilometers", "Next_Service_KM", "Type", "Reference", "Oil_Grade
