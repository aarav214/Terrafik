"""
Example script to test the Road Issue Prediction API

This script demonstrates how to:
1. Login with Supabase
2. Get an access token
3. Upload an image and get a prediction
4. Retrieve prediction history

Requirements:
    pip install supabase requests python-dotenv

Setup:
    1. Create a test image or use an existing one
    2. Set SUPABASE_URL, SUPABASE_ANON_KEY, API_URL, and TEST_USER_EMAIL/PASSWORD in .env
    3. Run: python test_prediction_api.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from supabase import create_client

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "testpassword123")


def login_with_supabase() -> str:
    """
    Login with Supabase and return access token.
    
    Returns:
        Access token for API requests
    """
    
    print(f"\n🔐 Logging in as {TEST_USER_EMAIL}...")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        response = supabase.auth.sign_in_with_password({
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        })
        
        access_token = response.session.access_token
        user_id = response.user.id
        
        print(f"✅ Login successful!")
        print(f"   User ID: {user_id}")
        print(f"   Token: {access_token[:20]}...")
        
        return access_token
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print(f"\nMake sure:")
        print(f"  1. SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")
        print(f"  2. User {TEST_USER_EMAIL} exists in Supabase")
        print(f"  3. Password is correct")
        sys.exit(1)


def upload_and_predict(access_token: str, image_path: str) -> dict:
    """
    Upload image and get prediction.
    
    Args:
        access_token: Supabase access token
        image_path: Path to image file
        
    Returns:
        Prediction result
    """
    
    print(f"\n📤 Uploading image: {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        print(f"   Create a test image first")
        sys.exit(1)
    
    try:
        with open(image_path, "rb") as f:
            files = {
                "file": (os.path.basename(image_path), f, "image/jpeg")
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.post(
                f"{API_URL}/predictions/predict",
                headers=headers,
                files=files,
                timeout=30,
            )
        
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n✅ Prediction successful!")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Probabilities:")
        for class_name, prob in result['probabilities'].items():
            print(f"     - {class_name}: {prob:.2%}")
        print(f"   Saved ID: {result['id']}")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API error: {e}")
        print(f"   Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)


def get_prediction_history(access_token: str, limit: int = 5) -> list[dict]:
    """
    Get prediction history.
    
    Args:
        access_token: Supabase access token
        limit: Number of records to retrieve
        
    Returns:
        List of predictions
    """
    
    print(f"\n📋 Fetching prediction history (limit={limit})...")
    
    try:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(
            f"{API_URL}/predictions/history",
            headers=headers,
            params={"limit": limit},
        )
        
        response.raise_for_status()
        
        predictions = response.json()
        
        if not predictions:
            print(f"   No predictions found")
            return []
        
        print(f"✅ Retrieved {len(predictions)} predictions:")
        for pred in predictions:
            print(f"\n   ID: {pred['id']}")
            print(f"   Prediction: {pred['prediction']}")
            print(f"   Confidence: {pred['confidence']:.2%}")
            print(f"   Created: {pred['created_at']}")
        
        return predictions
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ API error: {e}")
        print(f"   Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to get history: {e}")
        sys.exit(1)


def main():
    """Run all tests"""
    
    print("=" * 60)
    print("Road Issue Prediction API - Test Script")
    print("=" * 60)
    
    # Check environment
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Missing environment variables!")
        print("   Set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
        sys.exit(1)
    
    print(f"\n🔧 Configuration:")
    print(f"   API URL: {API_URL}")
    print(f"   Supabase URL: {SUPABASE_URL}")
    print(f"   Test Email: {TEST_USER_EMAIL}")
    
    # Check API is running
    try:
        response = requests.head(f"{API_URL}/")
        if response.status_code >= 400:
            print(f"\n⚠️  API may not be running: HTTP {response.status_code}")
    except Exception as e:
        print(f"\n⚠️  Cannot reach API at {API_URL}")
        print(f"   Error: {e}")
        print(f"   Make sure backend is running: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Login and get token
    access_token = login_with_supabase()
    
    # Create a simple test image if it doesn't exist
    test_image = Path(__file__).parent / "test_image.jpg"
    if not test_image.exists():
        print(f"\n⚠️  Test image not found: {test_image}")
        print(f"   Please provide an image file to test")
        print(f"   Usage: python test_prediction_api.py <image_path>")
        sys.exit(1)
    
    # Upload and predict
    image_path = str(test_image) if len(sys.argv) < 2 else sys.argv[1]
    upload_and_predict(access_token, image_path)
    
    # Get history
    get_prediction_history(access_token, limit=5)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
