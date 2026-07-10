"""Tests for the right-to-left pattern language."""

from parts_of_thought.diagram import Label, TokenAnnotation
from parts_of_thought.pattern import (
    Capture,
    Group,
    LabelAtom,
    Optional,
    Rule,
    Sequence,
    TokenLiteral,
    Union,
    apply_rules,
    apply_rule_at,
    compute_label_span,
    parse_pattern,
)


def test_parse_group_union_optional_capture():
    pattern = parse_pattern('(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)')

    assert isinstance(pattern, Sequence)
    assert len(pattern.elements) == 3

    boundary = pattern.elements[0]
    assert isinstance(boundary, Group)
    assert isinstance(boundary.element, Union)
    assert len(boundary.element.alternatives) == 4
    assert isinstance(boundary.element.alternatives[1], TokenLiteral)
    assert boundary.element.alternatives[1].value == "."

    capture = pattern.elements[1]
    assert isinstance(capture, Capture)
    assert isinstance(capture.element, Optional)
    assert isinstance(capture.element.element, LabelAtom)
    assert capture.element.element.name == "ARTICLE"

    current = pattern.elements[2]
    assert isinstance(current, Group)
    assert isinstance(current.element, Union)


def test_simple_subject_with_article_from_bof():
    anns = [
        TokenAnnotation(index=0, token="A", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="cat", labels=[Label("NOUN")]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=1,
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
    )

    assert emitted == Label(
        name="SIMPLE_SUBJECT",
        child_prev="ARTICLE",
        child_curr="NOUN",
        index_prev=0,
    )


def test_simple_subject_without_article_from_bof_is_leaf():
    anns = [
        TokenAnnotation(index=0, token="Ann", labels=[Label("NOUN")]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=0,
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
    )

    assert emitted == Label(name="SIMPLE_SUBJECT")


def test_simple_subject_after_literal_period():
    anns = [
        TokenAnnotation(index=0, token=".", labels=[Label("PERIOD")]),
        TokenAnnotation(index=1, token="The", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="cat", labels=[Label("NOUN")]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=2,
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
    )

    assert emitted == Label(
        name="SIMPLE_SUBJECT",
        child_prev="ARTICLE",
        child_curr="NOUN",
        index_prev=1,
    )


def test_simple_subject_can_capture_adjective_modifier():
    anns = [
        TokenAnnotation(index=0, token=".", labels=[Label("PERIOD")]),
        TokenAnnotation(index=1, token="Tom's", labels=[
            Label("ADJECTIVE"),
            Label("POSSESSIVE_NOUN"),
        ]),
        TokenAnnotation(index=2, token="nag", labels=[Label("NOUN")]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=2,
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ADJECTIVE? @ARTICLE? (NOUN|PRONOUN)',
    )

    assert emitted == Label(
        name="SIMPLE_SUBJECT",
        child_prev="ADJECTIVE",
        child_curr="NOUN",
        index_prev=1,
    )


def test_pattern_does_not_treat_period_label_as_literal_period():
    anns = [
        TokenAnnotation(index=0, token="not-a-dot", labels=[Label("PERIOD")]),
        TokenAnnotation(index=1, token="The", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=2, token="cat", labels=[Label("NOUN")]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=2,
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
    )

    assert emitted is None


def test_label_span_for_linking_label():
    label = Label(
        name="SIMPLE_SUBJECT",
        child_prev="ARTICLE",
        child_curr="NOUN",
        index_prev=0,
    )
    anns = [
        TokenAnnotation(index=0, token="A", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="cat", labels=[Label("NOUN"), label]),
    ]

    span = compute_label_span(anns, token_index=1, label=label)

    assert span.left == 0
    assert span.right == 1


def test_same_name_child_resolves_to_previous_label_on_token():
    first = Label(
        name="NOUN",
        child_prev="ADJECTIVE",
        child_curr="NOUN",
        index_prev=1,
    )
    second = Label(
        name="NOUN",
        child_prev="ARTICLE",
        child_curr="NOUN",
        index_prev=0,
    )
    anns = [
        TokenAnnotation(index=0, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="fat", labels=[Label("ADJECTIVE")]),
        TokenAnnotation(index=2, token="dog", labels=[
            Label("NOUN"),
            first,
            second,
        ]),
    ]

    first_span = compute_label_span(anns, token_index=2, label=first)
    second_span = compute_label_span(anns, token_index=2, label=second)

    assert first_span.left == 1
    assert first_span.right == 2
    assert second_span.left == 0
    assert second_span.right == 2


def test_recursive_noun_projection_absorbs_article_and_adjective():
    anns = [
        TokenAnnotation(index=0, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="fat", labels=[Label("ADJECTIVE")]),
        TokenAnnotation(index=2, token="dog", labels=[Label("NOUN")]),
    ]
    rules = [
        Rule(emit="NOUN", pattern="@ADJECTIVE NOUN"),
        Rule(emit="NOUN", pattern="@ARTICLE NOUN"),
    ]

    result = apply_rules(anns, rules)

    assert result[2].labels == [
        Label("NOUN"),
        Label(
            "NOUN",
            child_prev="ADJECTIVE",
            child_curr="NOUN",
            index_prev=1,
        ),
        Label(
            "NOUN",
            child_prev="ARTICLE",
            child_curr="NOUN",
            index_prev=0,
        ),
    ]


def test_compound_subject_consumes_subject_span():
    anns = [
        TokenAnnotation(index=0, token="A", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=1, token="cat", labels=[
            Label("NOUN"),
            Label(
                "SIMPLE_SUBJECT",
                child_prev="ARTICLE",
                child_curr="NOUN",
                index_prev=0,
            ),
        ]),
        TokenAnnotation(index=2, token="and", labels=[Label("CONJUNCTION")]),
        TokenAnnotation(index=3, token="a", labels=[Label("ARTICLE")]),
        TokenAnnotation(index=4, token="rat", labels=[
            Label("NOUN"),
            Label(
                "SIMPLE_SUBJECT",
                child_prev="ARTICLE",
                child_curr="NOUN",
                index_prev=3,
            ),
        ]),
    ]

    emitted = apply_rule_at(
        anns,
        token_index=4,
        emit="COMPOUND_SUBJECT",
        pattern="@SIMPLE_SUBJECT CONJUNCTION SIMPLE_SUBJECT",
    )

    assert emitted == Label(
        name="COMPOUND_SUBJECT",
        child_prev="SIMPLE_SUBJECT",
        child_curr="SIMPLE_SUBJECT",
        index_prev=1,
    )


def test_rule_weight_defaults_to_one():
    rule = Rule(
        emit="SIMPLE_SUBJECT",
        pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
    )

    assert rule.weight == 1.0


def test_rule_confidence_is_bounded_by_weakest_matched_label():
    anns = [
        TokenAnnotation(
            index=0,
            token="run",
            labels=[Label("VERB", weight=0.8), Label("NOUN", weight=0.2)],
        ),
    ]

    emitted = Rule(emit="SIMPLE_SUBJECT", pattern="NOUN", weight=0.5).apply_at(
        anns, 0
    )

    assert emitted is not None
    assert emitted.name == "SIMPLE_SUBJECT"
    assert emitted.weight == 0.1


def test_apply_rules_makes_emitted_labels_visible_to_later_rules():
    anns = [
        TokenAnnotation(index=0, token="Ann", labels=[Label("NOUN")]),
    ]
    rules = [
        Rule(
            emit="SIMPLE_SUBJECT",
            pattern='(BOF|"."|"?"|"!") @ARTICLE? (NOUN|PRONOUN)',
        ),
        Rule(
            emit="SUBJECT",
            pattern="SIMPLE_SUBJECT",
        ),
    ]

    result = apply_rules(anns, rules)

    assert result[0].labels == [
        Label("NOUN"),
        Label("SIMPLE_SUBJECT"),
        Label("SUBJECT"),
    ]
