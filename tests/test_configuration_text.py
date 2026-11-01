"""Require ASCII configuration letters without expansion or silent filtering."""

import re

import pytest

from enigma import EnigmaConfig, MachineModeName, Plugboard
from enigma.plugboard import normalize_pair


@pytest.mark.parametrize("letter", ["", "AB", "1", "é", "ß"])
@pytest.mark.parametrize("side", [0, 1])
def test_invalid_plug_letter_retains_exact_message(letter: str, side: int) -> None:
    pair = ["Z", "Z"]
    pair[side] = letter
    message = f"Invalid plugboard pair: {pair[0]}-{pair[1]}"
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        normalize_pair(pair)


@pytest.mark.parametrize("letter", ["\u0131", "\u017f"])
@pytest.mark.parametrize("side", [0, 1])
def test_plugboard_rejects_unicode_case_aliases(letter: str, side: int) -> None:
    pair = ["Z", "Z"]
    pair[side] = letter
    message = f"Invalid plugboard pair: {pair[0]}-{pair[1]}"
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        normalize_pair(pair)


@pytest.mark.parametrize(
    "key",
    [
        "Aß",
        "\u0131BC",
        "\u017fBC",
        "A1BC",
        "a b c",
        "AB-C",
        "A,B,C",
        "A\tBC",
        "A\u0301BC",
    ],
)
@pytest.mark.parametrize("count", [3, 4])
def test_key_rejects_expansion_and_filtering(key: str, count: int) -> None:
    with pytest.raises(ValueError, match=f"^Key must contain exactly {count} letters$"):
        EnigmaConfig(
            key=key + ("D" if count == 4 else ""),
            mode=MachineModeName.M4 if count == 4 else MachineModeName.WEHRMACHT,
            ring_settings=(1,) * count,
            reflector_name="B_THIN" if count == 4 else "B",
        )


@pytest.mark.parametrize("key", ["A1B", "A B", "A-B", "AéB", "AB\uff23", ""])
def test_key_rejects_nonletters_even_at_expected_length(key: str) -> None:
    with pytest.raises(ValueError, match=r"^Key must contain exactly 3 letters$"):
        EnigmaConfig(key=key)


@pytest.mark.parametrize("count", [3, 4])
@pytest.mark.parametrize("padding", ["", " ", "\t", "\r\n", "\u00a0"])
def test_key_strips_only_surrounding_whitespace(count: int, padding: str) -> None:
    letters = "aBcD"[:count]
    config = EnigmaConfig(
        key=padding + letters + padding,
        mode=MachineModeName.M4 if count == 4 else MachineModeName.WEHRMACHT,
        ring_settings=(1,) * count,
        reflector_name="B_THIN" if count == 4 else "B",
    )
    assert config.key == "ABCD"[:count]


@pytest.mark.parametrize("key", ["ß", "\u0131", "\u017f"])
def test_single_unicode_key_still_fails_normalized_length(key: str) -> None:
    with pytest.raises(ValueError, match=r"^Key must contain exactly 3 letters$"):
        EnigmaConfig(key=key)


@pytest.mark.parametrize("first", ["A", "a"])
@pytest.mark.parametrize("second", ["A", "a"])
def test_plugboard_rejects_repeated_letter_after_normalization(
    first: str, second: str
) -> None:
    with pytest.raises(
        ValueError, match=r"^Plugboard pair cannot repeat a letter: A-A$"
    ):
        Plugboard([(first, second)])


@pytest.mark.parametrize("name", [chr(0x0131), chr(0x017F), chr(0x00DF)])
def test_rotor_order_rejects_unicode_case_aliases(name: str) -> None:
    with pytest.raises(
        ValueError, match=r"^Moving rotors must be selected from I, II, III, IV, V$"
    ):
        EnigmaConfig(rotor_order=(name, "II", "III"))


@pytest.mark.parametrize("name", [chr(0x0131), chr(0x017F), chr(0x00DF)])
def test_reflector_name_rejects_unicode_case_aliases(name: str) -> None:
    with pytest.raises(ValueError, match=f"^Unknown reflector: {re.escape(name)}$"):
        EnigmaConfig(reflector_name=name)


@pytest.mark.parametrize("name", [chr(0x0131), chr(0x017F), chr(0x00DF)])
def test_greek_rotor_name_rejects_unicode_case_aliases(name: str) -> None:
    with pytest.raises(ValueError, match=f"^Unknown Greek rotor: {re.escape(name)}$"):
        EnigmaConfig(greek_rotor_name=name)
