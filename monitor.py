import os
import time
import subprocess
import json

def get_terraform_outputs():
    print("🔍 Fetching latest IPs from Terraform...")
    result = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True)
    outputs = json.loads(result.stdout)
    return outputs['primary_server_ip']['value'], outputs['backup_server_ip']['value']

# Automatically fetch the IPs
PRIMARY_IP, BACKUP_IP = get_terraform_outputs()

# ... (the rest of your check_server logic remains the same)
def check_server(ip):
    # Sends 1 ping packet to the IP
    # 'ping -n 1' for Windows, 'ping -c 1' for Mac/Linux
    param = "-n" if os.name == 'nt' else "-c"
    response = os.system(f"ping {param} 1 {ip} > nul")
    return response == 0

print("--- 🚀 CLOUD FAILOVER MONITOR STARTING ---")
print(f"Monitoring Primary (Mumbai): {PRIMARY_IP}")
print(f"Standby Backup (USA): {BACKUP_IP}")
print("------------------------------------------")

try:
    while True:
        if check_server(PRIMARY_IP):
            print(f"✅ [HEALTHY] Mumbai Server is LIVE. Time: {time.ctime()}")
        else:
            print(f"🚨 [ALERT] MUMBAI SERVER DOWN!")
            print(f"🔄 [FAILOVER] Traffic redirected to USA: {BACKUP_IP}")
            # In a real production setup, we would update DNS records here.
            break 
        
        time.sleep(5) # Checks every 5 seconds

except KeyboardInterrupt:
    print("\nMonitor stopped by user.")