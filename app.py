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
    
    /* Unified Terminal Card */
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
    .stButton>button:hover { background-color: #ff3333 !important; color: white !important; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-title" style="font-size: 36px;">Garage Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">SECURE SYSTEM ENTRY | V3.8</div>', unsafe_allow_html=True)
        
        input_pin = st.text_input("Enter Shop PIN", type="password", placeholder="****")
        
        if st.button("Unlock Terminal"):
            if input_pin == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA & STORAGE ---
LOG, FLEET, STL_DIR = "maintenance_log.csv", "fleet_database.csv", "stl_library"
COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_KM", "Notes", "STL_File", "Oil_G", "Oil_F", "Primary_Oil", "Trans_Oil", "Batt", "F_Tire", "R_Tire", "Low_B", "High_B"]

# Initialize folders/files
if not os.path.exists(STL_DIR): os.makedirs(STL_DIR)
if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 Shop Control")
    if st.button("🔒 Lock App"):
        st.session_state.authenticated = False
        st.rerun()
    st.divider()
    
    fleet_df = pd.read_csv(FLEET)
    active_unit = None
    
    if not fleet_df.empty:
        fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
        active_unit = st.selectbox("Select Active Vehicle", fleet_df["D"].tolist())

        with st.expander("🗑️ Remove a Vehicle"):
            to_remove = st.selectbox("Vehicle to Delete", fleet_df["D"].tolist(), key="del_box")
            if st.button("Confirm Delete", type="primary"):
                updated = fleet_df[fleet_df["D"] != to_remove].drop(columns=['D'])
                updated.to_csv(FLEET, index=False)
                st.success(f"Removed {to_remove}")
                st.rerun()

    with st.expander("➕ Add New Vehicle"):
        vy = st.selectbox("Year", range(2027, 1980, -1))
        vma = st.text_input("Make")
        vmo = st.text_input("Model")
        vct = st.radio("Category", ["Car/SUV", "Truck", "Motorcycle", "E-Bike"]) 
        if st.button("Save Vehicle"):
            if vma and vmo:
                new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
                pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False)
                st.rerun()

# --- 5. DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Select a vehicle to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.subheader(f"⚙️ Active: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", [
            "Repair (Mechanical/Audio)", "Oil Change", "Diagnostic", 
            "Battery Service", "Tire Service", "3D Printed Part", "Legal"
        ])
        
        entry_details = {"stl_name": "None"}
        
        if l_t == "3D Printed Part":
            entry_details['part'] = st.text_input("Part Name")
            entry_details['mat'] = st.selectbox("Material", ["ASA", "Carbon Fiber", "PETG", "PLA"])
            # The STL File Uploader
            uploaded_file = st.file_uploader("Attach STL File", type=['stl'])
            if uploaded_file:
                entry_details['stl_name'] = uploaded_file.name
                with open(os.path.join(STL_DIR, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            entry_details['notes'] = st.text_area("Print Notes")
        
        elif l_t == "Legal":
            entry_details['doc'] = st.selectbox("Type", ["Insurance", "Registration", "License"])
            entry_details['notes'] = st.text_area("Notes")
        else:
            entry_details['notes'] = st.text_area("Work Details (Repairs, Wiring, etc.)")

        # Fixed the cut-off button logic here
        if st.button("💾 Save Entry"):
            final_note = f"{entry_details.get('part', '')} [{entry_details.get('mat', '')}] {entry_details.get('notes', '')}".strip()
            
            new_row = pd.DataFrame([[
                datetime.now().strftime("%Y-%m-%d"), 
                active_unit, l_t, 0, 0, 0, 
                final_note, entry_details['stl_name'], 
                "", "", "", "", "", "", "", "", ""
            ]], columns=COLS)
            
            pd.concat([pd.read_csv(LOG), new_row]).to_csv(LOG, index=False)
            st.success("Log & STL Saved!")
            st.rerun()

with c2:
    st.subheader("📊 Service History")
    hist = pd.read_csv(LOG)
    if not hist.empty:
        st.dataframe(hist[hist["Unit"] == active_unit], use_container_width=True, hide_index=True)
