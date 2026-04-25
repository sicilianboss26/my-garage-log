import streamlit as st
import streamlit.components.v1 as components

# 1. This keeps the dashboard wide so the sidebar looks right
st.set_page_config(layout="wide", page_title="Garage Hub")

# 2. We wrap EVERYTHING in triple quotes so Python doesn't throw a SyntaxError
garage_hub_master = """
<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        /* THEME: Dark Industrial Restoration */
        body {
            background-color: #0b0b0b;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            display: flex;
            height: 100vh;
        }

        /* Fixed Sidebar */
        #sidebar {
            width: 280px;
            background-color: #111111;
            height: 100%;
            border-right: 1px solid #333;
            padding: 40px 20px;
            box-sizing: border-box;
            position: fixed;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 900;
            color: #ff9d00;
            text-transform: uppercase;
            border-bottom: 2px solid #ff9d00;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }

        .nav-label {
            color: #555;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 25px 0 10px 5px;
        }

        .nav-item {
            display: block;
            width: 100%;
            padding: 12px;
            color: #bbb;
            background: none;
            border: none;
            text-align: left;
            cursor: pointer;
            border-radius: 6px;
            transition: 0.2s;
        }

        .nav-item:hover {
            background: #222;
            color: #ff9d00;
        }

        /* THE NEW RECORDS VAULT (Hidden/Collapsible) */
        .records-vault {
            margin-top: 15px;
            background: #181818;
            border-radius: 8px;
            overflow: hidden;
        }

        summary {
            padding: 12px;
            color: #ff9d00;
            font-weight: bold;
            cursor: pointer;
            list-style: none;
        }

        /* MAIN CONTENT AREA */
        #main {
            margin-left: 280px;
            padding: 60px;
            width: calc(100% - 280px);
            background: radial-gradient(circle at top left, #1a1a1a, #0b0b0b);
        }

        .card {
            background: #141414;
            padding: 40px;
            border-radius: 15px;
            border: 1px solid #333;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        h2 { color: #ff9d00; margin-top: 0; }

        input {
            width: 100%;
            padding: 12px;
            background: #222;
            border: 1px solid #444;
            color: white;
            border-radius: 6px;
            margin: 10px 0 20px 0;
            box-sizing: border-box;
        }

        .save-btn {
            background: #ff9d00;
            color: black;
            border: none;
            padding: 15px;
            width: 100%;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            text-transform: uppercase;
        }
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="logo">GARAGE HUB</div>
        
        <div class="nav-label">Maintenance</div>
        <button class="nav-item">Battery Repairs</button>
        <button class="nav-item">Oil Changes</button>
        <button class="nav-item">Tire Service</button>

        <div class="nav-label">Legal</div>
        <button class="nav-item">License & Docs</button>

        <details class="records-vault">
            <summary>📁 Records Archive</summary>
            <button class="nav-item" style="padding-left: 30px;">History</button>
            <button class="nav-item" style="padding-left: 30px;">Expense Tracker</button>
        </details>
    </div>

    <div id="main">
        <div class="card">
            <h2>Vehicle License</h2>
            <label style="color: #888;">Renewal Expiry Date</label>
            <input type="date">
            
            <label style="color: #888;">Total Fee ($)</label>
            <input type="number" placeholder="0.00">
            
            <label style="color: #888;">Digital Copy (PDF/JPG)</label>
            <input type="file">
            
            <button class="save-btn">Save to Legal Folder</button>
        </div>
    </div>

</body>
</html>
"""

# 3. This is the command that makes it show up in Streamlit
components.html(garage_hub_master, height=1000, scrolling=True)
