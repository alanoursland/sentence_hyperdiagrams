# Sentence Hyperdiagrams

Linguistic annotation of natural language text using a uniform mechanism that
spans syntax, semantics, and discourse. Humans define and review the ontology
and annotations; deterministic lexical maps and pattern transforms can produce
explicit, traceable annotation proposals.

## Approach

A **label** is a tuple `[name, child_curr, child_prev, index_prev, parameter, weight]`
attached to a single token. Each label creates a tree node by linking a label
on the current token to a label on a previous token. Tokens are labels without
children.

By chaining labels that reference other labels, the system builds
relationships between relationships — from surface syntax up through semantic
roles, coreference, and discourse structure — all with the same mechanism.

The label ontology is called **Parts of Thought** — a single type hierarchy
of relation names where semantics is syntax, refined. AGENT is a kind of
NOUN_PHRASE. ACT-ON is a kind of VERB. The same hierarchy works for both
analysis (decomposing text) and generation (composing text).

The ontology and rules are hand-crafted from classical linguistics and
knowledge representation research. There is no model training or statistical
inference. Generated passes are deterministic proposals, not automatically
trusted ground truth.

## Label conventions

- General labels such as `SUBJECT`, `PREDICATE`, and `OBJECT_COMPLEMENT` are
  abstract ontology categories. Concrete annotation passes emit `SIMPLE_*` or
  `COMPOUND_*` labels.
- `NOUN` intentionally serves as both a lexical leaf label and a recursive
  linking label for nominal projection. This lets later rules consume one
  stable label regardless of how many pre-head modifiers were absorbed.
- General categories remain documented for classification and dependency
  planning; they are emitted only if a future pass explicitly defines a
  concrete use for them.

## Project structure

```
notes/                  Project documentation
  data_model.md         Label tuple specification
  clib.md               Component Library foundation
  transformer_connection.md  Hypothesis connecting labels to transformer state
  project_overview.md   Full project summary and sibling project connections

data/
  early_reader/         ~2,000 primer-register sentences (public domain)

component_library/
  rkf-clib/             UT Austin Component Library (KM source, 933 components)
  rkf-clib-one/         Single-file version

reference/              Ontology sources (PDFs gitignored, READMEs + download scripts)
  clark_porter_1997/    Building Concept Representations from Reusable Components
  barker_porter_clark_2001/  A Library of Generic Concepts (CLib inventory)
  barker_1998_dissertation/  Case roles and semantic relations
  yeh_porter_barker_2006/    Unified WSD + Semantic Role Labeling
  yeh_porter_barker_2005/    Discourse-level utterance matching
  fan_barker_porter_2003/    Knowledge for noun compound interpretation
  clib_slot_dictionary/      Full CLib relation inventory (~150 slots)
  wordnet/              Lexical database — synsets, hypernymy, meronymy
  framenet/             Frame semantics — frames and frame elements
  verbnet/              Verb classes — thematic roles, syntactic frames
  rogets_thesaurus/     Conceptual headword hierarchy
  longman_ldoce/        Defining vocabulary (~2,000 words)
  opencyc/              Upper ontology
```

The executable annotation path is:

```text
sentence files -> tokenized diagrams -> POS pass -> structural proposal passes
```

`src/apply_labels.py` applies both lexical and rule transforms. Transform
metadata lives under the YAML `metadata` key, separate from lexical vocabulary
entries.

## Ontology sources

The label ontology draws from the
[Component Library](https://www.cs.utexas.edu/~mfkb/RKF/clib.html) (CLib)
developed by Bruce Porter's group at UT Austin, which itself synthesized:

- [WordNet](https://wordnet.princeton.edu/) — lexical relations
- [FrameNet](https://framenet.icsi.berkeley.edu/) — frame semantics
- [VerbNet](https://verbs.colorado.edu/verbnet/) — verb classes and thematic roles
- [Roget's Thesaurus](https://www.gutenberg.org/ebooks/22) — conceptual organization
- Longman defining vocabulary — compact naming
- [OpenCyc](https://web.archive.org/web/2017/https://www.cyc.com/opencyc/) — upper ontology

## Related projects

- **regex_transformer** — What FSM structure does a transformer learn?
- **fsm_transducer** — Inspectable symbolic parser via stacked weighted FSMs

All three projects share the early reader dataset and address the same
question from different directions: what is the structure of language?

## Dataset

The early reader corpus contains ~2,000 sentences from four public-domain
19th-century textbooks (Project Gutenberg), escalating from "A cat and a rat."
to narrative with dialogue and causation. See `data/early_reader/README.md`.

## Gold evaluation

`gold/reed_kellogg/` contains 36 manually reviewed sentences covering the
currently executable POS and primitive constructions, including explicit
negative and weighted-ambiguity cases. Compare a generated pass with gold via:

```powershell
$env:PYTHONPATH='src'
python src/compare_gold.py --gold gold/reed_kellogg/primitives.txt `
  --generated gold/reed_kellogg/generated_primitives.txt `
  --context gold/reed_kellogg/pos.txt
```

The report includes precision, recall, missing labels, extra labels, and
invalid references. Generated labels below weight `1.0` are excluded by
default; pass `--min-weight 0` to inspect every hypothesis.
