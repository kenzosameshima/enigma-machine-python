"""EnigmaConfig construction and validation tests."""

from __future__ import annotations

import pytest

from enigma import EnigmaConfig, EnigmaMachine, MachineModeName, enigma_process


def make_machine(
    *,
    key: str = "AAA",
    mode: str = "wehrmacht",
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


def test_from_config_creates_independent_rotor_states() -> None:
    first_machine = make_machine(key="AAA")
    second_machine = make_machine(key="AAA")

    first_states = [rotor.state for rotor in first_machine.rotors]
    second_states = [rotor.state for rotor in second_machine.rotors]

    assert len({id(state) for state in first_states}) == 3
    assert {id(state) for state in first_states}.isdisjoint(
        {id(state) for state in second_states}
    )


def test_m4_rejects_invalid_greek_rotor() -> None:
    with pytest.raises(ValueError, match="Greek rotor"):
        make_machine(
            key="AAAA",
            mode="m4",
            ring_settings=(1, 1, 1, 1),
            reflector_name="B_THIN",
            greek_rotor_name="I",
        )


def test_three_rotor_mode_also_rejects_invalid_greek_rotor() -> None:
    """Greek rotor identity is checked for every mode, not only M4.

    Three-rotor mode never uses the Greek rotor, but an explicitly invalid
    value is still rejected rather than silently accepted and ignored.
    """

    with pytest.raises(ValueError, match="Greek rotor"):
        make_machine(greek_rotor_name="I")


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


def test_enigma_process_rejects_non_integer_ring_settings() -> None:
    with pytest.raises(ValueError, match="Ring settings must be integers"):
        enigma_process(
            text="HELLO",
            key="AAA",
            ring_settings=(1, "bad", 3),  # type: ignore[arg-type]
        )


def test_enigma_process_rejects_non_text_rotor_names() -> None:
    with pytest.raises(ValueError, match="Rotor names must be text"):
        enigma_process(
            text="HELLO",
            key="AAA",
            rotor_order=("I", "II", 3),  # type: ignore[arg-type]
        )


def test_direct_config_creates_machine_with_expected_window() -> None:
    machine = make_machine(key="ABC")

    assert machine.window() == "ABC"


def test_config_mode_defaults_to_wehrmacht() -> None:
    config = EnigmaConfig(
        rotor_order=("I", "II", "III"),
        ring_settings=(1, 1, 1),
        key="AAA",
        reflector_name="B",
    )

    assert config.mode == MachineModeName.WEHRMACHT


def test_config_mode_accepts_explicit_value() -> None:
    config = EnigmaConfig(
        rotor_order=("I", "II", "III"),
        ring_settings=(1, 1, 1, 1),
        key="AAAA",
        reflector_name="B_THIN",
        mode=MachineModeName.M4,
    )

    assert config.mode == MachineModeName.M4


def test_direct_config_normalizes_mutable_containers_to_hashable_tuples() -> None:
    config = EnigmaConfig(
        rotor_order=["I", "II", "III"],  # type: ignore[arg-type]
        ring_settings=(1, 1, 1),
        key="AAA",
        reflector_name="B",
    )

    assert config.rotor_order == ("I", "II", "III")
    hash(config)
