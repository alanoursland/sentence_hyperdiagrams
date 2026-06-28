"""Auto-generate POS annotation pass files using the vocabulary.

Reads tokenized files and the POS vocabulary, writes pass files
with leaf POS labels (including weights for ambiguous words).
"""

from pathlib import Path

import yaml

from parts_of_thought.diagram import (
    Label,
    TokenAnnotation,
    parse_tokens_file,
    write_pass_file,
)

TOKENIZED_DIR = Path("diagrams/tokenized")
VOCAB_PATH = Path("ontology/reed_kellogg_pos.yaml")
OUTPUT_BASE = Path("diagrams/reed_kellogg")

SOURCES = [
    "mcguffey_primer",
    "mcguffey_first_reader",
    "beacon_second_reader",
    "fifty_famous_stories",
]


def load_vocabulary(path: Path) -> dict[str, list[tuple[str, float]]]:
    """Load the POS vocabulary YAML.

    Returns dict: lowercase word -> list of (POS, weight) tuples.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    vocab: dict[str, list[tuple[str, float]]] = {}

    for word, tags in raw.items():
        word = str(word).lower()
        entries: list[tuple[str, float]] = []
        for tag in tags:
            if isinstance(tag, str):
                entries.append((tag, 1.0))
            elif isinstance(tag, dict):
                for pos, weight in tag.items():
                    entries.append((pos, float(weight)))
        vocab[word] = entries

    return vocab


def tag_token(
    token: str,
    vocab: dict[str, list[tuple[str, float]]],
) -> list[Label]:
    """Look up POS labels for a token.

    Returns list of Label objects with appropriate weights.
    """
    key = token.lower()
    if key not in vocab:
        return [Label(name="UNKNOWN")]

    entries = vocab[key]
    if len(entries) == 1:
        pos, weight = entries[0]
        return [Label(name=pos)]

    return [Label(name=pos, weight=weight) for pos, weight in entries]


def tag_tokens(
    annotations: list[TokenAnnotation],
    vocab: dict[str, list[tuple[str, float]]],
) -> list[TokenAnnotation]:
    """Apply POS tags to all tokens."""
    result: list[TokenAnnotation] = []
    for ann in annotations:
        labels = tag_token(ann.token, vocab)
        result.append(TokenAnnotation(
            index=ann.index, token=ann.token, labels=labels,
        ))
    return result


def autotag_source(
    source: str,
    vocab: dict[str, list[tuple[str, float]]],
) -> dict[str, int]:
    """Auto-tag a single source file. Returns stats."""
    input_path = TOKENIZED_DIR / f"{source}.txt"
    output_dir = OUTPUT_BASE / source
    output_path = output_dir / "pos.txt"

    tokens = parse_tokens_file(input_path)
    tagged = tag_tokens(tokens, vocab)

    metadata = {
        "pass": "pos",
        "ontology": "reed_kellogg",
        "focus": "parts of speech",
        "source": str(input_path),
        "generated_by": "scripts/autotag_pos.py",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_pass_file(output_path, tagged, metadata)

    # Compute stats.
    stats: dict[str, int] = {"total": 0, "tagged": 0, "ambiguous": 0, "unknown": 0}
    unknown_words: set[str] = set()
    for ann in tagged:
        stats["total"] += 1
        if len(ann.labels) == 1 and ann.labels[0].name == "UNKNOWN":
            stats["unknown"] += 1
            unknown_words.add(ann.token.lower())
        elif len(ann.labels) > 1:
            stats["ambiguous"] += 1
            stats["tagged"] += 1
        else:
            stats["tagged"] += 1

    print(f"{source}:")
    print(f"  {stats['total']} tokens, {stats['tagged']} tagged, "
          f"{stats['ambiguous']} ambiguous, {stats['unknown']} unknown")
    print(f"  -> {output_path}")

    return stats


def main() -> None:
    vocab = load_vocabulary(VOCAB_PATH)
    print(f"Loaded {len(vocab)} vocabulary entries\n")

    totals: dict[str, int] = {"total": 0, "tagged": 0, "ambiguous": 0, "unknown": 0}
    for source in SOURCES:
        stats = autotag_source(source, vocab)
        for k in totals:
            totals[k] += stats[k]
        print()

    print(f"Overall: {totals['total']} tokens, {totals['tagged']} tagged, "
          f"{totals['ambiguous']} ambiguous, {totals['unknown']} unknown")
    coverage = totals["tagged"] / totals["total"] * 100 if totals["total"] else 0
    print(f"Coverage: {coverage:.1f}%")


if __name__ == "__main__":
    main()
