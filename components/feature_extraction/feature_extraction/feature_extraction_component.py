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
from typing import List, Dict

@component(
    base_image="python:3.10",
    packages_to_install=["featurestoresdk", "modelmetricsdk"],
    target_image="feature_extraction:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def download_features(featurepath: str, featureList: List[str],
                      target_storage_config: Dict[str, str], target_storage_key: str)->str:
    import json
    from logger import get_default_logger
    from featurestoresdk.feature_store_sdk import FeatureStoreSdk
    from modelmetricsdk.artifact_manager import ArtifactManager

    logger = get_default_logger(name='feature_extraction')
    logger.info(f'donwload feature from path:{featurepath} featurelist:{featureList}')

    logger.debug(f'start extracting feature')
    fs_sdk = FeatureStoreSdk()
    features = fs_sdk.get_features(featurepath, featureList)

    logger.debug(f"dataframe: {features}")

    TMP_FILENAME_CSV = 'out.csv'
    logger.debug(f'will write {TMP_FILENAME_CSV} to target storage config:{target_storage_config} key:{target_storage_key}')
    features.to_csv(TMP_FILENAME_CSV, index=False)

    logger.debug(f'loading storage config from json {target_storage_config}')

    manager = ArtifactManager(target_storage_config, logger=logger)
    manager.upload_dataset(TMP_FILENAME_CSV, target_storage_key)

    logger.info(f'component is successfully executed and feature is availble at key:{target_storage_key}')
    return "success"