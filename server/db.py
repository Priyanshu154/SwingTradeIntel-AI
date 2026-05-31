import os

import boto3

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _running_on_lambda() -> bool:
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def dynamodb_table(table_name: str):
    kwargs: dict = {"region_name": AWS_REGION}
    if not _running_on_lambda():
        from ssm_secrets import get_secret

        kwargs["aws_access_key_id"] = get_secret("AWS_ACCESS_KEY_ID")
        kwargs["aws_secret_access_key"] = get_secret("AWS_SECRET_ACCESS_KEY")
    return boto3.resource("dynamodb", **kwargs).Table(table_name)
