import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Garage Hub")

# MASTER CODE - CONDENSED TO PREVENT TRUNCATION
garage_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #0b0b0b; color: #fff; font-family: sans-serif; margin: 0; display: flex; height: 100vh; justify-content: center; align-items: center; }
        #login { text-align: center; background: #111; padding: 40px; border-radius: 15px; border: 1px solid #ff9d00; }
        .pin-in { background: #222; border: 1px solid #444; color: #ff9d00; font-size: 2rem; text-align: center; width: 140px; padding: 10px; margin: 20px 0; border-radius: 10px; }
        #dash { display: none; width: 100%; height: 100%; flex-direction: row; }
        #side { width: 280px; background: #111; height: 100%; border-right: 1px solid #333; padding: 25px; box-sizing: border-box; display: flex; flex-direction: column; }
        .logo { font-size: 1.4rem; font-weight: 900; color: #ff9d00; border-bottom: 2px solid #ff9d00; padding-bottom: 5px; margin-bottom: 20px; text-transform: uppercase; }
        .lbl { color: #555; font-size: 0.7rem; text-transform: uppercase; margin: 15px 0 5px 0; }
        .item { display: block; width: 100%; padding: 10px; color: #bbb; background: none; border: none; text-align: left; cursor: pointer; border-radius: 6px; }
        .item:hover { background: #222; color: #ff9d00; }
        .vault { margin-top: auto; background: #181818; border-radius: 8px; border: 1px solid #333; }
        summary { padding: 10px; color: #ff9d00; font-weight: bold; cursor: pointer; }
        #main { flex: 1; padding: 40px; background: radial-gradient(at top left, #1a1a1a, #0b0b0b); overflow-y: auto; }
        .card { background: #141414; padding: 30px; border-radius: 15px; border: 1px solid #333; max-width: 600px; }
        input { width: 100%; padding: 12px; background: #222; border: 1px solid #444; color: white; border-radius: 6px; margin-bottom: 15px; box-sizing: border-box; }
        .btn { background: #ff9d00; color: #000; border: none; padding: 15px; width: 100%; font-weight: bold; cursor: pointer; border-radius: 6px; }
    </style>
</head>
<body>
    <div id="login">
        <h1 style="color:#ff9d00; margin:0;">GARAGE HUB</h1>
        <input type="password" id="pin" class="pin-in" maxlength="4" placeholder="****">
        <button class="btn" onclick="check()">UNLOCK</button>
    </div>
    <div id="dash">
        <div id="side">
            <div class="logo">GARAGE HUB</div>
            <div class="lbl">Your Fleet</div>
            <div id="fleet">
                <button class="item">2012 GMC Terrain</button>
                <button class="item">2018 Hyundai Kona</button>
                <button class="item">2020 Street Bob</button>
            </div>
            <div class="lbl">Maintenance</div>
            <button class="item">Oil Change (3-Hole)</button>
            <button class="item">Tire Service</button>
            <div class="lbl">Legal</div>
            <button class="item">License & Docs</button>
            <details class="vault">
                <summary>📁 Records</summary>
                <button class="item" style="padding-left:25px;">History</button>
                <button class="item" style="padding-left:25px;">Expenses</button>
            </details>
        </div>
        <div id="main">
            <div class="card">
                <h2 style="color:#ff9d00; margin-top:0;">Vehicle License</h2>
                <label style="color:#666;">Renewal Date</label><input type="date">
                <label style="color:#666;">Fee ($)</label><input type="number" placeholder="0.00">
                <label style="color:#666;">Document</label><input type="file">
                <button class="btn">UPDATE RECORDS</button>
            </div>
        </div>
    </div>
    <script>
        function check() {
            if (document.getElementById('pin').value === "1234") {
                document.getElementById('login').style.display = 'none';
                document.getElementById('dash').style.display = 'flex';
                document.body.style.display = 'block';
            } else { alert("INVALID PIN"); }
        }
    </script>
</body>
</html>
"""

components.html(garage_code, height=1000, scrolling=True)
