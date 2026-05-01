# Road Brain Backend

Minimal FastAPI backend using Supabase Auth.

## Setup

1. Copy `.env.example` to `.env` and fill in the Supabase values.
2. Install dependencies with `.venv/bin/pip install -r requirements.txt`.
3. Run the app with `.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.

## Endpoints

- `POST /signup`
- `POST /login`
- `GET /me`
