"""Tests for the generic apply_labels command helpers."""

from pathlib import Path

from parts_of_thought.diagram import Label, TokenAnnotation
from apply_labels import (
    apply_lexical_map,
    apply_rule_transform,
    build_metadata,
    labels_for_token,
    load_lexical_map,
    load_rules,
)


def test_load_lexical_map_supports_weighted_entries():
    vocab = load_lexical_map({
        "run": [{"VERB": 0.8}, {"NOUN": 0.2}],
        ".": ["PERIOD"],
    })

    assert vocab == {
        "run": [("VERB", 0.8), ("NOUN", 0.2)],
        ".": [("PERIOD", 1.0)],
    }


def test_lexical_metadata_is_separate_from_word_named_pass():
    data = {
        "metadata": {
            "type": "lexical",
            "output_pass": "pos",
            "ontology": "reed_kellogg",
        },
        "vocabulary": {
            "pass": ["VERB"],
        },
    }

    assert load_lexical_map(data) == {"pass": [("VERB", 1.0)]}
    assert build_metadata(
        Path("ontology/pos.yaml"), Path("tokens.txt"), data
    )["pass"] == "pos"


def test_labels_for_unknown_token():
    assert labels_for_token("missing", {}) == [Label("UNKNOWN")]


def test_apply_lexical_map_outputs_generated_labels_only():
    anns = [
        TokenAnnotation(index=0, token="run", labels=[]),
        TokenAnnotation(index=1, token=".", labels=[]),
    ]
    vocab = {
        "run": [("VERB", 0.8), ("NOUN", 0.2)],
        ".": [("PERIOD", 1.0)],
    }

    result = apply_lexical_map(anns, vocab)

    assert result == [
        TokenAnnotation(index=0, token="run", labels=[
            Label("VERB", weight=0.8),
            Label("NOUN", weight=0.2),
        ]),
        TokenAnnotation(index=1, token=".", labels=[Label("PERIOD")]),
    ]


def test_apply_rule_transform_outputs_generated_labels_only():
    anns = [
        TokenAnnotation(index=0, token="A", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="cat", labels=[Label("NOUN")]),
        TokenAnnotation(index=2, token="and", labels=[Label("CONJUNCTION")]),
        TokenAnnotation(index=3, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=4, token="rat", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_SUBJECT",
                "pattern": '(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
            },
            {
                "emit": "SIMPLE_SUBJECT",
                "pattern": "SIMPLE_SUBJECT CONJUNCTION @ARTICLE? (NOUN|PRONOUN)",
            },
            {
                "emit": "COMPOUND_SUBJECT",
                "pattern": "@SIMPLE_SUBJECT CONJUNCTION SIMPLE_SUBJECT",
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result == [
        TokenAnnotation(index=0, token="A", labels=[]),
        TokenAnnotation(index=1, token="cat", labels=[
            Label(
                "SIMPLE_SUBJECT",
                child_prev="ARTICLE",
                child_curr="NOUN",
                index_prev=0,
            ),
        ]),
        TokenAnnotation(index=2, token="and", labels=[]),
        TokenAnnotation(index=3, token="a", labels=[]),
        TokenAnnotation(index=4, token="rat", labels=[
            Label(
                "SIMPLE_SUBJECT",
                child_prev="ARTICLE",
                child_curr="NOUN",
                index_prev=3,
            ),
            Label(
                "COMPOUND_SUBJECT",
                child_prev="SIMPLE_SUBJECT",
                child_curr="SIMPLE_SUBJECT",
                index_prev=1,
            ),
        ]),
    ]


def test_apply_rule_transform_uses_period_as_boundary():
    anns = [
        TokenAnnotation(index=0, token=".", labels=[Label("PUNCT")]),
        TokenAnnotation(index=1, token="Ann", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_SUBJECT",
                "pattern": '(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[1].labels == [Label("SIMPLE_SUBJECT")]


def test_apply_rule_transform_subject_allows_possessive_modifier():
    anns = [
        TokenAnnotation(index=0, token=".", labels=[Label("PERIOD")]),
        TokenAnnotation(index=1, token="Tom's", labels=[
            Label("ADJECTIVE"),
            Label("POSSESSIVE_NOUN"),
        ]),
        TokenAnnotation(index=2, token="nag", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_SUBJECT",
                "pattern": '(BOF|"."|"?"|"!") @ADJECTIVE? @ARTICLE? (NOUN|PRONOUN)',
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[2].labels == [
        Label(
            "SIMPLE_SUBJECT",
            child_prev="ADJECTIVE",
            child_curr="NOUN",
            index_prev=1,
        )
    ]


def test_apply_rule_transform_builds_recursive_noun_before_role():
    anns = [
        TokenAnnotation(index=0, token="has", labels=[Label("VERB")]),
        TokenAnnotation(index=1, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="fat", labels=[Label("ADJECTIVE")]),
        TokenAnnotation(index=3, token="dog", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {"emit": "NOUN", "pattern": "@ADJECTIVE NOUN"},
            {"emit": "NOUN", "pattern": "@ARTICLE NOUN"},
            {
                "emit": "SIMPLE_OBJECT_COMPLEMENT",
                "pattern": "(VERB|VERB_PHRASE) NOUN",
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[3].labels == [
        Label(
            "NOUN",
            child_prev="ADJECTIVE",
            child_curr="NOUN",
            index_prev=2,
        ),
        Label(
            "NOUN",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=1,
        ),
        Label("SIMPLE_OBJECT_COMPLEMENT"),
    ]


def test_apply_rule_transform_adds_simple_object_complement():
    anns = [
        TokenAnnotation(index=0, token="has", labels=[Label("VERB")]),
        TokenAnnotation(index=1, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="rat", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_OBJECT_COMPLEMENT",
                "pattern": "(VERB|VERB_PHRASE) @ARTICLE? (NOUN|PRONOUN)",
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[2].labels == [
        Label(
            "SIMPLE_OBJECT_COMPLEMENT",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=1,
        )
    ]


def test_apply_rule_transform_adds_compound_object_complement():
    anns = [
        TokenAnnotation(index=0, token="has", labels=[Label("VERB")]),
        TokenAnnotation(index=1, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="cat", labels=[Label("NOUN")]),
        TokenAnnotation(index=3, token="and", labels=[Label("CONJUNCTION")]),
        TokenAnnotation(index=4, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=5, token="rat", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_OBJECT_COMPLEMENT",
                "pattern": "(VERB|VERB_PHRASE) @ARTICLE? (NOUN|PRONOUN)",
            },
            {
                "emit": "SIMPLE_OBJECT_COMPLEMENT",
                "pattern": (
                    "SIMPLE_OBJECT_COMPLEMENT CONJUNCTION "
                    "@ARTICLE? (NOUN|PRONOUN)"
                ),
            },
            {
                "emit": "COMPOUND_OBJECT_COMPLEMENT",
                "pattern": (
                    "@SIMPLE_OBJECT_COMPLEMENT CONJUNCTION "
                    "SIMPLE_OBJECT_COMPLEMENT"
                ),
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[5].labels == [
        Label(
            "SIMPLE_OBJECT_COMPLEMENT",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=4,
        ),
        Label(
            "COMPOUND_OBJECT_COMPLEMENT",
            child_prev="SIMPLE_OBJECT_COMPLEMENT",
            child_curr="SIMPLE_OBJECT_COMPLEMENT",
            index_prev=2,
        ),
    ]


def test_apply_rule_transform_adds_simple_prepositional_principal():
    anns = [
        TokenAnnotation(index=0, token="at", labels=[Label("PREPOSITION")]),
        TokenAnnotation(index=1, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="cat", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_PREPOSITIONAL_PRINCIPAL",
                "pattern": "PREPOSITION @ARTICLE? (NOUN|PRONOUN)",
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[2].labels == [
        Label(
            "SIMPLE_PREPOSITIONAL_PRINCIPAL",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=1,
        )
    ]


def test_apply_rule_transform_adds_compound_prepositional_principal():
    anns = [
        TokenAnnotation(index=0, token="at", labels=[Label("PREPOSITION")]),
        TokenAnnotation(index=1, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="cat", labels=[Label("NOUN")]),
        TokenAnnotation(index=3, token="and", labels=[Label("CONJUNCTION")]),
        TokenAnnotation(index=4, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=5, token="rat", labels=[Label("NOUN")]),
    ]
    rules = load_rules({
        "rules": [
            {
                "emit": "SIMPLE_PREPOSITIONAL_PRINCIPAL",
                "pattern": "PREPOSITION @ARTICLE? (NOUN|PRONOUN)",
            },
            {
                "emit": "SIMPLE_PREPOSITIONAL_PRINCIPAL",
                "pattern": (
                    "SIMPLE_PREPOSITIONAL_PRINCIPAL CONJUNCTION "
                    "@ARTICLE? (NOUN|PRONOUN)"
                ),
            },
            {
                "emit": "COMPOUND_PREPOSITIONAL_PRINCIPAL",
                "pattern": (
                    "@SIMPLE_PREPOSITIONAL_PRINCIPAL CONJUNCTION "
                    "SIMPLE_PREPOSITIONAL_PRINCIPAL"
                ),
            },
        ],
    })

    result = apply_rule_transform(anns, rules)

    assert result[5].labels == [
        Label(
            "SIMPLE_PREPOSITIONAL_PRINCIPAL",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=4,
        ),
        Label(
            "COMPOUND_PREPOSITIONAL_PRINCIPAL",
            child_prev="SIMPLE_PREPOSITIONAL_PRINCIPAL",
            child_curr="SIMPLE_PREPOSITIONAL_PRINCIPAL",
            index_prev=2,
        ),
    ]
