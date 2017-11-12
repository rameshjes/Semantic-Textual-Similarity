#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "They are washing clothes. I heard some noise. He ran quickly. I work on Sunday"
sentence2 = "I have washed my clothes. They run very slowly. I am hearing songs. I am working tomorrow"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
