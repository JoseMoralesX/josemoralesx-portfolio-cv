import json
from dataclasses import dataclass

import boto3

from app.policy import ModelConfig


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


def _to_anthropic_messages(messages: list[ChatMessage]) -> list[dict]:
    out: list[dict] = []
    for m in messages:
        role = "user" if m.role not in ("user", "assistant") else m.role
        out.append({"role": role, "content": [{"type": "text", "text": m.content}]})
    return out


def invoke_mock(model: ModelConfig, messages: list[ChatMessage]) -> str:
    text = "\n".join([f"{m.role}: {m.content}" for m in messages][-10:])
    if model.id == "mock-small":
        return f"Mock response (small): {text[:600]}"
    return f"Mock response (large): {text[:2000]}"


def invoke_bedrock(model: ModelConfig, region: str, messages: list[ChatMessage]) -> str:
    client = boto3.client("bedrock-runtime", region_name=region)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": model.max_output_tokens,
        "messages": _to_anthropic_messages(messages),
    }

    resp = client.invoke_model(
        modelId=model.id,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json",
    )
    data = json.loads(resp["body"].read())
    parts = data.get("content", [])
    texts = []
    for p in parts:
        if p.get("type") == "text":
            texts.append(p.get("text", ""))
    return "".join(texts).strip()
