# English Verb Classes and Alternations: A Preliminary Investigation

**Author:** Beth Levin
**Published:** University of Chicago Press, 1993
**ISBN:** 978-0-226-47533-2

## What it is

A classification of over 3,000 English verbs into classes based on shared
meaning and syntactic behavior. The core hypothesis: a verb's meaning
determines which syntactic frames it can appear in (its **alternations**).
Verbs that share alternation behavior share semantic properties.

### Structure

**Part I — Alternations:** Catalogs the syntactic frames verbs participate in:
- Transitivity alternations (causative/inchoative, middle, etc.)
- Dative alternations (double object, to-dative, for-dative)
- Locative alternations (spray/load, swarm, etc.)
- Other argument structure changes

**Part II — Verb Classes:** ~200 classes grouped by shared semantics:
- Verbs of putting (put, place, set, ...)
- Verbs of removing (remove, extract, withdraw, ...)
- Verbs of sending and carrying (send, carry, transport, ...)
- Verbs of change of state (break, bend, fold, ...)
- Verbs of contact by impact (hit, strike, kick, ...)
- Verbs of communication (say, tell, speak, ...)
- Verbs of creation and transformation
- Verbs of motion
- Verbs of perception
- Verbs of cognition
- ... and many more

Each class entry includes verb lists, example sentences, which alternations
the class participates in, and bibliographic references.

## Relevance to CLib / hyperdiagrams

Levin's verb classes are the **direct foundation** for VerbNet, which in turn
was one of the sources for the Component Library. The chain is:

    Levin classes → VerbNet → CLib → hyperdiagram label ontology

For the hyperdiagram project specifically:

- **Verb classes** inform the event-type label names (the `name` field for
  semantic labels over verbs)
- **Alternations** show how the same semantic roles surface in different
  syntactic positions — critical for designing labels that bridge syntax
  and semantics (e.g., the agent is the subject in active voice but a
  by-phrase in passive)
- **The meaning-behavior link** validates the hyperdiagram approach: if
  verbs in the same class behave the same syntactically, then the same
  label patterns should apply across the class

## Access

- **Publisher:** https://press.uchicago.edu/ucp/books/book/chicago/E/bo3684144.html
- **Internet Archive:** https://archive.org/details/englishverbclass0000levi
- **Amazon:** https://www.amazon.com/English-Verb-Classes-Alternations-Investigation/dp/0226475336
- **VerbNet** (computational successor): https://verbs.colorado.edu/verbnet/

This is a commercial book (not freely downloadable as PDF). VerbNet provides
the machine-readable computational version of Levin's classification.
