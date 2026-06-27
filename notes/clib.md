# The Component Library (CLib)

The sentence hyperdiagram project builds much of its semantic label ontology
on the Component Library (CLib) developed by Bruce Porter's group at UT Austin.

**Source page:** https://www.cs.utexas.edu/~mfkb/RKF/clib.html

## What CLib is

A library of reusable, domain-independent knowledge components. Each component
represents an **entity**, **event**, **role**, or **property**. Complex
representations are built by instantiating and composing these components.

Components are written in the KM formal language and include:
- Specifications of participating entities
- Pre-conditions and post-conditions
- Axioms enabling simulation and question-answering

## Semantic relations dictionary

CLib compiles a dictionary of semantic relations in five categories:

1. **Event-Event** — e.g., causes, enables
2. **Event-Entity** — e.g., agent, instrument
3. **Entity-Event** — e.g., capability
4. **Entity-Entity** — e.g., contents, parts
5. **Properties** of events and entities — e.g., duration, size

These relations are based on Ken Barker's thorough analysis of case roles
and other relations in his dissertation.

## How this maps to hyperdiagram labels

| CLib concept   | Hyperdiagram equivalent                        |
|----------------|------------------------------------------------|
| Component      | Label name (the `name` field in the tuple)     |
| Composition    | Labels referencing other labels as children    |
| Semantic relation | Label names at the semantic level           |
| Property       | Label names for modifier/attribute annotations |
| Entity/Event   | Top-level ontological distinction for labels   |

## Inspirational sources

CLib drew from existing ontological and lexical resources. These are also
relevant sources for the hyperdiagram label ontology:

- **WordNet** — lexical database of English; synsets, hypernymy, meronymy
- **FrameNet** — frame semantics; semantic frames and frame elements
- **VerbNet** — verb classes; syntactic-semantic mappings for verb behavior
- **Roget's Thesaurus** — headwords used for component naming
- **Longman Dictionary of Contemporary English** — defining vocabulary
  (~2000 words used to define all other words) used for component naming
- **OpenCyc** — upper ontology; common-sense knowledge categories

See the `reference/` directory for details on each of these sources.

## Key papers

- Clark & Porter 1997 — "Building Concept Representations from Reusable
  Components" (AAAI'97) — introduces the compositional approach
- Barker, Porter & Clark 2001 — "A Library of Generic Concepts for Composing
  Knowledge Bases" (K-CAP'01) — describes the full CLib inventory
- Ken Barker's dissertation — thorough analysis of case roles and semantic
  relations that underpins the CLib relation dictionary
