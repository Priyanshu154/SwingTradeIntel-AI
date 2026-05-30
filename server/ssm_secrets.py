import os
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Logical env key -> SSM parameter name or ARN (override per deploy via env)
_DEFAULT_SSM_REFS = {
    "AWS_ACCESS_KEY_ID": "arn:aws:ssm:us-east-1:555447962237:parameter/DB_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY": "arn:aws:ssm:us-east-1:555447962237:parameter/DB_SECRET_ACCESS_KEY",
    "JWT_SECRET": "arn:aws:ssm:us-east-1:555447962237:parameter/JWT_SECRET",
}

_SSM_ENV_OVERRIDES = {
    "AWS_ACCESS_KEY_ID": "SSM_DB_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY": "SSM_DB_SECRET_ACCESS_KEY",
    "JWT_SECRET": "SSM_JWT_SECRET",
}


def _ssm_ref(logical_key: str) -> str:
    override_env = _SSM_ENV_OVERRIDES[logical_key]
    return os.getenv(override_env, _DEFAULT_SSM_REFS[logical_key])


def _param_identifiers(ref: str) -> tuple[str, str]:
    """Return (api Name value, short name for matching GetParameters response)."""
    if ref.startswith("arn:aws:ssm:"):
        short = ref.split("/parameter/", 1)[-1].lstrip("/")
        return ref, short
    short = ref.lstrip("/")
    return short, short


@lru_cache(maxsize=1)
def _fetch_secrets() -> dict[str, str]:
    refs = {key: _ssm_ref(key) for key in _DEFAULT_SSM_REFS}
    api_names = [_param_identifiers(ref)[0] for ref in refs.values()]

    client = boto3.client("ssm", region_name=AWS_REGION)
    try:
        response = client.get_parameters(Names=api_names, WithDecryption=True)
    except ClientError as exc:
        raise RuntimeError("Unable to load secrets from AWS SSM") from exc

    invalid = response.get("InvalidParameters") or []
    if invalid:
        raise RuntimeError(
            f"SSM parameters not found or not accessible: {', '.join(invalid)}"
        )

    by_name: dict[str, str] = {}
    for param in response.get("Parameters", []):
        by_name[param["Name"]] = param["Value"]
        arn = param.get("ARN")
        if arn:
            by_name[arn] = param["Value"]

    secrets: dict[str, str] = {}
    for logical_key, ref in refs.items():
        api_name, short = _param_identifiers(ref)
        value = by_name.get(api_name) or by_name.get(short)
        if not value:
            raise RuntimeError(
                f"SSM parameter for {logical_key} ({ref}) returned no value"
            )
        secrets[logical_key] = value

    return secrets


def get_secret(key: str) -> str:
    if key not in _DEFAULT_SSM_REFS:
        raise KeyError(f"Unknown secret key: {key}")
    return _fetch_secrets()[key]
