#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *
import sys

sentence1 = "Four people died in accident. Well, United Arab Emirates is one of powerful country"
sentence2 = "Seven men are dead due to collisions."

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	flag = sys.argv[1]

	processing = Aligner(flag)
	processing.align_sentences(sentence1,sentence2)
