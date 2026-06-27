# A Unified Knowledge Based Approach for Sense Disambiguation and Semantic Role Labeling

**Authors:** Peter Z. Yeh, Bruce Porter, Ken Barker
**Published:** AAAI'06, 2006

## Summary

Presents a unified approach that performs word sense disambiguation (WSD) and
semantic role labeling (SRL) simultaneously through a single process: matching
candidate semantic interpretations against background knowledge (the Component
Library, CLib) to select the best match.

### Key ideas

- Most NLU systems treat WSD and SRL as separate tasks. This paper combines
  them — performing both concurrently improves results on each.
- Given a syntactic parse (e.g., subject/object/prepositional relations), the
  system generates **candidate semantic interpretations** by looking up all
  possible CLib concepts for each constituent and all possible CLib relations
  for each syntactic relationship.
- A **semantic matcher** (based on conceptual graphs) scores each candidate
  interpretation against the ontology using taxonomic distance and ~200
  transformation rules.
- Transformation rules are derived from the domain-independent upper ontology
  and encode patterns like part descension (acting on a whole also acts on its
  parts) and transitivity of causality.

### The Component Library (CLib)

The paper relies on CLib, a domain-independent upper ontology with:
- ~80 semantic relations
- ~500 generic concepts (events and entities)
- Over 2500 domain-specific concepts built by composition

### Semantic relations taxonomy (three categories)

1. **Event-Entity relations** — agent, instrument, object, destination, etc.
   (inspired by Fillmore's case roles)
2. **Entity-Entity relations** — has-part, possesses, material, etc.
3. **Event-Event relations** — caused-by, prevents, enables, etc.

Each semantic relation includes information about its **syntactic realization**
— e.g., "agent" can surface as a "by" prepositional phrase.

### Results

Evaluated on 196 sentences from chemistry, pollution prevention, employee
safety, and nuclear deterrence domains:
- WSD: 86-94% precision, 85-92% recall (vs. 74-77% baseline)
- SRL: 85-92% precision, 82-89% recall (vs. 42% baseline)

## Relevance

Direct source for the hyperdiagram label ontology:
- The **semantic relations** (agent, instrument, object, caused-by, etc.)
  map to label names at the semantic level.
- The **syntactic realization** data (which prepositions/structures surface
  which semantic roles) bridges syntax-level and semantics-level labels.
- The three-category relation taxonomy (event-entity, entity-entity,
  event-event) provides organizing structure for the label ontology.

## Access

- **PDF:** http://www.cs.utexas.edu/users/mfkb/papers/aaai06-unified-approach.pdf
- **AAAI page:** https://aaai.org/papers/aaai06-unified-approach/

Run `download.py` to fetch the PDF locally.
