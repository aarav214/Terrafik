# Road Brain Backend

Minimal FastAPI backend using Supabase Auth.

## Setup (quick)

1. Create a virtualenv and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Create `.env` with your Supabase credentials (do NOT commit this file):

```bash
cat > .env << 'EOF'
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
CORS_ORIGINS=["http://localhost:3000"]
EOF
```

3. Place the ML model (keep out of git):

```bash
mkdir -p models
# copy or move your model file
cp /path/to/road_model.pth models/road_model.pth
```

> Note: `models/` and `*.pth` are ignored by `.gitignore` to avoid committing large binaries.

4. Run the server:

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints (selected)

- `POST /signup`
- `POST /login`
- `GET /me` (protected — requires `Authorization: Bearer <token>`)

## Testing

- Open Swagger UI: `http://localhost:8000/docs` and use the Authorize button to set a Bearer token.
- Use `POST /predictions/predict` with form field `file` and a valid token to create predictions.

## Troubleshooting

- If you see `Model file not found`, ensure `models/road_model.pth` exists in `backend/models/`.
- If inserts fail with RLS errors, ensure the backend is using the service role key for trusted writes (server-only).
