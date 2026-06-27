# FrameNet

**Maintainer:** International Computer Science Institute (ICSI), Berkeley
**Based on:** Charles Fillmore's Frame Semantics

## What it is

A lexical database built on the theory of **Frame Semantics**. A semantic
frame represents a type of event, relation, or entity along with the
**frame elements** (participants, props, attributes) that characterize it.

Example — the **Commerce_buy** frame:
- Frame elements: Buyer, Seller, Goods, Money, Purpose
- Lexical units: buy, purchase, acquire, ...
- Each frame element has a semantic type and syntactic realization patterns

FrameNet contains ~1,200 frames, ~13,000 lexical units, and ~200,000
annotated sentences.

## Relevance to CLib / hyperdiagrams

CLib drew from FrameNet's frame inventory and frame elements. For the
hyperdiagram project, FrameNet provides:

- **Frame elements** map directly to semantic-level label names (agent,
  instrument, goal, etc.)
- **Frame-to-frame relations** (inheritance, subframe, perspective, etc.)
  inform how labels at different levels relate
- **Annotated sentences** serve as examples of how semantic roles surface
  syntactically — useful for designing the syntax-to-semantics label chain

## Access

- **Website:** https://framenet.icsi.berkeley.edu/
- **Data download:** https://framenet.icsi.berkeley.edu/framenet_data/
- **Frame index:** https://framenet2.icsi.berkeley.edu/fnReports/data/frameIndex.xml
- **NLTK:** `nltk.corpus.framenet`

## Python access

```python
import nltk
nltk.download('framenet_v17')
from nltk.corpus import framenet as fn
```
