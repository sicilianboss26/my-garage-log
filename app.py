import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP & CUSTOM THEME ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #111214 !important; }
    
    /* The Shop Sign / Login Box */
    .login-terminal {
        padding: 40px;
        background-color: #262730;
        border-radius: 15px;
        border: 2px solid #ff4b4b;
        text-align: center;
        margin-top: 50px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }
    .shop-name { 
        color: #ff4b4b; 
        font-size: 2.2em; 
        font-weight: 900; 
        margin-bottom: 0px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .terminal-sub { 
        color: #888; 
        font-size: 0.8em; 
        margin-bottom: 25px; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
    }

    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    div[data-testid="stExpander"] { border: 1px solid #333; border-radius: 8px; background-color: #262730; }
    h1, h2, h3 { color: #ff4b4b !important; }
    [data-testid="stMetricValue"] { color: #00ff00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.5, 1]) # Slightly wider center for the name
    with center_col:
        st.markdown('<div class="login-terminal">', unsafe_allow_html=True)
        # Using the box for the Shop Name as the main header
        st.markdown('<div class="shop-name">ANTONINO\'S</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-name" style="font-size:1.8em; margin-bottom:10px;">GARAGE HUB</div>', unsafe_allow_html=True)
        st.markdown('<div class="terminal-sub">Secure System Entry | v2.2</div>', unsafe_allow_html=True)
        
        input_pin = st.text_input("Enter Shop PIN", type="password", placeholder="****")
        
        if st.button("Unlock Terminal"):
            if input_pin == "1234":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Access Denied")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 3. DATA & DIRECTORIES ---
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service_photos"
if not os.path.exists(IMG): os.makedirs(IMG)
if not os.path.exists(FLEET):
    pd.DataFrame(columns=["Year", "Make", "Model", "Category"]).to_csv(FLEET, index=False)

COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_KM", "Notes", "Photo", "Oil_G", "Oil_F", "Primary_Oil", "Trans_Oil", "Batt", "F_Tire", "R_Tire", "Low_B", "High_B"]
if not os.path.exists(LOG):
    pd.DataFrame(columns=COLS).to_csv(LOG, index=False)

def get_df(f): return pd.read_csv(f)
def save_df(df, f): df.to_csv(f, index=False)

# --- 4. SIDEBAR / FLEET MANAGEMENT ---
fleet_df = get_df(FLEET)
active_unit, unit_cat = None, "Car"

with st.sidebar:
    st.title("🔧 Shop Control")
    if st.button("🔒 Lock App"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.divider()
    
    if not fleet_df.empty:
        fleet_df["D"] = fleet_df["Year"].astype(str) + " " + fleet_df["Make"] + " " + fleet_df["Model"]
        active_unit = st.selectbox("Select Active Vehicle", fleet_df["D"].tolist())
        unit_cat = fleet_df[fleet_df["D"] == active_unit]["Category"].values[0]

    st.markdown("---")

    with st.sidebar.expander("🗑️ Remove a Vehicle"):
        if not fleet_df.empty:
            to_remove = st.selectbox("Vehicle to Delete", fleet_df["D"].tolist(), key="del_sel")
            if st.button("Confirm Delete"):
                updated_fleet = fleet_df[fleet_df["D"] != to_remove].drop(columns=['D'])
                save_df(updated_fleet, FLEET)
                st.success(f"Removed {to_remove}")
                st.rerun()

    with st.sidebar.expander("➕ Add New Vehicle"):
        vy = st.selectbox("Year", range(2027, 1980, -1))
        vma = st.text_input("Make", key="vma")
        vmo = st.text_input("Model", key="vmo")
        vct = st.radio("Category", ["Car", "Truck", "Motorcycle"])
        if st.button("Save Vehicle"):
            if vma and vmo:
                new_v = pd.DataFrame([{"Year": vy, "Make": vma, "Model": vmo, "Category": vct}])
                save_df(pd.concat([get_df(FLEET), new_v]), FLEET)
                st.rerun()

# --- 5. MAIN DASHBOARD ---
st.title("🛠️ The Garage Hub")
if not active_unit:
    st.info("👈 Add a vehicle in the sidebar to begin."); st.stop()

c1, c2 = st.columns([1, 2], gap="large")

with c1:
    st.subheader(f"⚙️ Working on: {active_unit}")
    with st.container(border=True):
        l_t = st.selectbox("Activity", ["Repair", "Oil Change", "Tire Service", "Battery", "Bulbs", "Legal"], key=f"t_{active_unit}")
        
        sel_comp = "None"
        if l_t == "Repair":
            sel_comp = st.selectbox("System", ["Engine", "Transmission", "Suspension", "Brakes", "Electrical", "Body", "Audio"])

        l_km = 0
        if l_t not in ["Battery", "Bulbs", "Legal"] and sel_comp not in ["Audio", "Body"]:
            l_km = st.number_input("Current KM", min_value=0, step=1, key=f"k_{active_unit}")
        
        o_g, o_f, pri, tra, bat, f_sz, r_sz, l_b, h_b, nxt = "", "", "", "", "", "", "", "", "", 0
        l_cost, l_notes = 0.0, ""

        if l_t == "Repair":
            st.write(f"📋 **{sel_comp} Details**")
            parts_data = pd.DataFrame([{"Part": "", "Price": 0.00}])
            edited_parts = st.data_editor(parts_data, num_rows="dynamic", key=f"parts_{active_unit}")
            l_cost = float(edited_parts["Price"].sum())
            st.metric("Final Cost", f"${l_cost:,.2f}")
            l_notes = f"{sel_comp} Repair"

        elif l_t == "Oil Change":
            st.write("🛢️ **Engine Fluid**")
            m1, m2 = st.columns(2)
            o_g = m1.text_input("Oil Grade/Brand")
            o_f = m2.text_input("Filter Model #")
            if unit_cat == "Motorcycle":
                st.write("⛓️ **Drivetrain Fluids**")
                m3, m4 = st.columns(2)
                pri = m3.text_input("Primary Oil")
                tra = m4.text_input("Transmission Oil")
            l_cost = st.number_input("Total Fluid/Parts Cost", min_value=0.0, step=0.01)
            nxt = l_km + 8000

        elif l_t == "Tire Service":
            st.write("🛞 **Front Tires**")
            tf1, tf2, tf3 = st.columns(3)
            f_sz = f"{tf1.text_input('W', key='fw')}/{tf2.text_input('R', key='fr')}R{tf3.text_input('D', key='fd')}"
            st.write("🛞 **Rear Tires**")
            tr1, tr2, tr3 = st.columns(3)
            r_sz = f"{tr1.text_input('W', key='rw')}/{tr2.text_input('R', key='rr')}R{tr3.text_input('D', key='rd')}"
            l_cost = st.number_input("Service Cost", min_value=0.0, step=0.01)

        elif l_t == "Battery":
            st.write("🔋 **Battery Specs**")
            bc1, bc2, bc3 = st.columns(3)
            brand = bc1.text_input("Brand")
            group = bc2.text_input("Group")
            cca = bc3.text_input("CCA")
            l_cost = st.number_input("Battery Cost", min_value=0.0, step=0.01)
            bat = f"{brand} | Group: {group} | CCA: {cca}"

        elif l_t == "Bulbs":
            st.write("🔦 **Front Lighting**")
            b_c1, b_c2 = st.columns(2)
            l_b = b_c1.text_input("Low Beam Spec")
            h_b = b_c2.text_input("High Beam Spec")
            st.write("🚨 **Rear Lighting**")
            b_c3, b_c4 = st.columns(2)
            brake = b_c3.text_input("Brake Light")
            signal = b_c4.text_input("Signal Light")
            l_cost = st.number_input("Cost", min_value=0.0, step=0.01)
            l_notes = f"Brake: {brake} | Signal: {signal}"

        elif l_t == "Legal":
            st.write("📑 **Legal/Papers**")
            doc = st.selectbox("Doc Type", ["Insurance", "Registration", "License"])
            l_notes = f"{doc} Update"

        extra_n = st.text_area("Notes", placeholder="Specific details...", key=f"notes_{active_unit}")
        l_notes = f"{l_notes} | {extra_n}" if l_notes else extra_n
        gal = st.file_uploader("Photo/Receipt", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")
        
        if st.button("💾 Save Entry"):
            p_p = ""
            if gal:
                p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Image.open(gal).save(p_p)
            
            new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), active_unit, l_t, l_cost, l_km, nxt, l_notes, p_p, o_g, o_f, pri, tra, bat, f_sz, r_sz, l_b, h_b]], columns=COLS)
            save_df(pd.concat([get_df(LOG), new_row]), LOG)
            st.rerun()

with c2:
    tab1, tab2 = st.tabs(["📊 Service History", "💰 Expense Tracker"])
    hist = get_df(LOG)
    if not hist.empty:
        u_h = hist[hist["Unit"] == active_unit].sort_values("Date", ascending=False)
        with tab1:
            st.dataframe(u_h[["Date", "Type", "KM", "Notes"]], use_container_width=True, hide_index=True)
            if st.toggle("🔓 Edit Entries"):
                edited_df = st.data_editor(u_h, use_container_width=True, hide_index=True, key=f"editor_{active_unit}")
                if st.button("Apply Changes"):
                    save_df(pd.concat([hist[~hist.index.isin(u_h.index)], edited_df], ignore_index=True), LOG)
                    st.rerun()

        with tab2:
            st.subheader("Investment Summaries")
            finance_df = u_h[u_h["Type"].isin(["Repair", "Oil Change", "Tire Service", "Battery"])]
            mc1, mc2, mc3, mc4 = st.columns(4)
            r_sum = finance_df[finance_df["Type"] == "Repair"]["Cost"].sum()
            o_sum = finance_df[finance_df["Type"] == "Oil Change"]["Cost"].sum()
            t_sum = finance_df[finance_df["Type"] == "Tire Service"]["Cost"].sum()
            b_sum = finance_df[finance_df["Type"] == "Battery"]["Cost"].sum()
            
            mc1.metric("Repairs", f"${r_sum:,.2f}")
            mc2.metric("Oil", f"${o_sum:,.2f}")
            mc3.metric("Tires", f"${t_sum:,.2f}")
            mc4.metric("Battery", f"${b_sum:,.2f}")
            st.divider()
            st.metric("Total Overall Investment", f"${finance_df['Cost'].sum():,.2f}")
            st.dataframe(finance_df[["Date", "Type", "Cost", "Notes"]].style.format({"Cost": "${:,.2f}"}), use_container_width=True, hide_index=True)
