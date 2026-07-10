"""Consistency checks across the Reed-Kellogg ontology and transforms."""

from pathlib import Path

import yaml

from parts_of_thought.pattern import (
    Capture,
    Group,
    LabelAtom,
    Optional,
    SentinelAtom,
    Sequence,
    TokenLiteral,
    Union,
    parse_pattern,
)


ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_PATH = ROOT / "ontology" / "reed_kellogg.yaml"
DEPENDENCIES_PATH = ROOT / "ontology" / "reed_kellogg_dependencies.yaml"
PRIMITIVES_PATH = ROOT / "ontology" / "reed_kellogg_02_primitives.yaml"
POS_PATH = ROOT / "ontology" / "reed_kellogg_01_pos.yaml"


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def walk_pattern(element):
    """Yield the semantic atoms in a parsed pattern AST."""
    if isinstance(element, (LabelAtom, TokenLiteral, SentinelAtom)):
        yield element
    elif isinstance(element, (Group, Optional, Capture)):
        yield from walk_pattern(element.element)
    elif isinstance(element, Sequence):
        for child in element.elements:
            yield from walk_pattern(child)
    elif isinstance(element, Union):
        for child in element.alternatives:
            yield from walk_pattern(child)
    else:  # pragma: no cover - forces updates when the AST grows
        raise AssertionError(f"Unhandled pattern element: {type(element).__name__}")


def test_every_ontology_entry_has_description_and_source():
    ontology = load_yaml(ONTOLOGY_PATH)
    for name, entry in ontology.items():
        assert isinstance(entry, dict), name
        assert (
            isinstance(entry.get("description"), str)
            and entry["description"].strip()
        ), name
        assert isinstance(entry.get("source"), str) and entry["source"].strip(), name


def test_rule_emissions_and_atoms_exist_in_ontology():
    ontology_names = set(load_yaml(ONTOLOGY_PATH))
    transform = load_yaml(PRIMITIVES_PATH)

    assert set(transform["labels"]) <= ontology_names

    for rule in transform["rules"]:
        assert rule["emit"] in ontology_names
        for atom in walk_pattern(parse_pattern(rule["pattern"])):
            if isinstance(atom, LabelAtom):
                assert atom.name in ontology_names
            elif isinstance(atom, SentinelAtom):
                assert atom.name == "BOF"
            else:
                assert isinstance(atom, TokenLiteral)


def test_lexical_vocabulary_labels_exist_in_ontology():
    ontology_names = set(load_yaml(ONTOLOGY_PATH))
    lexical = load_yaml(POS_PATH)

    assert lexical["metadata"]["type"] == "lexical"
    assert lexical["metadata"]["output_pass"] == "pos"
    for entries in lexical["vocabulary"].values():
        for entry in entries:
            label = entry if isinstance(entry, str) else next(iter(entry))
            assert label in ontology_names


def test_every_dependency_label_exists_in_ontology():
    ontology_names = set(load_yaml(ONTOLOGY_PATH))
    dependencies = load_yaml(DEPENDENCIES_PATH)

    for child, parents in dependencies["is_a"].items():
        assert child in ontology_names
        assert parents
        assert set(parents) <= ontology_names

    for result, alternatives in dependencies["builds_from"].items():
        assert result in ontology_names
        assert alternatives
        for inputs in alternatives:
            assert inputs
            assert set(inputs) <= ontology_names

    for labels in dependencies["conventions"].values():
        assert labels
        assert set(labels) <= ontology_names


def test_canonical_label_conventions_are_explicit_and_observed():
    dependencies = load_yaml(DEPENDENCIES_PATH)
    transform = load_yaml(PRIMITIVES_PATH)
    conventions = dependencies["conventions"]
    emitted = {rule["emit"] for rule in transform["rules"]}

    assert set(conventions["abstract_labels"]).isdisjoint(emitted)
    assert "SIMPLE_SUBJECT" in conventions["concrete_annotation_labels"]
    assert conventions["recursive_projection_labels"] == ["NOUN"]
    assert ["NOUN", "ADJECTIVE"] in dependencies["builds_from"]["NOUN"]
    assert "NOUN" in emitted
