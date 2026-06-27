# CLib Slot Dictionary

**Source:** UT Austin MFKB Group (Bruce Porter's lab)
**URL:** https://www.cs.utexas.edu/~mfkb/RKF/tree/components/specs/slotdictionary.html
**Part of:** The Component Library for KM

## What it is

The complete inventory of semantic relations (slots) used in the Component
Library. This is the relation ontology that the hyperdiagram project draws
its semantic-level label names from.

## Relation categories

### Event-to-Event (13 relations)

| Slot | Inverse | Description |
|------|---------|-------------|
| causes | caused-by | Event1 causes Event2 |
| defeats | defeated-by | Action defeats State (mutually exclusive) |
| enables | enabled-by | Permits but doesn't ensure |
| inhibits | inhibited-by | Discourages but doesn't prevent |
| by-means-of | means-by-which | Event via alternative method |
| first-subevent | first-subevent-of | Initial component of composite event |
| objective | objective | Goal event of an action |
| next-event | prev-event | Immediate temporal succession |
| prevents | prevented-by | Blocks occurrence |
| resulting-state | resulting-from | Action produces resultant state |
| subevent | subevent-of | Component within larger event |
| supports | supported-by | Aids another's success |

### Event-to-Entity (21 relations)

| Slot | Inverse | Notes |
|------|---------|-------|
| agent | agent-of | Initiates/performs event |
| away-from | away-from-of | Location distinct from origin |
| base | base-of | Fixed reference entity |
| beneficiary | beneficiary-of | Gains advantage from event |
| destination | destination-of | Event ends at location |
| donor | donor-of | Dative events: releases object |
| experiencer | experiencer-of | State events: undergoes state |
| instrument | instrument-of | Used to perform event |
| location | location-of | Event occurs at place |
| object | object-of | Action events: main passive participant |
| origin | origin-of | Event begins at location |
| path | path-of | Follows spatial route |
| raw-material | raw-material-of | Consumed in event |
| recipient | recipient-of | Dative events: receives object |
| result | result-of | Action events: entity created |
| site | site-of | Specific effect location |
| substrate | substrate | Molecule converted in reaction |
| toward | toward-of | Directed toward location |

### Entity-to-Role (3 relations)

| Slot | Inverse | Description |
|------|---------|-------------|
| capability | capability-of | Entity able to fill a role |
| plays | played-by | Entity currently fills role |
| purpose | purpose-of | Entity's primary functional role |

### Role-to-Event (1 relation)

| Slot | Inverse | Description |
|------|---------|-------------|
| in-event | in-event-of | Role participant engages in event |

### Entity-to-Event (1 relation)

| Slot | Inverse | Description |
|------|---------|-------------|
| has-goal | is-goal-of | Goal of entity is that event happens |

### Entity-to-Entity (27 relations)

**Compositional:**
- has-part / is-part-of
- has-basic-functional-unit / is-basic-functional-unit-of
- has-basic-structural-unit / is-basic-structural-unit-of
- has-functional-part / is-functional-part-of
- has-structural-part / is-structural-part-of
- has-region / is-region-of
- content / content-of
- complement / complement

**Chemical/Formal:**
- chemical-formula / chemical-formula-of
- term / term-of
- information-content / information-content

**Spatial:**
- is-northwest-of / is-southeast-of
- is-southwest-of / is-northeast-of
- is-west-of / is-east-of
- location / location-of

**Material/Possession:**
- material / material-of
- possesses / is-possessed-by

**Aggregates/Sequences:**
- element / element-of
- first-element / first-element-of
- next-element / next-element-of

### Entity-to-Value (39 properties)

**Physical dimensions:** depth, height, thickness, length, width
**Quantitative:** age, area, density, temperature, mass, volume, weight
**Structural/Material:** breakability, brightness, capacity, consistency, integrity
**Aggregate:** number-of-elements
**Chemical:** pH, polarity
**Sensory/Perceptual:** size, slope, texture, wetness, color, smell, taste
**Animate-specific:** animacy, sentience, sex, trait
**Logical:** truth

### Event-to-Value (6 properties)

direction, distance, duration, frequency, intensity, rate

### Value-to-Value (3 relations)

- same-as / same-as
- greater-than / less-than
- greater-than-or-equal-to / less-than-or-equal-to

### Temporal relations (16 total)

**Entity-to-Temporal:** time-of-existence
**Event-to-Temporal:** time-at, time-during
**Interval-to-Interval (Allen's):** starts, overlaps, meets, finishes, equals, during, before
**Instant-to-Interval:** begins, ends, inside, begins-or-in
**Spanning:** between

### Place-to-Place (16 relations)

abuts, is-above/is-below, is-beside, is-between, is-behind/is-in-front,
is-inside/encloses, is-near, is-on/has-on, is-opposite,
is-outside/does-not-enclose, is-along, is-at, is-facing, is-oriented-toward

## Local KM source

The full Component Library KM source is in the project at:

    component_library/rkf-clib/components/core/   (933 KM files)
    component_library/rkf-clib-one/                (single-file version)

Individual slot definitions can be found as `.km` files (e.g., `agent.km`,
`causes.km`, `has-part.km`).

## Access

- **Slot dictionary:** https://www.cs.utexas.edu/~mfkb/RKF/tree/components/specs/slotdictionary.html
- **CLib browser:** https://www.cs.utexas.edu/~mfkb/RKF/tree/
- **CLib home:** https://www.cs.utexas.edu/~mfkb/RKF/clib.html
