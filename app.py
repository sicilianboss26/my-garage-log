import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub Pro v8.1", page_icon="🔧", layout="wide")

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
    section[data-testid="stSidebar"] { background-color: #1c1f26; border-right: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE & USER LOGIC ---
LOG, FLEET, USERS = "maintenance_log.csv", "fleet_database.csv", "users.csv"
COLS = ["User", "Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

if not os.path.exists(USERS):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS, index=False)

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_and_fix(file_path, default_cols):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=default_cols).to_csv(file_path, index=False)
    df = pd.read_csv(file_path)
    if 'User' not in df.columns:
        df.insert(0, 'User', st.session_state.user)
        df.to_csv(file_path, index=False)
    return df

# --- 3. LOGIN SYSTEM ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card"><div class="shop-title">Garage Hub</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Access Garage"):
                user_df = pd.read_csv(USERS)
                if not user_df[(user_df['username'] == u) & (user_df['password'] == hash_pass(p))].empty:
                    st.session_state.auth, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Invalid Login")
        with tab2:
            nu, np = st.text_input("New User"), st.text_input("New Pass", type="password")
            if st.button("Create Account"):
                ud = pd.read_csv(USERS)
                if nu not in ud['username'].values:
