# Reed-Kellogg Canonical Gold Corpus

This corpus contains 36 deliberately small, manually reviewed examples for the
currently executable POS and primitive-structure layers. It is an evaluation
fixture, not training data.

Coverage includes bare and modified subjects, compound subjects, direct and
compound objects, simple and compound prepositional principals, possessives,
stacked adjectives, fragments, and sentence-boundary punctuation.

Negative cases cover inverted interrogatives, copular attributes, clause-level
coordination, punctuation barriers, imperatives/direct address, and a token
with a low-confidence nominal interpretation. Unsupported structures are left
unlabeled in `primitives.txt`; this is intentional.

Files:

- `sentences.txt`: one reviewed example per line.
- `tokens.txt`: canonical continuous token sequence.
- `pos.txt`: manually reviewed POS/co-label hypotheses.
- `primitives.txt`: manually reviewed expected output of the current primitive
  grammar at confidence 1.0.
- `generated_primitives.txt`: reproducible rule output used for comparison.

Weighted labels below 1.0 are alternative hypotheses. They remain available to
rules, and generated conclusions inherit the weakest premise weight. The gold
comparison command defaults to confidence 1.0, while `--min-weight 0` exposes
all hypotheses.

Compare the checked-in generated pass with gold:

```powershell
$env:PYTHONPATH='src'
C:\Users\alano\anaconda3\python.exe src\compare_gold.py `
  --gold gold\reed_kellogg\primitives.txt `
  --generated gold\reed_kellogg\generated_primitives.txt `
  --context gold\reed_kellogg\pos.txt
```
