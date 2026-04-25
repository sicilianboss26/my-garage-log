import streamlit as st
import streamlit.components.v1 as components

# Forces the app to use the full width of your screen
st.set_page_config(layout="wide", page_title="Garage Hub")

# The Full Industrial Dashboard Code
garage_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            background-color: #0f0f0f; 
            color: #ffffff; 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            margin: 0; 
            overflow-x: hidden;
        }
        
        /* Sidebar Restored */
        .sidebar {
            width: 280px;
            background-color: #161616;
            height: 100vh;
            position: fixed;
            border-right: 1px solid #333;
            padding: 30px 20px;
            box-sizing: border-box;
        }

        .logo {
            color: #ff9d00;
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 40px;
            border-bottom: 2px solid #ff9d00;
            padding-bottom: 10px;
        }

        .nav-section {
            margin-bottom: 25px;
        }

        .section-title {
            color: #666;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 15px;
            display: block;
        }

        .nav-item {
            display: block;
            width: 100%;
            padding: 12px;
            color: #aaa;
            text-decoration: none;
            background: none;
            border: none;
            text-align: left;
            font-size: 1rem;
            cursor: pointer;
            border-radius: 6px;
            transition: 0.3s;
            margin-bottom: 5px;
        }

        .nav-item:hover {
            background: #252525;
            color: #ff9d00;
        }

        /* The New Records Vault */
        details.records-section {
            background: #1d1d1d;
            border-radius: 8px;
            padding: 5px;
            margin-top: 10px;
        }

        summary {
            list-style: none;
            padding: 10px;
            cursor: pointer;
            color: #ff9d00;
            font-weight: bold;
        }

        /* Main Display Area */
        .main-container {
            margin-left: 280px;
            padding: 60px;
            max-width: 900px;
        }

        .card {
            background: #1a1a1a;
            padding: 40px;
            border-radius: 15px;
            border: 1px solid #333;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        h1 { color: #ff9d00; margin-top: 0; font-size: 2.2rem; }

        .input-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #888; font-size: 0.9rem; }
        
        input {
            width: 100%;
            padding: 12px;
            background: #252525;
            border: 1px solid #444;
            color: white;
            border-radius: 8px;
            font-size: 1rem;
        }

        .btn-save {
            background: #ff9d00;
            color: black;
            border: none;
            padding: 15px 30px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">GARAGE HUB</div>
        
        <div class="nav-section">
            <span class="section-title">Maintenance</span>
            <button class="nav-item">Battery Repairs</button>
            <button class="nav-item">Oil Changes</button>
            <button class="nav-item">Tire Service</button>
        </div>

        <div class="nav-section">
            <span class="section-title">Legal</span>
            <button class="nav-item">License & Docs</button>
        </div>

        <details class="records-section">
            <summary>📁 RECORDS</summary>
            <button class="nav-item">Service History</button>
            <button class="nav-item">Expense Tracker</button>
        </details>
    </div>

    <div class="main-container">
        <div class="card">
            <h1>Vehicle License</h1>
            <div class="input-group">
                <label>Renewal Date</label>
                <input type="date">
            </div>
            <div class="input-group">
                <label>Renewal Fee</label>
                <input type="number" placeholder="$0.00">
            </div>
            <div class="input-group">
                <label>Document Upload (PDF/Image)</label>
                <input type="file">
            </div>
            <button class="btn-save">Save to Legal Folder</button>
        </div>
    </div>
</body>
</html>
"""

# Rendering it with enough height to show the whole sidebar
components.html(garage_html, height=900, scrolling=True)
