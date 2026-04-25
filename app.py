import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# --- 1. CONFIG ---
ACCESS_PIN = "1234"
IMG = "garage_images"
LOG = "garage_log.csv"
COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_Service", "Notes", "Photo", "Oil_G", "Oil_F", "Primary", "Trans", "Battery", "F_Tire", "R_Tire", "L_Brake", "H_Brake"]

# --- 2. AUTHENTICATION ---
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

# --- 4. SIDEBAR & VEHICLE SELECTION ---
with st.sidebar:
    st.title("Garage Hub")
    fleet = ["2012 GMC Terrain", "2018 Hyundai Kona", "2020 Street Bob"]
    active_unit
