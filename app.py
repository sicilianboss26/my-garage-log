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

COLS = ["Date", "Unit", "KM", "Next_KM", "Type", "Ref", "Oil_G", "Oil_Q", "Oil_Cat", "Oil_F", "Primary_Oil", "Trans_Oil", "Air_F", "Batt", "Tire_S", "Tire_Sea", "Tire_D", "Winter_Size", "Summer_Size", "Low_B", "High_B", "Fog", "Blink", "Dom", "Ins", "Reg", "Photo", "Notes"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. SIDEBAR: ADD & REMOVE VEHICLES ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"

with st.sidebar.expander("➕ Add New Vehicle"):
    vy = st.selectbox("Year", range(2027, 1980, -1))
    vma, vmo = st.text_input("Make"), st.text_input("Model")
    vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle") and vma and vmo:
        save_df(pd.concat([get_df(FLEET), pd.DataFrame([{"Year":vy, "Make":vma, "Model":vmo, "Category":vct}])]), FLEET)
        st.rerun()

if not fleet_df.empty:
    fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Active Vehicle", fleet_df["D"].tolist())
    unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Delete Selected Vehicle"):
        if st.sidebar.checkbox("Confirm Permanently Delete?"):
            save_df(fleet_df[fleet_df["D"] != active_unit].drop(columns=["D"]), FLEET)
            h = get_df(LOG)
            save_df(h[h["Unit"] != active_unit], LOG); st.rerun()

# --- 4. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

col1, col2 = st.columns([1, 2], gap="large")
with col1:
    st.subheader(f"📝 Log: {active_unit}")
    with st.container(border=True):
        l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        l_t = st.selectbox("Activity", ["Oil Change", "Tire Swap", "Bulbs", "Battery", "Repair", "Legal"], key=f"t_{active_unit}")
        o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, t_sea, t_d, w_sz, s_sz, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","","","", "","","","","","","","", "", 0
        
        if l_t == "Oil Change":
            if unit_cat == "Motorcycle":
                st.markdown("**Engine**"); c1, c2 = st.columns(2)
                o_g, o_f = c1.text_input("Grade", key=f"og_{active_unit}"), c2.text_input("Filter #", key=f"of_{active_unit}")
                o_c = st.selectbox("Oil Category", ["Mineral", "Synthetic Blend", "Full Synthetic", "V-Twin Specific"], key=f"oc_{active_unit}")
                st.markdown("**Drivetrain**"); c3, c4 = st.columns(2)
                pri, tra = c3.text_input("Primary Oil", key=f"pri_{active_unit}"), c4.text_input("Trans Oil", key=f"tra_{active_unit}")
            else:
                c1, c2 = st.columns(2)
                o_g, o_q = c1.text_input("Grade", key=f"og_{active_unit}"), c2.text_input("Liters", key=f"oq_{active_unit}")
                o_c = st.selectbox("Oil Category", ["Mineral", "Conventional", "Synthetic Blend", "Full Synthetic", "High Mileage"], key=f"oc_{active_unit}")
                o_f = st.text_input("Filter #", key=f"of_{active_unit}")
            nxt = l_km + 8000
            
        elif l_t == "Tire Swap":
            t_sea = st.radio("Set Installed", ["Winters ❄️", "Summers ☀️"], key=f"ts_{active_unit}")
            if unit_cat != "Motorcycle":
                c1, c2 = st.columns(2)
                w_sz, s_sz = c1.text_input("Winter Size", key=f"ws_{active_unit}"), c2.text_input("Summer Size", key=f"ss_{active_unit}")
            t_d = st.date_input("Deadline", value=datetime(2026,12,1) if "Summers" in t_sea else datetime(2027,3,15), key=f"td_{active_unit}")

        l_ref, l_notes = st.text_input("Ref #", key=f"rf_{active_unit}"), st.text_area("Notes", key=f"n_{active_unit}")
        gal_photo = st.file_uploader("Upload Gallery Photo", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")

        if st.button("Commit to Log"):
            if gal_photo:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(gal_photo).save(p_p)
            new_r = [datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, nxt, l_t, l_ref, o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, t_sea, str(t_d), w_sz, s_sz, l_b, h_b, fog, blk, dom, str(ins), str(reg), p_p, l_notes]
            save_df(pd.concat([get_df(LOG), pd.DataFrame([new_r], columns=COLS)]), LOG); st.rerun()

with col2:
    st.subheader(f"📊 {active_unit} History")
    hist = get_df(LOG)
    if not hist.empty:
        unit_h = hist[hist["Unit"] == active_unit].sort_values("KM", ascending=False)
        photo_rows = unit_h[unit_h["Photo"].notna() & (unit_h["Photo"] != "")]
        if not photo_rows.empty:
            with st.expander("🔍 View Photos"):
                sel_d = st.selectbox("Select Entry Date", photo_rows["Date"].tolist())
                st.image(photo_rows[photo_rows["Date"] == sel_d]["Photo"].values[0])

        edit_mode = st.toggle("🔓 Enable Edit Mode")
        if edit_mode:
            edited_df = st.data_editor(unit_h, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("💾 Save Changes"):
                save_df(pd.concat([hist[hist["Unit"] != active_unit], edited_df], ignore_index=True), LOG); st.rerun()
        else:
            st.dataframe(unit_h, use_container_width=True, hide_index=True)
