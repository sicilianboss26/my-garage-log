import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP & CUSTOM THEME ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    
    /* Unified Red Terminal Card */
    .login-card {
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        background-color: #262730;
        padding: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        margin-top: 50px;
    }
    .shop-title {
        color: #ff4b4b;
        font-size: 28px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        line-height: 1.2;
    }
    .shop-subtitle {
        color: #888;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    /* Style for Input and Button inside the card */
    div[data-baseweb="input"] { background-color: #1a1c1e !important; border-radius: 8px !important; }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        font-weight: bold;
        height: 3.5em;
        margin-top: 10px;
    }
    .stButton>button:hover { background-color: #ff3333 !important; color: white !important; border: none; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        # All login elements are nested in this div to match the red box layout
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-title" style="font-size: 36px;">Garage Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">SECURE SYSTEM ENTRY | V2.7</div>', unsafe_allow_html=True)
        
        input_pin = st.text_input("Enter Shop PIN", type="password", placeholder="****")
        
        if st.button("Unlock Terminal"):
            if input_pin == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA & DIRECTORIES ---
# FIXED: Completed the string literal for the image folder
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"

if not os.path.exists(IMG): os.makedirs(IMG)
COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_KM", "Notes", "Photo", "Oil_G", "Oil_F", "Primary_Oil", "Trans_Oil", "Batt", "F_Tire", "R_Tire", "Low_B", "High_B"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🔧 Shop Control")
    if st.button("🔒 Lock App"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()
    
    fleet_df = pd.read_csv(FLEET)
    active_unit = None
    if not fleet_df.empty:
        fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
        active_unit = st.selectbox("Select Active Vehicle", fleet_df["D"].tolist())

    with st.sidebar.expander("➕ Add New Vehicle"):
        vy = st.selectbox("Year", range(2027, 1980, -1))
        vma = st.text_input("Make")
        vmo = st.text_input("Model")
        vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            if vma and vmo:
                new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
                pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False)
                st.rerun()

# --- 5. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.subheader(f"⚙️ Working on: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Repair", "Oil Change", "Tire Service", "Battery", "Bulbs", "Legal"])
        
        if l_t == "Legal":
            doc = st.selectbox("Doc Type", ["Insurance", "Registration", "License"]) # License included
            notes = st.text_area("Notes")
        else:
            notes = st.text_area("Notes")

        if st.button("💾 Save Entry"):
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_t, 0, 0, 0, notes, "", "", "", "", "", "", "", "", "", ""]], columns=COLS)
            pd.concat([pd.read_csv(LOG), new_row]).to_csv(LOG, index=False)
            st.success("Entry Logged!")
            st.rerun()

with c2:
    st.subheader("📊 Service History")
    hist = pd.read_csv(LOG)
    if not hist.empty:
        st.dataframe(hist[hist["Unit"] == active_unit], use_container_width=True, hide_index=True)
