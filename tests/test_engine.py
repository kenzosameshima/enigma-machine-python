"""Regression tests for Enigma processing."""

from __future__ import annotations

import builtins
from collections.abc import Iterator

import pytest

from enigma import EnigmaConfigBuilder, EnigmaFactory, enigma_process
from enigma.cli import DailyKeySheetCommand
from enigma.engine import normalize_pairs, process_char, step_rotors
from enigma.machine import EnigmaMachine, _should_step_rotors
from enigma.modes import MachineModeName
from enigma.plugboard import Plugboard
from enigma.rotors import Rotor


def make_machine(
    *,
    text: str = "",
    key: str = "AAA",
    mode: MachineModeName | str = MachineModeName.WEHRMACHT,
    rotor_order: tuple[str, ...] = ("I", "II", "III"),
    ring_settings: tuple[int, ...] = (1, 1, 1),
    reflector_name: str = "B",
    plug_pairs: tuple[tuple[str, str], ...] = (),
    greek_rotor_name: str = "BETA",
):
    config = (
        EnigmaConfigBuilder()
        .text(text)
        .mode(mode)
        .rotors(rotor_order)
        .rings(ring_settings)
        .key(key)
        .reflector(reflector_name)
        .plugboard(plug_pairs)
        .greek(greek_rotor_name)
        .build()
    )
    return EnigmaFactory().create(config)


@pytest.mark.parametrize(
    ("reflector_name", "ring_settings"),
    [
        ("B", (1, 1, 1)),
        ("C", (1, 1, 1)),
        ("B", (2, 14, 26)),
    ],
)
def test_three_rotor_round_trip(
    reflector_name: str,
    ring_settings: tuple[int, ...],
) -> None:
    encrypted = enigma_process(
        text="HELLO WORLD",
        key="ABC",
        mode="wehrmacht",
        plug_pairs=[("A", "B"), ("C", "D")],
        rotor_order=("I", "II", "III"),
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )

    decrypted = enigma_process(
        text=encrypted,
        key="ABC",
        mode="wehrmacht",
        plug_pairs=[("A", "B"), ("C", "D")],
        rotor_order=("I", "II", "III"),
        ring_settings=ring_settings,
        reflector_name=reflector_name,
    )

    assert decrypted == "HELLO WORLD"


def test_m4_round_trip() -> None:
    encrypted = enigma_process(
        text="ENIGMA",
        key="WXYZ",
        mode="m4",
        rotor_order=("I", "II", "III"),
        ring_settings=(1, 1, 1, 1),
        reflector_name="B_THIN",
        greek_rotor_name="BETA",
    )

    decrypted = enigma_process(
        text=encrypted,
        key="WXYZ",
        mode="m4",
        rotor_order=("I", "II", "III"),
        ring_settings=(1, 1, 1, 1),
        reflector_name="B_THIN",
        greek_rotor_name="BETA",
    )

    assert decrypted == "ENIGMA"


def test_spaces_punctuation_and_numbers_are_preserved() -> None:
    result = enigma_process(text="HI, 42!", key="AAA")

    assert result[2:] == ", 42!"


def test_lowercase_input_is_normalized() -> None:
    assert enigma_process(text="hello", key="ABC") == enigma_process(
        text="HELLO",
        key="ABC",
    )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"text": "HELLOWORLD", "key": "AAA"}, "ILBDAAMTAZ"),
        (
            {
                "text": "HELLO, WORLD! 123",
                "key": "ABC",
                "plug_pairs": [("A", "B"), ("C", "D")],
            },
            "ROMUL, LAIAI! 123",
        ),
        (
            {
                "text": "ENIGMA",
                "key": "WXYZ",
                "mode": "m4",
                "rotor_order": ("I", "II", "III"),
                "ring_settings": (1, 1, 1, 1),
                "reflector_name": "B_THIN",
                "greek_rotor_name": "BETA",
            },
            "PKJETQ",
        ),
    ],
)
def test_index_conversion_refactor_preserves_known_outputs(
    kwargs: dict[str, object],
    expected: str,
) -> None:
    assert enigma_process(**kwargs) == expected


def test_plugboard_with_valid_pairs_changes_output_but_round_trips() -> None:
    encrypted = enigma_process(
        text="PLUGBOARD",
        key="MCK",
        plug_pairs=[("P", "O"), ("L", "U")],
    )
    decrypted = enigma_process(
        text=encrypted,
        key="MCK",
        plug_pairs=[("P", "O"), ("L", "U")],
    )

    assert encrypted != "PLUGBOARD"
    assert decrypted == "PLUGBOARD"


def test_machine_state_is_mutable_between_process_text_calls() -> None:
    machine = make_machine(key="AAA")

    first = machine.process_text("AAAA")
    second = machine.process_text("AAAA")
    fresh = make_machine(key="AAA").process_text("AAAA")

    assert first == fresh
    assert second != first


def test_factory_creates_independent_rotor_states() -> None:
    first_machine = make_machine(key="AAA")
    second_machine = make_machine(key="AAA")

    first_states = [rotor.state for rotor in first_machine.rotors]
    second_states = [rotor.state for rotor in second_machine.rotors]

    assert len({id(state) for state in first_states}) == 3
    assert {id(state) for state in first_states}.isdisjoint(
        {id(state) for state in second_states}
    )


def test_enigma_process_does_not_reuse_mutable_machine_state() -> None:
    first = enigma_process("AAAA", "AAA")
    second = enigma_process("AAAA", "AAA")

    assert first == second


def test_machine_reset_restores_initial_rotor_state() -> None:
    machine = make_machine(key="AEA")

    first = machine.process_text("AAAA")
    assert machine.window() != "AEA"

    machine.reset()

    assert machine.window() == "AEA"
    assert machine.process_text("AAAA") == first


def test_machine_clones_rotor_state_from_reused_rotor_objects() -> None:
    shared_rotors = [Rotor("I"), Rotor("II"), Rotor("III")]
    first_machine = EnigmaMachine(shared_rotors, "B", Plugboard())
    second_machine = EnigmaMachine(shared_rotors, "B", Plugboard())
    expected = make_machine(key="AAA").process_text("AAAA")

    assert first_machine.process_text("AAAA") == expected
    assert second_machine.process_text("AAAA") == expected
    assert "".join(rotor.get_position_letter() for rotor in shared_rotors) == "AAA"


def test_step_rotors_compat_helper_still_mutates_passed_rotors() -> None:
    rotors = [Rotor("I"), Rotor("II"), Rotor("III")]

    step_rotors(rotors)

    assert "".join(rotor.get_position_letter() for rotor in rotors) == "AAB"


def test_machine_rejects_incorrect_moving_rotor_count() -> None:
    with pytest.raises(ValueError, match="exactly 3 moving rotors"):
        EnigmaMachine([Rotor("I"), Rotor("II")], "B", Plugboard())


def test_machine_rejects_non_moving_rotor_in_moving_slots() -> None:
    with pytest.raises(ValueError, match="Moving rotors"):
        EnigmaMachine([Rotor("I"), Rotor("II"), Rotor("BETA")], "B", Plugboard())


def test_machine_rejects_duplicate_moving_rotors() -> None:
    with pytest.raises(ValueError, match="unique"):
        EnigmaMachine([Rotor("I"), Rotor("II"), Rotor("II")], "B", Plugboard())


def test_machine_rejects_unknown_reflector() -> None:
    with pytest.raises(ValueError, match="Unknown reflector"):
        EnigmaMachine([Rotor("I"), Rotor("II"), Rotor("III")], "D", Plugboard())


def test_machine_rejects_invalid_greek_rotor() -> None:
    with pytest.raises(ValueError, match="Greek rotor"):
        EnigmaMachine(
            [Rotor("I"), Rotor("II"), Rotor("III")],
            "B",
            Plugboard(),
            greek_rotor=Rotor("I", can_step=False),
        )


def test_machine_accepts_valid_non_stepping_greek_rotor() -> None:
    machine = EnigmaMachine(
        [Rotor("I"), Rotor("II"), Rotor("III")],
        "B_THIN",
        Plugboard(),
        greek_rotor=Rotor("BETA", can_step=False),
    )

    assert machine.window() == "A AAA"


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


def test_m4_rejects_invalid_greek_rotor() -> None:
    with pytest.raises(ValueError, match="Greek rotor"):
        make_machine(
            key="AAAA",
            mode="m4",
            ring_settings=(1, 1, 1, 1),
            reflector_name="B_THIN",
            greek_rotor_name="I",
        )


def test_m4_rejects_incompatible_reflector() -> None:
    with pytest.raises(ValueError, match="thin reflectors"):
        make_machine(
            key="AAAA",
            mode="m4",
            ring_settings=(1, 1, 1, 1),
            reflector_name="B",
        )


def test_three_rotor_mode_rejects_incorrect_rotor_count() -> None:
    with pytest.raises(ValueError, match="3 rotor names"):
        make_machine(rotor_order=("I", "II"))


def test_key_with_incorrect_size_fails() -> None:
    with pytest.raises(ValueError, match="exactly 3 letters"):
        make_machine(key="AB")


def test_builder_creates_machine_with_expected_window() -> None:
    machine = make_machine(text="HELLO", key="ABC")

    assert machine.window() == "ABC"


def test_right_rotor_steps_for_each_alphabetic_character() -> None:
    machine = make_machine(key="AAA")

    machine.process_text("ABC")

    assert machine.window() == "AAD"


def test_non_alphabetic_characters_do_not_step_rotors() -> None:
    machine = make_machine(key="ABC")

    assert machine.process_text(" 123?!") == " 123?!"
    assert machine.window() == "ABC"


def test_turnover_steps_middle_rotor() -> None:
    machine = make_machine(key="AAV")

    machine.process_char("A")

    assert machine.window() == "ABW"


def test_double_step_advances_left_and_middle_rotors() -> None:
    machine = make_machine(key="AEA")

    machine.process_char("A")

    assert machine.window() == "BFB"


def test_known_double_step_window_sequence() -> None:
    machine = make_machine(key="ADU")

    windows = []
    for _ in range(4):
        machine.process_char("A")
        windows.append(machine.window())

    assert windows == ["ADV", "AEW", "BFX", "BFY"]


def test_right_turnover_does_not_advance_left_without_middle_turnover() -> None:
    machine = make_machine(key="AAV")

    machine.process_char("A")

    assert machine.window()[0] == "A"


def test_should_step_rotors_documents_double_step_decisions() -> None:
    assert _should_step_rotors(middle_at_notch=False, right_at_notch=False) == (
        False,
        False,
        True,
    )
    assert _should_step_rotors(middle_at_notch=False, right_at_notch=True) == (
        False,
        True,
        True,
    )
    assert _should_step_rotors(middle_at_notch=True, right_at_notch=False) == (
        True,
        True,
        True,
    )


def test_step_rotors_rejects_incorrect_moving_rotor_count() -> None:
    with pytest.raises(ValueError, match="exactly 3 moving rotors"):
        step_rotors([Rotor("I"), Rotor("II")])


def test_process_char_uses_existing_advanced_rotor_positions() -> None:
    machine = make_machine(key="AAB")
    expected_machine = make_machine(key="AAC")

    assert machine.process_char("A") == expected_machine.encode_signal("A")


def test_compat_process_char_encodes_without_stepping_existing_rotors() -> None:
    machine = make_machine(key="AAC")

    assert process_char("A", machine.rotors, "B") == machine.encode_signal("A")


def test_daily_key_sheet_command_generates_valid_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs: Iterator[str] = iter(
        [
            "I II III",
            "1 1 1",
            "",
            "",
            "AAA",
            "ABC",
            "HELLO",
        ]
    )
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))

    output = DailyKeySheetCommand().execute()

    assert "Rotor order: I II III" in output
    assert "Ring settings: 1 1 1" in output
    assert "Decrypted: HELLO" in output


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
