import sys
import os
import json
from aws.assume_role import assume_role
from aws.cost_explorer import fetch_monthly_cost_by_service, fetch_daily_cost
from db.db import init_db, save_monthly, save_daily, save_ta_summary
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.trusted_advisor import get_ta_summary

def load_accounts():
    with open("registry/accounts.json") as f:
        return json.load(f)

def process_monthly(res):
    groups = res["ResultsByTime"][0]["Groups"]

    total = 0
    services = []

    for g in groups:
        name = g["Keys"][0]
        cost = float(g["Metrics"]["UnblendedCost"]["Amount"])
        total += cost
        services.append((name, cost))

    # sort + top 5
    services.sort(key=lambda x: x[1], reverse=True)
    top = [{k: round(v, 2)} for k, v in services[:5]]

    return round(total, 2), top

def process_daily(res):
    out = []
    for day in res["ResultsByTime"]:
        date = day["TimePeriod"]["Start"]
        cost = float(day["Total"]["UnblendedCost"]["Amount"])
        out.append({"date": date, "cost": round(cost, 2)})
    return out

def run():
    init_db()
    accounts = load_accounts()

    for acc in accounts:
        print(f"Syncing {acc['name']}...")

        creds = assume_role(acc["role_arn"])

        # monthly
        m = fetch_monthly_cost_by_service(creds)
        total, top = process_monthly(m)
        save_monthly(acc["account_id"], total, top)

        # daily
        d = fetch_daily_cost(creds)
        daily = process_daily(d)
        save_daily(acc["account_id"], daily)
        
        # trusted advisor summaries
        try:
            ta = get_ta_summary(acc)
        except Exception as e:
            print(f"Trusted Advisor fetch failed for {acc['name']}: {e}")
            ta = {"error": str(e)}

        save_ta_summary(acc["account_id"], ta)

if __name__ == "__main__":
    run()