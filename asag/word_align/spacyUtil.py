from __future__ import unicode_literals 
import spacy
from spacy.lang.en import English
import string 
import nltk
from nltk.parse.stanford import StanfordDependencyParser
from spacy import displacy
import re 


nlp = spacy.load('en')

class Text_processing_spacy:

	def __init__(self):
		
		self.spacy_parser = nlp
		self.CharacterOffsetEnd = 0 
		self.CharacterOffsetBegin = 0

	'''
	Input: sentence
	Returns: 
	'''


	def parser(self,sentence):


		# self.parseResult = {'parseTree':[], 'text':[], 'dependencies':[],'words':[] }
		self.parseResult = {'text':[], 'dependencies':[],'words':[] }
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

							 parseText['dependencies'][i][j][k] = tokens[0]+ '-' 
												
						else:
							w = ''
							for l in xrange(len(tokens)-1):
								w += tokens[l]
								if l<len(tokens)-2:
									w += '-'

							parseText['dependencies'][i][j][k] = w + '-'

			wordOffSet += len(parseText['words'][i])

		return parseText



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
		
		sentence = self.spacy_parser(unicode(sentence))
		tokenized_sentence = [sent for sent in sentence.sents]
		# print "tokenized sentences ", tokenized_sentence
		# print "tokenized sentence ", tokenized_sentence
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

		return parse, tokenized_sentence


	'''
	Using Stanford POS Tagger
	Input: parserResult 
	Returns: [[charBegin,charEnd], wordIndex(starts from 1), lemma, word_POS]] 
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
	Input: sentence, tokenized words
	Returns: list of words having named entities
	'''

		
	def getNamedEntities(self, sentence, tokenized_words):


		## Not good way, of getting named entities according to number of tokenized words
		entities = {} #dictonary to get named entites

		named_entities = [] #final list containing NE for each word

		for ent in sentence.ents:
			entities[ent.text] = ent.label_

		# print "named entities ", entities
		new_dict = {}

		for word in (tokenized_words):

			for key in entities.keys():
				if  word in key:
					new_dict[word] = entities[key]
					
		for i in xrange(len(tokenized_words)):
			if tokenized_words[i] in new_dict:
				named_entities.append(new_dict[tokenized_words[i]])
			else:
				named_entities.append('O')

		return named_entities

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



	def getDependencies(self, sentence, tokenized_words):

		dependency_tree = []
		for token in sentence:

			#convert to string and add 1, as index starts from 0
			token_index = tokenized_words.index(str(token)) + 1 
			token_head_text_index = tokenized_words.index(str(token.head.text)) + 1

			#if text and head is same word, we replace its head by "root"
			#so that our output looks similar as of stanford parser
			if token.head.text ==token.text:
				dependency_tree.append(["root",  "ROOT-", token.text+"-"])
			
			else:
				dependency_tree.append([token.dep_,  token.head.text +"-",  \
								token.text + "-"])

		return dependency_tree



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


	def is_Acronym(self, word, NE):


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
	Input: sentence, word(of which offset to determine)
	Return: [CharacterOffsetEnd,CharacterOffsetBegin] for each word
	'''


	def getCharOffSet(self, sentence, word):

		# word containing '.' causes problem in counting
		sentence = str(sentence)
		CharacterOffsetBegin = sentence.find(word)
		CharacterOffsetEnd = CharacterOffsetBegin + len(word)
		
		return [CharacterOffsetEnd,CharacterOffsetBegin]



	def getCombineWordsParam(self, sentence):


		sentence = self.spacy_parser(unicode(sentence))
		words_list = []
		tokenized_words = [token.text for token in sentence]
		# print "tokenized words ", tokenized_words
		pos_tags = [token.pos_ for token in sentence]
		named_entities = self.getNamedEntities(sentence, tokenized_words)
		# print "named entities ", named_entities
		lemma = [token.lemma_ for token in sentence]
		# print "lemas ", lemma
		# print ""
		if (self.count == 1):

			for i in xrange(len(tokenized_words)):

				word = str(tokenized_words[i])
				ne = named_entities[i]
				pos_tag = pos_tags[i]
				word_lemma = lemma[i]

				self.CharacterOffsetEnd, self.CharacterOffsetBegin = self.getCharOffSet(sentence,word)

				words_list.append([word, {"NamedEntityTag" : str(ne),
						"CharacterOffsetEnd" : str(self.CharacterOffsetEnd), "CharacterOffsetBegin" : str(self.CharacterOffsetBegin) 
						,"PartOfSpeech" : str(pos_tag) , "Lemma" : str(word_lemma)}])
			self.parseResult['text'] = [sentence]
			self.parseResult['words'] = [words_list]
			self.parseResult['dependencies'] = [self.getDependencies(sentence, tokenized_words)]

		else:

			for i in xrange(len(tokenized_words)):

				word = str(tokenized_words[i])
				ne = named_entities[i]
				pos_tag = pos_tags[i]
				word_lemma = lemma[i]


				self.CharacterOffsetEnd, self.CharacterOffsetBegin = self.getCharOffSet(sentence, word)

				end, begin = self.getCharOffSet(sentence,word)
				end = end + self.length_of_sentence[self.count-2] + 1
				begin = begin + self.length_of_sentence[self.count-2] + 1

				words_list.append([word, {"NamedEntityTag" : str(ne),
						"CharacterOffsetEnd" : str(end), "CharacterOffsetBegin" : str(begin) 
						,"PartOfSpeech" : str(pos_tag) , "Lemma" : str(word_lemma)}])

			self.parseResult['text'].append(sentence)
			self.parseResult['words'].append(words_list)
			self.parseResult['dependencies'].append(self.getDependencies(sentence, tokenized_words))

		return self.parseResult
