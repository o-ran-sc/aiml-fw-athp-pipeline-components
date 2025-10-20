FROM tensorflow/tensorflow:2.17.0-gpu

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model_training_for_green_network_component.py .

ENTRYPOINT ["python", "model_training_for_green_network_component.py"]
