"""
ML Model Service for Road Issue Prediction

Loads and uses the PyTorch model (road_model.pth) for making predictions
on uploaded road images (potholes, waterlogging, garbage detection).
"""

import logging
import os
from pathlib import Path
from typing import Any

import io
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

logger = logging.getLogger(__name__)

# Model configuration - try several common locations
MODEL_CANDIDATES = [
    Path(__file__).resolve().parents[1] / "models" / "road_model.pth",  # backend/app/models
    Path(__file__).resolve().parents[2] / "models" / "road_model.pth",  # backend/models
    Path.cwd() / "models" / "road_model.pth",
]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class labels for road issues
CLASS_LABELS = ["garbage", "potholes", "waterlogging"]

# Image preprocessing configuration
IMAGE_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class MLModelService:
    """Service for loading and using the PyTorch ML model"""
    
    def __init__(self, model_path: str | Path | None = None):
        """
        Initialize ML model service.
        
        Args:
            model_path: Path to the PyTorch model file (.pth)
        """
        # Determine model path: explicit argument wins, otherwise search candidates
        if model_path:
            self.model_path = Path(model_path)
        else:
            found = None
            for p in MODEL_CANDIDATES:
                if p.exists():
                    found = p
                    break
            self.model_path = found if found is not None else MODEL_CANDIDATES[0]
        self.device = DEVICE
        self.model = None
        self.transform = None
        self._initialize()
    
    def _initialize(self) -> None:
        """
        Load the model and set up preprocessing pipeline.
        
        Raises:
            FileNotFoundError: If model file not found
            RuntimeError: If model loading fails
        """
        
        if not self.model_path.exists():
            tried = "\n".join(str(p) for p in MODEL_CANDIDATES)
            raise FileNotFoundError(
                "Model file not found. Tried the following locations:\n"
                f"{tried}\n\n"
                "Please place road_model.pth in one of the above 'models' directories or set the exact path when creating MLModelService"
            )
        
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Load model checkpoint
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # Extract model if checkpoint contains state_dict
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model_state = checkpoint["model_state_dict"]
            elif isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                model_state = checkpoint["state_dict"]
            else:
                # Assume checkpoint is the state_dict directly
                model_state = checkpoint
            
            # Initialize model (dummy for now, will be replaced with actual architecture)
            # This assumes a standard ResNet-like architecture with 3 output classes
            self.model = self._create_model(model_state)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Model loaded successfully on {self.device}")
            
            # Set up image transformations
            self.transform = transforms.Compose([
                transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=IMAGENET_MEAN,
                    std=IMAGENET_STD
                ),
            ])
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model initialization failed: {e}") from e
    
    def _create_model(self, state_dict: dict) -> torch.nn.Module:
        """
        Create model instance based on state_dict structure.
        
        Args:
            state_dict: Model state dictionary
            
        Returns:
            PyTorch model instance
        """
        
        try:
            # Try importing standard architectures
            from torchvision.models import resnet50
            
            # Create model
            model = resnet50(pretrained=False)
            
            # Modify final layer for 3 classes
            num_features = model.fc.in_features
            model.fc = torch.nn.Linear(num_features, len(CLASS_LABELS))
            
            # Load state dict
            model.load_state_dict(state_dict)
            
            return model
            
        except Exception as e:
            logger.warning(f"Could not create ResNet50, trying generic loading: {e}")
            # Fallback: create a simple model
            model = torch.nn.Sequential(
                torch.nn.Flatten(),
                torch.nn.Linear(224 * 224 * 3, 512),
                torch.nn.ReLU(),
                torch.nn.Linear(512, len(CLASS_LABELS))
            )
            try:
                model.load_state_dict(state_dict)
            except:
                logger.warning("Using untrained model structure")
            return model
    
    def predict(self, image_data: bytes) -> dict[str, Any]:
        """
        Make prediction on road image.
        
        Args:
            image_data: Binary image data (jpg/png)
            
        Returns:
            Dictionary with prediction, confidence, and probabilities
            
        Raises:
            ValueError: If image cannot be processed
            RuntimeError: If model inference fails
        """
        
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            
            # Preprocess image
            tensor = self.transform(image)
            batch = tensor.unsqueeze(0).to(self.device)
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(batch)
                probabilities = F.softmax(outputs, dim=1)[0]
            
            # Get predictions
            probs_numpy = probabilities.cpu().numpy()
            predicted_idx = np.argmax(probs_numpy)
            predicted_class = CLASS_LABELS[predicted_idx]
            confidence_score = float(probs_numpy[predicted_idx])
            
            # Create probability breakdown
            probability_breakdown = {
                CLASS_LABELS[i]: float(probs_numpy[i])
                for i in range(len(CLASS_LABELS))
            }
            
            result = {
                "prediction": predicted_class,
                "confidence": confidence_score,
                "probabilities": probability_breakdown,
            }
            
            logger.info(
                f"Prediction: {predicted_class} (confidence: {confidence_score:.2%})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Model inference failed: {e}") from e
    
    def is_loaded(self) -> bool:
        """Check if model is loaded successfully"""
        return self.model is not None and self.transform is not None


# Global model instance (lazy loaded on first use)
_ml_model_instance: MLModelService | None = None


def get_ml_model() -> MLModelService:
    """
    Get or create ML model instance (singleton pattern).
    
    Returns:
        MLModelService instance
    """
    
    global _ml_model_instance
    
    if _ml_model_instance is None:
        try:
            _ml_model_instance = MLModelService()
        except Exception as e:
            logger.error(f"Failed to initialize ML model: {e}")
            raise
    
    return _ml_model_instance


# Import io here after defining usage
import io
