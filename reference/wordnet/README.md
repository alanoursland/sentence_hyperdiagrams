# WordNet

**Maintainer:** Princeton University, Cognitive Science Laboratory
**Current version:** 3.1

## What it is

A large lexical database of English. Nouns, verbs, adjectives, and adverbs
are grouped into **synsets** (sets of cognitive synonyms), each expressing a
distinct concept. Synsets are linked by conceptual-semantic and lexical
relations:

- **Hypernymy/Hyponymy** — is-a (dog is-a animal)
- **Meronymy/Holonymy** — part-of (wheel part-of car)
- **Antonymy** — opposites
- **Entailment** — verb entailment (snoring entails sleeping)
- **Troponymy** — manner-of for verbs (limping is a manner of walking)

## Relevance to CLib / hyperdiagrams

CLib used WordNet synsets as one source for naming and organizing components.
For the hyperdiagram project, WordNet provides:

- A canonical vocabulary for label names
- Taxonomic structure (hypernymy) for organizing the label ontology
- Part-whole relations (meronymy) as a source for entity-entity labels

## Access

- **Website:** https://wordnet.princeton.edu/
- **Download:** https://wordnet.princeton.edu/download
- **NLTK:** `nltk.corpus.wordnet` (included in NLTK data)
- **Online browser:** http://wordnetweb.princeton.edu/perl/webwn

## Python access

```python
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
```
