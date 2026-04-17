import json
import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from app.policy import find_model, load_policy
from app.providers import ChatMessage, invoke_bedrock, invoke_mock
from app.redaction import redact


APP_NAME = "enterprise-ai-gateway"
BASE_DIR = Path(__file__).resolve().parents[1]
UI_DIR = BASE_DIR / "ui"

REQUESTS_TOTAL = Counter("http_requests_total", "Total HTTP requests", ["app", "method", "path", "status"])
REQUEST_LATENCY_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency (seconds)",
    ["app", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.4, 0.75, 1.5, 3.0, 6.0, 12.0, 24.0),
)
LLM_CALLS_TOTAL = Counter("llm_calls_total", "Total LLM calls", ["app", "provider", "model_id", "status"])


policy = load_policy()
aws_region = os.getenv("AWS_REGION", "us-east-1")

app = FastAPI(title="Enterprise AI Gateway", version="1.0.0")


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


@app.get("/")
def ui_index():
    p = UI_DIR / "index.html"
    return FileResponse(p)


@app.get("/ui/{path:path}")
def ui_static(path: str):
    p = (UI_DIR / path).resolve()
    if not str(p).startswith(str(UI_DIR.resolve())):
        raise HTTPException(status_code=404, detail="not found")
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(p)


@app.get("/api/models")
def list_models():
    return JSONResponse(
        [
            {
                "id": m.id,
                "provider": m.provider,
                "display_name": m.display_name,
                "max_output_tokens": m.max_output_tokens,
            }
            for m in policy.models
        ]
    )


@app.post("/api/chat")
def chat(payload: dict):
    model_id = payload.get("model_id")
    messages_in = payload.get("messages")
    if not isinstance(model_id, str) or not model_id:
        raise HTTPException(status_code=400, detail="payload.model_id must be a string")
    if not isinstance(messages_in, list) or not messages_in:
        raise HTTPException(status_code=400, detail="payload.messages must be a non-empty list")

    try:
        model = find_model(policy, model_id)
    except KeyError:
        raise HTTPException(status_code=400, detail="model not allowed")

    messages: list[ChatMessage] = []
    for m in messages_in[-20:]:
        role = m.get("role")
        content = m.get("content")
        if role not in ("user", "assistant"):
            role = "user"
        if not isinstance(content, str):
            raise HTTPException(status_code=400, detail="message content must be string")
        messages.append(ChatMessage(role=role, content=content))

    joined = "\n".join([x.content for x in messages if x.role == "user"])
    if len(joined) > policy.max_input_chars:
        raise HTTPException(status_code=413, detail="input too large")

    if policy.redaction.enabled:
        messages = [ChatMessage(role=m.role, content=redact(m.content)) for m in messages]

    audit = {
        "event": "chat_request",
        "model_id": model.id,
        "provider": model.provider,
        "message_count": len(messages),
    }
    print(json.dumps(audit, ensure_ascii=False))

    status = "ok"
    try:
        if model.provider == "mock":
            out = invoke_mock(model, messages)
        elif model.provider == "bedrock":
            out = invoke_bedrock(model, aws_region, messages)
        else:
            raise HTTPException(status_code=400, detail="unsupported provider")
    except HTTPException:
        raise
    except Exception:
        status = "error"
        raise HTTPException(status_code=502, detail="upstream model error")
    finally:
        LLM_CALLS_TOTAL.labels(APP_NAME, model.provider, model.id, status).inc()

    return {"model_id": model.id, "provider": model.provider, "content": out}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
