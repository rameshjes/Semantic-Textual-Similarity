# Semantic Textual Similarity using Natural Language Processing(NLP)

## Abstract 

Semantic textual similarity computes the equivalence of two sentences on the basis of its conceptual similarity. It is widely used in natural languages processing tasks such as essay scoring, machine translation, text classification, information extraction, and question answering. This project focuses on one of the applications of semantic textual similarity known as automatic short answer grading (ASAG). It assigns a grade to a response provided by a student by comparing with one or more model answers. In particular, we selected one of the state-of-the-art short answer grading approaches that use Stanford CoreNLP library, and we used the same approach with the help of two open source libraries; Natural Language ToolKit (NLTK) and Spacy. For evaluation, Texas dataset and an in-house benchmarking ASAG dataset based on Mathematics for Robotics and Control (MRC) course were considered. Performances among all three libraries were evaluated using Pearson correlation coefficient, root mean square error (RMSE), and the runtime. Results based on Texas dataset showed that Stanford CoreNLP library has better Pearson correlation coefficient(0.66) and lowest RMSE(0.85) than NLTK and Spacy libraries. While using MRC dataset, all 3 libraries showed the comparative results on evaluated metrics.

## Contents of Repository

This repository contains:

        Exercises related to textual similarity using NLTK and SPACY libraries that can help for short answer grading
        
        Comparison of spell corrector approaches using:
                        - Spell corrector using Ngrams,Jaccard coefficient and Minimum edit distance
                        - Spell corrector using Minimum Edit Distance(MED)

        Create jupyter notebooks for each student from Mohler data set for short questions and answers

        Create instructor version of assignments using nbgrader

        Create student version of assignments using nbgrader
        
        Wiki contains theoretically concepts: https://github.com/rameshjesswani/Semantic-Textual-Similarity/wiki
        
        Word Aligner using NLTK and Spacy libraries
        
        ASAG based Sultan et al. (2016) approach using NLTK And Spacy libraries


## Guidelines for Monolingual Word Aligner

It can used as individual module. For more usage, check here: [Word Aligner using NLTK and Spacy](https://github.com/rameshjesswani/Semantic-Textual-Similarity/tree/master/monolingualWordAligner)

```
Install nltk library(procedure given below)
Setup Stanford Parser, NER, PosTagger(link to setup in nltk given below)

```

## Guidelines for ASAG 

Details about Asag can be found here: [ASAG](https://github.com/rameshjesswani/Semantic-Textual-Similarity/tree/master/asag)


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

Install SPACY(code works with version 2.0.12) library

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

# General NLP Pipeline

![General Nlp pipeline](https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/nlp_basics/GeneralNlpPipeline.jpg)

# Bibtex

```
@unpublished{[RnD]Kumar,
	Authors = {Ramesh Kumar},
	Month = {January},
	Note = {WS17
	H-BRS - Evaluation of Semantic Textual Similarity Approaches for Automatic Short Answer Grading
Ploeger, Nair supervising},
	Title = {Evaluation of Semantic Textual Similarity Approaches for Automatic Short Answer Grading},
	Year = {2017/18}}
```
