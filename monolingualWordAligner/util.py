
'''
Input: A and B; list of words
       
Check If A is subset of B
'''

def isSublist(A,B):

	flag = True

	for item in A:
		if item not in B:
			flag = False
			break

	return flag