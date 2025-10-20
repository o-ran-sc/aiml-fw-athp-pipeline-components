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

from kfp.dsl import component, Input, Model
from typing import NamedTuple

@component(
    base_image="python:3.11-slim",
    packages_to_install=["boto3==1.28.0"]
)
def model_storage_for_green_network(
    model_input: Input[Model],
    training_job_name: str,
    version: str,
    s3_endpoint: str,
    s3_access_key: str,
    s3_secret_key: str,
    s3_bucket: str,
    train_rmse: float,
    test_rmse: float,
    co2_emissions_kg: float
) -> NamedTuple('Outputs', [('model_url', str), ('model_size_mb', float)]):
    import boto3
    import json
    from collections import namedtuple
    import traceback

    try:
        # Model Input에서 S3 경로 읽기
        with open(model_input.path, 'r') as f:
            s3_path = f.read().strip()
        
        print(f"Model S3 path: {s3_path}")
        
        # S3 경로 파싱 (s3://bucket/key)
        if not s3_path.startswith('s3://'):
            raise ValueError(f"Invalid S3 path: {s3_path}")
        
        # s3://ml-models/green-network/models/...model.pth 에서 key 추출
        s3_key = s3_path.replace(f"s3://{s3_bucket}/", "")
        
        # S3 Client 생성
        s3_client = boto3.client(
            's3',
            endpoint_url=s3_endpoint,
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
        
        # 모델 파일 크기 확인
        response = s3_client.head_object(Bucket=s3_bucket, Key=s3_key)
        model_size_bytes = response['ContentLength']
        model_size_mb = model_size_bytes / (1024 * 1024)
        
        print(f"Model size: {model_size_mb:.2f} MB")
        
        # Metadata 생성
        metadata = {
            'training_job_name': training_job_name,
            'version': version,
            'model_type': 'LSTM',
            'framework': 'PyTorch',
            'metrics': {
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'co2_emissions_kg': co2_emissions_kg
            },
            'model_size_mb': model_size_mb,
            'model_s3_path': s3_path
        }
        
        # Metadata를 S3에 업로드
        metadata_key = f"green-network/models/{training_job_name}/{version}/metadata.json"
        metadata_json = json.dumps(metadata, indent=2)
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=metadata_key,
            Body=metadata_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        print(f"Metadata saved to: s3://{s3_bucket}/{metadata_key}")
        print(f"Model URL: {s3_path}")
        
        Outputs = namedtuple('Outputs', ['model_url', 'model_size_mb'])
        return Outputs(model_url=s3_path, model_size_mb=model_size_mb)

    except Exception as e:
        print(f"Error in model storage: {e}")
        print(traceback.format_exc())
        raise