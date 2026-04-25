import streamlit as st
import streamlit.components.v1 as components

# Setting page to wide mode to fit your sidebar
st.set_page_config(layout="wide")

# This is the "Engine" that holds your design
garage_layout = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background-color: #121212; color: #e0e0e0; font-family: sans-serif; margin: 0; }
        .sidebar { width: 250px; background: #1a1a1a; height: 100vh; padding: 20px; border-right: 1px solid #333; position: fixed; }
        .content { margin-left: 270px; padding: 20px; }
        .orange { color: #ff9d00; }
        .btn { background: none; border: none; color: #bbb; display: block; padding: 10px 0; cursor: pointer; width: 100%; text-align: left; }
        .btn:hover { color: #ff9d00; }
        details { margin-top: 20px; background: #222; padding: 10px; border-radius: 5px; }
        summary { cursor: pointer; font-weight: bold; color: #ff9d00; }
        input { width: 100%; padding: 8px; margin: 10px 0; background: #333; border: 1px solid #444; color: white; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2 class="orange">GARAGE HUB</h2>
        <p style="font-size: 10px; color: #666;">MAINTENANCE</p>
        <button class="btn">Battery Repairs</button>
        <button class="btn">Oil Changes</button>
        <button class="btn">Tire Service</button>
        
        <p style="font-size: 10px; color: #666;">LEGAL</p>
        <button class="btn">License & Docs</button>

        <details>
            <summary>📁 Records</summary>
            <button class="btn">Service History</button>
            <button class="btn">Expense Tracker</button>
        </details>
    </div>

    <div class="content">
        <h1 class="orange">Vehicle License</h1>
        <label>Renewal Date</label>
        <input type="date">
        <label>Renewal Fee</label>
        <input type="number" placeholder="$0.00">
        <label>Document Upload</label>
        <input type="file">
        <button style="background: #ff9d00; border: none; padding: 10px; width: 100%; font-weight: bold; cursor: pointer;">SAVE TO LEGAL FOLDER</button>
    </div>
</body>
</html>
"""

# Render the code
components.html(garage_layout, height=1000)
