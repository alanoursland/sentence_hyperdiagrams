# VerbNet

**Maintainer:** University of Colorado Boulder (Martha Palmer's group)
**Based on:** Beth Levin's verb classification

## What it is

A hierarchical, domain-independent verb lexicon that maps verb classes to
their syntactic and semantic behavior. Each verb class specifies:

- **Thematic roles** — Agent, Patient, Theme, Instrument, etc.
- **Selectional restrictions** — type constraints on roles (animate, concrete)
- **Syntactic frames** — the argument structures the verb participates in
- **Semantic predicates** — formal decomposition of meaning using primitives
  like `cause`, `motion`, `transfer`, `contact`

Contains ~300 verb classes covering ~6,000 verbs.

## Relevance to CLib / hyperdiagrams

CLib drew from VerbNet's verb classes and syntactic-semantic mappings. For
the hyperdiagram project, VerbNet provides:

- **Thematic roles** as semantic-level label name candidates
- **Syntactic frames** showing how semantic roles surface as syntactic
  positions — the bridge between syntax-level and semantic-level labels
- **Verb class hierarchy** for organizing event-type label names
- **Semantic predicates** (cause, motion, transfer) that parallel CLib's
  top-level action clusters

## Access

- **Website:** https://verbs.colorado.edu/verbnet/
- **GitHub:** https://github.com/cu-clear/verbnet
- **Unified Verb Index:** https://uvi.colorado.edu/
- **NLTK:** `nltk.corpus.verbnet`

## Python access

```python
import nltk
nltk.download('verbnet3')
from nltk.corpus import verbnet as vn
```
