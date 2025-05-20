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
from typing import List

@component(
    base_image="python:3.12",
    packages_to_install=[],
    target_image="model_training:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def model_training(featurepath: str, featureList: List[str], model_type: str = 'LSTM')->str:
    from logger import get_default_logger
    logger = get_default_logger(name='model-training')
    logger.info(f'model training will be done with featurepath:{featurepath} featurelist:{featureList} model_type:{model_type}')
    return "model_path"