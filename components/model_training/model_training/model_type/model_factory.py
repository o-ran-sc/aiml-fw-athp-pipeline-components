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
from model_type.base_model import BaseModel
from model_type.lstm_model import LSTMModel
import numpy as np

def model_factory(X:np.ndarray, y: np.ndarray,model_type: str) -> BaseModel:
    if model_type == 'LSTM':
        return LSTMModel(X, y, config={'a': 'b'})