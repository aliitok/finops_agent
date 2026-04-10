from db.db import get_monthly, get_daily, get_ta_summary, get_account

def detect_spike(daily):
    if not daily or len(daily) < 2:
        return False

    last = daily[-1]["cost"]
    avg = sum(d["cost"] for d in daily[:-1]) / (len(daily) - 1)

    return last > avg * 1.3

def explain(account_id):
    m = get_monthly(account_id)
    d = get_daily(account_id)
    ta = get_ta_summary(account_id)
    acc = get_account(account_id)

    if not m:
        return "No data available"

    # Get environment from account metadata or monthly_cost record
    environment = None
    if acc:
        environment = acc.get("environment")
    if not environment and m:
        environment = m.get("environment")

    spike = detect_spike(d["data"] if d else None)

    # Get trusted advisor data
    ta_data = ta.get("data") if ta else None

    if spike:
        return {
            "summary": "Cost spike detected",
            "account_id": account_id,
            "environment": environment,
            "total": m["total_cost"],
            "top_services": m["top_services"],
            "trusted_advisor": ta_data
        }
    else:
        return {
            "summary": "Cost is stable",
            "account_id": account_id,
            "environment": environment,
            "total": m["total_cost"],
            "top_services": m["top_services"],
            "trusted_advisor": ta_data
        }