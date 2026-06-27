# The Knowledge Required to Interpret Noun Compounds

**Authors:** James Fan, Ken Barker, Bruce Porter
**Published:** IJCAI'03 (Eighteenth International Joint Conference on AI), 2003

## Summary

An empirical investigation of what knowledge is needed to interpret noun
compounds (e.g., "concrete floor" = floor *made of* concrete; "gymnasium
floor" = floor *region of* a gymnasium). The paper concludes that the **top
levels of a hierarchical ontology** are most important — detailed knowledge
of specific nouns is less critical.

### Key ideas

- Noun compound interpretation is framed as finding a **path of semantic
  relations** between two concepts in a knowledge base (not selecting from
  a fixed list of categories).
- Uses a breadth-first search algorithm on the KB, starting from each
  constituent noun's concept and searching along semantic relation arcs.
- The paper uses ~50 thematic/semantic relations (agent, object, has-part,
  location, material, etc.).
- Tested on three diverse domains: cell biology (224 compounds), small engine
  repair (294 compounds), Sun Sparcstation manual (224 compounds).
- **Ablation study**: successively removes ontology levels and measures impact.
  Top two levels contribute most; lower levels diminish to nil. This means
  a compact, well-structured upper ontology is sufficient.

### Key result

Interpreting noun compounds does **not** require detailed knowledge of the
specific nouns — only that they are correctly placed in a taxonomy with
the right upper-level ontological distinctions and axioms (Entity vs. Event,
part-whole relations, etc.).

## Relevance

Relevant to the hyperdiagram project in two ways:

1. **Ontology design**: Confirms that a small, well-structured set of
   upper-level label names (relations) provides broad coverage. The
   hyperdiagram label ontology can prioritize depth at the top of the
   hierarchy rather than enumerating domain-specific labels.

2. **Noun compound patterns**: Noun compounds are a common syntactic
   structure where the relationship between tokens is implicit. The ~50
   semantic relations used here are candidates for label names that capture
   these implicit relationships (e.g., modifier-head relations within NPs).

## Access

- **PDF:** http://www.cs.utexas.edu/users/mfkb/papers/ijcai03-nn.pdf

Run `download.py` to fetch the PDF locally.
