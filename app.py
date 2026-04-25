<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        :root {
            --accent: #ff9d00;
            --bg-dark: #0f0f0f;
            --panel: #161616;
            --text-dim: #888;
        }

        body {
            background: var(--bg-dark);
            color: #fff;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            display: flex;
        }

        /* SIDEBAR - Exactly as built yesterday */
        #sidebar {
            width: 280px;
            background: var(--panel);
            height: 100vh;
            border-right: 1px solid #333;
            padding: 40px 20px;
            position: fixed;
        }

        .logo {
            font-size: 1.6rem;
            font-weight: 900;
            color: var(--accent);
            text-transform: uppercase;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 10px;
            margin-bottom: 30px;
        }

        .section-label {
            color: var(--text-dim);
            font-size: 0.7rem;
            text-transform: uppercase;
            margin: 20px 0 10px 0;
        }

        .nav-btn {
            background: none;
            border: none;
            color: #bbb;
            width: 100%;
            text-align: left;
            padding: 12px;
            cursor: pointer;
            border-radius: 6px;
            font-size: 1rem;
        }

        .nav-btn:hover {
            background: #252525;
            color: var(--accent);
        }

        /* NEW RECORDS DRAWER */
        .records-drawer {
            margin-top: 15px;
            background: #1d1d1d;
            border-radius: 8px;
        }

        summary {
            padding: 12px;
            cursor: pointer;
            color: var(--accent);
            font-weight: bold;
            list-style: none;
        }

        /* MAIN CONTENT */
        #main {
            margin-left: 280px;
            padding: 60px;
            width: 100%;
        }

        .card {
            background: var(--panel);
            padding: 40px;
            border-radius: 12px;
            border: 1px solid #333;
            max-width: 650px;
        }

        h2 { color: var(--accent); margin-top: 0; }

        input {
            width: 100%;
            padding: 12px;
            background: #252525;
            border: 1px solid #444;
            color: white;
            border-radius: 6px;
            margin: 10px 0 20px 0;
        }

        .save-btn {
            background: var(--accent);
            color: #000;
            border: none;
            padding: 15px;
            width: 100%;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
        }
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="logo">Garage Hub</div>
        
        <div class="section-label">Maintenance</div>
        <button class="nav-btn">Battery Repairs</button>
        <button class="nav-btn">Oil Changes</button>
        <button class="nav-btn">Tire Service</button>

        <div class="section-label">Legal</div>
        <button class="nav-btn">License & Docs</button>

        <details class="records-drawer">
            <summary>📁 Records Archive</summary>
            <button class="nav-btn" style="padding-left: 25px;">History</button>
            <button class="nav-btn" style="padding-left: 25px;">Expense Tracker</button>
        </details>
    </div>

    <div id="main">
        <div class="card">
            <h2>Vehicle License</h2>
            <label>Renewal Date</label>
            <input type="date">
            
            <label>Renewal Fee ($)</label>
            <input type="number" placeholder="0.00">
            
            <label>Digital Copy (Stored in /Legal/Docs/)</label>
            <input type="file">
            
            <button class="save-btn">UPDATE LEGAL RECORDS</button>
        </div>
    </div>

</body>
</html>
