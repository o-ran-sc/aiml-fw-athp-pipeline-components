# ==================================================================================
#
#       Copyright (c) 2025 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================

from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model
from typing import NamedTuple

@dsl.component(
    
    base_image="python:3.11-slim",
    packages_to_install=[
        "torch==2.2.0",
        "numpy==1.24.3",
        "pandas==2.1.0",
        "boto3==1.28.0",
        "codecarbon==2.3.5",
        "scikit-learn==1.3.0"
    ]
)
def model_training_for_green_network(
    features_csv: Input[Dataset],
    training_job_name: str,
    s3_endpoint: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_bucket: str,
    model_output: Output[Model],
    sequence_length: int = 24,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.003,
    train_split_ratio: float = 0.7
) -> NamedTuple("Outputs", [
    ("train_rmse", float),
    ("test_rmse", float),
    ("training_time", float),
    ("ram_energy_kwh", float),
    ("cpu_energy_kwh", float),
    ("gpu_energy_kwh", float),
    ("co2_emissions_kg", float),
]):
    import os
    import time
    import pandas as pd
    import numpy as np
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_squared_error
    import boto3
    from codecarbon import EmissionsTracker

    local_csv = features_csv.path
    df = pd.read_csv(local_csv)
    data = df['RRU.PrbUsedDl'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    def create_sequences(data, seq_len):
        xs, ys = [], []
        for i in range(len(data) - seq_len):
            xs.append(data[i:(i + seq_len)])
            ys.append(data[i + seq_len])
        return np.array(xs), np.array(ys)

    X, y = create_sequences(scaled_data, sequence_length)
    split_idx = int(len(X) * train_split_ratio)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32)
    train_loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=batch_size, shuffle=True)

    class LSTMModel(nn.Module):
        def __init__(self, input_size=1, hidden_size=64, num_layers=2):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, 1)
        def forward(self, x):
            out, _ = self.lstm(x)
            out = self.fc(out[:, -1, :])
            return out

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LSTMModel().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    tracker = EmissionsTracker(project_name=training_job_name, measure_power_secs=1)
    tracker.start()

    start_time = time.time()
    for epoch in range(epochs):
        model.train()
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            pred = model(batch_x)
            loss = criterion(pred, batch_y)
            loss.backward()
            optimizer.step()
    end_time = time.time()
    duration = end_time - start_time
    emissions = tracker.stop()

    model.eval()
    with torch.no_grad():
        preds = model(X_test_t.to(device)).cpu().numpy()
        y_true = y_test_t.cpu().numpy()
        test_rmse_val = float(mean_squared_error(y_true, preds, squared=False))
    train_rmse_val = float(loss.item())

    model_path = f"/tmp/{training_job_name}_model.pth"
    torch.save(model.state_dict(), model_path)

    s3_client = boto3.client(
        's3',
        endpoint_url=s3_endpoint,
        aws_access_key_id=s3_access_key,
        aws_secret_access_key=s3_secret_key
    )
    s3_key = f"green-network/models/{training_job_name}/model.pth"
    s3_client.upload_file(model_path, s3_bucket, s3_key)

    with open(model_output.path, "w") as f:
        f.write(f"s3://{s3_bucket}/{s3_key}")

    ram_energy_kwh_val = float(getattr(emissions, "ram_energy", 0.0))
    cpu_energy_kwh_val = float(getattr(emissions, "cpu_energy", 0.0))
    gpu_energy_kwh_val = float(getattr(emissions, "gpu_energy", 0.0))
    co2_emissions_kg_val = float(getattr(emissions, "emissions", 0.0))

    return (
        train_rmse_val,
        test_rmse_val,
        duration,
        ram_energy_kwh_val,
        cpu_energy_kwh_val,
        gpu_energy_kwh_val,
        co2_emissions_kg_val,
    )
