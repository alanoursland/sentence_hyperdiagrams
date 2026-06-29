# Pattern Language Design

## Purpose

The pattern language defines rule transforms over annotated token streams.
It is not intended to be a general regular-expression engine and does not
need to compile patterns into finite-state machines.

The immediate use case is the Reed-Kellogg primitive layer:

    (BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)
    @SIMPLE_SUBJECT CONJUNCTION SIMPLE_SUBJECT

Rules run left to right over tokens. Each pattern is evaluated right to left
from the current token. When a rule matches, it emits a label on the current
token.

## Design goals

- Keep the syntax small enough to hand-write in YAML.
- Match both labels and literal token text.
- Support right-to-left matching over label spans.
- Support captures for label construction.
- Avoid committing to a full regex compiler.
- Make parser data structures explicit enough to test independently.

## Syntax

### Labels

Bare names match labels already present on a token:

    NOUN
    ARTICLE
    SIMPLE_SUBJECT

Label names are ontology labels or pass-produced labels.

### Literal tokens

Quoted strings match input token text directly:

    "."
    "?"
    "!"
    "and"

Literal tokens should be quoted. This avoids ambiguity between punctuation as
input text and punctuation as pattern syntax. For example, `"?"` is a token,
while `?` is the optional quantifier.

### Sentinels

Sentinels are virtual match atoms supplied by the engine:

    BOF

`BOF` is a virtual beginning-of-file marker at index `-1`. It is not a diagram
label and is not emitted into pass files.

More sentinels may be added later if needed, but they should remain engine
facts, not ordinary ontology labels.

### Group

Parentheses group a subexpression:

    (NOUN|PRONOUN)
    (BOF|"."|"?"|"!")

Groups are structural syntax. They do not capture by themselves.

### Union

`|` means alternative:

    NOUN|PRONOUN
    "."|"?"|"!"

For the first implementation, union should be restricted to alternatives that
match one logical pattern item. Avoid chain alternatives such as:

    (ARTICLE NOUN | PRONOUN)

Those can be added later, but they make captures and spans harder to reason
about. Prefer separate rules or optional atoms in the first version.

### Optional

`?` makes the previous atom or group optional:

    ARTICLE?
    @ARTICLE?
    (NOUN|PRONOUN)?

If an optional capture does not match, no capture is recorded for that atom.

### Capture

`@` marks a matched atom as a capture candidate:

    @ARTICLE
    @SIMPLE_SUBJECT
    @ARTICLE?

Captures are used to construct linking labels:

    emit child_prev child_curr index_prev

The current matched label supplies `child_curr`. The last successful `@`
capture used by the match supplies `child_prev` and `index_prev`.

If no capture succeeds, the emitted label is a leaf label.

## Likely Extensions

These are probably needed, but they should be added when a real rule needs
them.

### Repeat

Repeat allows zero or more matches:

    ADJECTIVE*

This will be useful for stacked modifiers:

    @ARTICLE ADJECTIVE* NOUN

Repeat introduces ambiguity because there may be several valid match lengths.
The matcher needs a clear policy: shortest match, longest match, or all
matches. The first version can avoid `*` until this policy is needed.

### Any

Any matches one previous token or constituent:

    .

A multi-token skip is usually written:

    .*

Because literal periods are quoted as `"."`, unquoted `.` can safely mean
"any". This is useful for distant links:

    @SIMPLE_SUBJECT .* PREDICATE

Like repeat, `.*` creates ambiguity. It should probably be lazy by default,
but the engine should be able to report multiple matches later if ambiguity
matters.

### Exclude

Exclude prevents matching an atom or set of atoms:

    !VERB
    !(VERB|PREPOSITION)

This will be useful for barrier rules, such as "scan left until a boundary,
but fail if a verb or preposition intervenes."

Exclude can become hard to reason about if it is allowed everywhere. A safer
first form is a named rule field rather than inline syntax:

    reject_before_accept:
      - VERB
      - PREPOSITION

Inline exclude can wait until the need is clear.

## RegexElement Model

The parser should turn a pattern string into an AST of `RegexElement` objects.
This is not a compiled automaton. It is a tree/list of matchable elements.

Suggested element types:

    RegexElement
      TokenLiteral
      LabelAtom
      SentinelAtom
      Sequence
      Group
      Union
      Optional
      Capture
      Repeat
      Any
      Exclude

The first implementation probably only needs:

    TokenLiteral
    LabelAtom
    SentinelAtom
    Sequence
    Group
    Union
    Optional
    Capture

`Repeat`, `Any`, and `Exclude` can be parsed later when rules need them.

## Runtime Data

Some concepts should not be `RegexElement` nodes.

### Rule

A rule wraps a pattern and an emitted label:

    emit: SIMPLE_SUBJECT
    pattern: '(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)'
    weight: 1.0

`weight` defaults to `1.0`.

### MatchResult

A successful match should return:

    matched: bool
    child_curr: LabelInstance
    captures: list[LabelInstance]
    left_index_after_match: int

The emitted label uses:

    child_curr = current/rightmost matched label
    child_prev = last successful capture, if any
    index_prev = child_prev token index

### LabelInstance

Pattern matching needs label instances, not just label names:

    label name
    token index where attached
    parameter
    weight
    span

The span is important because matching a built label consumes the whole
constituent.

### Span

Every label instance has a derived span:

    leaf label:    token_index..token_index
    linking label: union(child_prev span, child_curr span)

Right-to-left matching resumes before the left edge of the matched span.

## Matching Semantics

The engine evaluates rules in token order:

    for token in tokens:
        for rule in rules:
            if rule matches at token:
                emit label on token

Later rules on the same token can see labels emitted by earlier rules.

Patterns are written left to right for readability, but matched right to left
from the current token. The rightmost pattern element is the current-token
element.

For example:

    @SIMPLE_SUBJECT CONJUNCTION SIMPLE_SUBJECT

on:

    A cat and a rat

matches the rightmost `SIMPLE_SUBJECT` at `rat`, consumes its span, matches
`CONJUNCTION` at `and`, then captures the earlier `SIMPLE_SUBJECT` at `cat`.

## First Implementation Scope

Implement only enough to support `reed_kellogg_02_primitives.yaml`:

    TokenLiteral
    LabelAtom
    SentinelAtom
    Sequence
    Group
    Union
    Optional
    Capture

Do not implement these yet unless a real rule needs them:

    Repeat
    Any
    Exclude

This keeps the parser small while leaving the AST shape ready for growth.

## Open Questions

- Should union eventually allow full sequence alternatives?
- Should `.*` return the first match, the best match, or all matches?
- Should multiple captures always use the last capture, or should rules name
  which capture constructs the emitted label?
- Should child_curr be implicit as the current/rightmost match, or should a
  future syntax explicitly mark it?
- Should punctuation function labels such as `TERMINAL_PERIOD` be produced by
  a separate primitive pass before grammatical primitives?
