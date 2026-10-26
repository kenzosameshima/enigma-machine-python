"""Rotor state and signal mapping tests."""

from __future__ import annotations

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
