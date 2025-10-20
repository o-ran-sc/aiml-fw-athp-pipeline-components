FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY feature_extraction_for_green_network_component.py .

ENTRYPOINT ["python", "feature_extraction_for_green_network_component.py"]
