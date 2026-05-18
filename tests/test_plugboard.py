"""Plugboard mapping and validation tests."""

from __future__ import annotations

import pytest

from enigma.engine import normalize_pairs
from enigma.plugboard import Plugboard


@pytest.mark.parametrize(
    "pairs",
    [
        [("A", "B"), ("A", "C")],
        [("A", "A")],
        [("A", "1")],
        [("AB", "C")],
    ],
)
def test_plugboard_rejects_invalid_pairs(pairs: list[tuple[str, str]]) -> None:
    with pytest.raises(ValueError):
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

    with pytest.raises(ValueError):
        Plugboard(pairs)


def test_normalize_pairs_normalizes_mixed_case_input() -> None:
    assert normalize_pairs([("a", "b"), ("c", "d")]) == (("A", "B"), ("C", "D"))


def test_normalize_pairs_preserves_order_and_does_not_dedupe() -> None:
    assert normalize_pairs([("c", "d"), ("a", "b")]) == (("C", "D"), ("A", "B"))


def test_normalize_pairs_rejects_repeated_letters() -> None:
    with pytest.raises(ValueError):
        normalize_pairs([("a", "b"), ("B", "c")])


def test_normalize_pairs_rejects_ambiguous_string_pair() -> None:
    with pytest.raises(ValueError, match="exactly two letters"):
        normalize_pairs(["ab"])  # type: ignore[list-item]
