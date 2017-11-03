import nltk 
from nltkUtil import *
from util import *
from config import *

class Aligner:

	def __init__(self):
		self.text_nor = Text_processing()

	def align_sentences(self,sentence1,sentence2):

		sentence1ParseResult = self.text_nor.parser(sentence1)
		# print "sentence1 parse ", sentence1ParseResult 
		# print ""
		sentence2ParseResult = self.text_nor.parser(sentence2)

		sentence1LemmasAndPosTags = self.text_nor.combine_lemmaAndPosTags(sentence1ParseResult)
		# print "sentce1 ", sentence1LemmasAndPosTags
		sentence2LemmasAndPosTags = self.text_nor.combine_lemmaAndPosTags(sentence2ParseResult)

		self.sourceWordIndices = [i+1 for i in xrange(len(sentence1LemmasAndPosTags))]
		self.targetWordIndices = [i+1 for i in xrange(len(sentence2LemmasAndPosTags))]

		self.sourceWords = [item[2] for item in sentence1LemmasAndPosTags]
		self.targetWords = [item[2] for item in sentence2LemmasAndPosTags]

		self.sourceLemmas = [item[3] for item in sentence1LemmasAndPosTags]
		self.targetLemmas = [item[3] for item in sentence2LemmasAndPosTags]

		self.sourcePosTags = [item[4] for item in sentence1LemmasAndPosTags]
		self.targetPosTags = [item[4] for item in sentence2LemmasAndPosTags] 

		myWordAlignments = self.alignWords(sentence1LemmasAndPosTags, sentence2LemmasAndPosTags, \
							sentence1ParseResult, sentence2ParseResult)
		
		align = []
		for i in myWordAlignments:
			align.append([self.sourceWords[i[0]-1], self.targetWords[i[1]-1] ])
		# print "align words ", align

		return align

	'''
	sourceSent and targetSent is list of:
        [[character begin offset, character end offset], word index, word, lemma, pos tag]
	sourceParseResult and targetParseResult is list of:
		Parse Tree(Constituency tree), Text, Dependencies, words(NE, CharacOffsetEn, CharOffsetBeg,
			POS, Lemma)
	1. Align the punctuations first
	2. Align named entities
	'''


	def alignWords(self,sourceSent, targetSent, sourceParseResult, targetParseResult):


		alignments = []
		srcWordAlreadyAligned = [] #sourceWordAlreadyAligned
		tarWordAlreadyAligned = [] #TargetWordAlreadyAligned

		# align the punctuations
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = \
			self.align_punctuations(self.sourceWords,self.targetWords, \
					alignments, srcWordAlreadyAligned, tarWordAlreadyAligned,sourceSent,targetSent)
		# align named entities
		neAlignments = self.align_namedEntities(sourceSent, targetSent, \
			sourceParseResult, targetParseResult, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned)
		
		for item in neAlignments:
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


	def align_punctuations(self,sourceWords, targetWords, alignments, \
				srcWordAlreadyAligned, tarWordAlreadyAligned, sourceSent, targetSent):
		
		global punctuations

		# if last word of source sentence is . or ! and last of target sent is . or ! or both are equal
		if (sourceWords[len(sourceSent)-1] in ['.','!'] and targetWords[len(targetSent)-1]\
				 in ['.','!']) or (sourceWords[len(sourceSent)-1]==targetWords[len(targetSent)-1]):
			
			alignments.append([len(sourceSent), len(targetSent)])
			srcWordAlreadyAligned.append(len(sourceSent))
			tarWordAlreadyAligned.append(len(targetSent))
		# or if second last of source sent. is . or ! and last word of target sent is . or ! then append too
		elif (sourceWords[len(sourceSent)-2] in ['.', '!'] and targetWords[len(targetSent)-1] in ['.', '!']):
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
	Input: source Sentence, target sentence, 
	       sourceParseResult, targetParseResult,
	       ExistingAlignments, srcWordAlreadyAligned, tarWordAlreadyAligner
	       1. Learn Named Entities
	       2. Align all full matches
	       3. Align Acronyms
	       4. Align subset matches
	Returns: list of alignments
	'''


	def align_namedEntities(self, sourceSent, targetSent, sourceParseResult, \
				targetParseResult, existingAlignments, srcWordAlreadyAligned, tarWordAlreadyAligned):
		
		
		sourceNE = self.text_nor.get_ner(sourceParseResult)
		targetNE = self.text_nor.get_ner(targetParseResult)

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
				
				if isSublist(item[2], jtem[2]):
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
							if [item[1][k], jtem[1][l]] not in alignment_list  and \
									targetSent[jtem[1][l]-1][2] not in sourceWords  and \
										item[2][k] not in punctuations and jtem[2][l] not in punctuations:
								
								alignment_list.append([item[1][k], jtem[1][l]])
				 # else find if the second is a part of the first
				elif isSublist(jtem[2], item[2]):
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
							if [item[1][l], jtem[1][k]] not in alignment_list  and \
									sourceSent[item[1][k]-1][2] not in targetWords  and \
										item[2][l] not in punctuations and jtem[2][k] not in punctuations:
								
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
					print "matched"
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