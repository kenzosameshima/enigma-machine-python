"""Rotor state and signal mapping tests."""

from __future__ import annotations

import pytest
from helpers import make_rotor


def test_rotor_steps_when_enabled() -> None:
    rotor = make_rotor("I")

    rotor.step()

    assert rotor.get_position_letter() == "B"


def test_fixed_rotor_does_not_step() -> None:
    rotor = make_rotor("BETA", can_step=False)

    rotor.step()

    assert rotor.get_position_letter() == "A"


def test_rotor_forward_backward_mapping_round_trips_indices() -> None:
    rotor = make_rotor("III", ring_setting=7, position="M")

    for index in range(26):
        assert rotor.encode_backward(rotor.encode_forward(index)) == index


def test_clone_produces_independent_rotor_with_same_state() -> None:
    rotor = make_rotor("I", ring_setting=5, position="C")
    clone = rotor.clone()

    clone.step()

    assert clone.get_position_letter() == "D"
    assert rotor.get_position_letter() == "C"


def test_snapshot_and_restore_round_trip_state() -> None:
    rotor = make_rotor("I")
    snapshot = rotor.snapshot()

    rotor.step()
    rotor.step()
    rotor.restore(snapshot)

    assert rotor.get_position_letter() == "A"


@pytest.mark.parametrize("name", ["I", "II", "III", "IV", "V", "BETA", "GAMMA"])
def test_rotor_has_exactly_twenty_six_contacts_in_each_direction(name: str) -> None:
    rotor = make_rotor(name)
    assert len(rotor.wiring) == len(rotor.inverse_wiring) == 26
