"""Tests for the generic apply_labels command helpers."""

from parts_of_thought.diagram import Label, TokenAnnotation
from apply_labels import (
    apply_lexical_map,
    apply_rule_transform,
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
