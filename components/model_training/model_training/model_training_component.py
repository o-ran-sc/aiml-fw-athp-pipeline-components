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
    packages_to_install=["featurestoresdk", "modelmetricsdk"],
    target_image="model_training:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def model_training(featurepath: str, target_storage_config: Dict[str, str],
                   target_dataset_name: str, featureList: List[str],
                   model_config: Dict[str, str],
                   model_type: str = 'LSTM') -> NamedTuple('outputs', path=str, accuracy=str): # type: ignore
    from logger import get_default_logger
    import logging
    import pandas as pd
    from modelmetricsdk.artifact_manager import ArtifactManager

    logger = get_default_logger(name='model-training')
    logger.info(f'model training will be done with featurepath:{featurepath} featurelist:{featureList} model_type:{model_type}')

    TEMP_DATASET_CSV = 'test.csv'
    manager = ArtifactManager(target_storage_config, logger=logger)
    manager.download_dataset(dataset_name= target_dataset_name, dest_path=TEMP_DATASET_CSV)

    features = pd.read_csv(TEMP_DATASET_CSV)
    logger.debug(f'dataframe after download: {features.head()}')

    logger.debug(f'Previous Data Types are --> ', features.dtypes)
    # TODO: Needed to fix to make generic
    features["pdcpBytesDl"] = pd.to_numeric(features["pdcpBytesDl"], downcast="float")
    features["pdcpBytesUl"] = pd.to_numeric(features["pdcpBytesUl"], downcast="float")
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