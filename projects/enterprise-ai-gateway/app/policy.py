import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = BASE_DIR / "policy" / "policy.json"


class ModelConfig(BaseModel):
    id: str
    provider: str
    display_name: str
    max_output_tokens: int = Field(ge=1, le=4096)


class RedactionConfig(BaseModel):
    enabled: bool = True


class Policy(BaseModel):
    max_input_chars: int = Field(default=8000, ge=1, le=200_000)
    redaction: RedactionConfig = RedactionConfig()
    models: list[ModelConfig]


def load_policy(path: Path | None = None) -> Policy:
    p = path or DEFAULT_POLICY_PATH
    data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return Policy.model_validate(data)


def find_model(policy: Policy, model_id: str) -> ModelConfig:
    for m in policy.models:
        if m.id == model_id:
            return m
    raise KeyError(model_id)
