from __future__ import unicode_literals 
import pandas as pd 
import codecs
import os
from os.path import basename
import glob
import numpy as np

'''
Loading data set taken from :
https://github.com/oarriaga/luvina/blob/master/luvina/datasets/short_answer_grading.py
'''
class ReadDataSet_2442:

    def readFile(self, filename):


        with codecs.open(filename, 'rb', encoding="utf-8") as data_file:

            texts = []
            data_ids = []
            for line in data_file:
                if line[3] == ' ':
                    data_id = line[:3]
                    text = line[4:]
                elif line[4] == ' ':
                    data_id = line[:4]
                    text = line[5:]
                elif line[5] == ' ':
                    data_id = line[:5]
                    text = line[6:]
                else:
                    raise NotImplementedError('Space value not found')
                data_ids.append(data_id)
                texts.append(text)
            data_frame = pd.DataFrame({'id': data_ids, 'text': texts})
        
            return data_frame



    def getStringData(self, path = 'rnd_nltk/sample_data_short/data/raw/'):


        questions_file = path + 'questions'
        teacher_answers_filename = path + 'answers'
        student_answers_filename = path + 'all'
        student_answers = self.readFile(student_answers_filename)

        teacher_answers = self.readFile(teacher_answers_filename)
        questions = self.readFile(questions_file)
        
        

        return questions, teacher_answers, student_answers


    def getScores(self, path = 'rnd_nltk/sample_data_short/data/scores/'):


        score_paths = glob.glob(path + '*')
        scores = dict()
        count = 0
        for scores_path in score_paths:
            score_files = glob.glob(scores_path + '/*')
            question_scores = []
            #it loads score of directory "me", "ave" and "other"
            #so far every student answer there are three graders
            for score_file in score_files:
                file_scores = []
                _score_file = open(score_file, 'r')
                for line in _score_file:
                    file_scores.append(float(line))
                    count += 1
                question_scores.append(file_scores)

            scores_key = basename(scores_path) #name of file (1.1, 1.2, etc)
            scores[scores_key] = question_scores

        return scores

    def convertToDict(self, string_data):

        data = dict()
        #convert string_data(pandas_frame) values to dictionary

        for arg, key in enumerate(string_data.id.tolist()):
            data[key] = string_data.text.iloc[arg]

        return data


    def readData(self):
        
        #student answers = 2442
        #question, teacher answers and student asnwers are pandas
        questions, teacher_answers, student_answers = self.getStringData()

        # print "student answers ", student_answers[student_answers.id == '9.7']
        scores = self.getScores()  #for every answer there are 3 scores
        print len(scores['1.1'])
        # print "scores ", scores["1.1"][0] #each answer has around 87 scores
        teacher_answers = self.convertToDict(teacher_answers) # 87 key with ans
        questions = self.convertToDict(questions) #87 keys
        # print "question ", questions
        # print "teacher answers ", teacher_answers

        teacher_answers_list = []
        student_answers_list = []
        questions_list = []
        scores_list = [] # size 206676
        keys_list = [] #question numbers total size 206676

        for key in student_answers.id.unique().tolist(): 

            #this loops run for 2442 answers
            masked_student_answers = student_answers[student_answers.id == key]
            # print masked_student_answers
            # print "masked stu ans text len ", len(masked_student_answers.text) # 29, 30
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


    def normalizeData(self, data):

        #last assignments use 10 scale instead of 5
        # data.iloc[5616:5676,2] = data.iloc[5616:5676 ,2] / 2.0 #11.1 (me and other)
        # data.iloc[5706:5766, 2] = data.iloc[5706:5766, 2] / 2.0 #11.2 (me and other)
        # data.iloc[5796:5856, 2] = data.iloc[5796:5856, 2] / 2.0 #11.3 (me and other)
        # data.iloc[5886:5946, 2] = data.iloc[5886:5946, 2] / 2.0 #11.4 (me and other)
        # data.iloc[5976:6036, 2] = data.iloc[5976:6036, 2] / 2.0 #11.5 (me and other)
        # data.iloc[6066:6126, 2] = data.iloc[6066:6126, 2] / 2.0  #11.6 (me and other)
        # data.iloc[6156:6216, 2] = data.iloc[6156:6216, 2] / 2.0 #11.7 (me and other)
        # data.iloc[6246:6306, 2] = data.iloc[6246:6306, 2] / 2.0 #11.8 (me and other)
        # data.iloc[6336:6396, 2] = data.iloc[6336:6396, 2] / 2.0 #11.9 (me and other)
        # data.iloc[6426:6486, 2] = data.iloc[6426:6486, 2] / 2.0 #11.10 (me and other)
        # data.iloc[6514:6570, 2] = data.iloc[6514:6570, 2] / 2.0 #12.1 (me and other)
        # data.iloc[6598:6654, 2] = data.iloc[6598:6654, 2] / 2.0 #12.2 (me and other)
        # data.iloc[6682:6738, 2] =  data.iloc[6682:6738, 2] / 2.0 #12.3 (me and other)
        # data.iloc[6766:6822, 2] = data.iloc[6766:6822, 2] / 2.0 #12.4 (me and other)
        # data.iloc[6850:6906, 2] = data.iloc[6850:6906, 2] / 2.0 #12.5 (me and other)
        # data.iloc[6934:6990, 2] = data.iloc[6934:6990, 2] / 2.0 #12.6 (me and other)
        # data.iloc[7018:7074, 2] = data.iloc[7018:7074, 2] / 2.0 #12.7(me and other)
        # data.iloc[7102:7158, 2] = data.iloc[7102:7158, 2] / 2.0 #12.8(me and other)
        # data.iloc[7186:7242, 2] = data.iloc[7186:7242, 2] / 2.0 #12.9(me and other)
        # data.iloc[7270:7326, 2] = data.iloc[7270:7326, 2] / 2.0 #12.10(me and other)

        data.iloc[:, 2] = data.iloc[:, 2] / 5.0

        return data

    def normalizeMrc(self, data):

        data.iloc[:, 2] = data.iloc[:, 2] / 2.0

        return data


    def splitData(self, data, validation_split):

        train_split = 1 - validation_split

        test_set, train_set = [], []

        for data_id in data.id.unique():

            masked_id_data = data[data.id == data_id]
            unique_student_answers = masked_id_data.student.unique()
            train_size = int(train_split * len(unique_student_answers))
            unique_student_train = unique_student_answers[:train_size]
            unique_student_val = unique_student_answers[train_size:]
            for sentence in unique_student_train:
                train_set.append(
                        masked_id_data[masked_id_data.student == sentence])
            for sentence in unique_student_val:
                test_set.append(
            masked_id_data[masked_id_data.student == sentence])

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
        # print data
        print "inside 2442"

        data = self.normalizeData(data)

        training_set, testing_set = self.splitData(data, validation_split)


        train_data = self.preProcessData(training_set)
        test_data = self.preProcessData(testing_set)
        
        train_data = self._encodeData(train_data)
        test_data = self._encodeData(test_data)

        print len(train_data[0]['teacher_input'])
        print len(test_data[0]['teacher_input'])

        # print len(training_set['student'])
        # print len(testing_set['student'])

        return train_data, test_data


# if __name__ == '__main__':
    
#   rData = ReadDataSet_2442()
#   train, test = rData.loadData(0.2)
  # data = rData.readData()
  # data = rData.normalizeData(data)
  # print data.iloc[:,2]
