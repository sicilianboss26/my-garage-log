import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# --- 1. CONFIG & DEFAULTS ---
ACCESS_PIN = "1234"
IMG = "garage_images"
LOG = "garage_log.csv"
COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_Service", "Notes", "Photo", "Oil_G", "Oil_F", "Primary", "Trans", "Battery", "F_Tire", "R_Tire", "L_Brake", "H_Brake"]

# --- 2. AUTHENTICATION CHECK ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Garage Hub 🛠️")
    pin_input = st.text_input("Enter Access PIN", type="password")
    if st.button("Unlock System"):
        if pin_input == ACCESS_PIN:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# --- 3. DATA HELPERS ---
def get_df(file):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=COLS)

def save_df(df, file):
    df.to_csv(file, index=False)

# --- 4. SIDEBAR (This defines 'active_unit') ---
with st.sidebar:
    st.title("Garage Hub")
    fleet = ["2012 GMC Terrain", "2018 Hyundai Kona", "2020 Street Bob"]
    active_unit = st.selectbox("Select Vehicle", fleet)
    st.divider()
    st.info(f"Active: {active_unit}")

# --- 5. YOUR ORIGINAL CODE (Restored & Connected) ---
c1, c2 = st.columns([1, 2])

with c1:
    st.write(f"### {active_unit} Management")
    st.write("📑 **Legal/Papers**")
    
    doc = st.selectbox("Doc Type", ["Insurance", "Registration", "Safety"])
    l_t = "Legal" # Placeholder for your Type column
    l_cost = 0.0 # Placeholder for Cost
    l_km = 0 # Placeholder for KM
    nxt = "" # Placeholder for Next Service
    
    extra_n = st.text_area("Notes", placeholder="Specific details...", key=f"notes_{active_unit}")
    l_notes = f"{doc} Update | {extra_n}" if extra_n else f"{doc} Update"
    
    gal = st.file_uploader("Photo/Receipt", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")
    
    if st.button("💾 Save Entry"):
        p_p = ""
        if gal:
            if not os.path.exists(IMG): os.makedirs(IMG)
            p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            Image.open(gal).save(p_p)
        
        # Mapping your variables to the data structure
        new_row = pd.DataFrame([[
            datetime.now().strftime("%Y-%m-%d"), active_unit, l_t, 0, 0, "", l_notes, p
