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
    
    /* The Unified Shop Sign Box */
    .shop-sign-container {
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        background-color: #262730;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .shop-title {
        color: #ff4b4b;
        font-size: 24px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }
    .shop-subtitle {
        color: #888;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 5px;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        # This wrapper ensures EVERYTHING stays inside the red box
        st.markdown('''
            <div class="shop-sign-container">
                <div class="shop-title">Antonino's</div>
                <div class="shop-title" style="font-size: 32px;">Garage Hub</div>
                <div class="shop-subtitle">SECURE SYSTEM ENTRY | V2.3</div>
            </div>
        ''', unsafe_allow_html=True)
        
        input_pin = st.text_input("Enter Shop PIN", type="password", placeholder="****")
        
        if st.button("Unlock Terminal"):
            if input_pin == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# --- 3. DATA & DIRECTORIES ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_KM", "Notes", "Photo", "Oil_G", "Oil_F", "Primary_Oil", "Trans_Oil", "Batt", "F_Tire", "R_Tire", "Low_B", "High_B"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 4. SIDEBAR ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"

with st.sidebar:
    st.title("🔧 Shop Control")
    if st.button("🔒 Lock App"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()
    if not fleet_df.empty:
        fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
        active_unit = st.selectbox("Select Active Vehicle", fleet_df["D"].tolist())
        unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]

    with st.sidebar.expander("➕ Add New Vehicle"):
        vy = st.selectbox("Year", range(2027, 1980, -1))
        vma = st.text_input("Make")
        vmo = st.text_input("Model")
        vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            if vma and vmo:
                new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
                save_df(pd.concat([get_df(FLEET), new_v]), FLEET)
                st.rerun()

# --- 5. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.subheader(f"⚙️ Working on: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Repair", "Oil Change", "Tire Service", "Battery", "Bulbs", "Legal"], key="act_sel")
        
        # Legal Logic Updated to include License
        if l_t == "Legal":
            st.write("📑 **Legal/Papers**")
            doc = st.selectbox("Doc Type", ["Insurance", "Registration", "License"])
            l_notes = f"{doc} Update"
        
        # Repair logic
        elif l_t == "Repair":
            sel_comp = st.selectbox("System", ["Engine", "Transmission", "Suspension", "Brakes", "Electrical", "Body", "Audio"])
            parts_data = pd.DataFrame([{"Part": "", "Price": 0.00}])
            edited_parts = st.data_editor(parts_data, num_rows="dynamic")
            l_cost = float(edited_parts["Price"].sum())
            l_notes = f"{sel_comp} Repair"
            st.metric("Total Cost", f"${l_cost:,.2f}")

        # Standard Fields
        extra_n = st.text_area("Notes")
        if st.button("💾 Save Entry"):
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_t, 0, 0, 0, extra_n, "", "", "", "", "", "", "", "", "", ""]], columns=COLS)
            save_df(pd.concat([get_df(LOG), new_row]), LOG)
            st.success("Entry Saved!")
            st.rerun()

with c2:
    st.subheader("📊 Service History")
    hist = get_df(LOG)
    if not hist.empty:
        st.dataframe(hist[hist["Unit"] == active_unit], use_container_width=True, hide_index=True)
