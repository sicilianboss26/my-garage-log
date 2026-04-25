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

# Columns to support the expanded battery and lighting data
COLS = ["Date", "Unit", "KM", "Next_KM", "Type", "Ref", "Oil_G", "Oil_Q", "Oil_Cat", "Oil_F", "Primary_Oil", "Trans_Oil", "Air_F", "Batt", "Tire_S", "Front_Size", "Rear_Size", "Low_B", "High_B", "Fog", "Blink", "Dom", "Ins", "Reg", "Photo", "Notes"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. SIDEBAR ---
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
    active_unit = st.sidebar.selectbox("Select Vehicle", fleet_df["D"].tolist())
    unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]
    if st.sidebar.button("🗑️ Delete Vehicle"):
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
        l_t = st.selectbox("Activity", ["Oil Change", "Tire Service", "Bulbs", "Battery", "Repair", "Legal"], key=f"t_{active_unit}")
        o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, f_sz, r_sz, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","", "","","","","","","","", "", 0
        
        # --- BATTERY CATEGORY (PROFESSIONAL LAYOUT) ---
        if l_t == "Battery":
            st.write("🔋 **Electrical System Specs**")
            b_c1, b_c2 = st.columns(2)
            b_size = b_c1.text_input("Group Size", placeholder="e.g. H6 / 24 / YTX14L-BS")
            b_cca = b_c2.text_input("CCA / Amp Hours", placeholder="e.g. 750 / 12Ah")
            
            b_c3, b_c4 = st.columns(2)
            b_volt = b_c3.text_input("Voltage (Static/Running)", placeholder="e.g. 12.6v / 14.2v")
            b_brand = b_c4.text_input("Brand/Model", placeholder="e.g. Interstate / AGM")
            
            bat = f"Size: {b_size} | CCA: {b_cca} | Volts: {b_volt} | Brand: {b_brand}"

        # --- BULBS CATEGORY ---
        elif l_t == "Bulbs":
            st.write("💡 **Lighting Maintenance**")
            l_c1, l_c2 = st.columns(2)
            l_b = l_c1.text_input("Low Beam", key="lb")
            h_b = l_c2.text_input("High Beam", key="hb")
            blk = l_c1.text_input("Blinkers", key="bk")
            
            if unit_cat != "Motorcycle":
                fog = l_c2.text_input("Fog Lights", key="fg")
                dom = l_c1.text_input("Dome Lights", key="dm")
                reg = l_c2.text_input("License Plate Lights", key="reg_l")

        # --- TIRE SERVICE ---
        elif l_t == "Tire Service":
            st.write("🔧 **Front Tire Size**")
            t_f1, t_f2, t_f3 = st.columns(3)
            fw, fa, fr = t_f1.text_input("W", key="fw"), t_f2.text_input("R", key="fa"), t_f3.text_input("D", key="fr")
            f_sz = f"{fw}/{fa}R{fr}" if fw and fa and fr else ""
            if unit_cat == "Motorcycle":
                st.write("🏍️ **Rear Tire Size**")
                t_r1, t_r2, t_r3 = st.columns(3)
                rw, ra, rr = t_r1.text_input("W ", key="rw"), t_r2.text_input("R ", key="ra"), t_r3.text_input("D ", key="rr")
                r_sz = f"{rw}/{ra}R{rr}" if rw and ra and rr else ""

        # --- OIL CHANGE ---
        elif l_t == "Oil Change":
            if unit_cat == "Motorcycle":
                st.markdown("**Engine**"); m1, m2 = st.columns(2)
                o_g, o_f = m1.text_input("Grade", key="og"), m2.text_input("Filter #", key="of")
                o_c = st.selectbox("Type", ["Mineral", "V-Twin", "Synthetic"], key="oc")
                st.markdown("**Drivetrain**"); m3, m4 = st.columns(2)
                pri, tra = m3.text_input("Primary Oil", key="pri"), m4.text_input("Trans Oil", key="tra")
            else:
                o1, o2 = st.columns(2)
                o_g, o_c = o1.text_input("Grade", key="og"), o2.selectbox("Type", ["Full Synthetic", "High Mileage", "Conventional"], key="oc")
                o_f = st.text_input("Filter #", key="of")
            nxt = l_km + 8000

        l_notes = st.text_area("General Notes", key=f"n_{active_unit}")
        gal = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")
        
        if st.button("Commit to Log"):
            if gal:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(gal).save(p_p)
            save_df(pd.concat([get_df(LOG), pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, nxt, l_t, "", o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, f_sz, r_sz, l_b, h_b, fog, blk, dom, str(ins), str(reg), p_p, l_notes]], columns=COLS)]), LOG); st.rerun()

with c2:
    st.subheader(f"📊 Service History")
    hist = get_df(LOG)
    if not hist.empty:
        u_h = hist[hist["Unit"] == active_unit].sort_values("KM", ascending=False)
        p_rows = u_h[u_h["Photo"].notna() & (u_h["Photo"] != "")]
        if not p_rows.empty:
            with st.expander("🔍 View Photos"):
                sd = st.selectbox("Select Date", p_rows["Date"].tolist())
                st.image(p_rows[p_rows["Date"] == sd]["Photo"].values[0])
        
        edit = st.toggle("🔓 Enable Edit Mode")
        if edit:
            ed = st.data_editor(u_h, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("💾 Save Changes"):
                save_df(pd.concat([hist[hist["Unit"] != active_unit], ed], ignore_index=True), LOG); st.rerun()
        else:
            st.dataframe(u_h, use_container_width=True, hide_index=True)
