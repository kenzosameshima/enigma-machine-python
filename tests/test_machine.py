"""EnigmaMachine behavior and stepping tests."""

from __future__ import annotations

import pytest

from enigma import EnigmaConfigBuilder, EnigmaFactory
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


def test_machine_state_is_mutable_between_process_text_calls() -> None:
    machine = make_machine(key="AAA")

    first = machine.process_text("AAAA")
    second = machine.process_text("AAAA")
    fresh = make_machine(key="AAA").process_text("AAAA")

    assert first == fresh
    assert second != first


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


def test_process_char_uses_existing_advanced_rotor_positions() -> None:
    machine = make_machine(key="AAB")
    expected_machine = make_machine(key="AAC")

    assert machine.process_char("A") == expected_machine.encode_signal("A")
