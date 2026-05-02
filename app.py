from flask import Flask, render_template_string
import os
import subprocess
import json
import time

app = Flask(__name__)

# Performance Data & Rates
MUMBAI_RATE = 0.0116 
USA_SPOT_RATE = 0.0035

def get_terraform_data():
    try:
        # Pulling live data from the Orchestration Layer
        result = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True)
        outputs = json.loads(result.stdout)
        return {
            "primary_ip": outputs['primary_server_ip']['value'],
            "backup_ip": outputs['backup_server_ip']['value']
        }
    except:
        return {"primary_ip": "0.0.0.0", "backup_ip": "0.0.0.0"}

def check_latency(ip):
    start = time.time()
    param = "-n" if os.name == 'nt' else "-c"
    response = os.system(f"ping {param} 1 {ip} > nul")
    end = time.time()
    l_val = round((end - start) * 1000, 2)
    return (response == 0, l_val if response == 0 else 1000.0)

@app.route('/')
def home():
    data = get_terraform_data()
    # Check both regions for the comparison table
    mumbai_ok, mumbai_lat = check_latency(data['primary_ip'])
    usa_ok, usa_lat = check_latency(data['backup_ip'])
    
    # Logic for Main Status
    if mumbai_ok:
        status, region, current_ip, accent = "OPERATIONAL", "ASIA-SOUTH-1 (MUMBAI)", data['primary_ip'], "#00ff88"
        cost_txt, savings_txt = f"${MUMBAI_RATE}/hr", "0%"
        current_lat = mumbai_lat
    else:
        current_lat = usa_lat
        status, region, current_ip, accent = "FAILOVER ACTIVE", "US-EAST-1 (VIRGINIA)", data['backup_ip'], "#ff4444"
        savings = round(((MUMBAI_RATE - USA_SPOT_RATE) / MUMBAI_RATE) * 100, 1)
        cost_txt, savings_txt = f"${USA_SPOT_RATE}/hr", f"{savings}%"

    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cloud Orchestrator NOC</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <style>
            :root {{ --accent: {accent}; --bg: #0b0e14; }}
            body {{ background: var(--bg); color: #c9d1d9; font-family: 'Inter', sans-serif; margin: 0; display: flex; height: 100vh; overflow: hidden; }}
            .sidebar {{ width: 350px; background: #161b22; border-right: 1px solid #30363d; padding: 20px; }}
            .main {{ flex-grow: 1; padding: 30px; display: flex; flex-direction: column; overflow-y: auto; }}
            .card {{ background: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
            .stat-value {{ font-size: 22px; font-weight: bold; color: var(--accent); }}
            .label {{ font-size: 10px; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }}
            
            /* Table Styling for that empty region */
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left; }}
            th {{ color: #8b949e; font-size: 11px; padding: 10px; border-bottom: 1px solid #30363d; }}
            td {{ padding: 15px 10px; font-size: 14px; border-bottom: 1px solid #30363d; }}
            .status-indicator {{ height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3 style="color:white; margin-bottom:25px;">NETWORK ANALYTICS</h3>
            <div class="card" style="background: #0d1117;">
                <p class="label">Primary Latency (ms)</p>
                <div style="height: 200px;"><canvas id="latencyChart"></canvas></div>
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

            <!-- NEW: This replaces your empty region with a Regional Distribution View -->
            <div class="card" style="flex-grow: 1;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <p class="label" style="margin:0;">Multi-Region Health Check Distribution</p>
                    <span style="font-size:11px; background:#30363d; padding:2px 8px; border-radius:10px;">Cloud Agnostic: AWS</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>REGION</th>
                            <th>ENDPOINT</th>
                            <th>STATUS</th>
                            <th>LATENCY</th>
                            <th>TYPE</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>ASIA-SOUTH-1 (Mumbai)</td>
                            <td><code>{data['primary_ip']}</code></td>
                            <td><span class="status-indicator" style="background:{'#00ff88' if mumbai_ok else '#ff4444'}"></span>{'Healthy' if mumbai_ok else 'Unreachable'}</td>
                            <td>{mumbai_lat} ms</td>
                            <td>Primary cloud</td>
                        </tr>
                        <tr>
                            <td>US-EAST-1 (Virginia)</td>
                            <td><code>{data['backup_ip']}</code></td>
                            <td><span class="status-indicator" style="background:#00ff88"></span>Healthy</td>
                            <td>{usa_lat} ms</td>
                            <td>Failover cloud</td>
                        </tr>
                    </tbody>
                </table>
                <p style="font-size: 12px; color: #8b949e; margin-top: 20px; font-style: italic;">
                    * The Orchestration Layer performs recursive health checks every 4 seconds. Failover initiates automatically upon primary heartbeat loss.
                </p>
            </div>
        </div>

        <script>
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

            setTimeout(() => {{ window.location.reload(); }}, 4000);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True, port=5000)