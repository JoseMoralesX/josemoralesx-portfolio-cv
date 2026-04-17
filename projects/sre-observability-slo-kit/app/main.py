import os
import random
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

APP_NAME = os.getenv("APP_NAME", "sre-observability-slo-kit")

REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["app", "method", "path", "status"],
)
REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["app", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.4, 0.75, 1.5, 3.0, 6.0),
)
WORK_FAILURES_TOTAL = Counter(
    "work_failures_total",
    "Simulated failures from /work",
    ["app", "reason"],
)

app = FastAPI(title="SRE Observability & SLO Kit", version="1.0.0")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_LATENCY_SECONDS.labels(APP_NAME, method, path).observe(elapsed)
        REQUESTS_TOTAL.labels(APP_NAME, method, path, str(status_code)).inc()


@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME}


@app.get("/work")
def work(ms: int = 120, fail_rate: float = 0.02, seed: Optional[int] = None):
    if ms < 0 or ms > 10_000:
        raise HTTPException(status_code=400, detail="ms must be between 0 and 10000")
    if fail_rate < 0 or fail_rate > 1:
        raise HTTPException(status_code=400, detail="fail_rate must be between 0 and 1")

    rng = random.Random(seed) if seed is not None else random
    time.sleep(ms / 1000.0)

    if rng.random() < fail_rate:
        reason = "simulated_error"
        WORK_FAILURES_TOTAL.labels(APP_NAME, reason).inc()
        raise HTTPException(status_code=500, detail="simulated failure")

    return {"result": "ok", "duration_ms": ms}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
