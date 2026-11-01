"""Plugboard mapping and validation tests."""

from __future__ import annotations

import pytest

from enigma.plugboard import Plugboard, normalize_pairs


@pytest.mark.parametrize(
    ("pairs", "message"),
    [
        ([("A", "B"), ("A", "C")], "Plugboard letter already used: A-C"),
        ([("A", "A")], "Plugboard pair cannot repeat a letter: A-A"),
        ([("A", "1")], "Invalid plugboard pair: A-1"),
        ([("AB", "C")], "Invalid plugboard pair: AB-C"),
    ],
)
def test_plugboard_rejects_invalid_pairs(
    pairs: list[tuple[str, str]], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        Plugboard(pairs)


def test_plugboard_rejects_more_than_ten_pairs() -> None:
    pairs = [
        ("A", "B"),
        ("C", "D"),
        ("E", "F"),
        ("G", "H"),
        ("I", "J"),
        ("K", "L"),
        ("M", "N"),
        ("O", "P"),
        ("Q", "R"),
        ("S", "T"),
        ("U", "V"),
    ]

    with pytest.raises(ValueError, match="Plugboard supports up to 10 pairs"):
        Plugboard(pairs)


def test_normalize_pairs_normalizes_mixed_case_input() -> None:
    assert normalize_pairs([("a", "b"), ("c", "d")]) == (("A", "B"), ("C", "D"))


def test_normalize_pairs_preserves_order_and_does_not_dedupe() -> None:
    assert normalize_pairs([("c", "d"), ("a", "b")]) == (("C", "D"), ("A", "B"))


def test_normalize_pairs_rejects_repeated_letters() -> None:
    with pytest.raises(ValueError, match="Plugboard letter already used: B-C"):
        normalize_pairs([("a", "b"), ("B", "c")])


def test_normalize_pairs_rejects_ambiguous_string_pair() -> None:
    with pytest.raises(ValueError, match="exactly two letters"):
        normalize_pairs(["ab"])  # type: ignore[list-item]
