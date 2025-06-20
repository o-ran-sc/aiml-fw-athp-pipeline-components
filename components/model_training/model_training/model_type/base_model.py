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
from abc import abstractclassmethod, ABC
import numpy as np
from typing import Dict

class BaseModel(ABC):
    def __init__(self, X: np.ndarray, y: np.ndarray,config: Dict[str, any]=None):
        print('parent init is started')
        self.config = config
        self.model = None
        self.X = X
        self.y = y
        self._build_model()
        print('parent init is done')

    @abstractclassmethod
    def _build_model(self):
        pass

    @abstractclassmethod
    def train(self, X: np.ndarray, y: np.ndarray):
        pass

    @abstractclassmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

    def summary(self):
        self.model.summary()

    @abstractclassmethod
    def save(self, path: str):
        pass

    @abstractclassmethod
    def export(self, path:str):
        pass

    @abstractclassmethod
    def accuracy(self) -> str:
        pass