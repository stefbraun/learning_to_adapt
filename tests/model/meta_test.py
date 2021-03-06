from keras.layers import Dense, Conv1D
from keras.models import Sequential
import numpy as np
import unittest

from learning_to_adapt.model import create_meta_learner, create_model_wrapper


class TestLoop(unittest.TestCase):

  def testMetaLearnerCanPredict(self):
    model = self.create_model()
    wrapper = create_model_wrapper(model, sparse=True, num_sparse_params=4)
    meta = create_meta_learner(wrapper)
    meta.compile(loss=model.loss, optimizer='adam')

    batch = next(self.generator())
    self.assertEquals((1, 2, 1), meta.predict(batch[0]).shape)

  def testMetaLearnerCanPredictWithConvolutionalModel(self):
    model = self.create_convolutional_model()
    wrapper = create_model_wrapper(model)
    meta = create_meta_learner(wrapper, input_type='sequences')
    meta.compile(loss=model.loss, optimizer='adam')

    batch = next(self.generator(return_sequences=True))
    self.assertEquals((1, 1, 2, 1), meta.predict(batch[0]).shape)

  def testMetaLearnerCanOverfit(self):
    np.random.seed(0)

    model = self.create_model()
    wrapper = create_model_wrapper(model)
    meta = create_meta_learner(wrapper)
    meta.compile(loss=model.loss, optimizer='adam')

    generator = self.generator()
    history = meta.fit_generator(generator, steps_per_epoch=100, epochs=5)

    loss = history.history["loss"]
    self.assertTrue(loss[0] > loss[-1])
    self.assertTrue(0.05 > loss[-1])

  def testMetaLearnerCanOverfitWithConvolutionalModel(self):
    np.random.seed(0)

    model = self.create_convolutional_model()
    wrapper = create_model_wrapper(model)
    meta = create_meta_learner(wrapper, input_type='sequences')
    meta.compile(loss=model.loss, optimizer='adam')

    generator = self.generator(return_sequences=True)
    history = meta.fit_generator(generator, steps_per_epoch=100, epochs=5)

    loss = history.history["loss"]
    self.assertTrue(loss[0] > loss[-1])
    self.assertTrue(0.05 > loss[-1])

  def create_model(self):
    model = Sequential()
    model.add(Dense(2, use_bias=True, input_shape=(1,), trainable=False))
    model.add(Dense(1, use_bias=True))
    model.compile(loss='mse', optimizer='adam')
    return model

  def create_convolutional_model(self):
    model = Sequential()
    model.add(Conv1D(2, 1, use_bias=True, input_shape=(None, 1), trainable=False))
    model.add(Conv1D(1, 1, use_bias=True))
    model.compile(loss='mse', optimizer='adam')
    return model

  def generator(self, return_sequences=False):
    while True:
      params = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
      training_feats = np.array([[[[1.], [0.]]] * 5])
      training_labels = np.array([[[[1.], [0.]]] * 5])
      testing_feats = np.array([[[1.], [0.]]])
      testing_labels = np.array([[[1.], [0.]]])

      if return_sequences:
        training_feats = np.expand_dims(training_feats, 2)
        training_labels = np.expand_dims(training_labels, 2)
        testing_feats = np.expand_dims(testing_feats, 1)
        testing_labels = np.expand_dims(testing_labels, 1)

      yield [params, training_feats, training_labels, testing_feats], testing_labels
