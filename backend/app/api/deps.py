from typing import Any
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from app.core.supabase import get_supabase_service_client

logger = logging.getLogger(__name__)


# Use FastAPI's HTTPBearer so OpenAPI/Swagger shows the "Authorize" button
http_bearer = HTTPBearer(bearerFormat="Bearer")


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    token = getattr(credentials, "credentials", None)
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token",
        )

    return token.strip()


def _to_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return value
    if hasattr(value, "dict"):
        return value.dict()
    return {"value": value}


def get_current_user(
    token: str = Depends(get_bearer_token),
    supabase: Client = Depends(get_supabase_service_client),
) -> dict[str, Any]:
    try:
        response = supabase.auth.get_user(token)
    except Exception as exc:  # Supabase client surfaces auth failures here.
        logger.warning("Token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    user = getattr(response, "user", None)
    if user is None and isinstance(response, dict):
        user = response.get("user")

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return _to_dict(user)
