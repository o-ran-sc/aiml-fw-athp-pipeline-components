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

FROM python:3.12

WORKDIR /usr/local/src/kfp/components
RUN pip install --index-url https://pypi.org/simple/ --no-cache-dir pandas cassandra-driver==3.29.1 pandas setuptools kfp==2.12.1 featurestoresdk modelmetricsdk
COPY . .
