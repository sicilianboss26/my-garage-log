import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. TERMINAL SETUP ---
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
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; height: 3.5em; border-radius: 8px; }
    h1, h2, h3, h4 { color: #ff4b4b !important; font-family: 'Courier New', monospace; }
    div[data-baseweb="select"] { border: 1px solid #ff4b4b; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE LOCK ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password", key="gate_pin")
        if st.button("Unlock Terminal"):
            if pin == "1234": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA PERSISTENCE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]

if os.path.exists(FLEET):
    check_df = pd.read_csv(FLEET)
    if "Cat" not in check_df.columns:
        check_df["Cat"] = "Car/SUV"
        check_df.to_csv(FLEET, index=False)

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 Control Panel")
    if st.button("🔒 Lock Terminal"): st.session_state.auth = False; st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("Select Vehicle", f_df["Name"].tolist())
        active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]

        with st.expander("🗑️ Remove Vehicle"):
            if st.button("Confirm Delete"):
                f_df[f_df["Name"] != active_v][["Year", "Make", "Model", "Cat"]].to_csv(FLEET, index=False)
                st.rerun()

    with st.expander("➕ Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma, mo = st.text_input("Make"), st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save to Fleet"):
            new_v = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False); st.rerun()

# --- 5. WORKSPACE ---
st.title("⚙️ Garage Hub Terminal")
if not active_v: st.info("👈 Select a vehicle to start."); st.stop()

col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    st.markdown(f"### 🚘 {active_v}")
    mode = st.selectbox("Select Service Category", ["Repair", "Oil Change", "Tires", "Bulbs"])
    st.divider()
    
    entry = {k: "" for k in COLS}

    if mode == "Repair":
        st.markdown("#### 🔧 System Diagnostics & Repair")
        entry["Notes"] = st.text_area("Work Performed (Mechanical, Audio, Electrical)", height=200)

    elif mode == "Oil Change":
        st.markdown("#### 🛢️ Fluid Service")
        if active_cat == "Motorcycle":
            entry["Oil_M"] = st.text_input("Engine Oil")
            c1, c2 = st.columns(2)
            with c1: entry["Oil_P"] = st.text_input("Primary")
            with c2: entry["Oil_T"] = st.text_input("Transmission")
            entry["Notes"] = st.text_input("Filter/Notes")
        else:
            # Professional Car/Truck Layout
            oil_col1, oil_col2 = st.columns([2, 1])
            with oil_col1:
                entry["Oil_M"] = st.text_input("Oil Grade (e.g. 5W-30 Synthetic)")
            with oil_col2:
                oil_qty = st.text_input("Qty (Liters)")
            
            # New dedicated fields
            st.markdown("##### Service Hardware")
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                filter_num = st.text_input("Filter Model #")
            with h_col2:
                drain_tq = st.text_input("Drain Plug Torque (lb-ft)")
            
            entry["Notes"] = f"Qty: {oil_qty}L | Filter: {filter_num} | Drain TQ: {drain_tq}"

    elif mode == "Tires":
        st.markdown("#### 🛞 Wheel & Tire Specs")
        if active_cat == "Motorcycle":
            ca, cb = st.columns(2)
            with ca: entry["F_Tire"] = st.text_input("Front Size")
            with cb: entry["R_Tire"] = st.text_input("Rear Size")
            entry["Notes"] = st.text_input("PSI / Torque")
        else:
            st.markdown("##### Front Axle")
            f_c1, f_c2 = st.columns(2)
            with f_c1: entry["F_Tire"] = st.text_input("Tire Size (Front)")
            with f_c2: f_psi = st.text_input("PSI (Front)")
            
            st.markdown("##### Rear Axle")
            r_c1, r_c2 = st.columns(2)
            with r_c1: entry["R_Tire"] = st.text_input("Tire Size (Rear)")
            with r_c2: r_psi = st.text_input("PSI (Rear)")
            
            st.divider()
            tq = st.text_input("Lug Nut Torque Spec (lb-ft)")
            entry["Notes"] = f"PSI: {f_p if 'f_p' in locals() else f_psi}/{r_p if 'r_p' in locals() else r_psi} | Torque: {tq}"

    elif mode == "Bulbs":
        st.markdown("#### 💡 Lighting Specs")
        b_c1, b_c2 = st.columns([2, 1])
        with b_c1:
            entry["Bulbs"] = st.selectbox("Bulb Location", ["H11 Low Beam", "9005 High Beam", "Fog Light", "Interior LED", "License Plate"])
        with b_c2:
            b_code = st.text_input("Bulb Code")
        entry["Notes"] = st.text_input("Additional Notes")

    st.divider()
    if st.button(f"💾 COMMIT {mode.upper()} TO LOG"):
        row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, entry["Notes"], entry["Oil_M"], entry["Oil_P"], entry["Oil_T"], entry["F_Tire"], entry["R_Tire"], entry["Bulbs"]]], columns=COLS)
        pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False)
        st.success(f"Log Updated Successfully")
        st.rerun()

with col2:
    st.subheader("📊 Service History")
    hist_df = pd.read_csv(LOG)
    if not hist_df.empty:
        unit_hist = hist_df[hist_df["Unit"] == active_v].sort_values(by="Date", ascending=False)
        st.dataframe(unit_hist, use_container_width=True, hide_index=True)
