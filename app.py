import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub Pro", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 10px; background-color: #1c1f26;
        padding: 50px; text-align: center; margin-top: 50px;
    }
    .shop-title { color: #ff4b4b; font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; }
    .working-on { color: #00ff00; font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold; margin-bottom: 20px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stDateInput>div>div>input { 
        background-color: #1c1f26 !important; color: #00ff00 !important; font-family: 'Courier New', monospace; border: 1px solid #444; 
    }
    .stButton>button { 
        width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; 
        height: 3.5em; border-radius: 5px; border: none; text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #d43f3f; border: 1px solid white; }
    section[data-testid="stSidebar"] { background-color: #1c1f26; border-right: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
LOG, FLEET, USERS = "maintenance_log.csv", "fleet_database.csv", "users.csv"
COLS = ["User", "Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

if not os.path.exists(USERS):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS, index=False)

def hash_pass(password):
    return hashlib.sha256(
