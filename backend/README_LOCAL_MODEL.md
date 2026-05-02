# 🚗 Road Issue Prediction Backend

Complete FastAPI backend for AI-powered road issue detection (potholes, garbage, waterlogging) with local PyTorch ML model integration.

**Latest Update:** Local ML model integration added - `road_model.pth`

---

## ⚡ Quick Start (5 minutes)

```bash
# 1. Prepare model
cp road_model.pth backend/models/

# 2. Setup environment
cd backend
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_key
CORS_ORIGINS=["http://localhost:3000"]
EOF

# 3. Run setup script (auto-installs dependencies)
bash setup.sh

# 4. Database migration
# Copy SQL from: migrations/01_create_predictions_table.sql
# Paste in: Supabase → SQL Editor → Run

# 5. Start server
uvicorn app.main:app --reload

# 6. Test it
python test_prediction_api.py image.jpg
```

**Server running:** http://localhost:8000/docs

---

## 📦 What's Included

### Core Features
- ✅ **Local ML Model Integration** - Uses PyTorch `road_model.pth` for instant predictions
- ✅ **Supabase Authentication** - JWT-based secure access
- ✅ **Row-Level Security** - Users only access their own predictions
- ✅ **File Upload & Validation** - jpg/png only, max 10MB
- ✅ **Prediction History** - Paginated access to past predictions
- ✅ **Error Handling** - Comprehensive validation and error messages
- ✅ **API Documentation** - Interactive Swagger UI at `/docs`

### Architecture
```
Upload Image
    ↓
Validate (file type, size)
    ↓
Load PyTorch Model (road_model.pth)
    ↓
Run Inference
    ↓
Save to Supabase
    ↓
Return Result
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Authentication middleware
│   │   └── routes/
│   │       ├── auth.py          # Login/signup
│   │       └── prediction.py     # Predictions
│   ├── ml/
│   │   ├── __init__.py
│   │   └── model.py             # PyTorch model service
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction.py        # Business logic
│   ├── schemas/
│   │   ├── auth.py
│   │   └── prediction.py        # Data models
│   ├── core/
│   │   ├── config.py            # Settings
│   │   └── supabase.py          # DB client
│   └── main.py                  # FastAPI app
├── models/
│   └── road_model.pth           # Your ML model
├── migrations/
│   └── 01_create_predictions_table.sql
├── setup.sh                     # Automated setup
├── test_prediction_api.py       # Test script
├── requirements.txt             # Dependencies
└── .env                         # Configuration (secret)
```

---

## 🚀 API Endpoints

### Predict
```
POST /predictions/predict
Authorization: Bearer {token}
Content-Type: multipart/form-data

Parameters:
  file: Image file (jpg/png, max 10MB)

Response (200):
{
  "id": "123",
  "prediction": "potholes",
  "confidence": 0.92,
  "probabilities": {
    "garbage": 0.05,
    "potholes": 0.92,
    "waterlogging": 0.03
  },
  "created_at": "2024-05-02T10:30:00Z"
}
```

### History
```
GET /predictions/history?limit=10&offset=0
Authorization: Bearer {token}

Response (200):
[
  {
    "id": "123",
    "prediction": "potholes",
    "confidence": 0.92,
    ...
  }
]
```

---

## 🔧 Setup Guide

### Prerequisites
- Python 3.10+
- Supabase account
- `road_model.pth` file
- 4GB+ RAM

### Step 1: Model File
```bash
mkdir -p backend/models
cp road_model.pth backend/models/
```

### Step 2: Environment
```bash
cd backend
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
CORS_ORIGINS=["http://localhost:3000"]
EOF
```

### Step 3: Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Database
Execute in Supabase SQL Editor:
```sql
-- Copy from: backend/migrations/01_create_predictions_table.sql
```

### Step 5: Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Verify
- Browser: http://localhost:8000/docs
- Script: `python test_prediction_api.py image.jpg`

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [COMPLETE_STARTUP_GUIDE.md](COMPLETE_STARTUP_GUIDE.md) | **Start here** - Full setup walkthrough |
| [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) | Local testing and validation |
| [PREDICTION_API_SETUP.md](PREDICTION_API_SETUP.md) | API details and configuration |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical overview |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | API quick reference |

---

## 🧪 Testing

### Automated Test
```bash
cd backend
source venv/bin/activate
python test_prediction_api.py image.jpg
```

### Manual Test (Swagger UI)
1. Open http://localhost:8000/docs
2. Click on endpoint
3. Enter Bearer token
4. Try it out

### Test Locally
```bash
cd backend
source venv/bin/activate

# Model initialization test
python3 << 'EOF'
from app.ml.model import get_ml_model
model = get_ml_model()
print("✅ Model loaded") if model.is_loaded() else print("❌ Failed")
EOF

# Server health
curl http://localhost:8000/docs
```

---

## ⚙️ Configuration

### Environment Variables

Required:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_ROLE_KEY=your_key
```

Optional:
```bash
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Model Configuration
- **Location:** `backend/models/road_model.pth`
- **Format:** PyTorch checkpoint (.pth)
- **Size:** Typically 100-500MB
- **Device:** Automatically uses GPU if available (CUDA)

### File Upload Settings
- **Accepted Types:** .jpg, .jpeg, .png
- **Max Size:** 10 MB (configurable in `app/api/routes/prediction.py`)
- **Image Preprocessing:** 224x224 resize, ImageNet normalization

---

## 🔒 Security Features

- ✅ **JWT Authentication** - Supabase tokens verified server-side
- ✅ **Row-Level Security** - Database policies isolate user data
- ✅ **Input Validation** - File type and size checks
- ✅ **CORS Control** - Configurable allowed origins
- ✅ **Error Masking** - No sensitive data in error responses
- ✅ **Rate Limiting Ready** - Can add middleware for throttling

---

## 📊 ML Model Details

### Model Loading
- Loads on server startup
- Singleton pattern (loads once)
- Supports both CPU and GPU
- Automatic device detection

### Inference
- **Speed:** 10-50ms (GPU), 100-500ms (CPU)
- **Memory:** ~2GB model + dependencies
- **Output:** Prediction class + confidence + all probabilities
- **Classes:** potholes, garbage, waterlogging

### Example Prediction
```json
{
  "prediction": "potholes",
  "confidence": 0.92,
  "probabilities": {
    "garbage": 0.05,
    "potholes": 0.92,
    "waterlogging": 0.03
  }
}
```

---

## 🚢 Deployment

### Local Development
```bash
uvicorn app.main:app --reload --port 8000
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
```

---

## 🛠️ Troubleshooting

### Model Not Loading
```
FileNotFoundError: Model file not found at /path/to/models/road_model.pth
```
**Fix:** Ensure `backend/models/road_model.pth` exists

### Token Errors
```
HTTPException: Invalid or expired token
```
**Fix:** Get fresh token from Supabase, verify token format

### Database Connection
```
Error: Failed to connect to Supabase
```
**Fix:** Check `.env` has correct `SUPABASE_URL` and keys

### Port In Use
```
Address already in use
```
**Fix:** `uvicorn app.main:app --port 8001`

### CORS Errors
**Fix:** Update `CORS_ORIGINS` in `.env` with your frontend URL

---

## 📈 Performance

### Response Times
- Model startup: 20-30 seconds
- Prediction: 100-500ms (CPU), 10-50ms (GPU)
- Database save: 50-200ms
- **Total:** 150-700ms per request

### Optimization Tips
- Use GPU for faster inference
- Increase worker count in production
- Add caching for frequent predictions
- Use CDN for static files

---

## 🔄 Changes from Previous Version

### Updated For Local ML Model:
- ✅ Removed external ML backend calls
- ✅ Added PyTorch model service (`app/ml/model.py`)
- ✅ Updated prediction service to use local model
- ✅ Removed `ML_BACKEND_URL` configuration requirement
- ✅ Added `torch`, `torchvision`, `Pillow` dependencies
- ✅ Created `models/` directory structure
- ✅ Updated API route error messages

### New Files:
- `app/ml/model.py` - PyTorch model service
- `app/ml/__init__.py` - Package initialization
- `COMPLETE_STARTUP_GUIDE.md` - Full setup guide
- `LOCAL_TESTING_GUIDE.md` - Testing procedures
- `setup.sh` - Automated setup script

---

## 📞 Support

### Quick Links
- **API Docs:** http://localhost:8000/docs
- **Supabase Dashboard:** https://supabase.com/dashboard
- **PyTorch Docs:** https://pytorch.org/docs

### Documentation
See [COMPLETE_STARTUP_GUIDE.md](COMPLETE_STARTUP_GUIDE.md) for detailed setup instructions.

---

## ✅ Startup Checklist

- [ ] `road_model.pth` copied to `backend/models/`
- [ ] `backend/.env` created with Supabase credentials
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database migration executed
- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] Swagger UI works: http://localhost:8000/docs
- [ ] Test passes: `python test_prediction_api.py image.jpg`

---

## 🎉 Ready to Go!

Your backend is ready for predictions. Start the server and begin exploring!

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** to interact with the API.

**Questions?** Check the documentation files listed above.

Happy predicting! 🚀
