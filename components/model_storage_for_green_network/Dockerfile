FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model_storage_for_green_network_component.py .

ENTRYPOINT ["python", "model_storage_for_green_network_component.py"]
