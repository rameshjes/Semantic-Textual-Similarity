from __future__ import division
from sklearn.linear_model import Ridge
import numpy as np
import pickle 

class RidgeModel:

	def __init__(self):

		self.model_path = 'model_svm_nltk_mrc.pkl' 
	'''
	Input: data observations (training example, desired output)
	return: model
	'''

	def trainModel(self, x_observations, y_observations):

		#alpha is regularization strength
		model = Ridge(alpha=10**0)  
		model.fit(np.array(x_observations), np.array(y_observations))

		#save model
		model_pickle = open(self.model_path, 'wb')
		pickle.dump(model, model_pickle)
		model_pickle.close()
		print "model saved"

		return model


	'''
	Predict data using trained model
	'''


	def predict_model(self, model, xs):


		return model.predict(xs)