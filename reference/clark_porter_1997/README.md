# Building Concept Representations from Reusable Components

**Authors:** Peter Clark, Bruce Porter
**Published:** AAAI'97, pages 369-376, CA: AAAI Press, 1997

## Summary

The paper addresses a key bottleneck in knowledge-based systems: building
concept representations is labor-intensive because each new concept must be
represented nearly from scratch. The authors propose a **component-based
approach** where a library of reusable, generalized representational
components can be composed to build new concept representations.

### Key ideas

- **Components** are small, reusable knowledge fragments (e.g., a "buy" event
  component captures buyer, seller, goods, money and their relationships).
  Components generalize across many specific concepts.
- **Composition** assembles components by unifying shared slots. A concept
  like "buy a dog" composes a "buy" component with a "dog" component by
  unifying the "goods" slot with the "dog" instance.
- **Articulation axioms** resolve vocabulary mismatches between independently
  authored components (e.g., mapping "goods" in a buy-component to "object"
  in a transfer-component).
- The library is organized around an ontology with ~130 components tested
  against ~360 questions, achieving ~70% coverage of representational
  requirements from those components alone.
- The approach is evaluated on the **Knowledge Entry Task** — given an
  English sentence, can the system build a formal representation using
  its component library?

### Component structure

Each component contains:
- **Participants** — the entities involved (slots)
- **Constraints** — type restrictions on participants
- **Subevents** — decomposition into sub-components
- **Relations** — connections between participants and subevents

## Relevance

This paper provides a model for building a **reusable ontology of
representational components** for sentence annotation. Key parallels to the
hyperdiagram project:

- Components are composable building blocks, analogous to how labels in the
  hyperdiagram system compose by referencing each other as children.
- The paper's ontology of event/relation types (buy, transfer, move, etc.)
  is a source for defining semantic-level label names.
- Articulation axioms address the same problem as the label `parameter`
  field — disambiguating and connecting variants of similar concepts.
- The component library spans syntax through deep semantics, matching the
  hyperdiagram project's scope.

## Access

- **AAAI PDF:** https://cdn.aaai.org/AAAI/1997/AAAI97-057.pdf
- **AAAI page:** https://aaai.org/papers/00369-AAAI97-057-building-concept-representations-from-reusable-components/
- **CiteSeerX:** https://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.51.2442

Run `download.py` to fetch the PDF locally.
