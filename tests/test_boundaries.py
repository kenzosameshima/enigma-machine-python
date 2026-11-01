"""Exercise validation branches independently, including their error messages."""

import re
from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from helpers import make_rotor

from enigma import EnigmaConfig, EnigmaMachine, Plugboard, Rotor
from enigma.data import ROTOR_SPECS
from enigma.modes import MODE_SPECS, MachineModeName
from enigma.plugboard import normalize_pair


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"key": None}, "Key must be text containing rotor position letters"),
        ({"key": "AB"}, "Key must contain exactly 3 letters"),
        ({"key": "ABCD"}, "Key must contain exactly 3 letters"),
        ({"rotor_order": ("I", "II", None)}, "Rotor names must be text"),
        (
            {"rotor_order": ("I", "II", "VI")},
            "Moving rotors must be selected from I, II, III, IV, V",
        ),
        ({"rotor_order": ("I", "II", "II")}, "Moving rotors must be unique"),
        ({"rotor_order": ("I", "II")}, "3-rotor mode requires 3 rotor names"),
        (
            {"rotor_order": ("I", "II", "III", "IV")},
            "3-rotor mode requires 3 rotor names",
        ),
        ({"reflector_name": None}, "Reflector name must be text"),
        ({"reflector_name": "D"}, "Unknown reflector: D"),
        ({"reflector_name": "B_THIN"}, "3-rotor mode uses reflector B or C"),
        ({"greek_rotor_name": None}, "Greek rotor must be text"),
        ({"greek_rotor_name": "I"}, "Unknown Greek rotor: I"),
        ({"ring_settings": (0, 1, 1)}, "Ring settings must be between 1 and 26"),
        ({"ring_settings": (1, 27, 1)}, "Ring settings must be between 1 and 26"),
        (
            {"ring_settings": (1, None, 1)},
            "Ring settings must be integers between 1 and 26",
        ),
        (
            {"ring_settings": (1, "bad", 1)},
            "Ring settings must be integers between 1 and 26",
        ),
        ({"ring_settings": (1, 1)}, "3-rotor mode requires 3 ring settings"),
        ({"ring_settings": (1, 1, 1, 1)}, "3-rotor mode requires 3 ring settings"),
        (
            {"mode": "wrong"},
            "Unsupported machine mode: wrong. Supported modes: m4, naval, wehrmacht",
        ),
    ],
)
def test_config_validation_branch(fields: dict[str, Any], message: str) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        EnigmaConfig(**fields)


@pytest.mark.parametrize("mode", list(MachineModeName))
@pytest.mark.parametrize("delta", [-1, 1])
def test_key_and_ring_counts_for_each_mode(mode: MachineModeName, delta: int) -> None:
    count = 4 if mode is MachineModeName.M4 else 3
    reflector = "B_THIN" if count == 4 else "B"
    with pytest.raises(ValueError, match=f"^Key must contain exactly {count} letters$"):
        EnigmaConfig(
            mode=mode,
            key="A" * (count + delta),
            ring_settings=(1,) * count,
            reflector_name=reflector,
        )
    label = "M4" if count == 4 else "3-rotor mode"
    with pytest.raises(ValueError, match=f"^{label} requires {count} ring settings$"):
        EnigmaConfig(
            mode=mode,
            key="A" * count,
            ring_settings=(1,) * (count + delta),
            reflector_name=reflector,
        )


@pytest.mark.parametrize("ring", [1, 26])
def test_config_normalizes_names_and_accepts_ring_endpoints(ring: int) -> None:
    config = EnigmaConfig(
        rotor_order=(" i ", "ii", " III"),
        key="a b c",
        ring_settings=(ring,) * 3,
        reflector_name=" b ",
        greek_rotor_name=" gamma ",
    )
    assert config.rotor_order == ("I", "II", "III")
    assert config.key == "ABC"
    assert config.reflector_name == "B"
    assert config.greek_rotor_name == "GAMMA"
    assert config.ring_settings == (ring,) * 3


@pytest.mark.parametrize(
    ("pair", "message"),
    [
        (None, "Plugboard pair must contain exactly two letters"),
        ([], "Plugboard pair must contain exactly two letters"),
        (["A"], "Plugboard pair must contain exactly two letters"),
        (["A", "B", "C"], "Plugboard pair must contain exactly two letters"),
        ([1, "A"], "Plugboard pair values must be letters"),
        (["A", 1], "Plugboard pair values must be letters"),
        (["1", "A"], "Invalid plugboard pair: 1-A"),
        (["A", "1"], "Invalid plugboard pair: A-1"),
        (["", "A"], "Invalid plugboard pair: -A"),
        (["A", ""], "Invalid plugboard pair: A-"),
        (["AB", "C"], "Invalid plugboard pair: AB-C"),
        (["A", "BC"], "Invalid plugboard pair: A-BC"),
    ],
)
def test_pair_validation_branch(pair: object, message: str) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        normalize_pair(pair)


def test_ten_plug_pairs_and_mapping_copy() -> None:
    pairs = tuple(zip("ACEGIKMOQS", "BDFHJLNPRT", strict=True))
    board = Plugboard(pairs)
    mapping = board.mapping
    assert len(mapping) == 20
    for first, second in pairs:
        assert mapping[first] == second
        assert mapping[second] == first
    mapping["A"] = "Z"
    assert board.swap("A") == "B"
    assert board.swap("Z") == "Z"
    with pytest.raises(ValueError, match=r"^Plugboard supports up to 10 pairs$"):
        Plugboard((*pairs, ("U", "V")))


@pytest.mark.parametrize("count", [2, 4])
def test_direct_machine_requires_three_rotors(count: int) -> None:
    rotors = [make_rotor(name) for name in ("I", "II", "III", "IV")[:count]]
    with pytest.raises(
        ValueError, match=r"^EnigmaMachine requires exactly 3 moving rotors$"
    ):
        EnigmaMachine(rotors, "B", Plugboard())


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        (
            "rotors",
            [None] * 3,
            TypeError,
            "EnigmaMachine rotors must be Rotor instances",
        ),
        (
            "plugboard",
            None,
            TypeError,
            "EnigmaMachine plugboard must be a Plugboard instance",
        ),
        ("greek_rotor", "BETA", TypeError, "Greek rotor must be a Rotor instance"),
    ],
)
def test_direct_machine_type_checks(
    field: str,
    value: object,
    error: type[Exception],
    message: str,
) -> None:
    arguments: dict[str, Any] = {
        "rotors": [make_rotor(name) for name in ("I", "II", "III")],
        "reflector_name": "B",
        "plugboard": Plugboard(),
        field: value,
    }
    with pytest.raises(error, match=f"^{re.escape(message)}$"):
        EnigmaMachine(**arguments)


def test_direct_machine_rejects_wrong_stepping_ability() -> None:
    rotors = [make_rotor(name) for name in ("I", "II", "III")]
    with pytest.raises(ValueError, match=r"^Greek rotor must not step$"):
        EnigmaMachine(rotors, "B_THIN", Plugboard(), make_rotor("BETA"))
    rotors[0] = make_rotor("I", can_step=False)
    with pytest.raises(ValueError, match=r"^Moving rotors must be able to step$"):
        EnigmaMachine(rotors, "B", Plugboard())


@pytest.mark.parametrize("name", list(ROTOR_SPECS))
def test_rotor_default_state(name: str) -> None:
    rotor = Rotor(ROTOR_SPECS[name])
    assert rotor.ring == 0
    assert rotor.position == 0
    assert rotor.get_position_letter() == "A"


@pytest.mark.parametrize(
    ("value", "attribute", "replacement"),
    [
        (EnigmaConfig(), "key", "BBB"),
        (make_rotor("I").snapshot(), "ring", 12),
        (make_rotor("I").snapshot(), "position", 12),
        (ROTOR_SPECS["I"], "name", "II"),
        (MODE_SPECS[MachineModeName.M4], "rotor_count", 3),
    ],
)
def test_settings_are_frozen(
    value: object, attribute: str, replacement: object
) -> None:
    with pytest.raises(FrozenInstanceError, match="cannot assign to field"):
        setattr(value, attribute, replacement)


def test_machines_from_equal_config_do_not_share_progress() -> None:
    config = EnigmaConfig(key="ADU")
    first = EnigmaMachine.from_config(config)
    second = EnigmaMachine.from_config(EnigmaConfig(key="ADU"))
    first.process_text("AAAA")
    assert second.window() == "ADU"
    assert config.key == "ADU"
    second.process_text("A")
    assert first.window() == "BFY"
    assert second.window() == "ADV"
