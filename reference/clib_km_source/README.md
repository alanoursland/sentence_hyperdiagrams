# Component Library — KM Source

**Developer:** Bruce Porter's group, University of Texas at Austin
**Language:** KM (Knowledge Machine)
**License:** LGPL 2.1 (in the distributed files) / Simplified BSD (on the download page)

## What it is

The full source code of the Component Library (CLib) — 933 KM files defining
domain-independent concepts (events, entities, roles, properties), their
axioms, slot definitions, and composition rules. This is the machine-readable
ontology behind all the CLib papers.

### Contents

Two distributions are available:

- **rkf-clib** — the full library with components organized into directories:
  - `components/core/` — 933 domain-independent KM files (the general ontology)
  - `components/specs/` — HTML specifications and documentation
  - `components/bsp/` — military domain examples
  - `components/science/` — chemistry/biology domain examples
  - `components/office/` — office/business domain examples
  - `components/tools/` — utility scripts
  - `clib-index-data.lisp` — index metadata

- **rkf-clib-one** — single-file version (`rkf-clib-one.km`) containing the
  entire core library concatenated into one KM file

### Local path

The KM source is in this project at:

    component_library/rkf-clib/
    component_library/rkf-clib-one/

These are gitignored (too large to check in). Obtain them from the download
page below.

## Relevance

This is the **primary ontological source** for the hyperdiagram label names.
The core KM files define:

- Event types (Action, Move, Transfer, Create, Break, Communicate, ...)
- Entity types (Tangible-Entity, Agent, Place, Information, ...)
- Roles (Agent-Role, Instrument-Role, ...)
- Semantic relations / slots (agent, causes, has-part, ...) — see the
  `clib_slot_dictionary` reference for the full inventory
- Properties (size, color, duration, ...)
- Axioms (pre-conditions, post-conditions, participating entities)

## Access

- **Download page:** https://www.cs.utexas.edu/~mfkb/RKF/tree/download-clib.html
  (requires accepting license agreement, then leads to releases)
- **CLib browser:** https://www.cs.utexas.edu/~mfkb/RKF/tree/
- **CLib home:** https://www.cs.utexas.edu/~mfkb/RKF/clib.html
- **Slot dictionary:** https://www.cs.utexas.edu/~mfkb/RKF/tree/components/specs/slotdictionary.html
- **KM language:** https://www.cs.utexas.edu/~mfkb/km/
