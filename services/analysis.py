from db.db import get_monthly, get_daily

def detect_spike(daily):
    if not daily or len(daily) < 2:
        return False

    last = daily[-1]["cost"]
    avg = sum(d["cost"] for d in daily[:-1]) / (len(daily) - 1)

    return last > avg * 1.3

def explain(account_id):
    m = get_monthly(account_id)
    d = get_daily(account_id)

    if not m:
        return "No data available"

    spike = detect_spike(d)

    if spike:
        return {
            "summary": "Cost spike detected",
            "total": m["total_cost"],
            "top_services": m["top_services"]
        }
    else:
        return {
            "summary": "Cost is stable",
            "total": m["total_cost"],
            "top_services": m["top_services"]
        }