# Reed-Kellogg Gaps and Parser Pressure Points

This note tracks places where the current RK-oriented annotation rules expose
real grammatical issues. The goal is not to fix every case immediately. For
the early corpus, it is acceptable to brute-force some cases by adding possible
POS labels to individual words. The important part is to preserve the observed
problem so later rule design does not forget why the workaround exists.

## Working stance

- Stay within the Reed-Kellogg framework where possible.
- Prefer small, corpus-specific POS additions when that keeps momentum.
- Do not add new structural labels too quickly unless repeated examples force
  the distinction.
- Treat generated parses as evidence. Bad parses often identify a missing
  layer rather than a single bad rule.

## Case and proper names

Capitalized words are doing work that the current POS pass mostly ignores.
Lowercase vocabulary lookup loses useful evidence for:

- multi-token personal names: `Henry Black`, `Ned Bell`
- month/date names: `May`
- possessive proper nouns: `Tom's`, `Nat's`
- sentence-initial common words, where capitalization is weaker evidence

Example:

```text
1443 Henry
  SIMPLE_SUBJECT
1444 Black
1445 and
1446 Ned
1447 Bell
1448 live
1449 near
1450 our
1451 house
  NOUN NOUN ADJECTIVE 1450
  SIMPLE_PREPOSITIONAL_PRINCIPAL
1452 .
```

The likely missing pieces are proper-name nominal formation and compound
subject formation over full names:

```text
Henry Black and Ned Bell
```

A future structural approach might introduce `CAPITALIZED`, `PROPER_NOUN`, or
`NAME`. A practical near-term approach is to add possible POS tags for known
names in the small corpus.

## Possessives

Possessive nouns and possessive pronoun modifiers are now treated as adjectival
modifiers while preserving possessive-specific labels.

Examples:

```text
Tom's
  ADJECTIVE
  POSSESSIVE_NOUN

his
  ADJECTIVE
  POSSESSIVE_PRONOUN
```

This seems RK-compatible: the word remains possessive by form, while its use
before a noun is adjectival.

## Recursive nominal projection

The primitive layer now reuses `NOUN` to build larger nominal projections:

```text
147 a
148 fat
149 dog
  NOUN NOUN ADJECTIVE 148
  NOUN NOUN ARTICLE 147
```

This keeps the label set small and lets roles consume `NOUN` without knowing
whether it includes an article, adjective, or possessive modifier. The risk is
that same-name labels require careful resolution rules in the engine.

## Interrogative inversion

Example:

```text
125 Has
126 Ann
  SIMPLE_OBJECT_COMPLEMENT
127 a
128 hat
  NOUN NOUN ARTICLE 127
129 ?
```

`Ann` is not an object complement here. The sentence is an inverted
interrogative form of:

```text
Ann has a hat.
```

This probably needs clause-pattern context, not just a local object-complement
rule. A sentence-initial finite verb can make the following nominal the subject
instead of the object.

## Compound sentences versus compound subjects

Example:

```text
88 Ann
  SIMPLE_SUBJECT
89 sat
90 ,
91 and
92 Nat
93 ran
94 .
```

`Nat ran` is a second independent clause, not the second half of a compound
subject. Current subject rules do not understand `, and` as a possible clause
boundary. This should probably wait until predicates, clauses, and compound
sentences are represented.

## Post-head modifiers and nominalized adjectives

Example:

```text
1725 It
  NOUN
  SIMPLE_SUBJECT
1726 is
1727 the
1728 first
1729 of
1730 May
1731 .
```

The difficult phrase is:

```text
the first of May
```

Problems exposed:

- `first` may be an adjective used substantively.
- `of May` is a post-head prepositional modifier.
- `May` is likely a proper noun/date name.
- Attribute complements after `is` need different handling from ordinary
  object-complement positions.

This points toward later support for prepositional modifiers, nominalized
adjectives, and attribute complements.

## Practical next steps

- Keep adding possible POS labels for the small corpus when that resolves a
  concrete example without distorting RK.
- Capture bad parses here when they expose a structural issue.
- Delay full solutions for names, inverted questions, clauses, and post-head
  modifiers until the repeated cases make the next layer obvious.
