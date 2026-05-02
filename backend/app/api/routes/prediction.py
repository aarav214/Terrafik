import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.supabase import get_supabase_service_client
from app.schemas.prediction import PredictionResultResponse, PredictionErrorResponse
from app.services.prediction import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])
logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


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
