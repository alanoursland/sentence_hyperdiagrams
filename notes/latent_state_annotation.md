# Latent State Annotation

## The problem

Sentence Hyperdiagrams store linguistic structure as labels attached to
tokens. A label is visible. The parser state that would have produced that
label is not necessarily visible.

If a finite-state parser processes a sentence token by token, it has some
internal state after each token. In an exact-state annotation scheme, each
token would record that state directly:

    token_i -> parser_state_i

Then parsing could resume from the last token without replaying the sentence.
The final annotation would be a complete summary of the prefix.

Hyperdiagrams do not require that. A token records Parts of Thought labels:

    token_i -> {NOUN, SUBJECT, OBJECT_COMPLEMENT, PREDICATE, ...}

These labels may be only a partial observation of the parser state. Multiple
different hidden parser states may produce the same visible labels. When that
happens, the continuation problem becomes hidden-state inference: what parser
state, or what set of parser states, is still compatible with the labels that
have been written so far?

## State, labels, and observations

For a deterministic finite-state parser, let:

    Q       = hidden parser states
    tokens  = input symbols
    delta   = transition function
    q_i     = hidden state after token i
    z_i     = visible labels attached to token i

The visible annotation can be understood as a projection of hidden state:

    z_i = phi(q_i)

If `phi` is one-to-one, every visible annotation identifies exactly one hidden
state. That is the easy case. The annotation is just a renamed parser state.

The interesting case is many-to-one:

    phi(q) = phi(r)

Two hidden states `q` and `r` emit the same visible label set. The label set is
locally ambiguous. It tells us that the parser is in one of several compatible
states, but it does not tell us which one.

In project terms, a token carrying `NOUN` and `SUBJECT` may not fully specify
all the FSM context that led there. It may only say that the token behaves as a
subject noun in the visible hyperdiagram. The hidden parser may still differ in
number agreement, clause status, quotation context, open coordination, or other
state needed for later parsing.

## Safe compression

Latent labels are harmless when they merge only states that have the same
future behavior.

If two hidden states produce the same visible annotation, and every future
token sequence leads to equivalent future annotations, then the distinction
between those states does not matter. The visible label is a valid quotient
state.

This is the finite-state version of safe compression:

    exact parser state -> behaviorally equivalent state class -> visible label

The exact state may contain more detail than the annotation needs. The
annotation is sufficient if all hidden states collapsed into the same label set
behave identically for future parsing.

This connects to quotient automata and Myhill-Nerode equivalence. Two histories
can be merged when no future continuation can distinguish them for the task at
hand.

For this project, this gives a concrete test for label design:

- A label set is strong if it preserves all distinctions needed by later
  structure.
- A label set is too weak if it merges states that later rules need to tell
  apart.
- A label set may still be acceptable if earlier labels in the sentence can
  recover the missing distinction.

## Retrodictive localization

Backward annotation says that later tokens can inspect earlier tokens and emit
new labels. Latent state annotation explains the same idea as state recovery.

Suppose the sentence has already been annotated:

    (token_0, labels_0)
    (token_1, labels_1)
    ...
    (token_n, labels_n)

The labels on token `n` may not identify the exact hidden parser state after
token `n`. But the full annotated history may constrain it.

Retrodictive localization asks:

    Which hidden parser states are consistent with this token and label trace?

A candidate hidden path is valid only if it could have consumed the same tokens
and emitted the same visible labels at each step. Walking backward through the
trace removes candidate states that could not have led to the observed later
labels.

This is the automata-theoretic version of scanning backward from a noun:

    "cat" sees ARTICLE, then boundary -> SUBJECT
    "rat" sees ARTICLE, then VERB -> OBJECT_COMPLEMENT

The visible token does not decide its role alone. Its role is localized by the
history behind it.

## Observer states

Once labels are allowed to be latent or ambiguous, the parser's known state is
not a single hidden state. It is a set of possible hidden states:

    S_i = { q in Q : q is compatible with tokens and labels through i }

This set is an observer state, belief state, or information state. It records
what the annotator or parser can know from the visible trace.

Weights fit naturally here. A weighted label set is not a commitment to one
parse. It is a compact record of competing hypotheses:

    VERB 0.8
    NOUN 0.2

Later structural labels do not erase those hypotheses. They add evidence. A
later token can emit a stronger `PREDICATE` label because it has accumulated
more context, even though an earlier token still carries a weaker local
predicate hypothesis.

The hyperdiagram is therefore not just a tree. It is a visible trace of an
observer over possible parse states.

## Placement of structural labels

The current diagram format requires every linking label to point backward:

    index_prev < current token index

That means a structural label belongs at the token where enough evidence has
arrived to emit it. The label is placed on the later child, not retroactively
written onto an earlier token.

This is why sentence-level structure naturally accumulates near the end of a
sentence. The final substantive token, or the sentence-ending punctuation, has
the widest backward view. It can see the subject, predicate, complements, and
modifiers that earlier tokens could not yet see.

In implementation terms, `fix_label_placement` enforces this idea: a linking
label should live on the token of its most recent child. Earlier tokens are not
mutated by later discoveries. Later tokens emit new labels that summarize what
has become visible.

## Possible outcomes

Backward localization can end in three ways.

### Exact localization

The visible token and label history identify exactly one hidden parser state:

    S_n = {q}

The latest label may have been ambiguous in isolation, but the annotated
history resolved it.

### Behavioral localization

Several hidden states remain possible, but they are equivalent for future
parsing. Exact identity is unknown, but the ambiguity is harmless.

This is sufficient for continuation. The parser can proceed because all
remaining states would behave the same way on every relevant future token
sequence.

### Persistent ambiguity

Several hidden states remain possible, and they differ under some future
continuation. The annotation has lost information needed for deterministic
continuation.

In that case the system must do one of four things:

- keep a set of possible parser states;
- keep weighted hypotheses over parser states;
- consult a larger window or the full prefix;
- enrich the visible annotation scheme.

## Quality levels for hyperdiagram labels

This gives a hierarchy for evaluating annotation quality.

1. Exact-state labels: each token's labels identify the exact parser state.
2. Quotient-state labels: labels merge only states with identical future
   behavior.
3. Window-recoverable labels: a finite backward window recovers the needed
   state or quotient state.
4. Prefix-recoverable labels: the full sentence prefix is required.
5. Lossy labels: the annotation destroys distinctions that cannot be recovered.

The project does not require exact-state labels. In fact, exact parser states
may be too implementation-specific to belong in a linguistic annotation. The
more useful target is behavioral sufficiency: labels should preserve enough
information for later grammatical, semantic, and discourse structure.

## Relation to the sibling projects

This note sits between the three projects.

In `sentence_hyperdiagrams`, labels define the target visible trace. They say
what linguistic structure should be recoverable from tokens and prior labels.

In `fsm_transducer`, finite-state machines generate labels by parsing as
accretion. The transducer's hidden state may be richer than the emitted labels.
Latent state annotation asks whether those emitted labels are sufficient to
continue parsing, or whether the transducer must retain hidden state outside
the diagram.

In `regex_transformer`, the question is whether attention can learn finite-state
structure. If a transformer learns an internal FSM-like state but emits only
compressed token annotations, this same distinction applies: are the visible
annotations exact states, quotient states, recoverable observations, or lossy
projections?

## Design implications

The practical consequence is that Parts of Thought labels should be judged by
their continuation value, not only by whether they name a local linguistic
category.

A good label answers two questions:

1. What structure has been identified here?
2. What future distinctions does this structure preserve?

For example, `SUBJECT` may be enough for simple declaratives. But if later
rules need to know whether the subject belongs to an independent clause, a
quoted clause, a compound structure, or a relative clause, then either those
distinctions must appear in visible labels or remain recoverable from nearby
labels.

This also clarifies why annotation passes can be layered. A POS pass supplies
local observations. A structural pass supplies stronger state localization. A
semantic pass supplies still richer equivalence classes. Each pass turns some
hidden parser distinctions into visible annotation.

## Summary

A hyperdiagram can be read as a token-level trace of a finite-state observer.
The parser has hidden state. The labels are visible observations of that state.
When labels are ambiguous, backward analysis can sometimes recover the current
state, or at least a behaviorally sufficient state class.

The central design question is therefore:

    Do the labels on the token stream preserve enough information for future
    parsing and annotation?

If yes, the hyperdiagram is not merely a record of a completed parse. It is a
restartable, inspectable memory of the parser's computation.
