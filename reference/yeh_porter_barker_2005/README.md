# Matching Utterances to Rich Knowledge Structures to Acquire a Model of the Speaker's Goal

**Authors:** Peter Z. Yeh, Bruce Porter, Ken Barker
**Published:** K-CAP'05 (Third International Conference on Knowledge Capture), 2005

## Summary

Presents a semantic matcher that bridges the representational gap between
logical forms produced by a language interpreter and semantically related
content in a rich knowledge base. The matcher uses **semantic transformation
rules** to overcome structural differences between the two representations.

### Key ideas

- Logical forms from a language interpreter mirror surface syntax too closely
  for direct use by a knowledge-based reasoner. Implicit knowledge is missing,
  multi-utterance information is fragmented, etc.
- The matcher uses two functions:
  - **EstablishModel** — matches a logical form introducing a new topic to
    concepts in the ontology, building an initial model of the speaker's goal
  - **RelateUtterance** — matches subsequent utterances to the existing goal
    model, elaborating it. Uses **bridging concepts** drawn from the ontology
    to establish indirect links between utterances.
- ~200 transformation rules (derived from a domain-independent upper ontology
  of ~500 concepts, events, roles, and ~75 relations) resolve structural
  mismatches. Example rules:
  - Part descension: acting on a whole also acts on its parts
  - Transitivity of causality

### Evaluation

Tested on 75 purchase request emails (468 utterances, 4252 words) from UT
Austin's CS department. Compared against LaSIE-II (MUC-7 system) and Overlay:
- Significantly better precision, recall, and lower overgeneration across
  all metrics (p < 0.01).

## Relevance

Demonstrates how the same ontological components handle **discourse-level**
relationships — linking utterances across sentence boundaries. This is
directly relevant to the hyperdiagram project's goal of capturing long-distance
relationships:
- **Bridging concepts** show how labels can connect structures across
  non-adjacent tokens
- The EstablishModel/RelateUtterance pattern maps to how hyperdiagram labels
  build up from local syntax to cross-sentence semantics
- The ~75 relation set is a concrete inventory of semantic label candidates

## Access

- **PDF:** http://www.cs.utexas.edu/users/mfkb/papers/kcap05-discourse.pdf

Run `download.py` to fetch the PDF locally.
