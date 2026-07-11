# Transformer Connection

## Status of the claim

The connection between sentence hyperdiagrams, backward-looking finite-state
parsers, and transformer language models is a research hypothesis. It is not a
claim that trained transformers literally store Parts of Thought labels, nor
that an attention map is a dependency diagram.

The hypothesis is that hyperdiagram labels may describe interpretable state
features encoded in token residual vectors, while attention and feed-forward
networks jointly implement the backward-looking computations that construct
and compose those features.

Three claims must remain separate:

1. Transformers can compute hyperdiagram-like structures.
2. Hyperdiagrams usefully describe information recoverable from transformer
   activations.
3. Trained transformers actually use causally important internal features
   equivalent to hyperdiagram labels.

Constructive implementations can establish the first claim. Probes can supply
evidence for the second. The third requires causal experiments.

## One transformer layer

For a typical pre-normalized causal transformer, let `x_t^l` be the residual
vector at token `t` and layer `l`:

```text
a_t = Attention(LN(x_t), LN(x_<=t))
y_t = x_t + a_t
m_t = FFN(LN(y_t))
x_t_next = y_t + m_t
```

The FFN receives one normalized vector per token. That vector already contains
the token's accumulated residual features plus information retrieved from the
current and earlier positions by causal attention. The FFN does not receive
the attention matrix or the other token vectors as separate inputs.

The persistent representation is not the FFN output alone. The FFN writes an
update into the residual stream, which retains the attention update, earlier
features, and the new FFN features in superposition.

## Attention as backward-looking computation

Attention is analogous to the projects' backward-looking FSAs, but not
identical to them.

- The query represents what the current token state is looking for.
- Keys represent conditions available at earlier token states.
- Query-key interaction performs a soft, content-addressed condition test.
- Values carry selected features of matching earlier states.
- Multiple heads perform several backward searches or transitions in parallel.
- The output projection combines the retrieved evidence at the current token.

This does more than route information. Selection, condition matching, value
transformation, aggregation, and output projection all perform part of the
state transition.

Unlike an ordinary sequential FSA, attention can examine every earlier
position in one operation. It normally returns a normalized mixture rather
than one discrete predecessor. It is therefore closer to a parallel,
content-addressed, weighted backward automaton.

## The FFN's part of the transition

The FFN performs token-local nonlinear computation over the current residual
state and the evidence attention placed there. It can:

- recognize conjunctions of current and retrieved features;
- classify the resulting configuration;
- construct or strengthen a new state feature;
- suppress incompatible hypotheses;
- prepare features that later layers will use as queries, keys, and values.

The FSA-like transition is consequently distributed across attention and the
FFN. A strict description such as "attention retrieves and the FFN computes"
is useful only as a first approximation. Attention participates in matching
and transformation, while FFNs construct the state features on which later
backward searches depend.

## Tentative correspondence

| Symbolic concept | Possible transformer analogue |
|---|---|
| Weighted labels at a token | Superposed residual-stream features |
| Current parser state | Current token's residual features |
| Backward rule condition | Query-key matching over earlier positions |
| Earlier matching state | Attended value source |
| Retrieved labels | Features carried by value vectors |
| Rule conjunction/classification | Attention composition plus FFN activation |
| Emitted label | Feature written into the residual stream |
| Repeated annotation closure | Successive transformer layers |
| Quotient or observer state | Behaviorally sufficient residual subspace |

For example, when processing `cat` in `the cat`, attention could retrieve
article and positional features from `the`. An FFN could recognize the
combination of those features with the current noun features and write a
nominal-projection feature at `cat`. Later layers could retrieve that feature
and compose it into a subject, object, clause, semantic role, or discourse
relation.

This is a hypothesis about features in residual vectors, not a requirement
that one neuron, dimension, or FFN unit correspond to one label. A label may be
distributed across dimensions and layers, and several labels may be
superposed in the same vector.

## Connection to parsing as accretion

The closest project-level analogy is:

```text
residual vector
    ~= weighted bag of latent state/label features

attention
    ~= backward matching and retrieval over earlier token states

FFN plus residual update
    ~= local rule closure and emission of new state features

successive layers
    ~= repeated rounds of annotation accretion
```

This connects to `latent_state_annotation.md`. Hyperdiagram labels need not be
exact transformer states. They may instead be visible names for quotient
states: distinctions that are sufficient to predict the relevant future
behavior while ignoring implementation-specific details.

## What would count as evidence

Decodability alone is weak evidence because a flexible probe can recover
information that the model does not use. Stronger tests include:

1. Train small transformers on controlled languages with known hyperdiagrams.
2. Test whether labels are decodable at the token and layer where the proposed
   computation predicts they should appear.
3. Compare hyperdiagrams against dependency, constituency, and ordinary FSA
   state representations using equally constrained probes.
4. Intervene on a decoded feature and test whether only the predicted family
   of continuations changes.
5. Test continuation equivalence: prefixes with the same proposed quotient
   state should produce equivalent relevant future behavior.
6. Trace whether attention retrieves the proposed operands before an FFN
   writes the proposed composite feature.

A particularly strong result would show that targeted alteration of a
hyperdiagram-like residual feature causes the predicted grammatical or
semantic behavior to change, while matched control interventions do not.

## Working formulation

The disciplined working hypothesis is:

> Each transformer layer performs a round of weighted backward annotation.
> Attention searches, matches, retrieves, and partially transforms relevant
> earlier latent states. The FFN performs local nonlinear closure and writes
> new latent-state features into the current token's residual vector.
> Hyperdiagrams propose human-interpretable names for behaviorally important
> quotient states within that distributed computation.

This formulation is intended to guide experiments. It should not be presented
as an established description of trained language models without causal
evidence.
