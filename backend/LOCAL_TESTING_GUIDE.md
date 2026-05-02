# 🧪 Local Testing Guide

This guide explains how to test the Road Issue Prediction backend locally before integrating with the frontend.

---

## 🎯 What We'll Test

1. ✅ Model initialization and inference
2. ✅ API endpoint accessibility  
3. ✅ Authentication with Supabase
4. ✅ File upload and validation
5. ✅ ML prediction pipeline
6. ✅ Database operations
7. ✅ Error handling

---

## 📝 Test 1: Model Initialization

Verify the PyTorch model loads correctly.

**Terminal Command:**
```bash
cd backend
source venv/bin/activate

python3 << 'EOF'
from app.ml.model import get_ml_model

print("Loading ML model...")
model = get_ml_model()

if model.is_loaded():
    print("✅ Model loaded successfully!")
    print(f"   Device: {model.device}")
    print(f"   Model: {model.model}")
    print(f"   Classes: {['garbage', 'potholes', 'waterlogging']}")
else:
    print("❌ Model failed to load")
    exit(1)
EOF
```

**Expected Output:**
```
Loading ML model...
✅ Model loaded successfully!
   Device: cpu
   Model: ResNet(...)
   Classes: ['garbage', 'potholes', 'waterlogging']
```

---

## 📝 Test 2: API Server Health Check

Verify the server starts and responds.

**Terminal 1 - Start Server:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Terminal 2 - Health Check:**
```bash
# Check if server is running
curl http://localhost:8000/

# Or using Python
python3 << 'EOF'
import requests

response = requests.get("http://localhost:8000/docs")
print(f"Server Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Server is running")
else:
    print("❌ Server error")
EOF
```

---

## 📝 Test 3: Swagger UI

The easiest way to test endpoints visually.

**Open in Browser:**
```
http://localhost:8000/docs
```

**You should see:**
- ✅ Swagger UI dashboard
- ✅ All endpoints listed
- ✅ Authentication option (lock icon)

---

## 📝 Test 4: Authentication

Test Supabase token verification.

**Using Test Script:**
```bash
cd backend
source venv/bin/activate

python3 << 'EOF'
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Load credentials
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("Supabase Configuration:")
print(f"  URL: {url}")
print(f"  Anon Key: {key[:20]}...")
print(f"  Service Key: {service_key[:20]}...")

# Test connection
if url and key:
    client = create_client(url, key)
    print("\n✅ Supabase credentials loaded successfully")
else:
    print("\n❌ Missing Supabase credentials in .env")
    exit(1)
EOF
```

---

## 📝 Test 5: File Upload Endpoint

Test the prediction endpoint with a sample image.

**Prerequisites:**
- Have a test image (jpg or png)
- Backend server running

**Create Test Image:**
```bash
# If you don't have a test image, create a simple one
python3 << 'EOF'
from PIL import Image
import numpy as np

# Create a dummy image (224x224)
img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
img.save("test_image.jpg")
print("✅ Test image created: test_image.jpg")
EOF
```

**Test With Swagger UI:**
1. Open `http://localhost:8000/docs`
2. Find endpoint: `POST /predictions/predict`
3. Click **"Try it out"**
4. Enter Bearer token (from Supabase login)
5. Select test image file
6. Click **"Execute"**

**Expected Response:**
```json
{
  "id": "123456",
  "user_id": "uuid-string",
  "prediction": "potholes",
  "confidence": 0.92,
  "probabilities": {
    "garbage": 0.05,
    "potholes": 0.92,
    "waterlogging": 0.03
  },
  "image_url": null,
  "created_at": "2024-05-02T10:30:00Z",
  "updated_at": "2024-05-02T10:30:00Z"
}
```

**Test With cURL:**
```bash
# First, get a Supabase token
# Then run:

curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test_image.jpg"
```

---

## 📝 Test 6: Prediction History

Test retrieving user's predictions.

**Using Swagger UI:**
1. Open `http://localhost:8000/docs`
2. Find endpoint: `GET /predictions/history`
3. Click **"Try it out"**
4. Enter Bearer token
5. Set limit and offset (optional)
6. Click **"Execute"**

**Expected Response:**
```json
[
  {
    "id": "123456",
    "user_id": "uuid-string",
    "prediction": "potholes",
    "confidence": 0.92,
    ...
  }
]
```

**Using cURL:**
```bash
curl -X GET "http://localhost:8000/predictions/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📝 Test 7: Full Automation Test

Run the provided test script for full workflow.

**Script Location:** `test_prediction_api.py`

**Run Test:**
```bash
cd backend
source venv/bin/activate

python test_prediction_api.py test_image.jpg
```

**What it tests:**
1. ✅ Supabase login
2. ✅ File upload
3. ✅ Prediction
4. ✅ History retrieval
5. ✅ Error handling

**Expected Output:**
```
============================================================
Road Issue Prediction API - Test Script
============================================================

🔧 Configuration:
   API URL: http://localhost:8000
   Supabase URL: https://your-project.supabase.co
   Test Email: test@example.com

🔐 Logging in as test@example.com...
✅ Login successful!
   User ID: uuid-123...
   Token: eyJhbGc...

📤 Uploading image: test_image.jpg...
✅ Prediction successful!
   Prediction: potholes
   Confidence: 92.34%
   Probabilities:
     - garbage: 5.21%
     - potholes: 92.34%
     - waterlogging: 2.45%
   Saved ID: 12345

📋 Fetching prediction history (limit=5)...
✅ Retrieved 1 predictions:
   ID: 12345
   Prediction: potholes
   Confidence: 92.34%
   Created: 2024-05-02T10:30:00Z

============================================================
✅ All tests completed!
============================================================
```

---

## 📝 Test 8: Error Handling

Test various error scenarios.

### Test 8a: Invalid File Type

**Command:**
```bash
# Create a text file
echo "invalid" > invalid.txt

# Try to upload it
curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@invalid.txt"
```

**Expected Response (400):**
```json
{
  "detail": "Invalid file type. Accepted: .jpg, .jpeg, .png"
}
```

### Test 8b: Missing Authentication

**Command:**
```bash
curl -X POST http://localhost:8000/predictions/predict \
  -F "file=@test_image.jpg"
```

**Expected Response (401):**
```json
{
  "detail": "Missing Authorization header"
}
```

### Test 8c: Invalid Token

**Command:**
```bash
curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer invalid_token_here" \
  -F "file=@test_image.jpg"
```

**Expected Response (401):**
```json
{
  "detail": "Invalid or expired token"
}
```

### Test 8d: File Too Large

**Commands:**
```bash
# Create a large file (>10MB)
dd if=/dev/zero of=large_file.jpg bs=1M count=15

# Try to upload
curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@large_file.jpg"
```

**Expected Response (413):**
```json
{
  "detail": "File size exceeds 10MB limit"
}
```

---

## 📝 Test 9: Database Operations

Verify predictions are saved to Supabase.

**Using Supabase Dashboard:**
1. Go to **Supabase → SQL Editor**
2. Run query:
   ```sql
   SELECT id, user_id, prediction, confidence, created_at
   FROM predictions
   ORDER BY created_at DESC
   LIMIT 10;
   ```

**Expected Output:**
```
id   user_id                          prediction  confidence  created_at
123  12345678-1234-1234-1234-123456  potholes    0.92        2024-05-02...
124  12345678-1234-1234-1234-123456  garbage     0.85        2024-05-02...
```

**Check Row-Level Security (RLS):**

```sql
-- This should only return YOUR predictions
SELECT COUNT(*) FROM predictions WHERE user_id = 'your-user-id';

-- Try to query another user's data (should fail or be empty)
SELECT * FROM predictions WHERE user_id = 'other-user-id';
```

---

## 📝 Test 10: Performance Testing

Measure API response times.

**Script:**
```bash
python3 << 'EOF'
import requests
import time
import json
from datetime import datetime

token = "YOUR_TOKEN_HERE"

# Test parameters
num_tests = 5
image_path = "test_image.jpg"

print("Performance Test Results")
print("=" * 50)
print(f"Test Date: {datetime.now()}")
print(f"Number of Tests: {num_tests}")
print()

times = []

for i in range(num_tests):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        headers = {'Authorization': f'Bearer {token}'}
        
        start = time.time()
        response = requests.post(
            'http://localhost:8000/predictions/predict',
            headers=headers,
            files=files
        )
        elapsed = time.time() - start
        times.append(elapsed)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Test {i+1}: ✅ {elapsed:.3f}s - {result['prediction']} ({result['confidence']:.1%})")
        else:
            print(f"Test {i+1}: ❌ {response.status_code}")

print()
print("Summary:")
print(f"  Min: {min(times):.3f}s")
print(f"  Max: {max(times):.3f}s")
print(f"  Avg: {sum(times)/len(times):.3f}s")
EOF
```

---

## 🐛 Debugging Tips

### View Logs

The backend logs all activity. Look for:

```
INFO:     POST /predictions/predict -> 200
INFO app.ml.model: ML inference successful: potholes (confidence: 0.92)
INFO app.services.prediction: Prediction saved for user X: id_123
ERROR app.ml.model: Failed to load model
WARNING app.api.routes.prediction: User without ID attempted prediction
```

### Check Model Loading

```bash
python3 << 'EOF'
import torch

print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
EOF
```

### Test Individual Components

```bash
# Test Supabase connection
python3 -c "from app.core.supabase import get_supabase_client; print('✅ Supabase OK')"

# Test ML model
python3 -c "from app.ml.model import get_ml_model; get_ml_model(); print('✅ ML Model OK')"

# Test FastAPI app
python3 -c "from app.main import app; print('✅ FastAPI OK')"
```

---

## ✅ Test Checklist

- [ ] Model loads without errors
- [ ] Server starts and responds
- [ ] Swagger UI accessible
- [ ] Can authenticate with Supabase
- [ ] Can upload and predict
- [ ] Can retrieve history
- [ ] Errors handled gracefully
- [ ] Database saves predictions
- [ ] Row-Level Security working
- [ ] Performance acceptable

---

## 🎯 Next Steps

After successful local testing:

1. **Document results** - Note any issues found
2. **Integrate frontend** - Connect to React/frontend app
3. **Load testing** - Test with higher volume
4. **Production deployment** - Deploy to staging/production
5. **Monitor** - Set up logging and alerting

---

## 📞 Common Test Issues

| Issue | Solution |
|-------|----------|
| Model not loading | Check `models/road_model.pth` exists |
| Token invalid | Get fresh token from Supabase |
| Database error | Run migration SQL in Supabase |
| CORS error | Check `CORS_ORIGINS` in `.env` |
| Port in use | Change to port 8001: `--port 8001` |
| Memory error | Reduce model size or increase RAM |

---

## 🎉 Ready to Deploy

Once all tests pass, you're ready to:
- Deploy to production server
- Connect frontend application
- Start accepting user predictions

Happy testing! 🧪
