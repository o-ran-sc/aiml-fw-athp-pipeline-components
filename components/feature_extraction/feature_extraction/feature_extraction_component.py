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
    packages_to_install=["featurestoresdk==0.3.1", "modelmetricsdk==0.3.1","kfp==2.13.0"],
    target_image="feature_extraction:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def _extract_feature_group_name(featurepath: str) -> str:
    """
    Extract feature group name from featurepath
    Example: 'aimlfw_feature_08_3' -> 'aimlfw_feature_08'
    """
    parts = featurepath.split('_')
    if len(parts) >= 2:
        while parts and parts[-1].isdigit():
            parts.pop()
        return '_'.join(parts)
    return featurepath

def _get_feature_list_from_config(feature_group_name: str) -> List[str]:
    """
    Retrieve feature list from Cassandra system tables
    Returns: List of feature names
    """
    from featurestoresdk.feature_store_sdk import FeatureStoreSdk 
    try:
        fs_sdk = FeatureStoreSdk()

        query = f"""
        SELECT column_name 
        FROM system_schema.columns 
        WHERE keyspace_name = '{fs_sdk.feature_store_db_name}' 
        AND table_name = '{feature_group_name}'
        """
        
        response = fs_sdk.session.execute(query)
        featureList = [row.column_name for row in response]
        return featureList

    except Exception as e:
        return []

def download_features(featurepath: str,
                      target_storage_config: Dict[str, str], target_storage_key: str)->str:
    import json
    from logger import get_default_logger
    from featurestoresdk.feature_store_sdk import FeatureStoreSdk
    from modelmetricsdk.artifact_manager import ArtifactManager

    logger = get_default_logger(name='feature_extraction')
    feature_group_name = _extract_feature_group_name(featurepath)
    featureList = _get_feature_list_from_config(feature_group_name)
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