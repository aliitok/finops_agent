from aws.trusted_advisor import get_ta_summary

# shim to keep import path stable (jobs expect services.trusted_advisor)

__all__ = ["get_ta_summary"]
