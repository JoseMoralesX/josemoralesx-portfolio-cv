FROM python:3.11-slim

WORKDIR /work

COPY incidentctl.py /tool/incidentctl.py
COPY templates /tool/templates

ENTRYPOINT ["python", "/tool/incidentctl.py"]
