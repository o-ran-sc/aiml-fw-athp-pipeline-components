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
from kfp.dsl import Output, Dataset
from typing import Optional

@dsl.component(
    
    base_image="python:3.11-slim",
    packages_to_install=[
        "influxdb-client==1.38.0",
        "pandas==2.1.0",
        "boto3==1.28.0",
        "numpy==1.24.3"
    ]
)
def feature_extraction_for_green_network(
    training_job_name: str,
    influxdb_url: str,
    influxdb_token: str,
    influxdb_org: str,
    influxdb_bucket: str,
    s3_endpoint: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_bucket: str,
    features_csv: Output[Dataset],
    cell_name: Optional[str] = None,
    time_range_days: int = 30
) -> dict:
    import pandas as pd
    import numpy as np
    from influxdb_client import InfluxDBClient
    import boto3
    from datetime import datetime, timedelta
    import traceback

    try:
        client = InfluxDBClient(
            url=influxdb_url,
            token=influxdb_token,
            org=influxdb_org
        )
        query_api = client.query_api()


        time_range = f"-{time_range_days}d"
        cell_filter = ""
        if cell_name:
            cell_filter = f'|> filter(fn: (r) => r["Viavi.Cell.Name"] == "{cell_name}")'

        flux_query = f'''
        from(bucket: "{influxdb_bucket}")
            |> range(start: {time_range})
            |> filter(fn: (r) => r["_measurement"] == "cell_metrics")
            |> filter(fn: (r) => r["_field"] == "RRU.PrbUsedDl")
            {cell_filter}
            |> sort(columns: ["_time"])
            |> keep(columns: ["_time", "_value", "Viavi.Cell.Name"])
        '''

        result = query_api.query_data_frame(flux_query)
        client.close()

        if result.empty:
            raise ValueError("No data returned from InfluxDB")

        df = result.rename(columns={
            '_time': 'timestamp',
            '_value': 'RRU.PrbUsedDl',
            'Viavi.Cell.Name': 'cell_name'
        })[['timestamp', 'RRU.PrbUsedDl']]

        df = df.sort_values('timestamp').reset_index(drop=True)
        df = df[df.index % 30 == 0].reset_index(drop=True)

        if df['RRU.PrbUsedDl'].isna().sum() > 0:
            df['RRU.PrbUsedDl'].fillna(method='ffill', inplace=True)
            df['RRU.PrbUsedDl'].fillna(method='bfill', inplace=True)

        local_csv_path = f"/tmp/{training_job_name}_features.csv"
        df.to_csv(local_csv_path, index=False)

        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
        s3_key = f"green-network/features/{training_job_name}_features.csv"
        s3_client.upload_file(local_csv_path, s3_bucket, s3_key)
        s3_path = f"s3://{s3_bucket}/{s3_key}"

        import shutil
        shutil.copy(local_csv_path, features_csv.path)

        return {
            'num_samples': int(len(df)),
            'features': ['RRU.PrbUsedDl'],
            'csv_path': s3_path,
            'time_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}",
            'statistics': {
                'mean': float(df['RRU.PrbUsedDl'].mean()),
                'std': float(df['RRU.PrbUsedDl'].std()),
                'min': float(df['RRU.PrbUsedDl'].min()),
                'max': float(df['RRU.PrbUsedDl'].max())
            }
        }

    except Exception as e:
        print(f"Error in feature extraction: {e}")
        print(traceback.format_exc())
        raise
