import nltk
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from .config import *
import re

class TextProcessing:


	def __init__(self):
		
		# print "Inside ntlk util"
		self.constituent_parse_tree = StanfordParser()
		self.stanford_dependency = StanfordDependencyParser()
		self.lemma = WordNetLemmatizer()
		self.home = '/home/ramesh/Documents/mas_course/second_semester/rnd/rnd_submission_cd'
		self.ner = StanfordNERTagger(self.home + '/stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz',self.home + '/stanford-ner-2017-06-09/stanford-ner.jar')
		self.pos_tag = StanfordPOSTagger(self.home + '/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger',self.home + '/stanford-postagger-2017-06-09/stanford-postagger-3.8.0.jar')
		self.CharacterOffsetEnd = 0 
		self.CharacterOffsetBegin = 0
		self.contractions = {"'nt":"not", "'ll": " will", "'re":"are", "'ve":"have", "'m":"am"}
		

	'''
	Input: sentence
	Returns: 
	'''


	def parser(self,sentence):


		# self.parseResult = {'parseTree':[], 'text':[], 'dependencies':[],'words':[] }
		self.parseResult = {'text':[], 'dependencies':[],'words':[] }

		# sentence = re.sub(r'\..', '.', sentence)

		parseText, sentences = self.getParseText(sentence)
		# print "sentences ", sentences
		# if source/target sent consist of 1 sentence 
		if len(sentences) == 1:
			return parseText
		
		wordOffSet = 0 # offset is number of words in first sentence 

		# if source/target sentence has more than 1 sentence

		for i in xrange(len(parseText['text'])):
			if i > 0:

				for j in xrange(len(parseText['dependencies'][i])):
					# [root, Root-0, dead-4]
					for k in xrange(1,3):
						tokens = parseText['dependencies'][i][j][k].split('-')

						if tokens[0] == 'Root':
							newWordIndex = 0

						else:
							if not tokens[len(tokens)-1].isdigit():
								continue 

							newWordIndex = int(tokens[len(tokens)-1]) + wordOffSet

						if len(tokens) == 2:
							parseText['dependencies'][i][j][k] = tokens[0] + '-'

							#original one
							# parseText['dependencies'][i][j][k] = tokens[0]+ '-' + str(newWordIndex)
												
						else:
							w = ''
							for l in xrange(len(tokens)-1):
								w += tokens[l]
								if l<len(tokens)-2:
									w += '-'

							parseText['dependencies'][i][j][k] = w + '-'
							#original one
							# parseText['dependencies'][i][j][k] = w + '-' + str(newWordIndex)

			wordOffSet += len(parseText['words'][i])


		return parseText


	'''
	Using Stanford POS Tagger
	Input: parserResult 
	Returns: [[charBegin,charEnd], wordIndex(starts from 1), word, word_POS]] 
	'''


	def combine_lemmaAndPosTags(self,parserResult):

		res = []
		
		wordIndex = 1
		for i in xrange(len(parserResult['words'])):
			
			for j in xrange(len(parserResult['words'][i])):
				
				tag = [[parserResult['words'][i][j][1]['CharacterOffsetBegin'], \
					parserResult['words'][i][j][1]['CharacterOffsetEnd']], \
					wordIndex,parserResult['words'][i][j][0], \
					parserResult['words'][i][j][1]['Lemma'], \
						parserResult['words'][i][j][1]['PartOfSpeech'] ]
				wordIndex += 1
				res.append(tag)

		return res


	'''
	Input: parserResult
	Returns: ([charOffsetBegin,charOffsetEnd], wordindex,word, NER ])
	'''


	def nerWordAnnotator(self,parserResult):

		res = []
		
		wordIndex = 1
		for i in xrange(len(parserResult['words'])):
			
			for j in xrange(len(parserResult['words'][i])):
				
				tag = [ [parserResult['words'][i][j][1]['CharacterOffsetBegin'], parserResult['words'][i][j][1]['CharacterOffsetEnd']], wordIndex,parserResult['words'][i][j][0] ,parserResult['words'][i][j][1]['NamedEntityTag'] ]
				# print "tag ", tag
				wordIndex += 1
				# if there is valid named entity then add in list
				if tag[3] != 'O':

					res.append(tag)

		return res


	'''
	Input : ParserResult
	Returns : list containing NamedEntites
	1. Group words in same list if they share same NE (Location), 
    2. Save other words in list that have any entity
	'''


	def get_ner(self,parserResult):


		nerWordAnnotations = self.nerWordAnnotator(parserResult) #[[ [charbegin,charEnd], wordIndex, word, NE ]]
		namedEntities = []
		currentWord = []
		currentCharacterOffSets = []
		currentWordOffSets = []

		for i in xrange(len(nerWordAnnotations)):

			if i == 0:

				currentWord.append(nerWordAnnotations[i][2]) # word having NE
				currentCharacterOffSets.append(nerWordAnnotations[i][0]) # [begin,end]
				currentWordOffSets.append(nerWordAnnotations[i][1]) # Word Index
				# if there is only one ner Word tag
				if (len(nerWordAnnotations) == 1):
					namedEntities.append([ currentCharacterOffSets, currentWordOffSets, \
						currentWord, nerWordAnnotations[i-1][3] ])
					# print "named Entities ", namedEntities
					break 
				continue
			# if consecutive tags have same NER Tag, save them in one list
			if nerWordAnnotations[i][3] == nerWordAnnotations[i-1][3] and \
					nerWordAnnotations[i][1] == nerWordAnnotations[i-1][1] + 1:
				
				currentWord.append(nerWordAnnotations[i][2]) # word having NE
				currentCharacterOffSets.append(nerWordAnnotations[i][0]) # [begin,end]
				currentWordOffSets.append(nerWordAnnotations[i][1]) # Word Index

				if i == (len(nerWordAnnotations) - 1):
					namedEntities.append([ currentCharacterOffSets, \
						currentWordOffSets, currentWord, nerWordAnnotations[i][3] ])
			# if consecutive tags do not match
			else:

				namedEntities.append([ currentCharacterOffSets, \
						currentWordOffSets, currentWord, nerWordAnnotations[i-1][3] ])
				currentWord = [nerWordAnnotations[i][2]]
				# remove everything from currentCharacterOffSets and currentWordOffSets
				currentCharacterOffSets = []
				currentWordOffSets = []
				# add charac offsets and currentWordOffSets of current word
				currentCharacterOffSets.append(nerWordAnnotations[i][0])
				currentWordOffSets.append(nerWordAnnotations[i][1])

				# if it is last iteration then update named Entities
				if i == len(nerWordAnnotations)-1:
					namedEntities.append([ currentCharacterOffSets, currentWordOffSets, \
							currentWord, nerWordAnnotations[i][3] ])
		#sort out according to len of characters in ascending order
		namedEntities = sorted(namedEntities, key=len)

		return namedEntities


	'''
	Input: Word(Word whose NE is not found), NE(word already have NE Tag) 
	Returns: Boolean; True if word is acronym
					False if word is not acronym
	'''


	def is_Acronym(self,word,NE):


		queryWord = word.replace('.','')
		# If all words of queryWord is not capital or length of word != 
				#length of NE(word already have NE Tag) or 
		   #  if word is 'a' or 'i' 
		if not queryWord.isupper() or len(queryWord) != len(NE) or queryWord.lower() in ['a', 'i']:
			return False

		acronym = True

		#we run for loop till length of query word(i.e 3)(if word is 'UAE')
		#Compare 1st letter(U) of query word with first letter of first element in named entity(U = U(united))
		# again we take second letter of canonical word (A) with second element in named entity(Arab)
		# and so on 
		for i in xrange(len(queryWord)):
			# print "queryword[i], NE ", queryWord, NE
			if queryWord[i] != NE[i][0]:
				acronym = False
				break

		return acronym


	'''
	Input: sentence
	Returns: parse(	{ParseTree, text, Dependencies, 
	  'word : [] NamedEntityTag, CharacterOffsetEnd, 
	  		CharacterOffsetBegin, PartOfSpeech, Lemma}']}) 
	  		sentence and
	'''


	def getParseText(self,sentence):

		self.count = 0
		self.length_of_sentence = [] # stores length of each sentence
		
		sentence = re.sub(r'([a-z]\.)([\d])', r'\1 \2', sentence)
		sentence = re.sub(r'(\)\.)([\d])', r'\1 \2', sentence)
		sentence = re.sub(r'([\d]\.)([\d])', r'\1 \2', sentence)
		sentence = re.sub(r'([a-z]\.)([A-Z])', r'\1 \2', sentence)
		sentence = re.sub(r'(\.)([A-Z]|[a-z])', r'\1 \2', sentence)
		sentence = re.sub(r'([*]|[+]|[-]|[=])([A-Z]|[a-z])', r'\1 \2', sentence)
		sentence = re.sub(r'([A-Z]|[a-z])([*]|[+]|[-]|[=])', r'\1 \2', sentence)
		sentence = re.sub(r'([*]|[+]|[-]|[=])([\d])', r'\1 \2', sentence)
		sentence = re.sub(r'([\d])([*]|[+]|[-]|[=])', r'\1 \2', sentence)

		if '[' in sentence:
			sentence = sentence.replace('[', ' [ ')

		if ']' in sentence:
			sentence = sentence.replace(']', ' ] ')

		if '/' in sentence:
			sentence = sentence.replace('/' , ' / ')

		if '//' in sentence:
			sentence = sentence.replace('//' , ' // ')

		if '{' in sentence:
			# print "came {"
			sentence = sentence.replace('{', ' { ')

		if '}' in sentence:
			# print "came }"
			sentence = sentence.replace('}', ' } ')

		if '(' in sentence:
			sentence = sentence.replace('(', ' ( ')

		if ')' in sentence:
			sentence = sentence.replace(')', ' ) ')

		if '$' in sentence:

			sentence = sentence.replace('$','')

		if '\\' in sentence:
			sentence = sentence.replace('\\',' ')

		if '|' in sentence:
			sentence = sentence.replace('|',' ')

		if 'times' in sentence:
			sentence = sentence.replace('times','x')

		if 'lambda' in sentence:
			sentence = sentence.replace('lambda', ' lambda ')



		tokenized_sentence = sent_tokenize(sentence)
		# print "len of tokenized ",len(tokenized_sentence)
		if (len(tokenized_sentence) == 1):
			self.count += 1
			for i in tokenized_sentence:
				parse = self.getCombineWordsParam(i)
		else:
			tmp = 0
			for i in tokenized_sentence:
				self.count += 1
				parse = self.getCombineWordsParam(i)
				s = len(i) + tmp
				self.length_of_sentence.append(s)
				tmp = s

		return parse,tokenized_sentence
		

	'''
	Input: sentences
    Return: constituency tree that represents relations between sub-phrases in sentences
    Not using for ASAG
	'''


	def getConstituencyTree(self, sentence):
		
		sentence = sent_tokenize(sentence)
		constituency_parser = self.constituent_parse_tree.raw_parse_sents(sentence)
		for parser in constituency_parser:
			for sent in parser:
				tree = str(sent)
		parse_string = ' '.join(str(tree).split()) 
        
		return parse_string


	'''
	Input: sentence
	returns: relation between words with their index
	'''	


	def getDependencies(self, sentence):

		#if first letter of sentence is '-', take rest sentence except hyphen

		if '#' in sentence:
			sentence = sentence.replace('#','')

 
		dependency_tree = []
		dependency_parser = StanfordDependencyParser().raw_parse(sentence)
		token = word_tokenize(sentence)
		parsetree = list(StanfordDependencyParser().raw_parse(sentence))[0]
		# Find root(head) of the sentence 
		for k in parsetree.nodes.values():
			# print "k ", k
			if k["head"] == 0:

				dependency_tree.append([str(k["rel"]), "Root-", str(k["word"] + "-") 
					 ])	    	

		# Find relation between words in sentences
		for dep in dependency_parser:
			# print "dep ", dep.triples()
			for triple in dep.triples():
				
				dependency_tree.append([str(triple[1]),str(triple[0][0]) + "-" ,\
							 str(triple[2][0]) + "-"])


		return dependency_tree


	'''
	Input: sentence, word(of which offset to determine)
	Return: [CharacterOffsetEnd,CharacterOffsetBegin] for each word
	'''


	def getCharOffSet(self,sentence, word):

		CharacterOffsetBegin = sentence.find(word)
		CharacterOffsetEnd = CharacterOffsetBegin + len(word)
		
		return [CharacterOffsetEnd,CharacterOffsetBegin]


	'''
	Input: sentence
	Returns: dictionary: 
	{ParseTree, text, Dependencies, 
	  #'word : [] NamedEntityTag, CharacterOffsetEnd, CharacterOffsetBegin, PartOfSpeech, Lemma}']}
	'''


	def getCombineWordsParam(self, sentence):
		

		# print " tokenized sentence in nltkUtil", sentence

		if sentence[0] == '-':
			sentence = sentence.split('-', 1)[1]

		

		words_list = [] 
		tokenized_words = word_tokenize(sentence)
		# print "tokenized words ", tokenized_words
		sentence = []
		#expand contractions 
		for i in tokenized_words:
			if i in self.contractions:
				sentence.append(self.contractions[i])
			else:
				sentence.append(i)
		sentence = " ".join(sentence)
		
		tokenized_words = word_tokenize(sentence)

		posTag = self.pos_tag.tag(tokenized_words)
		# print "pos Tag ", posTag
		ner = self.ner.tag(tokenized_words)
		# print "ner ", ner
		# if source sentence/target sentence has one sentence
		if (self.count == 1):
			for i in xrange(len(tokenized_words)):
				word_lemma = str()
				word = tokenized_words[i]
				name_entity = ner[i]
				word_posTag = posTag[i][-1]  # access tuple [(United, NNP),..]
				# print "word and pos tag ", word, word_posTag[0]	
				#wordNet lemmatizer needs pos tag with words else it considers noun
				if (word_posTag[0] == 'V'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.VERB)

				elif (word_posTag[0] == 'J'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.ADJ)

				elif (word_posTag[0:1] == 'RB'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.ADV)

				else:
					if (word == 'I'):
						# doing this because stanford lemmatize of 'I' is not present in stopwords
						word_lemma = self.lemma.lemmatize(word)
					else:
						word_lemma = self.lemma.lemmatize(word.lower())

				self.CharacterOffsetEnd, self.CharacterOffsetBegin = self.getCharOffSet(sentence,word)
				words_list.append([word, {"NamedEntityTag" : str(name_entity[1]),
					"CharacterOffsetEnd" : str(self.CharacterOffsetEnd), "CharacterOffsetBegin" : str(self.CharacterOffsetBegin) 
					,"PartOfSpeech" : str(word_posTag) , "Lemma" : str(word_lemma)}])

			# self.parseResult['parseTree'] = [self.getConstituencyTree(sentence)]
			self.parseResult['text'] = [sentence]
			self.parseResult['dependencies'] = [self.getDependencies(sentence)]
			self.parseResult['words'] = [words_list]

		else:
			for i in xrange(len(tokenized_words)):
				word = tokenized_words[i]
				name_entity = ner[i] 
				word_posTag = posTag[i][-1]

				if (word_posTag[0] == 'V'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.VERB)

				elif (word_posTag[0] == 'J'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.ADJ)

				elif (word_posTag[0:1] == 'RB'):
					word_lemma = self.lemma.lemmatize(word.lower(), wordnet.ADV)

				else:
					if (word == 'I'):
						# doing this because stanford lemmatize of 'I' is not present in stopwords
						word_lemma = self.lemma.lemmatize(word)
					else:
						word_lemma = self.lemma.lemmatize(word.lower())

				end, begin = self.getCharOffSet(sentence,word)
				end = end + self.length_of_sentence[self.count-2] + 1
				begin = begin + self.length_of_sentence[self.count-2] + 1	
				words_list.append([word, {"NamedEntityTag" : str(name_entity[1]),
					"CharacterOffsetEnd" : str(end), "CharacterOffsetBegin" : str(begin) 
					,"PartOfSpeech" : str(word_posTag) , "Lemma" : str(word_lemma)}])
				
			self.parseResult['text'].append(sentence)
			self.parseResult['dependencies'].append(self.getDependencies(sentence))
			self.parseResult['words'].append(words_list)

		return self.parseResult
