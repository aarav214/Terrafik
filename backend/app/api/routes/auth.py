import logging

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_client
from app.schemas.auth import AuthUserResponse, Credentials, LoginResponse

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=AuthUserResponse)
def signup(
    payload: Credentials,
    supabase: Client = Depends(get_supabase_client),
) -> dict:
    try:
        response = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
    except Exception as exc:
        logger.exception("Signup failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed",
        ) from exc

    user = getattr(response, "user", None)
    if user is None and isinstance(response, dict):
        user = response.get("user")

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed",
        )

    if hasattr(user, "model_dump"):
        user = user.model_dump()
    elif hasattr(user, "dict"):
        user = user.dict()
    elif not isinstance(user, dict):
        user = {"value": user}

    return {"user": user}


@router.post("/login", response_model=LoginResponse)
def login(
    payload: Credentials,
    supabase: Client = Depends(get_supabase_client),
) -> dict:
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password,
            }
        )
    except Exception as exc:
        logger.info("Login failed for %s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

    session = getattr(response, "session", None)
    user = getattr(response, "user", None)

    if session is None and isinstance(response, dict):
        session = response.get("session")
    if user is None and isinstance(response, dict):
        user = response.get("user")

    if session is None or user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = getattr(session, "access_token", None)
    if access_token is None and isinstance(session, dict):
        access_token = session.get("access_token")

    if hasattr(user, "model_dump"):
        user = user.model_dump()
    elif hasattr(user, "dict"):
        user = user.dict()
    elif not isinstance(user, dict):
        user = {"value": user}

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return {"access_token": access_token, "user": user}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {"user": current_user}
