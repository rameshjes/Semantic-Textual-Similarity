from wordAligner import *

sentence1 = "United States is one of biggest country in the world. Four people are dead from a collisions."
sentence2 = "Second sentence need to be in written form."
# sentence1 = "United State of America is one of biggest country in the world"
print "sentence1 =",sentence1
print "sentence2 =",sentence2

# aligner(sentence1,sentence2)

if __name__ == '__main__':
	processing = Aligner()
	processing.align_sentences(sentence1,sentence2)