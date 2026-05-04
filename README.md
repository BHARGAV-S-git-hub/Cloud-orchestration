# 🚀 Cloud-FinOps Orchestrator

A real-time **Multi-Region Network Operations Center (NOC)** that automates AWS infrastructure using a **triple-constraint decision engine**:

* 🟢 **Availability (Health)**
* ⚡ **Performance (Latency)**
* 💰 **Cost (FinOps)**

---

## 📌 Overview

Cloud-FinOps Orchestrator is designed to intelligently manage cloud infrastructure across multiple AWS regions. It ensures **high availability, optimal performance, and cost efficiency** through automated monitoring, failover, and decision-making.

---

## 🛠️ Tech Stack

| Category           | Technology                                 |
| ------------------ | ------------------------------------------ |
| ☁️ Cloud Platform  | Amazon Web Services (EC2, S3 Remote State) |
| 🏗️ Infrastructure | Terraform                                  |
| ⚙️ Backend Engine  | Python (Flask)                             |
| 🔗 Cloud SDK       | Boto3                                      |
| 🔄 CI/CD           | GitHub Actions                             |

---

## ✨ Key Features

### 🌍 1. Multi-Region High Availability (HA)

* Manages redundant instances across:

  * **Asia-South-1 (Mumbai)**
  * **US-East-1 (Virginia)**
* Eliminates single points of failure.

---

### ❤️ 2. Health-Aware Routing

* Integrated **ICMP-based heartbeat monitoring**.
* 🚨 **Failover Logic**:

  * Automatically switches to standby region if primary becomes unreachable.
* 🛡️ **Priority Rule**:

  * Health overrides cost and latency → ensures maximum uptime.

---

### 🗂️ 3. Hybrid State Management

* Uses **S3 Remote Backend** for:

  * Persistent infrastructure state
  * State locking
* Ensures consistency across:

  * Local development
  * CI/CD pipelines

---

### 🔄 4. Auto-Reconciliation Engine

* Python-driven synchronization loop.
* Executes:

  ```bash
  terraform refresh
  ```
* Automatically detects:

  * Public IP changes
  * Manual AWS instance reboots

---

### 🧠 5. Priority-Weighted Decision Engine

Decision hierarchy:

```
Health > Performance > Cost
```

* ⚡ **Latency Mode**:

  * Optimizes routing using real-time ICMP telemetry.
* 💰 **Profit Mode**:

  * Minimizes cost using live **Spot Instance pricing** via Boto3.

---

### 🔄 6. GitHub Actions CI/CD

* 🚀 **Continuous Deployment**:

  * Infrastructure auto-provisioned on every push.
* ☢️ **Nuclear Destroy Mode**:

  * Manual workflow to instantly destroy all resources
  * Prevents unexpected cost overruns

---

## ⚡ Quick Start

### 🔧 Provision Infrastructure

```bash
terraform init
terraform apply
```

---

### 🖥️ Launch NOC Dashboard

```bash
python app.py
```

---

### 🔁 Automate Lifecycle

* Push code changes to GitHub
* CI/CD pipeline will automatically:

  * Deploy infrastructure
  * Sync state
  * Apply updates

---
