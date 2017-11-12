import nltk 
from nltkUtil import *
from util import *
from config import *
from wordsim import *

class Aligner:

	def __init__(self):
		self.text_nor = Text_processing()
		self.util = Util()
		self.word_similarity = WordSimilarity()

	def align_sentences(self,sentence1,sentence2):

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
		
		# # print "myWordAlignments ", myWordAlignments
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
	7. Align Adjective
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

		print "**************************"
		print "alignments in neighboring words ", alignments
		print "source word aligned ", srcWordAlreadyAligned
		print "target word aligned ", tarWordAlreadyAligned
		print "**************************"
		
		#3. align Hyphenated words
		# print "source Hyphenated Words"
		checkSourceWordsInTarget = True # check if Source Words have any hyphen words
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
							self.align_hyphenWords(self.sourceWordIndices, sourceWords,\
									srcWordAlreadyAligned, alignments,\
									tarWordAlreadyAligned, checkSourceWordsInTarget)

		print "********************************************"
		print "alignments in hyphen source", alignments
		print "source word aligned ", srcWordAlreadyAligned
		print "target word aligned ", tarWordAlreadyAligned
		print "********************************************"
		print "target Hyphenated Words"
		
		checkSourceWordsInTarget = False  # check if target Words have any hyphen words
		alignments, tarWordAlreadyAligned, srcWordAlreadyAligned = \
							self.align_hyphenWords(self.targetWordIndices, targetWords, tarWordAlreadyAligned, alignments, \
									srcWordAlreadyAligned,checkSourceWordsInTarget)
		
		print "********************************************"
		print "alignments in hyphen words target", alignments
		print "source word aligned ", srcWordAlreadyAligned
		print "target word aligned ", tarWordAlreadyAligned
		print "********************************************"

		#4. align named entities
		neAlignments = self.align_namedEntities(sourceSent, targetSent, sourceParseResult, \
			    targetParseResult, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned) 
		print "***********************************"
		print "neAlignments ", neAlignments
		print "***********************************"
		
		for item in neAlignments:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])

		print "********************************************"
		print "alignments in neighboring words NE", alignments
		print "source word aligned ", srcWordAlreadyAligned
		print "target word aligned ", tarWordAlreadyAligned
		print "********************************************"

		sourceDependencyParse = self.util.dependencyTreeWithOffSets(sourceParseResult)
		targetDependencyParse = self.util.dependencyTreeWithOffSets(targetParseResult)

		#. Align Main Verbs
		aligned_verbs = self.alignMainVerbs(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)
		print "**********************************"
		print "aligned Verbs ", aligned_verbs
		print "**********************************"
		
		for item in aligned_verbs:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])



		aligned_nouns = self.alignNouns(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		print "aligned nouns ", aligned_nouns

		for item in aligned_nouns:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])
 
		aligned_adjectives = self.alignAdjective(self.sourceWordIndices, self.targetWordIndices, sourceWords, targetWords,
										self.sourceLemmas, self.targetLemmas, self.sourcePosTags, self.targetPosTags,
											sourceDependencyParse, targetDependencyParse, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)

		print "aligned adjectives ", aligned_adjectives

		for item in aligned_adjectives:
			if item not in alignments:
				alignments.append(item)
				if item[0] not in srcWordAlreadyAligned:
					srcWordAlreadyAligned.append(item[0])
				if item[1] not in tarWordAlreadyAligned:
					tarWordAlreadyAligned.append(item[1])

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


	def align_hyphenWords(self, wordIndices, Words, srcWordAlreadyAligned, alignments,
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
					# print "second if statement source"
					commonNeighboringWords = self.util.get_commonNeighboringWords(tokens, self.targetWords)

				else:
					# print" second else statemetn"
					commonNeighboringWords = self.util.get_commonNeighboringWords(tokens,self.sourceWords)

				for pairs in commonNeighboringWords:

					if len(pairs[0]) > 1:
						# print "third if statement source"
						for j in pairs[1]:
							if flag:

								if[i, j+1] not in alignments:

									alignments.append([i,j+1])
									srcWordAlreadyAligned.append(i)
									tarWordAlreadyAligned.append(j+1)
							else:
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


	def align_namedEntities(self, sourceSent, targetSent, sourceParseResult, targetParseResult, 
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

		#construct the two matrices in following loop
		for i in srcWordIndices:
			
			if i in srcWordAlreadyAligned or srcPosTags[i-1][0].lower() != 'v' or srcLemmas[i-1] in stopwords:
				continue

			numberofMainVerbsInSource += 1

			for j in tarWordIndices:

				if j in tarWordAlreadyAligned or tarPosTags[j-1][0].lower() != 'v' or tarLemmas[j-1] in stopwords:
					continue
				getSimilarityScore = max(self.word_similarity.computeWordSimilarityScore(srcWords[i-1], \
						srcPosTags[i-1], tarWords[j-1], tarPosTags[j-1]), \
								self.word_similarity.computeWordSimilarityScore(srcLemmas[i-1],\
							 	srcPosTags[i-1], tarLemmas[j-1], tarPosTags[j-1]))
				if getSimilarityScore < ppdbSim:
					
					# print "score less than 0.9 "
					continue
			
				wordSimilarity[(i,j)] = getSimilarityScore

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
		# print "number of Main Verbs in Source ", numberofMainVerbsInSource
		# print "evidence Count Matrix ", evidenceCountMatrix
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
						# item[0] and item[1] != 0 so that we should not store Root-0
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
	to reduce repeatation of code in align nouns and align adjective
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