import json
import threading
import time
from collections import deque
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from app.train import BASELINE_PATH, MODEL_PATH, featurize, main as train_main


APP_NAME = "ml-drift-monitoring-service"

REQUESTS_TOTAL = Counter("http_requests_total", "Total HTTP requests", ["app", "method", "path", "status"])
REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["app", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.4, 0.75, 1.5, 3.0, 6.0),
)
PREDICTIONS_TOTAL = Counter("predictions_total", "Total predictions", ["app", "label"])
DRIFT_SCORE = Gauge("drift_score", "Average drift score across features", ["app"])


class DriftMonitor:
    def __init__(self, baseline: dict, window_size: int = 500):
        self._baseline = baseline
        self._bins = [np.array(f["bins"], dtype=np.float64) for f in baseline["features"]]
        self._base_counts = [np.array(f["counts"], dtype=np.float64) for f in baseline["features"]]
        self._base_probs = [c / max(c.sum(), 1.0) for c in self._base_counts]
        self._window = deque(maxlen=window_size)
        self._lock = threading.Lock()

    def add(self, x: np.ndarray) -> None:
        with self._lock:
            self._window.append(x.astype(np.float64))

    def score(self) -> float:
        with self._lock:
            if len(self._window) < 50:
                return 0.0
            X = np.vstack(self._window)

        scores = []
        for i in range(X.shape[1]):
            col = X[:, i]
            hist, _ = np.histogram(col, bins=self._bins[i])
            p = hist.astype(np.float64)
            p = p / max(p.sum(), 1.0)
            q = self._base_probs[i]
            scores.append(float(np.abs(p - q).sum() / 2.0))
        return float(np.mean(scores))


def load_artifacts():
    if not MODEL_PATH.exists() or not BASELINE_PATH.exists():
        train_main()
    model_obj = joblib.load(MODEL_PATH)
    baseline = json.loads(Path(BASELINE_PATH).read_text(encoding="utf-8"))
    return model_obj["model"], baseline


model, baseline = load_artifacts()
monitor = DriftMonitor(baseline=baseline, window_size=800)

app = FastAPI(title="ML Drift Monitoring Service", version="1.0.0")


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
    return {"status": "ok", "service": APP_NAME, "baseline": baseline.get("meta", {})}


@app.post("/predict")
def predict(payload: dict):
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="payload.text must be a non-empty string")

    X = featurize([text])
    proba = model.predict_proba(X)[0]
    label = int(np.argmax(proba))

    monitor.add(X)
    drift = monitor.score()
    DRIFT_SCORE.labels(APP_NAME).set(drift)

    PREDICTIONS_TOTAL.labels(APP_NAME, str(label)).inc()

    return {"label": label, "probability": float(proba[label]), "drift_score": drift}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
