# ML Drift Monitoring Service (AI/ML + SRE)

An end-to-end example of an ML inference API with:

- Offline training step that produces a model + baseline feature distributions
- Online inference (FastAPI) with Prometheus metrics
- Drift scoring against the baseline using a lightweight statistical approach

## Quickstart (Docker)

```bash
cd projects/ml-drift-monitoring-service
docker compose up --build
```

- API: http://localhost:8090
- Docs: http://localhost:8090/docs
- Metrics: http://localhost:8090/metrics
- Prometheus: http://localhost:9091

## What it does

- Trains a simple classifier on synthetic “ticket” data (`train.py`)
- Serves `/predict` with probabilities and a drift score
- Tracks request metrics + drift gauge via Prometheus

## Local run (Python)

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r app/requirements.txt
python app/train.py
uvicorn app.service:app --reload --port 8090
```
