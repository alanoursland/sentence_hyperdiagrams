# Maintaining Knowledge about Temporal Intervals

**Author:** James F. Allen
**Published:** Communications of the ACM, 26(11):832-843, November 1983

## What it is

The foundational paper for interval-based temporal reasoning. Defines 13
mutually exclusive relations between any two time intervals and a constraint
propagation algorithm for maintaining consistency.

### The 13 Allen interval relations

| Relation | Inverse | Meaning |
|----------|---------|---------|
| before | after | X entirely precedes Y |
| meets | met-by | X ends exactly where Y begins |
| overlaps | overlapped-by | X starts before Y and ends during Y |
| starts | started-by | X and Y start together, X ends first |
| during | contains | X is entirely within Y |
| finishes | finished-by | X and Y end together, X starts later |
| equals | equals | X and Y occupy the same interval |

(7 base relations + 6 inverses + equals = 13 total)

### Key contributions

- **Interval algebra** — a complete calculus for temporal reasoning
- **Constraint propagation** — transitivity tables for inferring new
  relations from known ones
- **Interval vs. point** — argues that intervals are more natural than
  time points for representing events and states

## Relevance

The CLib slot dictionary already uses Allen's relations for its
Temporal-Entity slots (starts, overlaps, meets, finishes, equals, during,
before). This paper is the formal foundation — it guarantees that the
hyperdiagram's temporal labels form a **mathematically sound** system:

- Any two events/states can be related by exactly one of the 13 relations
- New temporal relations can be inferred by constraint propagation
- The system is complete — no temporal relationship falls outside it

## Access

- **ACM Digital Library:** https://dl.acm.org/doi/10.1145/182.358434
- **CACM page:** https://cacm.acm.org/research/maintaining-knowledge-about-temporal-intervals/

Run `download.py` to attempt to fetch the paper (may require ACM access).
