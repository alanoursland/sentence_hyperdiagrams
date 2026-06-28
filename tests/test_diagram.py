"""Tests for the diagram file parser/writer."""

import pytest

from parts_of_thought.diagram import (
    Label,
    TokenAnnotation,
    ValidationError,
    fix_label_placement,
    merge_passes,
    parse_metadata,
    parse_pass,
    tokenize,
    validate,
    validate_or_raise,
    write_pass,
    write_tokens,
)


# -- Label --

class TestLabel:
    def test_leaf_label(self):
        label = Label(name="DET")
        assert label.is_leaf
        assert label.to_line() == "DET"

    def test_linking_label(self):
        label = Label(name="NOUN_PHRASE", child_prev="DET",
                      child_curr="NOUN", index_prev=0)
        assert not label.is_leaf
        assert label.to_line() == "NOUN_PHRASE DET NOUN 0"

    def test_label_with_parameter(self):
        label = Label(name="NP", child_prev="DET", child_curr="NOUN",
                      index_prev=0, parameter=2)
        assert label.to_line() == "NP DET NOUN 0 2"

    def test_label_with_weight(self):
        label = Label(name="NP", child_prev="DET", child_curr="NOUN",
                      index_prev=0, parameter=0, weight=0.8)
        assert label.to_line() == "NP DET NOUN 0 0 0.8"

    def test_weighted_leaf_label(self):
        label = Label(name="VERB", weight=0.8)
        assert label.is_leaf
        assert label.to_line() == "VERB 0.8"

    def test_leaf_defaults(self):
        label = Label(name="VERB")
        assert label.parameter == 0
        assert label.weight == 1.0


# -- parse_pass --

SIMPLE_PASS = """\
# source: test

0 The
  DET
1 cat
  NOUN
  NOUN_PHRASE DET NOUN 0
2 sat
  VERB
3 .
  PUNCT
"""


class TestParsing:
    def test_simple_pass(self):
        result = parse_pass(SIMPLE_PASS)
        assert len(result) == 4
        assert result[0].index == 0
        assert result[0].token == "The"
        assert len(result[0].labels) == 1
        assert result[0].labels[0] == Label(name="DET")

    def test_multiple_labels(self):
        result = parse_pass(SIMPLE_PASS)
        cat = result[1]
        assert cat.token == "cat"
        assert len(cat.labels) == 2
        assert cat.labels[0] == Label(name="NOUN")
        assert cat.labels[1] == Label(
            name="NOUN_PHRASE", child_prev="DET",
            child_curr="NOUN", index_prev=0
        )

    def test_linking_label_fields(self):
        result = parse_pass(SIMPLE_PASS)
        np_label = result[1].labels[1]
        assert np_label.name == "NOUN_PHRASE"
        assert np_label.child_prev == "DET"
        assert np_label.child_curr == "NOUN"
        assert np_label.index_prev == 0
        assert not np_label.is_leaf

    def test_blank_lines_ignored(self):
        text = "0 The\n\n  DET\n\n1 cat\n  NOUN\n"
        result = parse_pass(text)
        assert len(result) == 2

    def test_comments_ignored(self):
        text = "# comment\n0 The\n  DET\n# another comment\n1 cat\n"
        result = parse_pass(text)
        assert len(result) == 2
        assert result[0].labels[0].name == "DET"

    def test_token_no_labels(self):
        text = "0 The\n1 cat\n  NOUN\n"
        result = parse_pass(text)
        assert len(result) == 2
        assert result[0].labels == []
        assert len(result[1].labels) == 1

    def test_label_with_parameter_and_weight(self):
        text = "0 The\n  DET\n1 cat\n  NP DET NOUN 0 1 0.75\n"
        result = parse_pass(text)
        label = result[1].labels[0]
        assert label.parameter == 1
        assert label.weight == 0.75

    def test_weighted_leaf_parse(self):
        text = "0 run\n  VERB 0.8\n  NOUN 0.2\n"
        result = parse_pass(text)
        assert len(result[0].labels) == 2
        assert result[0].labels[0] == Label(name="VERB", weight=0.8)
        assert result[0].labels[1] == Label(name="NOUN", weight=0.2)

    def test_weighted_leaf_round_trip(self):
        text = "0 run\n  VERB 0.8\n  NOUN 0.2\n"
        result = parse_pass(text)
        output = write_pass(result)
        reparsed = parse_pass(output)
        assert reparsed[0].labels == result[0].labels

    def test_bad_label_fields(self):
        text = "0 The\n  NP DET NOUN\n"
        with pytest.raises(ValueError, match="3"):
            parse_pass(text)

    def test_label_before_token(self):
        text = "  DET\n0 The\n"
        with pytest.raises(ValueError, match="before any token"):
            parse_pass(text)

    def test_punctuation_token(self):
        text = '0 .\n  PUNCT\n1 !\n  PUNCT\n2 ?\n  PUNCT\n'
        result = parse_pass(text)
        assert result[0].token == "."
        assert result[1].token == "!"
        assert result[2].token == "?"


# -- parse_metadata --

class TestMetadata:
    def test_metadata_extraction(self):
        text = "# source: mcguffey_primer\n# pass: 01\n0 The\n"
        meta = parse_metadata(text)
        assert meta == {"source": "mcguffey_primer", "pass": "01"}

    def test_plain_comments_skipped(self):
        text = "# just a comment\n# key: value\n"
        meta = parse_metadata(text)
        assert meta == {"key": "value"}

    def test_empty(self):
        assert parse_metadata("") == {}


# -- write_pass --

class TestWriting:
    def test_round_trip(self):
        original = parse_pass(SIMPLE_PASS)
        output = write_pass(original)
        reparsed = parse_pass(output)

        assert len(reparsed) == len(original)
        for orig, reparse in zip(original, reparsed):
            assert orig.index == reparse.index
            assert orig.token == reparse.token
            assert orig.labels == reparse.labels

    def test_write_with_metadata(self):
        anns = [TokenAnnotation(index=0, token="The", labels=[Label("DET")])]
        output = write_pass(anns, metadata={"pass": "01"})
        assert output.startswith("# pass: 01\n")
        assert "0 The\n  DET\n" in output

    def test_write_tokens_only(self):
        anns = [
            TokenAnnotation(index=0, token="The"),
            TokenAnnotation(index=1, token="cat"),
        ]
        output = write_tokens(anns)
        assert output == "0 The\n1 cat\n"


# -- merge_passes --

PASS_A = """\
0 The
  DET
1 cat
  NOUN
2 sat
  VERB
"""

PASS_B = """\
0 The
1 cat
  AGENT
2 sat
  ACT-ON AGENT VERB 1
"""


class TestMerge:
    def test_merge_two_passes(self):
        a = parse_pass(PASS_A)
        b = parse_pass(PASS_B)
        merged = merge_passes([a, b])

        assert len(merged) == 3
        assert merged[0].labels == [Label("DET")]
        assert merged[1].labels == [Label("NOUN"), Label("AGENT")]
        assert len(merged[2].labels) == 2
        assert merged[2].labels[0] == Label("VERB")
        assert merged[2].labels[1] == Label(
            "ACT-ON", child_prev="AGENT", child_curr="VERB", index_prev=1
        )

    def test_merge_token_mismatch(self):
        a = parse_pass("0 The\n1 cat\n")
        b = parse_pass("0 The\n1 dog\n")
        with pytest.raises(ValueError, match="Token mismatch"):
            merge_passes([a, b])

    def test_merge_length_mismatch(self):
        a = parse_pass("0 The\n1 cat\n")
        b = parse_pass("0 The\n")
        with pytest.raises(ValueError, match="tokens"):
            merge_passes([a, b])

    def test_merge_empty(self):
        assert merge_passes([]) == []


# -- validate --

VALID_DIAGRAM = """\
0 The
  DET
1 cat
  NOUN
  SUBJECT DET NOUN 0
2 sat
  VERB
  PREDICATE SUBJECT VERB 1
"""

BAD_CHILD_CURR = """\
0 The
  DET
1 cat
  NOUN
2 .
  PUNCT
  PREDICATE NOUN VERB 1
"""

BAD_CHILD_PREV = """\
0 The
  DET
1 cat
  NOUN
  SUBJECT DET NOUN 0
2 sat
  VERB
  PREDICATE AGENT VERB 1
"""

BAD_INDEX_PREV = """\
0 The
  DET
1 cat
  NOUN
  SUBJECT DET NOUN 99
"""

LABEL_ON_WRONG_TOKEN = """\
0 Ann
  NOUN
  SUBJECT
1 can
  VERB
2 fan
  VERB
  VERB_PHRASE VERB VERB 1
3 Nat
  NOUN
  OBJECT_COMPLEMENT
4 .
  PUNCT
  PREDICATE VERB_PHRASE OBJECT_COMPLEMENT 2
  DECLARATIVE SUBJECT PREDICATE 0
"""


class TestValidation:
    def test_valid_diagram(self):
        anns = parse_pass(VALID_DIAGRAM)
        errors = validate(anns)
        assert errors == []

    def test_child_curr_not_on_token(self):
        anns = parse_pass(BAD_CHILD_CURR)
        errors = validate(anns)
        assert len(errors) == 1
        assert "child_curr" in errors[0]
        assert "VERB" in errors[0]

    def test_child_prev_not_on_token(self):
        anns = parse_pass(BAD_CHILD_PREV)
        errors = validate(anns)
        assert len(errors) == 1
        assert "child_prev" in errors[0]
        assert "AGENT" in errors[0]

    def test_bad_index_prev(self):
        anns = parse_pass(BAD_INDEX_PREV)
        errors = validate(anns)
        assert len(errors) == 1
        assert "index_prev" in errors[0]
        assert "99" in errors[0]

    def test_label_on_wrong_token(self):
        """PREDICATE is on the period but its child_curr
        OBJECT_COMPLEMENT is not on this token — validator catches this.
        DECLARATIVE's child_curr PREDICATE happens to be on the same
        token (even though it's misplaced), so no error for that one."""
        anns = parse_pass(LABEL_ON_WRONG_TOKEN)
        errors = validate(anns)
        assert len(errors) == 1
        assert "OBJECT_COMPLEMENT" in errors[0]
        assert "child_curr" in errors[0]

    def test_validate_or_raise(self):
        anns = parse_pass(BAD_CHILD_CURR)
        with pytest.raises(ValidationError, match="1 validation error"):
            validate_or_raise(anns)

    def test_validate_or_raise_passes(self):
        anns = parse_pass(VALID_DIAGRAM)
        validate_or_raise(anns)  # should not raise

    def test_index_prev_not_less_than_current(self):
        """index_prev must be strictly less than the current token index."""
        anns = [
            TokenAnnotation(index=0, token="cat", labels=[Label("NOUN")]),
            TokenAnnotation(index=1, token="sat", labels=[
                Label("VERB"),
                Label("BAD", child_prev="NOUN", child_curr="VERB",
                      index_prev=1),
            ]),
        ]
        errors = validate(anns)
        assert len(errors) == 1
        assert "not less than" in errors[0]

    def test_leaf_labels_always_valid(self):
        anns = parse_pass("0 The\n  DET\n1 cat\n  NOUN\n")
        errors = validate(anns)
        assert errors == []


# -- fix_label_placement --

class TestFixPlacement:
    def test_moves_labels_off_punctuation(self):
        """Labels on the period should move to their child_curr's token."""
        anns = parse_pass(LABEL_ON_WRONG_TOKEN)
        fixed = fix_label_placement(anns)

        # PREDICATE and DECLARATIVE moved from token 4 to token 3.
        token_4 = fixed[4]
        assert [l.name for l in token_4.labels] == ["PUNCT"]

        token_3 = fixed[3]
        names = [l.name for l in token_3.labels]
        assert "PREDICATE" in names
        assert "DECLARATIVE" in names

        # PREDICATE children are correct.
        pred = next(l for l in token_3.labels if l.name == "PREDICATE")
        assert pred.child_curr == "OBJECT_COMPLEMENT"
        assert pred.child_prev == "VERB_PHRASE"
        assert pred.index_prev == 2

        # DECLARATIVE children are correct.
        decl = next(l for l in token_3.labels if l.name == "DECLARATIVE")
        assert decl.child_curr == "PREDICATE"
        assert decl.child_prev == "SUBJECT"
        assert decl.index_prev == 0

    def test_fixed_passes_validation(self):
        anns = parse_pass(LABEL_ON_WRONG_TOKEN)
        fixed = fix_label_placement(anns)
        assert validate(fixed) == []

    def test_already_valid_unchanged(self):
        anns = parse_pass(VALID_DIAGRAM)
        fixed = fix_label_placement(anns)
        assert len(fixed) == len(anns)
        for orig, fix in zip(anns, fixed):
            assert orig.index == fix.index
            assert orig.token == fix.token
            assert orig.labels == fix.labels

    def test_leaf_only_unchanged(self):
        anns = parse_pass("0 The\n  DET\n1 cat\n  NOUN\n")
        fixed = fix_label_placement(anns)
        assert len(fixed) == 2
        assert fixed[0].labels == [Label("DET")]
        assert fixed[1].labels == [Label("NOUN")]


# -- tokenize --

class TestTokenize:
    def test_simple_sentence(self):
        result = tokenize("A cat and a rat.")
        assert len(result) == 6
        assert result[0].index == 0
        assert result[0].token == "A"
        assert result[4].token == "rat"
        assert result[5].token == "."

    def test_trailing_punctuation(self):
        result = tokenize("Hello, world!")
        assert [t.token for t in result] == ["Hello", ",", "world", "!"]

    def test_leading_punctuation(self):
        result = tokenize('"Hello" she said.')
        assert result[0].token == '"'
        assert result[1].token == "Hello"
        assert result[2].token == '"'

    def test_start_index(self):
        result = tokenize("Ann has a cat.", start_index=6)
        assert result[0].index == 6
        assert result[-1].index == 10
        assert result[-1].token == "."

    def test_contraction_kept(self):
        result = tokenize("don't can't")
        assert [t.token for t in result] == ["don't", "can't"]

    def test_hyphenated_word_kept(self):
        result = tokenize("well-known fact.")
        assert [t.token for t in result] == ["well-known", "fact", "."]

    def test_indices_sequential(self):
        result = tokenize("The cat sat.")
        indices = [t.index for t in result]
        assert indices == list(range(len(result)))

    def test_no_labels(self):
        result = tokenize("The cat.")
        for t in result:
            assert t.labels == []

    def test_write_tokens_round_trip(self):
        result = tokenize("A cat and a rat.")
        output = write_tokens(result)
        assert output == "0 A\n1 cat\n2 and\n3 a\n4 rat\n5 .\n"
