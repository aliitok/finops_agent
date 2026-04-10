import boto3
from datetime import date, timedelta

def get_month_range():
    today = date.today()
    start = today.replace(day=1)
    end = today
    return str(start), str(end)

def get_last_30_days():
    end = date.today()
    start = end - timedelta(days=30)
    return str(start), str(end)

def fetch_monthly_cost_by_service(creds):
    ce = boto3.client("ce", **creds)

    start, end = get_month_range()

    res = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
    )

    return res

def fetch_daily_cost(creds):
    ce = boto3.client("ce", **creds)

    start, end = get_last_30_days()

    res = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="DAILY",
        Metrics=["UnblendedCost"]
    )

    return res