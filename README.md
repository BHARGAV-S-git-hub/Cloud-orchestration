Cloud-FinOps Orchestrator

A real-time Multi-Region Network Operations Center (NOC) that automates AWS infrastructure through a triple-constraint engine: Cost (FinOps), Performance (Latency), and Availability (Health).

🛠️ The Tech Stack
Cloud: AWS (EC2, S3 Backend)

IaC: Terraform

Backend: Python (Flask)

SDK: Boto3 (AWS Price Fetching)

CI/CD: GitHub Actions

⚡ Key Technical Features
Multi-Region High Availability (HA): Proactively manages redundant instances across Asia-South-1 (Mumbai) and US-East-1 (Virginia) to eliminate single points of failure.

Health-Aware Routing: An integrated Health Check Heartbeat that monitors ICMP connectivity. If a region becomes "Unreachable," the orchestrator triggers an immediate Failover to the standby region, bypassing cost or latency preferences to ensure 100% uptime.

Hybrid State Management: Leverages an S3 Remote Backend for persistent infrastructure state and locking.

Auto-Reconciliation: Python-driven State Synchronization that executes terraform refresh to detect dynamic IP changes from manual AWS reboots.

Priority-Weighted Engine:

Latency Mode: Optimizes the network path based on real-time ICMP telemetry.

Profit Mode: Minimizes cloud burn-rate using live Spot Instance market data via Boto3.

Conflict Logic: Health > Performance > Cost.

GitHub Actions CI/CD:

Automated infrastructure provisioning on push.

Nuclear Destroy: Manual workflow dispatch for rapid resource decommissioning to prevent budget overruns.
