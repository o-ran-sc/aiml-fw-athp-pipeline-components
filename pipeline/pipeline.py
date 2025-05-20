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

    comp = download_features(featurepath="featurepath", featureList=["feature1", "feature2"])
    comp.set_caching_options(False)
    kubernetes.set_image_pull_policy(comp, "IfNotPresent")

    print(f"output of feature extraction:{comp.output}")

compiler.Compiler().compile(pipeline, "pipeline.yaml")
