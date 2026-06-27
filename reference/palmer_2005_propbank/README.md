# The Proposition Bank: An Annotated Corpus of Semantic Roles

**Authors:** Martha Palmer, Daniel Gildea, Paul Kingsbury
**Published:** Computational Linguistics, 31(1):71-106, March 2005

## What it is

PropBank adds a layer of predicate-argument (semantic role) annotation on
top of the Penn Treebank's syntactic trees. For each verb in the corpus,
PropBank labels its arguments with standardized role labels.

### Key ideas

- **Numbered arguments** — each verb has a **frameset** defining its core
  arguments:
  - `Arg0` — proto-agent (doer, causer)
  - `Arg1` — proto-patient/theme (undergoer, thing affected)
  - `Arg2` — typically beneficiary, instrument, attribute, or end state
  - `Arg3`, `Arg4` — verb-specific roles
- **Modifier arguments** (ArgM) — adjunct roles consistent across all verbs:
  - `ArgM-LOC` — location
  - `ArgM-TMP` — temporal
  - `ArgM-MNR` — manner
  - `ArgM-DIR` — direction
  - `ArgM-CAU` — cause
  - `ArgM-PRP` — purpose
  - `ArgM-ADV` — adverbial
  - `ArgM-NEG` — negation
  - `ArgM-MOD` — modal
  - `ArgM-DIS` — discourse connective
  - `ArgM-EXT` — extent
- **Framesets** are verb-sense-specific — "run a company" and "run a race"
  have different framesets with different Arg mappings
- Annotated over the Wall Street Journal section of the Penn Treebank
  (~113,000 annotated predicates)

## Relevance

PropBank provides the **standardized argument labels** that bridge VerbNet's
verb classes to actual annotated text:

- The `Arg0`/`Arg1` system maps to CLib's agent/object distinction
- The `ArgM-*` modifiers map to CLib's event-to-entity and event-to-value
  slots (location, duration, instrument, etc.)
- PropBank framesets define **which semantic roles each verb takes** — this
  is the verb-specific data the hyperdiagram annotator needs
- AMR inherits its predicate-argument structure directly from PropBank

## Access

- **Paper PDF:** https://www.cs.rochester.edu/~gildea/palmer-propbank-cl.pdf
- **MIT Press:** https://direct.mit.edu/coli/article/31/1/71/1861/
- **PropBank data:** https://propbank.github.io/
- **PropBank frames:** https://github.com/propbank/propbank-frames
- **Unified Verb Index:** https://uvi.colorado.edu/

Run `download.py` to fetch the paper.
