# Cloud Cost Analytics ETL (Data)

ETL/ELT example focused on cloud cost analytics:

- Ingests AWS/GCP cost exports (CSV)
- Normalizes data into DuckDB
- Runs data quality checks (schema + invariants)
- Produces aggregated outputs (daily cost, cost by service, anomalies)

## Quickstart

```bash
cd projects/cloud-cost-analytics-etl
python -m venv .venv
.venv\\Scripts\\activate
pip install -r etl/requirements.txt
python etl/run_etl.py
```

Outputs:

- `output/cost_daily.csv`
- `output/cost_by_service.csv`
- `output/quality_report.json`

## Docker

```bash
docker build -t cloud-cost-etl .
docker run --rm -v ${PWD}:/work -w /work cloud-cost-etl
```
