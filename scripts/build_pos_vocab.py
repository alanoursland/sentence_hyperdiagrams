"""Build the Reed-Kellogg POS vocabulary from tokenized datasets.

Extracts unique tokens, auto-classifies closed classes and applies
suffix heuristics, then writes ontology/reed_kellogg_pos.yaml.
"""

from collections import Counter
from pathlib import Path

from parts_of_thought.diagram import parse_tokens_file

TOKENIZED_DIR = Path("diagrams/tokenized")
OUTPUT_PATH = Path("ontology/reed_kellogg_pos.yaml")

SOURCES = [
    "mcguffey_primer",
    "mcguffey_first_reader",
    "beacon_second_reader",
    "fifty_famous_stories",
]

# ---- Closed-class dictionaries ----

PUNCT_TOKENS = {".", ",", "!", "?", ";", ":"}

ARTICLES = {"the", "a", "an"}

CONJUNCTIONS = {
    "and", "but", "or", "nor",
    "because", "although", "though", "unless", "whether",
    "if", "when", "while", "whereas",
}

PREPOSITIONS = {
    "of", "to", "in", "on", "at", "by", "from", "with",
    "into", "upon", "through", "between", "among", "above",
    "under", "below", "behind", "beside", "besides", "across",
    "along", "around", "against", "toward", "towards",
    "within", "without", "except", "until", "during",
    "near", "past", "beyond",
}

PRONOUNS = {
    # Personal subject
    "i", "you", "he", "she", "it", "we", "they",
    # Personal object
    "me", "him", "her", "us", "them",
    # Possessive (pronoun form)
    "mine", "yours", "hers", "ours", "theirs",
    # Possessive (adjective form -- Reed-Kellogg treats as pronoun)
    "my", "your", "our", "their",
    # Demonstrative
    "this", "these", "those",
    # Relative / interrogative
    "who", "whom", "whose", "which",
    # Reflexive
    "myself", "yourself", "himself", "herself", "itself",
    "ourselves", "themselves",
    # Indefinite
    "everybody", "nobody", "somebody", "anybody",
    "everyone", "someone", "anyone", "no one",
    "everything", "something", "anything", "nothing",
    "whoever", "whatever",
    "each", "other", "another",
}

ADVERBS = {
    "not", "never", "always", "ever", "often",
    "now", "then", "soon", "already", "still", "yet",
    "here", "there", "where", "everywhere", "nowhere",
    "very", "too", "quite", "almost", "rather", "just",
    "also", "again", "away", "back",
    "how", "why",
}

INTERJECTIONS = {
    "oh", "ah", "alas", "hurrah", "lo", "hark",
    "hush", "pooh", "bravo",
}

# ---- Ambiguous words (with weights) ----

AMBIGUOUS: dict[str, list[tuple[str, float]]] = {
    "that": [("PRONOUN", 0.5), ("CONJUNCTION", 0.5)],
    "what": [("PRONOUN", 0.7), ("INTERJECTION", 0.3)],
    "for": [("PREPOSITION", 0.7), ("CONJUNCTION", 0.3)],
    "so": [("ADVERB", 0.6), ("CONJUNCTION", 0.4)],
    "as": [("ADVERB", 0.4), ("CONJUNCTION", 0.3), ("PREPOSITION", 0.3)],
    "before": [("PREPOSITION", 0.5), ("CONJUNCTION", 0.3), ("ADVERB", 0.2)],
    "after": [("PREPOSITION", 0.6), ("CONJUNCTION", 0.4)],
    "since": [("PREPOSITION", 0.4), ("CONJUNCTION", 0.4), ("ADVERB", 0.2)],
    "down": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "up": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "out": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "off": [("ADVERB", 0.6), ("PREPOSITION", 0.4)],
    "over": [("PREPOSITION", 0.5), ("ADVERB", 0.5)],
    "about": [("PREPOSITION", 0.6), ("ADVERB", 0.4)],
    "like": [("VERB", 0.4), ("PREPOSITION", 0.3), ("ADJECTIVE", 0.3)],
    "well": [("ADVERB", 0.5), ("INTERJECTION", 0.3), ("NOUN", 0.2)],
    "right": [("ADJECTIVE", 0.4), ("ADVERB", 0.3), ("NOUN", 0.3)],
    "no": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "yes": [("INTERJECTION", 0.5), ("ADVERB", 0.5)],
    "once": [("ADVERB", 0.6), ("CONJUNCTION", 0.4)],
    "only": [("ADVERB", 0.6), ("ADJECTIVE", 0.4)],
    "even": [("ADVERB", 0.6), ("ADJECTIVE", 0.4)],
    "much": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "more": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "most": [("ADVERB", 0.5), ("ADJECTIVE", 0.5)],
    "all": [("ADJECTIVE", 0.5), ("PRONOUN", 0.3), ("ADVERB", 0.2)],
    "some": [("ADJECTIVE", 0.5), ("PRONOUN", 0.5)],
    "many": [("ADJECTIVE", 0.5), ("PRONOUN", 0.5)],
    "one": [("PRONOUN", 0.5), ("ADJECTIVE", 0.3), ("NOUN", 0.2)],
}

# ---- Suffix heuristics ----

SUFFIX_RULES: list[tuple[str, str]] = [
    ("ly", "ADVERB"),
    ("ing", "VERB"),
    ("ed", "VERB"),
    ("tion", "NOUN"),
    ("sion", "NOUN"),
    ("ment", "NOUN"),
    ("ness", "NOUN"),
    ("ful", "ADJECTIVE"),
    ("ous", "ADJECTIVE"),
    ("ive", "ADJECTIVE"),
    ("able", "ADJECTIVE"),
    ("ible", "ADJECTIVE"),
    ("less", "ADJECTIVE"),
    ("est", "ADJECTIVE"),
    ("er", "NOUN"),
]


def extract_tokens() -> tuple[Counter, dict[str, set[str]]]:
    """Extract all tokens from tokenized files.

    Returns (lowercase_counts, lowercase_to_forms).
    """
    counts: Counter = Counter()
    forms: dict[str, set[str]] = {}

    for source in SOURCES:
        path = TOKENIZED_DIR / f"{source}.txt"
        annotations = parse_tokens_file(path)
        for ann in annotations:
            lower = ann.token.lower()
            counts[lower] += 1
            forms.setdefault(lower, set()).add(ann.token)

    return counts, forms


def classify_token(
    word: str, word_forms: set[str], all_forms: dict[str, set[str]],
) -> list[tuple[str, float]] | None:
    """Classify a word into POS tag(s) with weights.

    Returns list of (POS, weight) tuples, or None if unclassified.
    """
    # Punctuation.
    if word in PUNCT_TOKENS:
        return [("PUNCT", 1.0)]

    # Ambiguous (checked before closed classes to override).
    if word in AMBIGUOUS:
        return AMBIGUOUS[word]

    # Closed classes.
    if word in ARTICLES:
        return [("ARTICLE", 1.0)]
    if word in CONJUNCTIONS:
        return [("CONJUNCTION", 1.0)]
    if word in PREPOSITIONS:
        return [("PREPOSITION", 1.0)]
    if word in PRONOUNS:
        return [("PRONOUN", 1.0)]
    if word in ADVERBS:
        return [("ADVERB", 1.0)]
    if word in INTERJECTIONS:
        return [("INTERJECTION", 1.0)]

    # Contractions.
    if word.endswith("n't"):
        return [("VERB", 1.0)]
    if any(word.endswith(s) for s in ("'m", "'re", "'ve", "'ll", "'d")):
        return [("VERB", 1.0)]
    if word.endswith("'s"):
        return [("NOUN", 1.0)]

    # Proper noun detection: only appears capitalized.
    if all(f[0].isupper() for f in word_forms) and word[0].isalpha():
        # Check it's not a common word that just happens to start sentences.
        # If a word ONLY ever appears capitalized, it's likely proper.
        return [("NOUN", 1.0)]

    # Suffix heuristics (only for longer words to avoid false positives).
    if len(word) >= 4:
        for suffix, pos in SUFFIX_RULES:
            if word.endswith(suffix):
                return [(pos, 1.0)]

    return None


def build_vocabulary() -> dict[str, list[tuple[str, float]]]:
    """Build the complete vocabulary mapping."""
    counts, forms = extract_tokens()
    vocab: dict[str, list[tuple[str, float]]] = {}

    for word in sorted(counts.keys()):
        result = classify_token(word, forms[word], forms)
        if result is not None:
            vocab[word] = result

    return vocab


def write_yaml(
    vocab: dict[str, list[tuple[str, float]]],
    counts: Counter,
    path: Path,
) -> None:
    """Write the vocabulary to YAML."""
    lines: list[str] = [
        "# Reed-Kellogg POS Vocabulary",
        "# Maps each word (lowercase) to its possible POS tags.",
        "# Ambiguous words have explicit weights (should sum to 1.0).",
        "#",
        "# Generated by scripts/build_pos_vocab.py",
        "# Edit manually to add/correct POS tags.",
        "",
    ]

    for word, tags in sorted(vocab.items(), key=lambda kv: -counts[kv[0]]):
        # YAML-quote keys that need it.
        key = f'"{word}"' if word in PUNCT_TOKENS or word == "no" else word
        lines.append(f"{key}:")
        for pos, weight in tags:
            if weight == 1.0:
                lines.append(f"  - {pos}")
            else:
                lines.append(f"  - {pos}: {weight}")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def print_stats(
    vocab: dict[str, list[tuple[str, float]]],
    total_unique: int,
) -> None:
    """Print classification statistics."""
    classified = len(vocab)
    ambiguous = sum(1 for tags in vocab.values() if len(tags) > 1)
    unambiguous = classified - ambiguous

    by_pos: Counter = Counter()
    for tags in vocab.values():
        for pos, _ in tags:
            by_pos[pos] += 1

    print(f"Total unique tokens: {total_unique}")
    print(f"Classified: {classified}")
    print(f"  Unambiguous: {unambiguous}")
    print(f"  Ambiguous (weighted): {ambiguous}")
    print(f"  Unclassified: {total_unique - classified}")
    print()
    print("By POS tag:")
    for pos, count in by_pos.most_common():
        print(f"  {pos}: {count}")


def main() -> None:
    counts, forms = extract_tokens()
    vocab: dict[str, list[tuple[str, float]]] = {}

    for word in sorted(counts.keys()):
        result = classify_token(word, forms[word], forms)
        if result is not None:
            vocab[word] = result

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(vocab, counts, OUTPUT_PATH)
    print_stats(vocab, len(counts))
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
