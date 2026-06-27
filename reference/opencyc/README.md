# OpenCyc

**Original developer:** Cycorp (Doug Lenat)
**Status:** OpenCyc was discontinued in 2017; partially archived

## What it is

The open-source subset of the Cyc knowledge base — one of the longest-running
AI projects (started 1984). OpenCyc provided:

- An upper ontology of ~47,000 concepts
- ~306,000 assertions (facts and rules)
- Common-sense knowledge organized into **microtheories**

The full Cyc system distinguishes:
- **Things** vs. **Intangible Things**
- **Events** vs. **Static Situations**
- Detailed ontological categories (SpatialThing, Agent, InformationBearingObject, etc.)

## Relevance to CLib / hyperdiagrams

CLib drew from OpenCyc's upper ontology for organizational structure. For
the hyperdiagram project:

- OpenCyc's top-level distinctions (Event vs. Entity, Tangible vs.
  Intangible, Agent vs. Non-agent) provide a framework for categorizing
  label names
- The microtheory mechanism (context-dependent assertions) is relevant to
  how the same label might have different semantics in different contexts

## Access

- **Original site (archived):** https://web.archive.org/web/2017/https://www.cyc.com/opencyc/
- **GitHub mirror:** https://github.com/asanchez75/opencyc
- **ConceptNet** incorporates some OpenCyc data: https://conceptnet.io/
- The full Cyc KB is a commercial product (ResearchCyc available for
  academic use)
