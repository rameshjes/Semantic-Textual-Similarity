
# coding: utf-8

# # Text Normalization 

# In[2]:

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import string 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer


# Here for stemming, Porter Stemmer algorithm is used .
# 
# Other available algorithm for stemming in NLTK is Snowball stemmer, Lancaster stemmers
# 
# The WordNet lemmatizer removes affixes only if the resulting word is in its dictionary

# In[6]:

class text_normalization:
    
    def __init__(self):
        self.punctuations = list(string.punctuation)
        self.stemmer = PorterStemmer()
        self.lemma = WordNetLemmatizer()
    '''
    This function takes text as input 
    and returns list of tokenized words(punctuations not included) 
    '''    
    def word_tokenizer(self,text):
        self.word_tokenize_list = word_tokenize(text)

        for word in self.word_tokenize_list:
            if word in self.punctuations:
                self.word_tokenize_list.remove(word)        
        return self.word_tokenize_list
    '''
    This function takes text as input 
    and returns list of tokenized sentences 
    '''    
    def sentence_tokenizer(self,sentence):
        self.sentence_tokenize_list = sent_tokenize(sentence)
        return self.sentence_tokenize_list
    
    '''
    This function takes tokenized sentence as input 
    and returns lemma of tokenized sentence 
    
    1. First sentences from text are tokenized
    2. Then, words from sentences are tokenized
    3. Lemmatizer of words is determined
    
    '''
    
    def lemmatizer(self, sentences):
        token_sent = self.sentence_tokenizer(sentences)
        token_word = [self.word_tokenizer(token_sent[i]) for i in range(len(token_sent))]

        for noOfSent in range(len(token_word)):
            stem = [(self.lemma.lemmatize((token_word[noOfSent][words]))) for words in range(len(token_word[noOfSent]))]
            stem = " ".join(stem)            
            print "tokenized sentence is: " + str(token_sent[noOfSent])
            print "lemma of this sentence is: " +  str(stem)
            print "tokenized words in lemmatizer sentence are: " + str(self.word_tokenizer(stem))
            print "========================================================================="
    '''
    This function takes tokenized sentence as input 
    and returns stemmer of tokenized sentence 
    
    1. First sentences from text are tokenized
    2. Then, words from sentences are tokenized
    3. Porter stemmer algorithm is applied on tokenized words
    
    '''       
    def porter_stemmer(self,sentence):
        token_sent = self.sentence_tokenizer(sentence)
        token_word = [self.word_tokenizer(token_sent[i]) for i in range(len(token_sent))]
        for no_of_sent in range(len(token_word)):
            stem = [(self.stemmer.stem((token_word[no_of_sent][words]))) for words in range(len(token_word[no_of_sent]))]
            stem = " ".join(stem)
            print "tokenized sentence is: " + str(token_sent[no_of_sent])
            print "stemmer of this sentence is: " +  str(stem)
            print "tokenized words in stemmer sentence are: " + str(self.word_tokenizer(stem))
            print "========================================================================="    


# # Porter Stemmer Algorithm

# In[7]:

text_normalizer = text_normalization()
# define any sentence
sentence = "This is first cats. Ph.d is very difficult to complete. My favourite colours are red, orange, green. Let's try to tokenize the sentences. how are you? I am doing good"
print "*** Output of porter stemmer algorithm ****"
print "==========================================="

text_normalizer.porter_stemmer(sentence)
print "============================================================================="


# # Lemmatizing

# In[12]:

print "*** Output of Lemmatizing ****"
print "==========================================="
text_normalizer.lemmatizer(sentence)


# In[ ]:




# In[ ]:



