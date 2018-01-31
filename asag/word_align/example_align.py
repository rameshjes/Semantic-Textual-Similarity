#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from wordAligner import *

sentence1 = "The array of characters has a null character \0 at the end of the array to signify the array's end.  The string does not have this."

sentence2 = "The strings declared using an array of characters have a null element added at the end of the array."

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':
	# flag = sys.argv[1] # for command, 0 for file, 1,.. for type
	# print flag
	processing = Aligner()
	print processing.align_sentences(sentence1,sentence2)[0]
