from typing import Any

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    """Response model for prediction results"""
    prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float]


class PredictionResultResponse(BaseModel):
    """Response model for saved prediction with ID"""
    id: str
    user_id: str
    prediction: str
    confidence: float
    probabilities: dict[str, float] | None = None
    image_url: str | None = None
    created_at: str
    updated_at: str


class PredictionErrorResponse(BaseModel):
    """Response model for prediction errors"""
    detail: str
    error_type: str | None = None


class ReportIssueResponse(BaseModel):
    """Response model for issue reports generated from prediction + LLM"""
    issue_type: str
    severity: str
    complaint: str
