import json
from pathlib import Path

import duckdb
import pandas as pd

from etl.quality import run_quality_checks


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
DB_PATH = OUT_DIR / "cost.duckdb"


def load_aws() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sample_aws_cost.csv")
    df["provider"] = "aws"
    df["account"] = df["account_id"].astype(str)
    df["sku"] = None
    df = df.rename(columns={"region": "region"})
    df = df[["provider", "date", "account", "service", "region", "sku", "cost_usd"]]
    return df


def load_gcp() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sample_gcp_cost.csv")
    df["provider"] = "gcp"
    df["account"] = df["project_id"].astype(str)
    df["region"] = None
    df = df.rename(columns={"sku": "sku"})
    df = df[["provider", "date", "account", "service", "region", "sku", "cost_usd"]]
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    aws = load_aws()
    gcp = load_gcp()
    costs = pd.concat([aws, gcp], ignore_index=True)
    costs["date"] = pd.to_datetime(costs["date"]).dt.date.astype(str)
    costs["cost_usd"] = costs["cost_usd"].astype(float)

    quality = run_quality_checks(costs)
    (OUT_DIR / "quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")

    con = duckdb.connect(str(DB_PATH))
    con.register("costs_df", costs)
    con.execute("CREATE OR REPLACE TABLE costs AS SELECT * FROM costs_df")

    cost_daily = con.execute(
        """
        SELECT
          provider,
          date,
          round(sum(cost_usd), 2) AS cost_usd
        FROM costs
        GROUP BY 1,2
        ORDER BY 1,2
        """
    ).df()
    cost_daily.to_csv(OUT_DIR / "cost_daily.csv", index=False)

    cost_by_service = con.execute(
        """
        SELECT
          provider,
          service,
          round(sum(cost_usd), 2) AS cost_usd
        FROM costs
        GROUP BY 1,2
        ORDER BY cost_usd DESC
        """
    ).df()
    cost_by_service.to_csv(OUT_DIR / "cost_by_service.csv", index=False)

    anomalies = con.execute(
        """
        WITH daily AS (
          SELECT provider, date, sum(cost_usd) AS cost_usd
          FROM costs
          GROUP BY 1,2
        ),
        stats AS (
          SELECT provider,
                 avg(cost_usd) AS mean_cost,
                 stddev_samp(cost_usd) AS std_cost
          FROM daily
          GROUP BY 1
        )
        SELECT d.provider, d.date, round(d.cost_usd, 2) AS cost_usd,
               round(s.mean_cost, 2) AS mean_cost,
               round(s.std_cost, 2) AS std_cost
        FROM daily d
        JOIN stats s USING(provider)
        WHERE s.std_cost IS NOT NULL
          AND d.cost_usd > (s.mean_cost + (2 * s.std_cost))
        ORDER BY d.cost_usd DESC
        """
    ).df()
    anomalies.to_csv(OUT_DIR / "anomalies.csv", index=False)

    print(f"db={DB_PATH}")
    print(f"ok={quality['ok']}")
    print(f"output_dir={OUT_DIR}")


if __name__ == "__main__":
    main()
