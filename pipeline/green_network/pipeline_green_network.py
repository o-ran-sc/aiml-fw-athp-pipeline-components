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

from kfp import dsl, compiler
import sys
import os

# Add component directories to Python path
sys.path.append(os.path.abspath('../../components/feature_extraction_for_green_network'))
sys.path.append(os.path.abspath('../../components/model_training_for_green_network'))
sys.path.append(os.path.abspath('../../components/model_storage_for_green_network'))
sys.path.append(os.path.abspath('../../components/metrics_store_for_green_network'))

# Import pipeline components
from feature_extraction_for_green_network_component import feature_extraction_for_green_network
from model_training_for_green_network_component import model_training_for_green_network
from model_storage_for_green_network_component import model_storage_for_green_network
from metrics_store_for_green_network_component import metrics_store_for_green_network


@dsl.pipeline(
    name='Green Network Traffic Forecasting Pipeline V3',
    description='Deep Learning Based Traffic Forecasting with Carbon Tracking for Green Network'
)
def green_network_pipeline(
    training_job_name: str = 'green-network-lstm',
    version: str = 'v1',
    influxdb_url: str = 'http://influxdb2.nonrtric.svc.cluster.local:8086',
    influxdb_token: str = 'your-influxdb-token',
    influxdb_org: str = 'primary',
    influxdb_bucket: str = 'Viavi_Dataset',
    cell_name: str = None,
    time_range_days: int = 30,
    s3_endpoint: str = 'http://minio-service.kubeflow.svc.cluster.local:9000',
    s3_access_key: str = 'minioadmin',
    s3_secret_key: str = 'minioadmin',
    s3_bucket: str = 'ml-models',
    cassandra_host: str = 'cassandra.traininghost.svc.cluster.local',
    cassandra_port: int = 9042,
    cassandra_username: str = 'cassandra',
    cassandra_password: str = 'b3lpnlyZLn',
    cassandra_keyspace: str = 'ml_metrics',
    sequence_length: int = 24,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.003,
    train_split_ratio: float = 0.7
):

    # -------------------------------------------------------------------------
    # Task 1: Feature Extraction
    # -------------------------------------------------------------------------
    feature_task = feature_extraction_for_green_network(
        training_job_name=training_job_name,
        influxdb_url=influxdb_url,
        influxdb_token=influxdb_token,
        influxdb_org=influxdb_org,
        influxdb_bucket=influxdb_bucket,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_bucket=s3_bucket,
        cell_name=cell_name,
        time_range_days=time_range_days
    )

    feature_task.set_cpu_request('500m')
    feature_task.set_cpu_limit('1')
    feature_task.set_memory_request('1Gi')
    feature_task.set_memory_limit('2Gi')

    # -------------------------------------------------------------------------
    # Task 2: Model Training
    # -------------------------------------------------------------------------
    training_task = model_training_for_green_network(
        features_csv=feature_task.outputs['features_csv'],
        training_job_name=training_job_name,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_bucket=s3_bucket,
        sequence_length=sequence_length,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        train_split_ratio=train_split_ratio
    )
    training_task.after(feature_task)   # ✅ 명시적 dependency 연결

    training_task.set_cpu_request('500m')
    training_task.set_cpu_limit('2')
    training_task.set_memory_request('1Gi')
    training_task.set_memory_limit('2Gi')

    # -------------------------------------------------------------------------
    # Task 3: Model Storage (Upload to S3)
    # -------------------------------------------------------------------------
    storage_task = model_storage_for_green_network(
        model_input=training_task.outputs['model_output'],
        training_job_name=training_job_name,
        version=version,
        s3_endpoint=s3_endpoint,
        s3_access_key=s3_access_key,
        s3_secret_key=s3_secret_key,
        s3_bucket=s3_bucket,
        train_rmse=training_task.outputs['train_rmse'],
        test_rmse=training_task.outputs['test_rmse'],
        co2_emissions_kg=training_task.outputs['co2_emissions_kg']
    )
    storage_task.after(training_task)  # ✅ 명시적 dependency 연결

    storage_task.set_cpu_request('500m')
    storage_task.set_cpu_limit('1')
    storage_task.set_memory_request('1Gi')
    storage_task.set_memory_limit('2Gi')

    # -------------------------------------------------------------------------
    # Task 4: Metrics Storage (Save metrics to Cassandra)
    # -------------------------------------------------------------------------
    metrics_task = metrics_store_for_green_network(
        training_job_name=training_job_name,
        version=version,
        cassandra_host=cassandra_host,
        cassandra_port=cassandra_port,
        cassandra_username=cassandra_username,
        cassandra_password=cassandra_password,
        cassandra_keyspace=cassandra_keyspace,
        train_rmse=training_task.outputs['train_rmse'],
        test_rmse=training_task.outputs['test_rmse'],
        training_time=training_task.outputs['training_time'],
        ram_energy_kwh=training_task.outputs['ram_energy_kwh'],
        cpu_energy_kwh=training_task.outputs['cpu_energy_kwh'],
        gpu_energy_kwh=training_task.outputs['gpu_energy_kwh'],
        co2_emissions_kg=training_task.outputs['co2_emissions_kg']
    )
    metrics_task.after(training_task)  # ✅ 명시적 dependency 연결

    metrics_task.set_cpu_request('500m')
    metrics_task.set_cpu_limit('1')
    metrics_task.set_memory_request('512Mi')
    metrics_task.set_memory_limit('1Gi')


# -------------------------------------------------------------------------
# Compile pipeline to YAML
# -------------------------------------------------------------------------
if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=green_network_pipeline,
        package_path='green_network_pipeline.yaml'
    )
    print("✅ Pipeline compiled successfully: green_network_pipeline.yaml")
