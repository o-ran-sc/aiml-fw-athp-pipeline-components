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

@dsl.component(
    
    base_image="python:3.11-slim",
    packages_to_install=[
        "cassandra-driver==3.29.1"
    ]
)
def metrics_store_for_green_network(
    training_job_name: str,
    version: str,
    cassandra_host: str,
    cassandra_port: int,
    cassandra_username: str,
    cassandra_password: str,
    cassandra_keyspace: str,
    train_rmse: float,
    test_rmse: float,
    training_time: float,
    ram_energy_kwh: float,
    cpu_energy_kwh: float,
    gpu_energy_kwh: float,
    co2_emissions_kg: float
):
    from cassandra.cluster import Cluster
    from cassandra.auth import PlainTextAuthProvider
    from datetime import datetime
    import traceback

    try:
        auth_provider = PlainTextAuthProvider(
            username=cassandra_username,
            password=cassandra_password
        )
        cluster = Cluster(
            [cassandra_host],
            port=cassandra_port,
            auth_provider=auth_provider
        )
        session = cluster.connect(cassandra_keyspace)

        create_table_cql = f"""
        CREATE TABLE IF NOT EXISTS {cassandra_keyspace}.green_network_metrics (
            training_job_name TEXT,
            version TEXT,
            timestamp TIMESTAMP,
            metric_type TEXT,
            metric_name TEXT,
            metric_value DOUBLE,
            PRIMARY KEY ((training_job_name, version), timestamp, metric_type, metric_name)
        ) WITH CLUSTERING ORDER BY (timestamp DESC, metric_type ASC, metric_name ASC);
        """
        session.execute(create_table_cql)

        timestamp = datetime.now()
        metrics = [
            ('performance', 'train_rmse', train_rmse),
            ('performance', 'test_rmse', test_rmse),
            ('energy', 'ram_energy_kwh', ram_energy_kwh),
            ('energy', 'cpu_energy_kwh', cpu_energy_kwh),
            ('energy', 'gpu_energy_kwh', gpu_energy_kwh),
            ('energy', 'total_energy_kwh', ram_energy_kwh + cpu_energy_kwh + gpu_energy_kwh),
            ('carbon', 'co2_emissions_kg', co2_emissions_kg),
            ('carbon', 'co2_emissions_g', co2_emissions_kg * 1000),
            ('time', 'training_time_seconds', training_time),
            ('time', 'training_time_minutes', training_time / 60)
        ]

        insert_cql = f"""
        INSERT INTO {cassandra_keyspace}.green_network_metrics 
        (training_job_name, version, timestamp, metric_type, metric_name, metric_value)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        prepared = session.prepare(insert_cql)

        for metric_type, metric_name, metric_value in metrics:
            session.execute(prepared, (
                training_job_name,
                version,
                timestamp,
                metric_type,
                metric_name,
                float(metric_value)
            ))

        cluster.shutdown()

    except Exception as e:
        print(f"Error in metrics store: {e}")
        print(traceback.format_exc())
        raise