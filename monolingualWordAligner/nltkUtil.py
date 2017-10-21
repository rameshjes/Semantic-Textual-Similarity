import nltk
from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer

class Text_processing:


	def __init__(self):
		
		self.constituent_parse_tree = StanfordParser()
		self.dependency_tree = StanfordDependencyParser()
		self.lemma = WordNetLemmatizer()
		self.home = '/home/ramesh'
		self.ner = StanfordNERTagger(self.home + '/stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz',self.home + '/stanford-ner-2017-06-09/stanford-ner.jar')
		self.pos_tag = StanfordPOSTagger(self.home + '/stanford-postagger-2017-06-09/models/english-bidirectional-distsim.tagger',self.home + '/stanford-postagger-2017-06-09/stanford-postagger-3.8.0.jar')
		# self.parseResult = {'parseTree':[], 'text':[], 'dependencies':[],'words':[] }
		self.CharacterOffsetEnd = 0 
		self.CharacterOffsetBegin = 0
		self.count = 0 #count sentence number in source/target response

	'''
	Input: sentence
	Returns: 
	'''
	def parser(self,sentence):


		self.parseResult = {'parseTree':[], 'text':[], 'dependencies':[],'words':[] }
		parseText, sentences = self.get_parseText(sentence)
		
		# if source/target sent consist of 1 sentence 
		if len(sentences) == 1:
			return parseText
		
		wordOffSet = 0 # offset is number of words in first sentence 

		# if source/target sentence has more than 1 sentence

		for i in xrange(len(parseText['text'])):

			if (i == 0):
				wordOffSet += len(parseText['words'][i])
				
			else:
				# modify word numbers in dependencies
				for j in xrange(len(parseText['dependencies'][i])):
					# [root, Root-0, dead-4]
					for k in xrange(1,3):
						tokens = parseText['dependencies'][i][j][k].split('-')
						# [Root, 0]
						if tokens[0] == 'Root':
							newWordIndex = 0

						else:
							if not tokens[len(tokens)-1].isdigit():
								continue 

							newWordIndex = int(tokens[len(tokens)-1]) + wordOffSet

						if len(tokens) == 2:

							 parseText['dependencies'][i][j][k] = tokens[0]+ '-' + str(newWordIndex)
							 # print "parse Text ", parseText['dependencies'][i][j][k]
												
						else:
							w = ''
							for l in xrange(len(tokens)-1):
								w += tokens[l]
								if l<len(tokens)-2:
									w += '-'

							parseText['dependencies'][i][j][k] = w + '-' + str(newWordIndex)

		return parseText


	'''
	Input: parserResult 
	Returns: [[charBegin,charEnd], wordIndex(starts from 1), word, word_lemma]] 
	'''


	def get_lemma(self,parserResult):

		res = []
		
		wordIndex = 1
		for i in xrange(len(parserResult['words'])):
			
			for j in xrange(len(parserResult['words'][i])):
				
				tag = [ [parserResult['words'][i][j][1]['CharacterOffsetBegin'], parserResult['words'][i][j][1]['CharacterOffsetEnd']], wordIndex,parserResult['words'][i][j][0] ,parserResult['words'][i][j][1]['Lemma'] ]
				wordIndex += 1
				res.append(tag)

		return res



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
				
				tag = [ [parserResult['words'][i][j][1]['CharacterOffsetBegin'], parserResult['words'][i][j][1]['CharacterOffsetEnd']], wordIndex,parserResult['words'][i][j][0] ,parserResult['words'][i][j][1]['Lemma'] ,parserResult['words'][i][j][1]['PartOfSpeech'] ]
				wordIndex += 1
				res.append(tag)

		return res



	def get_parseText(self,sentence):


		tokenized_sentence = sent_tokenize(sentence)
		self.count = 0
		if (len(tokenized_sentence) == 1):
			self.count += 1
			for i in tokenized_sentence:
				parse = self.get_combine_words_param(i)
		else:
			for i in tokenized_sentence:
				self.count += 1
				parse = self.get_combine_words_param(i)

		# self.total_sentences['sentences'].append(self.parseResult)

		return parse,tokenized_sentence
		

	'''
	Input: sentences
    Return: constituency tree that represents relations between sub-phrases in sentences
	'''


	def get_constituency_Tree(self,sentence):
		
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


	def get_dependencies(self,sentence):


		dependency_tree = []
		dependency_parser = self.dependency_tree.raw_parse(sentence)
		token = word_tokenize(sentence)
		parsetree = list(self.dependency_tree.raw_parse(sentence))[0]
		# Find root(head) of the sentence 
		for k in parsetree.nodes.values():
			if k["head"] == 0:
		
				dependency_tree.append([str(k["rel"]), "Root-" + str(k["head"]), str(k["word"]) 
					+ "-" + str(k["address"]) ])	    	
		# Find relation between words in sentence
		for dep in dependency_parser:
			for triple in dep.triples():
				index_word = token.index(triple[0][0]) + 1 # because index starts from 0 
				index2_word = token.index(triple[2][0]) + 1
				# dependency_tree.append([str(triple[1]) + "(" + str(triple[0][0]) + "-" + str(index_word) + "," + str(triple[2][0]) + "-" + str(index2_word) + ")"])
				dependency_tree.append([str(triple[1]),str(triple[0][0]) + "-" + str(index_word), str(triple[2][0]) + "-" + str(index2_word)])

		return dependency_tree


	'''
	Input: sentence
	Returns: ner tag
	'''


	def get_ner(self,sentence):

		# print "inside get ner"
		return self.ner.tag(sentence)

	'''
	Input: sentence, word(of which offset to determine)
	Return: [CharacterOffsetEnd,CharacterOffsetBegin] for each word
	'''


	def get_charOffset(self,sentence, word):

		CharacterOffsetBegin = []
		CharacterOffsetEnd = []
		CharacterOffsetBegin = sentence.find(word)
		CharacterOffsetEnd = CharacterOffsetBegin + len(word)
		
		return [CharacterOffsetEnd,CharacterOffsetBegin]

	'''
	Input: sentence
	Returns: dictionary: 
	{ParseTree, text, Dependencies, 
	  #'word : [] NamedEntityTag, CharacterOffsetEnd, CharacterOffsetBegin, PartOfSpeech, Lemma}']}
	'''

	def get_combine_words_param(self,sentence):
		
		words_in_each_sentence = []
		words_list = [] 
		tokenized_words = word_tokenize(sentence)
		posTag = self.pos_tag.tag(tokenized_words)
		ner = self.get_ner(tokenized_words)

		# if source sentence/target sentence has one sentence
		if (self.count == 1):
			for i in xrange(len(tokenized_words)):
				word = tokenized_words[i]
				name_entity = ner[i] 
				word_lemma = self.lemma.lemmatize(tokenized_words[i])
				self.CharacterOffsetEnd, self.CharacterOffsetBegin = self.get_charOffset(sentence,tokenized_words[i])
				word_posTag = posTag[i][-1]  # access tuple [(United, NNP),..]

				words_list.append([word, {"NamedEntityTag" : str(name_entity[1]),
					"CharacterOffsetEnd" : str(self.CharacterOffsetEnd), "CharacterOffsetBegin" : str(self.CharacterOffsetBegin) 
					,"PartOfSpeech" : str(word_posTag) , "Lemma" : str(word_lemma)}])

			self.parseResult['parseTree'] = [self.get_constituency_Tree(sentence)]
			self.parseResult['text'] = [sentence]
			self.parseResult['dependencies'] = [self.get_dependencies(sentence)]
			self.parseResult['words'] = [words_list]

		else:
			for i in xrange(len(tokenized_words)):
				word = tokenized_words[i]
				name_entity = ner[i] 
				word_lemma = self.lemma.lemmatize(tokenized_words[i])
				end, begin = self.get_charOffset(sentence,tokenized_words[i])
				end = end + self.CharacterOffsetEnd + 1
				begin = begin + self.CharacterOffsetEnd + 1
				word_posTag = posTag[i]

				words_list.append([word, {"NamedEntityTag" : str(name_entity[1]),
					"CharacterOffsetEnd" : str(end), "CharacterOffsetBegin" : str(begin) 
					,"PartOfSpeech" : str(word_posTag) , "Lemma" : str(word_lemma)}])
			self.parseResult['parseTree'].append(self.get_constituency_Tree(sentence))
			self.parseResult['text'].append(sentence)
			self.parseResult['dependencies'].append(self.get_dependencies(sentence))
			self.parseResult['words'].append(words_list)
			
		return self.parseResult   









		


