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

@component(
    base_image="python:3.12",
    packages_to_install=["modelmetricsdk", "requests==2.28.0"],
    target_image="model_storage:v1",
    pip_index_urls=["https://pypi.org/simple/"],
)
def model_storage(modelpath: str,
                  modelname: str,
                  modelversion:str)->str:
    from logger import get_default_logger
    import requests
    from modelmetricsdk.model_metrics_sdk import ModelMetricsSdk

    logger = get_default_logger(name='model-storage')
    logger.info(f'model storage will be done to modelpath:{modelpath}')

    # store model
    logger.info(f'register the trained model to mme')
    artifactversion="1.0.0"    # need to decide if it is right to provide 1.0.0
    url = f"http://modelmgmtservice.traininghost:8082/ai-ml-model-registration/v1/model-registrations/updateArtifact/{modelname}/{modelversion}/{artifactversion}"

    logger.info(f'sending request to URL :{url}')
    try:
        updated_model_info= requests.post(url).json()
        logger.info(updated_model_info)
    except Exception as e:
        logger.info(f'error while mme operation: {e}')
        raise e

    logger.info(f'uploading model to leofs with name:{modelname}, modelver:{modelversion}, artifactnumber:{artifactversion}')
    mmsdk = ModelMetricsSdk()

    try:
        mmsdk.upload_model(model_path="./", model_name=modelname,
                           model_version=modelversion,
                           artifact_version=artifactversion)
    except Exception as e:
        logger.info(f'error while uploading the model:{e}')
        raise e

    logger.info('successfully uploaded the model')
    return "done"
