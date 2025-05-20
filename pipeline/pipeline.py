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
from kfp import kubernetes

@dsl.pipeline
def pipeline():
    from feature_extraction.feature_extraction_component import download_features
    from model_training.model_training_component import model_training
    from model_storage.model_storage_component import model_storage
    from metrics_store.metrics_store_component import metrics_store

    comp = download_features(featurepath="featurepath", featureList=["feature1", "feature2"])
    comp.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp, "IfNotPresent")

    print(f"output of feature extraction:{comp.output}")

    comp2 = model_training(featurepath=comp.output, featureList=["feature1", "feature2"])
    comp2.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp2, "IfNotPresent")

    print(f"output of model training:{comp2.output}")

    comp3 = model_storage(modelpath=comp2.output)
    comp3.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp3, "IfNotPresent")

    print(f"output of model storage:{comp3.output}")

    with dsl.If(comp3.output == 'done'):
        comp4 = metrics_store(metrics={"accuracy": ".8"})
        comp4.set_caching_options(False)
        kubernetes.set_image_pull_policy(comp4, "IfNotPresent")

        print(f"output of model storage:{comp4.output}")

compiler.Compiler().compile(pipeline, "pipeline.yaml")
