import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# --- PIN CONFIGURATION ---
ACCESS_PIN = "1234"

# Initialize Login State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- LOGIN SCREEN ---
if not st.session_state["authenticated"]:
    st.title("Garage Hub")
    pin_input = st.text_input("Enter Access PIN", type="password")
    
    if st.button("Unlock System"):
        if pin_input == ACCESS_PIN:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Access Denied: Invalid PIN")
    st.stop() # Stops the rest of the app from running until logged in

# --- YOUR ORIGINAL DASHBOARD STARTS HERE ---
# (The code below only runs if authenticated is True)

# Note: Ensure your 'active_unit', 'LOG', 'COLS', etc., are defined above this snippet
st.write("📑 **Legal/Papers**")
doc = st.selectbox("Doc Type", ["Insurance", "Registration", "Safety"]) 
l_notes = f"{doc} Update" 
extra_n = st.text_area("Notes", placeholder="Specific details...", key=f"notes_{active_unit}") 
l_notes = f"{l_notes} | {extra_n}" if extra_n else l_notes 

gal = st.file_uploader("Photo/Receipt", type=['jpg', 'jpeg', 'png'], key=f"g_{active_unit}") 

if st.button("💾 Save Entry"):
    p_p = "" 
    if gal:
        # Create directory if it doesn't exist
        if not os.path.exists(IMG): os.makedirs(IMG)
        p_p = f"{IMG}/{active_unit.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg" 
        Image.open(gal).save(p_p) 
    
    # Assuming l_t, l_cost, l_km, nxt, o_g, o_f, pri, tra, bat, f_sz, r_sz, l_b, h_b are defined earlier in your script
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
