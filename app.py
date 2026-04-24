import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")
with st.sidebar:
    st.title("🔧 Antonino's Shop")
    pin = st.text_input("Pin", type="password")
if pin != "1234":
    st.info("Awaiting pin..."); st.stop()

# --- 2. DATA ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "KM", "Next_KM", "Type", "Ref", "Oil_G", "Oil_Q", "Oil_Cat", "Oil_F", "Primary_Oil", "Trans_Oil", "Air_F", "Batt", "Tire_S", "Front_Size", "Rear_Size", "Low_B", "High_B", "Fog", "Blink", "Dom", "Ins", "Reg", "Photo", "Notes"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. SIDEBAR: VEHICLE MANAGEMENT ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"

with st.sidebar.expander("➕ Add New Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma, vmo = st.text_input("Make"), st.text_input("Model")
    vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle") and vma and vmo:
        save_df(pd.concat([get_df(FLEET), pd.DataFrame([{"Year":vy,"Make":vma,"Model":vmo,"Category":vct}])]), FLEET)
        st.rerun()

if not fleet_df.empty:
    fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Active Vehicle", fleet_df["D"].tolist())
    unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Delete Selected Vehicle"):
        if st.sidebar.checkbox("Confirm Delete?"):
            save_df(fleet_df[fleet_df["D"] != active_unit].drop(columns=["D"]), FLEET)
            save_df(get_df(LOG)[get_df(LOG)["Unit"] != active_unit], LOG); st.rerun()

# --- 4. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.subheader(f"📝 Log: {active_unit}")
    with st.container(border=True):
        l_km = st.number_input("KM", min_value=0, step=1, key=f"k_{active_unit}")
        
        # Build dynamic list based on category
        act_list = ["Oil Change", "Tire Service", "Bulbs", "Blinkers", "Battery", "Repair", "Legal"]
        if unit_cat != "Motorcycle":
            act_list.insert(act_list.index("Blinkers") + 1, "License Plate Lights")
            
        l_t = st.selectbox("Activity", act_list, key=f"t_{active_unit}")
        o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, f_sz, r_sz, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","", "","","","","","","","", "", 0
        
        if l_t == "Blinkers":
            blk = st.text_input("Blinker Bulb Model", placeholder="e.g. 1156 / 7440", key="bk_field")

        elif l_t == "License Plate Lights":
            l_notes = st.text_input("License Plate Bulb Model", placeholder="e.g. 194 / T10", key="lp_field")

        elif l_t == "Bulbs":
            # Dynamic header and fields for bike vs car
            if unit_cat == "Motorcycle":
                st.write("🏍️ **Headlights**")
                b_col1, b_col2 = st.columns(2)
                l_b = b_col1.text_input("Low Beam", key="lb")
                h_b = b_col2.text_input("High Beam", key="hb")
            else:
                st.write("💡 **Headlights & Interior**")
                b_col1, b_col2 = st.columns(2)
                l_b = b_col1.text_input("Low Beam", key="lb")
                h_b = b_col2.text_input("High Beam", key="hb")
                fog = b_col1.text_input("Fog Lights", key="fg")
                dom = b_col2.text_input("Dome Lights", key="dm")

        elif l_t == "Tire Service":
            st.write("🔧 **Tire Size**" if unit_cat != "Motorcycle" else "🏍️ **Front Tire**")
            f1, f2, f3 = st.columns(3)
            fw, fa, fr = f1.text_input("Width", key="fw"), f2.text_input("Ratio", key="fa"), f3.text_input("Rim", key="fr")
            f_sz = f"{fw}/{fa}R{fr}" if fw and fa and fr else ""
            if unit_cat == "Motorcycle":
                st.write("🏍️ **Rear Tire**")
                r1, r2, r3 = st.columns(3)
                rw, ra, rr = r1.text_input("Width ", key="rw"), r2.text_input("Ratio ", key="ra"), r3.text_input("Rim ", key="rr")
                r_sz = f"{rw}/{ra}R{rr}" if rw and ra and rr else ""

        elif l_t == "Oil Change":
            if unit_cat == "Motorcycle":
                st.markdown("**Engine**"); m1, m2 = st.columns(2)
                o_g, o_f = m1.text_input("Grade", key="og"), m2.text_input("Filter #", key="of")
                o_c = st.selectbox("Type", ["Mineral", "V-Twin", "Synthetic"], key="oc")
                st.markdown("**Drivetrain**"); m3, m4 = st.columns(2)
                pri, tra = m3
