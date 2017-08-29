
# coding: utf-8

# # Read Mohler data set 
# 
# source : http://web.eecs.umich.edu/~mihalcea/downloads.html#saga

# In[59]:

import numpy as np
import os
from collections import defaultdict
import glob


# In[60]:

# import string_similarity # another notebook name string similarity
# import text_normalization # notebook text normalization
# spell_dictionary = enchant.Dict('en')


# In[61]:

# object_string_similarity = string_similarity.string_similarity(spell_dictionary) # object of string similarity class
# object_text_normalization = text_normalization.text_normalization()


# In[62]:

class read_database():
    
    def __init__(self):
        
        self.questions_file = open('../data/raw/questions')
        self.answers_file = open('../data/raw/answers')
        self.database_questions = dict()
        self.database_answers = dict()
        
        self.students_files = sorted(glob.glob('../data/raw/*')) # 90 files
        # exlucding last three files because they contain models answer
        self.students_files = self.students_files[0:87] 
        self.scores = sorted(glob.glob('../data/scores/1.1/ave'))
        
    def file_preprocessing(self,file_lines):
        
        temp_database = dict()
        i = 0;
        for line in file_lines:
            i = i + 1
            temp = line.strip()
            number = temp[0:5]
            number = number.strip()
            text = temp[5:]
            temp_database[number] = text
#         print "number of lines in file", i
            
        return temp_database
  
        
    def read_question_file(self):
        
        read_file = self.questions_file.readlines()
        
        self.database_questions = self.file_preprocessing(read_file)        
        
        return self.database_questions
    
    # Read model answers file
    def read_answer_file(self):
        
        read_file = self.answers_file.readlines()
        
        self.database_answers = self.file_preprocessing(read_file)
            
        return self.database_answers
        
    '''
    Combine dictionary of model answers and questions
    Takes input question dictionary and answer dictionary 
    and returns combine dictionary 
    
    Example: combine_dict["1.1"] gives 1.1 question and answer
    '''    
    
    def combine_model_question_answer(self,question_database,answer_database):
        
        combine_dict = defaultdict(list)

        for d in (question_database, answer_database): 
            for key, value in d.iteritems():
                combine_dict[key].append(value)
                
        return combine_dict

    
    ''' 
    student id starts from 100 
    Returns all answers provided by each student
    '''
    
    def student_answers(self,question_database):
        
        combine_answers = defaultdict(list)
        print "question number 7.1", question_database["7.1"]
        for list_of_files in self.students_files:
#             print "file name: ", list_of_files
            open_file = open(list_of_files)
            read_file_lines = open_file.readlines()
            ID = 100 
            count = 0
            for line in read_file_lines:
                count += 1
                temp = line.strip()
                student_id = ID
                student_response = temp
                combine_answers[student_id].append(student_response)
#                 print "ID: ", ID
            
                ID = ID + 1
#             print "file opened", open_file
#             print "number of times loop exxecuted: ", count
#             print "combine answer dictionary: ", len(combine_answers)

#         print "count: ", count
        return  combine_answers
    
#     def average_scores(self):
        
#         combine_scores = defaultdict(list)
        
#         for list_of_files in self.scores:
#             open_file = open(list_of_files)
            
#             read_file_lines = open_file.readlines()
#             ID = 100
#             for line in read_file_lines:
#                 temp = line.strip()
#                 student_id = ID
#                 student_response = temp
#                 combine_scores[student_id].append(student_response)
#                 ID = ID + 1
                
#         return  combine_scores


# In[64]:

database = read_database()
question_database = database.read_question_file()
print question_database["1.1"]
# print "total number of questions ", len(question_database)
answer_database = database.read_answer_file()
# print answer_database
# print "total number of answers ", len(answer_database)
# print "Question and Expected Answer: "
combine_database  = database.combine_model_question_answer(question_database,answer_database)
# print "total number of questions and models answers", len(combine_database)

# model_question_answer = '10.4'
# print "Model Question Answer ", combine_database[model_question_answer]
# print "student Answer: "
student_answers = database.student_answers(question_database)
print student_answers[128]
# student_answers
# print "student ss ", student_answers
# print "total number of students", len(student_answers)
# print type(student_answers[105])
# student_answer_number = 10
# student_id = 101 # 100 denotes 1st student, 101 denotes 2nd student
# print "answer provided by student: ", student_answers[student_id][student_answer_number][4:]
# # print "Total number of answers provided by students are in database: ", 31*87
# object_text_normalization.lemmatizer(student_answers[student_id][student_answer_number][4:])
# scores = database.average_scores()
# print scores[101]


# 

# In[ ]:



