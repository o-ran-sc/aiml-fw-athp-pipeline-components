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
from typing import Dict
@component(
    base_image="python:3.10",
    packages_to_install=[],
    target_image="metrics_store:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def metrics_store(metrics: Dict[str, str]) -> str:
    from logger import get_default_logger
    logger = get_default_logger(name='metrics-store')
    logger.info(f'metrics to store metrics:{metrics}')
    return "done"