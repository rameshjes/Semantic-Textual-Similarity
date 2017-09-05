
# coding: utf-8

# # Levenshtein Distance in NLTK
# 
# It computes minimum edit distance between two strings by performing three operations:
# 1. Substitution
# 2. Insertion
# 3. Deletion
# 
# It is mainly used for spelling correction, I have tried to use as spelling corrector, but it does not performs always in optimal way
# 
# 
# # PyEnchant Library 
# 
# It is spell checking library for python, it has built-in english dictionary and functions to check the spells in the sentences 
# 
# 
# # Spell Correction Using Ngram, Jaccard Coefficient and Edit Distance
# 
# #### Steps performed:
# 
# 1. Find Misspelled words
# 2. Check Suggested Words
# 3. Filter suggested words which are different within some distance using edit distance
# 4. Compute Ngram of misspelled word and each suggested word
# 5. Compute Jaccard coefficient of misspelled word and each suggested word
# 6. Replace suggested word with maximum jaccard coefficient

# In[1]:

from __future__ import division
import numpy as np
import nltk
from nltk.metrics import *
from nltk.util import ngrams
import enchant  # spell checker library pyenchant
from enchant.checker import SpellChecker
from nltk.stem import PorterStemmer
from nltk.corpus import words


# In[2]:

spell_dictionary = enchant.Dict('en')


# In[3]:

class string_similarity:
    
    def __init__(self,dictionary):
        
        self.dictionary = dictionary
        self.check = SpellChecker("en_US")
        self.stemmer = PorterStemmer()
        
    '''
    suggest words according to input word
    '''    
    def suggest_words(self,word):
        return self.check.suggest(word)
    
    '''
    Compute minimum edit distance between two strings
    Operations performed: deletion, insertion and substitution
       
    '''
    def levenshtein_distance(self,s1,s2):
        
        # nltk already have implemeted function
        
        distance_btw_strings = edit_distance(s1,s2)
        
        return distance_btw_strings
    
    '''
    Given word and value of n(denotes how many grams of text)
    n = 1 means unigram
    n = 2 means bigram and so on
    '''
    def ngram(self,word,n):
        
        grams = list(ngrams(word,n))
    
        return grams
    
    '''
    Takes sentence as input, identifies incorrect word 
    according to dictionary provided by pyenchant library
    returns correct word with least distance using levenshtein distance, but sometimes this is not optimal too
    '''
    
    '''
    Takes input as sentence and returns list of misspelled words
    '''
    
    def check_mistakes_in_sentence(self,sentence):
        
        misspelled_words = []
        
        self.check.set_text(sentence)
        
        for err in self.check:
            misspelled_words.append(err.word)
            
        if len(misspelled_words) == 0:
            print " No mistakes found"
        return misspelled_words
    
    '''
    Jaccard correlation coefficient computes
    similarity between two terms
    '''
    
    def jaccard(self,a,b):

        union = list(set(a+b))
        intersection = list(set(a) - (set(a)-set(b)))
        jaccard_coeff = float(len(intersection))/len(union)
        return jaccard_coeff
    
    '''
    Take incorrect word as input and 
    returns closely suggested words
    '''
    
    def minimumEditDistance_spell_corrector(self,word):
        
        max_distance = 2
        if (self.dictionary.check(word)):
            return word
        suggested_words = self.suggest_words(word)
        
        num_modified_characters = []
        
        if suggested_words != 0:
            
            for sug_words in suggested_words:
                num_modified_characters.append(self.levenshtein_distance(word,sug_words))
                
            minimum_edit_distance = min(num_modified_characters)
            best_arg = num_modified_characters.index(minimum_edit_distance)
            if max_distance > minimum_edit_distance:
                best_suggestion = suggested_words[best_arg]
                return best_suggestion
            else:
                return word
        else:
            return word
        
    '''
    takes word as input and return closely corrected word
    '''
    
    def ngram_spell_corrector(self,word):
        
        max_distance = 2
        if (self.dictionary.check(word)):
            return word
        suggested_words = self.suggest_words(word)
        
        num_modified_characters = []
       
        max_jaccard = []
        list_of_sug_words = []
        if suggested_words != 0:
            
            word_ngrams = self.ngram(word,2)

            for sug_words in suggested_words:

                if (self.levenshtein_distance(word,sug_words)) < 3 :

                    sug_ngrams = self.ngram(sug_words,2)
                    jac = self.jaccard(word_ngrams,sug_ngrams)
                    max_jaccard.append(jac)
                    list_of_sug_words.append(sug_words)
            highest_jaccard = max(max_jaccard)
            best_arg = max_jaccard.index(highest_jaccard)
            word = list_of_sug_words[best_arg]
            return word
        else:
            return word


# # Spell Correction using Levenshtein Distance

# In[4]:

sentence1 = "I was abilites abd born in oovember Massachussets  "
word_tokenize = nltk.word_tokenize(sentence1)
obj = string_similarity(spell_dictionary)
correct_sentence = []
for misspelled_words in word_tokenize:
    correct_sentence.append(obj.minimumEditDistance_spell_corrector(misspelled_words))
print correct_sentence


# # Spell Correction Using Ngrams, Jaccard Coefficient and Edit Distance

# In[5]:

sentence = "Always abilites rememer oovember and decemer Massachussets "
word_tokenize = nltk.word_tokenize(sentence)
obj = string_similarity(spell_dictionary)
correct_sentence = []
for misspelled_words in word_tokenize:
    correct_sentence.append(obj.ngram_spell_corrector(misspelled_words))
print correct_sentence


# # Load Data set that contain misspelled and corrected words

# In[6]:

def load_misspelled_dataset(dataset):
    words_dictionary = dict()
    for i in range(len(dataset)):
        words_dictionary[dataset[i][0]] = dataset[i][2] 
        
    return words_dictionary


# In[7]:

load_dataset = np.loadtxt('dataset/dataset_misspelled.txt',dtype='str')


# # Performance of Spell Corrector using Ngrams on Dataset

# In[8]:

def check_misspelledWords_ngramCorrector(dataset):
    number_of_corrected_words = 0
    words = []
    dictionary_misspelled_and_corrected_words = load_misspelled_dataset(load_dataset)
    for i in range(len(dictionary_misspelled_and_corrected_words)):
        corrected_word = obj.ngram_spell_corrector(dataset[i][0])
        if corrected_word == dataset[i][2]:
            number_of_corrected_words += 1
    print "============================================================================================"
    print "Total number of misspelled words in database", len(dictionary_misspelled_and_corrected_words) 
    print "Total number of corrected words",number_of_corrected_words
    print "Total percentage ", (number_of_corrected_words/len(dictionary_misspelled_and_corrected_words)) * 100
    print "============================================================================================"
check_misspelledWords_ngramCorrector(load_dataset)


# # Performance of Spell Corrector using Minimum Edit Distance(MED) on Dataset

# In[9]:

def check_misspelledWords_medCorrector(dataset):
    number_of_corrected_words = 0
    words = []
    dictionary_misspelled_and_corrected_words = load_misspelled_dataset(load_dataset)
    for i in range(len(dictionary_misspelled_and_corrected_words)):
        corrected_word = obj.minimumEditDistance_spell_corrector(dataset[i][0])
        if corrected_word == dataset[i][2]:
            number_of_corrected_words += 1
    print "============================================================================================"
    print "Total number of misspelled words in database", len(dictionary_misspelled_and_corrected_words) 
    print "Total number of corrected words",number_of_corrected_words
    print "Total percentage ", (number_of_corrected_words/len(dictionary_misspelled_and_corrected_words)) * 100
    print "============================================================================================"
check_misspelledWords_medCorrector(load_dataset)


# In[ ]:



