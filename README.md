Cloud-FinOps Orchestrator
A real-time Multi-Region Network Operations Center (NOC) that automates AWS infrastructure through a triple-constraint engine: Cost (FinOps), Performance (Latency), and Availability (Health).

The Tech Stack
Cloud: AWS (EC2, S3 Backend)

IaC: Terraform

Backend: Python (Flask)

SDK: Boto3 (AWS Price Fetching)

CI/CD: GitHub Actions

Key Technical Features
Multi-Region Strategy: Manages instances in Mumbai (Primary) and Virginia (Standby) using Terraform providers.

Hybrid State Management: Uses an S3 Remote Backend for state persistence.

Auto-Reconciliation: Python logic triggers terraform refresh to automatically detect IP changes from manual AWS restarts.

Priority Engine:

Latency Mode: Prioritizes the fastest network path (ICMP telemetry).

Profit Mode: Switches to the cheapest region using live Spot rates.

Conflict Resolution: Performance (Latency) always overrides Cost if both are enabled.

GitHub Actions CI/CD:

Automated deployment of infrastructure on push.

Nuclear Destroy: Manual workflow dispatch to instantly wipe all AWS resources to prevent cost leakage.

Quick Start
Provision: terraform init & terraform apply.

Launch: python app.py.

Automate: Push to GitHub to trigger the CI/CD pipeline.
