#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "I really do care. The woman is quite pretty"
sentence2 = "He is doing really well. She looks quite beautiful"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
