from __future__ import division

import featuresExtract
import ridgeModel
import MrcDataSet
import mohlerDataSet 
import pickle 
from scipy.stats import pearsonr
import numpy as np
from sklearn.metrics import mean_squared_error
from math import sqrt

import xlsxwriter

import time
import sys 

class TrainGrader:

	def __init__(self, flag):


		# self.readDataSet = DataSet.ReadDataSet()
		self.flag = flag
		self.featuresExtract = featuresExtract.Features(self.flag)
		self.ridgeModel = ridgeModel.RidgeModel()
		self.model_path = 'model_svm_nltk_mrc.pkl'
		

	def getFeatures(self, question, ref_answer, student_response):

		# print "question ", question
		sim_alignment, cov_alignment, parse_results = \
						self.featuresExtract.sts_alignment(ref_answer, student_response)
		#include question demoting
		q_demoted_sim_alignment, q_demoted_cov_alignment, _ = \
						self.featuresExtract.sts_alignment(ref_answer, student_response,\
															parse_results, question)
		

		sim_cvm = self.featuresExtract.sts_cvm(ref_answer, student_response, \
												parse_results)

		# print "cosine similarity ", sim_cvm
		q_demoted_sim_cvm = self.featuresExtract.sts_cvm(ref_answer, student_response, \
														parse_results, question)

		lr = self.featuresExtract.ComputeLengthRatio(ref_answer, student_response, parse_results)

		feature_vector = (sim_alignment, cov_alignment, 
						 q_demoted_sim_alignment, q_demoted_cov_alignment,
						 sim_cvm, q_demoted_sim_cvm, lr)

		return feature_vector


	def constructTrainingExamples(self, data):

		

		train_examples = []
		questions = []
		ref_answer = []
		student_answer = []
		questions = data[0]['questions']
		ref_answer = data[0]['teacher_input']
		student_answer = data[0]['student_input']
		scores = data[1]['scores']
		# print "start ", start
		n = 0

		for i in xrange(len(student_answer)):

			features = self.getFeatures(questions[i], ref_answer[i], student_answer[i])


			score = scores[i]

			train_examples.append((features, score))

			n += 1
			print n

		return train_examples



	def trainGraderModel(self, train_examples):
		#trainModel(numberofFeatures, scores)
		model = self.ridgeModel.trainModel([item[0] for item in train_examples],
										[item[1] for item in train_examples])

		return model


	def assignGrade(self, data, model):


		results = []
		questions = []
		ref_answer = []
		student_answer = []
		questions = data[0]['questions']
		ref_answer = data[0]['teacher_input']
		student_answer = data[0]['student_input']

		row = 0
		col = 0
		
		for i in xrange(len(student_answer)):


			features = self.getFeatures(questions[i], ref_answer[i], student_answer[i])

			features = np.round(features,2)

			#predict model returns array, shape
			#we take array by accessing 0 index

			prediction = self.ridgeModel.predict_model(model, [features])[0]
			prediction = np.round(prediction, 2)
	
			results.append(prediction)

		workbook1.close()

		return results

if __name__ == '__main__':


	flag = sys.argv[1]

	grader = TrainGrader(flag)
	d = MrcDataSet.MrcSet()
	# d = mohlerDataSet.ReadDataSet_2442()
	train_data, test_data = d.loadData() 	
	
	training_examples = grader.constructTrainingExamples(train_data)

	
	print "training start"
	trainedModel = grader.trainGraderModel(training_examples)

	
	# # #Testing 
	# print "loading trained model"
	loaded_model = pickle.load(open(grader.model_path, 'rb'))

	predictions = grader.assignGrade(test_data, loaded_model)
	print "predictions ", predictions
	print "testing finished " 

	targets = test_data[1]['scores']
	n = len(predictions)
	pearson = pearsonr(targets, predictions)[0]
	print 'Pearson coefficient:', pearsonr(targets, predictions)[0]
	rmse = sqrt(mean_squared_error(targets, predictions))

	print "Mean Square error: ", rmse

	#Save in file 

	# f = open('spacy_mrc_results.txt','w')
	# f.writelines("n = " + str(n) + '\n')
	# f.writelines("pearson coefficient " + str(pearson) + '\n')
	# f.writelines("mean square error " + str(rmse) + '\n')
	# f.writelines("R2 score: " + str(r2) + '\n')
	# f.close() 