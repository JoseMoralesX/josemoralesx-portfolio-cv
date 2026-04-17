FROM python:3.11-slim

WORKDIR /work

COPY etl/requirements.txt /work/etl/requirements.txt
RUN pip install --no-cache-dir -r /work/etl/requirements.txt

COPY etl /work/etl
COPY data /work/data

CMD ["python", "etl/run_etl.py"]
