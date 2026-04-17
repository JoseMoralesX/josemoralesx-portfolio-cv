# SRE Incident Automation CLI

`incidentctl` is a small Python CLI that creates consistent incident artifacts:

- Incident folder structure
- Incident log template
- Postmortem template
- Timeline events file

This is designed to demonstrate on-call automation, incident hygiene, and repeatable post-incident reviews.

## Quickstart

```bash
cd projects/sre-incident-automation-cli
python incidentctl.py create --title "API Latency Regression" --sev SEV2
python incidentctl.py add-event --id INC-2026-0001 --time "2026-04-16T18:12:00Z" --who "On-call" --what "Mitigation started"
```

Artifacts are created under:

`incidents/INC-YYYY-NNNN/`

## Docker (optional)

```bash
docker build -t incidentctl .
docker run --rm -v ${PWD}:/work -w /work incidentctl create --title "Example Incident" --sev SEV3
```
