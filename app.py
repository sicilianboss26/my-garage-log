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
# Added 'User' column to track ownership
COLS = ["User", "Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

for file, columns in [(LOG, COLS), (FLEET, ["User", "Year", "Make", "Model", "Cat"]), (USERS, ["username", "password"])]:
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. MULTI-USER LOGIN SYSTEM ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Garage Hub Login</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Access Garage"):
                user_df = pd.read_csv(USERS)
                hashed = hash_pass(p)
                if not user_df[(user_df['username'] == u) & (user_df['password'] == hashed)].empty:
                    st.session_state.auth = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
        
        with tab2:
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type="password")
            if st.button("Register"):
                user_df = pd.read_csv(USERS)
                if new_u in user_df['username'].values:
                    st.error("Username already exists")
                else:
                    new_rec = pd.DataFrame([{"username": new_u, "password": hash_pass(new_p)}])
                    pd.concat([user_df, new_rec], ignore_index=True).to_csv(USERS, index=False)
                    st.success("Account Created! Use Login tab.")
    st.stop()

# --- 4. DATA FILTERING (USER SPECIFIC) ---
# Only load data belonging to the logged-in user
current_user = st.session_state.user
full_fleet = pd.read_csv(FLEET)
user_fleet = full_fleet[full_fleet['User'] == current_user]

# --- 5. SIDEBAR (OWNED VEHICLES) ---
with st.sidebar:
    st.markdown(f"### 👤 USER: {current_user.upper()}")
    if st.button("Log Out"):
        st.session_state.auth = False
        st.session_state.user = None
        st.rerun()
    st.divider()
    
    active_v, active_cat = None, "Car/SUV"
    if not user_fleet.empty:
        user_fleet["Name"] = user_fleet["Year"].astype(str) + " " + user_fleet["Make"] + " " + user_fleet["Model"]
        active_v = st.selectbox("YOUR VEHICLES", user_fleet["Name"].tolist())
        if active_v:
            active_cat = user_fleet[user_fleet["Name"] == active_v]["Cat"].values[0]

    with st.expander("Add New Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save to My Garage"):
            new_v = pd.DataFrame([{"User": current_user, "Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([full_fleet, new_v], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. MAIN INTERFACE ---
st.title("📟 ANTONINO'S MULTI-USER HUB")
if not active_v:
    st.info("Garage empty. Add a vehicle in the sidebar.")
    st.stop()

st.markdown(f'<div class="working-on">ACTIVE: {active_v.upper()}</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    mode = st.selectbox("CATEGORY", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("ODOMETER (KM)") if mode not in ["Bulbs", "Legal File"] else ""
    st.divider()

    # Pre-fill entry with owner info
    entry = {k: "" for k in COLS}
    entry["User"] = current_user
    entry["Date"] = datetime.now().strftime("%Y-%m-%d")
    entry["Vehicle"] = active_v
    entry["Type"] = mode
    entry["KM"] = km

    # (Logic for Oil Change / Tires / Repairs remains same, just ensure it writes to the entry dict)
    if mode == "Oil Change" and active_cat == "Motorcycle":
        st.markdown("### Triple-Oil Service")
        e_lit = st.text_input("E-Liters")
        p_lit = st.text_input("P-Liters")
        t_lit = st.text_input("T-Liters")
        entry["Oil_M"], entry["Oil_P"], entry["Oil_T"] = f"{e_lit}L", f"{p_lit}L", f"{t_lit}L"

    if st.button("💾 SAVE TO CLOUD"):
        pd.concat([pd.read_csv(LOG), pd.DataFrame([entry])], ignore_index=True).to_csv(LOG, index=False)
        st.success("Saved!")
        st.rerun()

with col2:
    st.subheader("📋 YOUR MAINTENANCE HISTORY")
    full_log = pd.read_csv(LOG)
    # Filter log so users only see their own records for the active vehicle
    user_log = full_log[(full_log["User"] == current_user) & (full_log["Vehicle"] == active_v)]
    st.dataframe(user_log.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
