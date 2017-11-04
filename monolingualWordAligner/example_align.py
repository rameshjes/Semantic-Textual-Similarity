#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "UAE is really well-designed country in  the world. US is powerful country"
sentence2 = "Really well designed is United Arab Emirates. But United States is more populated"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
