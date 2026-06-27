# Abstract Meaning Representation for Sembanking

**Authors:** Laura Banarescu, Claire Bonial, Shu Cai, Madalina Georgescu,
Kira Griffitt, Ulf Hermjakob, Kevin Knight, Philipp Koehn, Martha Palmer,
Nathan Schneider
**Published:** 7th Linguistic Annotation Workshop (LAW-VII), ACL 2013,
pages 178-186, Sofia, Bulgaria

## What it is

Introduces Abstract Meaning Representation (AMR) — a framework that
represents sentence meaning as a single rooted, directed, acyclic graph
(DAG). AMR strips away surface syntax and captures "who is doing what to
whom."

### Key ideas

- **Graph-based**, not tree-based — a node can have multiple parents
  (reentrant), capturing coreference and control naturally
- **Concepts** as nodes (not words) — "The boy wants to go" has a single
  `boy` node that is both the wanter and the goer
- **Relations** as labeled edges — ~100 core relations including:
  - `:ARG0`, `:ARG1`, ... (from PropBank framesets)
  - `:location`, `:time`, `:manner`, `:purpose`, `:cause`
  - `:mod`, `:poss`, `:part-of`
  - `:polarity`, `:degree`, `:quant`
  - `:op1`, `:op2`, ... (for coordination, names)
- **No syntactic structure** — "The boy destroyed the room" and "The
  destruction of the room by the boy" get the same AMR
- Handles negation, modality, questions, and multi-sentence coreference

### AMR Guidelines

The AMR annotation guidelines (maintained at amr.isi.edu) are an extensive
reference for handling edge cases: named entities, dates, quantities,
comparison, reification, etc.

## Relevance

AMR is the closest modern analogue to what the hyperdiagram project is
building. Key differences and lessons:

- AMR **discards** syntax; hyperdiagrams **keep** it (labels chain from
  syntax up to semantics). But AMR's semantic-level relation inventory
  is directly useful as label names.
- AMR's handling of **reentrancy** (shared nodes) addresses the same
  problem as hyperdiagram cross-token references for coreference and
  control.
- AMR's **edge case catalog** (negation, modality, comparison) is
  invaluable for designing labels that cover these phenomena.
- AMR uses PropBank frames for predicate-argument structure — the same
  source the hyperdiagram ontology draws from.

## Access

- **Paper PDF:** https://aclanthology.org/W13-2322.pdf
- **ACL Anthology:** https://aclanthology.org/W13-2322/
- **AMR Guidelines:** https://github.com/amrisi/amr-guidelines
- **AMR home:** https://amr.isi.edu/

Run `download.py` to fetch the paper.
