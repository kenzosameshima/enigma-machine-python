"""EnigmaMachine behavior and stepping tests."""

from __future__ import annotations

import pytest
from helpers import make_rotor

from enigma.config import EnigmaConfig
from enigma.machine import EnigmaMachine, _should_step_rotors
from enigma.modes import MachineModeName
from enigma.plugboard import Plugboard


def make_machine(
    *,
    key: str = "AAA",
    mode: MachineModeName | str = MachineModeName.WEHRMACHT,
    rotor_order: tuple[str, ...] = ("I", "II", "III"),
    ring_settings: tuple[int, ...] = (1, 1, 1),
    reflector_name: str = "B",
    plug_pairs: tuple[tuple[str, str], ...] = (),
    greek_rotor_name: str = "BETA",
) -> EnigmaMachine:
    config = EnigmaConfig(
        rotor_order=rotor_order,
        ring_settings=ring_settings,
        key=key,
        reflector_name=reflector_name,
        plugboard_pairs=plug_pairs,
        greek_rotor_name=greek_rotor_name,
        mode=mode,
    )
    return EnigmaMachine.from_config(config)


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
    shared_rotors = [make_rotor("I"), make_rotor("II"), make_rotor("III")]
    first_machine = EnigmaMachine(shared_rotors, "B", Plugboard())
    second_machine = EnigmaMachine(shared_rotors, "B", Plugboard())
    expected = make_machine(key="AAA").process_text("AAAA")

    assert first_machine.process_text("AAAA") == expected
    assert second_machine.process_text("AAAA") == expected
    assert "".join(rotor.get_position_letter() for rotor in shared_rotors) == "AAA"


def test_machine_rejects_incorrect_moving_rotor_count() -> None:
    with pytest.raises(ValueError, match="exactly 3 moving rotors"):
        EnigmaMachine([make_rotor("I"), make_rotor("II")], "B", Plugboard())


def test_machine_rejects_non_moving_rotor_in_moving_slots() -> None:
    with pytest.raises(ValueError, match="Moving rotors"):
        EnigmaMachine(
            [make_rotor("I"), make_rotor("II"), make_rotor("BETA")], "B", Plugboard()
        )


def test_machine_rejects_duplicate_moving_rotors() -> None:
    with pytest.raises(ValueError, match="unique"):
        EnigmaMachine(
            [make_rotor("I"), make_rotor("II"), make_rotor("II")], "B", Plugboard()
        )


def test_machine_rejects_unknown_reflector() -> None:
    with pytest.raises(ValueError, match="Unknown reflector"):
        EnigmaMachine(
            [make_rotor("I"), make_rotor("II"), make_rotor("III")], "D", Plugboard()
        )


def test_machine_rejects_invalid_greek_rotor() -> None:
    with pytest.raises(ValueError, match="Greek rotor"):
        EnigmaMachine(
            [make_rotor("I"), make_rotor("II"), make_rotor("III")],
            "B",
            Plugboard(),
            greek_rotor=make_rotor("I", can_step=False),
        )


def test_machine_accepts_valid_non_stepping_greek_rotor() -> None:
    machine = EnigmaMachine(
        [make_rotor("I"), make_rotor("II"), make_rotor("III")],
        "B_THIN",
        Plugboard(),
        greek_rotor=make_rotor("BETA", can_step=False),
    )

    assert machine.window() == "AAA A"


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


def test_turnover_notch_is_independent_of_ring_setting() -> None:
    """Turnover happens at a fixed window letter regardless of ring setting.

    Rotor III's notch is at window letter V. With ring setting 2 the old,
    buggy formula ((position + ring) % 26 in notches) would treat window
    letter U as the notch instead, triggering the middle rotor's step one
    keystroke early.
    """

    machine = make_machine(
        key="AAU",
        rotor_order=("I", "II", "III"),
        ring_settings=(1, 1, 2),
    )

    machine.process_char("A")

    assert machine.window() == "AAV"


def test_process_char_uses_existing_advanced_rotor_positions() -> None:
    machine = make_machine(key="AAB")
    expected_machine = make_machine(key="AAC")

    assert machine.process_char("A") == expected_machine.encode_signal("A")


def test_m4_window_round_trips_through_key() -> None:
    machine = make_machine(
        key="JNAV",
        mode=MachineModeName.M4,
        ring_settings=(1, 1, 1, 1),
        reflector_name="B_THIN",
    )

    rebuilt = make_machine(
        key=machine.window().replace(" ", ""),
        mode=MachineModeName.M4,
        ring_settings=(1, 1, 1, 1),
        reflector_name="B_THIN",
    )

    assert rebuilt.window() == machine.window()


def test_process_text_rejects_non_string_input() -> None:
    machine = make_machine()

    with pytest.raises(ValueError, match="Text must be a string"):
        machine.process_text(None)  # type: ignore[arg-type]
