"""Unit tests for the shared ascii_upper normalization helper."""

from __future__ import annotations

import pytest

from enigma.alphabet import ascii_upper

DOTLESS_I = chr(0x0131)
LONG_S = chr(0x017F)
SHARP_S = chr(0x00DF)
E_ACUTE = chr(0x00E9)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello", "HELLO"),
        ("Hello World", "HELLO WORLD"),
        ("", ""),
        ("123", "123"),
        ("a1b2c3", "A1B2C3"),
    ],
)
def test_ascii_upper_uppercases_only_ascii_letters(text: str, expected: str) -> None:
    assert ascii_upper(text) == expected


@pytest.mark.parametrize("char", [DOTLESS_I, LONG_S, SHARP_S, E_ACUTE])
def test_ascii_upper_leaves_non_ascii_characters_unchanged(char: str) -> None:
    """Dotless i, long s, sharp s, and e-acute are not ASCII a-z."""

    assert ascii_upper(char) == char


def test_ascii_upper_never_changes_output_length() -> None:
    """Unlike str.upper(), ascii_upper never expands a character (e.g. ss)."""

    text = "a" + SHARP_S + DOTLESS_I + LONG_S + E_ACUTE + " 1,-"
    assert len(ascii_upper(text)) == len(text)
