import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP & PIN ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")
with st.sidebar:
    st.title("🔧 Antonino's Shop")
    pin = st.text_input("Enter Pin", type="password")
if pin != "1234":
    st.info("Awaiting pin...")
    st.stop()

# --- 2. DATABASE ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)

if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "KM", "Next_KM", "Type", "Ref", "Oil_G", "Oil_Q", "Oil_F", "Air_F", "Batt", "Tire_S", "Tire_Season", "Tire_Date", "Low_B", "High_B", "Fog", "Blinker", "Dome", "Ins", "Reg", "Photo", "Notes"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. GARAGE ---
fleet_df = get_df(FLEET)
active_unit = None
if not fleet_df.empty:
    fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Vehicle", fleet_df["D"].tolist())

with st.sidebar.expander("➕ Add Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma, vmo = st.text_input("Make"), st.text_input("Model")
    vcat = st.radio("Type", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle"):
        save_df(pd.concat([get_df(FLEET), pd.DataFrame([{"Year":vy,"Make":vma,"Model":vmo,"Category":vcat}])]), FLEET)
        st.rerun()

# --- 4. MAIN DASH ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin.")
    st.stop()

col1, col2 = st.columns([1, 2], gap="large")
with col1:
    st.subheader("📝 New Log")
    with st.container(border=True):
        l_km = st.number_input("Current KM", min_value=0, step=1)
        l_type = st.selectbox("Activity", ["Oil Change", "Tire Swap", "Bulbs", "Battery", "Repair", "Legal"])
        
        # Init vars
        o_g, o_q, o_f, a_f, bat, t_s, t_sea, t_d, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","","","","","","", "", 0
        
        if l_type == "Oil Change":
            o_g, o_q = st.text_input("Oil Grade"), st.text_input("Liters")
            o_f, nxt = st.text_input("Oil Filter #"), l_km + 8000
        elif l_type == "Tire Swap":
            t_sea = st.radio("Installed", ["Winters ❄️", "Summers ☀️"])
            def_d = datetime(2026,12,1) if "Summers" in t_sea else datetime(2027,3,15)
            t_d = st.date_input("Next Deadline", value=def_d)
        elif l_type == "Bulbs":
            l_b, h_b = st.text_input("Low Beam"), st.text_input("High Beam")
            fog, blk = st.text_input("Fogs"), st.text_input("Blinker/Brake")
        elif l_type == "Legal":
            ins, reg = st.date_input("Insurance"), st.date_input("Plates")

        l_ref, l_notes = st.text_input("Part # / Ref"), st.text_area("Notes")
        photo = st.camera_input("Photo")

        if st.button("Save Entry"):
            if photo:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(photo).save(p_p)
            
            new_data = [datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, nxt, l_type, l_ref, o_g, o_q, o_f, a_f, bat, t_s, t_sea, str(t_d), l_b, h_b, fog, blk, dom, str(ins), str(reg), p_p, l_notes]
            save_df(pd.concat([get_df(LOG), pd.DataFrame([new_data], columns=COLS)]), LOG)
            st.rerun()

with col2:
    st.subheader(f"📊 {active_unit} History")
    hist = get_df(LOG)
    if not hist.empty:
        df_show = hist[hist["Unit"] == active_unit].sort_values("KM", ascending=False)
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        if not df_show.empty and pd.notna(df_show.iloc[0]['Photo']):
            if df_show.iloc[0]['Photo'] != "": st.image(df_show.iloc[0]['Photo'])
