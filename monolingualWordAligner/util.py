from config import *

class Util:


	'''
	Input: A and B; list of words	       
	Check If A is subset of B
	'''


	def isSublist(self, A, B):

		flag = True
		for item in A:
			if item not in B:
				flag = False
				break
		return flag


	'''
	Input: source and target Words
	Return: list of commonNeighboringWords
	'''


	def get_commonNeighboringWords(self, sourceWords, targetWords, 
							convertToLowerCase=True):


		commonNeighboringWords = []
		a = []
		b = []
		# If lowerCase true, then convert all word in lowercase
		if convertToLowerCase:
			for i in (sourceWords):
				a.append(i.lower())
			for j in (targetWords):
				b.append(j.lower())

		swapped = False

		if (len(a) > len(b)):
			temp = a
			a = b 
			b = temp
			swapped = True

		maximumSize = len(a)
		# print "maximum size (a)", maximumSize
		# print "length of b ", len(b) 

		for size in xrange(maximumSize, 0, -1):

			AIndices = [i for i in xrange(0, len(a)-size+1)] 
			BIndices = [j for j in xrange(0, len(b)-size+1)] 

			for i in AIndices: 
				for j in BIndices:

					# check if a contiguous superset has already been inserted; 
					#don't insert this one in that case
					if a[i:i+size] == b[j:j+size]:
						alreadyInserted = False
						# take indices of equal words
						currentAIndices = [item for item in xrange(i,i+size)]
						currentBIndices = [item for item in xrange(j,j+size)]
		
						for k in commonNeighboringWords:
							# print "k ", k[0]
							if self.isSublist(currentAIndices, k[0]) and self.isSublist(currentBIndices, k[1]):
								alreadyInserted = True
								break

						if not alreadyInserted:
							commonNeighboringWords.append([currentAIndices,currentBIndices])
		if swapped:
			for item in commonNeighboringWords:
				temp = item[0]
				item[0] = item[1]
				item[1] = temp
		return commonNeighboringWords 


	'''
	Input : parseResult of source/Target sentence
	returns: list contains:
		 (rel, parent{charStartOffset, charEndOffset, wordNumber}, 
       	childs{charStartOffset, charEndOffset, wordNumber})
	'''


	def dependencyTreeWithOffSets(self,parseResult):


		dependencies = parseResult['dependencies']
		combine_dependencies = []
		res = []
		words_param = parseResult['words']
		combine_wordsList = []

		if(len(dependencies)) > 1:
			for sublist in dependencies:
				combine_dependencies +=  sublist
		else:
			combine_dependencies = dependencies[0]

		if (len(words_param) > 1):
			for sublist in words_param:
				combine_wordsList += sublist 
		else:
			combine_wordsList = words_param[0]

		for dep in combine_dependencies:

			newItem  = []
			newItem.append(dep[0]) 

			parent = dep[1][0:dep[1].rindex("-")]
			
			wordNumber = dep[1][dep[1].rindex("-") + 1:]
			# print "word Number ", wordNumber

			if wordNumber.isdigit() == False:
				continue
			
			parent += '{' + combine_wordsList[int(wordNumber)-1][1]['CharacterOffsetBegin'] + \
				' ' + combine_wordsList[int(wordNumber)-1][1]['CharacterOffsetEnd'] + ' ' + wordNumber + '}'
			newItem.append(parent)

			child = dep[2][0:dep[2].rindex("-")]
			wordNumber = dep[2][dep[2].rindex("-")+1:]
			if wordNumber.isdigit() == False:
				continue
			child += '{' + combine_wordsList[int(wordNumber)-1][1]['CharacterOffsetBegin'] + \
				' ' + combine_wordsList[int(wordNumber)-1][1]['CharacterOffsetEnd'] + ' ' + wordNumber + '}'	
			newItem.append(child)

			res.append(newItem)

		return res


	'''
	Input: dependencies, wordIndex, word
	return : list(parents with Relation) : [[WordNumberOf parent, parent, relation]]
	'''


	def findParents(self, dependencies, wordIndex, word):


		wordsWithIndices = ( (int(item[2].split('{')[1].split('}')[0].split(' ')[2]) ,\
						item[2].split('{')[0])for item in dependencies)
		wordsWithIndices = list(set(wordsWithIndices))
		wordsWithIndices = sorted(wordsWithIndices, key=lambda item: item[0])

		wordIndexPresentInList = False
		for i in wordsWithIndices:
			if i[0] == wordIndex:
				# print "came here ", i[0], wordIndex
				wordIndexPresentInList = True
				break
				
		parentsWithRelation = []

		if wordIndexPresentInList:
			# dependencies : [['root', 'Root{85 86 0}', 'country{28 35 5}']
			for j in dependencies:

				currentIndex = int(j[2].split('{')[1].split('}')[0].split(' ')[2])

				if currentIndex == wordIndex:
					# store [WordNumberOf parent, parent, relation]
					# [0,Root, root]
					parentsWithRelation.append([int(j[1].split('{')[1].split('}')[0].split(' ')[2]),\
							 j[1].split('{')[0], j[0]])

		# need to check for this section
		else:

			nextIndex = 0
			for i in xrange(len(wordsWithIndices)):
				if wordsWithIndices[i][0] > wordIndex:
					nextIndex = wordsWithIndices[i][0]
					break

			if nextIndex == 0:
				return []

			for i in xrange(len(dependencies)):
				if int(dependencies[i][2].split('{')[1].split('}')[0].split(' ')[2]) == nextIndex:
					pos = i
					break

			for i in xrange(pos, len(dependencies)):
				if '_' in dependencies[i][0] and word in dependencies[i][0]:
					 parent = [int(dependencies[i][1].split('{')[1].split('}')[0].split(' ')[2]), \
					 			dependencies[i][1].split('{')[0], dependencies[i][0]]
					 parentsWithRelation.append(parent)
					 break

		return parentsWithRelation


		'''
		Input: dependencies; (rel, parent{charStartOffset, charEndOffset, wordNumber}, 
       						childs{charStartOffset, charEndOffset, wordNumber})

       		   wordIndex and word
       	output: list of children 
		'''


	def findChildren(self, dependencies, wordIndex, word):


		wordsWithIndices = ( (int(item[2].split('{')[1].split('}')[0].split(' ')[2]) ,\
					item[2].split('{')[0])for item in dependencies)
		wordsWithIndices = list(set(wordsWithIndices))
		wordsWithIndices = sorted(wordsWithIndices, key=lambda item: item[0])
		childrenWithRelation = []
		
		wordIndexPresentInList = False
		for i in wordsWithIndices:
			if i[0] == wordIndex:
				wordIndexPresentInList = True
				break

		if wordIndexPresentInList:
			for j in dependencies:
				currentIndex = int(j[1].split('{')[1].split('}')[0].split(' ')[2])
				if currentIndex == wordIndex:
					childrenWithRelation.append([int(j[2].split('{')[1].split('}')[0].split(' ')[2]),\
						 j[2].split('{')[0], j[0]])

		# find the closest following word index which is in the list
		else:
			nextIndex = 0

			for i in xrange(len(wordsWithIndices)):
				if wordsWithIndices[i][0] > wordIndex:
					nextIndex = wordsWithIndices[i][0]
					break

			if nextIndex == 0:
				return []

			for i in xrange(len(dependencies)):
				if int(dependencies[i][2].split('{')[1].split('}')[0].split(' ')[2]) == nextIndex:
					pos = i
					break

			for i in xrange(pos, len(dependencies)):
				if '_' in dependencies[i][0] and word in dependencies[i][0]:
					 child = [int(dependencies[i][2].split('{')[1].split('}')[0].split(' ')[2]), \
					 			dependencies[i][2].split('{')[0], dependencies[i][0]]
					 childrenWithRelation.append(child)
					 break

		return childrenWithRelation


	'''
	Returns words withn (3,3) neighborhood window
	'''

	def findNeighborhoodSimilarities(self, sentenceDetails, wordIndex, leftSpan, rightSpan):


		lemmas = []
		wordIndices = []
		sentenceLen = len(sentenceDetails)
		startWordIndex = max(1, wordIndex - rightSpan)
		endWordIndex = min(sentenceLen, wordIndex+rightSpan)
		for item in sentenceDetails[startWordIndex-1:wordIndex-1]:
			if item[3] not in stopwords + punctuations:
				lemmas.append(item[3])
				wordIndices.append(item[1])
		for item in sentenceDetails[wordIndex:endWordIndex]:
			if item[3] not in stopwords + punctuations:
				lemmas.append(item[3])
				wordIndices.append(item[1])

		return [wordIndices, lemmas, wordIndex-startWordIndex, endWordIndex-wordIndex]
