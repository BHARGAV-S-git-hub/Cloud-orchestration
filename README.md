## Cloud-FinOps Orchestrator

A real-time Multi-Region **Network Operations Center (NOC)** that automates AWS infrastructure through a triple-constraint engine: Availability (Health), Performance (Latency), and Cost (FinOps).

## The Tech Stack
Cloud Platform: AWS (EC2, S3 Remote State)

Infrastructure as Code: Terraform

Backend Engine: Python (Flask)

Cloud SDK: Boto3 (AWS Spot Price Telemetry)

Automation/CI-CD: GitHub Actions

 ## Key Technical Features
 
**1. Multi-Region High Availability (HA)**
Proactively manages redundant instances across Asia-South-1 (Mumbai) and US-East-1 (Virginia) to eliminate single points of failure.

**2. Health-Aware Routing**
*Integrated Health Check Heartbeat monitoring ICMP connectivity.

*Failover Logic: If a region becomes "Unreachable," the orchestrator triggers an immediate failover to the standby region.

*Safety First: This bypasses cost or latency preferences to ensure 100% service uptime.

**3. Hybrid State Management**
Utilizes an S3 Remote Backend for persistent infrastructure state and state locking, ensuring consistency across local and CI/CD environments.

4. Auto-Reconciliation Engine
A Python-driven State Synchronization loop that executes terraform refresh to automatically detect dynamic Public IP changes resulting from manual AWS instance reboots.

5. Priority-Weighted Decision Engine
*The system resolves routing conflicts using a strict hierarchy: Health > Performance > Cost.

*Latency Mode: Optimizes the network path based on real-time ICMP telemetry.

*Profit Mode: Minimizes cloud burn-rate using live Spot Instance market data via Boto3.

6. GitHub Actions CI/CD
**Continuous Deployment:** Automated infrastructure provisioning on every push.

**Nuclear Destroy:** A manual workflow dispatch for rapid, total resource decommissioning to prevent unauthorized budget overruns.

 ## Quick Start
**Provision Infrastructure:**

terraform init
terraform apply

**Launch the NOC Dashboard:**

python app.py

**Automate Lifecycle:**

Push code changes to GitHub to trigger the automated CI/CD pipeline.
