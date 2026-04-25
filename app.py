import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# --- 1. CONFIG ---
ACCESS_PIN = "1234"
IMG = "garage_images"
LOG = "garage_log.csv"
COLS = ["Date", "Unit", "Type", "Cost", "KM", "Next_Service", "Notes", "Photo", "Oil_G", "Oil_F", "Primary", "Trans", "Battery", "F_Tire", "R_Tire", "L_Brake", "H_Brake"]

# --- 2. AUTHENTICATION (The Gatekeeper) ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Garage Hub 🛠️")
    pin_input = st.text_input("Enter Access PIN", type="password")
    if st.button("Unlock System"):
        if pin_input == ACCESS_PIN:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# --- 3. DATA HELPERS ---
def get_df(file):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=COLS)

def save_df(df, file):
    df.to_csv(file, index=False)

# --- 4. SIDEBAR (CRITICAL: This defines active_unit first) ---
with st.sidebar:
    st.title("Garage Hub")
    fleet = ["2012 GMC Terrain", "2018 Hyundai Kona", "2020 Street Bob"]
    # This creates the variable that was causing the error:
    active_unit = st.selectbox("Select Vehicle", fleet)
    st.divider()
    st.write(f"Logged in: **Antonino**")

# --- 5. MAIN INTERFACE ---
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader(f"Manage: {active_unit}")
    st.write("📑 **Legal/Papers**")
    
    doc = st.selectbox("Doc Type", ["Insurance", "Registration", "Safety"])
    
    # Inputs for the log
    l_cost = st.number_input("Cost ($)", min_value=0.0, step=1.0, key=f"cost_{active_unit}")
    l_km = st.number_input("Current KM", min_value=0, step=100, key=f"km_{active_unit}")
    
    extra_n = st.text_area("Notes", placeholder="Specific details...", key=f"notes_{active_unit}")
    l_notes = f"{doc} Update | {extra_n}" if extra_n else f"{doc} Update"
    
    gal = st.file_uploader("Photo/Receipt", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}")
    
    if st.button("💾 Save Entry"):
        p_p = ""
        if gal:
            if not os.path.exists(IMG): os.makedirs(IMG)
            p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            Image.open(gal).save(p_p)
        
        # We fill all 17 columns to match your COLS list
        new_data = [[
            datetime.now().strftime("%Y-%m-%d"), active_unit, "Legal", l_cost, l_km, "", 
            l_notes, p_p, "", "", "", "", "", "", "", "", ""
        ]]
        
        new_row = pd.DataFrame(new_data, columns=COLS)
        save_df(pd.concat([get_df(LOG), new_row], ignore_index=True), LOG)
        st.success("Entry Saved to Garage Hub!")
        st.rerun()

with c2:
    tab1, tab2 = st.tabs(["📊 Service History", "💰 Expense Tracker"])
    hist = get_df(LOG)
    
    if not hist.empty:
        u_h = hist[hist["Unit"] == active_unit].sort_values("Date", ascending=False)
        
        with tab1:
            st.dataframe(u_h[["Date", "Type", "Cost", "Notes"]], use_container_width=True, hide_index=True)
            if st.toggle("🔓 Edit Mode"):
                edited_df = st.data_editor(u_h, use_container_width=True, hide_index=True, key=f"edit_{active_unit}")
                if st.button("Apply Changes"):
                    save_df(pd.concat([hist[~hist.index.isin(u_h.index)], edited_df], ignore_index=True), LOG)
                    st.rerun()

        with tab2:
            st.subheader("Investment Summaries")
            mc1, mc2, mc3 = st.columns(3)
            
            # Using your currency formatting
            mc1.metric("Total for Unit", f"${u_h['Cost'].sum():,.2f}")
            mc2.metric("Legal/Fees", f"${u_h[u_h['Type'] == 'Legal']['Cost'].sum():,.2f}")
            mc3.metric("Service Count", len(u_h))
            
            st.divider()
            st.dataframe(u_h[["Date", "Type", "Cost"]].style.format({"Cost": "${:,.2f}"}), use_container_width=True)
