import streamlit as st
import streamlit.components.v1 as components

# We wrap the entire HTML/CSS/JS code in a triple-quoted string
garage_hub_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: sans-serif; }
        .category-label { color: #888; font-size: 0.8rem; text-transform: uppercase; margin-top: 20px; }
        .nav-btn { background: none; border: none; color: #bbb; width: 100%; text-align: left; padding: 10px; cursor: pointer; }
        .nav-btn:hover { color: #ff9d00; }
        .records-vault { margin-top: 15px; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 5px; }
        summary { cursor: pointer; color: #ff9d00; font-weight: bold; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2 style="color: #ff9d00;">GARAGE HUB</h2>
        <div class="category-label">Maintenance</div>
        <button class="nav-btn">Battery Repairs</button>
        <button class="nav-btn">Oil Changes</button>
        <button class="nav-btn">Tire Service</button>
        
        <div class="category-label">Legal</div>
        <button class="nav-btn">License & Docs</button>

        <details class="records-vault">
            <summary>📁 Records</summary>
            <button class="nav-btn">Service History</button>
            <button class="nav-btn">Expense Tracker</button>
        </details>
    </div>
</body>
</html>
"""

# This line tells Python to render the HTML string
components.html(garage_hub_code, height=800, scrolling=True)
