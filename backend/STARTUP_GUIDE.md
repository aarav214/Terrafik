# 🚀 FINAL STARTUP GUIDE - Road Issue Prediction with Local ML Model

**Last Updated:** May 2, 2026 - Local PyTorch Model Integration

---

## ⚡ 60-Second Quick Start

```bash
# 1. Prepare model directory
mkdir -p backend/models

# 2. Move your model file
cp /path/to/road_model.pth backend/models/

# 3. Setup and start
cd backend
bash setup.sh

# 4. Done! Backend running at http://localhost:8000
```

---

## 📋 Complete Step-by-Step Setup (5-10 minutes)

### Step 1: Prepare Model File

Your ML model must be in the correct location:

```bash
# Verify model exists
ls -lh /path/to/road_model.pth

# Copy to backend models directory
mkdir -p backend/models
cp road_model.pth backend/models/
ls -lh backend/models/road_model.pth
```

✅ **Expected:** Model file is ~100-500MB in size

---

### Step 2: Create Environment Configuration

Create `backend/.env` with your Supabase credentials:

```bash
cd backend

# Create .env file
cat > .env << 'EOF'
# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# CORS Origins (Optional - adjust for your frontend)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
EOF

# Verify file created
cat .env
```

**Where to get Supabase credentials:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → API
4. Copy the three keys above

✅ **Expected:** `.env` file contains three valid Supabase keys

---

### Step 3: Automated Setup with Script

The setup script handles everything:

```bash
cd backend
bash setup.sh
```

**What the script does:**
- ✅ Checks Python version
- ✅ Verifies model file exists
- ✅ Creates virtual environment
- ✅ Installs FastAPI, PyTorch, Supabase
- ✅ Tests model loading
- ✅ Shows next steps

**Expected output:**
```
✅ Python 3.x.x found
✅ Model file found (XXX MB)
✅ Virtual environment activated
✅ Dependencies installed
✅ ML Model loaded successfully
Start backend server now? (y/n)
```

---

### Step 4: Manual Setup (if not using script)

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or on Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Takes 5-10 minutes** (PyTorch is large)

Expected completion:
```
Successfully installed fastapi torch torchvision pillow numpy ... (15+ packages)
```

---

### Step 5: Database Migration

Create the predictions table in Supabase:

1. Open https://supabase.com/dashboard
2. Go to **SQL Editor**
3. Click **"New Query"**
4. Copy content from `backend/migrations/01_create_predictions_table.sql`
5. Paste into SQL Editor
6. Click **"Run"**

**Expected output:**
```
✓ Success (no errors)
```

What this creates:
- `predictions` table for storing results
- `user_id` foreign key to `auth.users`
- Row-Level Security (users see only their data)
- Performance indexes

---

### Step 6: Start the Backend Server

Open terminal in `backend/` directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Keep this terminal open** - it's your server running!

---

### Step 7: Verify Backend Works

Open a **new terminal** while server is running:

```bash
cd backend

# Test 1: Check server is running
curl http://localhost:8000/docs

# Test 2: Check model loaded
python3 << 'EOF'
from app.ml.model import get_ml_model
model = get_ml_model()
print(f"✅ Model loaded on {model.device}")
EOF

# Test 3: Run full test
python test_prediction_api.py image.jpg
```

**Expected:**
- ✅ Server responds
- ✅ Model loads successfully
- ✅ Test completes with prediction

---

## 🌐 Access the API

### Option 1: Interactive API (Easiest)

Best for testing and development:

```
http://localhost:8000/docs
```

This opens **Swagger UI** where you can:
- See all endpoints
- Test with real data
- View responses
- Check error codes

### Option 2: Direct URL

```
http://localhost:8000/openapi.json
```

Returns OpenAPI specification.

---

## 🧪 Testing the API

### With the Test Script

```bash
cd backend
source venv/bin/activate

# Need a test image first
python3 << 'EOF'
from PIL import Image
import numpy as np

# Create dummy test image
img = Image.fromarray(np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8))
img.save("test_image.jpg")
print("✅ Created test_image.jpg")
EOF

# Run the test
python test_prediction_api.py test_image.jpg
```

**Expected output:**
```
🔐 Logging in as test@example.com...
✅ Login successful!
📤 Uploading image: test_image.jpg...
✅ Prediction successful!
   Prediction: potholes
   Confidence: 92.34%
🎉 All tests completed!
```

### With cURL

```bash
# Get a Supabase token first
# Then:

curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@test_image.jpg"
```

Response:
```json
{
  "id": "123",
  "prediction": "potholes",
  "confidence": 0.92,
  "probabilities": {...}
}
```

---

## 📊 Architecture

```
Your Image
    ↓
FastAPI HTTP Request
    ↓
Authentication Check (Supabase JWT)
    ↓
File Validation (type, size)
    ↓
PyTorch Model (road_model.pth)
    ↓
Inference → Prediction + Confidence
    ↓
Save to Supabase Database
    ↓
Return Result to Client
```

---

## 📁 What Was Set Up

### New ML Files
```
app/ml/
├── __init__.py          # Package initialization
└── model.py             # PyTorch model service (199 lines)

models/
└── road_model.pth       # Your ML model file
```

### Updated Files
```
requirements.txt        # Added torch, torchvision, pillow
app/core/config.py      # Removed external ML_BACKEND_URL
app/services/prediction.py  # Uses local model now
app/api/routes/prediction.py  # Updated error messages
app/main.py             # No changes needed
```

### Documentation Added
```
COMPLETE_STARTUP_GUIDE.md     # Comprehensive guide (you are here)
LOCAL_TESTING_GUIDE.md        # Testing procedures
README_LOCAL_MODEL.md         # Overview
setup.sh                      # Automated setup script
```

---

## 🔑 Key Features

| Feature | Details |
|---------|---------|
| **Model** | Local PyTorch (`road_model.pth`) - instant inference |
| **Auth** | Supabase JWT tokens - secure per-user access |
| **Database** | Supabase with Row-Level Security - user data isolation |
| **Upload** | jpg/png only, max 10MB, automatic validation |
| **Prediction** | 3 classes: potholes, garbage, waterlogging |
| **Speed** | 100-500ms per prediction (faster with GPU) |
| **API Docs** | Interactive Swagger UI at `/docs` |

---

## ⚙️ Configuration Reference

### Environment Variables (`.env`)

**Required:**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...  # From Supabase API Settings
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...  # From Supabase API Settings
```

**Optional:**
```bash
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Python Dependencies

Core packages installed:
- `fastapi>=0.115.0` - Web framework
- `torch>=2.0.0` - ML model
- `torchvision>=0.15.0` - Image preprocessing
- `supabase>=2.6.0` - Database
- `pydantic-settings>=2.3.0` - Config validation
- `pillow>=10.0.0` - Image handling

---

## 🐛 Troubleshooting

### Problem: Model file not found
```
FileNotFoundError: Model file not found at backend/models/road_model.pth
```

**Solution:**
```bash
# Check file exists
ls -la backend/models/road_model.pth

# If missing, copy it
cp /path/to/road_model.pth backend/models/
```

### Problem: Dependencies fail to install
```
ERROR: Could not find a version that satisfies ... (torch)
```

**Solution:**
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Try again
pip install -r requirements.txt
```

### Problem: "Invalid or expired token"
```json
{"detail": "Invalid or expired token"}
```

**Solution:**
- Get fresh token from Supabase login
- Check Authorization header format: `Bearer TOKEN`
- Tokens expire in ~1 hour

### Problem: "Cannot connect to Supabase"
```
Error: Failed to connect to Supabase
```

**Solution:**
```bash
# Check .env has correct keys
cat backend/.env | grep SUPABASE

# Verify internet connection
ping supabase.com

# Check Supabase project is active
# Go to: https://supabase.com/dashboard
```

### Problem: "Address already in use"
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

---

## 📈 Performance

### First Startup
- **Model Loading:** 20-30 seconds (one-time on server start)
- **Subsequent Predictions:** 100-500ms (CPU), 10-50ms (GPU)

### Resource Requirements
- **RAM:** 4GB+ minimum (2GB model + 2GB overhead)
- **Disk:** 1GB (model + dependencies)
- **Network:** Required for Supabase connection

### GPU Acceleration (Optional)
If you have CUDA GPU:

```bash
# Check GPU availability
python3 -c "import torch; print(f'GPU: {torch.cuda.is_available()}')"

# If True, inference is ~10x faster
```

---

## 📞 Quick Reference

### File Locations
```bash
# Model
backend/models/road_model.pth

# Configuration
backend/.env

# Database Schema
backend/migrations/01_create_predictions_table.sql

# API Code
backend/app/api/routes/prediction.py

# ML Model Service
backend/app/ml/model.py

# Test Script
backend/test_prediction_api.py
```

### Common Commands
```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn app.main:app --reload

# Run tests
python test_prediction_api.py image.jpg

# Check model
python3 -c "from app.ml.model import get_ml_model; get_ml_model()"

# View API docs
# Open: http://localhost:8000/docs
```

---

## ✅ Complete Startup Checklist

Before launching, verify:

- [ ] `road_model.pth` copied to `backend/models/`
- [ ] `backend/.env` created with Supabase keys
- [ ] Python 3.10+ installed
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database migration executed (SQL in Supabase)
- [ ] Model loads without error: `python3 -c "from app.ml.model import get_ml_model; get_ml_model()"`
- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] Swagger UI works: http://localhost:8000/docs

---

## 🎯 Next Steps After Startup

1. **Test Locally** - Use test script to verify everything
2. **Check Logs** - Look for any warnings or errors
3. **Try API** - Open Swagger UI and test endpoints
4. **Connect Frontend** - Integrate with your React app
5. **Deploy** - Use guide in documentation for production

---

## 📚 Documentation Map

| Document | Purpose | Start Here |
|----------|---------|-----------|
| **COMPLETE_STARTUP_GUIDE.md** | Detailed setup steps | ← You are here |
| **LOCAL_TESTING_GUIDE.md** | Testing procedures | After startup |
| **README_LOCAL_MODEL.md** | Project overview | For context |
| **QUICK_REFERENCE.md** | API quick lookup | During development |

---

## 🎉 Ready to Launch!

You're all set! Start your backend with:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Then visit: **http://localhost:8000/docs**

**Questions?** Check the documentation files or review the code comments.

**Happy predicting! 🚀**

---

## 📝 Last Update

- **Date:** May 2, 2026
- **Change:** Integrated local PyTorch model (`road_model.pth`)
- **Files Updated:** 5 Python files, 3 documentation files
- **New Files:** 3 files (ML module, setup script, guides)
- **Status:** Ready for deployment ✅
