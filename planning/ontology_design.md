# Parts of Thought — Ontology Design

## What this ontology is

Parts of Thought is a **dictionary of label names and what they mean**.

Each entry has:

- **Name** — the label identifier
- **Description** — what concept or relationship it describes (in prose)
- **Source** — where the concept comes from (CLib, FrameNet, VerbNet, etc.)

That's it.

## What this ontology is not

Parts of Thought is **not** a grammar. It does not define:

- Which labels can be children of which other labels
- Which labels apply to which parts of speech or tokens
- What sequences or combinations of labels are valid
- Formal inheritance or subtype constraints

Grammar rules — patterns over label names — belong elsewhere (e.g., in
the fsm_transducer project, where FSMs take labels as input symbols and
emit higher-level labels as output). Parts of Thought just provides the
vocabulary that grammars draw from.

## Informal organization

Descriptions may informally reference other labels to explain meaning:

- AGENT: "A noun phrase that initiates or performs an action"
- ACT-ON: "A verb describing an action performed on something"
- CAUSE: "A clause that brings about another event"

These references are **prose**, not formal relationships. They help a
human reader understand the label. They don't constrain what the label
can parent or be a child of.

Labels can be informally grouped for browsing and readability:

- Labels that typically describe **tokens** (NOUN, VERB, DET, ADJ, ...)
- Labels that typically describe **phrases** (NOUN_PHRASE, VERB_PHRASE, ...)
- Labels that typically describe **semantic roles** (AGENT, PATIENT, ...)
- Labels that typically describe **events** (ACT-ON, MOVE, TRANSFER, ...)
- Labels that typically describe **clausal relations** (CAUSE, PURPOSE, ...)
- Labels that typically describe **temporal relations** (BEFORE, DURING, ...)
- Labels that typically describe **spatial relations** (ABOVE, INSIDE, ...)

These groupings are organizing conventions, not type categories.

## The separation of concerns

1. **Parts of Thought** (this project) — the alphabet. Label names and
   their meanings.
2. **FSM transducer** — the grammar. Patterns over label names, defined
   as FSMs where labels are input symbols and states emit higher-level
   labels.
3. **Regex transformer** — the question. Does a neural network learn
   those same patterns?

Each project is cleanly separated. Parts of Thought doesn't know about
grammars. The transducer doesn't define labels. The transformer doesn't
know about either.

## Sources by label group

| Group | Primary sources |
|-------|----------------|
| Token-level labels | Universal Dependencies POS tags |
| Phrase-level labels | Universal Dependencies relations, CGEL |
| Semantic role labels | CLib event-entity slots, PropBank ArgM |
| Event/action labels | CLib action clusters, VerbNet classes, Levin |
| Preposition-sense labels | Tyler & Evans, Preposition Project, CLib spatial |
| Clausal relation labels | CLib event-event slots |
| Temporal labels | Allen interval algebra |
| Discourse labels | AMR, CLib |

## Open questions

- How many labels do we need? Start minimal for the early reader corpus
  and grow, or define the full inventory up front?
- Naming conventions — ALL_CAPS? lowercase-with-dashes? Follow CLib
  style (lowercase-with-dashes) or UD style (lowercase abbreviations)?
- How to store the dictionary — YAML files? Python module? Plain text?
- How to handle polysemy in label names — one label with a broad
  definition, or multiple labels with narrow definitions?
