FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY metrics_store_for_green_network_component.py .

ENTRYPOINT ["python", "metrics_store_for_green_network_component.py"]
