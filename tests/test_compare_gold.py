"""Tests for canonical-gold comparison and the reviewed fixture."""

from pathlib import Path

from apply_labels import load_rules, load_yaml
from compare_gold import compare_annotations, format_report
from parts_of_thought.diagram import Label, TokenAnnotation, parse_pass, parse_pass_file


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "gold" / "reed_kellogg"


def test_comparison_reports_missing_extra_and_invalid_references():
    gold = parse_pass("0 A\n1 cat\n  NOUN\n")
    generated = parse_pass(
        "0 A\n1 cat\n  NOUN\n  BAD NOUN MISSING 0\n"
    )
    context = parse_pass("0 A\n  ARTICLE\n1 cat\n")

    result = compare_annotations(gold, generated, context_passes=[context])

    assert result.precision == 0.5
    assert result.recall == 1.0
    assert len(result.missing) == 0
    assert len(result.extra) == 1
    assert len(result.invalid_references) == 1
    report = format_report(result)
    assert "Precision: 0.500" in report
    assert "Extra labels: 1" in report
    assert "Invalid references: 1" in report


def test_comparison_default_threshold_excludes_low_confidence_hypotheses():
    gold = [TokenAnnotation(index=0, token="run")]
    generated = [
        TokenAnnotation(index=0, token="run", labels=[Label("NOUN", weight=0.2)])
    ]

    canonical = compare_annotations(gold, generated)
    all_hypotheses = compare_annotations(gold, generated, min_weight=0.0)

    assert canonical.generated_count == 0
    assert len(canonical.extra) == 0
    assert all_hypotheses.generated_count == 1
    assert len(all_hypotheses.extra) == 1


def test_gold_corpus_size_and_supported_construction_coverage():
    sentences = (GOLD / "sentences.txt").read_text(encoding="utf-8").splitlines()
    pos = parse_pass_file(GOLD / "pos.txt")
    primitives = parse_pass_file(GOLD / "primitives.txt")
    names = {label.name for ann in primitives for label in ann.labels}

    assert 30 <= len(sentences) <= 50
    assert len(sentences) == 36
    assert len(pos) == len(primitives) == 180
    assert {
        "NOUN",
        "SIMPLE_SUBJECT",
        "COMPOUND_SUBJECT",
        "SIMPLE_OBJECT_COMPLEMENT",
        "COMPOUND_OBJECT_COMPLEMENT",
        "SIMPLE_PREPOSITIONAL_PRINCIPAL",
        "COMPOUND_PREPOSITIONAL_PRINCIPAL",
    } <= names
    assert {"ADJECTIVE", "POSSESSIVE_NOUN"} <= {
        label.name for label in pos[19].labels
    }
    assert {"ADJECTIVE", "POSSESSIVE_PRONOUN"} <= {
        label.name for label in pos[22].labels
    }
    assert sum(label.name == "NOUN" for label in primitives[17].labels) == 3


def test_gold_negative_examples_remain_unlabeled_at_canonical_confidence():
    gold = parse_pass_file(GOLD / "primitives.txt")
    generated = parse_pass_file(GOLD / "generated_primitives.txt")

    # Inverted interrogatives: Ann is not a direct object.
    assert gold[122].labels == []
    assert gold[127].labels == []
    # Clause coordination and comma barriers do not become compound subjects.
    assert gold[144].labels == []
    assert not any(label.name == "COMPOUND_SUBJECT" for label in gold[152].labels)
    # Imperative/direct address is unsupported rather than misclassified.
    assert gold[160].labels == []
    # The weak nominal reading of "run" remains visible but noncanonical.
    assert gold[156].labels == []
    assert generated[156].labels == [
        Label("SIMPLE_OBJECT_COMPLEMENT", weight=0.2)
    ]


def test_actual_grammar_rejects_inverted_interrogative_object():
    pos = parse_pass_file(GOLD / "pos.txt")
    rules = load_rules(load_yaml(ROOT / "ontology" / "reed_kellogg_02_primitives.yaml"))

    # The checked-in generated pass was produced by these rules; explicitly
    # verify the two post-verbal names do not receive object labels.
    from parts_of_thought.pattern import apply_rules

    result = apply_rules(pos, rules)
    assert not any(
        label.name == "SIMPLE_OBJECT_COMPLEMENT" for label in result[122].labels
    )
    assert not any(
        label.name == "SIMPLE_OBJECT_COMPLEMENT" for label in result[127].labels
    )


def test_checked_in_generated_pass_matches_gold_at_canonical_threshold():
    gold = parse_pass_file(GOLD / "primitives.txt")
    generated = parse_pass_file(GOLD / "generated_primitives.txt")
    pos = parse_pass_file(GOLD / "pos.txt")

    result = compare_annotations(gold, generated, context_passes=[pos])

    assert result.precision == 1.0
    assert result.recall == 1.0
    assert result.missing == ()
    assert result.extra == ()
    assert result.invalid_references == ()
