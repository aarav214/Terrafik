# Road Issue Prediction API - Backend Setup Guide

## Overview

The Road Issue Prediction API enables authenticated users to upload images and receive AI-powered predictions about road issues (potholes, garbage, waterlogging, etc.).

## Architecture

```
Frontend (Next.js)
    ↓ (Bearer Token + Image File)
API Route (/predictions/predict)
    ↓
Authentication (get_current_user)
    ↓
Prediction Service
    ├→ Call ML Backend (FastAPI)
    └→ Save to Supabase Database
    ↓
Return Result to Frontend
```

## Setup Instructions

### 1. Environment Variables

Add these to `.env` file in the `backend/` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# ML Backend URL (adjust port/host as needed)
ML_BACKEND_URL=http://localhost:8000

# CORS Origins (for frontend URLs)
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### 2. Database Setup

Run the SQL migration in your Supabase SQL Editor:

```sql
-- Copy contents of: backend/migrations/01_create_predictions_table.sql
-- and execute in Supabase dashboard
```

This creates:
- `predictions` table with user_id, prediction, confidence, probabilities, and timestamps
- Indexes for efficient queries
- Row-Level Security (RLS) policies for user data isolation

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Added packages:
- `python-multipart>=0.0.6` - For file uploads in FastAPI
- `requests>=2.31.0` - For calling ML backend

### 4. Update Supabase with New Permissions

The API uses the service role key to verify tokens, but RLS policies ensure users can only access their own predictions.

## API Endpoints

### 1. Predict (File Upload + Prediction)

**Endpoint:** `POST /predictions/predict`

**Authentication:** Required (Bearer Token)

**Request:**
- Content-Type: `multipart/form-data`
- File field: `file` (jpg, png only, max 10MB)

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

**Example Request (Python):**
```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

files = {
    "file": ("pothole.jpg", open("pothole.jpg", "rb"), "image/jpeg")
}

response = requests.post(
    "http://localhost:8000/predictions/predict",
    headers=headers,
    files=files
)

result = response.json()
print(result)
```

**Response (200 OK):**
```json
{
  "id": "123456",
  "user_id": "user-uuid-here",
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

**Error Responses:**

- `400 Bad Request` - Invalid file type or empty file
  ```json
  {
    "detail": "Invalid file type. Accepted: .jpg, .jpeg, .png"
  }
  ```

- `401 Unauthorized` - Missing or invalid token
  ```json
  {
    "detail": "Invalid or expired token"
  }
  ```

- `413 Payload Too Large` - File exceeds 10MB
  ```json
  {
    "detail": "File size exceeds 10MB limit"
  }
  ```

- `503 Service Unavailable` - ML backend connection failed
  ```json
  {
    "detail": "ML backend is unavailable"
  }
  ```

### 2. Get Prediction History

**Endpoint:** `GET /predictions/history`

**Authentication:** Required (Bearer Token)

**Query Parameters:**
- `limit` (optional, default=10, max=100): Number of records to return
- `offset` (optional, default=0): Pagination offset

**Example Request:**
```bash
curl -X GET "http://localhost:8000/predictions/history?limit=20&offset=0" \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN"
```

**Response (200 OK):**
```json
[
  {
    "id": "123456",
    "user_id": "user-uuid-here",
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
]
```

## Code Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # Authentication dependencies
│   │   └── routes/
│   │       ├── auth.py             # Authentication endpoints
│   │       └── prediction.py        # Prediction endpoints (NEW)
│   ├── schemas/
│   │   ├── auth.py                 # Auth request/response models
│   │   └── prediction.py           # Prediction models (NEW)
│   ├── services/
│   │   ├── __init__.py             # Services package (NEW)
│   │   └── prediction.py           # Prediction business logic (NEW)
│   ├── core/
│   │   ├── config.py               # Settings (UPDATED)
│   │   └── supabase.py             # Supabase client
│   └── main.py                     # FastAPI app setup (UPDATED)
├── migrations/
│   └── 01_create_predictions_table.sql  # DB schema (NEW)
└── requirements.txt                # Dependencies (UPDATED)
```

## File Upload Validation

- **Accepted Types:** `.jpg`, `.jpeg`, `.png`
- **Max Size:** 10 MB
- **Content-Type Detection:** Based on file extension

## ML Backend Integration

The service expects an ML backend at the URL specified in `ML_BACKEND_URL`:

**ML Backend Requirements:**

- Endpoint: `POST /predict`
- Request: multipart/form-data with field name `file`
- Response: JSON with structure:
  ```json
  {
    "prediction": "class_name",
    "confidence": 0.95,
    "probabilities": {
      "class1": 0.02,
      "class2": 0.95,
      "class3": 0.03
    }
  }
  ```

## Running the API

```bash
cd backend

# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (with Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

## Testing

```bash
# Start the backend
cd backend
uvicorn app.main:app --reload

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer TEST_TOKEN" \
  -F "file=@test_image.jpg"
```

## Database Queries

View recent predictions:
```sql
SELECT id, user_id, prediction, confidence, created_at
FROM predictions
ORDER BY created_at DESC
LIMIT 10;
```

Get predictions for a specific user:
```sql
SELECT * FROM predictions
WHERE user_id = 'specific-user-id'
ORDER BY created_at DESC;
```

Average confidence by prediction type:
```sql
SELECT prediction, AVG(confidence) as avg_confidence, COUNT(*) as count
FROM predictions
GROUP BY prediction
ORDER BY count DESC;
```

## Error Handling

The API includes comprehensive error handling:

- **Validation Errors:** Returns `400 Bad Request` with specific error message
- **Authentication Errors:** Returns `401 Unauthorized` for missing/invalid tokens
- **File Size/Type Errors:** Returns `400 Bad Request`
- **ML Backend Errors:** Returns `503 Service Unavailable`
- **Database Errors:** Returns `500 Internal Server Error`

All errors include a `detail` field with a user-friendly message.

## Logging

The API logs:
- Each prediction request with user ID and filename
- Prediction results
- Database saves
- All errors with full stack traces

Check logs:
```bash
# Development (logs to console)
# Production (configure based on your deployment)
```

## Security Considerations

1. **Authentication:** Uses Supabase JWT tokens verified server-side
2. **RLS Policies:** Users can only access/modify their own predictions
3. **File Validation:** Strict file type and size checks
4. **Input Sanitization:** All user inputs validated
5. **CORS:** Configured based on `CORS_ORIGINS` environment variable
6. **Timeout:** ML backend requests timeout after 30 seconds

## Troubleshooting

### ML Backend Connection Failed
- Check `ML_BACKEND_URL` environment variable
- Verify ML backend is running
- Check firewall/network connectivity
- Look for timeout errors in logs

### Database Connection Failed
- Verify Supabase credentials in `.env`
- Check internet connection
- Verify Supabase project is active
- Check RLS policies are correctly set

### Authentication Failures
- Ensure frontend sends valid bearer token
- Token must be from Supabase auth
- Token must not be expired
- Check token format: `Authorization: Bearer TOKEN`

### File Upload Issues
- Check file size (max 10MB)
- Verify file type (jpg/png only)
- Check Content-Type header is `multipart/form-data`
- Ensure `python-multipart` is installed

## Next Steps

1. ✅ Set up environment variables
2. ✅ Run database migration
3. ✅ Install dependencies
4. ✅ Start backend server
5. ✅ Test endpoints with provided examples
6. Implement frontend components (separate from this backend setup)
