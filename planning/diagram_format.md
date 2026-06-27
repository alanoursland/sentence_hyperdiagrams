# Diagram File Format

## Overview

A diagram file annotates a sentence with Parts of Thought labels. The
format is plain text, designed for hand-editing in any text editor.

## Token lines

Token lines are unindented and have the form:

    <index> <token>

Index is an explicit 0-based integer. Token is a word or punctuation mark.

    0 The
    1 cat
    2 sat
    3 .

## Label lines

Label lines are indented (whitespace-prefixed) and appear below the token
they are attached to. A token may have zero or more labels.

    0 The
      DET
    1 cat
      NOUN
      NOUN_PHRASE DET NOUN 0

### Label fields

Labels use positional shorthand. Trailing fields may be omitted.

    name [child_prev child_curr index_prev [parameter [weight]]]

| Position | Field | Required | Default |
|----------|-------|----------|---------|
| 1 | `name` | yes | — |
| 2 | `child_prev` | no | (leaf) |
| 3 | `child_curr` | no | (leaf) |
| 4 | `index_prev` | no | (leaf) |
| 5 | `parameter` | no | 0 |
| 6 | `weight` | no | 1.0 |

A bare name with no other fields is a **leaf label** — it tags the token
directly without linking to other labels.

    DET

A name with child_prev, child_curr, and index_prev is a **linking label**
— it creates a tree node connecting a label on a previous token to a label
on the current token.

    NOUN_PHRASE DET NOUN 0

The three linking fields (child_prev, child_curr, index_prev) must appear
together or not at all — you can't specify one without the others.

## Comments and metadata

Lines starting with `#` are comments. Blank lines are ignored.

    # source: mcguffey_primer
    # pass: 01
    # focus: pos, basic phrases

Metadata uses `# key: value` format in comments at the top of the file.

## Multi-file passes

Annotations can be split across multiple files, one per annotator pass.
Each pass file contains the same indexed tokens and adds whatever labels
the annotator identifies on that pass.

    diagrams/
      mcguffey_primer/
        001/
          tokens.txt        # canonical token sequence (no labels)
          pass_01.txt       # first annotation pass
          pass_02.txt       # second pass
          ...

`tokens.txt` contains only indexed token lines (no labels). Pass files
repeat the tokens and add labels. Token indexes and strings in pass files
must match `tokens.txt` exactly.

## Full example

**tokens.txt:**

    0 The
    1 cat
    2 sat
    3 on
    4 the
    5 mat
    6 .

**pass_01.txt:**

    # pass: 01
    # focus: pos, basic phrases

    0 The
      DET
    1 cat
      NOUN
      NOUN_PHRASE DET NOUN 0
    2 sat
      VERB
    3 on
      PREPOSITION
    4 the
      DET
    5 mat
      NOUN
      NOUN_PHRASE DET NOUN 4
    6 .
      PUNCT

**pass_02.txt:**

    # pass: 02
    # focus: semantic roles

    0 The
    1 cat
      AGENT
    2 sat
      ACT-ON AGENT PREPOSITION 1
    3 on
    4 the
    5 mat
      LOCATION
    6 .
      SENTENCE ACT-ON PUNCT 2

## File extension

`.pot` (Parts of Thought) or `.txt`. No preference enforced.
