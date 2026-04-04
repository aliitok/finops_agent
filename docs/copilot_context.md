# FinOps Agent Context (for GitHub Copilot)

## Project Goal

This project is a multi-account AWS FinOps agent that:

* Uses AWS Cost Explorer (CE) and Trusted Advisor (TA)
* Assumes roles across multiple AWS accounts
* Aggregates and caches cost + optimization insights
* Provides structured, agent-friendly outputs (NOT raw AWS responses)

---

## Architecture

* Python-based (no heavy frameworks)
* Modules:

  * aws/ → AWS interaction (STS, CE, TA)
  * jobs/ → cron ingestion
  * db/ → caching layer (SQLite now, Postgres later)
  * services/ → analysis logic
  * registry/ → account metadata

---

## Key Design Principles

1. NEVER expose raw AWS API output
2. ALWAYS normalize data into small structured summaries
3. LIMIT output size (top N results only)
4. PREFER precomputed data over live API calls
5. AGENT reads from DB/cache, not AWS directly

---

## AWS Access Pattern

* Use STS AssumeRole per account
* Do NOT hardcode credentials
* Trusted Advisor and Cost Explorer use `us-east-1`
* Regional services must dynamically detect regions

---

## Data Strategy

* Cron jobs fetch data → store in DB
* Agent reads only:

  * monthly cost summary
  * daily cost trend
  * trusted advisor summaries

---

## Trusted Advisor Usage

* Used as primary signal source for:

  * idle EC2
  * unattached EBS
  * savings plans / RI

* Always:

  * extract only relevant checks
  * aggregate results
  * keep top 5–10 resources

---

## Output Format Rules

All service outputs MUST follow this structure:

{
"summary": "...",
"total_count": number,
"estimated_savings": number,
"top_items": [...]
}

---

## What to Avoid

* No raw boto3 responses
* No full resource dumps
* No hardcoded regions
* No synchronous heavy loops across thousands of resources

---

## Future Direction

* Add AI reasoning layer (LLM)
* Add ranking/prioritization of savings
* Add multi-account aggregation
* Possibly expose via API (FastAPI optional)

---
