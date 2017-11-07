# Semantic Textual Similarity using Natural Language Processing(NLP)

This repository contains:

        Exercises related to textual similarity using NLTK and SPACY libraries that can help for short answer grading
        
        Comparison of spell corrector approaches using:
                        - Spell corrector using Ngrams,Jaccard coefficient and Minimum edit distance
                        - Spell corrector using Minimum Edit Distance(MED)

        Create jupyter notebooks for each student from Mohler data set for short questions and answers

        Create instructor version of assignments using nbgrader

        Create student version of assignments using nbgrader
        
        Wiki contains theoretically concepts: https://github.com/rameshjesswani/Semantic-Textual-Similarity/wiki
        
        Currently working on monolingual word-aligner in NLTK 


## Guidelines for Monolingual Word Aligner

```
Install nltk library(procedure given below)
Setup Stanford Parser, NER, PosTagger(link to setup in nltk given below)


```
### Installation

#### NLTK requires Python versions 2.7, 3.4, or 3.5

Install NLTK library

```
sudo pip install -U nltk
```

Install packages of NLTK

```
import nltk
nltk.download()
```

#### SPACY is compatible with 64-bit CPYTHON 2.6+/3.3+ and runs on Unix/Linux, macOS/OS X and WINDOWS

Install SPACY library

```
pip install -U spacy
```

After spacy installation you need to download a Language  model

```
python -m spacy download en
```

#### Nbgrader Installation

```
pip install nbgrader
```

if you are using Anaconda:

```
conda install jupyter
conda install -c conda-forge nbgrader
```

To install nbgrader extensions:

```
jupyter nbextension install --user-prefix --py nbgrader --overwrite
jupyter nbextension enable --user-prefix --py nbgrader
jupyter serverextension enable --user-prefix --py nbgrader
```

For more docs about nbgrader:

```
http://nbgrader.readthedocs.io/en/stable/user_guide/installation.html
```

To use Stanford Parser, NER, PosTagger in NLTK check files:

```
https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordParser_setup.txt

https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordNERTagger_setup.txt

https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordPOSTagger_setup.txt

```

# MindMap

![Mind map](https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/nlp_basics/NaturalLanguageProcessing_mindmap.png)
