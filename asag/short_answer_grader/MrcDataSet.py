import pandas as pd 
import codecs
import os
from os.path import basename
import glob
import numpy as np

class MrcSet:

	def readFile(self, filename):

		with codecs.open(filename, 'rb') as data_file:

			texts = []
			data_ids = []

			for line in data_file:

				if line[1] == ' ':
					data_id = line[:1]
					text = line[1:]
					
				if line[2] == ' ':
					data_id = line[:2]
					text = line[2:]

				data_ids.append(data_id)
				texts.append(text)

			# print data_ids
			data_frame = pd.DataFrame({'id': data_ids, 'text': texts})

		return data_frame


	def getStringData(self, path = 'rnd_nltk/sample_data/mrc_dataset/data/raw/'):	

		questions_file = path + 'questions'
		teacher_answers_filename = path + 'model_answers'
		students_answer_filename = path + 'all_answers'

		questions = self.readFile(questions_file)
		student_answers = self.readFile(students_answer_filename)
		teacher_answers = self.readFile(teacher_answers_filename)

		return questions, student_answers, teacher_answers

	def getScores(self, path = 'rnd_nltk/sample_data/mrc_dataset/data/scores/'):

		score_paths = glob.glob(path + '*')
		scores = dict()
		count = 0
		for scores_path in score_paths:
			score_files = glob.glob(scores_path + '/*')
			question_scores = []

			for score_file in score_files:
				file_scores = []
				_score_file = open(score_file, 'r')
				for line in _score_file:
					file_scores.append(float(line))
					count += 1
				question_scores.append(file_scores)

			scores_key = basename(scores_path)
			scores[scores_key] = question_scores
		return scores


	def convertToDict(self, string_data):

		data = dict()
		#convert string_data(pandas_frame) values to dictionary

		for arg, key in enumerate(string_data.id.tolist()):
		    data[key] = string_data.text.iloc[arg]

		return data


	def readData(self):
		    
		
		#question, teacher answers and student asnwers are pandas
		questions, student_answers, teacher_answers = self.getStringData()
		print len(questions)
		print len(student_answers)
		
		scores = self.getScores()  #for every answer there are 3 scores
		print len(scores['10'][0])

		
		teacher_answers = self.convertToDict(teacher_answers) # 87 key with ans
		questions = self.convertToDict(questions) #87 keys
		
		teacher_answers_list = []
		student_answers_list = []
		questions_list = []
		scores_list = [] # size 206676
		keys_list = [] #question numbers total size 206676

		
		for key in student_answers.id.unique().tolist(): 

		    
		    masked_student_answers = student_answers[student_answers.id == key]
		    
		    masked_scores = scores[key] #gives 3 sets of score for queried key

		    for score_set in masked_scores:
		        for mask_arg in range(len(masked_student_answers.text)):

		            student_answer = masked_student_answers.text.iloc[mask_arg]
		            student_answers_list.append(student_answer)
		            scores_list.append(score_set[mask_arg])
		            teacher_answers_list.append(teacher_answers[key])
		            questions_list.append(questions[key])
		            keys_list.append(key)

		return pd.DataFrame({'id': keys_list,
		                     'questions': questions_list,
		                 'teacher': teacher_answers_list,
		                 'student': student_answers_list,
		                 'scores': scores_list})

	
	def normalizeMrc(self, data):

		data.iloc[:, 2] = data.iloc[:, 2] / 2.0

		return data


	def splitData(self, data, validation_split):

		train_split = 1 - validation_split
		train_set = []
		test_set = []

		
		for data_id in data.id.unique():

			masked_id_data = data[data.id == data_id]
			
			unique_student_answers = masked_id_data.student.unique()
			
			train_size = int(train_split * len(unique_student_answers))
			
			unique_student_train = unique_student_answers[:train_size]
			unique_student_val = unique_student_answers[train_size:]
			for sentence in unique_student_train:
				train_set.append(masked_id_data[masked_id_data.student == sentence])
			for sentence in unique_student_val:
				test_set.append(masked_id_data[masked_id_data.student == sentence])

		return pd.concat(train_set), pd.concat(test_set)



	def preProcessData(self, data):

		student = data.student.as_matrix()
		teacher = data.teacher.as_matrix()
		scores = data.scores.as_matrix()
		questions = data.questions.as_matrix()

		return student, teacher, questions, scores 


	def _encodeData(self, data):

	    inputs = {'student_input' : np.asarray(data[0]),
	              'teacher_input' : np.asarray(data[1]),
	              'questions' : np.asarray(data[2])
	            }
	    outputs = {'scores': data[3] }
	    return inputs, outputs


	def loadData(self, validation_split = 0.2):

	    data = self.readData()

	    data = self.normalizeMrc(data)
	    training_set, testing_set = self.splitData(data, validation_split)


	    train_data = self.preProcessData(training_set)
	    test_data = self.preProcessData(testing_set)
	    
	    train_data = self._encodeData(train_data)
	    test_data = self._encodeData(test_data)

	    return train_data, test_data

if __name__ == '__main__':
	mrc = MrcSet()
	mrc.loadData()