"""
Backend Implementation Summary: Road Issue Prediction Feature

Files Created/Modified:
======================

✅ NEW FILES CREATED:
  1. app/schemas/prediction.py
     - PredictionResponse: ML backend prediction format
     - PredictionResultResponse: Saved prediction in database
     - PredictionErrorResponse: Error response format

  2. app/services/prediction.py
     - PredictionService class with methods:
       * predict(): Main prediction handler
       * _call_ml_backend(): Send file to ML backend
       * _save_prediction(): Save to Supabase database
       * get_user_predictions(): Retrieve user's prediction history

  3. app/api/routes/prediction.py
     - POST /predictions/predict - Upload image and get prediction
     - GET /predictions/history - Get user's prediction history
     - File validation, authentication, error handling

  4. app/services/__init__.py
     - Package initialization file

  5. migrations/01_create_predictions_table.sql
     - SQL schema for predictions table
     - Row-Level Security (RLS) policies
     - Indexes for efficient queries

  6. PREDICTION_API_SETUP.md
     - Complete setup and documentation
     - API endpoints documentation
     - Example requests/responses
     - Troubleshooting guide

  7. test_prediction_api.py
     - Test script for the API
     - Login → Upload → Get predictions
     - Example usage

✅ MODIFIED FILES:
  1. requirements.txt
     - Added: python-multipart>=0.0.6 (for file uploads)
     - Added: requests>=2.31.0 (for calling ML backend)

  2. app/core/config.py
     - Added: ml_backend_url setting (default: http://localhost:8000)
     - Reads from ML_BACKEND_URL environment variable

  3. app/main.py
     - Added: Import for prediction router
     - Added: Include prediction router to FastAPI app

API Endpoints
=============

1. POST /predictions/predict
   - Authentication: Bearer token (Supabase)
   - Input: multipart/form-data with "file"
   - Validation: jpg/png only, max 10MB
   - Process: Validate → Call ML backend → Save to DB → Return result
   - Response: Prediction with ID and metadata

2. GET /predictions/history
   - Authentication: Bearer token (Supabase)
   - Query params: limit (max 100), offset
   - Response: List of user's past predictions

Database Schema
===============

predictions table:
- id (bigserial, PK)
- user_id (uuid FK → auth.users)
- prediction (text)
- confidence (float8, 0-1)
- probabilities (jsonb)
- image_url (text, nullable)
- created_at (timestamptz)
- updated_at (timestamptz)

Indexes:
- idx_predictions_user_id
- idx_predictions_created_at
- idx_predictions_user_created

RLS Policies: Users can only access their own predictions

Environment Variables
=====================

Required:
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_ANON_KEY=your_anon_key
  SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

Optional:
  ML_BACKEND_URL=http://localhost:8000 (default)
  CORS_ORIGINS=[...] (default: all origins)

Setup Checklist
===============

1. ✅ Install dependencies
   pip install -r requirements.txt

2. ✅ Create database table
   - Execute: migrations/01_create_predictions_table.sql

3. ✅ Set environment variables
   - SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
   - ML_BACKEND_URL (if not localhost:8000)

4. ✅ Start backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

5. ✅ Test API
   python test_prediction_api.py <image_path>

Feature Highlights
==================

✨ Authentication & Authorization
   - Uses Supabase JWT tokens
   - Server-side token verification
   - Row-Level Security for data isolation

✨ File Handling
   - Multipart file upload support
   - Type validation (jpg/png only)
   - Size limit (10MB)
   - Proper error messages

✨ ML Backend Integration
   - Calls FastAPI ML backend
   - 30-second timeout
   - Proper error handling
   - Response validation

✨ Database Management
   - Automatic schema with RLS
   - Efficient indexes
   - Timestamp tracking
   - Full audit trail

✨ Error Handling
   - Comprehensive try-catch blocks
   - User-friendly error messages
   - Proper HTTP status codes
   - Full logging for debugging

✨ Code Quality
   - Type hints throughout
   - Clear docstrings
   - Separated concerns (schemas, services, routes)
   - Follows FastAPI best practices
   - Extensive error handling

API Response Examples
=====================

Success Response (200 OK):
{
  "id": "123456",
  "user_id": "uuid-here",
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

Error Response (400 Bad Request):
{
  "detail": "Invalid file type. Accepted: .jpg, .jpeg, .png"
}

Error Response (401 Unauthorized):
{
  "detail": "Invalid or expired token"
}

Error Response (503 Service Unavailable):
{
  "detail": "ML backend is unavailable"
}

Testing
=======

Unit Test Template:
```python
import requests

# 1. Login
token = login_with_supabase()

# 2. Upload prediction
response = requests.post(
    "http://localhost:8000/predictions/predict",
    headers={"Authorization": f"Bearer {token}"},
    files={"file": open("image.jpg", "rb")}
)
assert response.status_code == 200
prediction = response.json()

# 3. Verify response
assert "id" in prediction
assert "prediction" in prediction
assert prediction["confidence"] > 0

# 4. Get history
history = requests.get(
    "http://localhost:8000/predictions/history",
    headers={"Authorization": f"Bearer {token}"}
).json()
assert len(history) > 0
```

Running the Backend
===================

Development:
  cd backend
  uvicorn app.main:app --reload

Production (Gunicorn):
  cd backend
  gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

Health Check:
  curl http://localhost:8000/docs  # Swagger UI

Frontend Integration
====================

The frontend should:
1. Get Supabase session token after user login
2. Send Bearer token in Authorization header
3. Use multipart/form-data for file upload
4. Handle loading states during prediction
5. Display results from response
6. Use /predictions/history for past predictions

Example Frontend Code:
```javascript
// Get token from Supabase session
const { data: { session } } = await supabase.auth.getSession();
const token = session?.access_token;

// Upload and predict
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/predictions/predict', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

const prediction = await response.json();
console.log(prediction);
```

Common Issues & Solutions
==========================

Issue: "ML backend is unavailable"
→ Check ML_BACKEND_URL environment variable
→ Verify ML backend is running
→ Check network connectivity

Issue: "Invalid or expired token"
→ Get fresh token from Supabase
→ Verify token format: "Bearer TOKEN"
→ Check token expiration

Issue: "File size exceeds 10MB limit"
→ Compress image file
→ Use smaller images
→ Increase MAX_FILE_SIZE in prediction.py if needed

Issue: "Cannot connect to Supabase"
→ Check SUPABASE_URL and keys
→ Verify internet connection
→ Check Supabase project is active

Next Steps
==========

1. Run database migration:
   - Copy migrations/01_create_predictions_table.sql
   - Execute in Supabase SQL editor

2. Set environment variables in backend/.env:
   SUPABASE_URL=...
   SUPABASE_ANON_KEY=...
   SUPABASE_SERVICE_ROLE_KEY=...
   ML_BACKEND_URL=...

3. Start backend:
   cd backend && pip install -r requirements.txt
   uvicorn app.main:app --reload

4. Test endpoints:
   python test_prediction_api.py <image.jpg>

5. Frontend integration:
   - Implement file upload UI
   - Handle Supabase authentication
   - Call /predictions/predict endpoint
   - Display results
   - Show loading spinner during prediction
"""
