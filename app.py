from flask import Flask, render_template_string, request, jsonify
import os
import subprocess
import json
import time
import boto3
from datetime import datetime

app = Flask(__name__)

# --- GLOBAL CONFIG & FINOPS DATA ---
PROFIT_MODE = False 
MUMBAI_ON_DEMAND_RATE = 0.0208 # Fixed rate for ap-south-1

# Initialize AWS Client for Real-Time Spot Prices
# Ensure your local terminal is logged into AWS via 'aws configure'
ec2_client = boto3.client('ec2', region_name='us-east-1')

def get_real_spot_price():
    """Fetches actual market data from AWS us-east-1"""
    try:
        response = ec2_client.describe_spot_price_history(
            InstanceTypes=['t3.micro'],
            ProductDescriptions=['Linux/UNIX'],
            StartTime=datetime.now(),
            MaxResults=1
        )
        return float(response['SpotPriceHistory'][0]['SpotPrice'])
    except:
        return 0.0035 # Fallback rate if API is throttled

def get_terraform_data():
    """Pulls current Infrastructure IPs from the S3 Remote Backend"""
    try:
        result = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True)
        outputs = json.loads(result.stdout)
        return {
            "primary_ip": outputs['primary_server_ip']['value'],
            "backup_ip": outputs['backup_server_ip']['value']
        }
    except:
        return {"primary_ip": "0.0.0.0", "backup_ip": "0.0.0.0"}

def check_latency(ip):
    """Measures physical response time to the cloud instances"""
    if ip == "0.0.0.0": return (False, 1000.0)
    start = time.time()
    param = "-n" if os.name == 'nt' else "-c"
    response = os.system(f"ping {param} 1 {ip} > nul")
    end = time.time()
    l_val = round((end - start) * 1000, 2)
    return (response == 0, l_val if response == 0 else 1000.0)

@app.route('/toggle_profit', methods=['POST'])
def toggle_profit():
    """API endpoint to flip the Profit Mode switch"""
    global PROFIT_MODE
    data = request.get_json()
    PROFIT_MODE = data.get('enabled', False)
    return jsonify({"status": "success", "profit_mode": PROFIT_MODE})

@app.route('/')
def home():
    global PROFIT_MODE
    data = get_terraform_data()
    va_spot_rate = get_real_spot_price()
    
    mumbai_ok, mumbai_lat = check_latency(data['primary_ip'])
    usa_ok, usa_lat = check_latency(data['backup_ip'])
    
    # --- FINOPS ORCHESTRATION LOGIC ---
    # Choice 1: Profit Mode Active + Virginia is Cheaper + Virginia is Healthy
    if PROFIT_MODE and va_spot_rate < MUMBAI_ON_DEMAND_RATE and usa_ok:
        status, region, current_ip, accent = "COST OPTIMIZED", "US-EAST-1 (VIRGINIA)", data['backup_ip'], "#00d4ff"
        current_lat = usa_lat
        savings = round(((MUMBAI_ON_DEMAND_RATE - va_spot_rate) / MUMBAI_ON_DEMAND_RATE) * 100, 1)
        cost_txt, savings_txt = f"${va_spot_rate}/hr", f"{savings}%"

    # Choice 2: Standard Operation (Mumbai is healthy)
    elif mumbai_ok:
        status, region, current_ip, accent = "OPERATIONAL", "ASIA-SOUTH-1 (MUMBAI)", data['primary_ip'], "#00ff88"
        cost_txt, savings_txt = f"${MUMBAI_ON_DEMAND_RATE}/hr", "0%"
        current_lat = mumbai_lat
    
    # Choice 3: Emergency Failover (Mumbai is down)
    else:
        current_lat = usa_lat
        status, region, current_ip, accent = "FAILOVER ACTIVE", "US-EAST-1 (VIRGINIA)", data['backup_ip'], "#ff4444"
        savings = round(((MUMBAI_ON_DEMAND_RATE - va_spot_rate) / MUMBAI_ON_DEMAND_RATE) * 100, 1)
        cost_txt, savings_txt = f"${va_spot_rate}/hr", f"{savings}%"

    # --- UPDATED FRONTEND TEMPLATE (STEP 4) ---
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Orchestrator NOC</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {{ --accent: {accent}; --bg: #0b0e14; }}
            body {{ background: var(--bg); color: #c9d1d9; font-family: 'Inter', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }}
            .sidebar {{ width: 350px; background: #161b22; border-right: 1px solid #30363d; padding: 20px; }}
            .main {{ flex-grow: 1; padding: 30px; display: flex; flex-direction: column; overflow-y: auto; }}
            .card {{ background: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
            .stat-value {{ font-size: 22px; font-weight: bold; color: var(--accent); }}
            .label {{ font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
            
            /* Toggle Switch Design */
            .switch {{ position: relative; display: inline-block; width: 44px; height: 22px; }}
            .switch input {{ opacity: 0; width: 0; height: 0; }}
            .slider {{ position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #30363d; transition: .4s; border-radius: 34px; }}
            .slider:before {{ position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }}
            input:checked + .slider {{ background-color: #00d4ff; }}
            input:checked + .slider:before {{ transform: translateX(22px); }}

            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left; }}
            th {{ color: #8b949e; font-size: 11px; padding: 10px; border-bottom: 1px solid #30363d; }}
            td {{ padding: 15px 10px; font-size: 14px; border-bottom: 1px solid #30363d; }}
            .status-indicator {{ height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3 style="color:white; margin-bottom:25px;">NETWORK ANALYTICS</h3>
            
            <!-- STEP 4: PROFIT TOGGLE UI SECTION -->
            <div class="card" style="border: 1px solid #00d4ff44; background: linear-gradient(145deg, #1c2128, #0d1117);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p class="label" style="margin:0; color:#00d4ff;">Profitability Mode</p>
                    <label class="switch">
                        <input type="checkbox" id="profitToggle" {"checked" if PROFIT_MODE else ""} onchange="updateProfitMode()">
                        <span class="slider"></span>
                    </label>
                </div>
                <p style="font-size:11px; color:#8b949e; margin-top:10px;">Routes traffic to the cheapest healthy region based on live AWS spot rates.</p>
            </div>

            <div class="card" style="background: #0d1117;">
                <p class="label">Primary Latency (ms)</p>
                <div style="height: 180px;"><canvas id="latencyChart"></canvas></div>
            </div>
            <div class="card">
                <p class="label">FinOps Realized Savings</p>
                <div style="font-size: 2.5em; color: #00ff88; font-weight: bold;">{savings_txt}</div>
            </div>
        </div>

        <div class="main">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <div style="display:flex; align-items:center;">
                    <div style="height:12px; width:12px; background:{accent}; border-radius:50%; box-shadow: 0 0 10px {accent}; margin-right:15px;"></div>
                    <span style="font-size: 1.8em; font-weight: bold; color: white;">SYSTEM {status}</span>
                </div>
                <div style="text-align: right;">
                    <p class="label" style="margin:0;">Active Ingress</p>
                    <div style="color: white; font-weight: bold;">{region}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div class="card"><p class="label">IP Address</p><div class="stat-value">{current_ip}</div></div>
                <div class="card"><p class="label">Response Time</p><div class="stat-value">{current_lat} ms</div></div>
                <div class="card"><p class="label">Estimated Rate</p><div class="stat-value">{cost_txt}</div></div>
            </div>

            <div class="card" style="flex-grow: 1;">
                <p class="label" style="margin:0;">Multi-Region Health Check Distribution</p>
                <table>
                    <thead>
                        <tr>
                            <th>REGION</th>
                            <th>ENDPOINT</th>
                            <th>MARKET RATE</th>
                            <th>STATUS</th>
                            <th>LATENCY</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>ASIA-SOUTH-1 (Mumbai)</td>
                            <td><code>{data['primary_ip']}</code></td>
                            <td>${MUMBAI_ON_DEMAND_RATE}/hr</td>
                            <td><span class="status-indicator" style="background:{'#00ff88' if mumbai_ok else '#ff4444'}"></span>{'Healthy' if mumbai_ok else 'Unreachable'}</td>
                            <td>{mumbai_lat} ms</td>
                        </tr>
                        <tr>
                            <td>US-EAST-1 (Virginia)</td>
                            <td><code>{data['backup_ip']}</code></td>
                            <td style="color:#00d4ff;">${va_spot_rate}/hr</td>
                            <td><span class="status-indicator" style="background:{'#00ff88' if usa_ok else '#ff4444'}"></span>{'Healthy' if usa_ok else 'Unreachable'}</td>
                            <td>{usa_lat} ms</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Sends the toggle state to Flask backend
            function updateProfitMode() {{
                const isEnabled = document.getElementById('profitToggle').checked;
                fetch('/toggle_profit', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ enabled: isEnabled }})
                }}).then(() => {{
                    // Quick refresh to show the new "COST OPTIMIZED" status
                    location.reload(); 
                }});
            }}

            // Latency History Logic
            const currentLat = parseFloat("{current_lat}");
            let history = JSON.parse(localStorage.getItem('noc_latency_log') || '[]');
            history.push(currentLat);
            if (history.length > 20) history.shift();
            localStorage.setItem('noc_latency_log', JSON.stringify(history));

            const ctx = document.getElementById('latencyChart').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: history.map((_, i) => ""),
                    datasets: [{{
                        data: history,
                        borderColor: '{accent}',
                        backgroundColor: '{accent}22',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: '#30363d' }}, ticks: {{ display: false }} }},
                        x: {{ grid: {{ display: false }} }}
                    }}
                }}
            }});

            // Refresh page every 4 seconds to simulate live monitoring
            setTimeout(() => {{ window.location.reload(); }}, 4000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, port=5000)