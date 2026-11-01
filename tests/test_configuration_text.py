"""Pin existing configuration normalization pending a separate policy decision."""

import re

import pytest

from enigma import EnigmaConfig
from enigma.plugboard import normalize_pair


@pytest.mark.parametrize("letter", ["", "AB", "1", "é", "ß"])
@pytest.mark.parametrize("side", [0, 1])
def test_invalid_plug_letter_retains_exact_message(letter: str, side: int) -> None:
    pair = ["Z", "Z"]
    pair[side] = letter
    message = f"Invalid plugboard pair: {pair[0]}-{pair[1]}"
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        normalize_pair(pair)


@pytest.mark.parametrize(("letter", "normalized"), [("\u0131", "I"), ("\u017f", "S")])
def test_plugboard_current_unicode_normalization(letter: str, normalized: str) -> None:
    assert normalize_pair((letter, "Z")) == (normalized, "Z")
    assert normalize_pair(("Z", letter)) == ("Z", normalized)


@pytest.mark.parametrize(
    ("key", "normalized"),
    [("Aß", "ASS"), ("\u0131BC", "IBC"), ("\u017fBC", "SBC"), ("A1BC", "ABC")],
)
def test_key_current_expansion_and_filtering(key: str, normalized: str) -> None:
    assert EnigmaConfig(key=key).key == normalized


@pytest.mark.parametrize("key", ["ß", "\u0131", "\u017f"])
def test_single_unicode_key_still_fails_normalized_length(key: str) -> None:
    with pytest.raises(ValueError, match=r"^Key must contain exactly 3 letters$"):
        EnigmaConfig(key=key)
