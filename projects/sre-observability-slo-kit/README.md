# SRE Observability & SLO Kit

Production-style starter kit that demonstrates:

- A Python service instrumented for Prometheus metrics
- A local observability stack (Prometheus + Grafana) via Docker Compose
- A simple SLO definition format and a small generator that produces Prometheus alert rules

## Quickstart

```bash
cd projects/sre-observability-slo-kit
docker compose up --build
```

- App: http://localhost:8080
- Metrics: http://localhost:8080/metrics
- Grafana: http://localhost:3000 (admin / admin)
- Prometheus: http://localhost:9090

## App endpoints

- `GET /health` -> 200
- `GET /work?ms=120&fail_rate=0.02` -> simulates work and occasional failures
- `GET /metrics` -> Prometheus metrics

## SLOs

Edit the SLO file:

- `slo/slo.yaml`

Generate alert rules:

```bash
python tools/sloctl.py generate --in slo/slo.yaml --out prometheus/alerts.generated.yml
```

Prometheus loads both:

- `prometheus/alerts.yml` (static alerts)
- `prometheus/alerts.generated.yml` (generated from SLO config)

## Notes

- This kit is intentionally minimal and designed to be extended for real production environments (authn, RBAC, SSO, SIEM export, and hardened images).
