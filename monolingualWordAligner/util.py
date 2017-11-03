
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

			# print "sourceWordsIndices ", AIndices
			# print "targetWordIndices ", BIndices
			# print ""
			for i in AIndices: 
				for j in BIndices:

					# check if a contiguous superset has already been inserted; 
					#don't insert this one in that case
					if a[i:i+size] == b[j:j+size]:
						# print " equal ", a[i:i+size]
						# print "equal ", b[j:j+size]
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