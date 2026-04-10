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
* Trusted Advisor integration (idle EC2, unused EBS, RI/SP optimization)
* Environment tagging support (STG, PRD, etc.)
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
┌─────────────────┬────────────────────┐
│ AWS Cost        │ Trusted Advisor    │
│ Explorer        │ (Support API)      │
└─────────────────┴────────────────────┘
   ↓
SQLite Cache (monthly_cost, daily_cost, ta_summary)
   ↓
Analysis Layer (spike detection, cost breakdown)
   ↓
CLI / (Future: AI Agent)
```

---

## 📁 Project Structure

```
finops_agent/
├── aws/                # AWS interaction (STS, CE, Trusted Advisor)
├── db/                 # SQLite cache layer
├── jobs/               # Cron jobs (data ingestion)
├── services/           # Cost analysis logic
├── registry/           # Account metadata
├── tests/              # Unit tests
├── docs/               # Documentation
├── main.py             # CLI entry point
└── cost.db             # SQLite database (auto-generated)
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
    "role_arn": "arn:aws:iam::123456789012:role/FinOpsReadOnlyRole",
    "environment": "PRD"
  },
  {
    "account_id": "210987654321",
    "name": "staging",
    "role_arn": "arn:aws:iam::210987654321:role/FinOpsReadOnlyRole",
    "environment": "STG"
  }
]
```

| Field | Description |
|-------|-------------|
| `account_id` | AWS Account ID |
| `name` | Friendly name for the account |
| `role_arn` | ARN of the IAM role to assume |
| `environment` | (Optional) Environment tag (e.g., PRD, STG, DEV) |

---

## 🔐 IAM Configuration

### A. Agent Role (your runtime account)

Attach this policy to allow the agent to assume roles in target accounts:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": [
        "arn:aws:iam::<TARGET_ACCOUNT_ID>:role/FinOpsReadOnlyRole"
      ]
    }
  ]
}
```

---

### B. Target Account Role (`FinOpsReadOnlyRole`)

#### Trust Policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<YOUR_ACCOUNT_ID>:role/<AgentRole>"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

---

#### Permissions (minimum required):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    }
  ]
}
```

---

#### Permissions (with Trusted Advisor support):

To enable Trusted Advisor checks for cost optimization recommendations (idle EC2, unused EBS, RI/SP optimization), add these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "support:DescribeTrustedAdvisorChecks",
        "support:DescribeTrustedAdvisorCheckResult"
      ],
      "Resource": "*"
    }
  ]
}
```

> **Note:** Trusted Advisor requires a Business, Enterprise On-Ramp, or Enterprise Support plan to access the Support API. If you have Basic Support, the Trusted Advisor features will return errors.

---

#### Full Policy (all features):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CostExplorerAccess",
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "TrustedAdvisorAccess",
      "Effect": "Allow",
      "Action": [
        "support:DescribeTrustedAdvisorChecks",
        "support:DescribeTrustedAdvisorCheckResult"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EC2Describe",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchMetrics",
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SavingsPlansAndReservedInstances",
      "Effect": "Allow",
      "Action": [
        "savingsplans:DescribeSavingsPlans",
        "rds:DescribeReservedDBInstances",
        "ec2:DescribeReservedInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

---

#### AWS Managed Policy Alternative:

For convenience, you can attach the following AWS managed policies:

| Policy | Purpose |
|--------|---------|
| `AWSCostExplorerReadOnly` | Cost Explorer access |
| `AWSSupportAccess` | Trusted Advisor access (requires Support plan) |

---

#### Recommended additional permissions:

* `ec2:Describe*` - For detailed EC2 resource analysis
* `cloudwatch:GetMetricData` - For resource utilization metrics
* `savingsplans:Describe*` - For Savings Plans analysis

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

### Phase 1 (current) ✅

* [x] Cost ingestion
* [x] Basic analysis
* [x] Trusted Advisor integration
* [x] Environment tagging

### Phase 2

* [ ] EC2 idle detection (via CloudWatch metrics)
* [ ] EBS unused volumes
* [ ] Multi-account aggregation
* [ ] Parallel account processing

### Phase 3

* [ ] CUR + Athena integration
* [ ] Parallel execution
* [ ] Redis caching

### Phase 4

* [ ] AI agent (LangGraph or custom)
* [ ] Natural language queries
* [ ] Recommendations engine

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
