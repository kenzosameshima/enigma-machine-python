"""Configuration builder and factory validation tests."""

from __future__ import annotations

import pytest

from enigma import EnigmaConfigBuilder, EnigmaFactory, enigma_process


def make_machine(
    *,
    text: str = "",
    key: str = "AAA",
    mode: str = "wehrmacht",
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


def test_factory_creates_independent_rotor_states() -> None:
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


def test_builder_rejects_non_integer_ring_settings_with_predictable_message() -> None:
    with pytest.raises(ValueError, match="Ring settings must be integers"):
        enigma_process(
            text="HELLO",
            key="AAA",
            ring_settings=(1, "bad", 3),  # type: ignore[arg-type]
        )


def test_builder_rejects_non_text_rotor_names_with_predictable_message() -> None:
    with pytest.raises(ValueError, match="Rotor names must be text"):
        enigma_process(
            text="HELLO",
            key="AAA",
            rotor_order=("I", "II", 3),  # type: ignore[arg-type]
        )


def test_builder_creates_machine_with_expected_window() -> None:
    machine = make_machine(text="HELLO", key="ABC")

    assert machine.window() == "ABC"
