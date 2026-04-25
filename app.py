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
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 8px; height: 3em; }
    h1, h2, h3, h4 { color: #ff4b4b !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE LOCK ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="login-card"><div class="shop-title">Antonino\'s Garage Hub</div>', unsafe_allow_html=True)
        pin = st.text_input("Enter PIN", type="password")
        if st.button("Unlock Terminal"):
            if pin == "1234": st.session_state.auth = True; st.rerun()
            else: st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA ARCHITECTURE ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Unit", "Type", "KM_In", "KM_Out", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs"]

if not os.path.exists(LOG): pd.DataFrame(columns=COLS).to_csv(LOG, index=False)
if not os.path.exists(FLEET): pd.DataFrame(columns=["Year", "Make", "Model", "Cat"]).to_csv(FLEET, index=False)

# Auto-fix for KM columns
df_check = pd.read_csv(LOG)
needs_save = False
for col in ["KM_In", "KM_Out"]:
    if col not in df_check.columns:
        df_check[col] = 0
        needs_save = True
if needs_save: df_check.to_csv(LOG, index=False)

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

# --- 5. WORKSPACE ---
st.title("⚙️ Garage Hub Terminal")
if not active_v: st.info("👈 Select a vehicle to start."); st.stop()

col1, col2 = st.columns([1.4, 2], gap="large")

with col1:
    st.markdown(f"#### 🛠️ Service Entry: {active_v}")
    mode = st.selectbox("Category", ["Repair", "Oil Change", "Tires", "Bulbs"])
    
    st.markdown("##### 📏 Mileage Tracking")
    km_c1, km_c2 = st.columns(2)
    with km_c1: km_in = st.number_input("KM In", min_value=0, step=1)
    with km_c2: km_out = st.number_input("KM Out", min_value=0, step=1)
    
    st.divider()
    entry = {k: "" for k in COLS}

    if mode == "Repair":
        entry["Notes"] = st.text_area("Repair Details", placeholder="Work performed...", height=150)
    elif mode == "Oil Change":
        o_c1, o_c2 = st.columns([2,1])
        with o_c1: entry["Oil_M"] = st.text_input("Grade (5W-30)")
        with o_c2: qty = st.text_input("Liters")
        o_type = st.selectbox("Type", ["Full Synthetic", "Synthetic Blend", "Mineral"])
        filt = st.text_input("Filter #")
        entry["Notes"] = f"Type: {o_type} | Qty: {qty}L | Filt: {filt}"
    elif mode == "Tires":
        t_c1, t_c2 = st.columns(2)
        with t_c1: entry["F_Tire"] = st.text_input("F-Size"); f_p = st.text_input("F-PSI")
        with t_c2: entry["R_Tire"] = st.text_input("R-Size"); r_p = st.text_input("R-PSI")
        tq = st.text_input("Torque (lb-ft)")
        entry["Notes"] = f"PSI: {f_p}/{r_p} | TQ: {tq}"
    elif mode == "Bulbs":
        b1, b2 = st.columns([2,1])
        with b1: entry["Bulbs"] = st.selectbox("Loc", ["Low Beam", "High Beam", "Fog", "Signal"])
        with b2: b_code = st.text_input("Code")
        entry["Notes"] = f"Code: {b_code}"

    if st.button(f"💾 COMMIT TO LOG"):
        new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_v, mode, km_in, km_out, entry["Notes"], entry["Oil_M"], "", "", entry["F_Tire"], entry["R_Tire"], entry["Bulbs"]]], columns=COLS)
        pd.concat([pd.read_csv(LOG), new_row]).to_csv(LOG, index=False)
        st.success("Entry Saved"); st.rerun()

with col2:
    tab_view, tab_edit = st.tabs(["📊 History", "✏️ Edit Records"])
    with tab_view:
        h_df = pd.read_csv(LOG)
        if not h_df.empty:
            st.dataframe(h_df[h_df["Unit"] == active_v].sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    with tab_edit:
        full_df = pd.read_csv(LOG)
        if not full_df.empty:
            edit_df = full_df[full_df["Unit"] == active_v].tail(10)
            for i, row in edit_df.iterrows():
                with st.expander(f"Edit: {row['Date']} - {row['Type']}"):
                    n_note = st.text_area("Notes", value=row['Notes'], key=f"n_{i}")
                    c1, c2 = st.columns(2)
                    with c1: n_in = st.number_input("KM In", value=int(row['KM_In']), key=f"i_{i}")
                    with c2: n_out = st.number_input("KM Out", value=int(row['KM_Out']), key=f"o_{i}")
                    if st.button("✅ Update", key=f"u_{i}"):
                        full_df.at[i, 'Notes'], full_df.at[i, 'KM_In'], full_df.at[i, 'KM_Out'] = n_note, n_in, n_out
                        full_df.to_csv(LOG, index=False); st.rerun()
                    if st.button("🔥 Delete", key=f"d_{i}"):
                        full_df.drop(i).to_csv(LOG, index=False); st.rerun()
