import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. INTERFACE STYLING ---
st.set_page_config(page_title="Garage Hub", page_icon="🔧", layout="wide")

bg_img = "https://images.unsplash.com/photo-1507702553912-a15641ec5821?q=80&w=2600&auto=format&fit=crop"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("{bg_img}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    [data-testid="stVerticalBlock"] > div:has(div.login-card), 
    .dash-header, .stForm, [data-testid="column"], [data-testid="stExpander"] {{
        background: rgba(15, 15, 15, 0.85) !important;
        backdrop-filter: blur(8px); border-radius: 12px; padding: 20px;
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
    }}
    .shop-logo {{ font-size: 60px; font-weight: 900; color: #ff4b4b; text-shadow: 0px 0px 10px rgba(255, 75, 75, 0.5); letter-spacing: 3px; }}
    .shop-subtitle {{ color: #888; font-family: 'Courier New'; font-size: 14px; letter-spacing: 10px; margin-bottom: 40px; text-transform: uppercase; }}
    .working-on {{ color: #00ff00; font-family: 'Courier New', monospace; font-size: 28px; font-weight: bold; }}
    .current-time {{ color: #ff4b4b; font-size: 18px; font-weight: 800; text-transform: uppercase; }}
    .stTextInput input, .stTextArea textarea, .stSelectbox div {{
        background-color: rgba(0, 0, 0, 0.7) !important; color: #00ff00 !important;
        border: 1px solid #333 !important; font-family: 'Courier New', monospace !important;
    }}
    .stButton>button {{ 
        width: 100%; background: linear-gradient(135deg, #ff4b4b 0%, #a10000 100%); 
        color: white; font-weight: 900; height: 3.5em; border-radius: 8px; border: none; text-transform: uppercase;
    }}
    section[data-testid="stSidebar"] {{ background-color: rgba(10, 10, 10, 0.95) !important; border-right: 1px solid #ff4b4b; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TIME LOGIC (MONTREAL OFFSET UTC-4) ---
local_now = datetime.utcnow() - timedelta(hours=4)
display_time = local_now.strftime("%A, %B %d, %Y | %I:%M %p")

# --- 3. FRONT ACCESS ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div style="text-align:center; padding: 50px 0;">', unsafe_allow_html=True)
        st.markdown('<div class="shop-logo">GARAGE HUB</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">SYSTEM ONLINE</div>', unsafe_allow_html=True)
        pin = st.text_input("ACCESS PIN", type="password", placeholder="****")
        if st.button("AUTHENTICATE"):
            if pin == "1234":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
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
    st.markdown("### 🔧 HUB CONTROL")
    if st.button("LOCK SYSTEM"):
        st.session_state.auth = False
        st.rerun()
    st.divider()
    
    f_df = pd.read_csv(FLEET)
    active_v, active_cat = None, "Car/SUV"
    
    if not f_df.empty:
        f_df["Name"] = f_df["Year"].astype(str) + " " + f_df["Make"] + " " + f_df["Model"]
        active_v = st.selectbox("SELECT ACTIVE BAY", f_df["Name"].tolist())
        if active_v:
            active_cat = f_df[f_df["Name"] == active_v]["Cat"].values[0]
        
        with st.expander("DELETE UNIT"):
            if st.button("CONFIRM SCRAP"):
                new_f = f_df[f_df["Name"] != active_v].drop(columns=["Name"])
                new_f.to_csv(FLEET, index=False)
                st.rerun()
    
    with st.expander("REGISTER NEW UNIT"):
        y = st.selectbox("Year", range(2027, 1980, -1))
        ma = st.text_input("Make")
        mo = st.text_input("Model")
        ct = st.radio("Type", ["Car/SUV", "Truck", "Motorcycle"])
        if st.button("SAVE TO FLEET"):
            df_fleet = pd.read_csv(FLEET)
            new_row = pd.DataFrame([{"Year": y, "Make": ma, "Model": mo, "Cat": ct}])
            pd.concat([df_fleet, new_row], ignore_index=True).to_csv(FLEET, index=False)
            st.rerun()

# --- 6. DASHBOARD HEADER ---
if active_v:
    st.markdown(f"""
        <div class="dash-header">
            <div class="current-time">{display_time}</div>
            <div class="working-on">CURRENT VEHICLE: {active_v.upper()} ({active_cat.upper()})</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("FLEET EMPTY. ADD A VEHICLE IN THE SIDEBAR.")
    st.stop()

# --- 7. DATA ENTRY & LOGS ---
col1, col2 = st.columns([1.3, 2], gap="large")

with col1:
    st.markdown("### ⚙️ LOG SERVICE")
    mode = st.selectbox("TASK", ["Oil Change", "Tires", "Repair", "Diagnostic", "Bulbs", "Legal File"])
    km = st.text_input("KM READING") if mode != "Legal File" else ""
    st.divider()

    entry = {k: "" for k in COLS}
    entry.update({"Date": local_now.strftime("%Y-%m-%d"), "Vehicle": active_v, "Type": mode, "KM": km})

    if mode == "Oil Change":
        if active_cat == "Motorcycle":
            st.markdown("##### 🏍️ Triple-Oil Service")
            c1, c2, c3 = st.columns(3)
            o_m = c1.text_input("Motor Oil", "20W-50")
            o_p = c2.text_input("Primary Oil")
            o_t = c3.text_input("Trans Oil")
            v_m = c1.text_input("Motor (L)")
            v_p = c2.text_input("Primary (L)")
            v_t = c3.text_input("Trans (L)")
            o_f = st.text_input("Filter Part #")
            o_notes = st.text_area("Service Details")
            entry["Oil_M"], entry["Oil_P"], entry["Oil_T"] = f"{o_m} ({v_m}L)", f"{o_p} ({v_p}L)", f"{o_t} ({v_t}L)"
            entry["Notes"] = f"Filter: {o_f} | {o_notes}"
        else:
            o_type = st.selectbox("Type", ["Full Synth", "Blend", "Conventional"])
            o_grade = st.text_input("Grade")
            o_lit = st.text_input("Liters")
            o_f = st.text_input("Filter #")
            o_notes = st.text_area("Service Details")
            entry["Oil_M"] = f"{o_grade} ({o_type})"
            entry["Notes"] = f"{o_lit}L | Filter: {o_f} | {o_notes}"

    elif mode == "Tires":
        if active_cat == "Motorcycle":
            t1, t2 = st.columns([2, 1])
            f_s, f_p = t1.text_input("Front Size"), t2.text_input("Front PSI")
            t3, t4 = st.columns([2, 1])
            r_s, r_p = t3.text_input("Rear Size"), t4.text_input("Rear PSI")
            entry["F_Tire"], entry["R_Tire"] = f"{f_s} ({f_p})", f"{r_s} ({r_p})"
            entry["Notes"] = st.text_area("Condition / Brand")
        else:
            entry["Notes"] = st.text_area("Tire Notes (Size, PSI, Rotation, Brand)")

    elif mode == "Repair":
        rep_sys = st.selectbox("System", ["Engine", "Transmission", "Electrical", "Audio", "Suspension", "Brakes", "Exhaust", "Body"])
        parts = st.text_area("Parts List")
        work = st.text_area("Work Summary")
        entry["Type"] = f"Repair: {rep_sys}"
        entry["Notes"] = f"Parts: {parts} | Work: {work}"

    elif mode == "Diagnostic":
        dtc = st.text_input("DTC / Fault Codes")
        findings = st.text_area("Tech Findings")
        entry["Notes"] = f"CODES: {dtc} | {findings}"

    elif mode == "Bulbs":
        b_pos = st.selectbox("Position", ["Low Beam", "High Beam", "Fog", "Signal", "Tail"])
        b_spec = st.text_input("Bulb Spec")
        entry["Type"] = f"Bulb: {b_pos}"
        entry["Notes"] = f"Spec: {b_spec}"

    elif mode == "Legal File":
        l_doc = st.selectbox("Doc Type", ["Registration", "Insurance", "License", "Safety"])
        l_date = st.date_input("Valid Until")
        entry["Type"] = f"Legal: {l_doc}"
        entry["Notes"] = f"Expiry: {l_date}"

    if st.button("💾 SAVE RECORD TO LOG"):
        df_l = pd.read_csv(LOG)
        new_row = pd.DataFrame([entry])
        pd.concat([df_l, new_row], ignore_index=True).to_csv(LOG, index=False)
        st.rerun()

with col2:
    st.subheader("📋 HISTORY")
    h_df = pd.read_csv(LOG)
    if not h_df.empty:
        v_h = h_df[h_df["Vehicle"] == active_v].sort_values(by="Date", ascending=False)
        st.dataframe(v_h, use_container_width=True, hide_index=True)
        
        with st.expander("📝 EDIT / DELETE LOGS"):
            if not v_h.empty:
                v_h['Display'] = v_h['Date'] + " - " + v_h['Type']
                sel_idx = st.selectbox("Select Record", v_h.index, format_func=lambda x: v_h.loc[x, 'Display'])
                c_del, c_up = st.columns(2)
                if c_del.button("🗑️ DELETE"):
                    h_df.drop(sel_idx).to_csv(LOG, index=False)
                    st.rerun()
                
                new_notes = st.text_area("Edit Notes", value=str(h_df.loc[sel_idx, "Notes"]))
                if c_up.button("🔄 PUSH UPDATE"):
                    h_df.at[sel_idx, "Notes"] = new_notes
                    h_df.to_csv(LOG, index=False)
                    st.rerun()
