#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "I heared some noise. We are looking for a dog-friendly hotel. I am driving since few days. Four people died in accident. Well, United Arab Emirates is one of powerful country"
sentence2 = "She use to drive on weekends. Seven men are dead due to collisions. Is this hotel dog friendly? I use to hear songs. UAE is well-designed country"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
