# Towards a Standard Upper Ontology (SUMO)

**Authors:** Ian Niles, Adam Pease
**Published:** FOIS-2001 (2nd International Conference on Formal Ontology
in Information Systems), Ogunquit, Maine, October 2001

## What it is

Introduces the Suggested Upper Merged Ontology (SUMO) — a large, open-source
upper ontology created by merging several existing ontologies under IEEE
sponsorship. SUMO provides a formal, axiomatic foundation for general-purpose
knowledge representation.

### Key features

- **~25,000 terms** in the full SUMO + MILO (mid-level ontology)
- **~80,000 axioms** in first-order logic (SUO-KIF format)
- Top-level distinctions:
  - **Entity** → Physical / Abstract
  - **Physical** → Object / Process
  - **Object** → SelfConnectedObject / Collection
  - **Process** → IntentionalProcess / Motion / InternalChange / ...
- **Mereology** (part-whole relations) formally axiomatized
- **Temporal** and **spatial** relations built in
- Mapped to WordNet synsets (~100,000 mappings)

### Comparison to OpenCyc

Both are large upper ontologies, but:
- SUMO is fully open-source with formal axioms in SUO-KIF
- OpenCyc was partially open but discontinued in 2017
- SUMO has explicit WordNet mappings (useful for connecting to lexical data)
- SUMO's mereology is more formally developed

## Relevance

Complements OpenCyc (already in references) for fleshing out the
hyperdiagram ontology:

- **Entity-to-Entity labels** — SUMO's mereology provides formal
  definitions for part-of, component, member, piece, etc.
- **Entity-to-Value labels** — SUMO's physical quantity hierarchy
  (length, mass, temperature, etc.) is formally axiomatized
- **WordNet mappings** — connect SUMO concepts to the lexical layer,
  helping choose which label name to assign for a given word
- **Process taxonomy** — SUMO's process hierarchy is an alternative
  organization of event-type labels alongside CLib's action clusters

## Access

- **SUMO home:** https://www.ontologyportal.org/
- **GitHub:** https://github.com/ontologyportal/sumo
- **FOIS-2001 paper:** https://dl.acm.org/doi/10.1145/505168.505170
- **Sigma browser:** https://sigma.ontologyportal.org:8443/sigma/
- **WordNet mappings:** included in the SUMO GitHub repository
