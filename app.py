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
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_and_fix(file_path, default_cols):
    if not os.path.exists(file_path):
        pd.DataFrame(columns=default_cols).to_csv(file_path, index=False)
    df = pd.read_csv(file_path)
    # Patch for legacy data: Add 'User' column if missing and assign to current session user
    if 'User' not in df.columns:
        df.insert(0, 'User', st.session_state.user)
        df.to_csv(file_path, index=False)
    return df

# --- 3. LOGIN ---
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
                    pd.concat([ud, pd.DataFrame([{"username": nu, "password": hash_pass(np)}])]).to_csv(USERS, index=False)
                    st.success("Account Created!")
    st.stop()

# --- 4. DATA LOADING ---
full_fleet = load_and_fix(FLEET, ["User", "Year", "Make", "Model", "Cat"])
full_log = load_and_fix(LOG, COLS)
user_fleet = full_fleet[full_fleet['User'] == st.session_state.user]

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.user.upper()}**")
    if st.button("Log Out"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    active_v, active_cat = None, "Car/SUV"
    if not user_fleet.empty:
        user_fleet["Name"] = user_fleet["Year"].astype(str) + " " + user_fleet["Make"] + " " + user_fleet["Model"]
        active_v = st.selectbox("SELECT VEHICLE", user_fleet["Name"].tolist())
        if active_v:
            active_cat = user_fleet[user_fleet["Name"] == active_v]["Cat"].values[0]

    with st.expander("Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma, mo = st.text_input("Make"), st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            new_v = pd.DataFrame([{"User": st.session_state.user, "Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([full_fleet, new_v]).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. MAIN INTERFACE ---
st.title("📟 ANTONINO'S GARAGE HUB")
if not active_v:
    st.info("Please add a vehicle to begin.")
    st.stop()

st.markdown(f'<div class="working-on">WORKING ON: {active_v.upper()}</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    mode = st.selectbox("CATEGORY", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("ODOMETER (KM)") if mode not in ["Bulbs", "Legal File"] else ""
    st.divider()

    entry = {k: "" for k in COLS}
    entry.update({"User": st.session_state.user, "Date": datetime.now().strftime("%Y-%m-%d"), "Vehicle": active_v, "Type": mode, "KM": km})

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            st.markdown("### Triple-Oil Service")
            c1, c2, c3 = st.columns(3)
            with c1: e_oil, e_lit = st.text_input("Engine Oil", "20W-50"), st.text_input("E-Liters")
            with c2: p_oil, p_lit = st.text_input("Primary Oil"), st.text_input("P-Liters")
            with c3: t_oil, t_lit = st.text_input("Trans Oil"), st.text_input("T-Liters")
            entry.update({"Oil_M": f"{e_oil} ({e_lit}L)", "Oil_P": f"{p_oil} ({p_lit}L)", "Oil_T": f"{t_oil} ({t_lit}L)"})
            entry["Notes"] = st.text_area("Additional Service Notes")
        else:
            o_type = st.selectbox("Oil Type", ["Full Synthetic", "Synthetic Blend", "Conventional"])
            o_gr, o_lt, o_fl = st.text_input("Grade"), st.text_input("Liters"), st.text_input("Filter #")
            entry["Oil_M"] = f"{o_gr} ({o_type})"
            entry["Notes"] = st.text_area(f"{o_lt}L | Filter: {o_fl}")

    elif mode == "Tires":
        st.markdown("### Tire Specs")
        f_s, f_p = st.text_input("Front Size"), st.text_input("Front PSI")
        r_s, r_p = st.text_input("Rear Size"), st.text_input("Rear PSI")
        entry.update({"F_Tire": f"{f_s} ({f_p} PSI)", "R_Tire": f"{r_s} ({r_p} PSI)"})
        entry["Notes"] = st.text_area("Tire Condition/Brand")

    elif mode == "Diagnostic":
        st.markdown("### ⚡ System Scan")
        dtc, abs_c = st
