# The Preposition Project (TPP)

**Author:** Kenneth C. Litkowski (CL Research)
**Active:** 2002–present

## What it is

A computational linguistics project that disambiguates English prepositions
by mapping each preposition sense to its semantic role. Covers hundreds of
English prepositions with sense inventories linked to FrameNet frame elements
and other resources.

### Key ideas

- Each preposition has multiple senses, each triggering a different semantic
  relation (e.g., "with" can signal instrument, accompaniment, possession,
  manner, etc.)
- TPP maps preposition senses to **FrameNet frame elements** — directly
  connecting surface syntax to semantic roles
- Includes annotated corpora for preposition word-sense disambiguation
- Provides inheritance hierarchies showing how preposition senses relate

### Key publications

- Litkowski, K. C. (2013). "The Preposition Project Corpora." CL Research
  Technical Report 13-02.
- Litkowski, K. C. & Hargraves, O. (2006). "Coverage and Inheritance in
  The Preposition Project." Third ACL-SIGSEM Workshop on Prepositions.
- Litkowski, K. C. (2005). "The Preposition Project." Second ACL-SIGSEM
  Workshop on the Linguistic Dimensions of Prepositions.

## Relevance

Directly bridges syntax-level and semantic-level labels for prepositional
phrases. When a hyperdiagram annotator sees a preposition, TPP tells them
which semantic relation it encodes:

- "with a hammer" → instrument
- "with John" → accompaniment
- "in the garden" → location
- "in an hour" → duration
- "for Mary" → beneficiary

This is exactly the mapping the hyperdiagram label chain must capture.

## Access

- **Project page:** https://www.clres.com/prepositions.php
- **Technical report (2013):** https://www.clres.com/files/online-papers/prepwsd2013.pdf
- **ACL paper (2006):** https://aclanthology.org/W06-2106.pdf
- **SemEval-2007 task:** https://aclanthology.org/S07-1005.pdf

Run `download.py` to fetch available papers.
