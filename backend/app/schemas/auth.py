from typing import Any

from pydantic import BaseModel, EmailStr, Field


class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AuthUserResponse(BaseModel):
    user: dict[str, Any]


class LoginResponse(BaseModel):
    access_token: str
    user: dict[str, Any]
