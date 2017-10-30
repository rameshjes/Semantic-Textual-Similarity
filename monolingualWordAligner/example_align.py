#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from wordAligner import *

sentence1 = "UAE is one of biggest country in the world."
sentence2 = "Many people are living in United Arab Emirates"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	print "Words alignment ", processing.align_sentences(sentence1,sentence2)
