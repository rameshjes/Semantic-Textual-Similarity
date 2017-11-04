
from config import *
from Resources import *

class WordSimilarity:


	def __init__(self):

		self.ppdbSim = ppdbSim
		self.ppdbDict = ppdbDict
		self.stemmer = stemmer
		self.punctuations = punctuations
		self.load_paraphraseDatabase()



	'''
	Input: Paraphrase database
	Append tokens with similarity score(0.9)
	'''
	def load_paraphraseDatabase(self, FileName = 'Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'):

		file = open(FileName,'r')
		count = 0

		for line in file:
			if line == '\n':
				continue

			tokens = line.split()
			tokens[1] = tokens[1].strip()
			self.ppdbDict[(tokens[0], tokens[1])] = self.ppdbSim
			count += 1
		print count


	'''
	Input: Word1, word2
	Returns: True if word present in paraphrase database 
	'''	


	def checkWordPresentInDataBase(self, word1, word2):

		if (word1.lower(), word2.lower()) in ppdbDict:

			return True

		if (word1.lower(), word2.lower()) in ppdbDict:

			return True


	'''
	Input: word1, pos1, word2, pos2,
	Steps : 
		i. Check length of each word(word1,word2), and replace ('.','-',',') by space
		ii. If both words(word1, word2 are equal) then return true (1)
		iii. If both words have same stemma then return 1 
		iv. If both words are digiits and are not equal then return 0 
		v. Check if either of bothw ords are present in stopwords , then return 0
		vi. check if either of word is in punctuations then return 0
		vii. If both the words are present in PPDB then return then PPDBSim(similarity score)(0.9)

	Returns: similarity score between two words

	'''


	def computeWordSimilarityScore(self, word1, pos1, word2, pos2):

	    if len(word1) > 1:
	    	modifiedWord1 = word1.replace('.','')
	    	modifiedWord1 = word1.replace('-','')
	    	modifiedWord1 = word1.replace(',','')
	    else:
	    	modifiedWord1 = word1

	    if len(word2) > 1:
	    	modifiedWord2 = word2.replace('.','')
	    	modifiedWord2 = word2.replace('-','')
	    	modifiedWord2 = word2.replace(',','')
	    else:
	    	modifiedWord2 = word2

	    if modifiedWord1.lower() == modifiedWord2.lower():
	    	return 1

	    if self.stemmer.stem(word1).lower() == self.stemmer.stem(word2).lower():
	    	return 1

	    if modifiedWord1.isdigit() and modifiedWord2.isdigit() and modifiedWord1 != modifiedWord2:
	    	return 0
	    # digits mostly have 'cd' pos tag
	    if pos1.lower() == 'cd' and pos2.lower() == 'cd' and (not modifiedWord1.isdigit() \
	    			and not modifiedWord2.isdigit() and modifiedWord1 != modifiedWord2):
	    	return 0
	    # stopwords can be similar to only stopwords
	    if (word1.lower() in stopwords and word2.lower() not in stopwords) or \
	    		(word2.lower() in stopwords and word1.lower() not in stopwords):

	    	return 0 

	    #Punctuations can only be either identical or totally dissimilar
	    if word1 in punctuations or word2 in punctuations:
	    	return 0

	    #check words in database

	    if self.checkWordPresentInDataBase(word1.lower(), word2.lower()):
	    	return ppdbSim

	    else:
	    	return 0
