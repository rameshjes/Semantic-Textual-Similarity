from wordAligner import *

def test_align_sentences():
	aligner = Aligner()
	result = aligner.align_sentences("UAE is one of biggest country in the world.","Many people are living in United Arab Emirates")
	assert result == [['UAE', 'United'], ['UAE', 'Arab'], ['UAE', 'Emirates']]
	