# A Library of Generic Concepts for Composing Knowledge Bases

**Authors:** Ken Barker, Bruce Porter, Peter Clark
**Published:** K-CAP'01 (First International Conference on Knowledge Capture), 2001

## Summary

Describes the **Component Library (CLib)**, a hierarchy of reusable,
composable, domain-independent knowledge units designed so that domain experts
(not knowledge engineers) can build knowledge bases by instantiating and
composing generic components from a small library.

### Key ideas

- The library is deliberately small (~few hundred components) to be learnable
  by non-experts. Coverage is achieved through **composition** rather than
  enumeration.
- Components are labeled with intuitive English words, drawing from
  dictionaries, thesauri, and linguistic resources (Longman defining
  vocabulary, WordNet synsets, Roget's Thesaurus headwords).
- Each component contains axioms (not just a taxonomy) — the meaning of the
  component, how it interacts with others, preconditions, effects, etc.

### Ontology structure

**Events** — divided into entities (things that *are*) and events (things
that *happen*). Events split into actions and states.

**15 top-level action clusters** (Table 1 in the paper):

| Action             | Description                            | Example subclasses              |
|---------------------|----------------------------------------|---------------------------------|
| ADD                 | add a part to an entity                | --                              |
| REMOVE              | remove a part from an entity           | --                              |
| COMMUNICATE         | transfer information                   | INTERPRET, ENCODE, REPLY        |
| CREATE              | bring a new entity into existence      | COPY, PRODUCE, PUT-TOGETHER     |
| BREAK               | cause inability to be used as instrument | DESTROY, RUIN, TAKE-APART     |
| REPAIR              | undo a BREAK                           | --                              |
| MOVE                | change location of an entity           | CARRY, ENTER, SLIDE             |
| TRANSFER            | change possessor of an entity          | DONATE, LOSE, TAKE              |
| MAKE-CONTACT        | make entities touch                    | ATTACH, COLLIDE                 |
| BREAK-CONTACT       | make touching entities not touch       | DETACH, DISPERSE                |
| MAKE-ACCESSIBLE     | allow participation in events          | ADMIT, EXPOSE, RELEASE          |
| MAKE-INACCESSIBLE   | prevent participation in events        | BLOCK, CONCEAL, CONFINE         |
| PERCEIVE            | discern using senses                   | IDENTIFY, TOUCH                 |
| SHAPE               | change shape of an entity              | FLATTEN, FOLD                   |
| ORIENT              | change orientation of an entity        | FACE, ROTATE, TURN              |

**States** — temporally stable events: BE-BROKEN, BE-CLOSED, BE-RUINED,
BE-CONFINED, BE-TOUCHING, BE-ATTACHED-TO, etc.

**Roles** — temporally unstable entities defined by participation in events
(e.g., EMPLOYEE is a role; PERSON is independent of events).

**~80 relations** organized into:
- **Event-Entity relations** (case roles): agent, donor, instrument, object,
  recipient, result, etc.
- **Entity-Entity relations**: content, has-part, location, material,
  possesses, region, etc.
- **Event-Event relations**: causes, defeats, enables, entails, inhibits,
  by-means-of, prevents, resulting-state, subevent
- **Role relations**: entity-to-role, role-to-event

**~25 properties**: age, area, capacity, color, length, shape, size, smell,
wetness, etc.

### Composition

Composition connects component instances via the restricted relation/property
language. Axioms on the relations enable inference beyond what's explicitly
stated. Example: composing MOVE with a destination that is outside a container
triggers reclassification to EXIT, inheriting axioms about portals, prior
containment, etc.

## Relevance

This is the **most directly relevant** paper for the hyperdiagram label
ontology. It provides:
- A complete, linguistically-motivated inventory of ~500 generic concepts
- A curated set of ~80 semantic relations (label name candidates)
- ~25 properties (for adjectival/modifier labels)
- An explicit taxonomy of actions, states, entities, and roles
- A composition mechanism that parallels how hyperdiagram labels chain
  together

The entire CLib was browsable online at
http://www.cs.utexas.edu/users/mfkb/RKF/tree/ (may be archived).

## Access

- **PDF:** http://www.cs.utexas.edu/users/mfkb/papers/kcap01.pdf

Run `download.py` to fetch the PDF locally.
