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
    st.info("Awaiting pin...")
    st.stop()

# --- 2. DATA ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "KM", "Next_KM", "Type", "Ref", "Oil_G", "Oil_Q", "Oil_Cat", "Oil_F", "Air_F", "Batt", "Tire_S", "Tire_Sea", "Tire_D", "Low_B", "High_B", "Fog", "Blink", "Dom", "Ins", "Reg", "Photo", "Notes"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 3. GARAGE ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"
if not fleet_df.empty:
    fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
    active_unit = st.sidebar.selectbox("Select Vehicle", fleet_df["D"].tolist())
    unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]

with st.sidebar.expander("➕ Add Vehicle"):
    vy, vma, vmo = st.selectbox("Year", range(2027, 1980, -1)), st.text_input("Make"), st.text_input("Model")
    vct = st.radio("Type", ["Car", "Truck", "Motorcycle"])
    if st.button("Save Vehicle") and vma and vmo:
        save_df(pd.concat([get_df(FLEET), pd.DataFrame([{"Year":vy,"Make":vma,"Model":vmo,"Category":vct}])]), FLEET)
        st.rerun()

# --- 4. DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

col1, col2 = st.columns([1, 2], gap="large")
with col1:
    st.subheader(f"📝 Log: {active_unit}")
    with st.container(border=True):
        l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        l_t = st.selectbox("Activity", ["Oil Change", "Tire Swap", "Bulbs", "Battery", "Repair", "Legal"], key=f"t_{active_unit}")
        o_g, o_q, o_c, o_f, a_f, bat, t_s, t_sea, t_d, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","","","","","","", "", "", 0
        
        if l_t == "Oil Change":
            o_g, o_q = st.text_input("Grade", key=f"og_{active_unit}"), st.text_input("Liters", key=f"oq_{active_unit}")
            opts = ["Synthetic Blend", "Full Synthetic", "Mineral", "V-Twin Specific"] if unit_cat == "Motorcycle" else ["Full Synthetic", "High Mileage", "Synthetic Blend", "Conventional"]
            o_c, o_f, nxt = st.selectbox("Category", opts, key=f"oc_{active_unit}"), st.text_input("Filter #", key=f"of_{active_unit}"), l_km + 8000
        elif l_t == "Tire Swap":
            t_sea = st.radio("Installed", ["Winters ❄️", "Summers ☀️"], key=f"ts_{active_unit}")
            def_d = datetime(2026,12,1) if "Summers" in t_sea else datetime(2027,3,15)
            t_d = st.date_input("Deadline", value=def_d, key=f"td_{active_unit}")
        elif l_t == "Bulbs":
            l_b, h_b = st.text_input("Low", key=f"lb_{active_unit}"), st.text_input("High", key=f"hb_{active_unit}")
            fog, blk = st.text_input("Fog", key=f"fg_{active_unit}"), st.text_input("Blinker", key=f"bl_{active_unit}")
        elif l_t == "Legal":
            ins, reg = st.date_input("Insurance", key=f"i_{active_unit}"), st.date_input("Plates", key=f"r_{active_unit}")

        l_ref, l_notes = st.text_input("Part # / Ref", key=f"rf_{active_unit}"), st.text_area("Notes", key=f"n_{active_unit}")
        photo = st.camera_input("Photo", key=f"p_{active_unit}")

        if st.button("Commit to Log"):
            if photo:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(photo).save(p_p)
            new_r = [datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, nxt, l_t, l_ref, o_g, o_q, o_c, o_f, a_f, bat, t_s, t_sea, str(t_d), l_b, h_b, fog, blk, dom, str(ins), str(reg), p_p, l_notes]
            save_df(pd.concat([get_df(LOG), pd.DataFrame([new_r], columns=COLS)]), LOG)
            st.rerun()

with col2:
    st.subheader(f"📊 {active_unit} History")
    hist = get_df(LOG)
    if not hist.empty:
        edit_mode = st.toggle("🔓 Enable Edit Mode")
        unit_h = hist[hist["Unit"] == active_unit].sort_values("KM", ascending=False)
        if edit_mode:
            edited_df = st.data_editor(unit_h, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("💾 Save Changes"):
                non_unit_data = hist[hist["Unit"] != active_unit]
                final_df = pd.concat([non_unit_data, edited_df], ignore_index=True)
                save_df(final_df, LOG); st.success("Updated!"); st.rerun()
        else:
            st.dataframe(unit_h, use_container_width=True, hide_index=True)
        if not unit_h.empty and pd.notna(unit_h.iloc[0]['Photo']):
            if unit_h.iloc[0]['Photo'] != "": st.image(unit_h.iloc[0]['Photo'])
