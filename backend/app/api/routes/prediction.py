import logging
import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.supabase import get_supabase_service_client
from app.schemas.prediction import PredictionResultResponse, PredictionErrorResponse, ReportIssueResponse
from app.services.prediction import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])
report_router = APIRouter(tags=["predictions"])
logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
GROQ_MODEL = "llama3-70b-8192"
GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


def _get_issue_report_store(request: Request) -> list[dict[str, Any]]:
    store = getattr(request.app.state, "issue_reports", None)
    if store is None:
        store = []
        request.app.state.issue_reports = store
    return store


def _extract_json_object(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL | re.IGNORECASE)
    if fenced_match:
        parsed = json.loads(fenced_match.group(1))
        if isinstance(parsed, dict):
            return parsed

    object_match = re.search(r"\{.*\}", content, re.DOTALL)
    if object_match:
        parsed = json.loads(object_match.group(0))
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("LLM response did not contain valid JSON")


def _severity_from_prediction(prediction: str, confidence: float) -> str:
    if prediction == "waterlogging":
        return "high" if confidence >= 0.55 else "medium"
    if prediction == "potholes":
        return "high" if confidence >= 0.65 else "medium"
    return "medium" if confidence >= 0.5 else "low"


def _build_fallback_issue_report(
    prediction: dict[str, Any],
    email: str,
    latitude: float,
    longitude: float,
) -> dict[str, str]:
    issue_type = str(prediction.get("prediction", "road issue")).replace("_", " ")
    severity = _severity_from_prediction(str(prediction.get("prediction", "")), float(prediction.get("confidence", 0.0)))
    complaint = (
        f"Road issue detected near {latitude:.6f}, {longitude:.6f} for {email}. "
        f"Predicted issue: {issue_type}. Please inspect and resolve it promptly."
    )
    return {
        "issue_type": issue_type,
        "severity": severity,
        "complaint": complaint,
    }


def _generate_llm_complaint(
    prediction: dict[str, Any],
    email: str,
    latitude: float,
    longitude: float,
) -> dict[str, str]:
    settings = get_settings()
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    structured_input = {
        "user_email": email,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "ml_prediction": {
            "issue_type": prediction.get("prediction"),
            "confidence": prediction.get("confidence"),
            "probabilities": prediction.get("probabilities"),
        },
    }

    prompt = (
        "You generate a single JSON object for a civic issue complaint. "
        "Return ONLY valid JSON with the keys issue_type, severity, complaint. "
        "severity must be one of low, medium, high. complaint should be a concise report message. "
        "Use the provided structured input and keep the issue_type aligned with the ML prediction when possible."
    )
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(structured_input)},
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        GROQ_CHAT_COMPLETIONS_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore") if exc.fp else str(exc)
        raise RuntimeError(f"Groq API error: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Groq API request failed: {exc.reason}") from exc

    choices = response_payload.get("choices") or []
    if not choices:
        raise ValueError("Groq response did not contain choices")

    content = choices[0].get("message", {}).get("content", "")
    parsed = _extract_json_object(content)

    issue_type = str(parsed.get("issue_type") or prediction.get("prediction") or "road issue")
    severity = str(parsed.get("severity") or _severity_from_prediction(str(prediction.get("prediction", "")), float(prediction.get("confidence", 0.0))))
    complaint = str(parsed.get("complaint") or "Issue report generated successfully.")

    return {
        "issue_type": issue_type,
        "severity": severity,
        "complaint": complaint,
    }


def _send_issue_email(email: str, report: dict[str, str]) -> None:
    print("Sending issue report email")
    print({"to": email, **report})


def get_prediction_service(
    supabase: Client = Depends(get_supabase_service_client),
) -> PredictionService:
    """Dependency to provide PredictionService with local ML model"""
    return PredictionService(supabase)


@router.post("/predict", response_model=PredictionResultResponse)
async def predict(
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(get_current_user),
    service: PredictionService = Depends(get_prediction_service),
) -> dict[str, Any]:
    """
    Upload image and get road issue prediction.
    
    - Requires authentication (Bearer token)
    - Accepts jpg/png images only
    - Calls ML backend for prediction
    - Saves result to database
    
    Args:
        file: Image file (jpg or png)
        user: Authenticated user from token
        service: PredictionService instance
        
    Returns:
        Prediction result with ID and metadata
        
    Raises:
        HTTPException: On validation, processing, or database errors
    """
    
    try:
        user_id = user.get("id")
        if not user_id:
            logger.warning("User without ID attempted prediction")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session",
            )
        
        # Read and validate file
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024:.0f}MB limit",
            )
        
        # Check file extension
        filename = file.filename or "image"
        file_ext = "." + filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
            )
        
        logger.info(
            "Processing prediction request from user %s with file %s",
            user_id,
            filename,
        )
        
        # Process prediction
        result = await service.predict(
            file_content=file_content,
            filename=filename,
            user_id=user_id,
            image_url=None,  # Optional: set if you store images
        )
        
        logger.info(
            "Prediction completed for user %s: %s",
            user_id,
            result.get("prediction"),
        )
        
        return result
        
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error("ML model inference failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model inference failed. Please try again.",
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during prediction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        ) from e


@report_router.post("/report-issue", response_model=ReportIssueResponse)
async def report_issue(
    request: Request,
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    email: str | None = Form(None),
    user: dict[str, Any] = Depends(get_current_user),
    service: PredictionService = Depends(get_prediction_service),
) -> dict[str, str]:
    """
    Upload an image, run ML prediction, and generate a complaint with Groq.

    Email is taken from the authenticated login session. A client-provided email
    may be sent for validation, but it cannot override the authenticated identity.
    """

    try:
        user_id = user.get("id")
        user_email = user.get("email")
        if not user_id or not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session",
            )

        if email and email.strip().lower() != str(user_email).strip().lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email must match the authenticated login email",
            )

        if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location coordinates",
            )

        file_content = await image.read()
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024:.0f}MB limit",
            )

        filename = image.filename or "image"
        file_ext = "." + filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        logger.info(
            "Processing issue report for user %s at (%s, %s) with file %s",
            user_id,
            latitude,
            longitude,
            filename,
        )

        prediction = await service.predict(
            file_content=file_content,
            filename=filename,
            user_id=user_id,
            image_url=None,
        )

        try:
            report = _generate_llm_complaint(
                prediction=prediction,
                email=str(user_email),
                latitude=latitude,
                longitude=longitude,
            )
        except Exception as exc:
            logger.warning("LLM complaint generation failed, using fallback: %s", exc)
            report = _build_fallback_issue_report(
                prediction=prediction,
                email=str(user_email),
                latitude=latitude,
                longitude=longitude,
            )

        stored_report = {
            "user_id": user_id,
            "email": str(user_email),
            "latitude": latitude,
            "longitude": longitude,
            "prediction": prediction.get("prediction"),
            "confidence": prediction.get("confidence"),
            "issue_type": report["issue_type"],
            "severity": report["severity"],
            "complaint": report["complaint"],
        }
        _get_issue_report_store(request).append(stored_report)
        _send_issue_email(str(user_email), report)

        return report

    except HTTPException:
        raise
    except RuntimeError as exc:
        logger.error("Issue reporting failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during issue reporting")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request",
        ) from exc


@router.get("/history", response_model=list[PredictionResultResponse])
async def get_prediction_history(
    user: dict[str, Any] = Depends(get_current_user),
    service: PredictionService = Depends(get_prediction_service),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[dict[str, Any]]:
    """
    Get prediction history for authenticated user.
    
    - Requires authentication (Bearer token)
    - Returns user's past predictions in reverse chronological order
    
    Args:
        user: Authenticated user from token
        service: PredictionService instance
        limit: Number of records to return (max 100)
        offset: Pagination offset
        
    Returns:
        List of prediction records
        
    Raises:
        HTTPException: On authentication or database errors
    """
    
    try:
        user_id = user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session",
            )
        
        logger.info(
            "Fetching prediction history for user %s (limit=%d, offset=%d)",
            user_id,
            limit,
            offset,
        )
        
        predictions = await service.get_user_predictions(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        
        return predictions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to retrieve prediction history")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve prediction history",
        ) from e
