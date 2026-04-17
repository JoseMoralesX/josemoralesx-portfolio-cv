from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    details: dict[str, Any]


def _req_cols(df: pd.DataFrame, cols: list[str]) -> CheckResult:
    missing = [c for c in cols if c not in df.columns]
    return CheckResult("required_columns", len(missing) == 0, {"missing": missing})


def _no_negative_cost(df: pd.DataFrame) -> CheckResult:
    bad = int((df["cost_usd"] < 0).sum())
    return CheckResult("no_negative_cost", bad == 0, {"negative_rows": bad})


def _no_null_dates(df: pd.DataFrame) -> CheckResult:
    bad = int(df["date"].isna().sum())
    return CheckResult("no_null_dates", bad == 0, {"null_date_rows": bad})


def _no_null_provider(df: pd.DataFrame) -> CheckResult:
    bad = int(df["provider"].isna().sum())
    return CheckResult("no_null_provider", bad == 0, {"null_provider_rows": bad})


def run_quality_checks(df: pd.DataFrame) -> dict[str, Any]:
    required = ["provider", "date", "account", "service", "cost_usd"]
    checks = [
        _req_cols(df, required),
        _no_null_provider(df),
        _no_null_dates(df),
        _no_negative_cost(df),
    ]

    return {
        "row_count": int(len(df)),
        "ok": all(c.ok for c in checks),
        "checks": [asdict(c) for c in checks],
    }
