import boto3
from aws.assume_role import assume_role

# ==============================
# CONFIG
# ==============================

TA_CHECK_NAMES = {
    "idle_ec2": "Low Utilization Amazon EC2 Instances",
    "ebs_idle": "Underutilized Amazon EBS Volumes",
    "ri_opt": "Reserved Instance Optimization",
    "sp_util": "Savings Plans Utilization"
}

# in-memory cache (can move to DB later)
# _CHECK_ID_CACHE = {}


# ==============================
# CLIENT (same pattern as CE)
# ==============================

def get_ta_client(creds):
    return boto3.client(
        "support",
        region_name="us-east-1",
        **creds
    )


# ==============================
# CHECK ID RESOLUTION (cached)
# ==============================

# def resolve_check_ids(client):
#     global _CHECK_ID_CACHE

#     if _CHECK_ID_CACHE:
#         return _CHECK_ID_CACHE

#     checks = client.describe_trusted_advisor_checks(language="en")["checks"]

#     for c in checks:
#         if c["name"] in TA_CHECK_NAMES.values():
#             _CHECK_ID_CACHE[c["name"]] = c["id"]

#     return _CHECK_ID_CACHE


# ==============================
# FETCH
# ==============================

def fetch_ta_result(creds, check_name):
    client = get_ta_client(creds)
    check_map = resolve_check_ids(client)

    check_id = check_map.get(check_name)

    if not check_id:
        return None

    return client.describe_trusted_advisor_check_result(
        checkId=check_id
    )


# ==============================
# NORMALIZATION
# ==============================

def _normalize(flagged_resources, label, max_items=5):
    total = len(flagged_resources)

    items = []
    for r in flagged_resources[:max_items]:
        metadata = r.get("metadata", [])

        items.append({
            "resource_id": r.get("resourceId"),
            "region": metadata[0] if metadata else "unknown",
            "metadata": metadata
        })

    return {
        "summary": label,
        "total_count": total,
        "estimated_savings": 0.0,
        "top_items": items
    }


# ==============================
# SERVICE FUNCTIONS
# ==============================

def get_idle_ec2_summary(account):
    creds = assume_role(account["role_arn"])

    res = fetch_ta_result(creds, TA_CHECK_NAMES["idle_ec2"])
    if not res:
        return {"error": "Idle EC2 check not found"}

    flagged = res["result"].get("flaggedResources", [])

    return _normalize(flagged, "Idle EC2 Instances")


def get_ebs_idle_summary(account):
    creds = assume_role(account["role_arn"])

    res = fetch_ta_result(creds, TA_CHECK_NAMES["ebs_idle"])
    if not res:
        return {"error": "EBS check not found"}

    flagged = res["result"].get("flaggedResources", [])

    return _normalize(flagged, "Unused EBS Volumes")


def get_ri_summary(account):
    creds = assume_role(account["role_arn"])

    res = fetch_ta_result(creds, TA_CHECK_NAMES["ri_opt"])
    if not res:
        return {"error": "RI check not found"}

    flagged = res["result"].get("flaggedResources", [])

    return _normalize(flagged, "RI Optimization Opportunities")


def get_sp_summary(account):
    creds = assume_role(account["role_arn"])

    res = fetch_ta_result(creds, TA_CHECK_NAMES["sp_util"])
    if not res:
        return {"error": "SP check not found"}

    flagged = res["result"].get("flaggedResources", [])

    return _normalize(flagged, "Savings Plan Utilization")


# ==============================
# AGGREGATED ENTRY
# ==============================

def get_ta_summary(account):
    return {
        "idle_ec2": get_idle_ec2_summary(account),
        "ebs": get_ebs_idle_summary(account),
        "ri": get_ri_summary(account),
        "savings_plan": get_sp_summary(account)
    }
