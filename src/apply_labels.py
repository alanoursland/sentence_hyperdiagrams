"""Apply a label YAML file to a diagram pass.

Supports two YAML shapes. Transform metadata is always isolated from lexical
entries so ordinary words such as ``pass`` cannot be mistaken for metadata:

1. Lexical maps such as reed_kellogg_01_pos.yaml:

       metadata:
         type: lexical
         output_pass: pos
       vocabulary:
         cat:
           - NOUN
         run:
           - VERB: 0.8
           - NOUN: 0.2

2. Pattern transforms such as reed_kellogg_02_primitives.yaml:

       metadata:
         type: rules
         output_pass: primitives
       rules:
         - emit: SIMPLE_SUBJECT
           pattern: '(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)'

The output file contains the labels produced by this YAML, not a merge of the
input labels and produced labels.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from parts_of_thought.diagram import (
    Label,
    TokenAnnotation,
    parse_pass_file,
    write_pass_file,
)
from parts_of_thought.pattern import Rule, apply_rules


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML label definition file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Label YAML must be a mapping: {path}")
    return data


def is_rule_transform(data: dict[str, Any]) -> bool:
    """Return True if YAML data defines pattern rules."""
    return "rules" in data


def transform_metadata(data: dict[str, Any]) -> dict[str, Any]:
    """Return isolated transform metadata, validating its shape."""
    metadata = data.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("Label YAML metadata must be a mapping")
    return metadata


def load_lexical_map(data: dict[str, Any]) -> dict[str, list[tuple[str, float]]]:
    """Load a word -> [(label, weight)] mapping from POS-style YAML data."""
    vocab: dict[str, list[tuple[str, float]]] = {}

    raw_vocab = data.get("vocabulary", data)
    if not isinstance(raw_vocab, dict):
        raise ValueError("Lexical label YAML vocabulary must be a mapping")

    for word, entries in raw_vocab.items():
        if not isinstance(entries, list):
            continue

        parsed_entries: list[tuple[str, float]] = []
        for entry in entries:
            if isinstance(entry, str):
                parsed_entries.append((entry, 1.0))
            elif isinstance(entry, dict):
                for label_name, weight in entry.items():
                    parsed_entries.append((str(label_name), float(weight)))
            else:
                raise ValueError(
                    f"Unsupported label entry for {word!r}: {entry!r}"
                )

        vocab[str(word).lower()] = parsed_entries

    return vocab


def labels_for_token(
    token: str,
    vocab: dict[str, list[tuple[str, float]]],
) -> list[Label]:
    """Return lexical labels for one token."""
    entries = vocab.get(token.lower())
    if entries is None:
        return [Label("UNKNOWN")]

    if len(entries) == 1:
        label_name, weight = entries[0]
        if weight == 1.0:
            return [Label(label_name)]
        return [Label(label_name, weight=weight)]

    return [Label(label_name, weight=weight) for label_name, weight in entries]


def apply_lexical_map(
    annotations: list[TokenAnnotation],
    vocab: dict[str, list[tuple[str, float]]],
) -> list[TokenAnnotation]:
    """Apply token-level lexical labels to each token."""
    return [
        TokenAnnotation(
            index=ann.index,
            token=ann.token,
            labels=labels_for_token(ann.token, vocab),
        )
        for ann in annotations
    ]


def load_rules(data: dict[str, Any]) -> list[Rule]:
    """Load pattern rules from transform YAML data."""
    raw_rules = data.get("rules")
    if not isinstance(raw_rules, list):
        raise ValueError("Rule transform YAML must contain a rules list")

    rules: list[Rule] = []
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise ValueError(f"Rule must be a mapping: {raw_rule!r}")
        emit = raw_rule.get("emit")
        pattern = raw_rule.get("pattern")
        if not isinstance(emit, str) or not isinstance(pattern, str):
            raise ValueError(f"Rule must define string emit and pattern: {raw_rule!r}")
        weight = float(raw_rule.get("weight", 1.0))
        rules.append(Rule(emit=emit, pattern=pattern, weight=weight))

    return rules


def apply_rule_transform(
    annotations: list[TokenAnnotation],
    rules: list[Rule],
) -> list[TokenAnnotation]:
    """Apply pattern rules and return only labels emitted by this transform."""
    original_counts = [len(ann.labels) for ann in annotations]
    merged = apply_rules(annotations, rules)

    result: list[TokenAnnotation] = []
    for ann, original_count in zip(merged, original_counts):
        result.append(
            TokenAnnotation(
                index=ann.index,
                token=ann.token,
                labels=ann.labels[original_count:],
            )
        )

    return result


def build_metadata(
    labels_path: Path,
    input_path: Path,
    data: dict[str, Any],
) -> dict[str, str]:
    """Build output pass metadata."""
    transform = transform_metadata(data)
    pass_name = str(
        transform.get("output_pass") or transform.get("pass") or "labels"
    )
    metadata = {
        "pass": pass_name,
        "source": str(input_path),
        "labels": str(labels_path),
        "generated_by": "src/apply_labels.py",
    }
    if "ontology" in transform:
        metadata["ontology"] = str(transform["ontology"])
    return metadata


def apply_label_file(
    labels_path: str | Path,
    input_path: str | Path,
    output_path: str | Path,
) -> list[TokenAnnotation]:
    """Apply labels_path to input_path and write output_path."""
    labels_path = Path(labels_path)
    input_path = Path(input_path)
    output_path = Path(output_path)

    data = load_yaml(labels_path)
    annotations = parse_pass_file(input_path)

    if is_rule_transform(data):
        output = apply_rule_transform(annotations, load_rules(data))
    else:
        output = apply_lexical_map(annotations, load_lexical_map(data))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_pass_file(
        output_path,
        output,
        metadata=build_metadata(labels_path, input_path, data),
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply a label YAML file to a diagram pass."
    )
    parser.add_argument("--labels", required=True, help="Label YAML path")
    parser.add_argument("--in", dest="input", required=True, help="Input pass path")
    parser.add_argument("--out", required=True, help="Output pass path")
    args = parser.parse_args()

    output = apply_label_file(args.labels, args.input, args.out)
    label_count = sum(len(ann.labels) for ann in output)
    print(f"Wrote {label_count} labels -> {args.out}")


if __name__ == "__main__":
    main()
