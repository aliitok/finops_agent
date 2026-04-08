# FinOps Agent (Multi-Account AWS Cost Optimization)

A lightweight, self-hosted FinOps agent that analyzes AWS cost across multiple accounts using Cost Explorer, caching, and structured insights.

This project is designed to:

* Avoid paid FinOps platforms
* Work without AWS Organizations
* Use cross-account IAM roles
* Be extensible into a full AI agent later

---

## 🚀 Features (Current)

* Multi-account support via `STS AssumeRole`
* Cost Explorer ingestion (monthly + daily)
* Local caching using SQLite
* Top service cost breakdown
* Basic anomaly (spike) detection
* CLI-based interaction

---

## 🧱 Architecture

```
Python App
   ↓
Account Registry (JSON)
   ↓
STS AssumeRole
   ↓
AWS Cost Explorer
   ↓
SQLite Cache
   ↓
Analysis Layer
   ↓
CLI / (Future: AI Agent)
```

---

## 📁 Project Structure

```
finops_agent/
├── aws/                # AWS interaction (STS, CE)
├── db/                 # SQLite cache layer
├── jobs/               # Cron jobs (data ingestion)
├── services/           # Cost analysis logic
├── registry/           # Account metadata
├── main.py             # CLI entry point
```

---

## ⚙️ Setup

### 1. Clone & setup env

```bash
git clone <your-repo>
cd finops_agent

python -m venv .env
source .env/bin/activate

pip install boto3
```

---

### 2. Configure accounts

Edit:

```
registry/accounts.json
```

Example:

```json
[
  {
    "account_id": "123456789012",
    "name": "prod",
    "role_arn": "arn:aws:iam::123456789012:role/FinOpsReadOnlyRole"
  }
]
```

---

## 🔐 IAM Configuration

### A. Agent Role (your runtime account)

Attach this policy:

```json
{
  "Effect": "Allow",
  "Action": "sts:AssumeRole",
  "Resource": [
    "arn:aws:iam::<TARGET_ACCOUNT_ID>:role/FinOpsReadOnlyRole"
  ]
}
```

---

### B. Target Account Role (`FinOpsReadOnlyRole`)

#### Trust Policy:

```json
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<AgentRole>"
  },
  "Action": "sts:AssumeRole"
}
```

---

#### Permissions (minimum required):

```json
{
  "Effect": "Allow",
  "Action": [
    "ce:GetCostAndUsage"
  ],
  "Resource": "*"
}
```

---

#### Recommended additional permissions:

* `ec2:Describe*`
* `cloudwatch:GetMetricData`
* `savingsplans:Describe*`

---

## ▶️ Usage

### Run cost sync (cron job)

```bash
python -m jobs.cost_sync
```

---

### Query cost analysis

```bash
python main.py
```

---

## ⏱️ Cron (optional)

Example:

```bash
crontab -e
```

```bash
0 2 * * * cd /path/to/repo && python -m jobs.cost_sync
```

---

## ⚠️ Known Issues

### ❗ AccessDeniedException (STS)

Common causes:

* Trust policy incorrect
* Wrong role ARN
* Agent role missing `sts:AssumeRole`
* Target role not allowing your account

Debug checklist:

1. Verify trust relationship
2. Check exact role ARN
3. Test manually:

```bash
aws sts assume-role --role-arn <ROLE_ARN> --role-session-name test
```

---

### ❗ Cost Explorer region

Must use:

```python
boto3.client("ce", region_name="us-east-1")
```

---

## 🧠 Roadmap

### Phase 1 (current)

* Cost ingestion
* Basic analysis

### Phase 2

* EC2 idle detection
* EBS unused volumes
* Multi-account aggregation

### Phase 3

* CUR + Athena integration
* Parallel execution
* Redis caching

### Phase 4

* AI agent (LangGraph or custom)
* Natural language queries
* Recommendations engine

---

## 🎯 Design Principles

* No raw AWS calls from agent
* Precompute → cache → analyze
* Keep tools deterministic
* Optimize for cost + simplicity

---

## 🤝 Contributing / Next Steps

Planned improvements:

* [ ] Parallel account processing
* [ ] Better anomaly detection
* [ ] Cost delta analysis
* [ ] API layer (FastAPI optional)
* [ ] ECS deployment

---

## 📌 Notes

This project is intentionally minimal and extensible.
The goal is to evolve it into a **self-hosted FinOps AI agent platform** without relying on external SaaS tools.

---

TEST
