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

# --- 4. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")
with c1:
    st.subheader(f"📝 Log: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Oil Change", "Tire Service", "Bulbs", "Battery", "Repair", "Legal"], key=f"t_{active_unit}")
        
        # KM logic
        l_km = 0
        if l_t != "Legal":
            l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        else:
            st.info("📂 Administrative Log: Mileage not required.")

        o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, f_sz, r_sz, l_b, h_b, fog, blk, dom, ins, reg, p_p, nxt = "","","","","","","","","","", "","","","","","","","", "", 0
        l_notes = ""

        # --- LEGAL CATEGORY (STREAMLINED) ---
        if l_t == "Legal":
            st.write("📑 **Compliance Tracking**")
            leg_c1, leg_c2 = st.columns(2)
            doc_type = leg_c1.selectbox("Document", ["Registration", "Insurance", "Safety Inspection", "Permit"])
            ref_num = leg_c2.text_input("Reference / Policy #")
            exp_date = st.date_input("Expiry Date")
            l_notes = f"Type: {doc_type} | Ref: {ref_num} | Expires: {exp_date}"

        # --- REPAIR ---
        elif l_t == "Repair":
            st.write("📋 **Work Order**")
            comp_list = ["Engine", "Transmission", "Drivetrain", "Suspension", "Brakes", "Steering", "Cooling", "Exhaust", "Fuel", "Electrical", "Body", "Audio/Interior"]
            sel_comp = st.selectbox("System", comp_list)
            sel_act = st.segmented_control("Action", ["Replace", "Repair", "Service", "Inspect", "Upgrade"])
            st.write("📦 **Parts**")
            parts_data = pd.DataFrame([{"Part": "", "Part #": "", "Qty": 1, "Price": 0.00}])
            edited_parts = st.data_editor(parts_data, num_rows="dynamic", use_container_width=True)
            total_cost = (edited_parts["Qty"] * edited_parts["Price"]).sum()
            st.metric("Total Cost", f"${total_cost:,.2f}")
            parts_summary = "; ".join([f"{r['Part']}" for _, r in edited_parts.iterrows() if r['Part']])
            l_notes = f"System: {sel_comp} | Action: {sel_act} | Total: ${total_cost:.2f} | Parts: {parts_summary}"

        # --- BATTERY ---
        elif l_t == "Battery":
            st.write("🔋 **Electrical**")
            b1, b2 = st.columns(2)
            bat = f"Size: {b1.text_input('Size')} | CCA: {b2.text_input('CCA')} | Volts: {b1.text_input('Volts')} | Brand: {b2.text_input('Brand')}"

        # --- BULBS ---
        elif l_t == "Bulbs":
            st.write("💡 **Lighting**")
            l_c1, l_c2 = st.columns(2)
            l_b, h_b = l_c1.text_input("Low Beam"), l_c2.text_input("High Beam")
            blk = l_c1.text_input("Blinkers")
            if unit_cat != "Motorcycle":
                fog, dom, reg = l_c2.text_input("Fog"), l_c1.text_input("Dome"), l_c2.text_input("License Plate")

        # --- TIRE SERVICE ---
        elif l_t == "Tire Service":
            st.write("🔧 **Front Tire**")
            t_f1, t_f2, t_f3 = st.columns(3)
            fw, fa, fr = t_f1.text_input("W"), t_f2.text_input("R"), t_f3.text_input("D")
            f_sz = f"{fw}/{fa}R{fr}" if fw and fa and fr else ""
            if unit_cat == "Motorcycle":
                st.write("🏍️ **Rear Tire**")
                r1, r2, r3 = st.columns(3)
                rw, ra, rr = r1.text_input("W "), r2.text_input("R "), r3.text_input("D ")
                r_sz = f"{rw}/{ra}R{rr}" if rw and ra and rr else ""

        # --- OIL CHANGE ---
        elif l_t == "Oil Change":
            if unit_cat == "Motorcycle":
                st.markdown("**Engine**"); m1, m2 = st.columns(2)
                o_g, o_f = m1.text_input("Grade"), m2.text_input("Filter #")
                o_c = st.selectbox("Type", ["Mineral", "V-Twin", "Synthetic"])
                st.markdown("**Drivetrain**"); m3, m4 = st.columns(2)
                pri, tra = m3.text_input("Primary Oil"), m4.text_input("Trans Oil")
            else:
                o1, o2 = st.columns(2)
                o_g, o_c = o1.text_input("Grade"), o2.selectbox("Type", ["Full Synthetic", "High Mileage", "Conventional"])
                o_f = st.text_input("Filter #")
            nxt = l_km + 8000

        # Optional detail for Repairs/Tires/Oil etc. 
        # (Self-hiding for Legal unless you want to keep a generic notes box)
        if l_t != "Legal":
            extra_notes = st.text_area("Final Observations", key=f"ex_{active_unit}")
            if l_notes: l_notes += f" | Obs: {extra_notes}"
            else: l_notes = extra_notes
        
        gal = st.file_uploader("Upload Image/Doc", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")
        
        if st.button("Commit to Log"):
            if gal:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(gal).save(p_p)
            save_df(pd.concat([get_df(LOG), pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_km, nxt, l_t, "", o_g, o_q, o_c, o_f, pri, tra, a_f, bat, t_s, f_sz, r_sz, l_b, h_b, fog, blk, dom, str(ins), str(reg), p_p, l_notes]], columns=COLS)]), LOG); st.rerun()

with c2:
    st.subheader(f"📊 History")
    hist = get_df(LOG)
    if not hist.empty:
        u_h = hist[hist["Unit"] == active_unit].sort_values("Date", ascending=False)
        st.dataframe(u_h, use_container_width=True, hide_index=True)
