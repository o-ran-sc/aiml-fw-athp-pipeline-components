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
from typing import Dict
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten, Dropout, Activation
from tensorflow.keras.layers import LSTM
from model_type.base_model import BaseModel

class LSTMModel(BaseModel):

    def __init__(self, X: np.ndarray, y: np.ndarray, config: Dict[str, any]={}):
        # self.config = config
        # self.model = None
        self.input_shape = (X.shape[1], X.shape[2])
        self.lstm_units = config.get('lstm_units', [3])
        self.activation = config.get('activation', 'tanh')
        self.return_sequence_list = config.get(
            'return_sequence_list',
            [True] * (len(self.lstm_units)-1) + [False]
            )
        self.optimizer = config.get('optimizer', 'adam')
        self.loss = config.get('loss', 'mse')
        self.metrics = config.get('metrics', ['mse'])
        self.epoches = config.get('epoches', 2)
        self.validation_split = config.get('validation_split', 0.2)
        self.batch_size = config.get('batch_size', 10)
        super().__init__(X, y, config)
        print('LSTM: init is done')

    def _build_model(self):
        print('model build invoked')

        model = Sequential()
        # model.add(LSTM(units = 150, activation="tanh" ,return_sequences = True, input_shape = ))
        # model.add(LSTM(units = 150, return_sequences = True,activation="tanh"))
        # model.add(LSTM(units = 150,return_sequences = False,activation="tanh" ))
        # model.add((Dense(units = self.X.shape[2])))

        for i, (units, return_seq) in enumerate(zip(self.lstm_units, self.return_sequence_list)):
            if i == 0:
                model.add(LSTM(units=units,
                               activation=self.activation,
                               return_sequences=return_seq,
                               input_shape=self.input_shape))
            else:
                model.add(LSTM(units=units,
                               activation=self.activation,
                               return_seqence=return_seq,
                               ))
        model.add(Dense(units=self.input_shape[1]))
        model.compile(loss=self.loss, optimizer=self.optimizer,metrics=self.metrics)

        self.model = model
        print(f'model is prepared : {self.summary()}')

    def train(self):
        print('model train for LSTM')
        self.model.fit(self.X, self.y,
                       batch_size=self.batch_size,
                       epochs=self.epoches,
                       validation_split=self.validation_split,
                       )

    def predict(self, X: np.ndarray) -> np.ndarray:
        print('lstm: predict invoked')
        return self.model.predict(X)

    def save(self, path: str, format: str='tf'):
        print(f'save model to {path}')
        self.model.save(path)
        print('model saved')

    def export(self, path: str):
        print('lstm: model export invoked')
        self.model.export(path)

    def accuracy(self) -> str:
        print('lstm: accuracy invoked')
        # Note: return should be float
        accuracy = str(np.mean(np.absolute(np.asarray(self.y) - np.asarray(self.predict(self.X)))<5))
        print(f'lstm: calculated{accuracy}')
        return accuracy

