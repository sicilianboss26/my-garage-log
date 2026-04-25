import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 1. SETUP & CUSTOM THEME ---
st.set_page_config(page_title="The Garage Hub", page_icon="🔧", layout="wide")

# CSS block for the unified red-bordered terminal
st.markdown("""
    <style>
    .main { background-color: #1a1c1e; }
    .stApp { background-color: #1a1c1e; color: #e0e0e0; }
    
    .login-card {
        border: 2px solid #ff4b4b;
        border-radius: 15px;
        background-color: #262730;
        padding: 40px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        margin-top: 50px;
    }
    .shop-title {
        color: #ff4b4b;
        font-size: 28px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        line-height: 1.2;
    }
    .shop-subtitle {
        color: #888;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    div[data-baseweb="input"] { background-color: #1a1c1e !important; border-radius: 8px !important; }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border: none;
        font-weight: bold;
        height: 3.5em;
        margin-top: 10px;
    }
    .stButton>button:hover { background-color: #ff3333; color: white; border: none; }
    h1, h2, h3 { color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SECURE LOGIN SCREEN ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.8, 1])
    with center_col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="shop-title">Antonino\'s</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-title" style="font-size: 36px;">Garage Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="shop-subtitle">SECURE SYSTEM ENTRY | V2.6</div>', unsafe_allow_html=True)
        
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
LOG, FLEET, IMG = "maintenance_log.csv", "fleet_database.csv", "service
