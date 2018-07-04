import nltk 
from nltkUtil import *
from util import *
from config import *
from wordsim import *
from spacyUtil import *


class Aligner:

	def __init__(self, flag):


		if flag=='nltk':
			print "you are using word aligner using NLTK"
			self.text_nor = Text_processing()
		
		if flag=='spacy':

			print "you are using word aligner using Spacy"
			self.text_nor = Text_processing_spacy()
	

		self.util = Util()
		self.word_similarity = WordSimilarity()



	def align_sentences(self,sentence1,sentence2):


		print "please wait system is aliging words"
		sentence1ParseResult = self.text_nor.parser(sentence1)
		sentence2ParseResult = self.text_nor.parser(sentence2)

		sentence1LemmasAndPosTags = self.text_nor.combine_lemmaAndPosTags(sentence1ParseResult)
		sentence2LemmasAndPosTags = self.text_nor.combine_lemmaAndPosTags(sentence2ParseResult)

		self.sourceWordIndices = [i+1 for i in xrange(len(sentence1LemmasAndPosTags))]
		self.targetWordIndices = [i+1 for i in xrange(len(sentence2LemmasAndPosTags))]

		self.sourceWords = [item[2] for item in sentence1LemmasAndPosTags]
		self.targetWords = [item[2] for item in sentence2LemmasAndPosTags]

		self.sourceLemmas = [item[3] for item in sentence1LemmasAndPosTags]
		self.targetLemmas = [item[3] for item in sentence2LemmasAndPosTags]

		self.sourcePosTags = [item[4] for item in sentence1LemmasAndPosTags]
		self.targetPosTags = [item[4] for item in sentence2LemmasAndPosTags] 

		myWordAlignments = self.alignWords(sentence1LemmasAndPosTags, sentence2LemmasAndPosTags, 
									sentence1ParseResult, sentence2ParseResult, self.sourceWords, self.targetWords)

		align = []
		for i in myWordAlignments:
			align.append([self.sourceWords[i[0]-1], self.targetWords[i[1]-1] ])
		print "align words ", align

		return align


	'''
	sourceSent and targetSent is list of:
        [[character begin offset, character end offset], word index, word, lemma, pos tag]
	sourceParseResult and targetParseResult is list of:
		Parse Tree(Constituency tree), Text, Dependencies, words(NE, CharacOffsetEn, CharOffsetBeg,
			POS, Lemma)
	1. Align punctuations
	2. Align common NeighboringWords(at least bi-gram or more)
	3. Align Hyphenated Words
	4. Align named entities
	5. Align Main Verbs
	6. Align Nouns
	7. Align Adjectives
	8. Textual neighborhood 
	9. Align Hyphenated Words(again to check if there are still list)
	10. Dependencies neighborhood
	'''


	def alignWords(self,sourceSent, targetSent, sourceParseResult, targetParseResult, sourceWords, targetWords):


		alignments = []
		srcWordAlreadyAligned = [] #sourceWordAlreadyAligned
		tarWordAlreadyAligned = [] #TargetWordAlreadyAligned

		# 1. align the punctuations
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = self.align_punctuations(sourceWords,
				targetWords, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned,sourceSent,targetSent)

		#2. align commonNeighboringWords (atleast bigram, or more)
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
			self.align_commonNeighboringWords(sourceWords, targetWords, \
							srcWordAlreadyAligned, tarWordAlreadyAligned, alignments)

		
		#3. align Hyphenated words
		# print "source Hyphenated Words"
		checkSourceWordsInTarget = True # check if Source Words have any hyphen words
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
							self.alignHyphenWords(self.sourceWordIndices, sourceWords,\
									srcWordAlreadyAligned, alignments,\
									tarWordAlreadyAligned, checkSourceWordsInTarget)

		checkSourceWordsInTarget = False  # check if target Words have any hyphen words
		alignments,  srcWordAlreadyAligned, tarWordAlreadyAligned, = \
							self.alignHyphenWords(self.targetWordIndices, targetWords, srcWordAlreadyAligned, alignments, \
									tarWordAlreadyAligned,checkSourceWordsInTarget)

		#4. align named entities
		neAlignments = self.alignNamedEntities(sourceSent, targetSent, sourceParseResult, \
			    targetParseResult, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned) 
		
		for item in neAlignments:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])

		sourceDependencyParse = self.util.dependencyTreeWithOffSets(sourceParseResult)
		targetDependencyParse = self.util.dependencyTreeWithOffSets(targetParseResult)

		#5. Align Main Verbs
		aligned_verbs = self.alignMainVerbs(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		for item in aligned_verbs:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])


		#6. Align Nouns
		aligned_nouns = self.alignNouns(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		for item in aligned_nouns:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])
 		
 		#7. Align Adjectives
		aligned_adjectives = self.alignAdjective(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		for item in aligned_adjectives:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])

		#8. Align Adverbs
		aligned_adverbs = self.alignAdverb(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		for item in aligned_adverbs:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])

		#9. Align Textual Neighborhood
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
				self.alignTextualNeighborhoodContentWords(sourceSent, targetSent, self.sourceWordIndices,\
					self.targetWordIndices,  sourceWords, targetWords, self.sourceLemmas,\
				 		self.targetLemmas,  self.sourcePosTags, self.targetPosTags, alignments, \
				 			srcWordAlreadyAligned, tarWordAlreadyAligned)

		# Check again for hyphenated words (after textual neighborhood)
		checkSourceWordsInTarget = True # check if Source Words have any hyphen words
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
							self.alignHyphenWordsUnigram(self.sourceWordIndices, sourceWords,targetSent,\
									srcWordAlreadyAligned, alignments,\
									tarWordAlreadyAligned, checkSourceWordsInTarget)

		checkSourceWordsInTarget = False  # check if target Words have any hyphen words
		# print "target sent ", targetSent
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
							self.alignHyphenWordsUnigram(self.targetWordIndices, targetWords,sourceSent,\
									srcWordAlreadyAligned, alignments, \
									tarWordAlreadyAligned,checkSourceWordsInTarget)


		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
					self.alignDependencyNeighborhood(sourceSent, targetSent, self.sourceWordIndices,\
					self.targetWordIndices,  sourceWords, targetWords, self.sourceLemmas,\
				 	self.targetLemmas,  self.sourcePosTags, self.targetPosTags, sourceDependencyParse,\
				 	targetDependencyParse, alignments, \
				 	srcWordAlreadyAligned, tarWordAlreadyAligned)

		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
							self.alignTextualNeighborhoodPuncStopWords(self.sourceWordIndices,\
					self.targetWordIndices,  sourceWords, targetWords, self.sourceLemmas,\
				 		self.targetLemmas,  self.sourcePosTags, self.targetPosTags, alignments, \
				 			srcWordAlreadyAligned, tarWordAlreadyAligned)

		return alignments
		

	'''
	Align the sentence ending punctuation first
	returns: list; alignments, srcWordAlreadyAligned, tarWordAlreadyAligned
	'''


	def align_punctuations(self,sourceWords, targetWords, alignments, 
				srcWordAlreadyAligned, tarWordAlreadyAligned, sourceSent, targetSent):
		
		global punctuations

		# if last word of source sentence is . or ! and last of target sent is . or ! or both are equal
		if (sourceWords[len(sourceSent)-1] in ['.','!'] and targetWords[len(targetSent)-1] \
			     in ['.','!']) or (sourceWords[len(sourceSent)-1]==targetWords[len(targetSent)-1]):
			
			alignments.append([len(sourceSent), len(targetSent)])
			srcWordAlreadyAligned.append(len(sourceSent))
			tarWordAlreadyAligned.append(len(targetSent))
		# or if second last of source sent. is . or ! and last word of target sent is . or ! then append too
		elif (sourceWords[len(sourceSent)-2] in ['.', '!'] and \
					targetWords[len(targetSent)-1] in ['.', '!']):

			alignments.append([len(sourceSent), len(targetSent)])
			srcWordAlreadyAligned.append(len(sourceSent))
			tarWordAlreadyAligned.append(len(targetSent))
		# or if  last of source sent. is . or ! and second last word of target sent is . or ! then append too
		elif sourceWords[len(sourceSent)-1] in ['.', '!'] and targetWords[len(targetSent)-2]  in ['.', '!']:
			alignments.append([len(sourceSent), len(targetSent)])
			srcWordAlreadyAligned.append(len(sourceSent))
			tarWordAlreadyAligned.append(len(targetSent))
		# or if second last of source sent is 0 or ! and second last of target is . or !
		elif sourceWords[len(sourceSent)-2] in ['.', '!'] and targetWords[len(targetSent)-2]  in ['.', '!']:
			alignments.append([len(sourceSent), len(targetSent)])
			srcWordAlreadyAligned.append(len(sourceSent))
			tarWordAlreadyAligned.append(len(targetSent))

		return alignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Input: sourceWords, targetWords
	Returns: aligned words that are bigram, trigram,..(not unigram) 
			of content words
	'''


	def align_commonNeighboringWords(self, sourceWords, targetWords, srcWordAlreadyAligned, 
						tarWordAlreadyAligned, alignments):


		commonNeighboringWords = self.util.get_commonNeighboringWords(sourceWords, targetWords)
		# print "common NeighboringWords ", commonNeighboringWords

		for commonWords in commonNeighboringWords:
			stopWordsPresent = True
			# print "common Words ", commonWords
			for word in commonWords:
				
				if word not in stopwords and word not in punctuations:
					stopWordsPresent = 	False
					break
			# print "asds ", (len(word[0]))
			if len(commonWords[0]) >= 2 and not stopWordsPresent:

				for j in xrange(len(commonWords[0])):
					# print "common Word sss ", commonWords[0][j]+1
					# print "target words ", commonWords[1][j]+1
					if commonWords[0][j]+1 not in srcWordAlreadyAligned and commonWords[1][j]+1 not in \
							tarWordAlreadyAligned and [commonWords[0][j]+1, commonWords[1][j]+1] not in alignments:

						alignments.append([commonWords[0][j]+1, commonWords[1][j]+1])
						srcWordAlreadyAligned.append(commonWords[0][j]+1)
						tarWordAlreadyAligned.append(commonWords[1][j]+1)
		# print "&&&*********************************************"
		# print "alignments ", alignments
		# print "source word Aligned ", srcWordAlreadyAligned
		# print "target word aligned ", tarWordAlreadyAligned
		# print "&&&*********************************************"
		return alignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Input: wordIndices(srcWordIndices/tarWordIndices) depends upon whether we check sourceWords
				in targetWords, or other way 
			Words(srcWordIndices/tarWordIndices) 
			srcWordAlreadyAligned, alignments, tarWordAlreadyAligned,
			flag: true, then we check sourceWords in targetWords,
					else we check targetWords in sourceWords
	Returns: aligned hyphen Words(alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)
	'''


	def alignHyphenWords(self, wordIndices, Words, srcWordAlreadyAligned, alignments,
							tarWordAlreadyAligned, flag):

		
		for i in wordIndices:
			if flag:
				# print "first if statement source"
				if i in srcWordAlreadyAligned:
					continue
			else:
				# print "i in target word ", tarWordAlreadyAligned
				if i in tarWordAlreadyAligned:
					continue

			if '-' in Words[i-1] and Words[i-1] != '-':
				tokens = Words[i-1].split('-')
				#if flag true(means we check source words in target Words)

				if flag:
					commonNeighboringWords = self.util.get_commonNeighboringWords(tokens, self.targetWords)

				else:
					commonNeighboringWords = self.util.get_commonNeighboringWords(self.sourceWords, tokens)
				for pairs in commonNeighboringWords:

					if len(pairs[0]) > 1:
						
						if flag:
								for j in pairs[1]:
									if[i, j+1] not in alignments:

										alignments.append([i,j+1])
										srcWordAlreadyAligned.append(i)
										tarWordAlreadyAligned.append(j+1)
						else:
								for j in pairs[0]:
								# print"third else" 
									if[j+1, i] not in alignments:

										alignments.append([j+1,i])
										srcWordAlreadyAligned.append(j+1)
										tarWordAlreadyAligned.append(i)

		return alignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Input: source Sentence, target sentence, 
	       sourceParseResult, targetParseResult,
	       ExistingAlignments, srcWordAlreadyAligned, tarWordAlreadyAligner
	       1. Learn Named Entities
	       2. Align all full matches
	       3. Align Acronyms
	       4. Align subset matches
	Returns: list of alignments
	'''


	def alignNamedEntities(self, sourceSent, targetSent, sourceParseResult, targetParseResult, 
					existingAlignments, srcWordAlreadyAligned, tarWordAlreadyAligned):
		
		
		sourceNE = self.text_nor.get_ner(sourceParseResult)
		targetNE = self.text_nor.get_ner(targetParseResult)
		# print "before sourceNE ", sourceNE
		sourceNE, sourceWords = self.learn_NamedEntities(sourceSent, sourceNE, targetNE)
		targetNE, targetWords = self.learn_NamedEntities(targetSent, targetNE, sourceNE)

		if (len(sourceNE) == 0 or len(targetNE) == 0):
			return []

		# Align all full matches
		alignment_list, sourceNamedEntitiesAlreadyAligned, targetNamedEntitiesAlreadyAligned = \
						self.align_full_matches(sourceNE, targetNE)
		
		# Align Acronyms
		for item in sourceNE:
			if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
				continue
			for jtem in targetNE:
				if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
					continue
					
				if len(item[2])==1 and self.text_nor.is_Acronym(item[2][0], jtem[2]):
					for i in xrange(len(jtem[1])):
						if [item[1][0], jtem[1][i]] not in alignment_list:
							alignment_list.append([item[1][0], jtem[1][i]])
							sourceNamedEntitiesAlreadyAligned.append(item[1][0])
							targetNamedEntitiesAlreadyAligned.append(jtem[1][i])

				elif len(jtem[2])==1 and self.text_nor.is_Acronym(jtem[2][0], item[2]):
					for i in xrange(len(item[1])):
						if [item[1][i], jtem[1][0]] not in alignment_list:
							alignment_list.append([item[1][i], jtem[1][0]])
							sourceNamedEntitiesAlreadyAligned.append(item[1][i])
							targetNamedEntitiesAlreadyAligned.append(jtem[1][0])

		# align subset matches
		for item in sourceNE:
			if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION'] or item in \
						sourceNamedEntitiesAlreadyAligned:
				continue

			# do not align if the current source entity is present more than once
			count_words = 0
			for ktem in sourceNE:
				if ktem[2] == item[2]:
					count_words += 1
			if count_words > 1:
				continue

			for jtem in targetNE:
				if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION'] or jtem in \
								targetNamedEntitiesAlreadyAligned:
					continue

				if item[3] != jtem[3]:
					continue

				# do not align if the current target entity is present more than once
				count_words = 0
				for ktem in sourceNE:
					if ktem[2] == item[2]:
						count_words += 1

				if count_words > 1:
					continue
				
				if self.util.isSublist(item[2], jtem[2]):
					unalignedWordIndicesInTheLongerName = []
					for ktem in jtem[1]:
						unalignedWordIndicesInTheLongerName.append(ktem)
					for k in xrange(len(item[2])):
						for l in xrange(len(jtem[2])):
							if item[2][k] == jtem[2][l] and [item[1][k], jtem[1][l]] not in alignment_list:
								alignment_list.append([item[1][k], jtem[1][l]])
								if jtem[1][l] in unalignedWordIndicesInTheLongerName:
									unalignedWordIndicesInTheLongerName.remove(jtem[1][l])
					for k in xrange(len(item[1])): # the shorter name
						for l in xrange(len(jtem[1])):
							alreadyInserted = False
							for mtem in existingAlignments:
								if mtem[1] == jtem[1][l]:
									alreadyInserted = True
									break
							if jtem[1][l] not in unalignedWordIndicesInTheLongerName or alreadyInserted:
								continue
							if [item[1][k], jtem[1][l]] not in alignment_list  and targetSent[jtem[1][l]-1][2] \
										not in sourceWords  and item[2][k] not in punctuations and jtem[2][l] \
											not in punctuations:
								alignment_list.append([item[1][k], jtem[1][l]])
				 # else find if the second is a part of the first
				elif self.util.isSublist(jtem[2], item[2]):
					unalignedWordIndicesInTheLongerName = []
					for ktem in item[1]:
						unalignedWordIndicesInTheLongerName.append(ktem)
					for k in xrange(len(jtem[2])):
						for l in xrange(len(item[2])):
							if jtem[2][k] == item[2][l] and [item[1][l], jtem[1][k]] not in alignment_list:
								alignment_list.append([item[1][l], jtem[1][k]])
								if item[1][l] in unalignedWordIndicesInTheLongerName:
									unalignedWordIndicesInTheLongerName.remove(item[1][l])
					for k in xrange(len(jtem[1])): 
						for l in xrange(len(item[1])):
							alreadyInserted = False
							for mtem in existingAlignments:
								if mtem[0] == item[1][k]:
									alreadyInserted = True
									break
							if item[1][l] not in unalignedWordIndicesInTheLongerName or alreadyInserted:
								continue
							if [item[1][l], jtem[1][k]] not in alignment_list  and sourceSent[item[1][k]-1][2] \
								not in targetWords  and item[2][l] not in punctuations and jtem[2][k] \
								not in punctuations:
								
								alignment_list.append([item[1][l], jtem[1][k]])
		
		return alignment_list
					

	'''
	Input: sentParam is list of:
	 	[[character begin offset, character end offset], word index, word, lemma, pos tag]
	 LearnNE, KnownNE is list of:
		[[[['charBegin', 'charEnd'], ['charBegin', 'charEnd']], [wordIndex1, wordIndex2], ['United', 'States'], 'LOCATION']]
	LearnNE(e.g we want to find NE tags in sent1) determine unknown NE Tags from knownNE(e.g known NE tags in sent2) 
	Returns: 
	   List: LearnNE, ExtractWordsHavingNE 
	'''


	def learn_NamedEntities(self,SentParam, LearnNE, knownNE):

		
		ExtractWordsHavingNE = []

		for i in SentParam:
			alreadyIncluded = False
			for j in LearnNE:
				# check if word Index of source word is present in sourceNE(already has NE)
				if i[1] in j[1]:
					# print "matched ", i[1], j[1]
					alreadyIncluded = True
					break
			'''
			If sourceWord is already included or i[2](word length) is > 0 and 
			 firstLetterOfWord is not upper(No Acronym or not any name)
			 Then do nothing(do not append list)
			'''
			if alreadyIncluded or (len(i[2]) > 0 and not i[2][0].isupper()):
				continue

			#If sourceWord does not have any Named Entity learn from targetSent

			for k in knownNE:
				#check if sourceword(i[2]) is present in k[2](target Word)
				
				if i[2] in k[2]:
					#construct new item([ [charbegin,charEnd], [sourceWordIndex], [sourceWord], [targetWordNE] ])
					# we replace NE of sourceWord with NE of targetWord 
					newItem = [[i[0]], [i[1]], [i[2]], k[3]]
					# print "matched"
					partOfABiggerName = False
					for p in xrange(len(LearnNE)):
						if LearnNE[p][1][len(LearnNE[p][1])-1] == newItem[1][0] - 1:
							LearnNE[p][0].append(newItem[0][0])
							LearnNE[p][1].append(newItem[1][0])
							LearnNE[p][2].append(newItem[2][0])
							partOfABiggerName = True
					if not partOfABiggerName:
						LearnNE.append(newItem)

				elif self.text_nor.is_Acronym(i[2], k[2]) and [[i[0]], [i[1]], [i[2]], k[3]] not in LearnNE:
					LearnNE.append([[i[0]], [i[1]], [i[2]], k[3]])

		for i in LearnNE:

			for j in i[1]:
				if i[3] in ['PERSON', 'ORGANIZATION', 'LOCATION']:
					ExtractWordsHavingNE.append(SentParam[j-1][2])

		return LearnNE, ExtractWordsHavingNE


	'''
	Input: SourceNE, targetNE
	Returns: alignment list of full matches
	'''


	def align_full_matches(self,sourceNE, targetNE):

		# Align all full matches
		sourceNamedEntitiesAlreadyAligned = []
		targetNamedEntitiesAlreadyAligned = []
		alignments = []

		for item in sourceNE:
			# print "item in sourceNE ", item

			if item[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
				continue

			count_words = 0

			for ktem in sourceNE:
				if ktem[2] == item[2]:
					count_words += 1
			if count_words > 1:
				continue

			for jtem in targetNE:
				# print "item in sourceNE ", item

				if jtem[3] not in ['PERSON', 'ORGANIZATION', 'LOCATION']:
					continue

				count_words = 0

				for ktem in sourceNE:
					if ktem[2] == jtem[2]:
						count_words += 1
				if count_words > 1:
					continue


				# get rid of dots and hyphens in sourceNamedEntities as well targedNamedEntities
				canonicalItemWord = [i.replace('.', '') for i in item[2]] #replace . in source with space
				canonicalItemWord = [i.replace('-', '') for i in item[2]] #replace - in source with space
				canonicalJtemWord = [j.replace('.', '') for j in jtem[2]] #replace . in target with space
				canonicalJtemWord = [j.replace('-', '') for j in jtem[2]] ##replace - in target with space

				# if canonicalItemWord(sourceEntities) matches with canoncialJtemWord(targetEntities)
				# if word indexes are not aligned or not present in alignments list
				# then add with their indexes in alignment list
				# later on, also append item of source and targetNameEntites in separate lists
				if canonicalItemWord == canonicalJtemWord:
					for k in xrange(len(item[1])):
						if ([item[1][k], jtem[1][k]]) not in alignments:
							alignments.append([item[1][k], jtem[1][k]])
					sourceNamedEntitiesAlreadyAligned.append(item)
					targetNamedEntitiesAlreadyAligned.append(jtem)

		return alignments, sourceNamedEntitiesAlreadyAligned, targetNamedEntitiesAlreadyAligned


	'''
	Input: 
	Returns: aligned verbs
	'''


	def alignMainVerbs(self, srcWordIndices, tarWordIndices, srcWords, tarWords, srcLemmas,\
			 tarLemmas,  srcPosTags, tarPosTags, sourceDependencyParse,targetDependencyParse, existingalignments, 
			 			srcWordAlreadyAligned, tarWordAlreadyAligned):
		

		AlignedVerbs = []
		numberofMainVerbsInSource = 0 
		evidenceCountMatrix = {}
		relativeAlignmentsMatrix = {} # contains aligned Verbs with their similar child/parents 
		wordSimilarity = {} # dictionary contains similarity score of two word indices(src and tar)

		# sourceDependencyParse = self.util.dependencyTreeWithOffSets(sourceParseResult)
		# targetDependencyParse = self.util.dependencyTreeWithOffSets(targetParseResult)

		# print "targetDependencyParse ", targetDependencyParse

		#construct the two matrices in following loop
		# print "tar word Indices ", tarWordIndices
		# print "srcwordAlreadyAligned ", srcWordAlreadyAligned
		for i in srcWordIndices:
			# print "i ", i
			# print "i in srcWordAlready Aligned ", i in srcWordAlreadyAligned
			# print "sourcePOS TAgs != v ", srcPosTags[i-1][0].lower() != 'v'
			# print "source Lemmas in stop words ", srcLemmas[i-1] in stopwords
			# print "pos tags ", srcPosTags[i-1][0].lower()

			if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'v' or srcLemmas[i-1] in stopwords:
				# print "srcPOSTAgs, words inside ", srcPosTags[i-1][0].lower(), srcWords[i-1] 
				continue
			# print "srcPOSTAgs, words are verbs ", srcPosTags[i-1][0].lower(), srcWords[i-1] 
			# print "src Lemmas ", srcLemmas[i-1]
			numberofMainVerbsInSource += 1
			# print "*********************************************"
			# print "number Of verbs ", numberofMainVerbsInSource
			for j in tarWordIndices:
				# print "j", j
				if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'v' or tarLemmas[j-1] in stopwords:
					# print "tarPosTags, words inside", tarPosTags[j-1][0].lower(), tarWords[j-1]
					continue
				# print "tarPosTags, words are verbs ", tarPosTags[j-1][0].lower(), tarWords[j-1]
				# print "target lemmas ", tarLemmas[j-1]
				getSimilarityScore = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
						srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
								self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
							 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
				# print "similarity computations score ", res
				if getSimilarityScore < ppdbSim:
					
					# print "score less than 0.9 "
					continue
			
				wordSimilarity[(i,j)] = getSimilarityScore
				# print "word Similarity (i,j) ", wordSimilarity
				# print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
				# print "source Parse ", sourceDependencyParse
				# print "i ", i
				# print "source Words ", srcWords[i-1]
				# print "********************************************"
				# print"target Parse ", targetDependencyParse
				# print "*****************************************"
				# print ""  
				sourceWordParents = self.util.findParents(sourceDependencyParse, i, srcWords[i-1])
				sourceWordChildren = self.util.findChildren(sourceDependencyParse, i, srcWords[i-1])
				targetWordParents = self.util.findParents(targetDependencyParse, j, tarWords[j-1])
				targetWordChildren = self.util.findChildren(targetDependencyParse, j, tarWords[j-1])

				# Search for common or equivalent children(discussed in paper)
				group1OfSimilarRelationsForNounChild = ['agent', 'nsubj', 'xsubj']
				group2OfSimilarRelationsForNounChild = ['dobj', 'nsubjpass', 'rel', 'ccmop', 'partmod']
				group3OfSimilarRelationsForNounChild = ['tmod','prep_in','prep_at','prep_on']
				group4OfSimilarRelationsForNounChild = ['iobj','prep_to']
				groupOfSimilarRelationsForVerbChild = ['purpcl', 'xcomp']

				for k in sourceWordChildren:
					for l in targetWordChildren:

						if (k[0], l[0]) in existingalignments+AlignedVerbs or \
								max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], tarPosTags[l[0]-1]),\
									self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1]) ) >= ppdbSim and \
									 ((k[2] == l[2]) or \
									 (k[2] in group1OfSimilarRelationsForNounChild and l[2] in group1OfSimilarRelationsForNounChild) or \
									 (k[2] in group2OfSimilarRelationsForNounChild and l[2] in group2OfSimilarRelationsForNounChild) or \
									 (k[2] in group3OfSimilarRelationsForNounChild and l[2] in group3OfSimilarRelationsForNounChild) or \
									 (k[2] in group4OfSimilarRelationsForNounChild and l[2] in group4OfSimilarRelationsForNounChild) or \
									 (k[2] in groupOfSimilarRelationsForVerbChild and l[2] in groupOfSimilarRelationsForVerbChild)):

								 if (i, j) in evidenceCountMatrix:
								 	evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								 else:
								 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))

								 # print "evidence Count Matrix first tie ", evidenceCountMatrix
								 # relativeAlignmentsMatrix {(2, 3): [[1, 1]]} 
								 # (2,3) are verbs, and [1,1] are their childrens that has similar relations
								 if (i, j) in relativeAlignmentsMatrix:
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

								 else:
								 	relativeAlignmentsMatrix[(i,j)] = []
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])
				
				# # search for common or equivalent parents(children noun)
				# considers only first orientation from paper
				groupOfSimilarRelationsForNounParent = ['infmod', 'partmod', 'rcmod']
				groupOfSimilarRelationsForVerbParent = ['purpcl', 'xcomp']

				# if no parent(means it is only Root) then compare last words in sentence
				for k in sourceWordParents:
					for l in targetWordParents:
						if (k[0], l[0]) in existingalignments+AlignedVerbs or \
								max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1],
									l[1], tarPosTags[l[0]-1]),\
									self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], srcPosTags[k[0]-1], 
										tarLemmas[l[0]-1], tarPosTags[l[0]-1])) >= ppdbSim and \
								 (k[2] == l[2]) or \
								 (k[2] in groupOfSimilarRelationsForNounParent and l[2] in groupOfSimilarRelationsForNounParent) or \
								 (k[2] in groupOfSimilarRelationsForVerbChild and l[2] in groupOfSimilarRelationsForVerbChild):
								 
								 if (i, j) in evidenceCountMatrix:

								 	evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								 else:
								 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


								 if (i, j) in relativeAlignmentsMatrix:
								 	relativeAlignmentsMatrix
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

								 else:
								 	relativeAlignmentsMatrix[(i,j)] = []
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

				groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild = [['cop', 'csubj'], ['acomp']]
				group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['csubj'], ['csubjpass']]
				group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['conj_and'], ['conj_and']]
				group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['conj_or'], ['conj_or']]
				group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['conj_nor'], ['conj_nor']]

				# search for equivalent parent-child pairs
				evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordParents, targetWordChildren, \
					AlignedVerbs, existingalignments,\
					srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \
						groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1],\

							group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0],\
							group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \

							group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0],\
							group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \

							group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
							group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1],\

							group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
							group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \
							evidenceCountMatrix,relativeAlignmentsMatrix)

				# search for equivalent child-parent pairs
				evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordChildren, targetWordParents, \
					AlignedVerbs, existingalignments,\
					srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
						groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0],\
							group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1],\
							group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
							group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1],\
							group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
							group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \
							group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0],\
							group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \
							group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
							evidenceCountMatrix,relativeAlignmentsMatrix)

				# search for equivalent child-parent pairs

				for k in sourceWordChildren:
					for l in targetWordParents:
						if (k[0], l[0]) in existingalignments+AlignedVerbs or \
								max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1],
									l[1], tarPosTags[l[0]-1]),\
									self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], srcPosTags[k[0]-1], 
										tarLemmas[l[0]-1], tarPosTags[l[0]-1])) >= ppdbSim and \
								 (k[2] == l[2]) or \
								 (k[2] in groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild and l[2] in groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild) or \
								 (k[2] in group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild and l[2] in group1OfSimilarRelationsInOppositeDirectionForVerbParentAndChild) or \
								 (k[2] in group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild and l[2] in group2OfSimilarRelationsInOppositeDirectionForVerbParentAndChild) or \
								 (k[2] in group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild and l[2] in group3OfSimilarRelationsInOppositeDirectionForVerbParentAndChild) or \
								 (k[2] in group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild and l[2] in group4OfSimilarRelationsInOppositeDirectionForVerbParentAndChild):


								 if (i, j) in evidenceCountMatrix:
								 	evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								 else:
								 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


								 if (i, j) in relativeAlignmentsMatrix:
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

								 else:
								 	relativeAlignmentsMatrix[(i,j)] = []
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

		# use collected stats to align
		for p in xrange(numberofMainVerbsInSource):

			maxEvidenceCountForCurrentPass = 0
			maxOverallValueForCurrentPass = 0
			indexPairWithStrongestTieForCurrentPass = [-1, -1] # indexes of aligned verbs

			for i in srcWordIndices:
				if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'v' or \
							srcLemmas[i-1] in stopwords:
					continue

				for j in tarWordIndices:
					if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'v' or \
								tarLemmas[j-1] in stopwords:
						continue

					# getWeight = theta1 * wordSimilarity[(i, j)] + (1-theta1)*evidenceCountMatrix[(i, j)]

					if(i, j) in evidenceCountMatrix and theta1*wordSimilarity[(i,j)] + \
														(1-theta1)*evidenceCountMatrix[(i, j)] > maxOverallValueForCurrentPass:
						maxOverallValueForCurrentPass = theta1*wordSimilarity[(i,j)] + \
														(1-theta1)*evidenceCountMatrix[(i, j)]
						maxEvidenceCountForCurrentPass = evidenceCountMatrix[(i, j)]
						indexPairWithStrongestTieForCurrentPass = [i, j]
						
			if maxEvidenceCountForCurrentPass > 0:
				AlignedVerbs.append(indexPairWithStrongestTieForCurrentPass)
				srcWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[0])
				tarWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[1])
				
				for item in relativeAlignmentsMatrix[(indexPairWithStrongestTieForCurrentPass[0], \
								indexPairWithStrongestTieForCurrentPass[1])]:
				
						if item[0] != 0 and item[1] != 0 and item[0] not in srcWordAlreadyAligned and \
										item[1] not in tarWordAlreadyAligned:
								AlignedVerbs.append(item)
								srcWordAlreadyAligned.append(item[0])
								tarWordAlreadyAligned.append(item[1])
			# no aligned verbs formed
			else:
				break

		return AlignedVerbs


	'''
	Returns: Aligned nouns
	'''


	def alignNouns(self, srcWordIndices, tarWordIndices, srcWords, tarWords, srcLemmas,\
			 tarLemmas,  srcPosTags, tarPosTags, sourceDependencyParse,targetDependencyParse, existingalignments, 
			 			srcWordAlreadyAligned, tarWordAlreadyAligned):


		nounAlignments = []
		numberofNounsInSource = 0 
		evidenceCountMatrix = {}
		relativeAlignmentsMatrix = {} # contains aligned Verbs with their similar child/parents 
		wordSimilarity = {} # dictionary contains similarity score of two word indices(src and tar)


		for i in srcWordIndices:

			if i in srcWordAlreadyAligned or (srcPosTags[i-1][0].lower() != 'n' \
									and srcPosTags[i-1].lower() != 'prp'):
				continue

			numberofNounsInSource += 1

			for j in tarWordIndices:

				if j in tarWordAlreadyAligned or (tarPosTags[j-1][0].lower() != 'n' \
											and tarPosTags[j-1].lower() != 'prp'):
					continue

				getSimilarityScore = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
							srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
									self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
								 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
				if getSimilarityScore < ppdbSim:
					continue

				wordSimilarity[(i,j)] = getSimilarityScore

				sourceWordParents = self.util.findParents(sourceDependencyParse, i, srcWords[i-1])
				sourceWordChildren = self.util.findChildren(sourceDependencyParse, i, srcWords[i-1])
				targetWordParents = self.util.findParents(targetDependencyParse, j, tarWords[j-1])
				targetWordChildren = self.util.findChildren(targetDependencyParse, j, tarWords[j-1])

				
				#search for common or equivalent children
				groupOfSimilarRelationsForNounChild = ['pos', 'nn' 'prep_of', 'prep_in', 'prep_at', 'prep_for']
				groupOfSimilarRelationsForVerbChild = ['infmod', 'partmod', 'rcmod']
				groupOfSimilarRelationsForAdjectiveChild = ['amod', 'rcmod']

				for k in sourceWordChildren:
					for l in targetWordChildren:
						if (k[0], l[0]) in existingalignments+nounAlignments or \
								max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
											l[1], tarPosTags[l[0]-1]),\
									self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
											srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
														>= ppdbSim and \
								 ((k[2] == l[2]) or \
								 (k[2] in groupOfSimilarRelationsForNounChild and l[2] in groupOfSimilarRelationsForNounChild) or \
								 (k[2] in groupOfSimilarRelationsForVerbChild and l[2] in groupOfSimilarRelationsForVerbChild) or \
								 (k[2] in groupOfSimilarRelationsForAdjectiveChild and l[2] in groupOfSimilarRelationsForAdjectiveChild)):

							if (i, j) in evidenceCountMatrix:
								evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
							else:

							 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
							 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
							 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


							if (i, j) in relativeAlignmentsMatrix:
							 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

							else:
								relativeAlignmentsMatrix[(i,j)] = []
								relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

				#search for common or equivalent parents

				groupOfSimilarRelationsForNounParent = ['pos', 'nn', 'prep_of', 'prep_in', 'prep_at', 'prep_for']
				group1OfSimilarRelationsForVerbParent = ['agent', 'nsubj', 'xsubj']
				group2OfSimilarRelationsForVerbParent = ['ccomp', 'dobj', 'nsubjpass', 'rel', 'partmod']
				group3OfSimilarRelationsForVerbParent = ['tmod' 'prep_in', 'prep_at', 'prep_on']
				group4OfSimilarRelationsForVerbParent = ['iobj', 'prep_to']
				

				for k in sourceWordParents:
					for l in targetWordParents:
						if (k[0], l[0]) in existingalignments+nounAlignments or \
								max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
											l[1], tarPosTags[l[0]-1]),\
									self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
											srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
														>= ppdbSim and \
								 ((k[2] == l[2]) or \
								 (k[2] in groupOfSimilarRelationsForNounParent and l[2] in groupOfSimilarRelationsForNounParent) or \
								 (k[2] in group1OfSimilarRelationsForVerbParent and l[2] in group1OfSimilarRelationsForVerbParent) or \
								 (k[2] in group2OfSimilarRelationsForVerbParent and l[2] in group2OfSimilarRelationsForVerbParent) or \
								 (k[2] in group3OfSimilarRelationsForVerbParent and l[2] in group3OfSimilarRelationsForVerbParent) or \
								 (k[2] in group4OfSimilarRelationsForVerbParent and k[2] in group4OfSimilarRelationsForVerbParent)):

							if (i, j) in evidenceCountMatrix:
								evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
							else:

							 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
							 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
							 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


							if (i, j) in relativeAlignmentsMatrix:
							 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

							else:
								relativeAlignmentsMatrix[(i,j)] = []
								relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])			


				groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild = [['nsubj'], ['amod', 'rcmod']]
				groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['ccomp', 'dobj', 'nsubjpass', 'rel', 'partmod'], ['infmod', 'partmod', 'rcmod']]
				group1OfSimilarRelationsInOppositeDirectionForNounParentAndChild = [['conj_and'], ['conj_and']]
				group2OfSimilarRelationsInOppositeDirectionForNounParentAndChild = [['conj_or'], ['conj_or']]
				group3OfSimilarRelationsInOppositeDirectionForNounParentAndChild = [['conj_nor'], ['conj_nor']]
				# search for equivalent parent-child relations
				evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordParents, targetWordChildren, \
									nounAlignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \
										groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \
											group1OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0],\
											group1OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0], \
											group2OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1],\
											group3OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0], \
											group3OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1], \
											evidenceCountMatrix,relativeAlignmentsMatrix)
				
				# search for equivalent child-parent relations
				#here we iterate through sourceWordChildren(outerloop) and targetWordParents(inner loop) 
 				evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordChildren, targetWordParents, \
									nounAlignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
										groupOfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \
											group1OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1],\
											group1OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0], \
											group2OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0],\
											group3OfSimilarRelationsInOppositeDirectionForNounParentAndChild[1], \
											group3OfSimilarRelationsInOppositeDirectionForNounParentAndChild[0], \
											evidenceCountMatrix,relativeAlignmentsMatrix)

		# use collected stats to align
		for p in xrange(numberofNounsInSource):

			maxEvidenceCountForCurrentPass = 0
			maxOverallValueForCurrentPass = 0
			indexPairWithStrongestTieForCurrentPass = [-1, -1] # indexes of aligned nouns

			for i in srcWordIndices:
				if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'n' or \
							srcLemmas[i-1] in stopwords:
					continue

				for j in tarWordIndices:
					if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'n' or \
								tarLemmas[j-1] in stopwords:
						continue

					if(i, j) in evidenceCountMatrix and theta1*wordSimilarity[(i,j)] + \
														(1-theta1)*evidenceCountMatrix[(i, j)] > maxOverallValueForCurrentPass:
						maxOverallValueForCurrentPass = theta1*wordSimilarity[(i,j)] + \
														(1-theta1)*evidenceCountMatrix[(i, j)]
						maxEvidenceCountForCurrentPass = evidenceCountMatrix[(i, j)]
						indexPairWithStrongestTieForCurrentPass = [i, j]
						
			if maxEvidenceCountForCurrentPass > 0:
				nounAlignments.append(indexPairWithStrongestTieForCurrentPass)
				srcWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[0])
				tarWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[1])

				for item in relativeAlignmentsMatrix[(indexPairWithStrongestTieForCurrentPass[0], \
								indexPairWithStrongestTieForCurrentPass[1])]:
						# item[0] and item[1] != 0 so that we should not store Root-0
						if item[0] != 0 and item[1] != 0 and item[0] not in srcWordAlreadyAligned and \
										item[1] not in tarWordAlreadyAligned:
								nounAlignments.append(item)
								srcWordAlreadyAligned.append(item[0])
								tarWordAlreadyAligned.append(item[1])
			# no aligned nouns formed
			else:
				break

		return nounAlignments


	'''
	Auxillary function to find equivalent parent-child / child-parent relation used 
	to reduce repeatation of code in align nouns, align adjective and align verbs
	'''


	def findEquivalentParentChildRelation(self, i, j, sourceDepenency, targetDependency, Alignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, AdjParentAndChildSrc, AdjParentAndChildTar,\
											OppDirecVerbParentAndChildSrc, OppDirecVerbParentAndChildTar, \
											group1OppDirectNounParentAndChildSrc, group1OppDirectNounParentAndChildTar, \
											group2OppDirectNounParentAndChildSrc, group2OppDirectNounParentAndChildTar,\
											group3OppDirectNounParentAndChildSrc, group3OppDirectNounParentAndChildTar, \
											evidenceCountMatrix, relativeAlignmentsMatrix ):


		for k in sourceDepenency:
			for l in targetDependency:
				if (k[0], l[0]) in existingalignments+Alignments or \
						max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
									l[1], tarPosTags[l[0]-1]),\
							self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
									srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
												>= ppdbSim and \
						 ((k[2] == l[2]) or \
						 (k[2] in AdjParentAndChildSrc and l[2] in AdjParentAndChildTar) or \
						 (k[2] in OppDirecVerbParentAndChildSrc and l[2] in OppDirecVerbParentAndChildTar) or \
						 (k[2] in group1OppDirectNounParentAndChildSrc and l[2] in group1OppDirectNounParentAndChildTar) or \
						 (k[2] in group2OppDirectNounParentAndChildSrc and l[2] in group2OppDirectNounParentAndChildTar) or \
						 (k[2] in group3OppDirectNounParentAndChildSrc and k[2] in group3OppDirectNounParentAndChildTar)):

					if (i, j) in evidenceCountMatrix:
						evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
						 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
						 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
					else:

					 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
					 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
					 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


					if (i, j) in relativeAlignmentsMatrix:
					 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

					else:
						relativeAlignmentsMatrix[(i,j)] = []
						relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])	

		return evidenceCountMatrix, relativeAlignmentsMatrix	


	'''
	Returns Aligned adjectives
	'''


	def alignAdjective(self, srcWordIndices, tarWordIndices, srcWords, tarWords, srcLemmas,\
				 tarLemmas,  srcPosTags, tarPosTags, sourceDependencyParse,targetDependencyParse, existingalignments, 
				 			srcWordAlreadyAligned, tarWordAlreadyAligned):
			

			adjectiveAlignments= []
			numberofAdjectivesInSource = 0 
			evidenceCountMatrix = {}
			relativeAlignmentsMatrix = {} # contains aligned Verbs with their similar child/parents 
			wordSimilarity = {} # dictionary contains similarity score of two word indices(src and tar)

			for i in srcWordIndices:
				if i in srcWordAlreadyAligned or (srcPosTags[i-1][0].lower() != 'j'):
					continue

				numberofAdjectivesInSource += 1
				# print "number of adjectives in source ", numberofAdjectivesInSource

				for j in tarWordIndices:
					if j in tarWordAlreadyAligned or (tarPosTags[j-1][0].lower() != 'j'):
						continue

					getSimilarityScore = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
								srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
										self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
									 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
					
					if getSimilarityScore < ppdbSim:
						continue
					
					wordSimilarity[(i,j)] = getSimilarityScore

					sourceWordParents = self.util.findParents(sourceDependencyParse, i, srcWords[i-1])
					sourceWordChildren = self.util.findChildren(sourceDependencyParse, i, srcWords[i-1])
					targetWordParents = self.util.findParents(targetDependencyParse, j, tarWords[j-1])
					targetWordChildren = self.util.findChildren(targetDependencyParse, j, tarWords[j-1])

					# search for common children
					for k in sourceWordChildren:
						for l in targetWordChildren:
							if (k[0], l[0]) in existingalignments+adjectiveAlignments or \
									max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
												l[1], tarPosTags[l[0]-1]),\
										self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
												srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
															>= ppdbSim and (k[2] == l[2]):

								if (i, j) in evidenceCountMatrix:
									evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
									 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
									 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								else:

								 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


								if (i, j) in relativeAlignmentsMatrix:
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])
								 	# print "relative Alignments in common already present", relativeAlignmentsMatrix

								else:
									relativeAlignmentsMatrix[(i,j)] = []
									relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])
									
					# search for common or equivalent parents
					groupOfSimilarRelationsForNounParent = ['amod', 'rcmod']

					for k in sourceWordParents:
						for l in targetWordParents:
							if (k[0], l[0]) in existingalignments+adjectiveAlignments or \
									max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
												l[1], tarPosTags[l[0]-1]),\
										self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
												srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
															>= ppdbSim and \
									 ((k[2] == l[2]) or \
									 (k[2] in groupOfSimilarRelationsForNounParent and l[2] in groupOfSimilarRelationsForNounParent)):

								if (i, j) in evidenceCountMatrix:
									evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
									 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
									 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								else:

								 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
								 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
								 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
								if (i, j) in relativeAlignmentsMatrix:
								 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])
								else:
									relativeAlignmentsMatrix[(i,j)] = []
									relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

					groupOfSimilarRelationsInOppositeDirectionForNounParentAndChild = [['amod', 'rcmod'], ['nsubj']]
					groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild = [['acomp'], ['cop', 'csubj']]
					group1OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild = [['conj_and'], ['conj_and']]
					group2OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild = [['conj_or'], ['conj_or']]
					group3OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild = [['conj_nor'], ['conj_nor']]

					#search for equivaent parent-child pair

					evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordParents, targetWordChildren, \
									adjectiveAlignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForNounParentAndChild[0], \
										groupOfSimilarRelationsInOppositeDirectionForNounParentAndChild[1],\

											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1], \
											group1OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0],\
											group1OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \
											group2OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1],\
											group3OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \
											group3OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
											evidenceCountMatrix,relativeAlignmentsMatrix)

					#search for equivalent child-parent pair

					evidenceCountMatrix, relativeAlignmentsMatrix = self.findEquivalentParentChildRelation(i, j, sourceWordChildren, 
									targetWordParents, adjectiveAlignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, groupOfSimilarRelationsInOppositeDirectionForNounParentAndChild[1], \
										groupOfSimilarRelationsInOppositeDirectionForNounParentAndChild[0],\

											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[1],\
											groupOfSimilarRelationsInOppositeDirectionForVerbParentAndChild[0], \

											group1OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1],\
											group1OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \

											group2OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0],\

											group3OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[1], \
											group3OfSimilarRelationsInOppositeDirectionForAdjectiveParentAndChild[0], \
											evidenceCountMatrix,relativeAlignmentsMatrix)


			# use collected stats to align
			for p in xrange(numberofAdjectivesInSource):

				maxEvidenceCountForCurrentPass = 0
				maxOverallValueForCurrentPass = 0
				indexPairWithStrongestTieForCurrentPass = [-1, -1] # indexes of aligned nouns

				for i in srcWordIndices:
					if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'j' or \
								srcLemmas[i-1] in stopwords:
						continue

					for j in tarWordIndices:
						if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'j' or \
									tarLemmas[j-1] in stopwords:
							continue

						if(i, j) in evidenceCountMatrix and theta1*wordSimilarity[(i,j)] + \
															(1-theta1)*evidenceCountMatrix[(i, j)] > maxOverallValueForCurrentPass:
							maxOverallValueForCurrentPass = theta1*wordSimilarity[(i,j)] + \
															(1-theta1)*evidenceCountMatrix[(i, j)]
							maxEvidenceCountForCurrentPass = evidenceCountMatrix[(i, j)]
							indexPairWithStrongestTieForCurrentPass = [i, j]
							
				if maxEvidenceCountForCurrentPass > 0:
					adjectiveAlignments.append(indexPairWithStrongestTieForCurrentPass)
					srcWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[0])
					tarWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[1])

					for item in relativeAlignmentsMatrix[(indexPairWithStrongestTieForCurrentPass[0], \
									indexPairWithStrongestTieForCurrentPass[1])]:
							# item[0] and item[1] != 0 so that we should not store Root-0
							if item[0] != 0 and item[1] != 0 and item[0] not in srcWordAlreadyAligned and \
											item[1] not in tarWordAlreadyAligned:
									adjectiveAlignments.append(item)
									srcWordAlreadyAligned.append(item[0])
									tarWordAlreadyAligned.append(item[1])
				# no aligned adjective formed
				else:
					break
		
			return adjectiveAlignments


	'''
	Returns: Aligned adverbs
	'''


	def alignAdverb(self, srcWordIndices, tarWordIndices, srcWords, tarWords, srcLemmas,\
				 tarLemmas,  srcPosTags, tarPosTags, sourceDependencyParse,targetDependencyParse, existingalignments, 
				 			srcWordAlreadyAligned, tarWordAlreadyAligned):


			adverbAlignments= []
			numberofAdverbsInSource = 0 
			evidenceCountMatrix = {}
			relativeAlignmentsMatrix = {} # contains aligned Verbs with their similar child/parents 
			wordSimilarity = {} # dictionary contains similarity score of two word indices(src and tar)

			for i in srcWordIndices:

				if i in srcWordAlreadyAligned or (srcPosTags[i-1][0].lower() != 'r'):
					continue

				numberofAdverbsInSource += 1
				# print "number of adverbs in source ", numberofAdverbsInSource
				for j in tarWordIndices:
					if j in tarWordAlreadyAligned or (tarPosTags[j-1][0].lower() != 'r'):
						continue

					getSimilarityScore = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
								srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
										self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
									 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
					
					if getSimilarityScore < ppdbSim:
						continue
					
					wordSimilarity[(i,j)] = getSimilarityScore

					sourceWordParents = self.util.findParents(sourceDependencyParse, i, srcWords[i-1])
					sourceWordChildren = self.util.findChildren(sourceDependencyParse, i, srcWords[i-1])
					targetWordParents = self.util.findParents(targetDependencyParse, j, tarWords[j-1])
					targetWordChildren = self.util.findChildren(targetDependencyParse, j, tarWords[j-1])
					
					# print "***************************"
					# print "source Word Parents ", sourceWordParents
					# print "source word children ", sourceWordChildren
					# print "target word parents ", targetWordParents
					# print "target word children ", targetWordChildren
					# print "***************************"
					#search for common children
					evidenceCountMatrix, relativeAlignmentsMatrix = self.findCommonRelation(i, j, \
										sourceWordChildren, targetWordChildren, adverbAlignments, \
											existingalignments, srcPosTags, tarPosTags, \
											srcLemmas, tarLemmas, evidenceCountMatrix, relativeAlignmentsMatrix)
					# print "****************************"
					# print "Common children"
					# print "evidence count matrix ", evidenceCountMatrix
					# print "relative alignments ", relativeAlignmentsMatrix
					# print "****************************"
					#search for common parents
					evidenceCountMatrix, relativeAlignmentsMatrix = self.findCommonRelation(i, j, \
										sourceWordParents, targetWordParents, adverbAlignments, \
											existingalignments, srcPosTags, tarPosTags, \
											srcLemmas, tarLemmas, evidenceCountMatrix, relativeAlignmentsMatrix)

					# print "****************************"
					# print "Common parents"
					# print "evidence count matrix ", evidenceCountMatrix
					# print "relative alignments ", relativeAlignmentsMatrix
					# print "****************************"
					group1OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild = [['conj_and'], ['conj_and']]
					group2OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild = [['conj_or'], ['conj_or']]
					group3OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild = [['conj_nor'], ['conj_nor']]
					# search for equivalent parent-child relationships
					evidenceCountMatrix, relativeAlignmentsMatrix = self.findCommonParentChildRelationAdverb(i, \
										j, sourceWordParents, targetWordChildren, adverbAlignments, \
									existingalignments,srcPosTags, tarPosTags, srcLemmas,tarLemmas, \
									 
											group1OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0],\
											group1OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0], \
											group2OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1],\
											group3OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0], \
											group3OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1], \
											evidenceCountMatrix,relativeAlignmentsMatrix)
					# print "****************************"
					# print "equi parent-child"
					# print "evidence count matrix ", evidenceCountMatrix
					# print "relative alignments ", relativeAlignmentsMatrix
					# print "****************************"
					# search for equivalent child-parent relationships
					evidenceCountMatrix, relativeAlignmentsMatrix = self.findCommonParentChildRelationAdverb(i, \
										j, sourceWordChildren, targetWordParents, adverbAlignments, \
									existingalignments,srcPosTags, tarPosTags, srcLemmas,tarLemmas, \
											group1OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1],\
											group1OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0], \
											group2OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1], \
											group2OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0],\
											group3OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[1], \
											group3OfSimilarRelationsInOppositeDirectionForAdverbParentAndChild[0], \
											evidenceCountMatrix,relativeAlignmentsMatrix)

					# print "****************************"
					# print "equi child-parent"
					# print "evidence count matrix ", evidenceCountMatrix
					# print "relative alignments ", relativeAlignmentsMatrix
					# print "****************************"

			# use collected stats to align
			for p in xrange(numberofAdverbsInSource):

				maxEvidenceCountForCurrentPass = 0
				maxOverallValueForCurrentPass = 0
				indexPairWithStrongestTieForCurrentPass = [-1, -1] # indexes of aligned nouns

				for i in srcWordIndices:
					if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'r' or \
								srcLemmas[i-1] in stopwords:
						continue

					for j in tarWordIndices:
						if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'r' or \
									tarLemmas[j-1] in stopwords:
							continue

						if(i, j) in evidenceCountMatrix and theta1*wordSimilarity[(i,j)] + \
															(1-theta1)*evidenceCountMatrix[(i, j)] > maxOverallValueForCurrentPass:
							maxOverallValueForCurrentPass = theta1*wordSimilarity[(i,j)] + \
															(1-theta1)*evidenceCountMatrix[(i, j)]
							maxEvidenceCountForCurrentPass = evidenceCountMatrix[(i, j)]
							indexPairWithStrongestTieForCurrentPass = [i, j]
							
				if maxEvidenceCountForCurrentPass > 0:
					adverbAlignments.append(indexPairWithStrongestTieForCurrentPass)
					srcWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[0])
					tarWordAlreadyAligned.append(indexPairWithStrongestTieForCurrentPass[1])

					for item in relativeAlignmentsMatrix[(indexPairWithStrongestTieForCurrentPass[0], \
									indexPairWithStrongestTieForCurrentPass[1])]:
							# item[0] and item[1] != 0 so that we should not store Root-0
							if item[0] != 0 and item[1] != 0 and item[0] not in srcWordAlreadyAligned and \
											item[1] not in tarWordAlreadyAligned:
									adverbAlignments.append(item)
									srcWordAlreadyAligned.append(item[0])
									tarWordAlreadyAligned.append(item[1])
				# no aligned adjective formed
				else:
					break
		
			return adverbAlignments


	'''
	This function helps to reduce code for (search for common children) and (search for common parents)
		in align adverbs
	'''
	

	def findCommonRelation(self, i, j, sourceDepenency, targetDependency, Alignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas,
											evidenceCountMatrix, relativeAlignmentsMatrix):


			for k in sourceDepenency:
				for l in targetDependency:
					if (k[0], l[0]) in existingalignments+Alignments or \
							max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
										l[1], tarPosTags[l[0]-1]),\
								self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
										srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
													>= ppdbSim and (k[2] == l[2]):

						if (i, j) in evidenceCountMatrix:
							evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
							 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
							 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
						else:

						 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
						 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
						 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


						if (i, j) in relativeAlignmentsMatrix:
						 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

						else:
							relativeAlignmentsMatrix[(i,j)] = []
							relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

			return evidenceCountMatrix, relativeAlignmentsMatrix


	'''
	This function helps to reduce code for (search for common children-parent) and (search for 
		common parent-child) in align adverbs
	'''


	def findCommonParentChildRelationAdverb(self, i, j, sourceDepenency, targetDependency, Alignments, existingalignments,\
									srcPosTags, tarPosTags, srcLemmas,tarLemmas, \
											group1OppDirectAdverbParentAndChildSrc, group1OppDirectAdverbParentAndChildTar, \
											group2OppDirectAdverbParentAndChildSrc, group2OppDirectAdverbParentAndChildTar,\
											group3OppDirectAdverbParentAndChildSrc, group3OppDirectAdverbParentAndChildTar, \
											evidenceCountMatrix, relativeAlignmentsMatrix ):


		for k in sourceDepenency:
			for l in targetDependency:
				if (k[0], l[0]) in existingalignments+Alignments or \
						max( self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], \
									l[1], tarPosTags[l[0]-1]),\
							self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
									srcPosTags[k[0]-1],tarLemmas[l[0]-1], tarPosTags[l[0]-1])) \
												>= ppdbSim and \
						 ((k[2] == l[2]) or \
						 (k[2] in group1OppDirectAdverbParentAndChildSrc and l[2] in group1OppDirectAdverbParentAndChildTar) or \
						 (k[2] in group2OppDirectAdverbParentAndChildSrc and l[2] in group2OppDirectAdverbParentAndChildTar) or \
						 (k[2] in group3OppDirectAdverbParentAndChildSrc and k[2] in group3OppDirectAdverbParentAndChildTar)):

					if (i, j) in evidenceCountMatrix:
						evidenceCountMatrix[(i, j)] += max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
						 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
						 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))
					else:

					 	evidenceCountMatrix[(i, j)] = max(self.word_similarity.computeWordSimilarityScore(k[1], srcPosTags[k[0]-1], l[1], \
					 								tarPosTags[l[0]-1]), self.word_similarity.computeWordSimilarityScore(srcLemmas[k[0]-1], \
					 								srcPosTags[k[0]-1], tarLemmas[l[0]-1], tarPosTags[l[0]-1]))


					if (i, j) in relativeAlignmentsMatrix:
					 	relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])

					else:
						relativeAlignmentsMatrix[(i,j)] = []
						relativeAlignmentsMatrix[(i,j)].append([k[0],l[0]])	

		return evidenceCountMatrix, relativeAlignmentsMatrix	


	'''
	Returns textual neighborhood in 3 by 3 window
	'''


	def alignTextualNeighborhoodContentWords(self, sourceSent, targetSent, srcWordIndices, tarWordIndices, srcWords, tarWords, srcLemmas,\
				 tarLemmas,  srcPosTags, tarPosTags, existingalignments, 
				 			srcWordAlreadyAligned, tarWordAlreadyAligned):


		wordSimilarities = {}
		textualNeighborhoodSimilarities = {}
		sourceWordIndicesBeingConsidered = []
		targetWordIndicesBeingConsidered = []

		# print "source Word Already Aligned ", srcWordAlreadyAligned
		# print "target Wod Already Aligned ", tarWordAlreadyAligned
		for i in srcWordIndices:
			if i in srcWordAlreadyAligned or srcLemmas[i-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
				continue
			for j in tarWordIndices:

				if j in tarWordAlreadyAligned or tarLemmas[j-1] in stopwords + punctuations + ['\'s', '\'d', '\'ll']:
					# print "inside if lemma ", tarLemmas[j-1]

					continue

				# print "tar lemaa ", tarLemmas[j-1]
				wordSimilarities[(i,j)] = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
								srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
										self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
									 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))

				sourceWordIndicesBeingConsidered.append(i)
				targetWordIndicesBeingConsidered.append(j)
				# print "***** Neighborhood *********************"
				# print "sourceWordIndicesBeingConsidered ", sourceWordIndicesBeingConsidered
				# print "target Word Indices being consider ", targetWordIndicesBeingConsidered
				# print "***** Neighborhood *********************"
				# print "source ", sourceSent
				# print "target ", targetSent
				# print "*****************************************"
				# print " src word index ", i
				# print "tar word index ", j
				# textual neighborhood wordSimilarities
				sourceNeighborhood = self.util.findNeighborhoodSimilarities(sourceSent, i, 3, 3)
				targetNeighborhood = self.util.findNeighborhoodSimilarities(targetSent, j, 3, 3)
				# print "***** Neighborhood *********************"
				# print "source Neighborhood ", sourceNeighborhood
				# print "target Neighborhood ", targetNeighborhood
				# print "****************************************"
				# print "length of sourc eneighborhod[0] ", len(sourceNeighborhood[0])
				evidence = 0
				for k in xrange(len(sourceNeighborhood[0])):
					for l in xrange(len(targetNeighborhood[0])):
						if (sourceNeighborhood[1][k] not in stopwords + punctuations) and \
						    ((sourceNeighborhood[0][k], targetNeighborhood[0][l]) in existingalignments or \
						    		(self.word_similarity.computeWordSimilarityScore(sourceNeighborhood[1][k], \
						    			'none', targetNeighborhood[1][l], 'none') >= ppdbSim)):

						    # print "source neighborhood[1][k] ", sourceNeighborhood[1][k]
						    # print "source neighborhood[0][k] ", sourceNeighborhood[0][k]
						    # print "target Neighborhood[0][l] ", targetNeighborhood[0][l]
						    # print "targetNeighborhood[1][l] ", targetNeighborhood[1][l]
						    # print "evidence ", self.word_similarity.computeWordSimilarityScore(sourceNeighborhood[1][k], 'none', targetNeighborhood[1][l], 'none')
						    evidence += self.word_similarity.computeWordSimilarityScore(sourceNeighborhood[1][k], \
						    			'none', targetNeighborhood[1][l], 'none')
				# print "evidence ", evidence
				textualNeighborhoodSimilarities[(i, j)] = evidence
		numOfUnalignedWordsInSource = len(sourceWordIndicesBeingConsidered)
		# print "num Of Unaligned Words In Source ", numOfUnalignedWordsInSource
		# print "tecutal nieghborhood similarity ", textualNeighborhoodSimilarities
		# print "sourceWordIndicesBeingConsidered ", sourceWordIndicesBeingConsidered
		# print "targetWordIndicesBeingConsidered ", targetWordIndicesBeingConsidered
		# now align: find the best alignment in each iteration of the following loop and include in alignments if good enough
		
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = self.computeBestAlignment(numOfUnalignedWordsInSource, sourceWordIndicesBeingConsidered,\
								targetWordIndicesBeingConsidered, wordSimilarities, textualNeighborhoodSimilarities, srcLemmas,  \
								 existingalignments, srcWordAlreadyAligned,\
								tarWordAlreadyAligned)


		return existingalignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Input: wordIndices(srcWordIndices/tarWordIndices) depends upon whether we check sourceWords
				in targetWords, or other way 
			Words(srcWordIndices/tarWordIndices) 
			srcWordAlreadyAligned, alignments, tarWordAlreadyAligned,
			source: source/target
			flag: true, then we check sourceWords in targetWords,
					else we check targetWords in sourceWords
			we align hyphen words again to make sure that there are no missing ones(here 
						we handle hyphen words that are unigram( while we aligned hyphen words
							for first time that include bigram, trigram, etcetera))
			Example: if sourceSent contains word "well-desgined"
					and targetSent contains word "designed" (we consider them as similar)
	Returns: aligned hyphen Words(alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)
	'''

	
	def alignHyphenWordsUnigram(self, wordIndices, Words, source, srcWordAlreadyAligned, alignments,
							tarWordAlreadyAligned, flag):
		

		for i in wordIndices:
			if flag:
				# print "first if statement source"
				if i in srcWordAlreadyAligned:
					continue
			else:
				# print "i in target word ", tarWordAlreadyAligned
				if i in tarWordAlreadyAligned:
					# print "in target word"
					continue

			if '-' in Words[i-1] and Words[i-1] != '-':
				tokens = Words[i-1].split('-')
				#if flag true(means we check source words in target Words)

				if flag:
					commonNeighboringWords = self.util.get_commonNeighboringWords(tokens, self.targetWords)

				else:
					commonNeighboringWords = self.util.get_commonNeighboringWords(self.sourceWords, tokens)

				for pairs in commonNeighboringWords:

					#we check for source words
					if flag:
						#source[pairs[1][0]][3] gives us target word
						if len(pairs[0]) == 1 and source[pairs[1][0]][3] not in stopwords:
							for j in pairs[1]:
								if [i, j+1] not in alignments and j+1 not in tarWordAlreadyAligned:
									alignments.append([i, j+1])
									srcWordAlreadyAligned.append(i)
									tarWordAlreadyAligned.append(j+1)

					#we check for target words
					else:

						if len(pairs[0]) == 1 and source[pairs[0][0]][3] not in stopwords:
							for j in pairs[0]:
								# print "[j+1, i ]", [j+1, i]
								# print "[j+1, i] not in alignments", [j+1, i] not in alignments
								# print "j+1 not in srcWordAlreadyAligned ", j+1 not in srcWordAlreadyAligned
								if [j+1, i] not in alignments and j+1 not in srcWordAlreadyAligned:
									alignments.append([j+1, i])
									srcWordAlreadyAligned.append(j+1)
									tarWordAlreadyAligned.append(i)

		return alignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Here we compare relation of parent and children for sourceparent with targetparent
	and childparent with targetparent
	'''


	def alignDependencyNeighborhood(self, sourceSent, targetSent, srcWordIndices, tarWordIndices,\
								 srcWords, tarWords, srcLemmas,\
				 				tarLemmas,  srcPosTags, tarPosTags, srcDParse, tarDParse, existingalignments, 
				 				srcWordAlreadyAligned, tarWordAlreadyAligned):

		wordSimilarities = {}
		dependencyNeighborhoodSimilarities = {}
		sourceWordIndicesBeingConsidered = []
		targetWordIndicesBeingConsidered = []
		# sentence stop words cannot have dependencies therefore we filter them
		# print "source word Indices ", srcWordIndices
		# print "target word indices ", tarWordIndices
		for i in srcWordIndices:
			#only consider stop words in source words
			if i in srcWordAlreadyAligned or srcLemmas[i-1] not in stopwords:
				continue
			# print "src lemma ", srcLemmas[i-1]
			for j in tarWordIndices:
				#only consider stop words in target words
				if j in tarWordAlreadyAligned or tarLemmas[j-1] not in stopwords:
					continue

				# print "j targetWordIndices ", j
				# print "tar lemaa ", tarLemmas[j-1]
				if (srcLemmas[i-1] != tarLemmas[j-1]) and (self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
								srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1])< ppdbSim ):
					continue

				wordSimilarities[(i,j)] = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
					srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
							self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
						 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
				# print "word Similarities ", wordSimilarities

				sourceWordIndicesBeingConsidered.append(i)
				targetWordIndicesBeingConsidered.append(j)
				# print "***************************************"
				# print "source D Parse ", srcDParse
				# print " i ", i
				# print "src Words [i-1] ", srcWords[i-1]

				sourceWordParents = self.util.findParents(srcDParse, i, srcWords[i-1])
				sourceWordChildren = self.util.findChildren(srcDParse, i, srcWords[i-1])
				
				# print "sourceWordParents ", sourceWordParents
				# print "sourceWordChildren", sourceWordChildren
				# print "************************************"
				# print "target D Parse ", tarDParse
				# print " j ", j
				# print "tar Words [j-1] ", tarWords[j-1]
				targetWordParents = self.util.findParents(tarDParse, j, tarWords[j-1])
				targetWordChildren = self.util.findChildren(tarDParse, j, tarWords[j-1])

				# print "targetWordParents", targetWordParents
				# print "targetWordChildren", targetWordChildren
				# print "***************************************"

				# print "exising alignments ", existingalignments
				evidence = 0
				for k in sourceWordParents:
					for l in targetWordParents:
						# print "k[0] l[0] parents", k[0], l[0]
						if [k[0], l[0]] in existingalignments:
							evidence += 1

				for k in sourceWordChildren:
					for l in targetWordChildren:
						if [k[0], l[0]] in existingalignments:
							evidence += 1
				# print "i ", i
				# print "j ", j
				# print "evidence ", evidence

				dependencyNeighborhoodSimilarities[(i, j)] = evidence

		numOfUnalignedWordsInSource = len(sourceWordIndicesBeingConsidered)
		# print "dependency Neighborhood ", dependencyNeighborhoodSimilarities
		# alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = self.computeBestAlignment(numOfUnalignedWordsInSource, sourceWordIndicesBeingConsidered,\
		# 						targetWordIndicesBeingConsidered, wordSimilarities, dependencyNeighborhoodSimilarities, srcLemmas,  \
		# 						 existingalignments, srcWordAlreadyAligned,\
		# 						tarWordAlreadyAligned)

		for i in xrange(numOfUnalignedWordsInSource):
			
			highestWeightedSim = 0
			bestWordSim = 0
			bestSourceIndex = -1
			bestTargetIndex = -1

			for i in sourceWordIndicesBeingConsidered:
				for j in targetWordIndicesBeingConsidered:
					 	
					if (i,j) not in wordSimilarities:
						continue
					# print "in word similarity ", (i,j)
					theta2 = 1 - theta1

					if theta1*wordSimilarities[(i, j)] + theta2*dependencyNeighborhoodSimilarities[(i, j)] > highestWeightedSim:
						highestWeightedSim = theta1*wordSimilarities[(i, j)] + theta2*dependencyNeighborhoodSimilarities[(i, j)]
						bestSourceIndex = i
						bestTargetIndex = j
						bestWordSim = wordSimilarities[(i, j)]
						bestTextNeighborhoodSim = dependencyNeighborhoodSimilarities[(i, j)]

			if bestWordSim>=ppdbSim and bestTextNeighborhoodSim > 0 and [bestSourceIndex, bestTargetIndex] not in existingalignments:
				existingalignments.append([bestSourceIndex, bestTargetIndex])
				srcWordAlreadyAligned.append(bestSourceIndex)
				tarWordAlreadyAligned.append(bestTargetIndex)
				# print "existing alignments ", existingalignments
			if bestSourceIndex in sourceWordIndicesBeingConsidered:
				sourceWordIndicesBeingConsidered.remove(bestSourceIndex)
			if bestTargetIndex in targetWordIndicesBeingConsidered:
				targetWordIndicesBeingConsidered.remove(bestTargetIndex)

		return existingalignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	Align textual neighborhood punctuations and stop words
	'''


	def  alignTextualNeighborhoodPuncStopWords(self, srcWordIndices, \
									tarWordIndices, srcWords, tarWords, srcLemmas,\
				 					tarLemmas,  srcPosTags, tarPosTags, existingalignments, 
				 					srcWordAlreadyAligned, tarWordAlreadyAligned):


		wordSimilarities = {}
		textualNeighborhoodSimilarities = {}
		sourceWordIndicesBeingConsidered = []
		targetWordIndicesBeingConsidered = []
		for i in srcWordIndices:

			if i in srcWordAlreadyAligned or (srcLemmas[i-1] not in stopwords \
									+ punctuations + ['\'s', '\'d', '\'ll']):
				continue

			for j in tarWordIndices:
				if j in tarWordAlreadyAligned or (tarLemmas[j-1] not in stopwords \
											+ punctuations + ['\'s', '\'d', '\'ll']):
					continue

				if self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1], srcPosTags[i-1],\
												tarLemmas[j-1], tarPosTags[j-1]) < ppdbSim:
					continue

				wordSimilarities[(i,j)] = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
					srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
							self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
						 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))

				sourceWordIndicesBeingConsidered.append(i)
				targetWordIndicesBeingConsidered.append(j)

				evidence = 0
				# check if word before punctuation/stop words is aligned
				if [i-1, j-1] in existingalignments:
					evidence += 1
				# check if word after punctuation/stop words is aligned
				if [i+1, j+1] in existingalignments:
					evidence += 1

				try:
					textualNeighborhoodSimilarities[(i, j)] = evidence
				except ZeroDivisionError:
					textualNeighborhoodSimilarities[(i, j)] = 0
				# print "	"
		numOfUnalignedWordsInSource = len(sourceWordIndicesBeingConsidered)

		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
						self.computeBestAlignment(numOfUnalignedWordsInSource, \
						sourceWordIndicesBeingConsidered,\
						targetWordIndicesBeingConsidered, wordSimilarities, \
						textualNeighborhoodSimilarities, srcLemmas,  \
						existingalignments, srcWordAlreadyAligned,\
						tarWordAlreadyAligned, flag = False)

		return alignments, srcWordAlreadyAligned, tarWordAlreadyAligned


	'''
	This is auxillary function used in textual neighborhood similarities 
	& dependency neighborhood similarities for stop words
	'''


	def computeBestAlignment(self, numOfUnalignedWordsInSource, sourceWordIndicesBeingConsidered,\
								targetWordIndicesBeingConsidered, wordSimilarities, \
								NeighborhoodSimilarities, srcLemmas, existingalignments, srcWordAlreadyAligned,\
								tarWordAlreadyAligned, flag = True):


		for i in xrange(numOfUnalignedWordsInSource):
			
			highestWeightedSim = 0
			bestWordSim = 0
			bestSourceIndex = -1
			bestTargetIndex = -1

			for i in sourceWordIndicesBeingConsidered:
				if i in srcWordAlreadyAligned:
					continue
				# print "i ", i
				for j in targetWordIndicesBeingConsidered:
					if j in tarWordAlreadyAligned:
						continue
					# print "j ", j
					# align only that are 	
					if (i,j) not in wordSimilarities:
						continue
					# print "in word similarity ", (i,j)
					theta2 = 1 - theta1

					if theta1*wordSimilarities[(i, j)] + theta2*NeighborhoodSimilarities[(i, j)] > highestWeightedSim:
						highestWeightedSim = theta1*wordSimilarities[(i, j)] + theta2*NeighborhoodSimilarities[(i, j)]
						bestSourceIndex = i
						bestTargetIndex = j
						bestWordSim = wordSimilarities[(i, j)]
						bestTextNeighborhoodSim = NeighborhoodSimilarities[(i, j)]
			if flag:
						
				if bestWordSim>=ppdbSim and [bestSourceIndex, bestTargetIndex] not in existingalignments:
					if srcLemmas[bestSourceIndex-1] not in stopwords:
						existingalignments.append([bestSourceIndex, bestTargetIndex])
						srcWordAlreadyAligned.append(bestSourceIndex)
						tarWordAlreadyAligned.append(bestTargetIndex)
						# print "existing alignments ", existingalignments

			# else executes when alignTextualNeighborhoodPuncutationsAndStopWords calls			
			else:
				if bestWordSim>=ppdbSim and bestTextNeighborhoodSim > 0 and \
						[bestSourceIndex, bestTargetIndex] not in existingalignments:
						existingalignments.append([bestSourceIndex, bestTargetIndex])
						srcWordAlreadyAligned.append(bestSourceIndex)
						tarWordAlreadyAligned.append(bestTargetIndex)

			if bestSourceIndex in sourceWordIndicesBeingConsidered:
				sourceWordIndicesBeingConsidered.remove(bestSourceIndex)
			if bestTargetIndex in targetWordIndicesBeingConsidered:
				targetWordIndicesBeingConsidered.remove(bestTargetIndex)

		return existingalignments, srcWordAlreadyAligned, tarWordAlreadyAligned