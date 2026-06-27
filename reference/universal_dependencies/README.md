# Universal Dependencies (UD)

**Maintainer:** UD community (Nivre, de Marneffe, et al.)
**Current version:** v2 (ongoing releases)

## What it is

The modern open standard for syntactic annotation. UD defines a
cross-linguistically consistent set of **dependency relations** between
words. Instead of nested phrase-structure trees (constituency), UD draws
direct labeled arcs from head words to their dependents.

### Core dependency relations (~37 universal relations)

**Nominal core arguments:**
- `nsubj` — nominal subject
- `obj` — direct object
- `iobj` — indirect object

**Clausal core arguments:**
- `csubj` — clausal subject
- `ccomp` — clausal complement
- `xcomp` — open clausal complement (controlled subject)

**Nominal modifiers:**
- `nmod` — nominal modifier (typically prepositional)
- `amod` — adjectival modifier
- `nummod` — numeric modifier
- `appos` — appositional modifier

**Other modifiers:**
- `advmod` — adverbial modifier
- `obl` — oblique nominal (non-core prepositional argument)
- `vocative` — vocative

**Function words:**
- `det` — determiner
- `aux` — auxiliary
- `cop` — copula
- `mark` — subordinating conjunction / marker
- `cc` — coordinating conjunction
- `case` — preposition / postposition / case marker

**Coordination & parataxis:**
- `conj` — conjunct
- `parataxis` — parataxis

**Special:**
- `flat` — flat multiword expression (names, dates)
- `fixed` — fixed multiword expression
- `compound` — compound
- `punct` — punctuation
- `dep` — unspecified dependency
- `root` — root of the sentence

### Key design principles

- **Content words** are heads (not function words) — the verb heads the
  clause, the noun heads the NP
- **Function words** attach to content words as dependents (det, aux, case)
- **Cross-linguistically consistent** — the same relation labels work across
  100+ languages

## Relevance

UD provides the **base syntactic layer** for hyperdiagram labels:

- UD relations are the label names for syntax-level annotations
- The head-dependent structure maps naturally to the label tuple: a label
  on the dependent token references a label on the head token
- UD's function-word-as-dependent principle determines which token carries
  each label
- Semantic-level labels (agent, instrument, cause) build on top of UD
  syntactic labels — the hyperdiagram chain goes UD relation → semantic role

## Access

- **Guidelines:** https://universaldependencies.org/guidelines.html
- **English guidelines:** https://universaldependencies.org/en/
- **Relation index:** https://universaldependencies.org/u/dep/
- **POS tags:** https://universaldependencies.org/u/pos/
- **Features:** https://universaldependencies.org/u/feat/
- **Treebank data:** https://universaldependencies.org/#download
- **GitHub:** https://github.com/UniversalDependencies
