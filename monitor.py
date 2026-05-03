import os
import time
import subprocess
import json
import boto3
from datetime import datetime

# Initialize the AWS Client for real-market data
# Note: Ensure your AWS CLI is configured with credentials on your laptop
ec2_client = boto3.client('ec2', region_name='us-east-1')

def get_terraform_outputs():
    print("🔍 Fetching latest IPs from S3 Remote Backend...")
    # Because you set up the S3 backend, this now pulls from the cloud!
    result = subprocess.run(['terraform', 'output', '-json'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Error: Could not read Terraform state. Ensure S3 backend is initialized.")
        return "0.0.0.0", "0.0.0.0"
        
    outputs = json.loads(result.stdout)
    return outputs['primary_server_ip']['value'], outputs['backup_server_ip']['value']

def get_market_prices():
    """
    Fetches real-time Spot price for Virginia and compares it 
    against the fixed On-Demand price for Mumbai.
    """
    try:
        # Fetch Real-Time Spot Price for us-east-1 (Virginia)
        response = ec2_client.describe_spot_price_history(
            InstanceTypes=['t3.micro'],
            ProductDescriptions=['Linux/UNIX'],
            StartTime=datetime.now(),
            MaxResults=1
        )
        
        va_spot_price = float(response['SpotPriceHistory'][0]['SpotPrice'])
        
        # Fixed On-Demand Price for ap-south-1 (Mumbai) approx $0.0208/hr
        mumbai_ondemand_price = 0.0208 
        
        return {
            "us-east-1": va_spot_price,
            "ap-south-1": mumbai_ondemand_price
        }
    except Exception as e:
        print(f"⚠️ Pricing API Warning: {e}")
        # Professional Fallback values
        return {"us-east-1": 0.0035, "ap-south-1": 0.0208}

def check_server(ip):
    # Sends 1 ping packet to the IP
    if ip == "0.0.0.0": return False
    param = "-n" if os.name == 'nt' else "-c"
    response = os.system(f"ping {param} 1 {ip} > nul")
    return response == 0

# --- MAIN EXECUTION ---
PRIMARY_IP, BACKUP_IP = get_terraform_outputs()

print("--- 🚀 CLOUD ORCHESTRATOR & FINOPS MONITOR ---")
print(f"Primary (Mumbai): {PRIMARY_IP}")
print(f"Secondary (USA): {BACKUP_IP}")
print("----------------------------------------------")

try:
    while True:
        # 1. Check Physical Health (Existing HA Feature)
        mumbai_live = check_server(PRIMARY_IP)
        
        # 2. Fetch Financial Data (New FinOps Feature)
        prices = get_market_prices()
        
        if mumbai_live:
            print(f"✅ [HEALTHY] Mumbai is LIVE. Cost: ${prices['ap-south-1']}/hr")
        else:
            print(f"🚨 [ALERT] MUMBAI DOWN! Failover Active -> USA: {BACKUP_IP}")
            print(f"💡 [FINOPS] Current USA Spot Price: ${prices['us-east-1']}/hr")
        
        # Check if Virginia is currently cheaper (for the Profit Toggle logic)
        if prices['us-east-1'] < prices['ap-south-1']:
            print(f"💰 [OPPORTUNITY] Virginia is currently CHEAPER than Mumbai.")
            
        print(f"Last Check: {time.ctime()}")
        print("-" * 30)
        
        time.sleep(5) # Checks every 5 seconds

except KeyboardInterrupt:
    print("\nMonitor stopped by user.")