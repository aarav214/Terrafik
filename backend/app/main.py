import logging
import time
from collections import deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.auth import router as auth_router
from app.api.routes.prediction import router as prediction_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("road_brain")

app = FastAPI(title="Road Brain Auth API")
settings = get_settings()

# Simple in-memory rate limiter state: per-IP deque of recent request timestamps
# Note: in-memory limiter is process-local and intended for development/testing.
app.state.rate_limits = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Limit to N requests per rolling 60-second window per client IP
    limit = getattr(settings, "rate_limit_per_minute", 60)
    window_seconds = 60

    client_host = "unknown"
    if request.client:
        client_host = request.client.host

    now_ts = time.time()
    dq = app.state.rate_limits.get(client_host)
    if dq is None:
        dq = deque()
        app.state.rate_limits[client_host] = dq

    # Drop timestamps outside the rolling window
    while dq and dq[0] <= now_ts - window_seconds:
        dq.popleft()

    if len(dq) >= limit:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    dq.append(now_ts)
    return await call_next(request)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> %s in %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error for %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth_router)
app.include_router(prediction_router)
