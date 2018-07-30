# Semantic Textual Similarity using Natural Language Processing(NLP)

We re-implement automatic short answer grader using Sultan et al.(2016)[Fast and Easy Short Answer Grading with High Accuracy](http://www.aclweb.org/anthology/N16-1123) approach:

        We re-implement using two NLP libararies; NLTK and Spacy
        
        Compared results of Sultan et al.(2016) approach implmemented using Stanford library, NLTK and Spacy:

        We evaluate performance of all three libraries on Texas Dataset and in-house created dataset; Mathematics for Robotics and Control(MRC)

## Guidelines for Setting ASAG

```
Install python 2.7 
Install nltk library(procedure given below)
Setup Stanford Parser, NER, PosTagger(link to setup in nltk given below)
Install Spacy library
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

To use Stanford Parser, NER, PosTagger in NLTK check files:

```
https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordParser_setup.txt

https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordNERTagger_setup.txt

https://github.com/rameshjesswani/Semantic-Textual-Similarity/blob/master/monolingualWordAligner/stanfordPOSTagger_setup.txt

```

#### List of dependencies

```
pandas
numpy
scipy
sklearn
pickle


```

#### Setup

To run the asag pipeline
```
python -m asag.short_answer_grader.trainAndApplyGrader nltk   #To train and apply grader using NLTK
python -m asag.short_answer_grader.trainAndApplyGrader spacy #To train and grader using Spacy
```
