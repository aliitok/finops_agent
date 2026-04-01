import boto3

def assume_role(role_arn: str):
    sts = boto3.client("sts")

    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName="finops-agent"
    )

    creds = resp["Credentials"]

    return {
        "aws_access_key_id": creds["AccessKeyId"],
        "aws_secret_access_key": creds["SecretAccessKey"],
        "aws_session_token": creds["SessionToken"],
    }