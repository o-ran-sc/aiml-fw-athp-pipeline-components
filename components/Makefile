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
.PHONY: build-model-training build-feature-extraction build-model-storage build-metrics-store build-all install-all clean-all all
PROJECTS := feature_extraction model_storage model_training metrics_store
build-feature-extraction:
	cd feature_extraction && kfp component build feature_extraction/ --component-filepattern feature_extraction_component.py --push-image

build-model-training:
	cd model_training && kfp component build model_training/ --component-filepattern model_training_component.py --push-image

build-model-storage:
	cd model_storage && kfp component build model_storage/ --component-filepattern model_storage_component.py --push-image

build-metrics-store:
	cd metrics_store && kfp component build metrics_store/ --component-filepattern metrics_store_component.py --push-image

build-all:
	@for dir in $(PROJECTS); do \
		echo " build $$dir..."; \
		(cd $$dir && python -m build); \
	done

install-all:
	@for dir in $(PROJECTS); do \
		echo " install $$dir..."; \
		(cd $$dir && pip install --force-reinstall dist/*.whl); \
	done

clean-all:
	@for dir in $(PROJECTS); do \
		echo " clean $$dir..."; \
		(cd $$dir && rm -rf build/ dist/ *.egg-info && rm -rf); \
	done

all: clean-all build-all install-all
