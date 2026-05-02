#!/bin/bash

# 🚀 Road Issue Prediction - Setup & Launch Script
# This script automates the setup and startup process

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Road Issue Prediction Backend - Setup & Launch              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oP '(?<=Python )\d+\.\d+')
print_success "Python $PYTHON_VERSION found"

if ! command -v git &> /dev/null; then
    print_warning "Git not found (optional)"
fi

# Check model file
print_step "Checking for model file..."

if [ ! -f "models/road_model.pth" ]; then
    print_error "Model file not found!"
    echo "  Expected: backend/models/road_model.pth"
    echo ""
    echo "  To fix:"
    echo "    mkdir -p models"
    echo "    cp /path/to/road_model.pth models/"
    exit 1
fi
MODEL_SIZE=$(ls -lh models/road_model.pth | awk '{print $5}')
print_success "Model file found ($MODEL_SIZE)"

# Check .env file
print_step "Checking environment file..."

if [ ! -f ".env" ]; then
    print_warning "No .env file found"
    echo ""
    echo "  Creating template .env file..."
    cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# CORS Configuration (adjust for your frontend)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
EOF
    
    print_warning "Please update .env with your Supabase credentials:"
    echo "    1. Go to https://supabase.com/dashboard"
    echo "    2. Open your project settings → API"
    echo "    3. Copy Project URL, Anon Key, Service Role Key"
    echo "    4. Update backend/.env"
    echo ""
    read -p "Continue after updating .env? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success ".env file exists"
fi

# Create virtual environment
print_step "Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --quiet --upgrade pip
print_success "Pip upgraded"

# Install dependencies
print_step "Installing Python dependencies..."
echo "  This may take 5-10 minutes (first install with PyTorch is slower)..."
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Verify model loading
print_step "Verifying ML model..."
python3 << EOF
try:
    from app.ml.model import MLModelService
    from pathlib import Path
    
    model_path = Path("models/road_model.pth")
    service = MLModelService(model_path)
    
    if service.is_loaded():
        print(f"\033[0;32m✅\033[0m ML Model loaded successfully")
        print(f"\033[0;32m✅\033[0m Device: {service.device}")
    else:
        print(f"\033[0;31m❌\033[0m Failed to load model")
        exit(1)
except Exception as e:
    print(f"\033[0;31m❌\033[0m Error: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
print_success "Setup complete! ✨"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Next Steps                                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  1️⃣  Run database migration:"
echo "     - Open: https://supabase.com/dashboard"
echo "     - Go to: SQL Editor"
echo "     - Paste content from: migrations/01_create_predictions_table.sql"
echo "     - Click: Run"
echo ""
echo "  2️⃣  Start backend server:"
echo "     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  3️⃣  Test the API:"
echo "     - Browser: http://localhost:8000/docs"
echo "     - Or: python test_prediction_api.py image.jpg"
echo ""
echo "  📖 Full guide: See COMPLETE_STARTUP_GUIDE.md"
echo ""

# Ask to start server
read -p "Start backend server now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting server on http://0.0.0.0:8000"
    echo "📖 API docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
