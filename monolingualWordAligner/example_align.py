#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "Ramesh and rubanraj are doing Masters in Autonomus System. He is very innocent guy. Susan is really clever."
sentence2 = "They are too blameless people. Rubanraj and ramesh are doing their research and development project. The doctor is very intelligent."

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
