"""Regression tests for atomic character validation and ASCII normalization."""

import pytest
from helpers import make_machine


@pytest.mark.parametrize("text", ["ß", "ﬃ", "\u0131", "é", "aßz"])
def test_only_ascii_letters_are_normalized_and_step(text: str) -> None:
    machine = make_machine()
    control = make_machine()
    expected = "".join(
        control.process_char(char.upper())
        if char.isascii() and char.isalpha()
        else char
        for char in text
    )
    assert machine.process_text(text) == expected
    assert machine.window() == control.window()
    assert len(expected) == len(text)


@pytest.mark.parametrize("char", ["", "AB", "!?", None, 1, ["A"]])
def test_invalid_character_is_rejected_without_stepping(char: object) -> None:
    machine = make_machine(key="ADV")
    before = tuple(rotor.snapshot() for rotor in machine.rotors)
    try:
        with pytest.raises(ValueError, match=r"^Character must be a single character$"):
            machine.process_char(char)  # type: ignore[arg-type]
    finally:
        assert tuple(rotor.snapshot() for rotor in machine.rotors) == before


def test_process_char_normalizes_ascii_lowercase() -> None:
    machine = make_machine()
    assert machine.process_char("a") == make_machine().process_char("A")
    assert machine.window() == "AAB"
