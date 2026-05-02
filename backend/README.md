# Road Brain Backend

FastAPI backend for road issue prediction, issue reporting, and Supabase Auth.

## Setup (quick)

1. Create a virtualenv and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. Create `.env` from the example file and fill in your credentials:

```bash
cp .env.example .env
# then edit .env and set real values
```

Required environment variables:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional but recommended for issue reports:

- `GROQ_API_KEY`

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

# If you are starting from the repo root instead of backend/
# use:
# PYTHONPATH=backend backend/.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints (selected)

- `POST /signup`
- `POST /login`
- `GET /me` (protected — requires `Authorization: Bearer <token>`)
- `POST /predictions/predict` (protected — image upload)
- `POST /report-issue` (protected — image + latitude + longitude)

## Testing

- Open Swagger UI: `http://localhost:8000/docs` and use the Authorize button to set a Bearer token.
- Use `POST /predictions/predict` with form field `file` and a valid token to create predictions.
- Use `POST /report-issue` with form fields `image`, `latitude`, and `longitude`; the backend uses the authenticated login email.

## Troubleshooting

- If you see `Model file not found`, ensure `models/road_model.pth` exists in `backend/models/`.
- If inserts fail with RLS errors, ensure the backend is using the service role key for trusted writes (server-only).
- If issue reporting falls back to a basic complaint, ensure `GROQ_API_KEY` is set and reachable.
