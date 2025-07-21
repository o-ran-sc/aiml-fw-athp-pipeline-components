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
from kfp import compiler, dsl
from kfp import kubernetes, compiler

@dsl.pipeline()
def pipeline(featurepath: str, epochs: str, modelname: str, modelversion:str):
    from feature_extraction.feature_extraction_component import download_features
    from model_training.model_training_component import model_training
    from model_storage.model_storage_component import model_storage
    from metrics_store.metrics_store_component import metrics_store

    config_str = {
        "endpoint_url" : "http://leofs.kubeflow:8080",
        "aws_access_key_id" : "leofs",
        "aws_secreat_access_key" : "bGiBt0q2ub"
    }

    featureList = ["pdcpBytesDl", "pdcpBytesUl"]
    target_storage_key = 'test_dataset_influx_01_1'
    # featurepath = "testing_influxdb_01_1"

    ################# create pvc ########################
    pvcComp = kubernetes.CreatePVC(access_modes=['ReadWriteMany'],
                         pvc_name_suffix='-test',
                         size= '1Gi',
                         storage_class_name= 'nfs-client',
                         )

    ##################### download feature ##################
    comp1 = download_features(featurepath= featurepath,
                             featureList=featureList,
                             target_storage_config=config_str,
                             target_storage_key=target_storage_key)
    comp1.set_caching_options(False)
    comp1.after(pvcComp)
    kubernetes.set_image_pull_policy(comp1, "IfNotPresent")

    print(f"output of feature extraction:{comp1.output}")

    ####################   model training #################
    comp2 = model_training(featurepath=target_storage_key,
                           featureList=featureList,
                           model_config={"a": "b"},
                           target_storage_config=config_str,
                           target_dataset_name=target_storage_key)
    comp2.set_caching_options(False)
    comp2.after(comp1)
    kubernetes.mount_pvc(task=comp2,
                         pvc_name=pvcComp.outputs['name'],
                         mount_path='/model')
    kubernetes.set_image_pull_policy(comp2, "IfNotPresent")

    print(f"output of model training:{comp2.outputs}")

    ################## model storage ######################
    comp3 = model_storage(modelpath=comp2.outputs['path'],
                          modelname=modelname,
                          modelversion=modelversion)
    comp3.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp3, "IfNotPresent")
    kubernetes.mount_pvc(task=comp3,
                         pvc_name=pvcComp.outputs['name'],
                         mount_path='/model')

    print(f"output of model storage:{comp3.output}")

    ################# metrics store #########################
    comp4 = metrics_store(metrics={"accuracy": comp2.outputs['accuracy']})
    comp4.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp4, "IfNotPresent")

    print(f"output of model storage:{comp4.output}")

    ################ delete pvc #############################
    # Note: should be used as exithandler but component with
    # dependency could not be used as exithandler in kubeflow.
    deletePVC = kubernetes.DeletePVC(pvc_name=pvcComp.outputs['name'])
    deletePVC.after(comp3, comp4)


compiler.Compiler().compile(pipeline, "pipeline.yaml")
