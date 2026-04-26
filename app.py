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
    .stTextInput>div>div>input { background-color: #1c1f26 !important; color: #00ff00 !important; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
LOG, FLEET, USERS = "maintenance_log.csv", "fleet_database.csv", "users.csv"
COLS = ["User", "Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

# Ensure files exist
if not os.path.exists(USERS):
    pd.DataFrame(columns=["username", "password"]).to_csv(USERS, index=False)

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. LOGIN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Garage Hub</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Access Garage"):
                user_df = pd.read_csv(USERS)
                if not user_df[(user_df['username'] == u) & (user_df['password'] == hash_pass(p))].empty:
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Invalid Login")
        with tab2:
            nu, np = st.text_input("New User"), st.text_input("New Pass", type="password")
            if st.button("Create"):
                ud = pd.read_csv(USERS)
                if nu not in ud['username'].values:
                    pd.concat([ud, pd.DataFrame([{"username": nu, "password": hash_pass(np)}])]).to_csv(USERS, index=False)
                    st.success("Created!")
    st.stop()

# --- 4. DATA FIXER (Prevents the KeyError) ---
# This checks if the 'User' column exists; if not, it adds it.
def load_and_fix(file_path, default_cols):
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=default_cols)
    df = pd.read_csv(file_path)
    if 'User' not in df.columns:
        df.insert(0, 'User', st.session_state.user) # Claim existing data for the logged-in user
        df.to_csv(file_path, index=False)
    return df

full_fleet = load_and_fix(FLEET, ["User", "Year", "Make", "Model", "Cat"])
full_log = load_and_fix(LOG, COLS)

# Filter for current user
user_fleet = full_fleet[full_fleet['User'] == st.session_state.user]

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"👤 {st.session_state.user.upper()}")
    if st.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    
    active_v = None
    if not user_fleet.empty:
        user_fleet["Name"] = user_fleet["Year"].astype(str) + " " + user_fleet["Make"] + " " + user_fleet["Model"]
        active_v = st.selectbox("YOUR VEHICLES", user_fleet["Name"].tolist())

    with st.expander("Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma, mo = st.text_input("Make"), st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save"):
            new_v = pd.DataFrame([{"User": st.session_state.user, "Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([full_fleet, new_v]).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. MAIN ---
st.title("📟 ANTONINO'S GARAGE HUB")
if not active_v:
    st.info("Garage empty. Add a vehicle in the sidebar.")
    st.stop()

st.markdown(f'<div class="working-on">ACTIVE: {active_v.upper()}</div>', unsafe_allow_html=True)
# Standard record saving logic follows...
if st.button("💾 SAVE RECORD"):
    # (Entry creation and saving here)
    st.success("Saved!")
