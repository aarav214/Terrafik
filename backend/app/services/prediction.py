import logging
import io
from typing import Any

from supabase import Client

from app.ml.model import get_ml_model

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for handling road issue predictions using local ML model"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.ml_model = get_ml_model()
    
    async def predict(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Process prediction request:
        1. Run inference on image using local ML model
        2. Get prediction result
        3. Save result to Supabase
        
        Args:
            file_content: Binary file content
            filename: Original filename
            user_id: Supabase user ID
            image_url: Optional URL of image storage
            
        Returns:
            Dictionary containing prediction result with ID
            
        Raises:
            Exception: If ML model or database operation fails
        """
        
        # Step 1: Run ML model inference
        prediction_data = await self._run_inference(file_content, filename)
        
        # Step 2: Save to Supabase
        saved_result = await self._save_prediction(
            user_id=user_id,
            prediction=prediction_data["prediction"],
            confidence=prediction_data["confidence"],
            probabilities=prediction_data["probabilities"],
            image_url=image_url,
        )
        
        return saved_result
    
    async def _run_inference(
        self,
        file_content: bytes,
        filename: str,
    ) -> dict[str, Any]:
        """
        Run ML model inference on image.
        
        Args:
            file_content: Binary file content
            filename: Original filename
            
        Returns:
            Dictionary with prediction, confidence, and probabilities
            
        Raises:
            Exception: If inference fails
        """
        
        try:
            # Run model prediction
            result = self.ml_model.predict(file_content)
            
            logger.info(
                "ML inference successful: %s (confidence: %.2f)",
                result["prediction"],
                result["confidence"],
            )
            
            return result
            
        except Exception as e:
            logger.error("ML inference failed: %s", str(e))
            raise RuntimeError(f"Failed to process image with ML model: {str(e)}") from e
    
    async def _save_prediction(
        self,
        user_id: str,
        prediction: str,
        confidence: float,
        probabilities: dict[str, float],
        image_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Save prediction result to Supabase.
        
        Args:
            user_id: Supabase user ID
            prediction: Predicted class
            confidence: Confidence score
            probabilities: Dict of all class probabilities
            image_url: Optional image URL
            
        Returns:
            Saved prediction record
            
        Raises:
            Exception: If database operation fails
        """
        
        try:
            data = {
                "user_id": user_id,
                "prediction": prediction,
                "confidence": confidence,
                "probabilities": probabilities,
            }
            
            if image_url:
                data["image_url"] = image_url
            
            # Insert into predictions table
            response = self.supabase.table("predictions").insert(data).execute()
            
            if not response.data:
                raise ValueError("Failed to save prediction to database")
            
            saved_record = response.data[0]
            # Ensure ID is a string to match response schema
            if "id" in saved_record and not isinstance(saved_record["id"], str):
                try:
                    saved_record["id"] = str(saved_record["id"])
                except Exception:
                    # fallback: leave as-is; Pydantic will raise a clear error
                    pass
            logger.info(
                "Prediction saved for user %s: %s",
                user_id,
                saved_record.get("id"),
            )
            
            return saved_record
            
        except Exception as e:
            logger.error("Failed to save prediction: %s", str(e))
            raise
    
    async def get_user_predictions(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Retrieve prediction history for a user.
        
        Args:
            user_id: Supabase user ID
            limit: Number of records to return
            offset: Offset for pagination
            
        Returns:
            List of prediction records
        """
        
        try:
            response = (
                self.supabase.table("predictions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            # Coerce ids to strings for consistency with response schemas
            records = response.data or []
            for r in records:
                if "id" in r and not isinstance(r["id"], str):
                    try:
                        r["id"] = str(r["id"])
                    except Exception:
                        pass
            return records
            
        except Exception as e:
            logger.error("Failed to retrieve predictions: %s", str(e))
            raise
