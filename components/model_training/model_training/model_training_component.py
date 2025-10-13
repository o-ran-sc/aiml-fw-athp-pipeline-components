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
from kfp.dsl import component
from typing import List, Dict, NamedTuple

@component(
    base_image="python:3.10",
    packages_to_install=["tensorflow==2.17.1", "modelmetricsdk==0.3.1","kfp==2.13.0","pandas==2.2.1"],
    target_image="model_training:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def _extract_feature_group_name(featurepath: str) -> str:
    """
    Extract feature group name from featurepath
    Example: 'aimlfw_feature_08_3' -> 'aimlfw_feature_08'
    """
    # Split by underscore and remove the last part (training job id)
    parts = featurepath.split('_')
    if len(parts) >= 2:
        # Remove trailing numeric parts to get feature group name
        while parts and parts[-1].isdigit():
            parts.pop()
        return '_'.join(parts)
    return featurepath
def _get_feature_list_from_config(feature_group_name: str) -> List[str]:
    """
    Retrieve feature group configuration and extract feature list
    Returns: List of feature names
    """
    import requests

    BASE_URL = f"http://localhost:32002"
    try:
        url = f"{BASE_URL}/featureGroup/{feature_group_name}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        s = data.get("feature_list", "")
        # Example: "pdcpBytesDl,pdcpBytesUl" -> ["pdcpBytesDl", "pdcpBytesUl"]
        featureList = [x.strip() for x in s.split(",") if x.strip()]
        return featureList

    except Exception as e:
        return []

def model_training(featurepath: str, target_storage_config: Dict[str, str],
                   target_dataset_name: str,
                   model_config: Dict[str, str],
                   model_type: str = 'LSTM') -> NamedTuple('outputs', path=str, accuracy=str): # type: ignore
    from logger import get_default_logger
    import logging
    import pandas as pd
    from modelmetricsdk.artifact_manager import ArtifactManager

    feature_group_name = _extract_feature_group_name(featurepath)
    featureList = _get_feature_list_from_config(feature_group_name)
    logger = get_default_logger(name='model-training')
    logger.info(f'model training will be done with featurepath:{featurepath} featurelist:{featureList} model_type:{model_type}')

    TEMP_DATASET_CSV = 'test.csv'
    manager = ArtifactManager(target_storage_config, logger=logger)
    manager.download_dataset(dataset_name= target_dataset_name, dest_path=TEMP_DATASET_CSV)

    features = pd.read_csv(TEMP_DATASET_CSV)
    logger.debug(f'dataframe after download: {features.head()}')

    logger.debug(f'Previous Data Types are --> ', features.dtypes)
    for col in featureList:
        features[col] = pd.to_numeric(features[col], errors="coerce", downcast="float")
    logger.debug(f'New Data Types are --> ', features.dtypes)

    X, y = split_series(features.values, 10, 1)
    X = X.reshape((X.shape[0], X.shape[1],X.shape[2]))
    y = y.reshape((y.shape[0], y.shape[2]))
    logger.debug(X.shape)
    logger.debug(y.shape)

    from model_type.model_factory import model_factory
    model = model_factory(X, y, model_type)
    model.train()

    print('exporting model to /model/export/')
    model.export('/model/export/')

    # calculate accuracy
    print('calculate accuracy')
    accuracy = model.accuracy()
    print(f'accuracy calculated: {accuracy}')

    outputs = NamedTuple('outputs', path=str, accuracy=str)
    return outputs('/model/export', accuracy)

def split_series(series, n_past, n_future):
    import numpy as np
    X, y = list(), list()
    for window_start in range(len(series)):
        past_end = window_start + n_past
        future_end = past_end + n_future
        if future_end > len(series):
            break
        # slicing the past and future parts of the window
        past, future = series[window_start:past_end, :], series[past_end:future_end, :]
        X.append(past)
        y.append(future)
    return np.array(X), np.array(y)