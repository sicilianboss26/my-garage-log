import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. SETUP & CUSTOM THEME ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 15px; background-color: #262730;
        padding: 40px; text-align: center; margin-top: 50px;
    }
    .shop-title { color: #ff4b4b; font-size: 28px; font-weight: 900; text-transform: uppercase; margin: 0; }
    div[data-baseweb="input"] { background-color: #1a1c1e !important; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE LOGIN TERMINAL (FIXED) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        
        # Using a stable key to ensure the PIN box works every time
        current_pin = st.text_input("Enter Shop PIN", type="password", key="main_login_pin")
        
        if st.button("Unlock Terminal"):
            if current_pin == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA PERSISTENCE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("###
