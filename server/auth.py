import os
import boto3
import jwt
from botocore.exceptions import ClientError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from ssm_secrets import get_secret

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "users")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def _jwt_secret() -> str:
    return get_secret("JWT_SECRET")


def _dynamodb_table():
    resource = boto3.resource(
        "dynamodb",
        region_name=AWS_REGION,
        aws_access_key_id=get_secret("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=get_secret("AWS_SECRET_ACCESS_KEY"),
    )
    return resource.Table(TABLE_NAME)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str) -> str:
    payload = {"sub": email.lower()}
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return email
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    email: str
    access_token: str
    token_type: str = "bearer"


def signup_user(request: SignupRequest) -> AuthResponse:
    email = request.email.lower().strip()
    table = _dynamodb_table()

    try:
        existing = table.get_item(Key={"email": email})
        if "Item" in existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        table.put_item(
            Item={
                "email": email,
                "password_hash": hash_password(request.password),
            }
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach user database",
        ) from exc

    token = create_access_token(email)
    return AuthResponse(email=email, access_token=token)


def login_user(request: LoginRequest) -> AuthResponse:
    email = request.email.lower().strip()
    table = _dynamodb_table()

    try:
        result = table.get_item(Key={"email": email})
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach user database",
        ) from exc

    item = result.get("Item")
    if not item or not verify_password(request.password, item["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(email)
    return AuthResponse(email=email, access_token=token)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return decode_token(credentials.credentials)
