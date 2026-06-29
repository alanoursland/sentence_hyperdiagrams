# Backward Annotation

## The causal constraint

Every linking label points backward: `index_prev` is strictly less than the
current token's index. Structure is built left to right. A token at position
`n` can reference labels on tokens `0` through `n - 1`, but never labels on
future tokens.

This mirrors autoregressive processing. When the annotator or parser reaches a
token, it can use the token itself and everything already visible to its left.
It cannot go back and mutate earlier tokens. Later tokens can only emit new
labels on themselves.

That is why structural labels tend to accumulate on the right edge of a phrase
or sentence. The rightmost token has the widest backward view.

## Tokens, labels, and spans

Tokens are the input sequence. Labels are annotations attached to tokens.

A leaf label covers only its own token:

    4 rat
      NOUN

The label `NOUN` covers token `4`.

A linking label covers the span of its children:

    3 a
      ARTICLE
    4 rat
      NOUN
      SUBJECT NOUN ARTICLE 3

The label `SUBJECT NOUN ARTICLE 3` is attached to token `4`, but it covers the
constituent from token `3` through token `4`.

This matters for backward pattern matching. When a rule matches a built label
such as `SUBJECT`, it should consume the whole span of that label, not just the
single token where the label is attached. After matching the `SUBJECT` above,
the right-to-left cursor resumes before token `3`.

In implementation terms, every label instance has a derived span:

    span(label) -> (left_index, right_index)

For a leaf label, both indices are the token index. For a linking label, the
span is the union of the child spans. Because labels always point backward, the
right edge is the token where the label is attached.

## RTL pattern matching

Structural annotation can be described as right-to-left pattern matching over
the visible label trace.

Rules are evaluated left to right over the token stream. At each token, a rule
may look backward through earlier tokens and labels. If the pattern matches, it
emits a new label on the current token.

Rules are also evaluated in order. Later rules on the same token can see labels
emitted by earlier rules on that token. This creates emission chains:

    POS -> sentence element -> predicate -> sentence type

A rule pattern should match labels as constituents. This lets higher-level
rules reuse lower-level structure instead of restating it.

For example, once this has been emitted:

    SUBJECT NOUN ARTICLE 3

a later compound-subject rule can match `SUBJECT` directly. It does not need to
repeat `ARTICLE? NOUN`.

## Capture

Matching is not enough. Emitting a linking label requires choosing which
previous label becomes `child_prev`.

The rule language therefore needs an explicit capture operation. The proposed
syntax is `@`:

    @SUBJECT CONJUNCTION SUBJECT

`@SUBJECT` means: match `SUBJECT`, and capture that matched label as a possible
`child_prev`.

If a pattern contains multiple captures, the engine may record all of them, but
label construction uses the last successful capture selected by the rule's RTL
match. This keeps simple cases simple while leaving room for richer patterns.

The current token's matched label supplies `child_curr`. This may be implicit
as the rightmost/current atom in the pattern, or made explicit later with a
separate marker if needed.

Thus:

    @ARTICLE NOUN

on token `4` emits:

    SUBJECT NOUN ARTICLE 3

if `ARTICLE` matched token `3` and `NOUN` matched token `4`.

For a bare noun with no captured article:

    Ann
      NOUN
      SUBJECT

the emitted `SUBJECT` is a leaf label.

## Boundaries and punctuation

A punctuation token label is not the same thing as a sentence boundary.

The token `"."` can receive the token-level label `PERIOD`. But `PERIOD` alone
does not always mean the end of a sentence. Periods can occur in abbreviations,
initials, decimal numbers, section numbers, and URLs:

    Mrs. C.F. Alexander
    U.S.A.
    431.1
    www.gutenberg.org/license
    Section 1.A.

For this reason, broad `PUNCT` is too coarse for structural rules. Token-level
punctuation labels should distinguish forms such as:

    PERIOD
    COMMA
    QUESTION_MARK
    EXCLAMATION_POINT
    SEMICOLON
    COLON
    DOUBLE_QUOTE
    SINGLE_QUOTE

Sentence or clause boundary behavior should be treated as a separate parser
fact. Early rules may use virtual sentinels such as:

    BOF    beginning of file
    BOS    beginning of sentence

These are rule-engine sentinels, not ordinary labels emitted into the diagram.
They are useful because the first word of a sentence needs something to its
left for a backward rule to accept against.

Functional punctuation labels such as `TERMINAL_PERIOD` may be useful later,
but they should be introduced only when the annotation needs to distinguish a
period that functions as a terminal mark from a period that is part of an
abbreviation or other token-level construction.

## Subject formation

The simplest subject rule for the primer data is:

    BOS @ARTICLE? NOUN

or, allowing pronouns:

    BOS @ARTICLE? (NOUN|PRONOUN)

This emits a linking `SUBJECT` when an article is captured:

    0 A
      ARTICLE
    1 cat
      NOUN
      SUBJECT NOUN ARTICLE 0

When no article is captured, it emits a leaf `SUBJECT`:

    24 Ann
      NOUN
      SUBJECT

This rule is intentionally local. It works for the early primer examples
because the subject appears at the beginning of the sentence or fragment and
has only a very small prefix.

More general subject detection should not rely on "some punctuation appeared to
the left." It needs to respect barriers such as verbs and prepositions. A noun
after a verb is likely an object complement. A noun after a preposition is
likely part of a prepositional phrase.

So the broader subject rule is more like:

    A noun/pronoun phrase is a subject if, scanning left within the current
    sentence or clause, no predicate verb or preposition has intervened before
    the subject phrase begins.

The simple primer rule is a useful first approximation, not the full theory.

## Compound subjects

The hand annotation currently marks both conjuncts as `SUBJECT` and combines
them with a generic `COMPOUND` label:

    0 A
      ARTICLE
    1 cat
      NOUN
      SUBJECT NOUN ARTICLE 0
    2 and
      CONJUNCTION
    3 a
      ARTICLE
    4 rat
      NOUN
      SUBJECT NOUN ARTICLE 3
      COMPOUND SUBJECT SUBJECT 1

This captures the existence of a compound structure, but it loses an important
distinction for downstream rules. The two `SUBJECT` labels are subject
conjuncts. The full grammatical subject is the compound phrase:

    A cat and a rat

For later `SUBJECT + PREDICATE` matching, the full compound subject should be
available as a subject-like constituent.

The better computational label is:

    COMPOUND_SUBJECT SUBJECT SUBJECT 1

This is not really a departure from Reed-Kellogg. Reed-Kellogg has the concept
of a compound subject. The label makes that concept explicit enough for later
rules.

With span-aware matching, the compound rule can be compact:

    @SUBJECT CONJUNCTION SUBJECT

On token `4`, the rightmost `SUBJECT` covers tokens `3..4`, so the RTL cursor
jumps to token `2`, matches `CONJUNCTION`, then captures the earlier `SUBJECT`
on token `1`.

The result is:

    COMPOUND_SUBJECT SUBJECT SUBJECT 1

Later sentence rules can match:

    SUBJECT | COMPOUND_SUBJECT

without needing to know how either constituent was built.

## Predicate and sentence labels

A similar accretive pattern applies after subjects.

In:

    The cat has a rat.

the rightmost content token accumulates a chain:

    16 rat
      NOUN
      OBJECT_COMPLEMENT NOUN ARTICLE 15
      PREDICATE OBJECT_COMPLEMENT VERB 14
      DECLARATIVE PREDICATE SUBJECT 13

Each label enables the next:

1. `NOUN` comes from the POS pass.
2. `OBJECT_COMPLEMENT` uses the article and noun after a verb.
3. `PREDICATE` links the verb to the object complement.
4. `DECLARATIVE` links the subject to the predicate.

The sentence type labels have their own meanings:

    DECLARATIVE      sentence used to affirm or deny
    INTERROGATIVE    sentence expressing a question
    IMPERATIVE       sentence expressing a command or request
    EXCLAMATORY      sentence expressing sudden thought or strong feeling

Sentence complexity labels are separate:

    SIMPLE_SENTENCE    one subject and one predicate
    COMPLEX_SENTENCE   independent clause plus dependent clause(s)
    COMPOUND_SENTENCE  two or more independent clauses

`SENTENCE` is the general label. It should probably be emitted after the
sentence's type and/or complexity has been identified, not used as a crude
punctuation boundary.

## Weights as competing hypotheses

When a token is ambiguous, it may hold multiple labels simultaneously:

    run
      VERB 0.8
      NOUN 0.2

These weights are not values to overwrite. They are part of the annotation.
Both readings coexist.

Structural labels add to this picture. A local rule might emit a weak
`PREDICATE` from a bare verb. A later rule might emit a stronger linking
`PREDICATE` after an object complement or prepositional phrase appears. Both
labels may coexist if they represent different evidence.

The hyperdiagram is therefore not one chosen parse. It is a weighted,
inspectable record of plausible structure.

## Automation as hypothesis generation

The project is still fundamentally hand annotated. Automation should not be
treated as authoritative annotation too early.

A right-to-left rule engine is useful as a proposal mechanism:

    gold pass       hand-authored, trusted, small, slow
    proposal pass   generated, untrusted, useful for finding conflicts

The value of automation is not only that it fills labels in. Its failures show
which distinctions the ontology, tokenization, boundary handling, or rule
language has not yet captured.

The early Reed-Kellogg primer examples are simple enough that a small rule set
can be productive. But helper verbs, quotations, abbreviations, clause
boundaries, and punctuation functions should be handled when they appear in the
data rather than designed exhaustively up front.

## Connection to sibling projects

Backward annotation is the annotation-side counterpart of ideas explored in the
sibling projects.

`fsm_transducer` implements parsing as accretion: tokens accumulate weighted
bags of labels showing all hypotheses. Backward annotation specifies the target
labels that a correct parser should produce.

`regex_transformer` asks whether attention can learn finite-state structure.
The backward constraint in this project is the same causal constraint enforced
by autoregressive attention. The pattern "match labels to the left, emit a new
label here" is the kind of finite-state behavior that a transformer head might
learn internally.

The three projects converge:

    sentence_hyperdiagrams   target annotation
    fsm_transducer           symbolic mechanism
    regex_transformer        neural question
