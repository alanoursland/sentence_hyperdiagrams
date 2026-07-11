# Project Overview

## What this project is

Sentence Hyperdiagrams is a system for annotating natural language
text with rich linguistic structure — from surface syntax through deep
semantics and long-distance relationships — using a single, uniform
annotation mechanism called **labels**. Annotations may be written manually or
proposed by explicit deterministic transforms for human review.

The project distills existing human knowledge about language (linguistics,
semantics, ontology) into a formal annotation scheme. There is no machine
learning, no gradient descent, no statistical inference. The ontology is
hand-crafted by humans (or with AI assistance), drawing from decades of
classical NLP and knowledge representation research.

## Why "hyperdiagrams"

Traditional sentence diagrams (Reed-Kellogg, dependency trees) capture a
single level of structure. A hyperdiagram captures multiple levels
simultaneously using the same mechanism: labels that reference other labels.
A syntactic label links tokens. A semantic label links syntactic labels. A
discourse label links semantic labels. The result is not one tree but a
layered structure of relationships between relationships.

## Parts of Thought

The label ontology is called **Parts of Thought** — analogous to "Parts of
Speech" but for structure at every level. Just as Parts of Speech are the
finite set of categories for what a word *is*, Parts of Thought are the
finite set of categories for what a relationship *is*.

The hierarchy is a single tree where more specific names refine more general
ones. Semantics is not layered on top of syntax — it *is* syntax, refined.
AGENT is a kind of NOUN_PHRASE. ACT-ON is a kind of VERB. Choosing a more
specific label simultaneously encodes syntactic category and semantic role.

The same hierarchy works for both analysis (decomposing text into parts of
thought) and generation (composing parts of thought into text).

## The label mechanism

Every annotation is a **label** — a tuple attached to a single token:

    [name, child_curr, child_prev, index_prev, parameter, weight]

Each linking label creates a binary tree node by joining a label on the
current token to a label on a previous token. Tokens themselves are labels
without children (leaf nodes). See `data_model.md` for the full specification.

This mechanism is deliberately minimal. Its power comes from the **ontology**
— the set of label names and what they mean.

## The ontology

Label names are drawn from a hand-built ontology rooted in the UT Austin
Component Library (CLib), which itself drew from WordNet, FrameNet, VerbNet,
Roget's Thesaurus, the Longman defining vocabulary, and OpenCyc. See
`clib.md` for details.

The ontology covers:

- **Syntactic relations** — subject, object, modifier, complement, etc.
- **Semantic relations** — agent, instrument, cause, result, destination,
  etc. (~80 relations from the CLib slot dictionary, organized into
  event-event, event-entity, entity-entity, and property categories)
- **Long-distance relations** — coreference, binding, filler-gap
  dependencies, discourse connectives

The goal is a compact set of label names with broad coverage — depth at the
top of the hierarchy, not exhaustive enumeration of domain-specific terms.

## The dataset

The initial corpus is the **early reader dataset** (`data/early_reader/`):
~2,000 primer-register English sentences from four public-domain 19th-century
textbooks (McGuffey's Primer through Fifty Famous Stories Retold). The
sentences range from "A cat and a rat." to real narratives with dialogue,
sequence, and cause.

This dataset is shared with two sibling projects and was chosen because:

- The vocabulary is small (~2,000 words) and the syntax is simple, making
  hand annotation tractable
- The difficulty escalates across four tiers, providing a natural curriculum
- Adjacent sentences form discourse, enabling annotation of cross-sentence
  relationships (anaphora, narrative sequence)
- Tier 1's heavy structural repetition is ideal for establishing annotation
  patterns

## Sibling projects

Sentence Hyperdiagrams is part of a trio of projects that approach the same
question from different directions: **what is the structure of language, and
how can we represent it?**

### regex_transformer (`E:\Projects\regex_transformer`)

Trains single-layer transformers on regular languages and probes whether
attention heads learn finite-state machine (FSM) structure internally. This
is empirical mechanistic interpretability — asking what a neural network
actually learns, not what it outputs.

Key result: a constructive proof (`fsm_construction.py`) that attention
weight matrices can exactly encode FSM state transitions. One head per input
symbol, `d_model = num_states`, value matrices encoding transitions.

### fsm_transducer (`E:\Projects\fsm_transducer`)

A fully inspectable symbolic parser built on stacked weighted finite-state
machines. Implements "parsing as accretion" — tokens accumulate weighted bags
of labels showing all hypotheses with confidence scores, rather than
committing to a single parse tree. Every label traces to a named rule.

### How they connect

| Project | Direction | Question |
|---------|-----------|----------|
| regex_transformer | Neural → structure | What FSM does a transformer learn? |
| fsm_transducer | Structure → parser | Can we build an inspectable FSM parser? |
| sentence_hyperdiagrams | Knowledge → annotation | What is the correct linguistic structure? |

The hyperdiagrams provide **ground truth**. The FSM transducer provides a
**symbolic parser** whose output can be compared against that ground truth.
The regex transformer asks whether a **neural network** recovers equivalent
structure internally.

See `transformer_connection.md` for the precise working hypothesis: attention
acts as a parallel weighted backward matcher and retriever, FFNs perform local
nonlinear state closure, and the residual stream may carry distributed
features corresponding to behaviorally useful hyperdiagram quotient states.
This is an experimental proposal, not an established account of LLM internals.

All three share the early reader dataset as common ground — simple enough for
hand annotation, precise FSM grammars, and clean transformer learning.

## What this project is not

- Not a machine learning system. No training, no models, no gradients.
- Not a statistical or opaque parser. Its deterministic transforms generate
  inspectable annotation proposals from named lexical entries and rules.
- Not a new linguistic theory. It distills existing knowledge from classical
  NLP, formal semantics, and knowledge representation into a practical
  annotation format.

The contribution is the **annotation scheme** (the label mechanism) and the
**ontology** (the set of label names and their definitions), applied
systematically to real text.
