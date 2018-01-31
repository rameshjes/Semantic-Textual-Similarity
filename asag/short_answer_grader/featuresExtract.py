from __future__ import division

import numpy as np
import scipy
from ..word_align import wordAligner, nltkUtil, config, spacyUtil
import asag.Resources
from scipy import spatial
import nltk
from nltk.corpus import stopwords
import re 
import sys

class Features:


	def __init__(self, flag):

		self.flag = flag

		self.word_aligner = wordAligner.Aligner(self.flag)
		if self.flag == 'nltk':
			self.text_normalization = nltkUtil.TextProcessing()
		if self.flag == 'spacy':
			# print "here"
			self.text_normalization = spacyUtil.Text_processing_spacy()
			# print "called"
		self.embeddings = {}

		self.punctuations = ['(','-lrb-', '\n','.',',','-','?','!',';','_',':','{','}','[','/',']','...','"','\'',')', '-rrb-']
		self.stopwords = stopwords.words('english')

	'''
	Load embeddings
	Returns: dictionary
	'''

	def load_embeddings(self, FileName):


		
		file = open(FileName,'r')
		i = 0
		print  "Loading word embeddings first time"
		for line in file:
			# print line

			tokens = line.split('\t')

			#since each line's last token content '\n'
			# we need to remove that
			tokens[-1] = tokens[-1].strip()

			#each line has 400 tokens
			for i in xrange(1, len(tokens)):
				tokens[i] = float(tokens[i])


			self.embeddings[tokens[0]] = tokens[1:-1]
		print  "finished"
		return self.embeddings


	'''
	Input: vectors(srcSent/tarSent embeddings)
	Returns: list
	'''


	def vectorSum(self, vectors):

		
		n = len(vectors)  # vectors contains embedding score for each lemma word in sent
		d = len(vectors[0]) #len of embeddings(usually 400 for each word)

		s = [] # length is same as number of word embeddings for each word(400)
		for i in xrange(d):
			s.append(0)  
		s = np.array(s)

		for vec in vectors:
			# adding zero vector with word vector
			s = s + np.array(vec) 

		return list(s)



	'''
	Input: two vectors
	Returns: cosine similarity between two vectors 
	'''


	def computeCosineSimilarity(self, vec1, vec2):

		
		return 1 - spatial.distance.cosine(vec1, vec2)


	'''
	Input: sentences; srcSent = ref_answer and tarSent = student_answer
	Returns: sim_score, parse result, and coverage
	'''


	def sts_alignment(self, srcSent, tarSent, \
				parse_results = None, sentence_for_demoting = None):


		print "teacher original ", srcSent
		print "student original ", tarSent

		if parse_results == None:
			sentence1ParseResult = self.text_normalization.parser(srcSent)
			sentence2ParseResult = self.text_normalization.parser(tarSent)
			parse_results = []
			parse_results.append(sentence1ParseResult)
			parse_results.append(sentence2ParseResult)

		else:
			sentence1ParseResult = parse_results[0]
			sentence2ParseResult = parse_results[1]

		srcSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence1ParseResult)
		tarSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence2ParseResult)

		srcLemmatize = [item[3] for item in srcSentLemmasAndPosTags]
		tarLemmatize = [item[3] for item in tarSentLemmasAndPosTags]
		#sentence_for_demoting takes input question
		lemmas_to_be_demoted = []

		if sentence_for_demoting != None:

			if len(parse_results) == 2:
				#compute parse Text of question
				sentence_for_demoting_parseResult = \
							self.text_normalization.parser(sentence_for_demoting)
				parse_results.append(sentence_for_demoting_parseResult)
			else:
				#means there is already parsed of question, so we take last index
				sentence_for_demoting_parseResult = parse_results[2]

			sentence_for_demoting_LemmasAndPosTags = \
						self.text_normalization.combine_lemmaAndPosTags(sentence_for_demoting_parseResult)

			# make sure not stop words and punctuations
			lemmas_to_be_demoted = \
					[item[3].lower() for item in sentence_for_demoting_LemmasAndPosTags \
						if item[3].lower() not in self.stopwords + self.punctuations]

		alignments = self.word_aligner.align_sentences(srcSent, tarSent, sentence1ParseResult,
													sentence2ParseResult)[0]
		# print "alignment by word align ", alignments

		src_contentLemmas = \
					[item for item in srcLemmatize \
						if item.lower() not in self.stopwords + self.punctuations]

		tar_contentLemmas = \
					[item for item in tarLemmatize \
						if item.lower() not in self.stopwords + self.punctuations]

		# print "source content lemmas ", src_contentLemmas
		# print "target content Lemmas ", tar_contentLemmas

		if src_contentLemmas == [] or tar_contentLemmas == []:
			# we return parse_results because we use that for question demoting
			return (0, 0, parse_results)

		src_aligned_content_word_indexes = \
			[item[0] for item in alignments if \
				srcLemmatize[item[0]-1].lower() not in \
                                self.stopwords + self.punctuations + lemmas_to_be_demoted]

		tar_aligned_content_word_indexes = \
			[item[1] for item in alignments if \
				tarLemmatize[item[1]-1].lower() not in \
		                        self.stopwords + self.punctuations + lemmas_to_be_demoted]

		
		sim_score = (len(src_aligned_content_word_indexes) + len(tar_aligned_content_word_indexes) )/ \
									(len(src_contentLemmas) + len(tar_contentLemmas)) 
        
		# To avoid penalizaing long student responses that still contain correct answer
		# we consider proportion of aligned content words only in student response
		# that's why we need as coverage of reference answer's content by student response
		coverage = len(src_aligned_content_word_indexes) / len(src_contentLemmas)
 
		# print "sim score ", sim_score
		# print "coverage ", coverage

		return (sim_score, coverage, parse_results)


	'''
	Returns: Cosine similarity between sentences
	'''


	def sts_cvm(self, srcSent, tarSent, \
				parse_results, sentence_for_demoting = None):

		if self.embeddings == {}:
			print "loading embeddings "
			self.embeddings = self.load_embeddings('asag/Resources/EN-wform.w.5.cbow.neg10.400.subsmpl.txt')
			print "done" 
		
		sentence1ParseResult = parse_results[0]
		sentence2ParseResult = parse_results[1]

		srcSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence1ParseResult)
		tarSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence2ParseResult)

		srcLemmatize = [item[3].lower() for item in srcSentLemmasAndPosTags]
		tarLemmatize = [item[3].lower() for item in tarSentLemmasAndPosTags]
		#sentence_for_demoting takes input question
		lemmas_to_be_demoted = []

		if sentence_for_demoting != None:


			sentence_for_demoting_parseResult = parse_results[2]

			sentence_for_demoting_LemmasAndPosTags = \
						self.text_normalization.combine_lemmaAndPosTags(sentence_for_demoting_parseResult)

			# make sure not stop words and punctuations
			lemmas_to_be_demoted = \
					[item[3].lower() for item in sentence_for_demoting_LemmasAndPosTags \
						if item[3].lower() not in self.stopwords + self.punctuations]

		if srcLemmatize == tarLemmatize:
			return 1

		sentence1_content_lemma_embeddings = []
		for lemma in srcLemmatize:
			if lemma.lower() in self.stopwords + self.punctuations + lemmas_to_be_demoted:
				continue
			if lemma.lower() in self.embeddings:
				sentence1_content_lemma_embeddings.append(self.embeddings[lemma.lower()])
	
		sentence2_content_lemma_embeddings = []
		for lemma in tarLemmatize:
			if lemma.lower() in self.stopwords + self.punctuations + lemmas_to_be_demoted:
				continue
			if lemma.lower() in self.embeddings:
				sentence2_content_lemma_embeddings.append(self.embeddings[lemma.lower()])


		if sentence1_content_lemma_embeddings == sentence2_content_lemma_embeddings:
			return 1
		elif sentence1_content_lemma_embeddings == [] or sentence2_content_lemma_embeddings == []:
			return 0

		srcSent_embedding = self.vectorSum(sentence1_content_lemma_embeddings)
		tarSent_embedding = self.vectorSum(sentence2_content_lemma_embeddings)


		return self.computeCosineSimilarity(srcSent_embedding, tarSent_embedding)


	def ComputeLengthRatio(self, srcSent, tarSent, parse_results):

		sentence1ParseResult = parse_results[0]
		sentence2ParseResult = parse_results[1]

		srcSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence1ParseResult)
		tarSentLemmasAndPosTags = self.text_normalization.combine_lemmaAndPosTags(sentence2ParseResult)

		srcLemmatize = [item[3].lower() for item in srcSentLemmasAndPosTags]
		tarLemmatize = [item[3].lower() for item in tarSentLemmasAndPosTags]

		src_contentLemmas = \
					[item for item in srcLemmatize \
						if item.lower() not in self.stopwords + self.punctuations]

		tar_contentLemmas = \
					[item for item in tarLemmatize \
						if item.lower() not in self.stopwords + self.punctuations]

		if tar_contentLemmas == []:
			return len(srcLemmatize) / len(tarLemmatize)

		return len(src_contentLemmas) / len(tar_contentLemmas)