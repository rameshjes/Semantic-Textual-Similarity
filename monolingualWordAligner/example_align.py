#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wordAligner import *

sentence1 = "Ramesh and rubanraj are doing Masters in Autonomus System. Camel and cow gives milk "
sentence2 = "Rubanraj and ramesh are doing their research and development project. Cow and camel produces milk"

print "sentence1 = ", sentence1
print "sentence2 = ", sentence2

if __name__ == '__main__':

	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)
