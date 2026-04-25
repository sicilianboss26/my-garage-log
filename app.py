<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Garage Hub | Tech Dashboard</title>
    <style>
        /* THEME: Dark Industrial (Antonino's Shop Style) */
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            display: flex;
        }

        /* Sidebar Navigation */
        #sidebar {
            width: 260px;
            background-color: #1a1a1a;
            height: 100vh;
            padding: 20px;
            border-right: 2px solid #333;
            box-sizing: border-box;
            position: fixed;
        }

        .category-label {
            color: #888;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 20px 0 10px 0;
            display: block;
        }

        .nav-btn {
            background: none;
            border: none;
            color: #bbb;
            width: 100%;
            text-align: left;
            padding: 10px;
            font-size: 1rem;
            cursor: pointer;
            border-radius: 5px;
            transition: 0.2s;
        }

        .nav-btn:hover {
            background-color: #333;
            color: #ff9d00;
        }

        /* RECORDS CATEGORY (The Vault) */
        .records-vault {
            margin-top: 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
        }

        .records-vault summary {
            padding: 10px;
            cursor: pointer;
            color: #ff9d00;
            font-weight: bold;
            list-style: none;
            outline: none;
        }

        .records-vault summary:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        /* MAIN CONTENT AREA */
        #main-content {
            margin-left: 260px;
            padding: 40px;
            width: 100%;
        }

        .module-card {
            background: #1e1e1e;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #333;
            max-width: 600px;
        }

        h2 { color: #ff9d00; margin-top: 0; }

        /* LICENSE FORM ELEMENTS */
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #aaa; }
        input[type="text"], input[type="date"], input[type="number"], input[type="file"] {
            width: 100%;
            padding: 10px;
            background: #2a2a2a;
            border: 1px solid #444;
            color: white;
            border-radius: 5px;
            box-sizing: border-box;
        }

        .save-btn {
            background: #ff9d00;
            color: #000;
            border: none;
            padding: 12px 20px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            width: 100%;
        }

        .save-btn:hover { background: #e68a00; }
    </style>
</head>
<body>

    <div id="sidebar">
        <h2 style="font-size: 1.2rem; border-bottom: 1px solid #333; padding-bottom: 10px;">GARAGE HUB</h2>
        
        <span class="category-label">Maintenance</span>
        <button class="nav-btn" onclick="showModule('battery')">Battery Repairs</button>
        <button class="nav-btn" onclick="showModule('oil')">Oil Changes</button>
        <button class="nav-btn" onclick="showModule('tires')">Tire Service</button>

        <span class="category-label">Legal</span>
        <button class="nav-btn" onclick="showModule('license')">License & Docs</button>

        <details class="records-vault">
            <summary>📁 Records</summary>
            <button class="nav-btn" onclick="showModule('history')">Service History</button>
            <button class="nav-btn" onclick="showModule('expenses')">Expense Tracker</button>
        </details>
    </div>

    <div id="main-content">
        
        <div id="license-module" class="module-card">
            <h2>Vehicle License</h2>
            <p style="color:#888; font-size: 0.9rem;">Management for renewals and legal documentation.</p>
            
            <div class="form-group">
                <label>Renewal Date</label>
                <input type="date" id="ren-date">
            </div>

            <div class="form-group">
                <label>Renewal Fee ($)</label>
                <input type="number" id="ren-fee" placeholder="0.00">
            </div>

            <div class="form-group">
                <label>Digital Copy (Stored in /Legal/)</label>
                <input type="file" id="license-file" accept="image/*,.pdf">
            </div>

            <button class="save-btn" onclick="saveLicense()">Update License Records</button>
        </div>

        <div id="other-modules" style="display:none; margin-top: 20px; color: #666;">
            Module content will load here...
        </div>

    </div>

    <script>
        function showModule(moduleName) {
            // Simple logic to switch between views
            const card = document.getElementById('license-module');
            const placeholder = document.getElementById('other-modules');

            if(moduleName === 'license') {
                card.style.display = 'block';
                placeholder.style.display = 'none';
            } else {
                card.style.display = 'none';
                placeholder.style.display = 'block';
                placeholder.innerText = moduleName.toUpperCase() + " Module Active - Load UI for " + moduleName;
            }
        }

        function saveLicense() {
            const date = document.getElementById('ren-date').value;
            const fee = document.getElementById('ren-fee').value;
            const file = document.getElementById('license-file').value;

            if(!date || !fee) {
                alert("Please fill in the date and fee.");
                return;
            }

            console.log("Saving to Legal Folder:", { date, fee, file });
            alert("License information saved successfully in the Legal section.");
        }
    </script>
</body>
</html>
