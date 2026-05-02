# 🚀 Complete Startup Guide - Road Issue Prediction Backend

## 📋 Overview

This guide walks you through setting up and launching the Road Issue Prediction backend with local PyTorch ML model integration.

**What you have:**
- FastAPI backend with authentication via Supabase
- Local PyTorch ML model (`road_model.pth`) for road issue detection
- Supabase database integration with Row-Level Security
- Complete API for predictions and history retrieval

**What it does:**
- Users upload road images (jpg/png)
- Local ML model predicts issue class (potholes, garbage, waterlogging)
- Results are saved to Supabase database
- Users can view their prediction history

---

## 🔧 Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Supabase account** with a project created
- **Git** (optional, for version control)
- **4GB+ RAM** (for PyTorch model loading)
- **CUDA compatible GPU** (optional, for faster inference)

Check your Python version:
```bash
python3 --version  # Should be 3.10 or higher
```

---

## 📦 Step 1: Prepare Your Model File

Your `road_model.pth` file should be in the correct location:

```bash
# Verify model file location
ls -la backend/models/road_model.pth

# If not there, copy it:
cp /path/to/road_model.pth backend/models/
```

**Expected output:**
```
-rw-r--r-- 1 user user 123456789 May  2 10:30 backend/models/road_model.pth
```

> The model file should be the PyTorch checkpoint that your ML team provided. If you're missing the model file, ask your ML team for `road_model.pth`.

---

## 🔑 Step 2: Get Supabase Credentials

1. Go to [Supabase Console](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings → API**
4. Copy these values:
   - **Project URL** → `SUPABASE_URL`
   - **Anon Public Key** → `SUPABASE_ANON_KEY`
   - **Service Role Key** → `SUPABASE_SERVICE_ROLE_KEY`

Keep these safe - they're your database credentials.

---

## 📁 Step 3: Create Environment File

Create `backend/.env` with your Supabase credentials:

```bash
cd backend

# Using nano/vim
nano .env

# Or create with cat
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
EOF
```

**Verify it was created:**
```bash
cat .env
```

**Keep this file secret!** Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## 🗄️ Step 4: Create Database Schema

The backend needs a `predictions` table in Supabase.

1. Go to **Supabase Dashboard → SQL Editor**
2. Click **"New Query"**
3. Copy and paste the content from [migrations/01_create_predictions_table.sql](../migrations/01_create_predictions_table.sql)
4. Click **"Run"**

**What this does:**
- Creates `predictions` table
- Sets up user-data isolation with RLS
- Creates indexes for performance
- Adds automatic timestamps

Expected output: `✓ Success`

---

## 💻 Step 5: Install Dependencies

Install all required Python packages:

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Expected packages:**
- `fastapi` - Web framework
- `torch` & `torchvision` - ML model
- `supabase` - Database client
- `pydantic` - Data validation
- `pillow` - Image processing
- `numpy` - Numerical computing

**Installation takes 5-10 minutes** (slower on first install due to PyTorch size)

Verify installation:
```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

Expected output:
```
PyTorch: 2.x.x
CUDA available: True  (or False if no GPU)
```

---

## 🚀 Step 6: Start the Backend Server

Run the FastAPI development server:

```bash
cd backend

# Activate virtual environment if not already active
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Uvicorn started process [12345]
```

The server is now running! ✅

---

## 🧪 Step 7: Verify Everything Works

### Option A: Using the Interactive API Docs

Open in your browser:
```
http://localhost:8000/docs
```

This opens **Swagger UI** where you can test endpoints directly.

### Option B: Using Test Script

In a new terminal:

```bash
cd backend

# Make sure virtual environment is active
source venv/bin/activate

# Run the test script
python test_prediction_api.py image.jpg
```

**The script will:**
1. Login to Supabase
2. Upload the test image
3. Get a prediction
4. Retrieve history

**Expected output:**
```
🔐 Logging in as test@example.com...
✅ Login successful!
📤 Uploading image: image.jpg...
✅ Prediction successful!
   Prediction: potholes
   Confidence: 92.34%
   Probabilities: ...
📋 Fetching prediction history (limit=5)...
✅ Retrieved 1 predictions:
   ...
```

### Option C: Using cURL

Test the predict endpoint:

```bash
# You'll need a Supabase user token
# Login first to get it, or use postman/insomnia

curl -X POST http://localhost:8000/predictions/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg"
```

---

## 📊 API Endpoints

### 1. **Upload & Predict**

```
POST /predictions/predict
Authorization: Bearer {supabase_token}
Content-Type: multipart/form-data

file: [binary image data]
```

**Response (200):**
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

### 2. **Get History**

```
GET /predictions/history?limit=10&offset=0
Authorization: Bearer {supabase_token}
```

**Response (200):**
```json
[
  {
    "id": "123456",
    "prediction": "potholes",
    "confidence": 0.92,
    ...
  }
]
```

---

## 🛑 Troubleshooting

### Issue: "Model file not found"

```
FileNotFoundError: Model file not found at /path/to/models/road_model.pth
```

**Solution:**
1. Check model file exists: `ls -la backend/models/road_model.pth`
2. If missing, copy it: `cp your_model.pth backend/models/road_model.pth`
3. Restart the server

### Issue: "Invalid or expired token"

```
HTTPException: Invalid or expired token
```

**Solution:**
1. Get a fresh token from Supabase
2. Ensure token format: `Authorization: Bearer TOKEN`
3. Check token expiration (typically 1 hour)

### Issue: "Module not found" or Import errors

```
ModuleNotFoundError: No module named 'torch'
```

**Solution:**
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Restart server
```

### Issue: "No space left on device" (PyTorch installation)

PyTorch is large (~500MB). Ensure you have enough disk space:

```bash
df -h  # Check disk space
```

### Issue: CORS errors in frontend

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
Update `CORS_ORIGINS` in `backend/.env`:

```bash
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "https://yourdomain.com"]
```

Then restart the server.

### Issue: Database connection failed

```
Error: Failed to connect to Supabase
```

**Solution:**
1. Check `.env` file has correct credentials
2. Verify Supabase project is active
3. Check internet connection
4. Verify credentials:
   ```bash
   cat backend/.env | grep SUPABASE
   ```

---

## 🔄 Development Workflow

### During Development

```bash
# Terminal 1: Backend server (with auto-reload)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Testing
cd backend
source venv/bin/activate
python test_prediction_api.py image.jpg

# Terminal 3: Frontend (if you have one)
cd frontend
npm run dev
```

### View Logs

The backend logs all requests and errors:

```bash
# See live logs (from terminal running uvicorn)
# Just look at the Terminal 1 output

# Common log messages:
INFO:     POST /predictions/predict -> 200
INFO app.ml.model: ML inference successful: potholes (confidence: 0.92)
INFO app.services.prediction: Prediction saved for user uuid123: record_id456
```

---

## 📈 Performance Notes

### First Startup
- Takes **20-30 seconds** to load the PyTorch model
- This is normal and only happens once on server start
- Subsequent predictions are **100-500ms**

### Memory Usage
- Model + dependencies: ~2GB RAM
- Per request: ~200MB temporary
- Ensure your server has 4GB+ RAM

### GPU Acceleration (Optional)
If you have CUDA GPU, PyTorch will automatically use it:
```bash
# Check if GPU is available
python3 -c "import torch; print(torch.cuda.is_available())"
```

- With GPU: **10-50ms per prediction**
- Without GPU (CPU): **100-500ms per prediction**

---

## 🚢 Production Deployment

### Using Gunicorn (Production)

```bash
pip install gunicorn

gunicorn \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  app.main:app
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PyTorch
RUN apt-get update && apt-get install -y build-essential

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
```

Build and run:
```bash
docker build -t road-prediction-api .
docker run -p 8000:8000 -e SUPABASE_URL=... road-prediction-api
```

### Environment Variables for Production

```bash
# .env for production
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_key_here
SUPABASE_SERVICE_ROLE_KEY=your_key_here
CORS_ORIGINS=["https://yourdomain.com"]
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Authentication
│   │   └── routes/
│   │       ├── auth.py          # Auth endpoints
│   │       └── prediction.py     # Prediction endpoints
│   ├── ml/
│   │   ├── __init__.py
│   │   └── model.py             # PyTorch model service
│   ├── services/
│   │   ├── __init__.py
│   │   └── prediction.py        # Business logic
│   ├── schemas/
│   │   ├── auth.py              # Auth models
│   │   └── prediction.py        # Prediction models
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   └── supabase.py          # Database client
│   └── main.py                  # FastAPI app
├── models/
│   └── road_model.pth           # Your ML model (place here)
├── migrations/
│   └── 01_create_predictions_table.sql
├── .env                         # Your credentials (secret!)
├── requirements.txt             # Python dependencies
└── test_prediction_api.py       # Test script
```

---

## ✅ Startup Checklist

- [ ] `road_model.pth` is in `backend/models/` folder
- [ ] `backend/.env` file created with Supabase credentials
- [ ] Database table created (SQL migration executed)
- [ ] Python 3.10+ installed
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] Can access Swagger UI: `http://localhost:8000/docs`
- [ ] Test script runs successfully: `python test_prediction_api.py image.jpg`

---

## 🎯 Next Steps

1. **Test locally** with your images
2. **Integrate with frontend** - Use Bearer token pattern for auth
3. **Monitor logs** - Check for errors and performance
4. **Scale if needed** - Use Docker/Kubernetes for production
5. **Add monitoring** - Set up logging and alerting

---

## 📞 Quick Reference Commands

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Start backend
cd backend && uvicorn app.main:app --reload

# Run tests
python test_prediction_api.py image.jpg

# Check model loading
python3 -c "from app.ml.model import get_ml_model; m = get_ml_model(); print('✅ Model loaded')"

# View API docs
# Open: http://localhost:8000/docs

# Database check
# Supabase → SQL Editor → SELECT * FROM predictions LIMIT 1;
```

---

## 🎉 You're Ready!

Your Road Issue Prediction backend is ready to go. Start the server and begin making predictions!

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs` to explore the API.

**Happy predicting! 🚀**
