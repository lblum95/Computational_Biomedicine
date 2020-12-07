# HK, 2020 - 11 - 21
import keras
import tensorflow as tf
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import Sequential
from kerastuner.engine.hypermodel import HyperModel
from tensorflow import keras
from tensorflow.keras import layers

""" 
taken from https://github.com/bio-ontology-research-group/phenomenet-vp/blob/master/dev/nn_final_training.py
"""


class Phenomenet:
    def __init__(self, input_dim: int):
        self.input_dim = input_dim

    def get_phenomenet(self):
        model = Sequential()
        model.add(Dense(67, input_dim=self.input_dim, kernel_initializer='uniform', activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(32, kernel_initializer='uniform', activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(256, kernel_initializer='uniform', activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(1, kernel_initializer='uniform', activation='sigmoid'))

        adam = keras.optimizers.Adam(lr=0.001)
        loss = tf.keras.losses.BinaryCrossentropy()
        model.compile(loss=loss, optimizer=adam,
                      metrics=['accuracy', 'AUC', tf.keras.metrics.Precision(name='precision'),
                               tf.keras.metrics.Recall()])

        return model


class HyperPhenomenet(HyperModel):

    def __init__(self, input_dim):
        self.input_dim = input_dim

    def build(self, hp):
        # optimizers = {
        #     'Adam': keras.optimizers.Adam(
        #         hp.Choice('learning_rate_Adam',
        #                   values=[1e-2, 1e-3, 1e-4])),
        #     'SGD': tf.keras.optimizers.SGD(
        #         hp.Choice('learning_rate_SGD',
        #                   values=[1e-2, 1e-3, 1e-4]), momentum=0.0, nesterov=False, name='SGD')
        # }

        # which_optimizer = hp.Choice('optimizer', ['Adam', 'SGD'])
        model = keras.Sequential()
        model.add(layers.Dense(units=hp.Int('units_' + str(0),
                                            min_value=32,
                                            max_value=512,
                                            step=32),
                               activation='relu', input_dim=self.input_dim))
        for i in range(hp.Int('num_layers', 1, 20)):
            model.add(layers.Dense(units=hp.Int('units_' + str(i),
                                                min_value=32,
                                                max_value=512,
                                                step=32),
                                   activation='relu'))
            model.add(Dropout(rate=hp.Float('dropout_' + str(i), 0, 0.5, step=0.1, default=0.5)))
        model.add(Dense(1, kernel_initializer='uniform',
                        activation='sigmoid'))
        model.compile(
            optimizer=keras.optimizers.Adam(
                hp.Choice('learning_rate_Adam',
                          values=[1e-2, 1e-3, 1e-4])),
            loss='binary_crossentropy',

            metrics=['accuracy', 'AUC', tf.keras.metrics.Precision(name='precision'),
                     tf.keras.metrics.Recall()])
        return model
