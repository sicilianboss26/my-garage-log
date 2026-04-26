import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; color: #ffffff; }
    .login-card {
        border: 2px solid #ff4b4b; border-radius: 15px; background-color: #1c1f26;
        padding: 60px; text-align: center; margin-top: 50px;
        box-shadow: 0px 0px 30px rgba(255, 75, 75, 0.15);
    }
    .shop-logo { font-size: 54px; font-weight: 900; color: #ff4b4b; margin-bottom: 5px; text-shadow: 3px 3px #000; letter-spacing: 2px; }
    .shop-subtitle { color: #888; font-family: 'Courier New'; font-size: 16px; letter-spacing: 8px; margin-bottom: 35px; text-transform: uppercase; }
    .dash-header { 
        background: linear-gradient(90deg, #1c1f26 0%, #0e1117 100%);
        padding: 25px; border-radius: 10px; border-left: 6px solid #ff4b4b; margin-bottom: 25px;
    }
    .working-on { color: #00ff00; font-family: 'Courier New', monospace; font-size: 26px; font-weight: bold; text-shadow: 1px 1px #000; }
    .current-time { color: #ff4b4b; font-size: 20px; font-weight: 900; text-transform: uppercase; margin-bottom: 8px; font-family: 'Segoe UI', sans-serif; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stDateInput>div>div>input { 
        background-color: #1c1f26 !important; color: #00ff00 !important; font-family: 'Courier New', monospace; border: 1px solid #444; 
    }
    .stButton>button { 
        width: 100%; background-color: #ff4b4b; color: white; font-weight: 900; 
        height: 3.5em; border-radius: 5px; border: none; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #d43f3f; box-shadow: 0px 0px 15px #ff4b4b; }
    section[data-testid="stSidebar"] { background-color: #1c1f26; border-right: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIME LOGIC (MONTREAL OFFSET UTC-4) ---
local_now = datetime.utcnow() - timedelta(hours=4)
display_time = local_now.strftime("%A, %B %d, %Y | %I:%M %p")

# --- 3. FRONT ACCESS ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.4, 1])
    with center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-logo">GARAGE HUB</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">FLEET MANAGEMENT</div>', unsafe_allow_html=True)
        pin = st.text_input("ENTER ACCESS PIN", type="password", placeholder="****")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("OPEN HUB"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("INVALID PIN")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DATABASE SETUP ---
LOG, FLEET = "maintenance_log.csv", "fleet_database.csv"
COLS = ["Date", "Vehicle", "Type", "KM", "Notes", "Oil_M", "Oil_P", "Oil_T", "F_Tire", "R_Tire", "Bulbs", "Photo"]

for f in [LOG, FLEET]:
    if not os.path.exists(f):
        pd.DataFrame(columns=COLS if f==LOG else ["Year", "Make", "Model", "Cat"]).to_csv(f, index=False)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ SYSTEM")
    if st.button("LOCK HUB"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("SELECT VEHICLE", f_df["Name"].tolist())
        if active_v:
            active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]
        
        with st.expander("REMOVE VEHICLE"):
            if st.button("CONFIRM DELETE"):
                new_f = f_df[f_df["Name"] != active_v].drop(columns=["Name"])
                new_f.to_csv(FLEET, index=False)
                st.rerun()
    
    with st.expander("ADD NEW VEHICLE"):
        y = st.selectbox("Year", range(2027, 1990, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("SAVE UNIT"):
            df_fleet = pd.read_csv(FLEET)
            new_row = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([df_fleet, new_row], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. DASHBOARD HEADER ---
if active_v:
    st.markdown(f"""
        <div class="dash-header">
            <div class="current-time">{display_time}</div>
            <div class="working-on">ACTIVE BAY: {active_v.upper()}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No vehicles registered. Add one in the sidebar.")
    st.stop()

# --- 7. DATA ENTRY ---
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    mode = st.selectbox("SERVICE MODULE", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("ODOMETER (KM)") if mode != "Legal File" else ""
    uploaded_file = st.file_uploader("📂 ATTACH DOCS/PHOTOS", type=['png', 'jpg', 'jpeg'])
    photo_name = uploaded_file.name if uploaded_file else "None"
    st.divider()

    entry = {k: "" for k in COLS}
    entry.update({"Date": local_now.strftime("%Y-%m-%d"), "Vehicle": active_v, "Type": mode, "KM": km, "Photo": photo_name})

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            c1, c2, c3 = st.columns(3)
            entry["Oil_M"] = c1.text_input("Engine Oil", "20W-50")
            entry["Oil_P"] = c2.text_input("Primary Oil")
            entry["Oil_T"] = c3.text_input("Trans Oil")
            filter_val = st.text_input("Filter #")
            notes_val = st.text_area("Notes")
