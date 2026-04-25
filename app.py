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
    
    /* Unified Terminal Container */
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

    /* Input & Button Theme */
    div[data-
