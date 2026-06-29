"""Tokenize all early_reader sentence files into diagrams/tokenized/."""

from pathlib import Path

from parts_of_thought.diagram import tokenize, write_tokens

SENTENCES_DIR = Path("data/early_reader/sentences")
OUTPUT_DIR = Path("diagrams/tokenized")

# Skip combined.txt — it's a concatenation of the others.
SOURCES = [
    "mcguffey_primer",
    "mcguffey_first_reader",
    "beacon_second_reader",
    "fifty_famous_stories",
]


def tokenize_file(source: str) -> None:
    input_path = SENTENCES_DIR / f"{source}.txt"
    output_path = OUTPUT_DIR / f"{source}.txt"

    lines = input_path.read_text(encoding="utf-8").splitlines()

    all_tokens = []
    index = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        sentence_tokens = tokenize(line, start_index=index)
        all_tokens.extend(sentence_tokens)
        index = all_tokens[-1].index + 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(write_tokens(all_tokens), encoding="utf-8")

    print(f"{source}: {len(lines)} sentences, {len(all_tokens)} tokens -> {output_path}")


def main() -> None:
    for source in SOURCES:
        tokenize_file(source)


if __name__ == "__main__":
    main()
