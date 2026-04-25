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
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE LOCK (PIN: 1234) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password", key="gate_pin")
        if st.button("Unlock"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATABASE CHECK ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔧 Control Panel")
    if st.button("🔒 Lock"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, None
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("Active Vehicle", f_df["Name"].tolist())
        active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]

    with st.expander("➕ Add Vehicle"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma, mo = st.text_input("Make"), st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            new_v = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([pd.read_csv(FLEET), new_v]).to_csv(FLEET, index=False)
            st.rerun()

# --- 5. WORKSPACE ---
st.title("🛠️ Garage Hub Terminal")
if not active_v:
    st.info("👈 Please add/select a vehicle in the sidebar."); st.stop()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader(f"⚙️ {active_v}")
    with st.container(border=True):
        mode = st.selectbox("Action", ["Tires", "Repair", "Oil Change", "Bulbs"])
        entry = {k: "" for k in COLS}
        
        if mode == "Tires":
            if active_cat == "Motorcycle":
                entry["F_Tire"] = st.text_input("Front Size")
                entry["R_Tire"] = st.text_input("Rear Size")
                entry["Notes"] = st.text_input("PSI / Torque")
            else:
                ca, cb = st.columns(2)
                with ca:
                    entry["F_Tire"] = st.text_input("Front Size")
                    f_psi = st.text_input("Front PSI")
                with cb:
                    entry["R_Tire"] = st.text_input("Rear Size")
                    r_psi = st.text_input("Rear PSI")
                tq = st.text_input("Torque Spec")
                entry["Notes"] = f"PSI: {f_psi}/{r_psi} | Torque: {tq}"
        
        elif mode == "Repair":
            entry["Notes"] = st.text_area("Mechanical, Audio, Electrical details")
        
        elif mode == "Oil Change":
            entry["Oil_M"] = st.text_input("Engine Oil")
            if active_cat == "Motorcycle":
                entry["Oil_P"] = st.text_input("Primary Oil")
                entry["Oil_T"] = st.text_input("Transmission Oil")
            entry["Notes"] = st.text_area("Notes")

        if st.button("💾 Save Record"):
            row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, entry["Notes"], entry["Oil_M"], entry["Oil_P"], entry["Oil_T"], entry["F_Tire"], entry["R_Tire"], ""]], columns=COLS)
            pd.concat([pd.read_csv(LOG), row]).to_csv(LOG, index=False)
            st.success("Saved!")
            st.rerun()

with col2:
    st.subheader("📊 History")
    hist_df = pd.read_csv(LOG)
    if not hist_df.empty:
        st.dataframe(hist_df[hist_df["Unit"] == active_v], use_container_width=True, hide_index=True)
