"""Tests for generated POS vocabulary heuristics."""

from build_pos_vocab import classify_token


def test_possessive_forms_are_adjectival_possessive_nouns():
    assert classify_token("tom's", {"Tom's"}, {"tom's": {"Tom's"}}) == [
        ("ADJECTIVE", 1.0),
        ("POSSESSIVE_NOUN", 1.0),
    ]
    assert classify_token("bears'", {"bears'"}, {"bears'": {"bears'"}}) == [
        ("ADJECTIVE", 1.0),
        ("POSSESSIVE_NOUN", 1.0),
    ]


def test_contractions_still_classify_as_verbs():
    assert classify_token("don't", {"don't"}, {"don't": {"don't"}}) == [
        ("VERB", 1.0)
    ]
    assert classify_token("i'm", {"I'm"}, {"i'm": {"I'm"}}) == [
        ("VERB", 1.0)
    ]
