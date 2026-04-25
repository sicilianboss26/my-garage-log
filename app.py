import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub Pro", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 10px; background-color: #1c1f26;
        padding: 50px; text-align: center; margin-top: 100px;
    }
    .shop-title { color: #ff4b4b; font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: 3px; }
    h1, h2, h3 { color: #ff4b4b !important; font-family: 'Segoe UI', sans-serif; text-transform: uppercase; }
    .working-on { color: #00ff00; font-family: 'Courier New', monospace; font-size: 20px; font-weight: bold; margin-bottom: 20px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div { 
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

# --- 2. LOG IN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password")
        if st.button("Log In"):
            if pin == "1234": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied")
    st.stop()

# --- 3. DATABASE INITIALIZATION ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR & VEHICLE LOGIC ---
with st.sidebar:
    st.markdown("### 🛠️ CONTROL")
    if st.button("Log Out"): st.session_state.auth = False; st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        # Create display name for dropdown
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("SELECT VEHICLE", f_df["Name"].tolist())
        
        # Get the category (Motorcycle vs Car) safely
        if active_v:
            active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]
            
        with st.expander("Delete Vehicle"):
            if st.button("Confirm Delete"):
                new_f = f_df[f_df["Name"] != active_v].drop(columns=["Name"])
                new_f.to_csv(FLEET, index=False)
                st.rerun()
    
    with st.expander("Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            new_row = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([pd.read_csv(FLEET), new_row], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 5. MAIN WORKSPACE ---
st.title("📟 ANTONINO'S GARAGE HUB")

if not active_v:
    st.info("👋 Welcome! Use the sidebar to add a vehicle (e.g., GMC Terrain or Harley Bob) to get started.")
    st.stop()

st.markdown(f'<div class="working-on">WORKING ON: {active_v.upper()}</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    mode = st.selectbox("CATEGORY", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("ODOMETER (KM)")
    uploaded_file = st.file_uploader("📷 Attach Photo", type=['png', 'jpg', 'jpeg'])
    photo_name = uploaded_file.name if uploaded_file else "None"
    st.divider()

    # Shared Entry Dictionary
    entry = {k: "" for k in COLS}
    entry["Date"] = datetime.now().strftime("%Y-%m-%d")
    entry["Vehicle"] = active_v
    entry["Type"] = mode
    entry["KM"] = km
    entry["Photo"] = photo_name

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            st.markdown("### 🏍️ Triple-Oil Service")
            c1, c2, c3 = st.columns(3)
            with c1: entry["Oil_M"] = st.text_input("Engine Oil", "20W-50")
            with c2: entry["Oil_P"] = st.text_input("Primary Oil")
            with c3: entry["Oil_T"] = st.text_input("Trans Oil")
            entry["Notes"] = st.text_area("Filter/Drain Plug Notes")
        else:
            o_type = st.selectbox("Oil Type", ["Full Synthetic", "Synthetic Blend", "Conventional"])
            o_grade = st.text_input("Oil Grade")
            o_liters = st.text_input("Liters")
            o_filter = st.text_input("Filter #")
            o_notes = st.text_area("Notes")
            entry["Oil_M"] = f"{o_grade} ({o_type})"
            entry["Notes"] = f"{o_liters}L | Filter: {o_filter} | {o_notes}"

    elif mode == "Tires":
        st.markdown("### Tires & PSI")
        ft1, ft2 = st.columns([2, 1])
        with ft1: f_s = st.text_input("Front Size")
        with ft2: f_p = st.text_input("Front PSI")
        rt1, rt2 = st.columns([2, 1])
        with rt1: r_s = st.text_input("Rear Size")
        with rt2: r_p = st.text_input("Rear PSI")
        entry["F_Tire"], entry["R_Tire"] = f"{f_s} ({f_p} PSI)", f"{r_s} ({r_p} PSI)"
        entry["Notes"] = st.text_area("Service Notes")

    elif mode == "Repair":
        rep_cat = st.selectbox("System Involved", ["Engine", "Transmission", "Electrical/Electronics", "Audio/Custom", "Suspension", "Brakes/ABS", "Exhaust", "Body"])
        entry["Type"] = f"Repair: {rep_cat}"
        entry["Notes"] = st.text_area("Work Details")

    elif mode == "Diagnostic":
        st.markdown("### ⚡ Diagnostic Scan")
        d1, d2 = st.columns(2)
        with d1: dtc = st.text_input("DTC"); abs_c = st.text_input("ABS")
        with d2: srs = st.text_input("SRS"); oth = st.text_input("Body")
        entry["Notes"] = f"DTC:{dtc} | SRS:{srs} | ABS:{abs_c} | Body:{oth} | {st.text_area('Live Data')}"

    elif mode == "Bulbs":
        st.markdown("### 💡 Lighting")
        b_l = st.selectbox("Location", ["Low/High Beam", "Fog", "Turn/Marker", "License Plate", "Tail/Brake", "Reverse", "Interior", "Side Marker/Custom"])
        entry["Type"] = f"Lighting: {b_l}"
        entry["Bulbs"] = st.text_input("Bulb Spec")
        entry["Notes"] = st.text_area("Replacement Notes")

    if st.button("💾 SAVE RECORD"):
        pd.concat([pd.read_csv(LOG), pd.DataFrame([entry])], ignore_index=True).to_csv(LOG, index=False)
        st.rerun()

with col2:
    st.subheader("📋 HISTORY")
    h_df = pd.read_csv(LOG)
    if not h_df.empty:
        v_h = h_df[h_df["Vehicle"] == active_v].sort_values(by="Date", ascending=False)
        st.dataframe(v_h, use_container_width=True, hide_index=True)
        st.divider()
        with st.expander("📝 Edit History"):
            if not v_h.empty:
                sel = st.selectbox("Delete which record?", v_h.index, format_func=lambda x: f"{v_h.loc[x,'Date']} - {v_h.loc[x,'Type']}")
                if st.button("PURGE RECORD"):
                    h_df.drop(sel).to_csv(LOG, index=False); st.rerun()
