import nltk 
from nltkUtil import *

class Aligner:

	def __init__(self):
		pass

	def align_sentences(self,sentence1,sentence2):

		text_nor = Text_processing()
		
		sentence1ParseResult = text_nor.parser(sentence1)
		# print "sentence1 parse ", sentence1ParseResult 
		# print ""
		sentence2ParseResult = text_nor.parser(sentence2)

		# sentence1Lemmas = text_nor.get_lemma(sentence1ParseResult)
		# print "lemmas ", sentence1Lemmas
		# print ""
		# print "sentenceLem"
		# sentence2Lemmas = text_nor.get_lemma(sentence2ParseResult)
		# print "sentence2 ", sentence2Lemmas

		# sentence1PosTags = text_nor.find_posTags(sentence1ParseResult)
		# print "pos tag ", sentence1PosTags

		# sentence2PosTags = text_nor.find_posTags(sentence2ParseResult)
		# print "pos tag2 ", sentence2PosTags

		sentence1LemmasAndPosTags = text_nor.combine_lemmaAndPosTags(sentence1ParseResult)
		sentence2LemmasAndPosTags = text_nor.combine_lemmaAndPosTags(sentence2ParseResult)

		self.sourceWordIndices = [i+1 for i in xrange(len(sentence1LemmasAndPosTags))]
		self.targetWordIndices = [i+1 for i in xrange(len(sentence2LemmasAndPosTags))]

		self.sourceWords = [item[2] for item in sentence1LemmasAndPosTags]
		self.targetWords = [item[2] for item in sentence2LemmasAndPosTags]

		self.sourceLemmas = [item[3] for item in sentence1LemmasAndPosTags]
		self.targetLemmas = [item[3] for item in sentence2LemmasAndPosTags]

		self.sourcePosTags = [item[4] for item in sentence1LemmasAndPosTags]
		self.targetPosTags = [item[4] for item in sentence2LemmasAndPosTags] 

		myWordAlignments = self.alignWords(sentence1LemmasAndPosTags, sentence2LemmasAndPosTags, sentence1ParseResult, sentence2ParseResult)


	'''
	sourceSent and targetSent is list of:
        [[character begin offset, character end offset], word index, word, lemma, pos tag]
	sourceParseResult and targetParseResult is list of:
		Parse Tree(Constituency tree), Text, Dependencies, words(NE, CharacOffsetEn, CharOffsetBeg,
			POS, Lemma)
	1. Align the punctuations first
	2. 
	'''


	def alignWords(self,sourceSent, targetSent, sourceParseResult, targetParseResult):


		alignments = []
		srcWordAlreadyAligned = [] #sourceWordAlreadyAligned
		tarWordAlreadyAligned = [] #TargetWordAlreadyAligned

		# print "source Lemma ", self.sourceLemmas
		# print "target lemma ", self.targetLemmas

		# align the punctuations
		alignments, srcWordAlreadyAligned, tarWordAlreadyAligned = self.align_punctuations(self.sourceWords,self.targetWords, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned,sourceSent,targetSent)
		print "alignments ", alignments
		print "source Wrod Already Aligned ", srcWordAlreadyAligned
		print "target word Already Aligned ", tarWordAlreadyAligned


		'''
		Align the sentence ending punctuation first
		returns: list; alignments, srcWordAlreadyAligned, tarWordAlreadyAligned
		'''


	def align_punctuations(self,sourceWords, targetWords, alignments, srcWordAlreadyAligned, tarWordAlreadyAligned, sourceSent, targetSent):
		

		# if last word of source sentence is . or ! and last of target sent is . or ! or both are equal
		if (sourceWords[len(sourceSent)-1] in ['.','!'] and targetWords[len(targetSent)-1] in ['.','!']) or (sourceWords[len(sourceSent)-1]==targetWords[len(targetSent)-1]):
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



		





